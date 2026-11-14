#!/usr/bin/env python3
"""Aperçus réduits (900 px de large) des images brutes d'une niche, pour les regarder une par une avant de choisir.
Usage : python3 apercu.py <projet> <niche> [préfixe d'id ...]   → <niche>/creatives/work/view/*.jpg"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from projet import Projet  # noqa: E402
from PIL import Image  # noqa: E402

if len(sys.argv) < 3:
    sys.exit(__doc__)
P = Projet(sys.argv[1]); N = P.niche(sys.argv[2]); SEUL = sys.argv[3:]
WORK = N["chemin"] / "creatives" / "work"; (WORK / "view").mkdir(parents=True, exist_ok=True)
for f in sorted((WORK / "raw").glob("*.png")):
    if SEUL and not any(f.stem.startswith(o) for o in SEUL):
        continue
    im = Image.open(f).convert("RGB"); im.thumbnail((900, 1125)); im.save(WORK / "view" / f"{f.stem}.jpg", quality=82); print(WORK / "view" / f"{f.stem}.jpg")
