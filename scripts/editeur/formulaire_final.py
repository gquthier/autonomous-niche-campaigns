#!/usr/bin/env python3
"""Formulaire final d'une niche, dans l'éditeur de Meta Business Suite (l'API ne sait ni poser une logique conditionnelle ni une seconde page de fin) :
copie du formulaire de base « IF - <Niche> (base) » créé par l'API, nommée « IF - <Niche> », puis
  - question 1 (« Vous êtes ? ») : chaque réponse → question 2 ;
  - question 2 (chiffre d'affaires) : les N premières tranches (sous le seuil) → « Fermer le formulaire » = page de fin des non-prospects,
    AUCUN prospect pour Meta ; les autres → « Envoyer le formulaire » = page de fin des prospects ;
  - les deux pages de fin identiques (titre, texte, bouton vers le calendrier), lien marqué « non qualifié » pour les non-prospects ;
  - publication, puis vérification par l'API et note de l'identifiant dans _meta/etat.json.
S'arrête à la première vérification manquée en laissant l'éditeur ouvert (rien n'est publié dans ce cas).
Usage : python3 formulaire_final.py <projet> <clé de niche>"""
import json
import sys
import time
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI)); sys.path.insert(0, str(ICI.parent / "lib"))
from projet import Projet  # noqa: E402
from meta import Meta  # noqa: E402
from navigateur import Onglet  # noqa: E402
from editeur import Editeur, L  # noqa: E402

P = Projet(sys.argv[1]); N = P.niche(sys.argv[2]); M = Meta(P)
BASE, FINAL = P.nom_formulaire(N, base=True), P.nom_formulaire(N)
FIN = P["formulaire"]["page_fin"]
NON_QUALIFIEES = int(P.get("formulaire", "tranches_non_qualifiees", defaut=1))
PICKER = ('var d = H.dialogs().filter(function(x){ var t = H.txt(x); return t.indexOf(%s)===0 && t.indexOf(%s)>0 && t.indexOf(%s)<0; })[0];'
          % (json.dumps(L["dialogue"]), json.dumps(L["copier"]), json.dumps(L["constructeur"])))


def etape(msg):
    print("—", msg, flush=True)


def stop(msg):
    sys.exit(f"ARRÊT ({N['cle']}) : {msg}")


# 0. ce que contient le formulaire de base (lu par l'API : intitulés exacts, nombre de réponses)
base_id = P.etat["formulaires_base"].get(N["cle"])
if not base_id:
    stop("formulaire de base absent : lancer d'abord `meta_campagne.py <projet> formulaires`")
fb = M.get(base_id, token=M.page_token(), fields="name,status,questions{key,label,type,options}")
qs = [q for q in fb.get("questions", []) if q["type"] == "CUSTOM"]
if len(qs) < 2:
    stop(f"le formulaire de base n'a pas ses deux questions : {fb}")
Q1, Q2 = qs[0]["label"], qs[1]["label"]
R1 = [o["value"] for o in qs[0]["options"]]; R2 = [o["value"] for o in qs[1]["options"]]
if any(" ".join(x["name"].split()) == FINAL for x in M.formulaires()):
    stop(f"« {FINAL} » existe déjà sur la page : lancer `meta_campagne.py <projet> trouver --ecrire` au lieu de le recréer")

O = Onglet(P); print(O.ouvrir()); E = Editeur(O)
if E.dialogues():
    stop(f"un dialogue est déjà ouvert dans l'onglet de travail : {E.dialogues()} (le fermer à la main, sans archiver ni « OK » sur « Fermer le formulaire prospect ? »)")

# 1. ouvrir une copie du formulaire de base
etape("créer un formulaire, copier un formulaire existant")
if not E.js(f'var b = H.all("[role=button],button,a").filter(function(e){{ return H.vis(e) && H.txt(e)==={json.dumps(L["dialogue"])}; }})[0]; if(b){{ H.click(b); }} return !!b;'):
    stop("bouton « Créer un formulaire » introuvable : l'onglet n'est pas sur la liste des formulaires instantanés de la page")
for _ in range(10):
    time.sleep(1.5)
    if E.js(PICKER + 'return !!d;'):
        break
else:
    stop("le dialogue de création ne s'est pas ouvert")
E.js(PICKER + f'var l = H.all("*", d).filter(function(e){{ return H.vis(e) && e.children.length===0 && H.txt(e)==={json.dumps(L["copier"])}; }})[0]; if(l){{ H.click(l); }} return !!l;')
time.sleep(2.5)
for essai in range(4):
    etape(f"choisir « {BASE} » (essai {essai + 1})")
    # le champ de recherche n'affiche ses choix qu'après des événements de focus simulés
    E.js(PICKER + 'var f = H.all("input[role=combobox]", d).filter(H.vis)[0]; if(!f) return false; f.blur(); f.dispatchEvent(new FocusEvent("focusin",{bubbles:true})); f.focus(); f.dispatchEvent(new FocusEvent("focus",{bubbles:false})); H.click(f); return true;')
    time.sleep(2.5)
    E.js(f'var o = H.all("[role=option]").filter(function(o){{ return H.vis(o) && H.txt(o).indexOf({json.dumps(BASE, ensure_ascii=False)} + " ")===0; }})[0]; if(o){{ H.click(o); }} return !!o;')
    time.sleep(2)
    if E.js(PICKER + 'var f = H.all("input[role=combobox]", d).filter(H.vis)[0]; return f ? f.value : null;') != BASE:
        continue
    E.js(PICKER + f'var b = H.all("[role=button],button", d).filter(function(b){{ return H.vis(b) && H.txt(b)==={json.dumps(L["suivant"])} && b.getAttribute("aria-disabled")!=="true"; }})[0]; if(b){{ H.click(b); }} return !!b;')
    for _ in range(8):
        time.sleep(2.5)
        if E.constructeur_ouvert():
            break
    if E.constructeur_ouvert():
        break
else:
    stop("l'éditeur ne s'est pas ouvert sur la copie")

# 2. bonne copie ? puis le nom final
assert E.cliquer_texte(L["etape_type"]) is True; time.sleep(2.5)
f = E.champs()
if not (f and f[0]["ph"].startswith(L["nom_placeholder"]) and f[0]["v"].startswith(BASE)):
    stop(f"mauvaise copie ouverte : {f[:1]}")
if E.saisir(0, FINAL) != FINAL:
    stop("nom non saisi")
etape(f"nom : {FINAL}")

# 3. logique conditionnelle
assert E.cliquer_texte(L["etape_questions"]) is True; time.sleep(3)
if not E.logique_active(activer=True):
    stop("logique conditionnelle non activée")
etape("question 1 : toutes les réponses vont à la question 2")
if not E.cliquer_feuille(Q1):
    stop(f"carte de la question 1 introuvable : « {Q1} »")
time.sleep(2.5)
if len(E.menus()) != len(R1):
    stop(f"question 1 : {len(E.menus())} menus pour {len(R1)} réponses")
for i in range(len(R1)):
    if E.regler(i, L["aller_question"], "Q2 " + Q2) != "Q2 " + Q2:
        stop(f"question 1, réponse {i + 1} non reliée")
r1 = E.regles(); print("  ", r1)
if not (len(r1) == len(R1) and all(b == Q2 for _, b in r1)):
    stop(f"règles de la question 1 inattendues : {r1}")
etape(f"question 2 : {NON_QUALIFIEES} tranche(s) sous le seuil sortent sans prospect, les autres continuent")
if not E.cliquer_feuille(Q2):
    stop(f"carte de la question 2 introuvable : « {Q2} »")
time.sleep(2.5)
if len(E.menus()) != len(R2):
    stop(f"question 2 : {len(E.menus())} menus pour {len(R2)} réponses")
for i in range(len(R2)):
    if i < NON_QUALIFIEES:
        if "non-prospects" not in (E.regler(i, L["fermer"]) or ""):
            stop(f"question 2, réponse {i + 1} : la sortie vers la page des non-prospects n'est pas posée")
    elif not str(E.regler(i, L["envoyer"], L["page_fin_1"])).startswith("E1"):
        stop(f"question 2, réponse {i + 1} : pas reliée à la page de fin des prospects")
r2 = E.regles(); print("  ", r2)
attendu = [(R2[i], L["page_non_prospects"] if i < NON_QUALIFIEES else "Leads ending page 1") for i in range(len(R2))]
if r2 != attendu:
    stop(f"règles de la question 2 inattendues : {r2} (attendu {attendu})")

# 4. pages de fin : identiques, lien marqué non qualifié pour les non-prospects
etape("pages de fin")
assert E.cliquer_texte(L["etape_fin"]) is True; time.sleep(2.5)
if not E.cliquer_feuille(L["page_non_prospects"]):
    stop("carte de la page des non-prospects introuvable")
time.sleep(2)
f = E.champs()
if not (len(f) >= 5 and f[0]["v"] == L["page_non_prospects"]):
    stop(f"champs inattendus sur la page des non-prospects : {f}")
for i, v in enumerate([FIN["titre"], FIN["texte"], FIN["bouton"], P.lien_reservation(N, qualifie=False)], start=1):
    if E.saisir(i, v) != v:
        stop(f"page des non-prospects : champ {i} non saisi")
time.sleep(1.5)
if not any(E.cliquer_feuille(x) for x in L["page_prospects"]):
    stop("carte de la page des prospects introuvable")
time.sleep(2)
f = E.champs()
if not (len(f) >= 5 and f[1]["v"] == FIN["titre"] and f[3]["v"].startswith("http") and f[4]["v"] == FIN["bouton"]):
    stop(f"page des prospects inattendue (elle doit venir du formulaire de base) : {f}")
nom_e1 = P.get("formulaire", "nom_page_prospects", defaut="Page de fin des prospects")
if E.saisir(0, nom_e1) != nom_e1 or E.saisir(3, P.lien_reservation(N)) != P.lien_reservation(N):
    stop("page des prospects : nom ou lien non saisi")
time.sleep(1.5)
t = E.texte(longueur=30000)
i = t.find(L["apercu_debut"]); apercu = t[i:i + 700] if i >= 0 else ""
print("aperçu des fins :", apercu[:400])
if not (apercu.count(FIN["titre"]) == 2 and apercu.count(FIN["bouton"]) >= 2 and L["apercu_non_prospect"] in apercu):
    stop("les deux pages de fin ne sont pas identiques dans l'aperçu")
if "requis" in t.lower():
    stop("un champ requis manque (voir le texte de l'éditeur)")

# 5. publication
assert E.cliquer_texte(L["etape_fin"]) is True; time.sleep(2)
if E.cliquer_texte(L["publier"]) is not True:
    stop("bouton « Créer le formulaire » grisé ou absent")
for _ in range(10):
    time.sleep(4)
    d = E.dialogues()
    autres = [x for x in d if not str(x).startswith(L["dialogue"])]
    if autres:
        stop(f"dialogue inattendu après publication : {autres} (si « Créer le formulaire » ne fait rien, une réponse n'est pas reliée)")
    if not d:
        break
else:
    stop("l'éditeur ne s'est pas fermé : la publication n'a pas eu lieu (une réponse sans logique bloque la publication sans message)")

# 6. vérification par l'API, puis note de l'identifiant
time.sleep(3)
hits = [x for x in M.formulaires() if " ".join(x["name"].split()) == FINAL]
if len(hits) != 1:
    stop(f"« {FINAL} » introuvable par l'API après publication ({len(hits)} trouvé(s))")
P = Projet(sys.argv[1]); P.etat["formulaires"][N["cle"]] = hits[0]["id"]; P.sauver()
print("FAIT :", FINAL, hits[0]["id"])
