#!/usr/bin/env python3
"""Télécharge les visuels des annonces de quelques Pages et en fait une planche.
Usage : python3 -I planche_concurrents.py <adlib-data> <dossier de sortie> <Page 1> [Page 2 ...]"""
import json, sys, io, re, urllib.request
from pathlib import Path
import site; sys.path.append(site.getusersitepackages())   # Pillow installé avec pip --user reste visible sous python3 -I
from PIL import Image, ImageDraw

ROOT, OUT = Path(sys.argv[1]), Path(sys.argv[2]); WANT = [w.lower() for w in sys.argv[3:]]
OUT.mkdir(parents=True, exist_ok=True)
seen, tiles = set(), []
for f in sorted(ROOT.glob("*/*.json")):
    for a in json.loads(f.read_text()):
        page = a.get("pageName", "")
        if not any(w in page.lower() for w in WANT):
            continue
        s = a["snapshot"]
        urls = []
        for key in ("images", "cards", "videos"):
            for x in (s.get(key) or [])[:3]:
                u = x.get("originalImageUrl") or x.get("resizedImageUrl") or x.get("videoPreviewImageUrl")
                if u:
                    urls.append(u)
        for u in urls[:2]:
            k = re.sub(r"\?.*", "", u)
            if k in seen or len([t for t in tiles if t[0] == page]) >= 4:
                continue
            seen.add(k)
            try:
                raw = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40).read()
                im = Image.open(io.BytesIO(raw)).convert("RGB")
            except Exception:
                continue
            im.thumbnail((520, 650))
            tiles.append((page, im))
W, H, cols = 540, 700, 5
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * W, max(1, rows) * H), "white"); d = ImageDraw.Draw(sheet)
for i, (page, im) in enumerate(tiles):
    x, y = (i % cols) * W + 10, (i // cols) * H + 10
    sheet.paste(im, (x, y + 24)); d.text((x, y), page[:60], fill="black")
sheet.save(OUT / "planche-concurrents.jpg", quality=85)
print(len(tiles), "visuels →", OUT / "planche-concurrents.jpg", sheet.size)
