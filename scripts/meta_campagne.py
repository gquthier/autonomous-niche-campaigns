#!/usr/bin/env python3
"""Campagne Meta à formulaire instantané pour toutes les niches d'un projet : une campagne ABO, un ad set par niche, un formulaire par niche
(qualifié sur le chiffre d'affaires par logique conditionnelle), les créatives de chaque niche en publicités.
Tout est créé EN PAUSE. Seule l'étape `activer --oui` lance la diffusion, et seulement sur décision explicite de la personne.
Chaque identifiant est noté dans <projet>/_meta/etat.json : relancer une étape ne recrée rien.

Usage : python3 meta_campagne.py <dossier du projet> <étape> [niche ...] [--dry-run] [options]
  --dry-run       simulation complète, sans clé ni réseau ; état dans _meta/etat.dry-run.json et _meta/monde.dry-run.json

Ordre conseillé :
  verifier        resume.json de chaque niche, puis jeton, droits, compte, page, Instagram, formulaires existants (lecture seule)
  textes          affiche les textes des publicités de chaque niche (lecture seule, sans clé)
  regles          affiche la logique conditionnelle attendue de chaque formulaire (lecture seule, sans clé)
  campagne        crée la campagne ABO (en pause)
  adsets          crée un ad set par niche (budget du projet, ciblage large, en pause)
  formulaires     crée les formulaires de base par l'API (questions, page de fin), sans logique
                  --nouvelle-version : après un changement de formulaire.nom, recrée la base (l'ancienne reste notée et en ligne)
  logique         lance l'éditeur de Meta dans le navigateur pour chaque niche : copie du formulaire de base, logique conditionnelle, deux pages de fin
  trouver         retrouve les formulaires finaux par leur nom exact et les note (--ecrire)
  images          envoie les créatives finales (creatives/final/*.jpg) dans la bibliothèque du compte
  pubs            crée les créatives Meta et les publicités (pointées sur le formulaire final de la niche)
  controle        relit tout : campagne, ad sets, publicités, formulaire de chaque publicité
  usage           pour chaque formulaire de la page : les publicités qui l'utilisent
  archiver_bases  archive les formulaires de base qu'aucune publicité n'utilise
  activer --oui   active les ad sets puis la campagne (dépense réelle)
  parcours        en simulation seulement : verifier, campagne, adsets, formulaires, logique, trouver, images, pubs, controle"""
import hashlib
import json
import re
import subprocess
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI / "lib"))
from projet import Projet, textes_pub, regles_logique, controle_resume  # noqa: E402
from meta import Meta, FauxMeta, ok  # noqa: E402

SANS_AMELIO = json.loads((ICI.parent / "assets" / "creative_sans_ameliorations.json").read_text(encoding="utf-8"))
SANS_AMELIO = {k: v for k, v in SANS_AMELIO.items() if not k.startswith("_") and v}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:60]


def formulaire_de(ad):
    try:
        return ad["creative"]["object_story_spec"]["link_data"]["call_to_action"]["value"].get("lead_gen_form_id")
    except (KeyError, TypeError, AttributeError):
        return None


class Contexte:
    def __init__(self, P, niches, opts):
        self.P, self.NICHES, self.opts = P, niches, opts
        self.simulation = P.simulation
        self._M = None

    @property
    def E(self):
        return self.P.etat

    @property
    def M(self):
        if self._M is None:
            self._M = FauxMeta(self.P) if self.simulation else Meta(self.P)
        return self._M

    def nom_adset(self, n):
        return self.P.get("campagne", "prefixe_adset", defaut=f"{self.P['agence']['nom']} | ") + n["label"]

    def ciblage(self):
        c = self.P["campagne"]
        t = {"geo_locations": {"countries": c.get("pays", ["FR"]), "location_types": ["home", "recent"]},
             "age_min": c.get("age_min", 25), "age_max": c.get("age_max", 60),
             # Large : aucun intérêt, Advantage+ audience coupé, Facebook et Instagram seulement (pas d'Audience Network).
             "targeting_automation": {"advantage_audience": 0, "individual_setting": {"age": 0}},
             "publisher_platforms": ["facebook", "instagram"],
             "facebook_positions": ["feed", "instream_video", "marketplace", "story", "facebook_reels", "facebook_reels_overlay", "profile_feed", "notification"],
             "instagram_positions": ["stream", "story", "reels"], "device_platforms": ["mobile", "desktop"],
             "brand_safety_content_filter_levels": ["FACEBOOK_RELAXED"]}
        if c.get("langues_meta"):
            t["locales"] = c["langues_meta"]
        return t

    def finales(self, n):
        """[(nom, clé de version, chemin ou None)] des créatives finales d'une niche.
        En simulation, sans images, on prend les id de creatives/spec.json (+ leurs variantes « performance »)."""
        d = n["chemin"] / "creatives" / "final"
        fichiers = sorted(p for p in d.glob("*.jpg") if not p.name.startswith("_")) if d.exists() else []
        if fichiers or not self.simulation:
            return [(p.stem, f"{p.stem}:{p.stat().st_size}", p) for p in fichiers]
        spec_f = n["chemin"] / "creatives" / "spec.json"
        spec = json.loads(spec_f.read_text(encoding="utf-8")) if spec_f.exists() else []
        ids = [i["id"] for i in spec][:int(self.P.get("creatives", "par_niche", defaut=10))] or [f"N{n['rang']}{i:02d}-simulation" for i in range(1, 11)]
        perf = n["resume"].get("variantes_performance") or ids[:int(self.P.get("creatives", "variantes_performance", defaut=2))]
        noms = ids + [f"{i}-performance" for i in perf]
        return [(s, f"{s}:simulation", None) for s in noms]


# ---------------------------------------------------------------- lecture seule
def verifier(c):
    P, NICHES = c.P, c.NICHES
    bloquant = 0
    for n in NICHES:
        pb = controle_resume(P, n)
        print(f"niche {n['cle']} : resume.json {'ok' if not pb else 'À CORRIGER'} | {len(c.finales(n))} créatives finales"
              + (" (simulées)" if c.simulation and not (n['chemin'] / 'creatives' / 'final').exists() else ""))
        for x in pb:
            print("   -", x)
        bloquant += len(pb)
    M = c.M
    me = ok(M.get("me", fields="id,name"), "jeton")
    print("jeton : valide pour", me.get("name"))
    perms = {p["permission"] for p in M.get("me/permissions").get("data", []) if p.get("status") == "granted"}
    besoin = ["ads_management", "ads_read", "leads_retrieval", "pages_manage_ads", "pages_read_engagement", "pages_show_list", "business_management"]
    print("droits manquants :", [p for p in besoin if p not in perms] or "aucun", "(un utilisateur système n'expose pas toujours la liste : un « manquant » ici n'est pas forcément bloquant)")
    a = ok(M.get(M.act, fields="name,account_status,currency,timezone_name,disable_reason"), "compte publicitaire")
    print("compte :", a.get("name"), "| statut", a.get("account_status"), "(1 = actif) |", a.get("currency"), a.get("timezone_name"))
    M.page_token()
    print("page : accès ok")
    if M.ig:
        print("instagram :", M.get(M.ig, fields="username").get("username", "non lisible avec ce jeton (fréquent avec un utilisateur système ; la création des publicités dira si l'identifiant est refusé)"))
    fs = M.formulaires()
    print(len(fs), "formulaires actifs sur la page :", ", ".join(sorted(f["name"] for f in fs))[:600] or "aucun")
    camps = M.toutes(f"{M.act}/campaigns", fields="name,effective_status", limit=100)
    print("campagnes du compte :", ", ".join(f"{x['name']} [{x['effective_status']}]" for x in camps)[:900] or "aucune")
    if bloquant:
        print(f"{bloquant} point(s) à corriger dans les resume.json avant de créer quoi que ce soit")
    return 1 if bloquant else 0


def textes(c):
    for n in c.NICHES:
        t = textes_pub(c.P, n)
        tp = textes_pub(c.P, n, True)
        print(f"===== {n['label']}\nTITRE : {t['title']} | DESCRIPTION : {t['desc']}\n{t['body']}\nCARTE D'INTRO : {t['card_title']} | {t['card']}\n--- variante performance : {tp['desc']}\n")
        tv = options_texte(n)
        if tv:
            for cle, valeurs in tv.items():
                for i, texte in enumerate(valeurs, 1):
                    print(f"OPTION {cle} {i} : {texte}")


def options_texte(n):
    """Options rédigées par niche : 1 à 5 textes non vides par champ."""
    tv = n["resume"].get("textes_variantes")
    if tv is None:
        return None
    champs = ("bodies", "titles", "descriptions")
    if not isinstance(tv, dict) or set(tv) != set(champs):
        raise SystemExit(f"{n['cle']} : textes_variantes attend bodies, titles et descriptions")
    for cle in champs:
        valeurs = tv[cle]
        if not isinstance(valeurs, list) or not 1 <= len(valeurs) <= 5 or any(not isinstance(x, str) or not x.strip() for x in valeurs):
            raise SystemExit(f"{n['cle']} : textes_variantes.{cle} attend 1 à 5 textes non vides")
    return tv


def regles(c):
    for n in c.NICHES:
        print(f"===== {c.P.nom_formulaire(n)}")
        for q, rep, dest, effet in regles_logique(c.P, n):
            print(f"  {q[:28]:<28} | {rep[:42]:<42} → {dest}" + (f"  [{effet}]" if effet != "-" else ""))


# ---------------------------------------------------------------- campagne et ad sets
def campagne(c):
    P, E, M = c.P, c.E, c.M
    if not E.get("campagne"):
        base = dict(name=P.nom_campagne(), objective="OUTCOME_LEADS", buying_type="AUCTION", special_ad_categories=[], status="PAUSED")
        r = M.post(f"{M.act}/campaigns", **base)
        if "error" in r:   # budget porté par les ad sets (ABO) : les versions récentes de l'API veulent ce champ
            r = M.post(f"{M.act}/campaigns", is_adset_budget_sharing_enabled=False, **base)
        E["campagne"] = ok(r, "campagne", P)["id"]
        P.sauver()
    print("campagne", E["campagne"], P.nom_campagne(), "(en pause)")


def adsets(c):
    P, E, M = c.P, c.E, c.M
    if not E.get("campagne"):
        raise SystemExit("lancer d'abord l'étape campagne")
    budget = int(round(float(P["campagne"]["budget_jour_par_niche"]) * 100))
    for n in c.NICHES:
        if n["cle"] not in E["adsets"]:
            champs = dict(name=c.nom_adset(n), campaign_id=E["campagne"], daily_budget=budget, bid_strategy="LOWEST_COST_WITHOUT_CAP",
                          billing_event="IMPRESSIONS", optimization_goal="QUALITY_LEAD", destination_type="ON_AD",
                          promoted_object={"page_id": M.page}, attribution_spec=[{"event_type": "CLICK_THROUGH", "window_days": 1}],
                          targeting=c.ciblage(), status="PAUSED")
            if P.get("meta", "dsa_beneficiary"):
                champs.update(dsa_beneficiary=P["meta"]["dsa_beneficiary"], dsa_payor=P["meta"].get("dsa_payor") or P["meta"]["dsa_beneficiary"])
            E["adsets"][n["cle"]] = ok(M.post(f"{M.act}/adsets", **champs), f"ad set {n['cle']}", P)["id"]
            P.sauver()
        print("ad set", n["cle"], E["adsets"][n["cle"]], c.nom_adset(n), f"{budget / 100:.0f} €/jour (en pause)")


# ---------------------------------------------------------------- formulaires
def formulaires(c):
    P, E, M = c.P, c.E, c.M
    pt = M.page_token()
    f = P["formulaire"]
    if not (E.get("campagne") and all(n["cle"] in E["adsets"] for n in c.NICHES)):
        print("ATTENTION : campagne ou ad sets pas encore créés, les liens de réservation n'auront pas utm_id / utm_term (recommandé : campagne puis adsets d'abord)")
    noms = E.setdefault("noms_formulaires", {})
    for n in c.NICHES:
        k = n["cle"]
        if k in E["formulaires_base"]:
            if "--nouvelle-version" not in c.opts or noms.get(E["formulaires_base"][k]) == P.nom_formulaire(n, base=True):
                print("déjà créé :", P.nom_formulaire(n, base=True))
                continue
            # Nouvelle version (nouveau formulaire.nom) : l'ancienne reste notée, et reste en ligne tant que des publicités l'utilisent.
            if any(x["name"] == P.nom_formulaire(n, base=True) for x in M.formulaires()):
                raise SystemExit(f"un formulaire actif s'appelle déjà « {P.nom_formulaire(n, base=True)} » : change formulaire.nom avant --nouvelle-version")
            E.setdefault("formulaires_precedents", {}).setdefault(k, []).append({"base": E["formulaires_base"].pop(k), "final": E["formulaires"].pop(k, None)})
            P.sauver()
        r = n["resume"]
        t = textes_pub(P, n)
        intro = r.get("formulaire_intro") or {}   # promesse propre au formulaire (ex. vague CBO), sinon celle des publicités

        def options(vals):
            return [{"value": v, "key": slug(v)} for v in vals]

        fin = f["page_fin"]
        res = M.post(f"{M.page}/leadgen_forms", token=pt, name=P.nom_formulaire(n, base=True), locale=f.get("locale", "fr_FR"),
                     questions=[{"type": "CUSTOM", "key": "profil", "label": r.get("formulaire_q1") or f.get("question_profil", "Vous êtes ?"), "options": options(r["formulaire_q1_options"])},
                                {"type": "CUSTOM", "key": "chiffre_affaires", "label": r.get("formulaire_q2") or f.get("question_ca", "Quel est votre chiffre d'affaires annuel ?"),
                                 "options": options(r.get("formulaire_q2_options") or f["tranches_ca"])},
                                {"type": "EMAIL"}, {"type": "FULL_NAME"}, {"type": "PHONE"}],
                     context_card={"title": intro.get("titre", t["card_title"]), "style": "PARAGRAPH_STYLE", "content": [intro.get("texte", t["card"])]},
                     privacy_policy={"url": f["lien_confidentialite"], "link_text": f.get("texte_confidentialite", "Politique de confidentialité")},
                     follow_up_action_url=P.lien_reservation(n),
                     thank_you_page={"title": fin["titre"], "body": fin["texte"], "button_text": fin["bouton"], "button_type": "VIEW_WEBSITE", "website_url": P.lien_reservation(n)},
                     question_page_custom_headline=f.get("entete_questions", "Deux questions, puis réservez votre étude dans notre calendrier."),
                     block_display_for_non_targeted_viewer=True, is_optimized_for_quality=False)
        E["formulaires_base"][n["cle"]] = ok(res, f"formulaire {n['cle']}", P)["id"]
        noms[E["formulaires_base"][n["cle"]]] = P.nom_formulaire(n, base=True)
        P.sauver()
        print("formulaire de base", n["cle"], E["formulaires_base"][n["cle"]], P.nom_formulaire(n, base=True))


def logique(c):
    P = c.P
    for n in c.NICHES:
        if n["cle"] in c.E["formulaires"]:
            print("déjà fait :", P.nom_formulaire(n))
            continue
        print("=====", n["label"], flush=True)
        if c.simulation:
            base = c.E["formulaires_base"].get(n["cle"])
            if not base:
                raise SystemExit(f"{n['cle']} : formulaire de base absent (étape formulaires)")
            for q, rep, dest, effet in regles_logique(P, n):
                print(f"  [à blanc] {rep} → {dest}" + (f" [{effet}]" if effet != "-" else ""))
            print("  [à blanc] deux pages de fin identiques ; lien des non-prospects :", P.lien_reservation(n, qualifie=False))
            c.E["formulaires"][n["cle"]] = c.M.copier_formulaire(base, P.nom_formulaire(n))["id"]
            P.sauver()
            print("  [à blanc] publié :", P.nom_formulaire(n), c.E["formulaires"][n["cle"]])
            continue
        code = subprocess.run([sys.executable, str(ICI / "editeur" / "formulaire_final.py"), str(P.racine), n["cle"]]).returncode
        if code:
            raise SystemExit(f"ARRÊT sur {n['cle']} : l'éditeur est laissé ouvert pour inspection (voir references/formulaire.md, « Reprendre après un arrêt »)")
        P.etat = Projet(P.racine).etat   # formulaire_final.py a noté l'identifiant


def trouver(c):
    actifs = c.M.formulaires()

    def norm(s):
        return " ".join(s.replace(" ", " ").split()).lower()

    for n in c.NICHES:
        x = [f for f in actifs if norm(f["name"]) == norm(c.P.nom_formulaire(n))]
        print(n["cle"], "→", [(f["name"], f["id"]) for f in x] or "INTROUVABLE")
        if len(x) == 1 and "--ecrire" in c.opts:
            c.E["formulaires"][n["cle"]] = x[0]["id"]
    if "--ecrire" in c.opts:
        c.P.sauver()
        print("état noté")


# ---------------------------------------------------------------- images et publicités
def images(c):
    E = c.E
    for n in c.NICHES:
        E["images"].setdefault(n["cle"], {})
        fichiers = c.finales(n)
        noms = {s for s, _, _ in fichiers}
        for stem in [s for s in E["images"][n["cle"]] if s not in noms]:
            del E["images"][n["cle"]][stem]   # retirée de la sélection : reste dans la bibliothèque, sans publicité
        for stem, cle, chemin in fichiers:
            if E["images"][n["cle"]].get(stem, {}).get("cle") == cle:
                continue
            E["images"][n["cle"]][stem] = {"hash": c.M.envoyer_image(str(chemin or stem)), "cle": cle}
            c.P.sauver()
        print(n["cle"], len(E["images"][n["cle"]]), "images")


def pubs(c):
    P, E, M = c.P, c.E, c.M
    for n in c.NICHES:
        k = n["cle"]
        if k not in E["formulaires"] or k not in E["adsets"]:
            raise SystemExit(f"{k} : formulaire final ou ad set manquant (étapes logique + trouver --ecrire, adsets)")
        E["creatives"].setdefault(k, {})
        E["pubs"].setdefault(k, {})
        variantes = options_texte(n)
        for stem in sorted(E["images"].get(k, {})):
            perf = stem.endswith("-performance")
            t = textes_pub(P, n, perf)
            img = E["images"][k][stem]
            label = f"{n['label']} · {stem}"
            tv = variantes if not perf else None
            contenu = [t, tv] if tv else t  # conserve les clés des publicités sans options
            cle = f"{img['cle']}|{E['formulaires'][k]}|{hashlib.md5(json.dumps(contenu, sort_keys=True).encode()).hexdigest()[:10]}"
            if E["creatives"][k].get(stem, {}).get("cle") != cle:
                spec = {"page_id": M.page, **({"instagram_user_id": M.ig} if M.ig else {}),
                        "link_data": {"image_hash": img["hash"], "link": "http://fb.me/", "message": t["body"], "name": t["title"], "description": t["desc"],
                                      "call_to_action": {"type": "LEARN_MORE", "value": {"lead_gen_form_id": E["formulaires"][k], "link": "http://fb.me/"}}}}
                afs = {}
                if tv:
                    spec["link_data"].update(message=tv["bodies"][0], name=tv["titles"][0], description=tv["descriptions"][0])
                    afs = {"asset_feed_spec": {**{champ: [{"text": x} for x in tv[champ]] for champ in tv}, "optimization_type": "DEGREES_OF_FREEDOM"}}
                r = {"error": {"message": "aucun essai"}}
                for extra in (SANS_AMELIO, {}):
                    r = M.post(f"{M.act}/adcreatives", name=f"{P['agence']['nom']} {label}", object_story_spec=spec, **afs, **extra)
                    if "error" not in r:
                        break
                    print("  créative refusée avec ces réglages :", str(r["error"].get("error_user_msg") or r["error"].get("message"))[:200], flush=True)
                E["creatives"][k][stem] = {"id": ok(r, f"créative {label}", P)["id"], "cle": cle}
                P.sauver()
                if stem in E["pubs"][k]:   # image, texte ou formulaire changés : la publicité existante prend la nouvelle créative
                    ok(M.post(E["pubs"][k][stem], creative={"creative_id": E["creatives"][k][stem]["id"]}), f"mise à jour {label}", P)
            if stem not in E["pubs"][k]:
                statut = "PAUSED" if perf and n["resume"].get("variantes_performance_en_pause") else "ACTIVE"   # l'ad set en pause retient la diffusion
                r = M.post(f"{M.act}/ads", name=label, adset_id=E["adsets"][k], creative={"creative_id": E["creatives"][k][stem]["id"]}, status=statut)
                E["pubs"][k][stem] = ok(r, f"publicité {label}", P)["id"]
                P.sauver()
        print(k, len(E["pubs"][k]), "publicités")


# ---------------------------------------------------------------- contrôle
def controle(c):
    E, M = c.E, c.M
    if E.get("campagne"):
        x = ok(M.get(E["campagne"], fields="name,status,effective_status,objective"), "campagne")
        print("CAMPAGNE", x["name"], "|", x["status"], x["effective_status"], "|", x["objective"])
    total = bons = budget = 0
    noms = {x["id"]: x["name"] for x in M.formulaires()}
    for n in c.NICHES:
        k = n["cle"]
        if k not in E["adsets"]:
            print(f"  {k} : pas d'ad set")
            continue
        s = ok(M.get(E["adsets"][k], fields="name,status,effective_status,daily_budget,optimization_goal,destination_type,targeting,issues_info"), f"ad set {k}")
        tg = s.get("targeting", {})
        large = not any(x in tg for x in ("flexible_spec", "interests", "behaviors", "custom_audiences")) and tg.get("targeting_automation", {}).get("advantage_audience") == 0
        ads = M.toutes(f"{E['adsets'][k]}/ads", fields="name,status,effective_status,issues_info,creative{object_story_spec}", limit=100)
        bon = sum(1 for a in ads if formulaire_de(a) == E["formulaires"].get(k))
        total += len(ads)
        bons += bon
        budget += int(s.get("daily_budget", 0)) if s["status"] == "ACTIVE" else 0
        souci = [a["name"] for a in ads if a.get("issues_info") or a["effective_status"] in ("DISAPPROVED", "WITH_ISSUES")]
        print(f"  {s['name']} | {s['status']} {s['effective_status']} | {int(s.get('daily_budget', 0)) / 100:.0f} €/j | {s.get('optimization_goal')} {s.get('destination_type')} | "
              f"{sorted(tg.get('geo_locations', {}).get('countries', []))} {tg.get('age_min')}-{tg.get('age_max')} | large : {'oui' if large else 'NON'} | "
              f"{len(ads)} pubs {dict(Counter(a['effective_status'] for a in ads))} | sur « {noms.get(E['formulaires'].get(k), 'formulaire inconnu ou inactif')} » : {bon}/{len(ads)}"
              + (f" | À VOIR : {souci}" if souci else ""))
    print(f"TOTAL : {total} publicités, {bons} sur le bon formulaire ; dépense des ad sets actifs : {budget / 100:.0f} €/jour")


def usage_formulaires(c, archiver=False):
    M = c.M
    noms = {x["id"]: f"{x['name']} ({x['status']})" for st in ("ACTIVE", "ARCHIVED") for x in M.formulaires(st)}
    usage = {}
    for camp in M.toutes(f"{M.act}/campaigns", fields="name", limit=100):
        for a in M.toutes(f"{camp['id']}/ads", fields="name,creative{object_story_spec}", limit=200):
            f = formulaire_de(a)
            if f:
                usage.setdefault(f, Counter())[camp["name"]] += 1
    if not archiver:
        for f, camps in sorted(usage.items(), key=lambda kv: noms.get(kv[0], kv[0])):
            print(noms.get(f, f), "←", dict(camps))
        return
    for n in c.NICHES:
        fid = c.E["formulaires_base"].get(n["cle"])
        if not fid:
            continue
        if usage.get(fid):
            print("GARDÉ (encore utilisé) :", n["cle"], dict(usage[fid]))
            continue
        r = M.post(fid, token=M.page_token(), status="ARCHIVED")
        print("archivé :", c.P.nom_formulaire(n, base=True), r.get("error", {}).get("message", "ok"))


# ---------------------------------------------------------------- activation
def activer(c):
    if "--oui" not in c.opts:
        raise SystemExit("Rien n'est activé : relancer avec --oui, seulement après l'accord explicite de la personne (dépense réelle).")
    E = c.E
    for n in c.NICHES:
        k = n["cle"]
        manque = [x for x in ("adsets", "formulaires") if k not in E[x]] + ([] if E["pubs"].get(k) else ["pubs"])
        if manque:
            raise SystemExit(f"{k} : pas prêt ({manque}), rien n'est activé")
    budget = float(c.P["campagne"]["budget_jour_par_niche"]) * len(c.NICHES)
    print(f"activation de {len(c.NICHES)} ad set(s), {budget:.0f} €/jour au total" + (" [à blanc]" if c.simulation else ""))
    for n in c.NICHES:
        ok(c.M.post(E["adsets"][n["cle"]], status="ACTIVE"), f"activation {n['cle']}", c.P)
        print("ad set actif :", n["cle"])
    ok(c.M.post(E["campagne"], status="ACTIVE"), "activation de la campagne", c.P)
    print("campagne active")
    E["active_le"] = time.strftime("%Y-%m-%d %H:%M")
    c.P.sauver()


ETAPES = {"verifier": verifier, "textes": textes, "regles": regles, "campagne": campagne, "adsets": adsets, "formulaires": formulaires,
          "logique": logique, "trouver": trouver, "images": images, "pubs": pubs, "controle": controle,
          "usage": usage_formulaires, "archiver_bases": lambda c: usage_formulaires(c, archiver=True), "activer": activer}
PARCOURS = ["verifier", "campagne", "adsets", "formulaires", "logique", "trouver", "images", "pubs", "controle"]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    args = [a for a in argv if not a.startswith("--")]
    opts = {a for a in argv if a.startswith("--")}
    if len(args) < 2 or (args[1] not in ETAPES and args[1] != "parcours"):
        print(__doc__)
        return 2
    simulation = "--dry-run" in opts
    P = Projet(args[0], simulation=simulation)
    c = Contexte(P, P.niches(args[2:]), opts)
    if simulation:
        print("[simulation : aucun appel réseau, aucune clé ; état dans _meta/etat.dry-run.json]")
    if args[1] == "parcours":
        if not simulation:
            raise SystemExit("parcours n'existe qu'en simulation (--dry-run) : en réel, chaque étape se lance et se relit une par une")
        c.opts = opts | {"--ecrire"}
        for nom in PARCOURS:
            print(f"\n### {nom}")
            if ETAPES[nom](c):
                return 1
        return 0
    return ETAPES[args[1]](c) or 0


if __name__ == "__main__":
    sys.exit(main())
