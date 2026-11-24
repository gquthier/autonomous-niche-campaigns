"""Client Graph API minimal (bibliothèque standard seulement) et son double de simulation.

Meta : le jeton vient de la variable d'environnement (META_ACCESS_TOKEN par défaut) et ne s'affiche jamais, même dans un message d'erreur.
Les limites de débit (codes 4, 17, 32, 613, 80004) sont attendues puis rejouées : après beaucoup d'écritures, Meta refuse un moment
les LECTURES aussi ; ne jamais conclure d'une liste vide lue pendant ce temps.

FauxMeta : même interface, aucun appel réseau, aucune clé. Les objets créés vivent dans <projet>/_meta/monde.dry-run.json,
pour que les étapes suivantes (controle, usage, activer) relisent ce que les précédentes ont « créé »."""
import hashlib
import json
import mimetypes
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

LIMITES = (4, 17, 32, 613, 80004)


class Meta:
    def __init__(self, projet):
        m = projet.get("meta", defaut={}) or {}
        self.token = projet.secret(m.get("token_var", "META_ACCESS_TOKEN"))
        self.v = m.get("graph_version") or os.environ.get("META_GRAPH_VERSION") or "v23.0"
        act = projet.meta_id("ad_account")
        self.act = act if act.startswith("act_") else f"act_{act}"
        self.page = projet.meta_id("page_id")
        self.ig = projet.meta_id("instagram_user_id", requis=False)
        self._page_token = None

    def _propre(self, s):
        return s.replace(self.token, "***") if self.token else s

    def _url(self, path):
        return f"https://graph.facebook.com/{self.v}/{path.lstrip('/')}"

    def get(self, path, token=None, essais=12, **p):
        p["access_token"] = token or self.token
        url = self._url(path) + "?" + urllib.parse.urlencode({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in p.items()})
        r = {"error": {"message": "aucun essai"}}
        for _ in range(essais):
            try:
                return json.load(urllib.request.urlopen(url, timeout=60))
            except urllib.error.HTTPError as e:
                r = {"error": json.loads(self._propre(e.read().decode() or "{}")).get("error", {})}
                if r["error"].get("code") in LIMITES:
                    time.sleep(40)
                    continue
                return r
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                time.sleep(10)
        return r

    def post(self, path, token=None, **p):
        p["access_token"] = token or self.token
        data = urllib.parse.urlencode({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list, bool)) else v) for k, v in p.items()}).encode()
        for _ in range(10):
            try:
                return json.load(urllib.request.urlopen(urllib.request.Request(self._url(path), data=data), timeout=120))
            except urllib.error.HTTPError as e:
                err = json.loads(self._propre(e.read().decode() or "{}")).get("error", {})
                if err.get("code") in LIMITES or err.get("error_subcode") == 4841018:
                    time.sleep(35)
                    continue
                return {"error": err}
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                time.sleep(10)
        return {"error": {"message": "limite de débit Meta ou réseau indisponible"}}

    def toutes(self, path, **p):
        """Toutes les pages d'une liste (suit `paging.next`)."""
        out, apres = [], None
        for _ in range(50):
            r = self.get(path, **p, **({"after": apres} if apres else {}))
            if "error" in r:
                raise RuntimeError(f"lecture refusée ({path}) : {r['error'].get('message')}")
            out += r.get("data", [])
            apres = r.get("paging", {}).get("cursors", {}).get("after") if r.get("paging", {}).get("next") else None
            if not apres:
                return out
        return out

    def page_token(self):
        if not self._page_token:
            r = self.get(self.page, fields="access_token")
            if "access_token" not in r:
                raise SystemExit(f"le jeton n'a pas accès à la page configurée : {r.get('error', {}).get('message')}")
            self._page_token = r["access_token"]
        return self._page_token

    def formulaires(self, statut="ACTIVE"):
        return self.toutes(f"{self.page}/leadgen_forms", token=self.page_token(), fields="id,name,status,created_time,questions{key,label,type,options}", limit=100,
                           filtering=[{"field": "status", "operator": "EQUAL", "value": statut}])

    def envoyer_image(self, chemin):
        """Envoie une image dans la bibliothèque du compte publicitaire, renvoie son hash."""
        b = uuid.uuid4().hex
        nom = os.path.basename(chemin)
        with open(chemin, "rb") as fh:
            contenu = fh.read()
        corps = (f"--{b}\r\nContent-Disposition: form-data; name=\"access_token\"\r\n\r\n{self.token}\r\n"
                 f"--{b}\r\nContent-Disposition: form-data; name=\"filename\"; filename=\"{nom}\"\r\nContent-Type: {mimetypes.guess_type(chemin)[0] or 'image/jpeg'}\r\n\r\n").encode() \
            + contenu + f"\r\n--{b}--\r\n".encode()
        for _ in range(6):
            try:
                r = json.load(urllib.request.urlopen(urllib.request.Request(self._url(f"{self.act}/adimages"), data=corps,
                                                                            headers={"Content-Type": f"multipart/form-data; boundary={b}"}), timeout=180))
                return list(r["images"].values())[0]["hash"]
            except urllib.error.HTTPError as e:
                err = json.loads(self._propre(e.read().decode() or "{}")).get("error", {})
                if err.get("code") in LIMITES:
                    time.sleep(35)
                    continue
                raise RuntimeError(str(err)[:300])
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                time.sleep(10)
        raise RuntimeError("envoi d'image impossible")


class FauxMeta:
    """Double de simulation : mêmes méthodes que Meta, identifiants fictifs, aucun réseau."""

    def __init__(self, projet):
        self.v = "simulation"
        act = projet.meta_id("ad_account", requis=False) or "act_SIMULATION"
        self.act = act if act.startswith("act_") else f"act_{act}"
        self.page = projet.meta_id("page_id", requis=False) or "PAGE_SIMULATION"
        self.ig = projet.meta_id("instagram_user_id", requis=False)
        self.fichier = projet.racine / "_meta" / "monde.dry-run.json"
        self.monde = json.loads(self.fichier.read_text(encoding="utf-8")) if self.fichier.exists() else {"seq": 0, "objets": {}}

    # ---------- monde simulé ----------
    def _sauver(self):
        self.fichier.parent.mkdir(parents=True, exist_ok=True)
        self.fichier.write_text(json.dumps(self.monde, indent=1, ensure_ascii=False), encoding="utf-8")

    def _creer(self, type_, **champs):
        self.monde["seq"] += 1
        oid = f"SIM{self.monde['seq']:05d}"
        self.monde["objets"][oid] = {"id": oid, "type": type_, **champs}
        self._sauver()
        return {"id": oid}

    def _de_type(self, type_, **filtre):
        return [o for o in self.monde["objets"].values() if o["type"] == type_ and all(o.get(k) == v for k, v in filtre.items())]

    def _vue(self, o):
        o = dict(o)
        if o["type"] == "ad":
            cr = self.monde["objets"].get(o.get("creative", {}).get("creative_id"), {})
            o["creative"] = {"id": cr.get("id"), "object_story_spec": cr.get("object_story_spec", {})}
            adset = self.monde["objets"].get(o.get("adset_id"), {})
            camp = self.monde["objets"].get(adset.get("campaign_id"), {})
            if o["status"] != "ACTIVE":
                o["effective_status"] = o["status"]
            elif adset.get("status") != "ACTIVE":
                o["effective_status"] = "ADSET_PAUSED"
            elif camp.get("status") != "ACTIVE":
                o["effective_status"] = "CAMPAIGN_PAUSED"
            else:
                o["effective_status"] = "PENDING_REVIEW"
        elif o["type"] in ("campaign", "adset"):
            o["effective_status"] = o.get("status")
        return o

    # ---------- interface de Meta ----------
    def get(self, path, token=None, essais=1, **p):
        path = path.strip("/")
        if path == "me":
            return {"id": "0", "name": "utilisateur système (simulation)"}
        if path == "me/permissions":
            return {"data": [{"permission": x, "status": "granted"} for x in ("ads_management", "ads_read", "leads_retrieval", "pages_manage_ads",
                                                                             "pages_read_engagement", "pages_show_list", "business_management")]}
        if path == self.act:
            return {"name": "compte publicitaire (simulation)", "account_status": 1, "currency": "EUR", "timezone_name": "Europe/Paris"}
        if path == self.page:
            return {"access_token": "simulation"}
        if self.ig and path == self.ig:
            return {"username": "compte_instagram_simulation"}
        if path == f"{self.act}/campaigns":
            return {"data": [self._vue(o) for o in self._de_type("campaign")]}
        if path == f"{self.page}/leadgen_forms":
            statut = next((f["value"] for f in p.get("filtering", []) if f.get("field") == "status"), None)
            return {"data": [o for o in self._de_type("form") if not statut or o["status"] == statut]}
        if path.endswith("/ads"):
            parent = path[:-4]
            ads = [o for o in self._de_type("ad") if o.get("adset_id") == parent
                   or self.monde["objets"].get(o.get("adset_id"), {}).get("campaign_id") == parent]
            return {"data": [self._vue(o) for o in ads]}
        if path in self.monde["objets"]:
            return self._vue(self.monde["objets"][path])
        return {"error": {"message": f"objet inconnu en simulation : {path}", "code": 100}}

    def post(self, path, token=None, **p):
        path = path.strip("/")
        if path == f"{self.act}/campaigns":
            return self._creer("campaign", name=p["name"], status=p.get("status", "PAUSED"), objective=p.get("objective"))
        if path == f"{self.act}/adsets":
            champs = {k: p[k] for k in ("name", "campaign_id", "daily_budget", "optimization_goal", "destination_type", "targeting") if k in p}
            return self._creer("adset", status=p.get("status", "PAUSED"), **champs)
        if path == f"{self.page}/leadgen_forms":
            qs = [{"key": q.get("key", q["type"].lower()), "label": q.get("label", q["type"]), "type": q["type"], "options": q.get("options", [])}
                  for q in p.get("questions", [])]
            return self._creer("form", name=p["name"], status="ACTIVE", questions=qs, context_card=p.get("context_card"))
        if path == f"{self.act}/adcreatives":
            options = {"asset_feed_spec": p["asset_feed_spec"]} if "asset_feed_spec" in p else {}
            return self._creer("creative", name=p.get("name"), object_story_spec=p.get("object_story_spec", {}), **options)
        if path == f"{self.act}/ads":
            return self._creer("ad", name=p["name"], adset_id=p["adset_id"], creative=p["creative"], status=p.get("status", "PAUSED"))
        if path in self.monde["objets"]:
            o = self.monde["objets"][path]
            for k in ("status", "creative", "name"):
                if k in p:
                    o[k] = p[k]
            self._sauver()
            return {"success": True}
        return {"error": {"message": f"écriture inconnue en simulation : {path}", "code": 100}}

    def toutes(self, path, **p):
        r = self.get(path, **p)
        if "error" in r:
            raise RuntimeError(f"lecture refusée ({path}) : {r['error'].get('message')}")
        return r.get("data", [])

    def page_token(self):
        return "simulation"

    def formulaires(self, statut="ACTIVE"):
        return [o for o in self._de_type("form") if o["status"] == statut]

    def copier_formulaire(self, base_id, nom):
        """Simulation de l'éditeur : copie du formulaire de base, sous son nom final (la logique n'existe pas dans l'API)."""
        base = self.monde["objets"][base_id]
        return self._creer("form", name=nom, status="ACTIVE", questions=base["questions"], logique=True)

    def envoyer_image(self, chemin):
        return "hash_" + hashlib.md5(str(chemin).encode()).hexdigest()[:16]


def ok(r, quoi, projet=None):
    """Arrête proprement sur une erreur Meta, après avoir sauvé l'état."""
    if "error" in r:
        if projet is not None:
            projet.sauver()
        e = r["error"]
        raise SystemExit(f"ÉCHEC {quoi} : {e.get('error_user_msg') or e.get('message')} (code {e.get('code')}, sous-code {e.get('error_subcode')})")
    return r
