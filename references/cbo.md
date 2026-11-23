# Passer de l'ABO à la CBO : trois angles par niche

Le lancement se fait en ABO, un ad set par niche (`campagne.md`) : chaque niche reçoit le même budget et se lit à part. Après une semaine, la question change. On ne cherche plus quelle niche répond, on cherche **quel argument fait répondre dans chaque niche**. Ce fichier décrit l'étape suivante telle qu'elle a tourné sur un vrai compte en novembre 2026 :

- une campagne CBO par niche ;
- trois ad sets par campagne, un par angle bas de funnel ;
- 4 à 8 statiques par angle, chacune en 4:5 et en 9:16 ;
- la copy complète de chaque annonce ;
- un script vidéo face caméra par angle ;
- des formulaires refaits ;
- tout créé en pause.

Le plus cher ce jour-là n'a pas été de créer les annonces. Ça a été de **prouver qu'elles étaient dans le compte**. Lis la dernière section et `pieges.md` (« Passage en CBO ») avant de commencer.

Exemple fictif complet : `examples/agence-exemple/*/cbo/angles.json`, `examples/agence-exemple/cbo/`.

## 1. Quand passer

- **Après la lecture des résultats par annonce**, pas par ad set : au moins 7 jours d'ABO, et des prospects dans chaque niche. Une niche sans prospect ne passe pas en CBO : son offre ou sa cible est à revoir.
- **Exporte les résultats au niveau Publicité** dans le gestionnaire de publicités, sur toute la période de l'ABO. Les colonnes utiles sont le nom de l'ensemble de publicités, le nom de la publicité, le montant dépensé et les résultats. Range l'export dans `cbo/resultats-abo.csv`, puis lance :

  ```bash
  python3 scripts/cbo.py <projet> gagnants
  ```

  Pour chaque ad set, le script donne les prospects, la dépense et le coût par prospect. Il classe les annonces, marque les gagnantes (au moins 3 prospects et 20 % de la niche) et rattache chaque annonce à son format de `creatives/spec.json`.
- **Lis-le avec prudence.** Une semaine d'ABO donne souvent peu de prospects par niche, et une seule image en porte parfois plus de la moitié. C'est une indication, pas une preuve. Garde la **famille visuelle** gagnante (la photo du métier, la carte typographique, l'objet porteur du texte), pas l'image exacte. Ces chiffres comptent des formulaires envoyés, pas des rendez-vous tenus : croise-les avec l'outil de l'équipe avant de couper un angle.

## 2. Choisir trois angles à partir des gagnants

Un angle est **un argument**, pas un visuel. Chaque angle reprend une famille visuelle gagnante de l'ABO et teste un argument nouveau, toujours bas de funnel, toujours avec la même offre.

La grille qui a servi, d'une niche à l'autre :

| Angle | Ce qu'il dit | Exemple fictif (salles de sport) |
|---|---|---|
| 1. Le critère vérifié avant le rendez-vous | Ce que l'agence vérifie pour lui avant qu'il se déplace ou reçoive | « Il a déjà choisi son créneau d'essai » |
| 2. Le moment où l'agence prend le relais | Le moment de sa journée où il ne peut pas répondre | « Les heures creuses remplies » |
| 3. L'offre et sa garantie écrites | Pour celui qui compare deux prestataires : le volume, le délai, le recours | « 40 demandes d'essai préqualifiées, garanties ou remboursées » |

Pour chaque angle, écris dans `<niche>/cbo/angles.json` :
- une hypothèse en une phrase (« le gérant pense en créneaux à remplir, pas en contacts ») ;
- l'annonce de l'ABO dont il part (`gagnant_de_depart`) ;
- le texte principal ;
- les statiques, avec leur format, leur accroche et leur titre.

```json
{
 "code": "F",
 "promesse": "40 demandes d'essai préqualifiées en 90 jours",
 "expressions_interdites": ["essais tenus", "essais encadrés tenus"],
 "angles": [
  {"cle": "F1", "titre": "Le nouveau venu attendu à l'accueil", "gagnant_de_depart": "N103-photo-metier",
   "hypothese": "…", "texte_principal": "…", "texte_court": "…", "texte_long": "…", "description": "Mise en place en 5 jours",
   "statiques": [{"format": "Photo du métier avec carte d'offre", "accroche": "Il a déjà choisi son créneau d'essai.", "titre": "40 demandes d'essai en 90 jours"}, "…"]}
 ]
}
```

- `promesse` : la phrase que **l'annonce et le formulaire disent à l'identique**.
- `expressions_interdites` : les anciennes formulations, refusées partout (copy et formulaire).
- Une statique peut remplacer le texte de l'angle (`texte`, `texte_court`, `texte_long`, `description`, `bouton`).

**Si l'offre change entre l'ABO et la CBO**, c'est une décision du dirigeant. Cas réel : la garantie est passée des rendez-vous tenus aux **demandes préqualifiées**. L'agence maîtrise la demande, pas la venue, et la prise de rendez-vous reste dans le service. Reporte ce changement dans `offre.md`, `resume.json`, la présentation et les e-mails (« Changer le prix ou la garantie » dans `SKILL.md`). Mets aussi l'ancienne formulation dans `expressions_interdites`.

## 3. La structure

| Niveau | Règle |
|---|---|
| **Campagne** | Une par niche (`cbo.campagne_nom`, « Instant Form - CBO \| {label} »). Le budget est porté par la campagne (`cbo.budget_jour_par_campagne`), avec une enchère au plus bas coût et l'objectif prospects. Créée en pause. |
| **Ad set** | Un par angle, trois au minimum (`cbo.angles_min`), sans budget propre. Mêmes réglages que l'ad set ABO de la niche : ciblage large, `QUALITY_LEAD`, `ON_AD`, Page, attribution et champs DSA. Créé en pause. |
| **Annonce** | De 4 à 8 par ad set (`statiques_min`, `statiques_max`). Une statique donne une annonce à deux visuels : le 4:5 (1080 × 1350) pour le fil, le 9:16 (1080 × 1920) pour les stories et les reels. L'annonce pointe vers le formulaire CBO de la niche. Créée en pause. |
| **Formulaire** | Un par niche, en nouvelle version (`cbo.formulaire_nom`, « IF - {label} - CBO »), avec la même promesse que les annonces et la logique sur le chiffre d'affaires (section 6). |

```bash
python3 scripts/cbo.py <projet> grille              # la grille et la copy → cbo/annonces.csv
python3 scripts/cbo.py <projet> grille --fichiers   # + chaque visuel présent, à la bonne taille (Pillow)
```

`grille` s'arrête dans quatre cas :
- moins de trois angles ;
- un angle hors de 4 à 8 statiques ;
- une copy incomplète, une ancienne promesse ou un mot sans accent ;
- un `resume.json → formulaire_intro` qui ne dit pas la promesse.

**Ajouter à une CBO qui tourne déjà**, c'est possible. Sur le vrai compte, deux niches avaient déjà leur CBO active. Les nouveaux ad sets en pause ne dépensent rien, mais la campagne active continue de diffuser ce qu'elle contient déjà. `verifier` le signale.

## 4. Les visuels

- Même direction que `creatives.md` : lumineux, la cible nommée, l'offre au centre, un seul point focal. Par angle, quatre directions artistiques, une par statique, et une seule offre.
- Le 9:16 n'est pas un recadrage du 4:5. On recompose la même idée sur le même fond, en gardant le texte loin du haut et du bas de l'image (l'interface des stories et des reels les couvre).
- Nommage : `<dossier de niche>/cbo/statiques/F1-S01-4x5.jpg` et `F1-S01-9x16.jpg`. Sur le vrai compte : 3 niches × 3 angles × 4 statiques = 36 annonces, donc 72 fichiers.
- Fais une planche par niche et par format pour la relecture, et regarde chaque image (règles de `creatives.md` : aucun mot inventé, aucun chiffre inventé).

## 5. La copy, annonce par annonce

`cbo/annonces.csv` contient une ligne par annonce : niche, campagne, formulaire, angle, ad set, annonce, format, les deux fichiers, l'accroche de l'image, les textes court, principal et long, le titre, la description et le bouton. C'est le fichier que la personne relit, et celui d'où partent les annonces. `verifier` compare ensuite le texte et le titre lus dans Meta à ce fichier.

Règles : la même promesse partout, aucune expression interdite, les accents contrôlés, aucun chiffre inventé. Un budget « pour l'exemple » dans une accroche est un chiffre inventé.

## 6. Les formulaires de la vague CBO

1. Écris la promesse dans `resume.json → formulaire_intro` (`titre`, `texte`). Sans ça, le nouveau formulaire reprend la carte d'intro des publicités de l'ABO, donc l'ancienne promesse.
2. Change `formulaire.nom` en « IF - {label} - CBO » (ou la valeur de `cbo.formulaire_nom`).
3. Lance `python3 scripts/meta_campagne.py <projet> formulaires <niche> --nouvelle-version`. L'ancienne version reste notée dans l'état et reste en ligne : des annonces l'utilisent encore. Puis lance `logique <niche>` et `trouver --ecrire` (voir `formulaire.md`).
4. **Contrôle bloquant en aperçu.** `python3 scripts/cbo.py <projet> apercu` liste les parcours à tester et crée `_meta/apercu-formulaires.json`. Dans l'aperçu de Meta :
   - choisis chaque tranche de chiffre d'affaires et note où elle mène (`prospect`, `non_prospect_avec_reservation`, `non_prospect_sans_reservation`) ;
   - relis chaque écran mot à mot ;
   - clique sur le lien de confidentialité.

   Puis remplis le relevé avec l'identifiant du formulaire. `verifier` refuse un formulaire sans relevé, un relevé fait sur une autre version, et une tranche qui ne mène pas où elle doit. L'API ne lit pas la logique conditionnelle : seul l'aperçu la prouve.
5. **Décide avant de publier ce que deviennent les non-qualifiés** (`cbo.non_qualifies`). Meta n'offre que deux sorties : le formulaire envoie les coordonnées (un prospect compté) ou il ne les envoie pas.

| Choix | Sous le seuil | Ce qui reste |
|---|---|---|
| `sans_trace` | Le formulaire se ferme avant les coordonnées, avec un simple merci | Rien. Ni Meta, ni l'équipe ne sait qui c'était. |
| `reservation_marquee` | Le formulaire se ferme avant les coordonnées. La page de fin propose la réservation, avec un lien marqué non qualifié. | Seulement ceux qui réservent (le choix par défaut du skill, voir `formulaire.md`). |
| `liste` | Les coordonnées sont envoyées et l'outil de l'équipe les range en « non qualifiés » | Une vraie liste, mais Meta les compte comme prospects et apprend à en chercher d'autres. |

`verifier` refuse de valider tant que ce choix n'est pas écrit.

Ne relance pas `meta_campagne.py pubs` sur l'ABO après une nouvelle version : il rebrancherait les annonces de l'ABO, qui portent l'ancienne promesse, sur le nouveau formulaire.

## 7. Créer dans Meta, tout en pause

L'ordre est le suivant : campagnes, ad sets, images, créatives, annonces. Note chaque identifiant dès que Meta le renvoie, dans un fichier d'état sous `_meta/`, pour qu'une relance ne recrée rien. Les champs qui ont marché :

- **Campagne** : `POST act_<compte>/campaigns` avec `name`, `objective=OUTCOME_LEADS`, `buying_type=AUCTION`, `special_ad_categories=[]`, `daily_budget` (en centimes), `bid_strategy=LOWEST_COST_WITHOUT_CAP` et `status=PAUSED`.
- **Ad set** : `POST act_<compte>/adsets`. Recopie de l'ad set ABO de la niche `targeting`, `optimization_goal`, `billing_event`, `destination_type`, `promoted_object`, `attribution_spec` et les champs DSA. Ajoute `name`, `campaign_id` et `status=PAUSED`, **sans `daily_budget`**.
- **Images** : `POST act_<compte>/adimages`, les deux formats, qui renvoient chacun un `hash`.
- **Créative à deux formats** : `POST act_<compte>/adcreatives` avec :
  - `object_story_spec` : `page_id` et le compte Instagram ;
  - `asset_feed_spec` :
    - `images` : les deux hashes, chacun avec un `adlabels` (`i4x5`, `i9x16`) ;
    - `asset_customization_rules` : le 4:5 sur le fil, le 9:16 sur les stories et les reels ;
    - les textes : `bodies`, `titles`, `descriptions`, `link_urls` ;
    - `ad_formats=["SINGLE_IMAGE"]`, `optimization_type=PLACEMENT`, `call_to_action_types=["LEARN_MORE"]` ;
    - `call_to_actions` : `[{"type": "LEARN_MORE", "value": {"lead_gen_form_id": <formulaire>}}]`.

  Les règles de placement sont pointilleuses. Recopie-les depuis une annonce faite dans le gestionnaire avec « personnaliser par placement » : lis sa créative et retire `image_label.id`.
- **Annonce** : `POST act_<compte>/ads` avec `name` (« F1-S01 | <accroche> », la clé en tête sert à la vérification), `adset_id`, `creative` et `status=PAUSED`.
- Juste après l'import, les statuts effectifs `PAUSED`, `PENDING_REVIEW` (en examen) ou `IN_PROCESS` sont normaux. Après beaucoup d'écritures, Meta limite aussi les **lectures de listes** : relis les annonces par identifiant (`GET /?ids=…`, par petits lots), et ne conclus jamais d'une liste vide.

## 8. La preuve avant le « fait »

```bash
python3 scripts/cbo.py <projet> lire        # lecture seule : campagnes, ad sets, annonces, images, formulaires, autres annonces actives
python3 scripts/cbo.py <projet> verifier    # écrit _meta/push-verified.json seulement si tout passe
```

Lance-les **après chaque lot de créations**, pas seulement à la fin. L'écart restant doit être exactement ce qui n'est pas encore créé. `verifier` contrôle :
- **les campagnes** : chacune présente, une seule par nom, avec un budget de campagne (sinon ce n'est pas une CBO) ;
- **les ad sets** : chaque angle a le sien, en pause et sans budget propre ;
- **les annonces** :
  - chacune dans le bon ad set, en pause, ni refusée ni en erreur ;
  - sur le formulaire CBO de sa niche ;
  - avec ses deux formats, le 9:16 affecté aux stories et aux reels ;
  - avec le texte et le titre de `annonces.csv` ;
- **les formulaires** :
  - un seul actif par nom, avec l'intro qui dit la promesse et aucune expression interdite ;
  - aucun mot sans accent, et les tranches de la configuration ;
  - un lien de confidentialité qui n'ouvre pas l'accueil du site ;
  - un relevé d'aperçu complet et conforme ;
- **la décision** sur les non-qualifiés ;
- **un état lu il y a moins d'une heure** (`cbo.fraicheur_minutes`).

Il liste aussi, sans bloquer, les **annonces actives hors de la nouvelle structure** et le formulaire qu'elles utilisent. Montre-les à la personne : les couper, les garder ou les rebrancher est sa décision. Un échec efface le `push-verified.json` précédent.

**« Prêt en local » et « dans le gestionnaire de pubs » sont deux états différents.** Dis toujours lequel. Ne dis « c'est dans le compte » qu'avec un `push-verified.json` du jour, et cite son contenu : campagnes, ad sets, nombre d'annonces et leurs statuts effectifs relus.

## 9. Les scripts vidéo face caméra

Écris un script par angle, en trois durées, pour l'équipe qui tourne. Mêmes règles que la copy : même promesse, bas de funnel, aucun chiffre inventé.

| Durée | Structure |
|---|---|
| 30 s | Accroche (la question du métier, 3 secondes) → ce que l'agence fait pour lui → appel à remplir le formulaire |
| 60 s | Accroche → le problème dans ses mots → le mécanisme → la garantie → appel |
| 90 s | Accroche → le problème → le mécanisme pas à pas → ce que la demande contient → la garantie et ses conditions → appel |

Pour chaque script : le texte à dire, les plans à tourner (face caméra, plan de coupe du métier, écran du formulaire) et l'appel à l'action vers le formulaire, jamais vers un site.

Exemple fictif, angle F1, 30 secondes :

> Un nouveau venu qui a déjà choisi son créneau d'essai, ça change votre soirée ? Si vous dirigez une salle de sport, on trouve ces personnes dans votre quartier. On vérifie qu'elles habitent la zone et qu'elles sont disponibles, puis on leur propose vos créneaux. Remplissez le formulaire pour demander l'étude de votre club.

Pour partager les scripts, un document ou un mini-site statique suffit, avec une ancre par angle et par durée (`#F1-30`). **Demande avant de publier en ligne.** Sur le vrai compte, le site était public et sans connexion. Un tel lien circule plus loin que l'équipe. Il ne contient donc ni identifiant, ni lien du gestionnaire de pubs, ni prix non validé.

## 10. Activer

Même règle que `campagne.md` : l'accord explicite de la personne, pour ces campagnes et ce budget. Avant de le demander, il faut :
- un `push-verified.json` du jour ;
- une décision sur les anciennes annonces actives ;
- le statut du compte publicitaire et de sa facturation, lu par l'API (`account_status`, `disable_reason`) ;
- un prospect de test reçu dans l'outil de l'équipe ;
- **chaque compte publicitaire concerné vérifié** : demande la liste au départ, un deuxième compte oublié n'est jamais contrôlé.

## Simulation, sans clé

```bash
E=examples/agence-exemple
python3 scripts/cbo.py $E gagnants
python3 scripts/cbo.py $E grille
python3 scripts/cbo.py $E lire --dry-run && python3 scripts/cbo.py $E verifier --dry-run            # VÉRIFIÉ : 24 annonces
python3 scripts/cbo.py $E lire --dry-run --pieges && python3 scripts/cbo.py $E verifier --dry-run   # les erreurs du vrai compte, bloquées
```

La simulation écrit dans `_meta/*.dry-run.json`, jamais dans l'état réel. En réel, `verifier` refuse un état lu en simulation et un relevé d'aperçu simulé.
