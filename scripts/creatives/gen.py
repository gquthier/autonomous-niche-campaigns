#!/usr/bin/env python3
"""Génère les créatives d'une niche avec GPT Image 2.6 (kie.ai, texte vers image), 4:5, 2K, qualité haute (environ 18 crédits l'image).
Lit <niche>/creatives/spec.json (voir references/creatives.md), écrit work/raw/<id>.png. Une relance ne repaie pas une image déjà faite.
Usage : python3 gen.py <projet> <niche> [id ...] [--dry-run]      VERSION=b pour une seconde version (fichiers <id>-b.png) ; POOL=3 tâches en parallèle
--dry-run : liste les images et le coût estimé, sans clé ni appel."""
import concurrent.futures as cf
import json
import os
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI)); sys.path.insert(0, str(ICI.parent / "lib"))
from projet import Projet  # noqa: E402
from kie import Kie, TEXTE  # noqa: E402

ARGS = [a for a in sys.argv[1:] if a != "--dry-run"]; A_BLANC = "--dry-run" in sys.argv
if len(ARGS) < 2:
    sys.exit(__doc__)
P = Projet(ARGS[0]); N = P.niche(ARGS[1]); SEUL = set(ARGS[2:])
VER = os.environ.get("VERSION", "")
DOSSIER = N["chemin"] / "creatives"; WORK = DOSSIER / "work"
SPEC = json.loads((DOSSIER / "spec.json").read_text(encoding="utf-8"))


def faire(it):
    nom = it["id"] + (f"-{VER}" if VER else "")
    entree = {"prompt": it["prompt"], "aspect_ratio": it.get("aspect", "4:5"), "resolution": "2K", "quality": "high"}
    return nom, K.tache(WORK / "raw" / f"{nom}.png", WORK / "jobs" / f"{nom}-task.json", TEXTE, entree)


items = [i for i in SPEC if not SEUL or i["id"] in SEUL]
if A_BLANC:
    for it in items:
        nom = it["id"] + (f"-{VER}" if VER else "")
        print(f"[à blanc] {nom} | {it.get('format', '')} | {it.get('aspect', '4:5')} | {len(it['prompt'])} signes de consigne | "
              + ("déjà là" if (WORK / "raw" / f"{nom}.png").exists() else "à générer"))
    print(f"[à blanc] {len(items)} images, environ {18.3 * len(items):.0f} crédits ; rien n'est lancé")
    sys.exit(0)
K = Kie(P)
solde = K.solde(); cout = 18.3 * len(items)
print(f"solde {solde:.0f} crédits | {len(items)} images, environ {cout:.0f} crédits", flush=True)
if solde - cout < K.reserve:
    sys.exit(f"solde insuffisant : il resterait moins que la réserve de {K.reserve:.0f} crédits, rien n'est lancé")
with cf.ThreadPoolExecutor(int(os.environ.get("POOL", 3))) as ex:   # au-delà de 4 tâches, kie ralentit
    for nom, r in ex.map(faire, items):
        print(nom, r, flush=True)
print(f"solde {K.solde():.0f}")
