#!/usr/bin/env python3
"""Variantes « performance » : pour les créatives choisies d'une niche, la même image où seule la phrase de garantie
(`garantie_courte`, par exemple « Garantis ou remboursés. ») est remplacée par `offre.variante_performance` (par exemple « Payé à la performance. »).
Image vers image par GPT Image 2.6 (environ 20 crédits), puis logo reposé, export creatives/final/<id>-performance.jpg.
Choix des images : resume.json → "variantes_performance": ["<id>", "<id>"] ; à défaut, les deux premières entrées de spec.json.
Usage : python3 variantes.py <projet> gen|check|finish [niche ...] [--dry-run]   (--dry-run avec gen : liste et coût, sans clé)"""
import concurrent.futures as cf
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI)); sys.path.insert(0, str(ICI.parent / "lib"))
from projet import Projet  # noqa: E402
from kie import Kie, IMAGE  # noqa: E402

ARGS = [a for a in sys.argv[1:] if a != "--dry-run"]; A_BLANC = "--dry-run" in sys.argv
if len(ARGS) < 2:
    sys.exit(__doc__)
P = Projet(ARGS[0]); ETAPE = ARGS[1]; NICHES = P.niches(ARGS[2:])
NOUVEAU = P["offre"].get("variante_performance")
if not NOUVEAU:
    sys.exit("offre.variante_performance absent de projet.json")


def elements():
    for n in NICHES:
        work = n["chemin"] / "creatives" / "work"
        sel = json.loads((work / "sel.json").read_text()) if (work / "sel.json").exists() else {}
        spec = json.loads((n["chemin"] / "creatives" / "spec.json").read_text(encoding="utf-8"))
        ids = n["resume"].get("variantes_performance") or [i["id"] for i in spec[:int(P.get("creatives", "variantes_performance", defaut=2))]]
        par_id = {i["id"]: i for i in spec}
        ancien = n["resume"].get("garantie_courte", P["offre"]["garantie_courte"])
        for id_ in ids:
            yield n, id_, work / "raw" / sel.get(id_, id_ + ".png"), work, par_id.get(id_, {}).get("logo"), ancien


def faire(e):
    n, id_, brut, work, _, ancien = e
    if not brut.exists():
        return id_, f"image source absente : {brut.name}"
    prompt = (f"Edit the provided advertisement image. Make exactly one change: replace the text \"{ancien}\" with the text \"{NOUVEAU}\". "
              "Use the same typeface, weight, size, colour and position as the replaced text; if the text sits on a highlighter bar, a band or a pill, keep the same style "
              "and adjust its width to fit the new text. Everything else in the image stays strictly identical: every other word, number, colour, shape, photograph, layout, "
              "margin and proportion. Do not add, remove, move or restyle anything else. Render the text exactly as written, with every accent. "
              "Do not render the quotation marks. Portrait 4:5, same framing.")
    entree = {"prompt": prompt, "input_urls": [K.envoyer(brut, work / "jobs" / "variantes-depots.json")], "aspect_ratio": "4:5", "resolution": "2K", "quality": "high"}
    return id_, K.tache(work / "raw" / f"{id_}-perf.png", work / "jobs" / f"{id_}-perf-task.json", IMAGE, entree)


def norm(s):
    return re.sub(r"[\s·•\-–—.,:;?]+", "", unicodedata.normalize("NFC", s).replace("’", "'").lower())


if ETAPE == "gen" and A_BLANC:
    todo = list(elements())
    for n, id_, brut, work, _, ancien in todo:
        print(f"[à blanc] {n['cle']} {id_} : « {ancien} » → « {NOUVEAU} »" + ("" if brut.exists() else " (image source pas encore générée)"))
    print(f"[à blanc] {len(todo)} variantes, environ {20.2 * len(todo):.0f} crédits ; rien n'est lancé")
elif ETAPE == "gen":
    K = Kie(P); todo = list(elements()); solde = K.solde()
    print(f"solde {solde:.0f} | {len(todo)} variantes, environ {20.2 * len(todo):.0f} crédits", flush=True)
    if solde - 20.2 * len(todo) < K.reserve:
        sys.exit("solde insuffisant au regard de la réserve, rien n'est lancé")
    with cf.ThreadPoolExecutor(3) as ex:
        for id_, r in ex.map(faire, todo):
            print(id_, r, flush=True)
elif ETAPE == "check":
    if sys.platform != "darwin":
        sys.exit("l'OCR utilise Vision (macOS) : regarder les variantes à la main")
    OCR = ICI / "ocr"
    if not OCR.exists():
        subprocess.run(["swiftc", "-O", str(ICI / "ocr.swift"), "-o", str(OCR)], check=True)
    for n, id_, brut, work, _, ancien in elements():
        f = work / "raw" / f"{id_}-perf.png"
        if not f.exists():
            print("MANQUE", id_); continue
        try:
            lignes = json.loads(subprocess.run([str(OCR), str(f)], capture_output=True, text=True).stdout.strip()).get("lines", [])
        except Exception:
            lignes = []
        tout = norm(" ".join(lignes))
        print(("OK    " if norm(NOUVEAU) in tout and norm(ancien) not in tout else "À VOIR"), id_, "|", " / ".join(lignes)[:230])
elif ETAPE == "finish":
    from PIL import Image
    from finish import logos, poser_logo
    LOGOS = logos(P)
    for n, id_, brut, work, logo, _ in elements():
        f = work / "raw" / f"{id_}-perf.png"
        if not f.exists():
            print("MANQUE", id_); continue
        im = Image.open(f).convert("RGB"); note = ""
        if logo and logo in LOGOS:
            im, note = poser_logo(im, LOGOS[logo])
        dest = n["chemin"] / "creatives" / "final" / f"{id_}-performance.jpg"
        im.save(dest, quality=93, subsampling=0); print(dest.name, im.size, note)
else:
    sys.exit(__doc__)
