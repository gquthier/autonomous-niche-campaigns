# Les créatives statiques d'une niche

Dix publicités Meta statiques par niche, dix formats différents, plus deux variantes « performance ». Ce sont les publicités **de l'agence**, adressées aux professionnels du métier (le gérant de salle, le paysagiste), pas à leurs clients. Le dirigeant choisit les meilleures.

La demande, telle qu'elle a été validée : « high design, gros impact », lumineuses mais vraiment simples, **bas de funnel**, l'offre irrésistible au centre, la cible nommée de façon extrêmement précise, inspirées de ce qui dure dans la Bibliothèque publicitaire (voir `etude-niche.md`). Une première direction sombre et chargée a été refusée.

## Ce que chaque image fait, dans cet ordre

1. **Arrêter le bon regard** : le professionnel se reconnaît en une demi-seconde. Son métier est écrit en haut (`cible_pub` en capitales espacées), ou un objet, un lieu, un écran de son quotidien le dit.
2. **Poser l'offre** : le volume est l'élément le plus gros de l'image.
3. **Lever le risque** : `garantie_courte`, mot pour mot, sur un surligneur.
4. **Donner le délai** : `offre.installation` en pastille.

Rien d'autre. Une idée par image, **25 mots au plus** (sauf les formats « écran », note, agenda, certificat).

## Les textes : seulement ceux de la niche

Les textes viennent **uniquement** de `resume.json` (`cible_pub`, `promesse_pub`, `unite_longue`, `unite_courte`, `garantie_courte`, `garantie_phrase`, `remboursement_par_unite`, `unite_manquante`, `titres`) et de `projet.json` → `offre`. Interdits à l'image :
- tout chiffre, preuve, client, témoignage ou prix inventé ; **le prix de l'offre** ; « 0 € », « rien à la signature », « vous ne payez que… » (le prix est réglé au départ, ces phrases seraient fausses) ;
- le montant remboursé (« 90 € remboursés par essai manquant ») sur plus de **trois** images sur dix ;
- tout nom de marque ou logo (Meta, WhatsApp, Google, Apple, opérateur, enseigne du métier), bouton factice, emoji, point d'exclamation, hashtag, « gratuit » si l'offre ne le dit pas ;
- faux article de presse, faux avis, fausse capture de résultats.

Une fiche ou une notification fictive porte « Exemple de fiche » en petit, et ses valeurs restent dans la définition de l'unité (un budget au-dessus du plancher, pas un montant flatteur). Respecte `resume.json` → `reglementation` : si une formulation y est déconseillée, prends la version prudente.

`scripts/creatives/spec_check.py` contrôle ces règles **avant** de payer une image.

## Direction artistique : « lumière »

- **Fonds clairs** : blanc pur `#FFFFFF`, blanc cassé chaud `#F6F2EA`, ou un aplat de la couleur d'accent. Photos en plein jour, hautes lumières, couleurs franches. Aucune ambiance nocturne ; une image sur dix au plus à fond sombre, et seulement pour le contraste.
- **Une couleur d'accent par niche**, choisie pour le métier et tenue sur les dix images (exemple fictif : orange vif `#F26B1D` pour les salles de sport, vert profond `#2E7D5B` pour le paysage). Surligneur jaune `#FFE14D` sous la garantie. Encre `#100F0D`.
- **Typographie** : une linéale géométrique très grasse (l'esprit de Jost Bold ou Futura Bold), chiffres énormes, interlignage serré ; petites étiquettes en capitales espacées.
- **Hiérarchie fixe** : étiquette de cible en haut → chiffre géant (environ 30 % de la hauteur) → unité sur deux ou trois lignes → barre jaune avec la garantie → pastille d'accent avec le délai → pied vide si logo.
- **Niveau** : une marque premium : beaucoup de blanc, une marge stricte, un seul point focal, ombres douces, coins arrondis. Jamais l'esthétique « promo » (éclairs, flèches rouges, dégradés criards, pictogrammes en rafale).
- **Personnes** : professionnels crédibles, non retouchés, sans sourire forcé, de dos ou visage en flou si possible. Aucune personnalité, aucun mineur. Aucun robot, cerveau ni circuit : l'agent IA est un moyen, pas le sujet.

## Les dix formats de la livraison de référence

| # | Format | Ce qui le rend efficace |
|---|---|---|
| 1 | **Carte typographique** : fond `#F6F2EA`, tout aligné à gauche, chiffre géant en accent, logo | La promesse entière, un seul point focal |
| 2 | **Aplat de couleur** : fond d'accent, texte blanc centré, chiffre géant, logo clair | La plus forte pour arrêter le pouce |
| 3 | **Photo du métier en plein jour** avec une carte blanche d'offre par-dessus | Montre l'unité promise (un nouveau venu accueilli par un coach) |
| 4 | **Objet du métier porteur du texte** (chevalet, panneau, véhicule floqué, plaque) vu de face, 70 à 75 % de la largeur | Le mécanisme de la garantie écrit sur l'objet où il affiche ses prix |
| 5 | **Note de téléphone** (application de notes, très gros caractères, liste cochée) | Aspect natif, garantie complète en cinq lignes, budget publicitaire dit |
| 6 | **Écran verrouillé avec notifications** de nouvelles demandes, vocabulaire du métier | Ce qu'il sait avant que le client entre ; « Exemple de fiche » |
| 7 | **Comparatif en deux colonnes** : « Un contact acheté » (gris) / l'unité tenue (accent) | Parle à celui qui achète déjà des contacts |
| 8 | **Agenda de la semaine rempli**, un créneau mis en avant | Le résultat sous la forme où il le vit |
| 9 | **Carton d'invitation adressé à la cible**, posé sur sa table de travail, vue de dessus, objets du métier autour | Il reconnaît sa table en une demi-seconde |
| 10 | **Certificat de garantie avec sceau** | Pour celui qui a déjà vu « 30 essais garantis » : l'engagement écrit, avec son montant |

Autres formats possibles, sans répéter un format dans la même niche : conversation par messages (4 à 6 bulles courtes), post-it ou tableau blanc écrit à la main, reçu qui liste ce qui est inclus et finit par la garantie, illustration au trait élégante, question frontale en très gros (« Salles de sport : combien d'essais ce mois-ci ? »), carte de visite ou courrier. **La facture à 0,00 € est exclue** tant que le prix est réglé au départ (elle a été retirée de la référence et remplacée par le certificat).

## Écrire une consigne d'image (GPT Image)

Consignes en anglais, textes français entre guillemets doubles. Le modèle rend le français sans faute **si chaque phrase est citée et si tout autre mot est interdit**. Ce qui a marché :
- Commence par la nature de l'image (« Flat graphic design, premium typographic poster, no photograph, no illustration, no icon. » ou « Photorealistic top-down flat-lay photograph, bright soft daylight, high-key… »).
- Donne le fond et **chaque couleur en hexadécimal**.
- Décris **de haut en bas**, éléments numérotés, avec leur position (« at 8% of the canvas height ») et la marge (« left-aligned on one strict left margin at 9% of the canvas width »).
- Dis sur combien de lignes va chaque texte et où il se coupe : `on 2 lines: "essais encadrés tenus dans" / "votre club en 90 jours."`
- Dis la taille relative : « gigantic numeral "40" … about 30% of the canvas height, by far the biggest element ».
- Écran de téléphone : « Realistic full-frame screenshot of the Notes app on a smartphone, light mode, French interface, no phone bezel, no hand », « no carrier name », heure « 09:41 ». Pas de nom de marque dans la consigne.
- Objet imprimé : vu de face ou de dessus, « perfectly flat and straight », 70 à 75 % de la largeur ; objets autour « never covering its text ».
- Écriture manuscrite : « large, neat, perfectly legible handwriting ».
- Deux colonnes : « exactly the same size », « natural letter proportions, never condensed and never squeezed ».
- **Logo** : ne le fais **jamais** dessiner. Termine la composition par le bloc `FOOT` et mets `"logo": "noir"` (fond clair) ou `"clair"` (fond sombre ou d'accent). Trois ou quatre images sur dix suffisent.

Blocs fixes (dans `scripts/creatives/build_spec.py`, à reprendre tels quels) :

```python
FOOT = "Leave the bottom 10% of the canvas completely empty: plain background, no text, no line, no shape."
BAR = ("a highlighter-yellow (#FFE14D) bar with slightly rounded corners, like one clean marker stroke, only as wide as its "
       "text plus padding, holding one single line of large bold ink-black (#100F0D) text, clearly larger than the pill text")
FONT = "a very bold geometric sans-serif (the spirit of Jost Bold or Futura Bold), tight line spacing"
RULES = ("TEXT RULES: render the French text EXACTLY as written between the double quotation marks: same words, same accents "
  "(é, è, ê, à, â, ç, î), same apostrophes and punctuation, each sentence complete, sharp and fully legible, never cropped. "
  "Do not render the quotation marks themselves. Do not add any other word, number, slogan, logo, brand name, watermark, emoji, "
  "exclamation mark, hashtag, sticker or fake button. Keep every piece of text at least 7% away from each edge of the canvas. "
  "FORMAT: static advertisement for the Meta feed, portrait 4:5, bright, clean, premium, high-impact, French market.")
```

Pratique validée : les phrases sont des constantes (`G = garantie_courte`, `INST = installation`) réutilisées à la fois dans la consigne et dans `expect` : le texte demandé et le texte contrôlé ne peuvent pas diverger. `build_spec.py <projet> <niche>` écrit un premier jet des dix formats ainsi construits, à partir de `resume.json` (et de `creatives_en` pour les détails visuels du métier). L'agent de la niche relit et adapte chaque consigne, puis lance `spec_check.py`. Exemples complets : `examples/agence-exemple/*/creatives/spec.json`.

## Le fichier `creatives/spec.json`

Une liste de dix objets :

```json
{"id": "N101-carte-typographique", "format": "Carte typographique", "prompt": "… TEXT RULES: …",
 "expect": ["SALLES DE SPORT", "40", "essais encadrés tenus dans", "votre club en 90 jours.", "Garantis ou remboursés.", "Mise en place en 5 jours"],
 "logo": "noir"}
```

- `id` : `N<rang de la niche><01 à 10>-<nom-court>`, stable. Une régénération garde l'id et prend un suffixe de version.
- `format` : le nom du format, en français.
- `prompt` : la consigne complète, `RULES` compris.
- `expect` : **chaque ligne de texte attendue à l'image, telle qu'elle est citée dans la consigne** (une entrée par ligne coupée). C'est ce que vérifie l'OCR.
- `logo` : `null`, `"noir"` ou `"clair"`.
- Facultatif : `aspect` (par défaut `"4:5"`).
- **Ordre** : mets en premier les deux créatives qui recevront une variante « performance » (la carte typographique, puis l'aplat ou la photo du métier). `variantes.py` prend les deux premières, sauf si `resume.json` → `variantes_performance` en désigne d'autres.

## Le flux

Scripts dans `scripts/creatives/`, tous appelés avec `<projet> <clé de niche>` (lis l'en-tête de chacun). Clé : `KIE_API_KEY`, jamais affichée. Les fichiers vont dans `<dossier de niche>/creatives/work/` puis `final/`.

0. **Préparer** : `build_spec.py <projet> <niche>` (premier jet), relecture, puis `spec_check.py <projet> <niche>` jusqu'à 0 erreur. `gen.py <projet> <niche> --dry-run` donne le nombre d'images et le coût, sans clé.
1. **Générer** : `python3 scripts/creatives/gen.py <projet> <niche> [id ...]` (variables : `POOL` tâches en parallèle, `VERSION=b` pour une seconde version). GPT Image chez kie.ai, texte vers image, 4:5, 2K, qualité haute ; 2 à 4 minutes par image. Chaque tâche est notée avant l'attente : **une relance reprend les tâches déjà payées sans les repayer**. Lance en arrière-plan si la commande dépasse ton délai.
2. **Contrôler le texte** : `check.py <projet> <niche>` lit chaque image par OCR (Vision, macOS ; l'outil se compile seul la première fois) et écrit `work/check.json` : phrases manquantes et lignes en plus. Un « À VOIR » peut être un faux manque (accent mal lu sur un très gros titre, écriture manuscrite, « m² ») : vérifie à l'œil. Une ligne « en plus » réelle (mot ajouté par le modèle) impose de refaire.
3. **Regarder chaque image** : `apercu.py <projet> <niche>` écrit des aperçus dans `work/view/` ; ouvre-les un par un, en directeur artistique sévère : faute, mot en trop, lisibilité à la taille d'un téléphone, luminosité, impact, crédibilité des personnes et des objets du métier, zone sombre en bordure, respect de l'offre.
4. **Refaire** ce qui ne passe pas : corrige la consigne, puis `VERSION=b … gen.py <projet> <niche> <id>`. **Cinq régénérations au plus par niche.** Un détail minime (un plafonnier sombre en bordure) se retouche à la main, sans génération.
5. **Choisir** : note la version retenue dans `work/sel.json` : `{"N101-carte-typographique": "N101-carte-typographique-b.png"}`.
6. **Finir** : `finish.py <projet> <niche>` exporte dix JPEG et `final/_planche.jpg`. Le logo de l'agence (`projet.json` → `agence.logo_noir` / `logo_clair`) est posé par programme, centré, **seulement si le bas de l'image est vraiment vide** ; sinon le script le dit (« pied non vide ») et l'image part sans logo. Regarde la planche.
7. **Variantes « performance »** : `variantes.py <projet> gen|check|finish [niche ...]` (`gen --dry-run` d'abord). Pour **deux** créatives par niche, la même image où seule `garantie_courte` devient `offre.variante_performance` (« Payé à la performance. »), par modification d'image (image vers image). Dans une niche où le paiement au résultat est réglementé, mets `variantes_performance_en_pause: true` dans `resume.json` (voir `offre.md`, section 8). L'OCR vérifie que la nouvelle phrase est là **et que l'ancienne a disparu**. Sortie : `final/<id>-performance.jpg`, logo reposé.

## Coût

Environ **18 crédits kie.ai par image** en texte vers image, **20 en image vers image**. Budget d'une niche : 10 images + 5 régénérations au plus + 2 variantes ≈ 310 crédits ; deux versions complètes d'une niche ont coûté environ 400 crédits sur le projet d'origine. Le script refuse de lancer sous la réserve (`projet.json` → `creatives.reserve_credits`) : vérifie le solde avant de lancer plusieurs niches en parallèle.

## Contrôle avant de rendre la main

- 10 images, 10 formats différents, la cible nommée sur chacune.
- OCR : chaque phrase de `expect` présente, aucun mot ajouté, vérifié à l'œil.
- Mêmes chiffres que `resume.json` ; garantie mot pour mot ; aucun prix d'offre ; montant remboursé sur trois images au plus.
- Une seule couleur d'accent, fonds clairs, logo jamais dessiné par le modèle.
- Les deux variantes ne diffèrent de leur original que par la phrase de garantie.

## `creatives/LISEZ-MOI.md`

En tête : format et taille (4:5, 2048 × 2560, JPEG), couleurs, d'où viennent les textes, la phrase de garantie, ce qu'aucune image ne porte. Puis un tableau `# | Fichier | Format | Texte exact à l'image | Pourquoi elle devrait fonctionner`, le classement des trois meilleures, les versions et les crédits consommés, et les **doutes** (offre et réglementation, direction artistique). Exemple de doute à signaler : « Garantis ou remboursés. » peut se lire comme un remboursement intégral alors que la garantie est au prorata ; la phrase complète doit figurer dans le texte sous la publicité.

Ne publie rien, ne touche à aucun compte publicitaire pendant cette étape.
