#!/usr/bin/env python3
"""Bibliothèque publicitaire Meta (annonces actives) par mots-clés, via l'acteur Apify `apify~facebook-ads-scraper`.
Requêtes : projet.json → niches[].ads_library (courtes ! les requêtes longues renvoient 0 ; « vous êtes <métier> » trouve les annonceurs B2B).
Pays : projet.json → recherche.pays (sinon le premier pays de la campagne). Sortie : <projet>/_commun/ads-library/<clé>/<requête>.json (cache).
Usage : python3 adlib.py <projet> [niche ...] [--limite 25] [--dry-run]   (--dry-run : affiche les requêtes et les adresses, sans jeton)
Ensuite : python3 -I digest.py <projet>/_commun/ads-library > <projet>/_commun/ads-library/resume.txt
          python3 -I planche_concurrents.py <projet>/_commun/ads-library <dossier> <Page 1> [Page 2 ...]"""
import concurrent.futures as cf
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from projet import Projet  # noqa: E402

args = [a for a in sys.argv[1:] if a != "--dry-run"]; A_BLANC = "--dry-run" in sys.argv
LIMITE = 25
if "--limite" in args:
    i = args.index("--limite"); LIMITE = int(args[i + 1]); del args[i:i + 2]
if not args:
    sys.exit(__doc__)
P = Projet(args[0]); NICHES = P.niches(args[1:])
r = P.get("recherche", defaut={}) or {}
PAYS = r.get("pays") or (P.get("campagne", "pays", defaut=["FR"]) or ["FR"])[0]
ACTEUR = "https://api.apify.com/v2/acts/apify~facebook-ads-scraper/run-sync-get-dataset-items?timeout=240&memory=1024"
SORTIE = P.racine / "_commun" / "ads-library"


def nom_cache(q):
    s = unicodedata.normalize("NFKD", q).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") + ".json"


def lancer(cle, q):
    f = SORTIE / cle / (nom_cache(q))
    if f.exists():
        return cle, q, len(json.loads(f.read_text())), "cache"
    url = (f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={PAYS}&media_type=all&q="
           + urllib.parse.quote(q) + "&search_type=keyword_unordered")
    corps = json.dumps({"startUrls": [{"url": url}], "resultsLimit": LIMITE}).encode()
    err = None
    for _ in range(2):
        try:
            rep = urllib.request.urlopen(urllib.request.Request(ACTEUR, data=corps, headers={"authorization": f"Bearer {JETON}", "content-type": "application/json"}), timeout=280)
            data = [x for x in json.loads(rep.read()) if isinstance(x, dict) and x.get("adArchiveId") and x.get("snapshot")]
            f.parent.mkdir(parents=True, exist_ok=True); f.write_text(json.dumps(data, ensure_ascii=False))
            return cle, q, len(data), "ok"
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:120]}"; time.sleep(4)
    return cle, q, 0, err


travaux = [(n["cle"], q) for n in NICHES for q in n.get("ads_library", [])]
if not travaux:
    sys.exit("aucune requête : remplir niches[].ads_library dans projet.json")
if A_BLANC:
    for cle, q in travaux:
        f = SORTIE / cle / (nom_cache(q))
        print(f"[à blanc] {cle} | {q} | " + ("en cache" if f.exists() else f"à relever ({LIMITE} annonces au plus, pays {PAYS})"))
    sys.exit(0)
JETON = P.secret(r.get("apify_token_var", "APIFY_TOKEN"))
with cf.ThreadPoolExecutor(6) as ex:
    for cle, q, k, s in ex.map(lambda a: lancer(*a), travaux):
        print(cle, "|", q, "|", k, "annonces |", s, flush=True)
