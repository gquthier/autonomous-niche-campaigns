#!/usr/bin/env python3
"""Passage de l'ABO à la CBO : une campagne par niche, un ad set par angle, 4 à 8 statiques par angle, chacune en 4:5 et en 9:16.
Ce script ne crée rien dans Meta : il lit les résultats, construit la grille attendue, relit l'état réel et vérifie (references/cbo.md).

Usage : python3 cbo.py <dossier du projet> <étape> [niche ...] [options]
  gagnants [fichier.csv]  résultats de l'ABO par annonce (export du gestionnaire de publicités, par défaut cbo/resultats-abo.csv)
  grille                  grille niche × angle × statique × format depuis <niche>/cbo/angles.json → cbo/annonces.csv (copy comprise)
                          --fichiers : vérifie aussi que chaque visuel existe, au bon format
  apercu                  les parcours à tester dans l'aperçu de chaque formulaire, et le relevé à remplir (_meta/apercu-formulaires.json)
  lire                    relit l'état réel par l'API, en lecture seule → _meta/cbo-etat-lu.json
                          --dry-run : état simulé conforme à la grille ; --dry-run --pieges : avec les erreurs rencontrées sur un vrai compte
  verifier                compare l'état lu à la grille et au relevé d'aperçu ; écrit _meta/push-verified.json SEULEMENT si tout passe
Règle : ne jamais dire « c'est dans le gestionnaire de pubs » sans un push-verified écrit par `verifier` juste après un `lire`."""
import csv
import datetime as dt
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI / "lib"))
from projet import Projet, questions, textes_pub  # noqa: E402

DEFAUTS = {"campagne_nom": "Instant Form - CBO | {label}", "adset_nom": "{agence} | {angle} | {titre}", "formulaire_nom": "IF - {label} - CBO",
           "angles_min": 3, "statiques_min": 4, "statiques_max": 8, "bouton": "En savoir plus", "fraicheur_minutes": 60,
           "formats": {"4x5": [1080, 1350], "9x16": [1080, 1920]}, "accents_permis": []}
NON_QUALIFIES = {
    "sans_trace": ("non_prospect_sans_reservation", "sous le seuil : formulaire fermé avant les coordonnées, aucune réservation, aucune trace"),
    "reservation_marquee": ("non_prospect_avec_reservation", "sous le seuil : formulaire fermé avant les coordonnées, bouton de réservation marqué non qualifié"),
    "liste": ("prospect", "sous le seuil : coordonnées envoyées (Meta les compte comme prospects), l'outil de l'équipe les range en « non qualifiés »"),
}
COLONNES = ["niche", "campagne", "formulaire", "angle", "angle_titre", "gagnant_de_depart", "adset", "annonce", "format_visuel",
            "fichier_4x5", "fichier_9x16", "accroche_image", "texte_court", "texte_principal", "texte_long", "titre", "description", "bouton"]
# Mots que l'on voit sans accent dans des formulaires et des publicités. Ils n'existent pas sans accent en français.
SANS_ACCENT = {"etude": "étude", "etudes": "études", "reservez": "réservez", "reserver": "réserver", "reservation": "réservation",
               "derniere": "dernière", "etape": "étape", "interet": "intérêt", "creneau": "créneau", "creneaux": "créneaux", "deja": "déjà",
               "tres": "très", "apres": "après", "delai": "délai", "equipe": "équipe", "reponse": "réponse", "reponses": "réponses",
               "repondez": "répondez", "telephone": "téléphone", "proprietaire": "propriétaire", "proprietaires": "propriétaires",
               "activite": "activité", "confidentialite": "confidentialité", "premiere": "première", "metier": "métier", "region": "région",
               "periode": "période", "seance": "séance", "seances": "séances", "beneficiez": "bénéficiez", "precis": "précis",
               "prequalifie": "préqualifié", "prequalifies": "préqualifiés",
               "verifie": "vérifié", "verifies": "vérifiés", "selection": "sélection", "francais": "français", "societe": "société",
               "gerant": "gérant", "deplacement": "déplacement", "reponds": "réponds"}
ACCENTS = set("éèêëàâäîïôöùûüçÉÈÊÀÂÎÔÙÛÇ")


# ---------------------------------------------------------------- configuration et texte
def conf(P):
    c = dict(DEFAUTS)
    c.update({k: v for k, v in (P.get("cbo", defaut={}) or {}).items() if not k.startswith("_")})
    return c


def remplir(modele, **v):
    for k, x in v.items():
        modele = modele.replace("{" + k + "}", str(x))
    return modele


def norm(s):
    """Comparaison de textes : apostrophes et espaces unifiés, casse ignorée."""
    s = unicodedata.normalize("NFC", str(s or "")).replace("’", "'").replace(" ", " ").replace(" ", " ")
    return " ".join(s.split()).lower()


def fautes_accents(texte, permis=()):
    """Les mots écrits sans leur accent, et les participes en -ee(s) sans é. Renvoie [(mot lu, mot attendu)]."""
    out = []
    for mot in re.findall(r"[A-Za-zÀ-ÿ]+", str(texte or "")):
        m = mot.lower()
        if m in permis:
            continue
        if m in SANS_ACCENT:
            out.append((mot, SANS_ACCENT[m]))
        elif len(m) > 4 and re.search(r"[^eé]ees?$", m):
            out.append((mot, m[:-2 if m.endswith("ee") else -3] + ("ée" if m.endswith("ee") else "ées")))
    return out


def sans_aucun_accent(texte):
    mots = re.findall(r"[A-Za-zÀ-ÿ']+", str(texte or ""))
    return len(mots) >= 20 and not (set(str(texte)) & ACCENTS)


def lien_vers_accueil(url, site):
    """Vrai si le lien de confidentialité ouvre l'accueil du site (cas réel) ou une racine de domaine."""
    if not url:
        return False
    u = urlsplit(url)
    if u.path.strip("/") == "" and not u.query:
        return True
    s = urlsplit(site or "")
    return bool(s.netloc) and u.netloc == s.netloc and u.path.strip("/") == s.path.strip("/")


def nombre(x):
    s = str(x or "").replace(" ", "").replace("\xa0", "").replace(" ", "").replace("€", "")
    if "," in s and "." in s:
        s = s.replace(",", "")
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


# ---------------------------------------------------------------- gagnants de l'ABO
ALIAS = {"adset": ("Nom de l'ensemble de publicités", "Nom de l’ensemble de publicités", "Ad set name", "adset"),
         "pub": ("Nom de la publicité", "Ad name", "pub"),
         "depense": ("Montant dépensé (EUR)", "Amount spent (EUR)", "Montant dépensé", "depense"),
         "resultats": ("Résultats", "Results", "Prospects", "Leads", "resultats")}


def lire_resultats(fichier):
    txt = Path(fichier).read_text(encoding="utf-8-sig")
    sep = ";" if txt.splitlines()[0].count(";") > txt.splitlines()[0].count(",") else ","
    lignes = list(csv.DictReader(txt.splitlines(), delimiter=sep))
    col = {}
    for k, noms in ALIAS.items():
        col[k] = next((c for c in (lignes[0].keys() if lignes else []) if c.strip() in noms), None)
        if not col[k]:
            raise SystemExit(f"{fichier} : colonne introuvable pour « {k} » (attendu l'une de : {', '.join(noms)})")
    return [{k: (r[col[k]] or "").strip() for k in col} for r in lignes]


def gagnants(P, lignes, part_min=0.2, prospects_min=3):
    """Par ad set de l'ABO : prospects, dépense, coût, et les annonces qui portent la niche. Renvoie {ad set: dict}."""
    formats = {}
    for n in P.niches():
        f = n["chemin"] / "creatives" / "spec.json"
        if f.exists():
            formats.update({i["id"]: i["format"] for i in json.loads(f.read_text(encoding="utf-8"))})
    out = {}
    for r in lignes:
        a = out.setdefault(r["adset"], {"prospects": 0, "depense": 0.0, "pubs": []})
        res, dep = int(nombre(r["resultats"])), nombre(r["depense"])
        stem = r["pub"].split("·")[-1].strip()
        a["prospects"] += res
        a["depense"] += dep
        a["pubs"].append({"pub": stem, "format": formats.get(stem.replace("-performance", ""), ""), "prospects": res, "depense": dep})
    for a in out.values():
        a["cout"] = round(a["depense"] / a["prospects"], 2) if a["prospects"] else None
        a["pubs"].sort(key=lambda x: (-x["prospects"], x["depense"]))
        for x in a["pubs"]:
            x["part"] = round(x["prospects"] / a["prospects"], 2) if a["prospects"] else 0
            x["gagnant"] = x["prospects"] >= prospects_min and x["part"] >= part_min
    return out


def etape_gagnants(P, args, opts):
    fichier = Path(args[0]) if args else P.racine / "cbo" / "resultats-abo.csv"
    if not fichier.exists():
        raise SystemExit(f"{fichier} introuvable : exporte les résultats par annonce du gestionnaire de publicités (niveau publicité, toute la période de l'ABO)")
    res = gagnants(P, lire_resultats(fichier))
    for nom, a in res.items():
        cout = f"{a['cout']:.2f} € par prospect" if a["cout"] else "aucun prospect"
        print(f"===== {nom} : {a['prospects']} prospects, {a['depense']:.2f} €, {cout}")
        for x in a["pubs"]:
            if x["prospects"] or x["gagnant"]:
                print(f"  {'GAGNANT ' if x['gagnant'] else '        '}{x['pub']:<40} {x['prospects']:>3} ({x['part']:.0%})  {x['depense']:>7.2f} €  {x['format']}")
        muettes = [x["pub"] for x in a["pubs"] if not x["prospects"]]
        if muettes:
            print(f"  sans prospect : {', '.join(muettes)}")
        if a["prospects"] < 30:
            print(f"  ATTENTION : {a['prospects']} prospects, c'est une indication, pas une preuve. Garde les familles visuelles gagnantes, pas une image.")
    print("\nCes résultats comptent des formulaires envoyés, pas des rendez-vous tenus : croise avec l'outil de l'équipe avant de couper un angle.")
    return 0


# ---------------------------------------------------------------- grille attendue
def charger_angles(n):
    f = n["chemin"] / "cbo" / "angles.json"
    if not f.exists():
        raise SystemExit(f"{n['cle']} : {f} absent (voir references/cbo.md, « Choisir trois angles »)")
    return json.loads(f.read_text(encoding="utf-8"))


def textes_de(ligne):
    return [ligne[k] for k in ("accroche_image", "texte_court", "texte_principal", "texte_long", "titre", "description")]


def construire_grille(P, niches):
    """(lignes, erreurs, avertissements). Une ligne = une annonce = une statique en deux formats."""
    C, lignes, err, avert = conf(P), [], [], []
    for n in niches:
        a = charger_angles(n)
        code = a.get("code") or n["cle"][0].upper()
        angles = a.get("angles", [])
        interdites = a.get("expressions_interdites", [])
        camp = remplir(C["campagne_nom"], label=n["label"])
        form = remplir(C["formulaire_nom"], label=n["label"])
        if not a.get("promesse"):
            err.append(f"{n['cle']} : angles.json sans « promesse » (la phrase que l'annonce et le formulaire doivent dire à l'identique)")
        intro = n["resume"].get("formulaire_intro") or {}
        if a.get("promesse") and norm(a["promesse"]) not in norm(f"{intro.get('titre', '')} {intro.get('texte', '')}"):
            err.append(f"{n['cle']} : resume.json → formulaire_intro ne dit pas « {a['promesse']} » : le nouveau formulaire reprendrait la promesse de l'ABO")
        if len(angles) < int(C["angles_min"]):
            err.append(f"{n['cle']} : {len(angles)} angle(s), au moins {C['angles_min']} attendus (un ad set par angle)")
        vus = set()
        for i, ang in enumerate(angles, 1):
            cle = ang.get("cle") or f"{code}{i}"
            if cle in vus:
                err.append(f"{n['cle']} : clé d'angle en double {cle}")
            vus.add(cle)
            st = ang.get("statiques", [])
            if not int(C["statiques_min"]) <= len(st) <= int(C["statiques_max"]):
                err.append(f"{cle} : {len(st)} statique(s), entre {C['statiques_min']} et {C['statiques_max']} attendues")
            adset = remplir(C["adset_nom"], agence=P["agence"]["nom"], angle=cle, titre=ang.get("titre", ""), label=n["label"])
            for j, s in enumerate(st, 1):
                k = f"{cle}-S{j:02d}"
                base = f"{n.get('dossier', n['cle'])}/cbo/statiques/{k}"
                ligne = {"niche": n["cle"], "campagne": camp, "formulaire": form, "angle": cle, "angle_titre": ang.get("titre", ""),
                         "gagnant_de_depart": ang.get("gagnant_de_depart", ""), "adset": adset, "annonce": k, "format_visuel": s.get("format", ""),
                         "fichier_4x5": f"{base}-4x5.jpg", "fichier_9x16": f"{base}-9x16.jpg", "accroche_image": s.get("accroche", ""),
                         "texte_court": s.get("texte_court") or ang.get("texte_court", ""), "texte_principal": s.get("texte") or ang.get("texte_principal", ""),
                         "texte_long": s.get("texte_long") or ang.get("texte_long", ""), "titre": s.get("titre", ""),
                         "description": s.get("description") or ang.get("description", ""), "bouton": s.get("bouton") or C["bouton"]}
                manque = [c for c in ("format_visuel", "accroche_image", "texte_principal", "titre") if not ligne[c]]
                if manque:
                    err.append(f"{k} : copy incomplète ({', '.join(manque)})")
                for t in textes_de(ligne):
                    for x in interdites:
                        if norm(x) in norm(t):
                            err.append(f"{k} : « {x} » (ancienne promesse) dans « {t[:70]} »")
                    for lu, bon in fautes_accents(t, C["accents_permis"]):
                        err.append(f"{k} : « {lu} » sans accent (→ {bon})")
                lignes.append(ligne)
    return lignes, err, avert


def taille_image(chemin):
    try:
        from PIL import Image
    except ImportError:
        return None
    with Image.open(chemin) as im:
        return im.size


def etape_grille(P, niches, opts):
    lignes, err, avert = construire_grille(P, niches)
    C = conf(P)
    if "--fichiers" in opts:
        for li in lignes:
            for fmt in ("4x5", "9x16"):
                f = P.racine / li[f"fichier_{fmt}"]
                if not f.exists():
                    err.append(f"{li['annonce']} : visuel {fmt} absent ({li[f'fichier_{fmt}']})")
                    continue
                t = taille_image(f)
                if t and list(t) != list(C["formats"][fmt]):
                    err.append(f"{li['annonce']} : {f.name} fait {t[0]}×{t[1]}, attendu {C['formats'][fmt][0]}×{C['formats'][fmt][1]}")
    sortie = P.racine / "cbo" / "annonces.csv"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    with sortie.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLONNES, delimiter=";")
        w.writeheader()
        w.writerows(lignes)
    par_niche = Counter(li["niche"] for li in lignes)
    for niche, nb in par_niche.items():
        sets = Counter(li["adset"] for li in lignes if li["niche"] == niche)
        camp = next(li["campagne"] for li in lignes if li["niche"] == niche)
        print(f"{camp} : {len(sets)} ad sets, {nb} annonces, {nb * 2} visuels")
        for s, k in sets.items():
            print(f"   {s} : {k} statiques")
    print(f"→ {sortie.relative_to(P.racine)} ({len(lignes)} lignes, une par annonce, copy comprise)")
    for x in avert:
        print("ATTENTION :", x)
    for x in err:
        print("ERREUR :", x)
    return 1 if err else 0


# ---------------------------------------------------------------- relevé d'aperçu des formulaires
def chemins_attendus(P, n):
    C = conf(P)
    _, _, _, tranches, k = questions(P, n)
    sous = NON_QUALIFIES.get(C.get("non_qualifies"), (None,))[0]
    return {t: (sous if i < k else "prospect") for i, t in enumerate(tranches)}


def fichier_meta(P, nom, simulation):
    base, ext = nom.rsplit(".", 1)
    return P.racine / "_meta" / (f"{base}.dry-run.{ext}" if simulation else nom)


def etape_apercu(P, niches, opts):
    simulation = "--dry-run" in opts
    C = conf(P)
    etat_f = fichier_meta(P, "cbo-etat-lu.json", simulation)
    lu = json.loads(etat_f.read_text(encoding="utf-8")) if etat_f.exists() else {}
    ids = {f["nom"]: f["id"] for f in lu.get("formulaires", [])}
    modele = {}
    for n in niches:
        nom = remplir(C["formulaire_nom"], label=n["label"])
        a = charger_angles(n)
        print(f"===== {nom}")
        print(f"  1. L'intro dit exactement : « {a.get('promesse', '?')} »")
        for t, att in chemins_attendus(P, n).items():
            print(f"  2. Réponse « {t} » → {att or 'À DÉCIDER (cbo.non_qualifies)'}")
        print("  3. Chaque écran relu mot à mot : accents, apostrophes, majuscules")
        print("  4. Le lien de confidentialité ouvre la page de confidentialité, pas l'accueil du site")
        modele[nom] = {"id": ids.get(nom), "vu_le": None, "par": None, "chemins": {t: None for t in chemins_attendus(P, n)},
                       "promesse_lue": None, "accents_relus": None, "confidentialite_ouvre": None}
    f = fichier_meta(P, "apercu-formulaires.json", simulation)
    if f.exists():
        print(f"\n{f.relative_to(P.racine)} existe déjà : à compléter, jamais réécrit par ce script")
    else:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(modele, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nrelevé à remplir après l'aperçu : {f.relative_to(P.racine)} "
              f"(chemins : {', '.join(sorted({v[0] for v in NON_QUALIFIES.values()}))})")
    return 0


# ---------------------------------------------------------------- lecture de l'état réel
CHAMPS_CREATIVE = "creative{id,object_story_spec,asset_feed_spec}"


def format_de(w, h):
    if not w or not h:
        return None
    r = w / h
    for nom, cible in (("4x5", 0.8), ("9x16", 9 / 16), ("1x1", 1.0)):
        if abs(r - cible) < 0.02:
            return nom
    return f"{w}x{h}"


def formulaire_de(cr):
    ld = (cr.get("object_story_spec") or {}).get("link_data") or {}
    f = ((ld.get("call_to_action") or {}).get("value") or {}).get("lead_gen_form_id")
    for cta in (cr.get("asset_feed_spec") or {}).get("call_to_actions", []):
        f = f or (cta.get("value") or {}).get("lead_gen_form_id")
    return f


def normaliser_pub(a, dims):
    """Une publicité lue par l'API → ce que vérifie `verifier` (formats, vertical en story/reels, formulaire, textes)."""
    cr = a.get("creative") or {}
    afs = cr.get("asset_feed_spec") or {}
    ld = (cr.get("object_story_spec") or {}).get("link_data") or {}
    images = afs.get("images") or ([{"hash": ld["image_hash"]}] if ld.get("image_hash") else [])
    fmt = {im["hash"]: format_de(*dims.get(im["hash"], (None, None))) for im in images if im.get("hash")}
    par_label = {lab["name"]: im["hash"] for im in images for lab in im.get("adlabels", [])}
    vertical = False
    for r in afs.get("asset_customization_rules", []):
        sp = r.get("customization_spec") or {}
        pos = set(sp.get("instagram_positions", [])) | set(sp.get("facebook_positions", []))
        h = par_label.get((r.get("image_label") or {}).get("name"))
        vertical = vertical or (fmt.get(h) == "9x16" and bool(pos & {"story", "reels", "facebook_reels"}))
    return {"id": a.get("id"), "nom": a.get("name", ""), "adset": a.get("adset_id"), "campagne": a.get("campaign_id"),
            "statut": a.get("status"), "statut_effectif": a.get("effective_status"), "formulaire": formulaire_de(cr),
            "formats": sorted({x for x in fmt.values() if x}), "vertical_en_story": vertical,
            "texte": ((afs.get("bodies") or [{}])[0].get("text")) or ld.get("message", ""),
            "titre": ((afs.get("titles") or [{}])[0].get("text")) or ld.get("name", ""), "problemes": a.get("issues_info") or []}


def normaliser_formulaire(f):
    cc, ty = f.get("context_card") or {}, f.get("thank_you_page") or {}
    return {"id": f.get("id"), "nom": f.get("name", ""), "statut": f.get("status"),
            "intro_titre": cc.get("title", ""), "intro_texte": " ".join(cc.get("content") or []),
            "questions": [{"label": q.get("label", q.get("type")), "options": [o.get("value") for o in q.get("options", [])]} for q in f.get("questions", [])],
            "fin_titre": ty.get("title", ""), "fin_texte": ty.get("body", ""), "fin_bouton": ty.get("button_text", ""),
            "lien_confidentialite": f.get("privacy_policy_url")}


def lire_reel(P, lignes):
    from meta import Meta
    M = Meta(P)
    pt = M.page_token()
    noms = {li["campagne"] for li in lignes}
    camps = [c for c in M.toutes(f"{M.act}/campaigns", fields="id,name,status,effective_status,daily_budget,lifetime_budget,objective", limit=200)
             if c["name"] in noms]
    sets, brutes = [], []
    for c in camps:
        sets += M.toutes(f"{c['id']}/adsets", fields="id,name,campaign_id,status,effective_status,daily_budget,lifetime_budget", limit=200)
        brutes += M.toutes(f"{c['id']}/ads", fields="id,name,adset_id,campaign_id,status,effective_status,issues_info," + CHAMPS_CREATIVE, limit=200)
    hashes = set()
    for a in brutes:
        cr = a.get("creative") or {}
        hashes |= {im.get("hash") for im in (cr.get("asset_feed_spec") or {}).get("images", [])}
        hashes.add(((cr.get("object_story_spec") or {}).get("link_data") or {}).get("image_hash"))
    hashes = sorted(h for h in hashes if h)
    dims = {}
    for i in range(0, len(hashes), 50):
        for im in M.toutes(f"{M.act}/adimages", hashes=hashes[i:i + 50], fields="hash,width,height"):
            dims[im["hash"]] = (im.get("width"), im.get("height"))
    pubs = [normaliser_pub(a, dims) for a in brutes]
    voulus = {li["formulaire"] for li in lignes}
    ids = {f["id"] for f in M.formulaires() if f["name"] in voulus} | {p["formulaire"] for p in pubs if p["formulaire"]}
    forms = []
    champs = "id,name,status,questions{key,label,type,options},context_card{title,content},thank_you_page{title,body,button_text,website_url}"
    for fid in sorted(ids):
        f = M.get(fid, token=pt, fields=champs + ",privacy_policy_url")
        if "error" in f:   # lien de confidentialité parfois illisible par l'API : il se relève alors dans l'aperçu
            f = M.get(fid, token=pt, fields=champs)
        if "error" not in f:
            forms.append(normaliser_formulaire(f))
    ids_camps = {c["id"] for c in camps}
    autres = []
    for a in M.toutes(f"{M.act}/ads", fields="id,name,campaign{name}," + CHAMPS_CREATIVE, effective_status=["ACTIVE"], limit=200):
        if (a.get("campaign") or {}).get("id") not in ids_camps:
            autres.append({"id": a["id"], "nom": a.get("name", ""), "campagne": (a.get("campaign") or {}).get("name", ""),
                           "formulaire": formulaire_de(a.get("creative") or {})})
    noms_f = {x["id"]: x["name"] for st in ("ACTIVE", "ARCHIVED") for x in M.formulaires(st)}
    for a in autres:
        a["formulaire_nom"] = noms_f.get(a["formulaire"], a["formulaire"] or "sans formulaire")
    return {"source": "api", "campagnes": [{"id": c["id"], "nom": c["name"], "statut": c.get("status"), "statut_effectif": c.get("effective_status"),
                                             "budget_jour": c.get("daily_budget"), "budget_total": c.get("lifetime_budget")} for c in camps],
            "adsets": [{"id": s["id"], "nom": s["name"], "campagne": s.get("campaign_id"), "statut": s.get("status"),
                        "budget_jour": s.get("daily_budget"), "budget_total": s.get("lifetime_budget")} for s in sets],
            "pubs": pubs, "formulaires": forms, "autres_pubs_actives": autres}


def etat_simule(P, niches, lignes, pieges=False):
    """Un compte où le push a été fait comme il faut ; avec pieges=True, les erreurs vues sur un vrai compte en novembre 2026."""
    C, f = conf(P), P["formulaire"]
    etat = {"source": "simulation", "campagnes": [], "adsets": [], "pubs": [], "formulaires": [], "autres_pubs_actives": []}
    apercu, seq = {}, Counter()

    def nid(t):
        seq[t] += 1
        return f"SIM-{t}{seq[t]:03d}"

    for n in niches:
        nl = [li for li in lignes if li["niche"] == n["cle"]]
        q1, r1, q2, r2, _ = questions(P, n)
        intro = n["resume"].get("formulaire_intro") or {}
        fid = nid("F")
        etat["formulaires"].append({"id": fid, "nom": nl[0]["formulaire"], "statut": "ACTIVE", "intro_titre": intro.get("titre", ""),
                                    "intro_texte": intro.get("texte", ""), "questions": [{"label": q1, "options": r1}, {"label": q2, "options": r2}],
                                    "fin_titre": f["page_fin"]["titre"], "fin_texte": f["page_fin"]["texte"], "fin_bouton": f["page_fin"]["bouton"],
                                    "lien_confidentialite": f.get("lien_confidentialite")})
        apercu[nl[0]["formulaire"]] = {"id": fid, "vu_le": dt.datetime.now().isoformat(timespec="minutes"), "par": "simulation",
                                       "chemins": chemins_attendus(P, n), "promesse_lue": True, "accents_relus": True,
                                       "confidentialite_ouvre": f.get("lien_confidentialite")}
        cid = nid("C")
        etat["campagnes"].append({"id": cid, "nom": nl[0]["campagne"], "statut": "PAUSED", "statut_effectif": "PAUSED",
                                  "budget_jour": str(int(float(C.get("budget_jour_par_campagne", 30)) * 100)), "budget_total": None})
        for s in dict.fromkeys(li["adset"] for li in nl):
            sid = nid("A")
            etat["adsets"].append({"id": sid, "nom": s, "campagne": cid, "statut": "PAUSED", "budget_jour": None, "budget_total": None})
            for li in [x for x in nl if x["adset"] == s]:
                etat["pubs"].append({"id": nid("P"), "nom": f"{li['annonce']} | {li['accroche_image']}", "adset": sid, "campagne": cid,
                                     "statut": "PAUSED", "statut_effectif": "PAUSED", "formulaire": fid, "formats": ["4x5", "9x16"],
                                     "vertical_en_story": True, "texte": li["texte_principal"], "titre": li["titre"], "problemes": []})
    if pieges and len(niches) >= 2:
        # 1. « C'est fait » alors que la deuxième campagne n'existe pas, et que la première n'a qu'un ad set.
        absente = etat["campagnes"].pop(1)["id"]
        etat["adsets"] = [s for s in etat["adsets"] if s["campagne"] != absente]
        etat["pubs"] = [p for p in etat["pubs"] if p["campagne"] != absente]
        premier = next(s for s in etat["adsets"] if s["campagne"] == etat["campagnes"][0]["id"])
        etat["adsets"] = [s for s in etat["adsets"] if s["campagne"] != etat["campagnes"][0]["id"] or s is premier]
        etat["pubs"] = [p for p in etat["pubs"] if p["campagne"] != etat["campagnes"][0]["id"] or p["adset"] == premier["id"]]
        etat["formulaires"].pop(1)
        fo = etat["formulaires"][0]
        n0 = niches[0]
        # 2. Le formulaire reprend la promesse de l'ABO, 3. sans accents, 4. avec un lien de confidentialité vers l'accueil.
        fo["intro_titre"] = textes_pub(P, n0)["card_title"]
        fo["fin_titre"], fo["fin_texte"] = "Derniere etape : reservez votre etude", "Choisissez votre creneau dans notre calendrier."
        fo["lien_confidentialite"] = P["agence"]["site"].rstrip("/") + "/"
        # 5. La logique conditionnelle oubliée : sous le seuil, le formulaire part quand même.
        ap = apercu[fo["nom"]]
        premiere = next(iter(ap["chemins"]))
        ap["chemins"][premiere] = "prospect"
        ap["confidentialite_ouvre"] = fo["lien_confidentialite"]
        apercu = {fo["nom"]: ap}
        # 6. Des annonces de l'ABO toujours actives, branchées sur l'ancien formulaire et l'ancienne offre.
        etat["autres_pubs_actives"] = [{"id": f"SIM-OLD{i}", "nom": f"{n0['label']} · N10{i}", "campagne": P.nom_campagne(),
                                        "formulaire": "SIM-ANCIEN", "formulaire_nom": P.nom_formulaire(n0)} for i in (1, 3, 8)]
    return etat, apercu


def etape_lire(P, niches, opts):
    simulation = "--dry-run" in opts
    lignes, err, _ = construire_grille(P, niches)
    if not lignes:
        raise SystemExit("grille vide : lance d'abord `grille` et corrige ses erreurs")
    if simulation:
        etat, apercu = etat_simule(P, niches, lignes, pieges="--pieges" in opts)
        fa = fichier_meta(P, "apercu-formulaires.json", True)
        fa.parent.mkdir(parents=True, exist_ok=True)
        fa.write_text(json.dumps(apercu, indent=1, ensure_ascii=False), encoding="utf-8")
    else:
        etat = lire_reel(P, lignes)
    etat["lu_le"] = dt.datetime.now().isoformat(timespec="seconds")
    f = fichier_meta(P, "cbo-etat-lu.json", simulation)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(etat, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"état lu{' (simulation)' if simulation else ''} : {len(etat['campagnes'])} campagne(s), {len(etat['adsets'])} ad set(s), "
          f"{len(etat['pubs'])} publicité(s), {len(etat['formulaires'])} formulaire(s), "
          f"{len(etat['autres_pubs_actives'])} autre(s) publicité(s) active(s) → {f.relative_to(P.racine)}")
    return 0


# ---------------------------------------------------------------- vérification
def verifier_etat(P, niches, lignes, etat, apercu, maintenant=None):
    """(erreurs, avertissements, résumé). Aucune erreur = push vérifié."""
    C, err, avert = conf(P), [], []
    maintenant = maintenant or dt.datetime.now()
    lu = dt.datetime.fromisoformat(etat.get("lu_le", "1970-01-01T00:00:00"))
    if (maintenant - lu).total_seconds() > 60 * float(C["fraicheur_minutes"]):
        err.append(f"état lu à {lu:%d/%m %H:%M} : trop ancien, relance `lire` (toute création après cette heure n'y est pas)")
    if C.get("non_qualifies") not in NON_QUALIFIES:
        err.append("cbo.non_qualifies non décidé : sous le seuil, veut-on aucune trace (sans_trace), une réservation marquée (reservation_marquee) "
                   "ou une liste « non qualifiés » (liste, Meta les compte alors comme prospects) ? À trancher avec la personne avant de publier")
    resume = {"campagnes": [], "formulaires": []}
    camps = {}
    for c in etat["campagnes"]:
        camps.setdefault(c["nom"], []).append(c)
    forms = {}
    for f in etat["formulaires"]:
        forms.setdefault(f["nom"], []).append(f)
    for n in niches:
        nl = [li for li in lignes if li["niche"] == n["cle"]]
        if not nl:
            continue
        a = charger_angles(n)
        # --- formulaire
        fnom = nl[0]["formulaire"]
        actifs = [f for f in forms.get(fnom, []) if f["statut"] == "ACTIVE"]
        fo = actifs[0] if len(actifs) == 1 else None
        if not actifs:
            err.append(f"formulaire « {fnom} » absent ou inactif")
        elif len(actifs) > 1:
            err.append(f"{len(actifs)} formulaires actifs s'appellent « {fnom} » : impossible de savoir lequel est le bon")
        if fo:
            textes = [fo["intro_titre"], fo["intro_texte"], fo["fin_titre"], fo["fin_texte"], fo["fin_bouton"]] + \
                     [q["label"] for q in fo["questions"]] + [o for q in fo["questions"] for o in q["options"]]
            if norm(a.get("promesse")) not in norm(f"{fo['intro_titre']} {fo['intro_texte']}"):
                err.append(f"« {fnom} » : l'intro ne dit pas la promesse des annonces « {a.get('promesse')} » (lu : « {fo['intro_titre']} »)")
            for x in a.get("expressions_interdites", []):
                if any(norm(x) in norm(t) for t in textes):
                    err.append(f"« {fnom} » : « {x} » (ancienne promesse) dans le formulaire")
            fautes = [f"{lu} → {bon}" for t in textes for lu, bon in fautes_accents(t, C["accents_permis"])]
            if fautes:
                err.append(f"« {fnom} » : mots sans accent : {', '.join(dict.fromkeys(fautes))}")
            if any(sans_aucun_accent(t) for t in textes):
                avert.append(f"« {fnom} » : un texte long sans aucun accent, à relire")
            _, _, q2, r2, _ = questions(P, n)
            q = next((x for x in fo["questions"] if norm(x["label"]) == norm(q2)), None)
            if not q:
                err.append(f"« {fnom} » : question « {q2} » absente")
            elif [norm(o) for o in q["options"]] != [norm(o) for o in r2]:
                err.append(f"« {fnom} » : tranches de chiffre d'affaires différentes de la configuration ({q['options']})")
            lien = fo.get("lien_confidentialite")
            ap = apercu.get(fnom) or {}
            if ap.get("id") != fo["id"]:
                err.append(f"« {fnom} » : aucun relevé d'aperçu pour ce formulaire (id {fo['id']}) : `apercu`, tester chaque réponse, remplir le relevé")
            else:
                for t, att in chemins_attendus(P, n).items():
                    vu = ap.get("chemins", {}).get(t)
                    if vu is None:
                        err.append(f"« {fnom} » : réponse « {t} » non testée en aperçu")
                    elif att and vu != att:
                        err.append(f"« {fnom} » : réponse « {t} » → {vu} en aperçu, attendu {att} (logique conditionnelle absente ou fausse)")
                for champ, quoi in (("promesse_lue", "promesse relue dans l'aperçu"), ("accents_relus", "accents relus dans l'aperçu")):
                    if ap.get(champ) is not True:
                        err.append(f"« {fnom} » : {quoi} : non confirmé")
                lien = lien or ap.get("confidentialite_ouvre")
                if etat.get("source") == "api" and ap.get("par") == "simulation":
                    err.append(f"« {fnom} » : relevé d'aperçu simulé : il faut un vrai aperçu")
            attendu = P.get("formulaire", "lien_confidentialite")
            if not lien:
                err.append(f"« {fnom} » : lien de confidentialité inconnu (illisible par l'API) : le relever dans l'aperçu")
            elif lien_vers_accueil(lien, P["agence"].get("site")):
                err.append(f"« {fnom} » : le lien de confidentialité ouvre l'accueil du site ({lien}), pas la page de confidentialité")
            elif attendu and norm(lien).rstrip("/") != norm(attendu).rstrip("/"):
                err.append(f"« {fnom} » : lien de confidentialité {lien}, attendu {attendu}")
            resume["formulaires"].append({"nom": fnom, "id": fo["id"], "non_qualifies": C.get("non_qualifies")})
        # --- campagne
        cnom = nl[0]["campagne"]
        cs = camps.get(cnom, [])
        if not cs:
            err.append(f"campagne absente du compte : « {cnom} » ({len(nl)} annonces attendues, aucune en ligne)")
            continue
        if len(cs) > 1:
            err.append(f"{len(cs)} campagnes s'appellent « {cnom} »")
        c = cs[0]
        if not (c.get("budget_jour") or c.get("budget_total")):
            err.append(f"« {cnom} » : pas de budget au niveau de la campagne, ce n'est pas une CBO")
        if c["statut"] == "ACTIVE":
            avert.append(f"« {cnom} » est déjà active : les nouveaux ad sets en pause ne diffusent pas, toute annonce active dedans diffuse")
        sets = [s for s in etat["adsets"] if s["campagne"] == c["id"]]
        par_nom = {}
        for s in sets:
            par_nom.setdefault(s["nom"], []).append(s)
        rc = {"nom": cnom, "id": c["id"], "statut": c["statut"], "budget_jour": c.get("budget_jour"), "adsets": []}
        autres_sets = [s for s in par_nom if s not in {li["adset"] for li in nl}]
        if autres_sets:
            avert.append(f"« {cnom} » contient aussi les ad sets : {', '.join(autres_sets)} (vague précédente ?)")
        for snom in dict.fromkeys(li["adset"] for li in nl):
            sl = [li for li in nl if li["adset"] == snom]
            ss = par_nom.get(snom, [])
            if not ss:
                err.append(f"« {cnom} » : ad set « {snom} » absent ({len(sl)} annonces attendues)")
                continue
            if len(ss) > 1:
                err.append(f"« {cnom} » : {len(ss)} ad sets « {snom} »")
            s = ss[0]
            if s["statut"] != "PAUSED":
                err.append(f"ad set « {snom} » {s['statut']} : tout doit être créé en pause")
            if s.get("budget_jour") or s.get("budget_total"):
                err.append(f"ad set « {snom} » porte son propre budget : c'est de l'ABO, pas de la CBO")
            pubs = [p for p in etat["pubs"] if p["adset"] == s["id"]]
            for li in sl:
                ps = [p for p in pubs if p["nom"].split(" | ")[0].strip() == li["annonce"]]
                if not ps:
                    err.append(f"{li['annonce']} absente de « {snom} »")
                    continue
                if len(ps) > 1:
                    err.append(f"{li['annonce']} : {len(ps)} publicités du même nom dans « {snom} »")
                p = ps[0]
                if p["statut"] != "PAUSED":
                    err.append(f"{li['annonce']} créée {p['statut']} : tout doit être créé en pause")
                if p["statut_effectif"] in ("DISAPPROVED", "WITH_ISSUES") or p.get("problemes"):
                    err.append(f"{li['annonce']} : {p['statut_effectif']} {p.get('problemes') or ''}".strip())
                if not fo or p["formulaire"] != fo["id"]:
                    vrai = next((f["nom"] for f in etat["formulaires"] if f["id"] == p["formulaire"]), p["formulaire"])
                    err.append(f"{li['annonce']} branchée sur « {vrai} » au lieu de « {fnom} »")
                manque = [x for x in ("4x5", "9x16") if x not in p["formats"]]
                if manque:
                    err.append(f"{li['annonce']} : visuel {' et '.join(manque)} absent")
                elif not p["vertical_en_story"]:
                    err.append(f"{li['annonce']} : le 9:16 n'est pas affecté aux stories et reels")
                if norm(p["texte"]) != norm(li["texte_principal"]) or norm(p["titre"]) != norm(li["titre"]):
                    err.append(f"{li['annonce']} : texte ou titre différent de cbo/annonces.csv")
            hors = [p["nom"] for p in pubs if p["nom"].split(" | ")[0].strip() not in {li["annonce"] for li in sl}]
            if hors:
                avert.append(f"« {snom} » contient aussi : {', '.join(hors)}")
            rc["adsets"].append({"nom": snom, "id": s["id"], "statut": s["statut"], "pubs": len(pubs),
                                 "statuts_effectifs": dict(Counter(p["statut_effectif"] for p in pubs))})
        resume["campagnes"].append(rc)
    anciennes = etat.get("autres_pubs_actives", [])
    if anciennes:
        par_form = Counter(a.get("formulaire_nom") or a.get("formulaire") for a in anciennes)
        avert.append(f"{len(anciennes)} publicité(s) active(s) hors de la nouvelle structure, encore sur l'ancienne offre : "
                     + ", ".join(f"{k} ({v})" for k, v in par_form.items()) + " : les montrer à la personne (couper, garder, ou rebrancher)")
    resume["anciennes_pubs_actives"] = anciennes
    return err, avert, resume


def etape_verifier(P, niches, opts):
    simulation = "--dry-run" in opts
    fe, fa = fichier_meta(P, "cbo-etat-lu.json", simulation), fichier_meta(P, "apercu-formulaires.json", simulation)
    if not fe.exists():
        raise SystemExit(f"{fe.relative_to(P.racine)} absent : lance `lire` d'abord (on ne vérifie jamais de mémoire)")
    etat = json.loads(fe.read_text(encoding="utf-8"))
    if not simulation and etat.get("source") != "api":
        raise SystemExit("l'état lu ne vient pas de l'API : relance `lire` sans --dry-run")
    apercu = json.loads(fa.read_text(encoding="utf-8")) if fa.exists() else {}
    lignes, err_g, _ = construire_grille(P, niches)
    err, avert, resume = verifier_etat(P, niches, lignes, etat, apercu)
    err = err_g + err
    sortie = fichier_meta(P, "push-verified.json", simulation)
    if sortie.exists():
        sortie.unlink()   # une preuve ancienne ne doit jamais survivre à une vérification ratée
    for x in avert:
        print("ATTENTION :", x)
    if err:
        for x in err:
            print("ERREUR :", x)
        print(f"\nNON VÉRIFIÉ : {len(err)} écart(s). Ne dis pas que c'est fait. Corrige, relance `lire`, puis `verifier`.")
        return 1
    preuve = {"verifie_le": dt.datetime.now().isoformat(timespec="seconds"), "source": etat.get("source"), "etat_lu_le": etat.get("lu_le"),
              "annonces": sum(a["pubs"] for c in resume["campagnes"] for a in c["adsets"]), **resume, "avertissements": avert}
    sortie.write_text(json.dumps(preuve, indent=1, ensure_ascii=False), encoding="utf-8")
    for c in resume["campagnes"]:
        print(f"{c['nom']} | {c['statut']}")
        for a in c["adsets"]:
            print(f"   {a['nom']} | {a['statut']} | {a['pubs']} pubs {a['statuts_effectifs']}")
    print(f"VÉRIFIÉ : {preuve['annonces']} annonces conformes, relues à {etat.get('lu_le', '?')[11:16]} → {sortie.relative_to(P.racine)}")
    return 0


ETAPES = {"gagnants": etape_gagnants, "grille": etape_grille, "apercu": etape_apercu, "lire": etape_lire, "verifier": etape_verifier}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    args = [a for a in argv if not a.startswith("--")]
    opts = {a for a in argv if a.startswith("--")}
    if len(args) < 2 or args[1] not in ETAPES:
        print(__doc__)
        return 2
    P = Projet(args[0], simulation="--dry-run" in opts)
    if args[1] == "gagnants":
        return etape_gagnants(P, args[2:], opts)
    return ETAPES[args[1]](P, P.niches(args[2:]), opts)


if __name__ == "__main__":
    sys.exit(main())
