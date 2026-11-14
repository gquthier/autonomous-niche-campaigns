"""Lecture du projet : projet.json à la racine du dossier de travail, resume.json de chaque niche, état des identifiants Meta.

Les secrets se lisent uniquement dans des variables d'environnement et ne s'affichent jamais.
Les identifiants Meta (compte, page, Instagram, business) se lisent dans projet.json, sinon dans les variables
META_AD_ACCOUNT, META_PAGE_ID, META_INSTAGRAM_ID, META_BUSINESS_ID.
En simulation (--dry-run), l'état est écrit dans _meta/etat.dry-run.json : il ne se mélange jamais avec l'état réel."""
import datetime as _dt
import json
import os
from pathlib import Path

MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
ENV_META = {"ad_account": "META_AD_ACCOUNT", "page_id": "META_PAGE_ID", "instagram_user_id": "META_INSTAGRAM_ID", "business_id": "META_BUSINESS_ID"}
CLES_RESUME = ("cible_pub", "unite_longue", "unite_courte", "unite_manquante", "volume_garanti", "remboursement_par_unite", "ligne_metier")


class Projet:
    def __init__(self, chemin, simulation=False):
        p = Path(chemin).expanduser().resolve()
        self.fichier = p / "projet.json" if p.is_dir() else p
        if not self.fichier.exists():
            raise SystemExit(f"projet.json introuvable : {self.fichier} (copier assets/projet.exemple.json et le remplir)")
        self.racine = self.fichier.parent
        self.simulation = simulation
        self.cfg = json.loads(self.fichier.read_text(encoding="utf-8"))
        self.etat_fichier = self.racine / "_meta" / ("etat.dry-run.json" if simulation else "etat.json")
        self.etat = json.loads(self.etat_fichier.read_text(encoding="utf-8")) if self.etat_fichier.exists() else {}
        for k in ("formulaires_base", "formulaires", "adsets", "images", "creatives", "pubs"):
            self.etat.setdefault(k, {})

    # ---------- configuration ----------
    def __getitem__(self, k):
        return self.cfg[k]

    def get(self, *chemin, defaut=None):
        x = self.cfg
        for k in chemin:
            if not isinstance(x, dict) or k not in x:
                return defaut
            x = x[k]
        return x

    @staticmethod
    def secret(variable):
        """Variable d'environnement seulement ; jamais affichée, jamais écrite."""
        v = os.environ.get(variable, "").strip()
        if not v:
            raise SystemExit(f"secret {variable} absent : l'exporter dans le terminal (voir .env.example), ou lancer avec --dry-run")
        return v

    def meta_id(self, champ, requis=True):
        """Identifiant Meta : projet.json → meta.<champ>, sinon la variable d'environnement correspondante."""
        v = str(self.get("meta", champ, defaut="") or "").strip() or os.environ.get(ENV_META.get(champ, ""), "").strip()
        if not v and requis:
            raise SystemExit(f"meta.{champ} vide dans projet.json et variable {ENV_META.get(champ)} absente")
        return v or None

    def nom_campagne(self):
        maintenant = _dt.date.today()
        return self.get("campagne", "nom", defaut="Instant Form - ABO | Niches | {mois}").replace("{mois}", f"{MOIS[maintenant.month - 1]} {maintenant.year}")

    # ---------- niches ----------
    def niches(self, seulement=()):
        """Les niches du projet, avec leur resume.json chargé (clé `resume`, vide s'il manque)."""
        seulement = set(seulement or ())
        out = []
        for i, n in enumerate(self.cfg.get("niches", []), start=1):
            if seulement and not ({n["cle"], n.get("dossier", "")} & seulement):
                continue
            d = self.racine / n.get("dossier", n["cle"])
            r = d / "resume.json"
            out.append({**n, "rang": i, "chemin": d, "resume": json.loads(r.read_text(encoding="utf-8")) if r.exists() else {}})
        if seulement and not out:
            raise SystemExit(f"aucune niche ne correspond à {sorted(seulement)}")
        return out

    def niche(self, cle):
        return self.niches([cle])[0]

    def nom_formulaire(self, n, base=False):
        modele = self.get("formulaire", "nom", defaut="IF - {label}")
        nom = modele.replace("{label}", n["label"])
        return f"{nom} (base)" if base else nom

    def lien_reservation(self, n, qualifie=True):
        """Le calendrier, avec de quoi rattacher la réservation à la niche, à la campagne et à l'ad set."""
        base = self["formulaire"]["lien_reservation"]
        med = "formulaire_instantane" if qualifie else "formulaire_instantane_non_qualifie"
        q = f"utm_source=meta&utm_medium={med}&utm_campaign={n['cle']}"
        if self.etat.get("campagne"):
            q += f"&utm_id={self.etat['campagne']}"
        if self.etat["adsets"].get(n["cle"]):
            q += f"&utm_term={self.etat['adsets'][n['cle']]}"
        return f"{base}{'&' if '?' in base else '?'}{q}"

    # ---------- état ----------
    def sauver(self):
        self.etat_fichier.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.etat_fichier.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.etat, indent=1, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.etat_fichier)


def textes_pub(projet, n, performance=False):
    """Le texte de la publicité d'une niche. resume.json peut fournir `texte_pub` (body, title, desc, card_title, card) pour l'imposer."""
    r, o = n["resume"], projet["offre"]
    if r.get("texte_pub"):
        t = dict(r["texte_pub"])
        if performance and o.get("variante_performance"):
            g = r.get("garantie_courte", o.get("garantie_courte", ""))
            t = {k: (v.replace(g, o["variante_performance"]).replace(g.rstrip("."), o["variante_performance"].rstrip(".")) if isinstance(v, str) else v) for k, v in t.items()}
        return t
    manque = [k for k in CLES_RESUME if k not in r]
    if manque:
        raise SystemExit(f"{n['cle']} : resume.json incomplet, il manque {manque} (voir references/offre.md)")
    jours = o.get("duree_jours", 90)
    garantie = o["variante_performance"] if performance else r.get("garantie_courte", o["garantie_courte"])
    prolong = o.get("prolongation_jours")
    remb = f"{garantie[:-1] if garantie.endswith('.') else garantie} : {r['remboursement_par_unite']} € remboursés par {r['unite_manquante']}" + (f", ou {prolong} jours de plus sans frais." if prolong else ".")
    lignes = [f"{r['cible_pub']} : {r['volume_garanti']} {r['unite_longue']} en {jours} jours.", "", r["ligne_metier"], "", remb]
    if o.get("installation"):
        lignes.append(o["installation"] + ("" if o["installation"].endswith(".") else "."))
    if o.get("budget_pub"):
        lignes.append(o["budget_pub"])
    lignes += ["", projet.get("formulaire", "consigne_pub", defaut="Répondez à deux questions, puis réservez votre étude dans notre calendrier.")]
    titre = f"{r['volume_garanti']} {r['unite_courte']} en {jours} jours"
    court = garantie[:-1] if garantie.endswith(".") else garantie
    carte = f"{r['cible_pub']} : {garantie[0].lower()}{garantie[1:]}" + (f" {o['installation']}." if o.get("installation") else "")
    return {"body": "\n".join(lignes), "title": titre, "desc": court, "card_title": titre, "card": carte}


def questions(projet, n):
    """(intitulé Q1, réponses Q1, intitulé Q2, réponses Q2, nombre de tranches sous le seuil) d'une niche."""
    r, f = n["resume"], projet.get("formulaire", defaut={}) or {}
    q1 = r.get("formulaire_q1") or f.get("question_profil", "Vous êtes ?")
    q2 = r.get("formulaire_q2") or f.get("question_ca", "Quel est votre chiffre d'affaires annuel ?")
    r1 = list(r.get("formulaire_q1_options") or [])
    r2 = list(r.get("formulaire_q2_options") or f.get("tranches_ca") or [])
    return q1, r1, q2, r2, int(f.get("tranches_non_qualifiees", 1))


def regles_logique(projet, n):
    """La logique conditionnelle attendue, réponse par réponse : (question, réponse, va vers, effet pour Meta).
    Q1 ne bloque personne ; sous le seuil, Q2 ferme le formulaire (aucun prospect) ; au-dessus, Q2 envoie le formulaire."""
    q1, r1, q2, r2, k = questions(projet, n)
    out = [(q1, a, f"Q2 {q2}", "-") for a in r1]
    for i, a in enumerate(r2):
        if i < k:
            out.append((q2, a, "Fermer le formulaire → page de fin des non-prospects", "aucun prospect"))
        else:
            out.append((q2, a, "Envoyer le formulaire → page de fin des prospects", "prospect"))
    return out


def controle_resume(projet, n):
    """Les incohérences d'un resume.json, en phrases. Liste vide = rien à signaler."""
    r, o = n["resume"], projet["offre"]
    if not r:
        return ["resume.json absent"]
    pb = []
    if not r.get("texte_pub"):
        pb += [f"clé manquante : {k}" for k in CLES_RESUME + ("formulaire_q1_options",) if k not in r]
    if r.get("label") and r["label"] != n["label"]:
        pb.append(f"label « {r['label']} » différent de projet.json « {n['label']} »")
    vol, remb, prix = r.get("volume_garanti"), r.get("remboursement_par_unite"), o.get("prix_ht")
    if isinstance(vol, int) and isinstance(remb, int) and isinstance(prix, (int, float)) and vol > 0:
        if abs(vol * remb - prix) > vol:
            pb.append(f"remboursement_par_unite × volume_garanti = {vol * remb}, loin de offre.prix_ht = {prix}")
    _, r1, _, r2, k = questions(projet, n)
    if r1 and len(r1) != 4:
        pb.append(f"« Vous êtes ? » a {len(r1)} réponses (attendu : trois profils + « Autre »)")
    for p in r.get("profils_vises", []):
        if p not in r1:
            pb.append(f"profil visé absent des réponses de Q1 : « {p} »")
    if r.get("formulaire_ca_min") and r2:
        if k >= len(r2) or r2[k] != r["formulaire_ca_min"]:
            attendu = r2[k] if k < len(r2) else "aucune"
            pb.append(f"formulaire_ca_min « {r['formulaire_ca_min']} » ne correspond pas à la première tranche qualifiée « {attendu} »")
    if r2 and k >= len(r2):
        pb.append("toutes les tranches sont sous le seuil : aucun prospect ne passerait")
    gp = r.get("garantie_phrase", "")
    for x in (vol, remb):
        if x is not None and gp and str(x) not in gp:
            pb.append(f"garantie_phrase ne reprend pas {x}")
    pp = r.get("promesse_pub", "")
    if pp and r.get("cible_pub") and not pp.startswith(r["cible_pub"]):
        pb.append("promesse_pub ne commence pas par cible_pub")
    if pp and vol is not None and str(vol) not in pp:
        pb.append("promesse_pub ne reprend pas volume_garanti")
    if "bonus" in r and len(r["bonus"]) != 4:
        pb.append(f"{len(r['bonus'])} bonus (attendu : 4)")
    return pb
