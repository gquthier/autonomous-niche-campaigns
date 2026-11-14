# Étudier une niche

But : savoir, avant d'écrire une offre, si le métier peut payer `{offre.prix}` réglés au départ, ce qu'il compte, ce qu'il a déjà vu passer, ce que la loi lui interdit, et avec quels mots il parle. Une étude faible donne une offre fausse : tout le reste du skill (offre, présentation, créatives, formulaire, e-mails) recopie ce qui est écrit ici.

Deux temps :
1. **Le tri** (une fois par projet) : une liste longue de métiers, notée, pour garder les niches qui peuvent payer.
2. **L'étude de chaque niche retenue** : `<dossier de niche>/analyse.md`, un agent par niche, en parallèle.

## Règles qui valent pour toute l'étude

- **Chaque chiffre porte sa source (lien) et son niveau** : `[mesuré]` (statistique publique, comptes déposés, chiffre d'enseigne publié), `[estimé]` (calcul, fourchette d'un tiers), `[vendeur]` (déclaré par quelqu'un qui vend), `[inconnu]` (cherché, pas trouvé). Pas de chiffre sans source. Un `[inconnu]` écrit vaut mieux qu'un chiffre plausible : l'offre se calibre dessus.
- **Une citation entre « » est un texte lu**, avec sa date et son lien. Les phrases de douleur réécrites par l'agent se disent « dans les mots du métier », jamais comme des citations.
- **Aucune preuve inventée.** L'agence n'a en général aucun client dans la niche : le dire.
- **Ne rien publier, ne rien envoyer, ne toucher à aucun compte publicitaire** pendant l'étude.
- Écrire en français, phrases courtes, aucun emoji, aucun point d'exclamation.

## 1. Le tri des niches

Écris la liste longue (12 à 20 métiers) puis note chacun. Ce qui a marché sur le projet d'origine : une quinzaine de niches notées par trois agents « juges » aux angles différents, puis un pré-mortem par finaliste ; la décision et le classement sont écrits dans un fichier JSON (`_commun/premiere-etude/decision.json`).

### Grille de notation (sur 100)

| Critère | Poids | Ce qu'on regarde |
|---|---:|---|
| Saturation des agences | 20 | Combien vendent déjà des contacts ou des rendez-vous à ce métier, avec quelles promesses |
| Panier moyen | 15 | Ce que rapporte une vente au client du métier |
| Pouvoir d'achat | 15 | Chiffre d'affaires par établissement, résultat net, ce qu'il dépense déjà en publicité |
| Meta adapté | 15 | Ses clients sont-ils sur Facebook et Instagram ; catégorie spéciale (Logement, Crédit, Emploi, produits financiers) |
| Maturité de vente | 10 | Un vendeur, un rendez-vous, un devis, une signature : le métier sait-il transformer un contact |
| Clients particuliers | 10 | Une vente locale à des particuliers se pilote bien sur Meta |
| Ancrage local | 5 | Un lieu, une zone de chalandise, un rendez-vous physique |
| Cols blancs | 5 | Un gérant qui lit, décide et répond aux e-mails |
| Croissance, rachats | 5 | Marché qui monte, consolidation, fonds qui rachètent |

Malus : taille du noyau sous le seuil fixé par le dirigeant ; métier déjà saturé de vendeurs de contacts (bâtiment, énergie).

Trois angles de juge, chacun choisit sa niche et note les autres :
- **Économie de l'offre** : coût total pour le client sur 90 jours (prix + publicité), marge par vente, nombre de ventes pour rentrer dans ses frais, délai avant que l'argent rentre.
- **Exécution Meta et conformité** : annonceurs actifs, coût par demande publié, catégorie spéciale, réglementation de la publicité et du rappel.
- **Mise sur le marché de l'agence** : accès au décideur (décide-t-il seul ou un siège décide-t-il), liste facile à bâtir, réseaux et franchises (levier ou frein).

Puis un **pré-mortem** par finaliste : « on a échoué dans 90 jours, pourquoi ? » ; verdict `go`, `go_sous_conditions` ou `no_go`, probabilité de réussite, bloquants.

### Les niches à écarter

Le modèle est un forfait payé au départ, garanti au prorata (voir `offre.md`). Écarte, ou mets en dernier, la niche où :

| Motif | Pourquoi | Exemples typiques |
|---|---|---|
| **L'argent du client rentre après les 90 jours** | Il paie d'avance et n'encaisse rien pendant le contrat : pas de renouvellement, pas de cas client avant des mois | Honoraires payés à la vente plusieurs mois après le mandat ; intermédiaire payé au déblocage des fonds |
| **La saison tombe hors de la fenêtre** | Une garantie ratée se rattrape l'année suivante | Piscine et jardin (l'essentiel se décide au printemps) |
| **La marge par vente est trop faible** | Il faut trop de ventes pour couvrir prix + publicité | Revente à faible marge unitaire |
| **Le prix vaut plusieurs fois son budget marketing habituel** | Il ne paiera pas, ou seulement s'il va mal (sélection adverse) | Métiers qui dépensent très peu en publicité |
| **La réglementation menace le canal ou le mode de paiement** | La publicité ou la rémunération peut devenir illégale en cours de contrat | Santé, professions à ordre |
| **Le noyau solvable est trop petit** | Quelques centaines de comptes : la réputation circule vite, peu de clients possibles | Spécialités très étroites |
| **Personne ne décide seul** | Le siège capte les demandes ou impose son prestataire | Franchises qui pilotent la publicité locale |

Test rapide de capacité à payer : `(prix + publicité sur 90 jours) ÷ marge par vente` = ventes nécessaires. Si ce nombre n'est pas atteignable avec un taux de signature prudent sur le volume promis, la niche ne tient pas. La meilleure raison de retenir une niche en premier est mesurée et simple : **l'argent du client rentre pendant le contrat** (acompte à la commande, cycle de vente court).

Le dirigeant valide la liste des niches retenues. Chacune reçoit une entrée dans `projet.json` → `niches` (`cle`, `dossier`, `label`, `ads_library`).

## 2. Ce qu'on cherche pour chaque niche

| Sujet | Questions | Sources qui ont marché (France) |
|---|---|---|
| **Taille du marché** | Combien d'établissements, combien au-dessus du seuil de chiffre d'affaires, combien décident seuls | API Recherche d'entreprises (codes NAF, tranches d'effectif), localisateurs de magasins des enseignes, annuaires professionnels |
| **Argent du métier** | Chiffre d'affaires médian, marge brute, résultat net, part en perte | Comptes déposés (jeu `ratios_inpi_bce` sur data.economie.gouv.fr), brochures de franchise, Insee |
| **Panier moyen** | Ce que rapporte une vente, par gamme | Enseignes, presse professionnelle, déclarations de gérants (datées) |
| **Cycle de vente** | Délai du premier contact à la signature, acompte, délai de paiement | Pages de vendeurs, fédérations, études sectorielles |
| **Saisonnalité** | Temps forts, creux, quand le gérant décide | Google Trends, notes de conjoncture des fédérations |
| **Capacité à payer en cash** | Quand l'argent rentre chez lui, ce qu'il paie déjà (redevance de réseau, contacts achetés, plateformes) | Brochures de franchise, tarifs publics des vendeurs de contacts |
| **Qui vend, qui décroche** | Vendeur salarié ou gérant, combien de rendez-vous par semaine, qui rappelle | Brochures d'enseignes, offres d'emploi, vidéos de gérants |
| **Réglementation** | Ce qui encadre sa publicité, le rappel téléphonique, la rémunération d'un intermédiaire, les catégories spéciales de Meta | Legifrance, CNIL, DGCCRF, ordres et autorités du métier, règles publicitaires de Meta |
| **Vocabulaire** | Les mots qu'il emploie, ceux qu'il n'emploie jamais | Interviews, forums, presse pro, publicités qu'il diffuse lui-même |
| **Douleurs et objections** | Ce qui l'inquiète, ce qu'il a déjà essayé et ce qu'il en retient | Citations datées, avis, témoignages publiés par les concurrents |
| **Concurrents** | Qui lui vend des contacts ou des rendez-vous : promesse exacte, prix, garantie, preuve | Sites, conditions générales publiées, Bibliothèque publicitaire |

**Réglementation : ce qu'il faut toujours relever.** Rappel téléphonique d'un particulier (consentement préalable, mentions, plages horaires, nombre d'appels) ; obligation de dire qu'un agent IA est une IA ; appels sortants par agent vocal ; messages WhatsApp et SMS (consentement distinct) ; catégorie spéciale Meta ; mentions obligatoires de la publicité du métier ; **règle qui interdirait de rémunérer l'agence au résultat** (voir `offre.md`) ; avis clients (pas de sollicitation sélective). Marque `[avocat]` ce qui doit être validé avant le premier client.

## 3. La Bibliothèque publicitaire

Relève les annonces actives par mots-clés (acteur Apify `facebook-ads-scraper`, jeton dans `APIFY_TOKEN`). Les requêtes de chaque niche viennent de `projet.json` → `niches[].ads_library`.

```bash
python3 scripts/recherche/adlib.py <projet> [niche ...] --dry-run          # les requêtes, ce qui est déjà en cache, sans jeton
python3 scripts/recherche/adlib.py <projet> [niche ...] [--limite 25]      # cache : _commun/ads-library/<clé>/<requête>.json
python3 -I scripts/recherche/digest.py <projet>/_commun/ads-library > <projet>/_commun/ads-library/resume.txt
python3 -I scripts/recherche/planche_concurrents.py <projet>/_commun/ads-library <dossier> "<Page 1>" ["<Page 2>" …]   # planche des visuels
```

Une relance réutilise les requêtes déjà en cache. Le résumé est la source de la section 6 d'`analyse.md` : donne-le à l'agent de chaque niche.

**Écrire les requêtes.**
- **Courtes : 2 à 4 mots.** Les requêtes longues renvoient 0 annonce, ou du bruit. La promesse exacte d'un concurrent recopiée mot pour mot a ramené de l'immobilier et des formations, aucun vendeur du métier.
- **La forme « vous êtes <métier> »** trouve les annonceurs qui s'adressent au professionnel (agences, fabricants, salons) : c'est la meilleure requête pour voir les concurrents.
- Ajoute 3 à 6 requêtes : `<métier> rendez-vous`, `<métier> clients`, `<métier> nous recherchons`, `<objet du métier> <ville ou zone>`. Le pluriel et le singulier ne ramènent pas la même chose.
- Une recherche à part, pour la concurrence directe de l'agence : `<cible> vous ne payez que`, `rendez-vous qualifiés <cible>`.

**Lire le relevé.** Le résumé donne une ligne par Page avec la durée de son annonce active la plus ancienne. Sépare :
- les annonces **adressées au métier** : ce sont les concurrents de l'agence (promesse, chiffre, garantie, format, durée) ;
- les annonces **du métier lui-même** : ce que ses clients voient déjà, les registres (prix, remise, sur-mesure), ce qui tient longtemps.

Une annonce active depuis plus de 90 jours est un signal que le format paie. Le relevé est partiel par construction : une Page absente n'est pas une Page arrêtée. Note aussi les visuels qui durent (photo du professionnel avec une étiquette de cible, carte claire avec un titre, gros chiffre) : ils nourrissent `creatives.md`.

## 4. Le format d'`analyse.md`

En tête : la date, les sources de base, puis la légende des niveaux.

1. **L'essentiel** : 5 à 7 puces. Ce qui fait tenir la niche (ou non), la promesse déjà prise par le marché, ce qui a bougé, la place libre.
2. **Marché et taille** : tableau des couches (établissements → au-dessus du seuil → solvables → adressables), chaque ligne avec nombre, niveau et source. Puis « L'argent du métier » (tableau), la conjoncture, « Qui vend, qui décroche, quand » (vendeur, visites, taux de signature, coût d'une demande, absences, saison) et la conséquence pour le calendrier.
3. **L'avatar** : qui décide (chiffres), son quotidien, ce qui l'inquiète (citations datées), ce qu'il a déjà essayé (tableau canal, ce qu'il en retient, prix, niveau), ses mots et les mots à ne pas employer, la limite de ce qui a été lu.
4. **Niveau de conscience** : tableau des cinq stades (ne voit pas le problème → prêt à acheter) avec une part estimée et ce qu'il se dit, puis ce que cela impose à une publicité de bas de funnel.
5. **Concurrents** : tableau `Acteur (lien) | Promesse exacte | Prix | Garantie ou recours | Preuve dans le métier | Changement récent`, puis ce que le tableau dit (façons de garantir, prix repères, qui rappelle le contact).
6. **Ce que montre la Bibliothèque publicitaire** : nombre d'annonces et de Pages, vendeurs visibles, annonces du métier, signaux utiles pour l'offre.
7. **Réglementation** : dans la publicité de l'agence adressée au métier ; dans ce que l'agence installe chez le client ; ce que les agents IA ajoutent ; tableau « Formulation risquée | Pourquoi | Formulation sûre ».
8. **Objections et réponses** : tableau, réponses vraies et vérifiables.
9. **Ce que disait l'étude précédente, et ce qui tient** (si elle existe).
10. **Ce qui reste inconnu** : la liste honnête de ce qui décidera de l'offre et n'est pas mesuré.

Longueur visée : environ 250 lignes denses. `examples/agence-exemple/1-salles-de-sport/resume.json` montre ce qui en sort.

## 5. Ce que l'étude doit livrer à l'offre

À la fin d'`analyse.md`, l'agent doit pouvoir répondre en chiffres sourcés :
- le **volume que le marché promet déjà** sur la même unité (pour la règle du volume, voir `offre.md`) ;
- le **coût probable d'une unité** (rendez-vous tenu, visite, essai) : coût d'une demande ÷ (part qui prend rendez-vous × part qui vient), en fourchette ;
- la **marge par vente** et le **taux de signature prudent** ;
- les **trois sous-niches** qui trient le mieux la question « Vous êtes ? » (celle visée, celle d'à côté, celle à écarter) ;
- les **règles qui bornent l'offre** (rémunération au résultat interdite, catégorie spéciale, mots interdits).
