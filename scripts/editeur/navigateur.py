#!/usr/bin/env python3
"""Exécute du JavaScript dans l'onglet Meta Business Suite (formulaires instantanés) du navigateur de la personne, déjà connecté à Meta.
macOS seulement (AppleScript). Arc : rien à régler. Google Chrome : menu Présentation > Options pour les développeurs >
« Autoriser JavaScript à partir des événements Apple ».
Le JS reçoit une boîte à outils `H` (texte visible, clic comme une souris, saisie dans un champ React).

Usage :
  python3 navigateur.py <projet> ouvrir            trouve l'onglet des formulaires instantanés, ou l'ouvre ; note l'onglet dans _meta/editeur.json
  python3 navigateur.py <projet> js '<code JS>'    exécute le code (il doit `return` une valeur sérialisable) et affiche le résultat
Module : from navigateur import Onglet ; Onglet(projet).js(code)"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from projet import Projet  # noqa: E402

AIDES = r"""
var H = window.__H = (function(){
  function vis(e){ var r=e.getBoundingClientRect(); return r.width>1 && r.height>1 && getComputedStyle(e).visibility!=='hidden'; }
  function txt(e){ return (e.innerText||e.textContent||'').replace(/\s+/g,' ').trim(); }
  function all(sel, root){ return Array.prototype.slice.call((root||document).querySelectorAll(sel)); }
  function click(e){
    e.scrollIntoView({block:'center'}); var r=e.getBoundingClientRect(), x=r.left+r.width/2, y=r.top+r.height/2;
    ['pointerover','pointerenter','mouseover','pointerdown','mousedown','pointerup','mouseup','click'].forEach(function(n){
      var C = n.indexOf('pointer')===0 ? PointerEvent : MouseEvent;
      e.dispatchEvent(new C(n,{bubbles:true,cancelable:true,view:window,clientX:x,clientY:y,button:0,pointerType:'mouse',isPrimary:true})); });
    return true;
  }
  function setValue(el, value){
    var proto = el.tagName==='TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto,'value').set.call(el, value);
    el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); return el.value;
  }
  function dialogs(){ return all('[role=dialog]').filter(vis); }
  return {vis:vis, txt:txt, all:all, click:click, setValue:setValue, dialogs:dialogs};
})();
"""


def osa(script, timeout=90):
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if not r.returncode else "ERR " + r.stderr.strip()[:300]


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


class Onglet:
    def __init__(self, projet):
        self.p = projet if isinstance(projet, Projet) else Projet(projet)
        self.app = self.p.get("formulaire", "navigateur", defaut="Arc")
        if self.app not in ("Arc", "Google Chrome"):
            raise SystemExit(f"navigateur non pris en charge : {self.app} (Arc ou Google Chrome)")
        self.fichier = self.p.racine / "_meta" / "editeur.json"
        self.cible = json.loads(self.fichier.read_text()) if self.fichier.exists() else None

    def url_formulaires(self):
        return f"https://business.facebook.com/latest/instant_forms/forms?asset_id={self.p.meta_id('page_id')}" + (
            f"&business_id={self.p.meta_id('business_id', requis=False)}" if self.p.meta_id("business_id", requis=False) else "")

    def _fenetres(self):
        n = osa(f'tell application "{self.app}" to count windows')
        return int(n) if n.isdigit() else 0

    def _localiser(self):
        """(index de fenêtre, index d'onglet) de l'onglet noté, ou None."""
        if not self.cible:
            return None
        for i in range(1, self._fenetres() + 1):
            if osa(f'tell application "{self.app}" to get id of window {i}') == self.cible["fenetre"]:
                ids = osa(f'tell application "{self.app}" to get id of every tab of window {i}').split(", ")
                if self.cible["onglet"] in ids:
                    return i, ids.index(self.cible["onglet"]) + 1
        return None

    def ouvrir(self):
        if self._localiser():
            return "onglet déjà noté"
        for i in range(1, self._fenetres() + 1):
            urls = osa(f'tell application "{self.app}" to get URL of every tab of window {i}').split(", ")
            for j, u in enumerate(urls, start=1):
                if "business.facebook.com/latest/instant_forms" in u and f"asset_id={self.p.meta_id('page_id')}" in u:
                    self._noter(i, j); return f"onglet trouvé : fenêtre {i}, onglet {j}"
        if not self._fenetres():
            osa(f'tell application "{self.app}" to make new window')
        osa(f'tell application "{self.app}" to tell front window to make new tab with properties {{URL:{q(self.url_formulaires())}}}')
        n = int(osa(f'tell application "{self.app}" to count tabs of front window') or 1)
        self._noter(1, n)
        return "onglet ouvert : se connecter à Meta dans cet onglet si la page le demande, puis relancer"

    def _noter(self, i, j):
        self.cible = {"application": self.app, "fenetre": osa(f'tell application "{self.app}" to get id of window {i}'),
                      "onglet": osa(f'tell application "{self.app}" to get id of tab {j} of window {i}')}
        self.fichier.parent.mkdir(parents=True, exist_ok=True); self.fichier.write_text(json.dumps(self.cible))

    def js(self, code):
        loc = self._localiser()
        if not loc:
            raise SystemExit("onglet de travail introuvable : lancer `navigateur.py <projet> ouvrir`")
        w, t = loc
        js = AIDES + "\n(function(){ try { var __r = (function(){ " + code + " })(); return JSON.stringify(__r === undefined ? null : __r); } catch(e){ return JSON.stringify({erreur: String(e && e.stack || e).slice(0,400)}); } })()"
        if self.app == "Arc":
            out = osa(f'tell application "Arc" to tell tab {t} of window {w} to execute javascript {q(js)}')
        else:
            out = osa(f'tell application "Google Chrome" to execute tab {t} of window {w} javascript {q(js)}')
        if out.startswith("ERR"):
            if "JavaScript" in out and self.app == "Google Chrome":
                raise SystemExit("Chrome refuse le JavaScript : Présentation > Options pour les développeurs > Autoriser JavaScript à partir des événements Apple")
            return out
        try:
            v = json.loads(out)
            return json.loads(v) if isinstance(v, str) else v
        except Exception:
            return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    o = Onglet(sys.argv[1])
    if sys.argv[2] == "ouvrir":
        print(o.ouvrir())
    elif sys.argv[2] == "js":
        print(json.dumps(o.js(sys.argv[3]), ensure_ascii=False, indent=1)[:6000])
    else:
        sys.exit(__doc__)
