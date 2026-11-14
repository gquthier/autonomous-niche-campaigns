#!/usr/bin/env python3
"""Contrôle d'une séquence de relance (references/sequence-email.md) avant toute mise en ligne :
- chaque niche du projet (et `defaut`) a ses 6 e-mails E-IF-1 à E-IF-6, avec objet et texte ;
- seulement les variables {prenom}, {lien_reservation}, {pied_email} ; un seul {lien_reservation} ; {pied_email} en dernière ligne,
  précédé de la signature du projet (agence.signature_email) ;
- au plus 130 mots hors pied ; objet de 60 signes au plus ; aucun mot de projet.json → sequences.mots_interdits ; ni « Re: » dans l'objet, ni point d'exclamation, ni émoji, ni prix (le prix se donne pendant l'appel) ;
- chaque nombre du texte se retrouve dans les sources de sa niche (resume.json, offre.md, analyse.md, publicite.md), dans l'offre du projet,
  ou dans projet.json → sequences.nombres_permis (par défaut « 30 », la durée de l'étude).
  Les numéros de liste en début de ligne (« 1. ») ne comptent pas ; « 6 » n'est pas retrouvé dans « 600 000 ».
Usage : python3 verifier.py <projet> [chemin du JSON, par défaut <projet>/sequences-email/sequence-formulaire.json]"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from projet import Projet  # noqa: E402

if len(sys.argv) < 2:
    sys.exit(__doc__)
P = Projet(sys.argv[1])
F = Path(sys.argv[2]) if len(sys.argv) > 2 else P.racine / "sequences-email" / "sequence-formulaire.json"
S = json.loads(F.read_text(encoding="utf-8"))
CODES = [f"E-IF-{i}" for i in range(1, 7)]
VARS = {"prenom", "lien_reservation", "pied_email"}
SIGNATURE = P.get("agence", "signature_email", defaut="")
INTERDITS = [m.lower() for m in P.get("sequences", "mots_interdits", defaut=["lead", "leads"])]
PERMIS = set(P.get("sequences", "nombres_permis", defaut=["30"]))
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")
PRIX = re.compile(r"\b\d[\d\s  ]*(?:,\d+)?\s?(?:€|euros?)\b.*\b(?:HT|TTC|par mois|/mois)\b", re.I)
erreurs = []


def err(n, c, m):
    erreurs.append(f"{n} {c} : {m}")


def sources(cle):
    txt = json.dumps(P["offre"], ensure_ascii=False) + json.dumps(P.get("formulaire", defaut={}), ensure_ascii=False)
    if cle != "defaut":
        try:
            n = P.niche(cle)
        except SystemExit:
            return txt
        for nom in ("resume.json", "offre.md", "analyse.md", "publicite.md"):
            f = n["chemin"] / nom
            if f.exists():
                txt += f.read_text(encoding="utf-8")
    return txt.replace(" ", " ").replace(" ", " ")


def present(nb, src):
    """Le nombre entier figure dans les sources (« 6 » ne se trouve pas dans « 600 000 », ni « 600 » dans « 3 600 »)."""
    nb = nb.replace("\u00a0", " ").replace("\u202f", " ")
    return re.search(rf"(?<!\d)(?<!\d ){re.escape(nb)}(?!\d)(?! \d{{3}})(?!,\d)", src) is not None


attendues = {n["cle"] for n in P.niches()} | {"defaut"}
presentes = set(S.get("niches", {}))
for cle in sorted(attendues - presentes):
    err(cle, "-", "niche absente du fichier")
for cle, niche in S.get("niches", {}).items():
    src = sources(cle)
    for code in CODES:
        e = (niche.get("emails") or {}).get(code)
        if not e or not e.get("objet") or not e.get("texte"):
            err(cle, code, "objet ou texte manquant"); continue
        tout = e["objet"] + "\n" + e["texte"]
        inconnues = set(re.findall(r"\{([a-zA-Z_]+)\}", tout)) - VARS
        if inconnues:
            err(cle, code, f"variables non autorisées {sorted(inconnues)}")
        if e["texte"].count("{lien_reservation}") != 1:
            err(cle, code, "il faut exactement un {lien_reservation}")
        if not e["texte"].rstrip().endswith("{pied_email}") or e["texte"].count("{pied_email}") != 1:
            err(cle, code, "{pied_email} doit être la dernière ligne, une seule fois")
        if SIGNATURE and f"{SIGNATURE}\n\n{{pied_email}}" not in e["texte"]:
            err(cle, code, f"fin attendue : « {SIGNATURE} », ligne vide, {{pied_email}}")
        mots = len(re.findall(r"\w+", e["texte"].replace("{pied_email}", "")))
        if mots > 130:
            err(cle, code, f"{mots} mots (130 au plus)")
        if len(e["objet"]) > 60:
            err(cle, code, f"objet de {len(e['objet'])} signes (60 au plus)")
        mots_txt = set(re.findall(r"\w+", tout.lower()))
        if any(m in mots_txt for m in INTERDITS):
            err(cle, code, f"mot interdit par le projet : {sorted(m for m in INTERDITS if m in mots_txt)}")
        if re.match(r"\s*(re|tr|fwd?)\s*:", e["objet"], re.I):
            err(cle, code, "faux « Re: » ou « TR: » dans l'objet")
        if "!" in tout or EMOJI.search(tout):
            err(cle, code, "point d'exclamation ou émoji")
        if PRIX.search(tout):
            err(cle, code, "un prix apparaît (il se donne pendant l'appel)")
        for nb in set(re.findall(r"\d+(?:[   ]\d{3})*(?:,\d+)?", re.sub(r"(?m)^\s*\d+\.\s", "", tout.replace("E-IF-", "")))):
            if nb not in PERMIS and not present(nb, src):
                err(cle, code, f"nombre « {nb} » introuvable dans les sources de la niche (inventé ?)")
print(f"{len(presentes)} niches, {sum(len((n.get('emails') or {})) for n in S.get('niches', {}).values())} e-mails")
if erreurs:
    print("\n".join(erreurs)); sys.exit(f"{len(erreurs)} problème(s)")
print("Tout passe.")
