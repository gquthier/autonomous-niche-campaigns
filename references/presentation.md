# La présentation commerciale d'une niche (15 pages)

Un PDF de 15 diapositives, 1280 × 720, écrit en HTML puis rendu en PDF. Il présente **l'offre de la niche à tout professionnel de ce métier**. Il ne nomme aucun prospect.

**Une proposition pour UN prospect nommé** (son entreprise, son site, ses chiffres) relève d'un autre outil : [autonomous-sales-proposal](https://github.com/gquthier/autonomous-sales-proposal).

Rédaction : un agent par niche (le modèle le plus fort disponible), en parallèle, une fois `offre.md`, `publicite.md` et `resume.json` écrits.

## À lire d'abord, en entier

1. **La présentation générique de l'agence** (`projet.json` → `agence.presentation_generique`) : c'est la base de mise en page (feuille de style, composants, polices, logo) et la seule source des preuves. Même structure, même design. Si l'agence n'en a pas, utilise le style neutre décrit plus bas.
2. Le dossier de la niche : `offre.md` (source de vérité de l'offre), `resume.json` (chiffres, bonus, garantie), `publicite.md`, et `analyse.md` pour les mots du métier, l'avatar, les objections et la réglementation.
3. `projet.json` → `agence` (nom, site, positionnement) et `offre` (prix, garantie, installation, budget publicitaire).

## Le cadre (Alex Hormozi)

- **Valeur** : le résultat rêvé, dans les mots du métier, avec le volume, dès la couverture.
- **Preuve avant l'offre** : les résultats réels de l'agence, avant tout prix.
- **Effort et délai réduits** : le délai de `offre.installation`, « Votre part » en une heure.
- **Bonus** : chacun règle un problème précis du métier et se présente par la situation désirée.
- **Pile de valeur relue juste avant le prix**, prix « ailleurs » sourcés.
- **Risque inversé** : la garantie écrite, mot pour mot, avec sa définition.
- **Urgence vraie seulement** (une exclusivité de zone réellement tenue, une saison réelle). Jamais « plus que 3 places » si ce n'est pas vrai.

## Les 15 diapositives

Numéros de section dans les étiquettes : 01 Objectif · 02 Nos résultats · 03 Le déroulé · 04 L'infrastructure · 05 Bonus · 06 L'offre · 07 La garantie · 08 La suite. Pied de chaque page : le nom de l'agence à gauche, `N / 15` à droite.

| # | Diapositive | Fond | Contenu |
|---|---|---|---|
| 1 | **Couverture** | sombre | Étiquette « Pour les <métier> · 90 jours ». Titre : le volume et l'unité longue, le chiffre en couleur d'accent (« 40 essais encadrés tenus dans votre club en 90 jours. »). Sous-titre : ce qui est installé, le délai, la garantie courte. Trois pastilles : prix et durée · garantie en quelques mots · délai de mise en place. Pied : le positionnement / le site de l'agence |
| 2 | **Vos objectifs** | clair | Six cartes, six objectifs dits pour ce métier, tirés de l'avatar et des objections d'`analyse.md` (plus de <unité>, ne plus travailler pour rien, savoir ce que coûte une <unité>, ne plus rater un appel…) |
| 3 | **Preuves : chiffres clés** | clair | Repris de la présentation générique, à l'identique |
| 4 | **Preuves : études de cas** | clair | Idem, sans changer un chiffre ni un nom |
| 5 | **Preuves : autres résultats** | clair | Idem. Seule la phrase du bas s'adapte : « Ces résultats viennent d'autres métiers que le vôtre. C'est pour cela que notre engagement est écrit : » + la garantie de la niche |
| 6 | **Preuves : témoignages** | sombre | Idem, à l'identique |
| 7 | **Le déroulé** | clair | « Installé en <délai>, piloté pendant 90 jours. » Cinq étapes : Jour 0 démarrage (appel de 30 minutes, critères, accès, photos) ; installation ; lancement (budget publicitaire minimum de la niche) ; pilotage jusqu'au jour 90 ; Jour 90 bilan (ce que déclenche la garantie). Puis « Votre part » et « Ce que vous gardez » |
| 8 | **L'infrastructure** | clair | « Une infrastructure, pas une campagne… ». Chaîne de quatre cartes avec flèches, dans le vocabulaire du métier : 01 campagnes (ce qu'elles montrent, à qui, quelle zone) → 02 préqualification (les questions de tri, le consentement) → 03 agent IA (répond, vérifie, écarte, réserve) → « Vous » en carte sombre (la fiche reçue). Bandeau du bas : les quatre bonus en une ligne |
| 9 à 12 | **Un bonus par diapositive** | clair | Gabarit identique pour les quatre (ci-dessous) |
| 13 | **L'offre** | clair | Pile de valeur en tableau resserré : 01 à 03 le cœur (« Le cœur » dans la colonne « Ailleurs »), B1 à B4 les bonus avec leur prix ailleurs, « + Inclus sans supplément » (délai, comptes au nom du client, point hebdomadaire, ligne directe, garantie en une ligne). Bandeau sombre : durée, « réglé au départ », budget publicitaire minimum réglé à Meta ; à droite le prix et « 90 jours · garantis ou remboursés » |
| 14 | **La garantie** | sombre | `garantie_phrase` **mot pour mot**, sans guillemets, le volume et le remboursement en couleur d'accent. Trois cartes chiffrées : le volume · le remboursement par unité (« jusqu'à <prix> HT ; ou, à votre choix, <prolongation> jours de plus sans frais ») · le budget publicitaire minimum. En petit : la définition de l'unité, la contestation sous 48 heures, la prolongation si une condition manque côté client, « Aucun engagement sur les ventes. Conditions au contrat. » |
| 15 | **La suite** | sombre | « Trois étapes, et votre infrastructure tourne. » 1 Votre accord (contrat signé à distance, zone et critères en annexe) · 2 L'appel de démarrage · 3 « <délai> plus tard » (annonces en ligne, agent qui répond, premières <unités>). Pied : l'offre en une ligne (prix · durée · volume · garantie courte) et le site |

### Le gabarit des diapositives de bonus

- En haut : `05 · Bonus N sur 4` avec quatre petits traits (le N-ième en encre), et à droite le nom du bonus.
- Grand titre : la **situation désirée** (`bonus[].situation_desiree`).
- Trois cartes côte à côte : « Aujourd'hui » (le problème dans les mots du client) · « Ce que nous installons » (ce que fait l'agent IA) · « Ce que vous y gagnez » (carte sombre, texte plus grand).
- Bandeau sombre en bas : à gauche « Ailleurs : … » avec le prix de marché en gras et sa **source en petit** ; à droite « Inclus dans votre accompagnement » en couleur d'accent. Sans prix sourcé dans `offre.md`, une phrase sans prix (« c'est le travail d'un assistant commercial, aux heures de bureau »).

### Les preuves (diapositives 3 à 6)

Reprends les preuves de la présentation générique **sans changer un chiffre ni un nom**. L'agence n'a en général aucun client dans la niche : n'en invente pas, et ne laisse entendre nulle part que ces résultats viennent de ce métier (la phrase du bas de la diapositive 5 le dit). Si l'agence n'a pas de quoi remplir quatre diapositives de preuves réelles, n'invente rien : signale-le au dirigeant avant de rédiger, et retire les diapositives vides plutôt que de les remplir.

## Règles de texte

- **N'invente rien.** Chaque chiffre (prix, volume, durée, budget, remboursement, prix « ailleurs ») vient de `offre.md` ou de `resume.json`. Un élément manque : n'écris pas la ligne, signale-le.
- Mêmes chiffres partout : couverture, diapositive 5, déroulé, offre, garantie, dernière page.
- Respecte la réglementation relevée (`resume.json` → `reglementation`) : mentions, mots interdits, promesses interdites.
- Vouvoiement, phrases courtes, aucun emoji, aucun point d'exclamation, apostrophes typographiques (’), espaces insécables dans les montants (`3&nbsp;600&nbsp;€`). Les mots du métier, pas le jargon d'agence.
- Écris « budget annoncé » si le budget est seulement déclaré par le prospect ; « vérifié » seulement si l'agent le vérifie vraiment.

## Le style

**Toujours d'abord** : copie la feuille de style de la présentation générique de l'agence plutôt que de la réécrire. À défaut, un style neutre qui a fait ses preuves :

- Diapositive : `.slide` de 1280 × 720, marges 54 / 72 / 58 px, `@page{size:1280px 720px;margin:0}`, une `<section class="slide" data-cle="…">` par page, `.slide.dark` pour les fonds sombres.
- Couleurs en variables CSS : un fond clair chaud, des cartes un ton plus clair, une encre presque noire, un gris pour le texte secondaire, un fond sombre pour les diapositives `dark`, **une seule** couleur d'accent (celle de l'agence) pour les chiffres (`em.b`).
- Trois familles au plus : une linéale géométrique légère pour les titres, une linéale lisible pour le texte, une chasse fixe pour les étiquettes en capitales espacées. Polices sous licence libre, copiées dans `presentation/fonts/`. Logo de l'agence en SVG en ligne, couleur `currentColor`.
- Composants : `.top` (étiquettes du haut), `.foot` (pied), `.card`, `.grid.g3`, `.tag` (pastilles), `.pill` (bandeau sombre), `.num` et `.big` (chiffres), `table.tight` (pile de valeur), `.bonus .trio` (trois cartes).
- Une seule idée par diapositive, beaucoup d'air, rien de collé au pied.

## Fabrication

Dans `<dossier de niche>/presentation/` : copie les polices dans `fonts/`, écris `presentation.html`, puis rends-le avec le script de rendu d'[autonomous-sales-proposal](https://github.com/gquthier/autonomous-sales-proposal) (Playwright) :

```bash
cd "<dossier de niche>/presentation"
node <chemin d'autonomous-sales-proposal>/scripts/render.cjs presentation.html
```

Il écrit le PDF et une image par page, et **échoue** si un contenu déborde d'une diapositive, si une image manque, ou si le PDF ne compte pas une page par diapositive. Corrige (texte plus court, police resserrée sur la pile de valeur) et relance jusqu'au succès. Sans ce script : Chrome sans interface (`--headless --print-to-pdf`), format 16:9, une page par diapositive, puis contrôle à l'œil de chaque page.

## Contrôle avant livraison

1. **Ouvre chacune des 15 images de page.** Regarde : alignements, titres coupés au mauvais endroit, cartes de même hauteur, rien de collé au pied, numérotation « N / 15 ».
2. Prix, volume, remboursement et garantie identiques sur les pages 1, 5, 7, 13, 14 et 15, et identiques à `resume.json`.
3. Diapositives 3 à 6 identiques à la présentation générique (chiffres et noms).
4. Les quatre bonus de la présentation sont ceux de `resume.json` → `bonus`, dans le même ordre, avec les mêmes prix « ailleurs » et sources.
5. Aucune phrase interdite par la réglementation du métier ; aucun nom de prospect.

Réponse de l'agent, 8 lignes au plus : chemins du HTML et du PDF, ce que dit la couverture, la phrase de garantie retenue, et tout ce qu'il n'a pas pu écrire faute de source.

Ne publie rien, n'envoie rien.
