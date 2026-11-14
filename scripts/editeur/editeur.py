"""Briques de pilotage de l'éditeur de formulaire instantané de Meta Business Suite, par le DOM : on lit du texte, on clique des éléments
repérés par leur texte, on relit pour vérifier. Interface de Meta en FRANÇAIS : les libellés sont dans `L` ; pour une autre langue, les adapter.
Testé sur Arc en novembre 2026, sur une vingtaine de formulaires publiés. Meta change son interface : si une vérification échoue, regarder le texte réel
avec `texte()` et ajuster `L`."""
import json
import re
import time

L = {
    "dialogue": "Créer un formulaire",              # titre du dialogue de création ET du constructeur
    "copier": "Copier un formulaire existant",
    "suivant": "Suivant",
    "constructeur": "Type de formulaire",            # présent seulement dans le constructeur
    "etape_type": "Type de formulaire", "etape_questions": "Questions", "etape_fin": "Fin",
    "nom_placeholder": "Nommez",
    "logique": "Logique conditionnelle",
    "aller_question": "Accéder à une question", "envoyer": "Envoyer le formulaire", "fermer": "Fermer le formulaire",
    "page_fin_1": "Page de fin 1", "page_non_prospects": "Page de fin pour les non-prospects",
    "page_prospects": ["Page de fin pour les prospects", "End page for leads"],
    "publier": "Créer le formulaire",
    "apercu_debut": "Politique de confidentialité Envoyer",
    "apercu_non_prospect": "Votre réponse ne sera pas envoyée",
}
BUILDER = f'var d = H.dialogs().filter(function(x){{ return H.txt(x).indexOf({json.dumps(L["dialogue"])})===0; }})[0];'
COMBOS = BUILDER + 'var c = H.all("[role=combobox]", d).filter(H.vis);'
# Chaque menu de logique a SA liste (aria-owns) ; plusieurs listes restent affichées en même temps : toujours viser celle du menu cliqué.
OWN = COMBOS + 'var cb = c[%d]; var l = cb && document.getElementById(cb.getAttribute("aria-owns")); function leaf(t){ return l && H.all("*", l).filter(function(e){ return e.children.length===0 && H.txt(e)===t; })[0]; } '


class Editeur:
    def __init__(self, onglet):
        self.o = onglet

    def js(self, code):
        return self.o.js(code)

    def dialogues(self):
        return self.js('return H.dialogs().map(function(x){ return H.txt(x).slice(0,60); });') or []

    def constructeur_ouvert(self):
        return any(L["constructeur"] in str(x) for x in self.dialogues())

    def menus(self):
        return self.js(COMBOS + 'return c.map(function(e){ return H.txt(e).replace(/\\u200b/g,"").trim(); });') or []

    def regler(self, index, premier, second=None):
        """Règle le menu de logique n° index : premier niveau (« Accéder à une question », « Envoyer… », « Fermer… »), puis le second s'il y en a un."""
        self.js(OWN % index + 'if(cb){ H.click(cb); } return !!cb;'); time.sleep(1.4)
        retour = self.js(OWN % index + f'if(!l) return "liste absente"; if(leaf({json.dumps(premier, ensure_ascii=False)})) return "niveau 1"; '
                         'var b = H.all("[role=button]", l).filter(function(e){ return H.txt(e).replace(/\\u200b/g,"").trim()===""; })[0]; '
                         'if(b){ H.click(b); return "retour"; } return "ni choix ni retour : " + H.txt(l).slice(0,80);')
        if retour == "retour":
            time.sleep(1.2)
        self.js(OWN % index + f'var x = leaf({json.dumps(premier, ensure_ascii=False)}); if(x){{ H.click(x); return "ok"; }} return "absent";'); time.sleep(1.4)
        if second:
            self.js(OWN % index + f'var x = leaf({json.dumps(second, ensure_ascii=False)}); if(x){{ H.click(x); return "ok"; }} return "absent";'); time.sleep(1.4)
        return self.js(OWN % index + 'return H.txt(cb).replace(/\\u200b/g,"").trim();')

    def cliquer_texte(self, texte, sel='[role=button],[role=tab],button'):
        return self.js(BUILDER + f'var b = H.all({json.dumps(sel)}, d).filter(function(e){{ return H.vis(e) && H.txt(e).replace(/\\u200b/g,"").trim()==={json.dumps(texte, ensure_ascii=False)}; }})[0]; '
                       'if(b && b.getAttribute("aria-disabled")!=="true"){ H.click(b); return true; } return b ? "grisé" : false;')

    def cliquer_feuille(self, texte, x_max=1300):
        """Élément sans enfant au texte exact (déplie les cartes Q1, Q2, E1, E2 de la colonne de gauche)."""
        return self.js(BUILDER + f'var l = H.all("*", d).filter(function(e){{ return H.vis(e) && e.children.length===0 && H.txt(e)==={json.dumps(texte, ensure_ascii=False)} && e.getBoundingClientRect().left < {x_max}; }})[0]; '
                       'if(l){ H.click(l); } return !!l;')

    def champs(self):
        return self.js(BUILDER + 'return H.all("input,textarea", d).filter(function(e){ return H.vis(e) && e.type!=="radio" && e.type!=="checkbox"; })'
                       '.map(function(e){ return {v: e.value, ph: e.placeholder}; });') or []

    def saisir(self, index, valeur):
        return self.js(BUILDER + f'var f = H.all("input,textarea", d).filter(function(e){{ return H.vis(e) && e.type!=="radio" && e.type!=="checkbox"; }})[{index}]; '
                       f'if(!f) return "champ absent"; f.focus(); H.setValue(f, {json.dumps(valeur, ensure_ascii=False)}); f.dispatchEvent(new Event("blur",{{bubbles:true}})); return f.value;')

    def texte(self, debut=None, longueur=900):
        t = self.js(BUILDER + 'return d ? H.txt(d) : null;')
        if not isinstance(t, str):
            return ""
        if debut:
            i = t.find(debut); t = t[i:] if i >= 0 else ""
        return t[:longueur]

    def regles(self):
        """Les règles affichées sous chaque réponse (Meta les écrit en anglais, même dans l'interface française)."""
        t = self.texte(longueur=30000)
        return [(a.strip(), b.strip()) for a, b in re.findall(r"If answer is (.+?), then go to (.+?)(?= Appliquez| ​|$)", t)]

    def logique_active(self, activer=False):
        code = BUILDER + f'var cb = H.all("input[type=checkbox]", d).filter(function(e){{ return e.getAttribute("aria-label")==={json.dumps(L["logique"])}; }})[0]; '
        if activer:
            self.js(code + 'if(cb && !cb.checked){ cb.click(); } return true;'); time.sleep(2.5)
        return bool(self.js(code + 'return !!(cb && cb.checked);'))
