#!/usr/bin/env python3
"""Premier jet de creatives/spec.json pour une niche : dix formats différents, consignes GPT Image écrites avec les blocs validés,
textes tirés UNIQUEMENT de resume.json et de projet.json → offre. Le texte demandé dans la consigne et le texte contrôlé par l'OCR
(`expect`) viennent des mêmes constantes : ils ne peuvent pas diverger.

C'est un point de départ : l'agent de la niche relit chaque consigne, l'adapte au métier (objets, lieu, personnes), puis lance
spec_check.py. Les détails visuels du métier se donnent en anglais dans resume.json → "creatives_en" (facultatif) :
  {"accent": "#2E7D5B", "accent_nom": "deep green", "scene": "<photo du métier en plein jour>", "objets": ["...", "..."],
   "objet_porteur": "<objet du métier qui porte le texte>", "table": "<surface de travail du métier, vue de dessus>"}

Usage : python3 build_spec.py <projet> <niche> [--force] [--stdout]"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from projet import Projet  # noqa: E402

FOOT = "Leave the bottom 10% of the canvas completely empty: plain background, no text, no line, no shape."
BAR = ("a highlighter-yellow (#FFE14D) bar with slightly rounded corners, like one clean marker stroke, only as wide as its "
       "text plus padding, holding one single line of large bold ink-black (#100F0D) text, clearly larger than the pill text")
FONT = "a very bold geometric sans-serif (the spirit of Jost Bold or Futura Bold), tight line spacing"
RULES = ("TEXT RULES: render the French text EXACTLY as written between the double quotation marks: same words, same accents "
         "(é, è, ê, à, â, ç, î), same apostrophes and punctuation, each sentence complete, sharp and fully legible, never cropped. "
         "Do not render the quotation marks themselves. Do not add any other word, number, slogan, logo, brand name, watermark, emoji, "
         "exclamation mark, hashtag, sticker or fake button. Keep every piece of text at least 7% away from each edge of the canvas. "
         "FORMAT: static advertisement for the Meta feed, portrait 4:5, bright, clean, premium, high-impact, French market.")
INK = "#100F0D"


def couper(texte, largeur=26):
    """Coupe une phrase en lignes d'au plus `largeur` signes, sans couper un mot."""
    lignes, cur = [], ""
    for mot in texte.split():
        if cur and len(cur) + 1 + len(mot) > largeur:
            lignes.append(cur)
            cur = mot
        else:
            cur = f"{cur} {mot}".strip()
    return lignes + ([cur] if cur else [])


def q(lignes):
    """« on N lines: "a" / "b" » : la consigne dit où chaque ligne se coupe."""
    lignes = [lignes] if isinstance(lignes, str) else lignes
    corps = " / ".join(f'"{x}"' for x in lignes)
    return corps if len(lignes) == 1 else f"on {len(lignes)} lines: {corps}"


def construire(P, n):
    r, o = n["resume"], P["offre"]
    manque = [k for k in ("cible_pub", "volume_garanti", "unite_longue", "unite_courte", "unite_manquante", "remboursement_par_unite") if k not in r]
    if manque:
        raise SystemExit(f"{n['cle']} : resume.json incomplet pour les créatives, il manque {manque}")
    cx = r.get("creatives_en", {}) or {}
    A = cx.get("accent", "#2E7D5B")
    AN = cx.get("accent_nom", "accent colour")
    objets = cx.get("objets") or ["two or three tidy, unbranded tools of the trade"]
    scene = cx.get("scene") or "a credible professional of the trade at work, seen from behind, in a bright daylight workplace"
    porteur = cx.get("objet_porteur") or "a clean A-frame sign board standing in front of the business"
    table = cx.get("table") or "a light wooden work desk"

    CIBLE = r["cible_pub"].upper()
    V = str(r["volume_garanti"])
    JOURS = f"en {o.get('duree_jours', 90)} jours."
    UL = couper(f"{r['unite_longue']} {JOURS}")
    UC = r["unite_courte"]
    G = r.get("garantie_courte", o["garantie_courte"])
    INST = o.get("installation", "")
    REMB = f"{r['remboursement_par_unite']} € remboursés par {r['unite_manquante']}"
    PROL = f"Ou {o['prolongation_jours']} jours de plus sans frais, à votre choix" if o.get("prolongation_jours") else ""
    BUDGET = "Budget publicitaire en plus"
    pref = f"N{n['rang']}"
    spec = []

    def add(num, nom, fmt, prompt, expect, logo=None):
        spec.append({"id": f"{pref}{num:02d}-{nom}", "format": fmt, "prompt": f"{prompt} {RULES}",
                     "expect": [e for e in expect if e], "logo": logo})

    pill = f'a {AN} ({A}) rounded pill with bold white text: "{INST}"' if INST else ""

    # 1. Carte typographique : la promesse entière, un seul point focal
    add(1, "carte-typographique", "Carte typographique",
        "Flat graphic design, premium typographic poster, no photograph, no illustration, no icon. Background: a perfectly uniform warm off-white (#F6F2EA) "
        "over the whole canvas, no texture, no frame. Everything is left-aligned on one strict left margin at 9% of the canvas width. TEXT, from top to bottom. "
        f'(1) Near the top, at 8% of the canvas height: a small bold uppercase label with wide letter spacing, {AN} ({A}): "{CIBLE}". '
        f'(2) Under it: a gigantic numeral "{V}" in {AN} ({A}), in {FONT}, about 30% of the canvas height, by far the biggest element of the image. '
        f"(3) Right under the numeral, in the same font, ink black ({INK}), large, {q(UL)}. (4) Under it, after a clear gap: {BAR}: \"{G}\". "
        + (f"(5) Under it: {pill}. " if pill else "")
        + f"Generous empty space on the right, strict alignment, one single focal point, the restraint of a premium brand. {FOOT}",
        [CIBLE, V] + UL + [G, INST], "noir")

    # 2. Aplat de couleur : le plus fort pour arrêter le pouce
    add(2, "aplat-couleur", "Aplat de couleur",
        f"Flat graphic design, bold colour-block poster, no photograph, no illustration, no icon. Background: one perfectly uniform flat {AN} ({A}) over the whole canvas. "
        f'Everything centred. TEXT, from top to bottom: (1) at 9% of the canvas height, a small bold uppercase white label with wide letter spacing: "{CIBLE}". '
        f'(2) a gigantic white numeral "{V}" in {FONT}, about 32% of the canvas height. (3) under it, bold white, large, {q(UL)}. '
        f'(4) a white rounded bar holding one line of large bold ink-black ({INK}) text: "{G}". '
        + (f'(5) under it, small bold white text: "{INST}". ' if INST else "") + FOOT,
        [CIBLE, V] + UL + [G, INST], "clair")

    # 3. Photo du métier en plein jour, carte d'offre blanche par-dessus
    add(3, "photo-metier", "Photo du métier en plein jour avec carte d'offre",
        f"Photorealistic photograph, bright natural daylight, high-key, luminous, real and unretouched: {scene}. No face in sharp focus, no logo, no readable sign. "
        "Over the lower-middle part of the photo: a pure white card with soft rounded corners and a soft shadow, about 78% of the canvas width, left edge at 11%. "
        f'TEXT on the card, left-aligned: (1) small bold uppercase label, {AN} ({A}), wide letter spacing: "{CIBLE}". (2) a very large numeral "{V}" in {AN} ({A}), {FONT}. '
        f'(3) bold ink black ({INK}) {q(couper(UC + " " + JOURS, 22))}. (4) {BAR}: "{G}". Nothing else written anywhere in the image.',
        [CIBLE, V] + couper(UC + " " + JOURS, 22) + [G])

    # 4. Objet du métier porteur du texte
    add(4, "objet-porteur", "Objet du métier porteur du texte",
        f"Photorealistic photograph, bright soft daylight, high-key: {porteur}, seen exactly from the front, perfectly flat and straight, about 72% of the canvas width, centred. "
        f"Background softly out of focus, light and clean. TEXT printed on the object, crisp, centred, from top to bottom: (1) bold uppercase {AN} ({A}) label: \"{CIBLE}\". "
        f'(2) a gigantic ink-black numeral "{V}", {FONT}. (3) bold ink black {q(couper(UC + " " + JOURS, 20))}. (4) {BAR}: "{G}". '
        + (f"(5) {pill}. " if pill else "") + "No other text anywhere.",
        [CIBLE, V] + couper(UC + " " + JOURS, 20) + [G, INST])

    # 5. Note de téléphone : aspect natif, garantie complète
    titre5 = [f"{r['cible_pub']} :", f"{V} {UC}", JOURS.rstrip(".")]
    liste5 = [G.rstrip("."), REMB, PROL, INST, BUDGET]
    add(5, "note-telephone", "Note de téléphone",
        "Realistic full-frame screenshot of the Notes app on a smartphone, light mode, pure white background, French interface, no phone bezel, no hand. "
        'Status bar with the time "09:41", then signal, wifi and battery icons, no carrier name. Top-left: a yellow back chevron followed by "Notes" in yellow. '
        f"Standard system typography, large and readable. Note content: a very large bold black title {q(titre5)}. Under it, a checklist, each item with a round "
        f"yellow ticked checkbox, in this order: {' / '.join(chr(34) + x + chr(34) for x in liste5 if x)}. Text size very large, like the largest accessibility "
        "setting: title and checklist fill about 80% of the screen height, an item may wrap on two lines. Nothing else on the note.",
        ["09:41", "Notes"] + titre5 + liste5)

    # 6. Écran verrouillé avec notifications du métier
    notifs = r.get("notifications") or ["Nouvelle demande", "Rendez-vous confirmé", "Rendez-vous confirmé"]
    add(6, "ecran-notifications", "Écran verrouillé avec notifications",
        "Realistic full-frame smartphone lock screen, light bright wallpaper (soft pale gradient), no phone bezel, no hand, no carrier name, no app logo. "
        f'Large clock "09:41" at the top. Under it, a small bold uppercase label in {AN} ({A}): "{CIBLE}". Then {len(notifs)} stacked white rounded notification cards, '
        f"each with one bold line: {' / '.join(chr(34) + x + chr(34) for x in notifs)}. Under the cards: {BAR}: \"{G}\". "
        'At the very bottom, small grey text: "Exemple de fiche".',
        ["09:41", CIBLE] + notifs + [G, "Exemple de fiche"])

    # 7. Comparatif en deux colonnes
    gauche, droite = ["Un contact acheté", "à rappeler vous-même"], [f"{V} {UC}", "dans votre agenda"]
    add(7, "comparatif", "Comparatif en deux colonnes",
        f"Flat graphic design on a pure white background, no photograph. At the top, centred, a small bold uppercase {AN} ({A}) label: \"{CIBLE}\". "
        "Two rounded columns side by side, exactly the same size, natural letter proportions, never condensed and never squeezed: "
        f"left column light grey (#ECEAE6) with grey text {q(gauche)}; right column {AN} ({A}) with bold white text {q(droite)}. "
        f'Under the columns, centred: {BAR}: "{G}". {FOOT}',
        [CIBLE] + gauche + droite + [G], "noir")

    # 8. Agenda de la semaine rempli
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    add(8, "agenda-semaine", "Agenda de la semaine rempli",
        "Clean flat illustration of a weekly calendar view on a white background, light mode, five day columns with these headers: "
        f"{' / '.join(chr(34) + j + chr(34) for j in jours)}. Several time slots are filled with plain {AN} ({A}) blocks without any text; one block on Thursday is highlighted "
        f'with a soft glow. Above the calendar, left-aligned: a small bold uppercase {AN} label "{CIBLE}", then a huge numeral "{V}" and the words "{UC}" in ink black, {FONT}. '
        f'Under the calendar: {BAR}: "{G}". {FOOT}',
        jours + [CIBLE, V, UC, G], "noir")

    # 9. Carton d'invitation sur la table de travail, vue de dessus
    add(9, "carton-invitation", "Carton d'invitation adressé à la cible, vue de dessus",
        f"Photorealistic top-down flat-lay photograph, camera perfectly vertical, bright soft daylight, high-key, soft natural shadows. The whole canvas is {table}. "
        "Centred: a thick matte pure-white invitation card, portrait, perfectly flat and straight, about 70% of the canvas width, top edge at 13% and bottom edge at 85% of the "
        f"canvas height. Neatly arranged around the card and never covering its text: {', '.join(objets[:3])}. Nothing else. TEXT printed on the card, centred: "
        f'(1) a small bold uppercase {AN} ({A}) label with wide letter spacing: "RÉSERVÉ AUX {CIBLE}". (2) a gigantic ink-black numeral "{V}", {FONT}. '
        f'(3) bold ink black {q([UC, JOURS])}. (4) {BAR}: "{G}". ' + (f"(5) at the bottom of the card, {pill}." if pill else ""),
        [f"RÉSERVÉ AUX {CIBLE}", V, UC, JOURS, G, INST])

    # 10. Certificat de garantie avec sceau
    add(10, "certificat-garantie", "Certificat de garantie avec sceau",
        "Photorealistic photograph of an elegant printed certificate on thick cream paper (#FBF8F1), seen exactly from the front, perfectly flat, thin fine double border "
        f"in {AN} ({A}), a round embossed {AN} seal at the bottom right with no text in it. Bright, soft, premium. TEXT on the certificate, centred: "
        f'(1) small uppercase spaced: "CERTIFICAT DE GARANTIE". (2) small bold uppercase {AN} label: "{CIBLE}". (3) large bold ink black: "{V} {UC}". (4) "{JOURS.rstrip(".")}". '
        f'(5) {BAR}: "{REMB}". ' + (f'(6) small ink text: "{PROL}". ' if PROL else "") + "No signature scribble, no other text.",
        ["CERTIFICAT DE GARANTIE", CIBLE, f"{V} {UC}", JOURS.rstrip("."), REMB, PROL])
    return spec


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 2
    P = Projet(args[0])
    n = P.niche(args[1])
    spec = construire(P, n)
    texte = json.dumps(spec, indent=1, ensure_ascii=False)
    if "--stdout" in argv:
        print(texte)
        return 0
    dest = n["chemin"] / "creatives" / "spec.json"
    if dest.exists() and "--force" not in argv:
        print(f"{dest} existe déjà : relancer avec --force pour l'écraser (la spec a peut-être été retouchée à la main)")
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(texte + "\n", encoding="utf-8")
    print(f"{len(spec)} consignes écrites dans {dest.relative_to(P.racine)} ; relire et adapter au métier, puis spec_check.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
