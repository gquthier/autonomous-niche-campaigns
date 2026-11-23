---
name: autonomous-niche-campaigns
description: Machine d'acquisition par niche de métier pour une agence de génération de prospects, de A à Z. Pour chaque niche, étude du marché et des concurrents (Bibliothèque publicitaire Meta), offre « Plein 90 » (prix unique payé au départ, garantie au prorata, bonus 100 % numériques), présentation commerciale de 15 pages façon Hormozi, 10 créatives statiques bas de funnel GPT Image (lumineuses, offre au centre, cible nommée) + 2 variantes « Payé à la performance ». Puis un formulaire instantané Meta qui qualifie sur le chiffre d'affaires par logique conditionnelle (sous le seuil, même page de fin mais aucun prospect compté), une campagne ABO à un ad set par niche déployée par l'API, tout en pause, et une séquence de 6 e-mails de relance par niche. Après une semaine, le passage à une CBO par niche, avec trois ad sets pour trois angles construits sur les annonces gagnantes de l'ABO, 4 à 8 statiques en 4:5 et 9:16, la copy de chaque annonce, des scripts vidéo de 30, 60 et 90 s et des formulaires refaits. Rien n'est dit « fait » sans une preuve relue dans le compte. Utilise ce skill dès qu'on parle de lancer des campagnes Meta ou Facebook Ads sur plusieurs niches, de formulaire instantané qualifiant, d'instant form, de « logique conditionnelle », de qualifier les prospects sur le chiffre d'affaires, de créatives bas de funnel, d'offre par niche, de « déployer les campagnes avec mon token Meta », d'ajouter une niche ou des ad sets à une campagne qui tourne, de passer de l'ABO à la CBO, de nouveaux angles par niche, de vérifier que tout est bien dans le gestionnaire de pubs, même si la personne n'en demande qu'un morceau (seulement les créatives, seulement le formulaire, seulement les e-mails). Pour des pubs vidéo ou pour basculer une campagne existante vers un formulaire, utilise plutôt autonomous-meta-launch.
---

# Campagnes par niche : de l'étude à la campagne Meta qui tourne

Ce skill reproduit un système qui a tourné sur un vrai compte publicitaire en novembre 2026 : plusieurs niches de métier, une campagne ABO, plus d'une centaine de publicités, un formulaire qualifiant par niche, des alertes de prospects et des relances e-mail. Le niveau à atteindre, c'est celui de ces livrables. L'exemple fictif complet (une agence, deux niches : salles de sport et paysagistes) est dans `examples/agence-exemple/`.

Il complète [autonomous-meta-launch](https://github.com/gquthier/autonomous-meta-launch), qui couvre les pubs vidéo, la conversion sur page merci, la reprise d'un import long, la création du jeton Meta avec un agent qui pilote l'écran, et le passage d'une campagne existante vers un formulaire instantané. Ne le duplique pas : renvoie la personne vers lui pour ces sujets.

## Règles non négociables

1. **Les clés restent dans des variables d'environnement** (`META_ACCESS_TOKEN`, `KIE_API_KEY`, `APIFY_TOKEN`). Ne les affiche pas, ne les écris dans aucun fichier, ne les demande pas dans le chat. Si la personne te colle un jeton, dis-lui de le révoquer et d'en générer un autre.
2. **Tout est créé en pause.** Seule `activer --oui` lance la diffusion, sur l'accord explicite de la personne, pour cette campagne et ce budget.
3. **Simulation d'abord.** `meta_campagne.py <projet> parcours --dry-run` sur la configuration réelle, avant le premier appel réel.
4. **Aucun chiffre inventé** : prix, seuil, volume, cas client, prix « ailleurs ». Tout vient de `projet.json → offre`, de `resume.json` ou d'une source écrite dans `analyse.md`.
5. **`_meta/etat.json` est privé** : il contient des identifiants de compte. Le dossier de travail ne se versionne pas dans un dépôt public.
6. **Si un contrôle s'arrête, corrige la cause.** Ne contourne pas un `ARRÊT` ni une erreur de `spec_check.py` ou de `verifier.py`.
7. **« Prêt en local » n'est pas « dans le compte ».** Après chaque création dans Meta, relis l'état réel par l'API. Ne dis « c'est fait » qu'avec la preuve écrite par le contrôle : `controle` pour l'ABO, `cbo.py lire` puis `verifier` (`_meta/push-verified.json`) pour la CBO.

## Ce qu'il faut avant de commencer

1. **Le projet** : copie `assets/projet.exemple.json` en `<dossier de travail>/projet.json` et remplis-le avec la personne (voir `references/config.md`) :
   - l'agence, la règle d'offre commune (prix, durée, garantie, phrase des variantes) et les niches ;
   - le compte publicitaire, la page, le compte Instagram (ou les variables `META_AD_ACCOUNT`, `META_PAGE_ID`, `META_INSTAGRAM_ID`) ;
   - le lien du calendrier et le lien de confidentialité ;
   - le budget par niche, les pays et le navigateur.
2. **Les clés**, exportées dans le terminal (voir `.env.example`) : jeton Meta d'utilisateur système, clé kie.ai (images), jeton Apify (concurrents, facultatif).
3. **Le contrôle** : `python3 scripts/meta_campagne.py <projet> verifier`. Ne va pas plus loin tant que le jeton, le compte et la page ne sont pas bons.

Ne pose à la personne que les questions qui lui reviennent : le prix et la garantie, les niches, le budget, les liens de calendrier et de confidentialité, l'activation, l'ouverture des e-mails. Le reste, décide-le et dis-le.

## Le parcours (dans cet ordre)

| # | Étape | Lire | Produit | Outils |
|---|---|---|---|---|
| 1 | Concurrents de chaque niche | `references/etude-niche.md` | `_commun/ads-library/` | `scripts/recherche/adlib.py`, `digest.py`, `planche_concurrents.py` |
| 2 | Étude de chaque niche | `references/etude-niche.md` | `<niche>/analyse.md` | agents |
| 3 | Offre de chaque niche | `references/offre.md` | `offre.md`, `publicite.md`, `resume.json` | agents, `meta_campagne.py verifier --dry-run` |
| 4 | Présentation de 15 pages | `references/presentation.md` | `presentation/presentation.html` + `.pdf` | agents |
| 5 | Créatives | `references/creatives.md` | `creatives/spec.json`, `creatives/final/*.jpg` | `scripts/creatives/build_spec.py`, `spec_check.py`, `gen.py`, `check.py`, `apercu.py`, `finish.py`, `variantes.py` |
| 6 | Textes des publicités | `references/campagne.md` | validation par la personne | `meta_campagne.py textes` |
| 7 | Campagne, ad sets, formulaires | `references/campagne.md`, `references/formulaire.md` | tout **en pause** | `meta_campagne.py regles`, `campagne`, `adsets`, `formulaires`, `logique`, `trouver`, `images`, `pubs`, `controle` |
| 8 | Séquence e-mail | `references/sequence-email.md` | `sequences-email/sequence-formulaire.json` + `.md` | agents, `scripts/sequences/verifier.py` |
| 9 | Lancement | `references/campagne.md` (« Activer ») | campagne active | `meta_campagne.py activer --oui`, seulement sur accord explicite |
| 10 | Passage en CBO, après une semaine | `references/cbo.md` | `cbo/annonces.csv`, statiques 4:5 + 9:16, scripts vidéo, formulaires v2, `_meta/push-verified.json` | `cbo.py gagnants`, `grille`, `apercu`, `lire`, `verifier` ; `meta_campagne.py formulaires --nouvelle-version`, `logique` |

Lis `references/pieges.md` une fois avant l'étape 5, et sa section « Passage en CBO » avant l'étape 10 : il évite les erreurs déjà payées une fois.

### La simulation

```bash
python3 scripts/meta_campagne.py <projet> parcours --dry-run   # verifier → controle, sans clé ni réseau
python3 scripts/creatives/gen.py <projet> <niche> --dry-run     # images à générer et coût en crédits
python3 scripts/recherche/adlib.py <projet> --dry-run           # requêtes de la Bibliothèque publicitaire
```

La simulation écrit dans `_meta/etat.dry-run.json` et `_meta/monde.dry-run.json`, jamais dans l'état réel. Elle valide l'enchaînement, les textes, la logique du formulaire et le décompte des publicités ; elle ne dit pas si Meta refusera un texte à l'examen.

### Organiser le travail

- **Un agent par niche** pour les étapes 2 à 4, lancés en parallèle en arrière-plan. Chaque agent reçoit :
  - le chemin du projet et sa niche ;
  - le fichier de référence de l'étape, et rien d'autre à deviner ;
  - la règle d'offre de `projet.json`.
  Les présentations se font avec le modèle le plus fort disponible. Les agents écrivent dans le dossier de leur niche et rendent un rapport court.
- Si un agent s'arrête sur une limite d'usage, reprends-le avec son contexte au lieu d'en relancer un nouveau.
- **Les créatives** : un agent par niche part de `build_spec.py` (premier jet de dix formats), adapte chaque consigne au métier et passe `spec_check.py` à 0 erreur. Toi, tu lances `gen.py` puis `check.py`, tu regardes chaque image (`apercu.py`), tu choisis dans `work/sel.json`, puis tu lances `finish.py`. Les deux variantes passent par `variantes.py gen|check|finish`.
- **Meta** : toi, par les scripts, niche par niche, en relisant chaque sortie. L'éditeur de formulaires pilote le navigateur de la personne : préviens-la avant de commencer (environ 4 minutes par niche) et demande-lui de ne pas cliquer dans cet onglet pendant ce temps.

### Ce que la personne doit voir avant chaque étape irréversible

- **Avant de générer les créatives** : le coût en crédits (`gen.py --dry-run`), soit le nombre d'images × 18 environ. `gen.py` refuse de descendre sous la réserve.
- **Avant `pubs`** : les textes de chaque niche (`textes`), la logique de chaque formulaire (`regles`) et la planche des créatives (`final/_planche.jpg`).
- **Avant `activer --oui`** :
  - le nombre d'ad sets et le budget total par jour ;
  - les phrases de garantie affichées ;
  - ce qui n'est pas encore branché : réception des prospects, calendrier reconnu par l'outil de l'équipe, e-mails.

  Son accord vaut pour cette campagne et ce budget, pas pour un lot ajouté plus tard.
- **Avant d'ouvrir les e-mails** : la relecture des 6 e-mails de chaque niche (`sequences.md`).
- **Avant de publier les formulaires de la CBO** : ce que deviennent ceux qui sont sous le seuil (`cbo.non_qualifies` : aucune trace, réservation marquée ou liste comptée par Meta), et la liste des anciennes annonces encore actives.

## La barre de qualité (ce qui a été validé, ce qui a été refusé)

- **Offre** :
  - promesse chiffrée dans l'unité du métier, sur 90 jours (« 40 essais encadrés tenus dans votre club en 90 jours ») ;
  - volume un peu au-dessus de ce que promet déjà le marché ;
  - prix unique payé au départ, garantie remboursée au prorata ou quelques semaines de plus sans frais ;
  - jamais de commission sur le résultat (risque réglementaire) ;
  - bonus 100 % numériques, faisables par des agents IA, coût limité aux clés d'API, une diapositive chacun.
- **Créatives** :
  - lumineuses et simples ;
  - la cible nommée en haut, l'offre au centre, la garantie visible ;
  - un seul point focal, une idée par image ;
  - dix formats différents par niche ;
  - aucun mot inventé (contrôle OCR), le logo posé par programme.

  Refusé : direction sombre et chargée.
- **Formulaire** :
  - « Vous êtes ? » avec trois profils + Autre, puis le chiffre d'affaires en tranches ;
  - sous le seuil, la même page de fin avec le bouton de réservation, mais aucun prospect pour Meta ;
  - deux questions seulement, pour que ce soit rapide.
- **Campagne** : une ABO, un ad set par niche, ciblage large, Facebook + Instagram, aucune amélioration automatique sur les créatives. Tout est créé en pause.
- **CBO** (après une semaine) :
  - une campagne par niche, budget de campagne, un ad set par angle (trois au moins) ;
  - chaque angle part d'une famille visuelle gagnante et teste un argument bas de funnel ;
  - 4 à 8 statiques par angle, chacune en 4:5 et 9:16 ;
  - la même promesse mot pour mot dans l'annonce et le formulaire ;
  - tout en pause, et un `push-verified.json` avant de dire que c'est dans le compte.
- **E-mails** : courts, humains, un seul lien, aucun chiffre inventé, aucun prix, aucune fausse urgence. Ils s'arrêtent dès que la personne réserve ou répond.
- **Partout** : jamais de prix, de seuil, de chiffre ou de cas client inventé. Les phrases de garantie restent à faire valider par un avocat : signale-le à chaque livraison.

## Reprendre ou ajouter

- Chaque script note ce qu'il crée dans `<projet>/_meta/etat.json` : relancer une étape ne recrée rien et reprend là où elle s'est arrêtée.
- **Ajouter des niches à une campagne qui tourne** : ajoute-les dans `projet.json`, puis passe les étapes 1 à 8 pour ces seules niches (`… <étape> <clé>`) et demande l'accord avant `activer --oui <clé>`.
- **Changer le prix ou la garantie** :
  1. modifie `projet.json → offre` ;
  2. reporte le changement dans chaque `resume.json`, présentation et e-mail ;
  3. régénère les images qui portent l'ancienne phrase (`variantes.py` sait remplacer une phrase dans une image existante) ;
  4. relance `images` puis `pubs`, qui mettent à jour les publicités existantes.
- **Formulaire à refaire** :
  1. la nouvelle intro dans `resume.json → formulaire_intro` ;
  2. un nouveau nom dans `formulaire.nom` (par exemple « IF - {label} v2 ») ;
  3. `formulaires <niche> --nouvelle-version`, puis `logique`, puis `pubs` (en ABO) ;
  4. le test de chaque tranche en aperçu.

  Liste les publicités qui utilisent l'ancien formulaire (`usage`) avant d'archiver quoi que ce soit.
- **Passer en CBO** : `references/cbo.md`, de la lecture des gagnants à la preuve `push-verified`.

## Rendre compte

À la fin, en quelques lignes :
- ce qui est en ligne (campagne, budget par jour, nombre de publicités relu par statut), d'après `controle` ou `_meta/push-verified.json` du jour, jamais de mémoire ;
- les anciennes publicités encore actives, avec leur formulaire ;
- ce qui est prêt mais fermé ;
- les choix faits sans la personne (profils de « Vous êtes ? », formats d'images retenus) ;
- les points à trancher (avocat, calendrier, ouverture des e-mails) ;
- les chemins des livrables.

Pas de rapport long.
