#!/usr/bin/env python3
"""Contrôle des textes des créatives par OCR (Vision de macOS) : chaque phrase de `expect` (spec.json) doit se retrouver dans l'image,
et tout texte en plus est signalé (le modèle invente parfois des mots). Écrit work/check.json.
Faux manques connus : accents sur les très gros titres et texte manuscrit ; regarder l'image avant de jeter.
Usage : python3 check.py <projet> <niche> [id ...]"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "lib"))
from projet import Projet  # noqa: E402

if len(sys.argv) < 3:
    sys.exit(__doc__)
if sys.platform != "darwin":
    sys.exit("check.py lit les images avec Vision (macOS). Ailleurs, regarder chaque image à la main ou brancher un autre OCR qui écrit {\"lines\": [...]}")
P = Projet(sys.argv[1]); N = P.niche(sys.argv[2]); SEUL = set(sys.argv[3:])
WORK = N["chemin"] / "creatives" / "work"
SPEC = json.loads((N["chemin"] / "creatives" / "spec.json").read_text(encoding="utf-8"))
OCR = ICI / "ocr"
if not OCR.exists():
    subprocess.run(["swiftc", "-O", str(ICI / "ocr.swift"), "-o", str(OCR)], check=True)


def norm(s):
    s = unicodedata.normalize("NFC", s).replace("’", "'").replace("‘", "'").replace(" ", " ").replace(" ", " ")
    return re.sub(r"[\s·•\-–—>$.,:;?✓✔☑]+", "", s.replace("œ", "oe").lower())


rapport = {}
for it in [i for i in SPEC if not SEUL or i["id"] in SEUL]:
    for f in sorted((WORK / "raw").glob(it["id"] + "*.png")):
        out = subprocess.run([str(OCR), str(f)], capture_output=True, text=True).stdout.strip()
        try:
            lignes = json.loads(out).get("lines", [])
        except Exception:
            lignes = []
        tout = norm(" ".join(lignes)); attendu = norm(" ".join(it.get("expect", [])))
        manque = [e for e in it.get("expect", []) if norm(e) not in tout]
        enplus = [l for l in lignes if len(norm(l)) > 3 and norm(l) not in attendu]
        rapport[f.stem] = {"manque": manque, "en_plus": enplus, "lignes": lignes}
        print(("OK    " if not manque else "À VOIR") + f" {f.stem}" + (f" | manque : {manque}" if manque else "") + (f" | en plus : {enplus}" if enplus else ""))
p = WORK / "check.json"
ancien = json.loads(p.read_text()) if p.exists() else {}
ancien.update(rapport); p.write_text(json.dumps(ancien, ensure_ascii=False, indent=1))
