#!/usr/bin/env python3
"""Résumé des annonces Ads Library : par niche, une ligne par Page (annonce la plus ancienne encore active).
Usage : python3 -I digest.py <dossier adlib-data> [longueur du texte]"""
import json, sys, time, re
from pathlib import Path

ROOT = Path(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 420
now = time.time()


def days(a):
    s = a.get("startDate") or a.get("start_date")
    try:
        s = float(s)
        return int((now - s) / 86400)
    except Exception:
        return -1


for niche in sorted(p for p in ROOT.iterdir() if p.is_dir()):
    ads = {}
    for f in sorted(niche.glob("*.json")):
        for a in json.loads(f.read_text()):
            ads.setdefault(a["adArchiveId"], (a, f.stem))
    pages = {}
    for a, q in ads.values():
        pages.setdefault(a.get("pageName", "?"), []).append((days(a), a, q))
    print(f"\n######## {niche.name} : {len(ads)} annonces, {len(pages)} pages")
    rows = sorted(pages.items(), key=lambda kv: -max(d for d, _, _ in kv[1]))
    for page, lst in rows:
        lst.sort(key=lambda t: -t[0])
        d, a, q = lst[0]
        s = a["snapshot"]
        body = re.sub(r"\s+", " ", ((s.get("body") or {}).get("text") or ""))[:N]
        fmt = s.get("displayFormat") or ""
        img = ""
        for key in ("images", "cards", "videos"):
            v = s.get(key) or []
            if v:
                x = v[0]
                img = x.get("originalImageUrl") or x.get("resizedImageUrl") or x.get("videoPreviewImageUrl") or ""
                if img:
                    break
        cats = ",".join(s.get("pageCategories") or [])[:40]
        print(f"\n== {page} [{cats}] · {len(lst)} pub(s) · {d} j · {fmt} · id {a['adArchiveId']} · q={q}")
        print(f"   TITRE: {(s.get('title') or '')[:140]} | CTA: {s.get('ctaText') or ''} | {(s.get('linkUrl') or '')[:80]}")
        print(f"   TEXTE: {body}")
        if img:
            print(f"   IMG: {img[:300]}")
