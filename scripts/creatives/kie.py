"""Client kie.ai pour GPT Image 2.6 (texte vers image et image vers image), partagé par gen.py et variantes.py.
Chaque taskId est noté AVANT l'attente : une relance reprend la tâche au lieu de la repayer."""
import json
import mimetypes
import time
import urllib.request
import uuid

API = "https://api.kie.ai/api/v1"
TEXTE = "gpt-image-2-6/sunburst-text-to-image"
IMAGE = "gpt-image-2-6/sunburst-image-to-image"


class Kie:
    def __init__(self, projet):
        c = projet.get("creatives", defaut={}) or {}
        self.cle = projet.secret(c.get("kie_key_var", "KIE_API_KEY"))
        self.reserve = float(c.get("reserve_credits", 300))

    def req(self, url, data=None, entetes=None):
        h = {"Authorization": f"Bearer {self.cle}"}; h.update(entetes or {})
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=240) as r:
            return json.loads(r.read())

    def solde(self):
        return float(self.req(f"{API}/chat/credit")["data"])

    def envoyer(self, chemin, cache):
        """Dépose une image chez kie (pour l'image vers image) ; garde l'adresse en cache."""
        connu = json.loads(cache.read_text()) if cache.exists() else {}
        if chemin.name in connu:
            return connu[chemin.name]
        b = uuid.uuid4().hex; nom = f"variante-{chemin.name}"
        parts = [f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode() for k, v in (("uploadPath", "ads"), ("fileName", nom))]
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{nom}\"\r\nContent-Type: {mimetypes.guess_type(str(chemin))[0] or 'image/png'}\r\n\r\n".encode())
        corps = b"".join(parts) + chemin.read_bytes() + f"\r\n--{b}--\r\n".encode()
        connu[chemin.name] = self.req("https://kieai.redpandaai.co/api/file-stream-upload", corps, {"Content-Type": f"multipart/form-data; boundary={b}"})["data"]["downloadUrl"]
        cache.parent.mkdir(parents=True, exist_ok=True); cache.write_text(json.dumps(connu)); return connu[chemin.name]

    def tache(self, sortie, fichier_tache, modele, entree):
        """Crée (ou reprend) une tâche et attend l'image. Renvoie un court compte rendu."""
        if sortie.exists():
            return "déjà là"
        if fichier_tache.exists():
            tid = json.loads(fichier_tache.read_text())["taskId"]
        else:
            res = self.req(f"{API}/jobs/createTask", json.dumps({"model": modele, "input": entree}).encode(), {"Content-Type": "application/json"})
            if res.get("code") != 200:
                return f"création refusée : {str(res)[:300]}"
            tid = res["data"]["taskId"]
            fichier_tache.parent.mkdir(parents=True, exist_ok=True)
            fichier_tache.write_text(json.dumps({"taskId": tid, "model": modele, "input": entree}, indent=1, ensure_ascii=False))
        for _ in range(240):
            try:
                d = self.req(f"{API}/jobs/recordInfo?taskId={tid}")["data"]
            except Exception:
                time.sleep(6); continue
            if d["state"] == "success":
                with urllib.request.urlopen(json.loads(d["resultJson"])["resultUrls"][0], timeout=240) as r:
                    sortie.parent.mkdir(parents=True, exist_ok=True); sortie.write_bytes(r.read())
                return f"ok crédits={d.get('creditsConsumed')}"
            if d["state"] == "fail":
                fichier_tache.rename(fichier_tache.with_suffix(".failed.json"))
                return f"échec : {d.get('failMsg')}"
            time.sleep(6)
        return "toujours en attente (relancer reprend la même tâche)"
