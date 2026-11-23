"""Passage en CBO, sans clé ni réseau : python3 -m unittest discover -s tests"""
import contextlib
import datetime as dt
import io
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXEMPLE = ROOT / "examples" / "agence-exemple"
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts"))
import projet as projet_mod  # noqa: E402
import cbo  # noqa: E402
import meta_campagne  # noqa: E402

CLES_ENV = ("META_ACCESS_TOKEN", "META_AD_ACCOUNT", "META_PAGE_ID", "META_INSTAGRAM_ID", "META_BUSINESS_ID", "KIE_API_KEY", "APIFY_TOKEN")


class Base(unittest.TestCase):
    """Une copie de l'exemple fictif, aucune clé dans l'environnement, aucun appel réseau possible."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name) / "projet"
        shutil.copytree(EXEMPLE, self.dir, ignore=shutil.ignore_patterns("_meta"))
        env = {k: v for k, v in os.environ.items() if k not in CLES_ENV}
        for p in (mock.patch.dict(os.environ, env, clear=True),
                  mock.patch.object(socket.socket, "connect", side_effect=AssertionError("appel réseau en test")),
                  mock.patch.object(subprocess, "run", side_effect=AssertionError("navigateur en test"))):
            p.start()
            self.addCleanup(p.stop)

    def lancer(self, module, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = module.main([str(self.dir), *args])
        return code, out.getvalue()

    def angles(self, dossier):
        f = self.dir / dossier / "cbo" / "angles.json"
        return f, json.loads(f.read_text(encoding="utf-8"))

    def projet_json(self, modif):
        f = self.dir / "projet.json"
        d = json.loads(f.read_text(encoding="utf-8"))
        modif(d)
        f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


class Grille(Base):
    def test_exemple(self):
        code, out = self.lancer(cbo, "grille")
        self.assertEqual(code, 0, out)
        lignes = (self.dir / "cbo" / "annonces.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lignes), 25)
        self.assertIn("Instant Form - CBO | Salles de sport : 3 ad sets, 12 annonces, 24 visuels", out)
        self.assertEqual((self.dir / "cbo" / "annonces.csv").read_bytes(), (EXEMPLE / "cbo" / "annonces.csv").read_bytes(),
                         "examples/agence-exemple/cbo/annonces.csv n'est plus à jour : relancer `cbo.py examples/agence-exemple grille`")

    def test_trop_peu_d_angles_ou_de_statiques(self):
        f, a = self.angles("1-salles-de-sport")
        a["angles"] = a["angles"][:2]
        a["angles"][0]["statiques"] = a["angles"][0]["statiques"][:3]
        f.write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")
        code, out = self.lancer(cbo, "grille")
        self.assertEqual(code, 1)
        self.assertIn("2 angle(s), au moins 3 attendus", out)
        self.assertIn("F1 : 3 statique(s), entre 4 et 8 attendues", out)

    def test_ancienne_promesse_et_accents_dans_la_copy(self):
        f, a = self.angles("2-paysagistes")
        a["angles"][0]["statiques"][0]["accroche"] = "24 visites qualifiées, reservez votre etude."
        f.write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")
        code, out = self.lancer(cbo, "grille")
        self.assertEqual(code, 1)
        self.assertIn("« visites qualifiées » (ancienne promesse)", out)
        self.assertIn("« reservez » sans accent", out)

    def test_formulaire_qui_garderait_la_promesse_de_l_abo(self):
        f = self.dir / "1-salles-de-sport" / "resume.json"
        r = json.loads(f.read_text(encoding="utf-8"))
        del r["formulaire_intro"]
        f.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        code, out = self.lancer(cbo, "grille")
        self.assertEqual(code, 1)
        self.assertIn("reprendrait la promesse de l'ABO", out)


class Verification(Base):
    def test_push_conforme(self):
        self.lancer(cbo, "lire", "--dry-run")
        code, out = self.lancer(cbo, "verifier", "--dry-run")
        self.assertEqual(code, 0, out)
        preuve = json.loads((self.dir / "_meta" / "push-verified.dry-run.json").read_text(encoding="utf-8"))
        self.assertEqual(preuve["annonces"], 24)
        self.assertEqual(len(preuve["campagnes"]), 2)
        self.assertFalse((self.dir / "_meta" / "push-verified.json").exists(), "la simulation n'écrit jamais la preuve réelle")

    def test_les_pieges_du_vrai_compte_sont_bloques(self):
        self.lancer(cbo, "lire", "--dry-run")
        self.assertEqual(self.lancer(cbo, "verifier", "--dry-run")[0], 0)
        self.lancer(cbo, "lire", "--dry-run", "--pieges")
        code, out = self.lancer(cbo, "verifier", "--dry-run")
        self.assertEqual(code, 1)
        for attendu in ("campagne absente du compte : « Instant Form - CBO | Paysagistes »",
                        "ad set « Agence Exemple | F2 | Les heures creuses remplies » absent",
                        "l'intro ne dit pas la promesse des annonces",
                        "« essais tenus » (ancienne promesse)",
                        "reservez → réservez",
                        "logique conditionnelle absente ou fausse",
                        "ouvre l'accueil du site",
                        "3 publicité(s) active(s) hors de la nouvelle structure",
                        "NON VÉRIFIÉ"):
            self.assertIn(attendu, out)
        self.assertFalse((self.dir / "_meta" / "push-verified.dry-run.json").exists(), "une preuve ancienne ne survit pas à un échec")

    def test_non_qualifies_a_decider_avant(self):
        self.projet_json(lambda d: d["cbo"].pop("non_qualifies"))
        self.lancer(cbo, "lire", "--dry-run")
        code, out = self.lancer(cbo, "verifier", "--dry-run")
        self.assertEqual(code, 1)
        self.assertIn("cbo.non_qualifies non décidé", out)

    def test_etat_trop_ancien(self):
        self.lancer(cbo, "lire", "--dry-run")
        f = self.dir / "_meta" / "cbo-etat-lu.dry-run.json"
        e = json.loads(f.read_text(encoding="utf-8"))
        e["lu_le"] = (dt.datetime.now() - dt.timedelta(hours=3)).isoformat(timespec="seconds")
        f.write_text(json.dumps(e), encoding="utf-8")
        code, out = self.lancer(cbo, "verifier", "--dry-run")
        self.assertEqual(code, 1)
        self.assertIn("trop ancien, relance `lire`", out)

    def test_le_reel_refuse_un_etat_simule(self):
        self.lancer(cbo, "lire", "--dry-run")
        m = self.dir / "_meta"
        shutil.copy(m / "cbo-etat-lu.dry-run.json", m / "cbo-etat-lu.json")
        with self.assertRaises(SystemExit) as ctx:
            self.lancer(cbo, "verifier")
        self.assertIn("ne vient pas de l'API", str(ctx.exception))

    def test_lire_en_reel_sans_jeton_s_arrete(self):
        with self.assertRaises(SystemExit) as ctx:
            self.lancer(cbo, "lire")
        self.assertIn("META_ACCESS_TOKEN", str(ctx.exception))


class Lecture(unittest.TestCase):
    def test_publicite_a_deux_formats(self):
        brute = {"id": "1", "name": "F1-S01 | Accroche", "adset_id": "A", "campaign_id": "C", "status": "PAUSED", "effective_status": "PENDING_REVIEW",
                 "creative": {"asset_feed_spec": {
                     "images": [{"hash": "h45", "adlabels": [{"name": "i4x5"}]}, {"hash": "h916", "adlabels": [{"name": "i9x16"}]}],
                     "bodies": [{"text": "Texte"}], "titles": [{"text": "Titre"}],
                     "call_to_actions": [{"type": "LEARN_MORE", "value": {"lead_gen_form_id": "F9"}}],
                     "asset_customization_rules": [
                         {"customization_spec": {"facebook_positions": ["feed"], "instagram_positions": ["stream"]}, "image_label": {"name": "i4x5"}},
                         {"customization_spec": {"facebook_positions": ["story"], "instagram_positions": ["story", "reels"]}, "image_label": {"name": "i9x16"}}]}}}
        p = cbo.normaliser_pub(brute, {"h45": (1080, 1350), "h916": (1080, 1920)})
        self.assertEqual(p["formats"], ["4x5", "9x16"])
        self.assertTrue(p["vertical_en_story"])
        self.assertEqual((p["formulaire"], p["texte"], p["titre"]), ("F9", "Texte", "Titre"))
        p = cbo.normaliser_pub(brute, {"h45": (1080, 1350), "h916": (1080, 1350)})
        self.assertEqual(p["formats"], ["4x5"])
        self.assertFalse(p["vertical_en_story"])

    def test_accents_et_lien(self):
        self.assertEqual(cbo.fautes_accents("Derniere etape : vos demandes prequalifiees"),
                         [("Derniere", "dernière"), ("etape", "étape"), ("prequalifiees", "prequalifiées")])
        self.assertEqual(cbo.fautes_accents("Dernière étape : vos demandes préqualifiées, l'idée de l'année"), [])
        self.assertTrue(cbo.lien_vers_accueil("https://www.example.com/", "https://www.example.com"))
        self.assertFalse(cbo.lien_vers_accueil("https://www.example.com/confidentialite", "https://www.example.com"))


class Gagnants(unittest.TestCase):
    def test_exemple(self):
        P = projet_mod.Projet(EXEMPLE)
        res = cbo.gagnants(P, cbo.lire_resultats(EXEMPLE / "cbo" / "resultats-abo.csv"))
        sport = res["Agence Exemple | Salles de sport"]
        self.assertEqual((sport["prospects"], round(sport["depense"], 2)), (14, 120.0))
        self.assertEqual([x["pub"] for x in sport["pubs"] if x["gagnant"]], ["N103-photo-metier", "N108-agenda-semaine"])
        self.assertEqual([x["pub"] for x in res["Agence Exemple | Paysagistes"]["pubs"] if x["gagnant"]], ["N204-objet-porteur", "N201-carte-typographique"])


class NouvelleVersionFormulaire(Base):
    def test_recree_sans_doublon(self):
        self.assertEqual(self.lancer(meta_campagne, "parcours", "--dry-run")[0], 0)
        etat_f = self.dir / "_meta" / "etat.dry-run.json"
        e = json.loads(etat_f.read_text(encoding="utf-8"))
        avant = e["formulaires_base"]["salles-de-sport"]
        code, out = self.lancer(meta_campagne, "formulaires", "salles-de-sport", "--nouvelle-version", "--dry-run")
        self.assertIn("déjà créé", out, "même nom : c'est déjà la version courante")
        del e["noms_formulaires"]   # état d'avant cette option : le nom de la base n'était pas noté
        etat_f.write_text(json.dumps(e), encoding="utf-8")
        with self.assertRaises(SystemExit):   # même nom qu'un formulaire actif : refusé
            self.lancer(meta_campagne, "formulaires", "salles-de-sport", "--nouvelle-version", "--dry-run")
        self.projet_json(lambda d: d["formulaire"].update(nom="IF - {label} - CBO"))
        code, out = self.lancer(meta_campagne, "formulaires", "salles-de-sport", "--nouvelle-version", "--dry-run")
        self.assertEqual(code, 0, out)
        e = json.loads(etat_f.read_text(encoding="utf-8"))
        self.assertNotEqual(e["formulaires_base"]["salles-de-sport"], avant)
        self.assertEqual(e["formulaires_precedents"]["salles-de-sport"][0]["base"], avant)
        self.assertNotIn("salles-de-sport", e["formulaires"], "la logique est à refaire sur la nouvelle version")
        monde = json.loads((self.dir / "_meta" / "monde.dry-run.json").read_text(encoding="utf-8"))
        self.assertIn("40 demandes d'essai préqualifiées", json.dumps(monde, ensure_ascii=False))
        seq = monde["seq"]
        self.lancer(meta_campagne, "formulaires", "salles-de-sport", "--nouvelle-version", "--dry-run")
        self.assertEqual(json.loads((self.dir / "_meta" / "monde.dry-run.json").read_text(encoding="utf-8"))["seq"], seq, "une relance ne recrée rien")


if __name__ == "__main__":
    unittest.main()
