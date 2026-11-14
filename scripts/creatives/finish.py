#!/usr/bin/env python3
"""Finition des créatives d'une niche : export JPEG de chaque image retenue dans creatives/final/, logo officiel de l'agence posé
dans le pied vide si la spec le demande (`"logo": "noir"` sur fond clair, `"clair"` sur fond sombre ; jamais si le pied n'est pas vide),
planche d'ensemble final/_planche.jpg. work/sel.json (facultatif) : {"<id>": "<fichier brut retenu>.png"} pour choisir une version.
Usage : python3 finish.py <projet> <niche>"""
import json
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "lib"))
from projet import Projet  # noqa: E402
from PIL import Image, ImageStat  # noqa: E402


def logos(projet):
    out = {}
    for k in ("clair", "noir"):
        chemin = projet.get("agence", f"logo_{k}")
        if chemin:
            f = (projet.racine / chemin).expanduser()
            if f.exists():
                out[k] = Image.open(f).convert("RGBA")
    return out


def poser_logo(im, logo):
    """Pose le logo au centre du pied (bas 10 %) si cette zone est vraiment vide. Renvoie (image, note)."""
    w, h = im.size
    sd = max(ImageStat.Stat(im.crop((int(.2 * w), int(.905 * h), int(.8 * w), int(.985 * h)))).stddev)
    if sd >= 7:
        return im, f"pied non vide (écart {sd:.0f}), sans logo"
    lw = int(.19 * w); lh = round(lw * logo.height / logo.width); lg = logo.resize((lw, lh), Image.LANCZOS)
    im.paste(lg, ((w - lw) // 2, int(.945 * h) - lh // 2), lg)
    return im, "logo"


def planche(images, dest, largeur=560, colonnes=5):
    if not images:
        return
    th = round(largeur * images[0].height / images[0].width); lignes = (len(images) + colonnes - 1) // colonnes
    s = Image.new("RGB", (colonnes * (largeur + 16) + 16, lignes * (th + 16) + 16), "#FFFFFF")
    for i, im in enumerate(images):
        s.paste(im.resize((largeur, th), Image.LANCZOS), (16 + (i % colonnes) * (largeur + 16), 16 + (i // colonnes) * (th + 16)))
    s.save(dest, quality=88)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    P = Projet(sys.argv[1]); N = P.niche(sys.argv[2])
    DOSSIER = N["chemin"] / "creatives"; WORK = DOSSIER / "work"; DEST = DOSSIER / "final"; DEST.mkdir(parents=True, exist_ok=True)
    sel = json.loads((WORK / "sel.json").read_text()) if (WORK / "sel.json").exists() else {}
    LOGOS = logos(P); faits = []
    for it in json.loads((DOSSIER / "spec.json").read_text(encoding="utf-8")):
        brut = WORK / "raw" / sel.get(it["id"], it["id"] + ".png")
        if not brut.exists():
            print("MANQUE", it["id"]); continue
        im = Image.open(brut).convert("RGB"); note = ""
        if it.get("logo"):
            im, note = poser_logo(im, LOGOS[it["logo"]]) if it["logo"] in LOGOS else (im, f"logo « {it['logo']} » absent du projet")
        im.save(DEST / f"{it['id']}.jpg", quality=93, subsampling=0); faits.append(im); print(it["id"], im.size, note)
    planche(faits, DEST / "_planche.jpg"); print("planche :", DEST / "_planche.jpg")
