#!/usr/bin/env python3
"""Contrôle de creatives/spec.json AVANT de payer une seule image (aucune clé, aucun réseau).
Bloquant : nombre d'entrées, id stables et uniques, formats tous différents, bloc TEXT RULES, chaque ligne de `expect` citée telle quelle
dans la consigne, logo dessiné par programme seulement, aucun prix de l'offre, ni « 0 € », « gratuit », « vous ne payez que »,
point d'exclamation ou hashtag dans le texte de l'image, montant remboursé sur trois images au plus.
À voir : cible non nommée en toutes lettres, garantie absente, plus de 25 mots hors formats « écran ».
Usage : python3 spec_check.py <projet> <niche> [chemin de spec.json]"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from projet import Projet  # noqa: E402

INTERDITS = ["0 €", "0,00 €", "gratuit", "vous ne payez que", "rien à la signature", "payé au résultat"]


def montant(nb):
    """3600 → les écritures possibles d'un prix dans une image."""
    s = str(int(nb))
    groupes = f"{int(nb):,}".split(",")
    return {s, " ".join(groupes), " ".join(groupes), " ".join(groupes), ".".join(groupes)}


def controler(P, n, spec):
    r, o = n["resume"], P["offre"]
    erreurs, avis = [], []
    attendu = int(P.get("creatives", "par_niche", defaut=10))
    if len(spec) != attendu:
        erreurs.append(f"{len(spec)} entrées (attendu : {attendu})")
    ids = [i.get("id", "") for i in spec]
    if len(set(ids)) != len(ids):
        erreurs.append("id en double")
    formats = [i.get("format", "").strip().lower() for i in spec]
    if len(set(formats)) != len(formats):
        erreurs.append("deux entrées ont le même format : dix formats différents par niche")
    remb = f"{r.get('remboursement_par_unite')} €" if r.get("remboursement_par_unite") is not None else None
    avec_remb = 0
    prix = montant(o["prix_ht"]) if o.get("prix_ht") else set()
    cible = (r.get("cible_pub") or "").lower()
    garantie = (r.get("garantie_courte") or o.get("garantie_courte") or "").rstrip(".").lower()
    for it in spec:
        i, p, ex = it.get("id", "?"), it.get("prompt", ""), it.get("expect", [])
        if not re.match(rf"^N{n['rang']}\d{{2}}-[a-z0-9-]+$", i):
            erreurs.append(f"{i} : id attendu N{n['rang']}01-nom-court à N{n['rang']}10-nom-court")
        if "TEXT RULES:" not in p or "FORMAT:" not in p:
            erreurs.append(f"{i} : bloc TEXT RULES absent de la consigne")
        if not ex:
            erreurs.append(f"{i} : expect vide, l'OCR ne pourra rien vérifier")
        for e in ex:
            if f'"{e}"' not in p:
                erreurs.append(f"{i} : « {e} » est attendu mais pas cité tel quel dans la consigne")
        if it.get("logo") not in (None, "noir", "clair"):
            erreurs.append(f"{i} : logo doit valoir null, \"noir\" ou \"clair\"")
        if it.get("logo") and "bottom 10%" not in p:
            erreurs.append(f"{i} : logo demandé sans pied vide (bloc FOOT)")
        consigne = re.sub(r"\bno [a-z ]{0,20}logo", "", p.split("TEXT RULES:")[0], flags=re.I)
        if re.search(r"\blogo\b", consigne, re.I):
            avis.append(f"{i} : la consigne parle de logo ; le modèle ne doit jamais le dessiner")
        texte = " ".join(ex)
        bas = texte.lower()
        for x in INTERDITS:
            if re.search(rf"(?<![\d,]){re.escape(x)}", bas):
                erreurs.append(f"{i} : « {x} » interdit à l'image")
        if "!" in texte or "#" in texte:
            erreurs.append(f"{i} : point d'exclamation ou hashtag à l'image")
        for m in prix:
            if re.search(rf"(?<!\d)(?<!\d[\s.]){re.escape(m)}(?!\d)", texte):
                erreurs.append(f"{i} : le prix de l'offre ({m}) apparaît à l'image")
        if remb and remb in texte:
            avec_remb += 1
        if cible and cible not in bas:
            avis.append(f"{i} : la cible « {r.get('cible_pub')} » n'est pas écrite en toutes lettres ; vérifier que l'image la dit autrement")
        if garantie and garantie not in bas and not (remb and remb in texte):
            avis.append(f"{i} : « {garantie} » absent de l'image")
        mots = len(re.findall(r"\w+", texte))
        if mots > 25 and not re.search(r"téléphone|écran|note|agenda|certificat", it.get("format", ""), re.I):
            avis.append(f"{i} : {mots} mots à l'image (25 au plus hors formats écran)")
    if avec_remb > 3:
        erreurs.append(f"le montant remboursé figure sur {avec_remb} images (trois au plus)")
    return erreurs, avis


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    if len(argv) < 2:
        print(__doc__)
        return 2
    P = Projet(argv[0])
    n = P.niche(argv[1])
    f = Path(argv[2]) if len(argv) > 2 else n["chemin"] / "creatives" / "spec.json"
    spec = json.loads(f.read_text(encoding="utf-8"))
    erreurs, avis = controler(P, n, spec)
    for a in avis:
        print("À VOIR ", a)
    for e in erreurs:
        print("ERREUR ", e)
    perf = n["resume"].get("variantes_performance") or [i["id"] for i in spec[:2]]
    print(f"{n['cle']} : {len(spec)} consignes, {len(erreurs)} erreur(s), {len(avis)} point(s) à voir ; variantes « performance » sur {', '.join(perf)}")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
