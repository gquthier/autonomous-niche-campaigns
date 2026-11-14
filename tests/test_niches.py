"""Tests sans clé ni réseau : python3 -m unittest discover -s tests"""
import contextlib
import copy
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
sys.path.insert(0, str(ROOT / "scripts" / "creatives"))
sys.path.insert(0, str(ROOT / "scripts"))
import projet as projet_mod  # noqa: E402
import meta_campagne  # noqa: E402
import build_spec  # noqa: E402
import spec_check  # noqa: E402

CLES_ENV = ("META_ACCESS_TOKEN", "META_AD_ACCOUNT", "META_PAGE_ID", "META_INSTAGRAM_ID", "META_BUSINESS_ID", "KIE_API_KEY", "APIFY_TOKEN")


class CopieDuProjet(unittest.TestCase):
    """Chaque test travaille sur une copie de l'exemple fictif, sans clé dans l'environnement."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name) / "projet"
        shutil.copytree(EXEMPLE, self.dir, ignore=shutil.ignore_patterns("_meta"))
        env = {k: v for k, v in os.environ.items() if k not in CLES_ENV}
        p = mock.patch.dict(os.environ, env, clear=True)
        p.start()
        self.addCleanup(p.stop)

    def projet(self, simulation=False):
        return projet_mod.Projet(self.dir, simulation=simulation)


class Textes(CopieDuProjet):
    def test_texte_de_publicite(self):
        P = self.projet()
        n = P.niche("salles-de-sport")
        t = projet_mod.textes_pub(P, n)
        self.assertEqual(t["title"], "40 essais tenus en 90 jours")
        self.assertTrue(t["body"].startswith("Salles de sport : 40 essais encadrés tenus dans votre club en 90 jours."))
        self.assertIn("90 € remboursés par essai manquant, ou 45 jours de plus sans frais.", t["body"])
        self.assertEqual(t["desc"], "Garantis ou remboursés")

    def test_variante_performance_ne_change_que_la_garantie(self):
        P = self.projet()
        n = P.niche("paysagistes")
        t, tp = projet_mod.textes_pub(P, n), projet_mod.textes_pub(P, n, True)
        self.assertEqual(tp["desc"], "Payé à la performance")
        self.assertEqual(t["title"], tp["title"])
        self.assertIn("Garanties ou remboursées", t["body"])
        self.assertNotIn("Garanties ou remboursées", tp["body"])

    def test_resume_incomplet_arrete(self):
        P = self.projet()
        n = P.niche("paysagistes")
        del n["resume"]["ligne_metier"]
        with self.assertRaises(SystemExit):
            projet_mod.textes_pub(P, n)


class Logique(CopieDuProjet):
    def test_sous_le_seuil_aucun_prospect(self):
        P = self.projet()
        r = projet_mod.regles_logique(P, P.niche("salles-de-sport"))
        q1 = [x for x in r if x[0] == "Vous êtes ?"]
        q2 = [x for x in r if x[0] != "Vous êtes ?"]
        self.assertEqual(len(q1), 4)
        self.assertTrue(all(x[2].startswith("Q2 ") for x in q1), "chaque réponse de Q1 doit pointer vers Q2, sinon Meta ne publie pas")
        self.assertEqual([x[3] for x in q2], ["aucun prospect", "prospect", "prospect", "prospect", "prospect"])

    def test_seuil_deplace(self):
        P = self.projet()
        P.cfg["formulaire"]["tranches_non_qualifiees"] = 2
        r = projet_mod.regles_logique(P, P.niche("salles-de-sport"))
        self.assertEqual([x[3] for x in r[4:]], ["aucun prospect", "aucun prospect", "prospect", "prospect", "prospect"])
        self.assertTrue(any("formulaire_ca_min" in x for x in projet_mod.controle_resume(P, P.niche("salles-de-sport"))))

    def test_lien_marque_non_qualifie(self):
        P = self.projet()
        n = P.niche("paysagistes")
        self.assertIn("utm_medium=formulaire_instantane_non_qualifie", P.lien_reservation(n, qualifie=False))
        P.etat["campagne"], P.etat["adsets"]["paysagistes"] = "C1", "A1"
        self.assertTrue(P.lien_reservation(n).endswith("utm_campaign=paysagistes&utm_id=C1&utm_term=A1"))


class Resume(CopieDuProjet):
    def test_exemple_coherent(self):
        P = self.projet()
        for n in P.niches():
            self.assertEqual(projet_mod.controle_resume(P, n), [], n["cle"])

    def test_incoherences_signalees(self):
        P = self.projet()
        n = P.niche("salles-de-sport")
        n["resume"]["remboursement_par_unite"] = 150
        n["resume"]["profils_vises"] = ["Profil inconnu"]
        pb = " | ".join(projet_mod.controle_resume(P, n))
        self.assertIn("loin de offre.prix_ht", pb)
        self.assertIn("profil visé absent", pb)
        self.assertIn("garantie_phrase ne reprend pas 150", pb)


class Simulation(CopieDuProjet):
    def setUp(self):
        super().setUp()
        for cible, nom in ((socket.socket, "connect"), (subprocess, "run")):
            garde = mock.patch.object(cible, nom, side_effect=AssertionError("appel réseau ou navigateur en simulation"))
            garde.start()
            self.addCleanup(garde.stop)

    def lancer(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = meta_campagne.main([str(self.dir), *args])
        return code, out.getvalue()

    def test_parcours_complet_puis_reprise(self):
        code, out = self.lancer("parcours", "--dry-run")
        self.assertEqual(code, 0, out)
        self.assertIn("TOTAL : 24 publicités, 24 sur le bon formulaire ; dépense des ad sets actifs : 0 €/jour", out)
        etat = json.loads((self.dir / "_meta" / "etat.dry-run.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(etat["adsets"]), ["paysagistes", "salles-de-sport"])
        self.assertEqual(sum(len(v) for v in etat["pubs"].values()), 24)
        self.assertFalse((self.dir / "_meta" / "etat.json").exists(), "la simulation ne doit jamais écrire l'état réel")
        monde = self.dir / "_meta" / "monde.dry-run.json"
        avant = json.loads(monde.read_text(encoding="utf-8"))["seq"]
        code, out = self.lancer("parcours", "--dry-run")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(monde.read_text(encoding="utf-8"))["seq"], avant, "une relance ne doit rien recréer")

    def test_tout_est_cree_en_pause(self):
        self.lancer("parcours", "--dry-run")
        monde = json.loads((self.dir / "_meta" / "monde.dry-run.json").read_text(encoding="utf-8"))["objets"]
        for o in monde.values():
            if o["type"] in ("campaign", "adset"):
                self.assertEqual(o["status"], "PAUSED", o["name"])

    def test_activer_exige_oui(self):
        self.lancer("parcours", "--dry-run")
        with self.assertRaises(SystemExit):
            self.lancer("activer", "--dry-run")
        code, out = self.lancer("activer", "--oui", "--dry-run")
        self.assertIn("30 €/jour au total", out)

    def test_parcours_refuse_en_reel(self):
        with self.assertRaises(SystemExit):
            self.lancer("parcours")

    def test_reel_sans_jeton_s_arrete_avant_le_reseau(self):
        with self.assertRaises(SystemExit) as ctx:
            self.lancer("campagne")
        self.assertIn("META_ACCESS_TOKEN", str(ctx.exception))


class Creatives(CopieDuProjet):
    def test_specs_de_l_exemple(self):
        P = self.projet()
        for n in P.niches():
            spec = json.loads((n["chemin"] / "creatives" / "spec.json").read_text(encoding="utf-8"))
            erreurs, _ = spec_check.controler(P, n, spec)
            self.assertEqual(erreurs, [], n["cle"])

    def test_build_spec_tient_les_regles(self):
        P = self.projet()
        for n in P.niches():
            spec = build_spec.construire(P, n)
            self.assertEqual(len({i["format"] for i in spec}), 10)
            self.assertEqual(spec_check.controler(P, n, spec)[0], [])

    def test_prix_et_mots_interdits_bloques(self):
        P = self.projet()
        n = P.niche("salles-de-sport")
        spec = build_spec.construire(P, n)
        mauvais = copy.deepcopy(spec)
        mauvais[0]["expect"].append("3 600 € HT")
        mauvais[0]["prompt"] = mauvais[0]["prompt"].replace("TEXT RULES:", '"3 600 € HT" TEXT RULES:')
        mauvais[1]["expect"].append("Essai gratuit !")
        mauvais[1]["prompt"] = mauvais[1]["prompt"].replace("TEXT RULES:", '"Essai gratuit !" TEXT RULES:')
        erreurs = " | ".join(spec_check.controler(P, n, mauvais)[0])
        self.assertIn("prix de l'offre", erreurs)
        self.assertIn("gratuit", erreurs)
        self.assertIn("point d'exclamation", erreurs)

    def test_ligne_attendue_non_citee(self):
        P = self.projet()
        n = P.niche("paysagistes")
        spec = build_spec.construire(P, n)
        spec[2]["expect"].append("Texte jamais demandé")
        self.assertTrue(any("pas cité tel quel" in e for e in spec_check.controler(P, n, spec)[0]))


class Scripts(unittest.TestCase):
    def test_sequence_de_l_exemple(self):
        env = {k: v for k, v in os.environ.items() if k not in CLES_ENV}
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "sequences" / "verifier.py"), str(EXEMPLE)], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Tout passe.", r.stdout)

    def test_sequence_avec_chiffre_invente(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = pathlib.Path(tmp) / "projet"
            shutil.copytree(EXEMPLE, dest, ignore=shutil.ignore_patterns("_meta"))
            f = dest / "sequences-email" / "sequence-formulaire.json"
            s = json.loads(f.read_text(encoding="utf-8"))
            e = s["niches"]["salles-de-sport"]["emails"]["E-IF-3"]
            e["texte"] = e["texte"].replace("Un essai réservé", "Déjà 6 clubs nous font confiance. Un essai réservé")
            f.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / "sequences" / "verifier.py"), str(dest)], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("« 6 » introuvable", r.stdout)

    def test_tout_compile(self):
        for f in ROOT.glob("scripts/**/*.py"):
            compile(f.read_text(encoding="utf-8"), str(f), "exec")


if __name__ == "__main__":
    unittest.main()
