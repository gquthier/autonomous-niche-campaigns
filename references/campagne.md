# Campagne Meta : structure, réglages, mise en ligne

Ce fichier couvre la structure propre à ce skill : **une campagne ABO, un ad set par niche, des publicités image vers le formulaire qualifiant de la niche**. Pour des publicités vidéo, une conversion sur page merci ou le passage d'une campagne existante vers un formulaire, utilise [autonomous-meta-launch](https://github.com/gquthier/autonomous-meta-launch).

Après une semaine, lis les résultats par annonce et passe à une CBO par niche, un ad set par angle : voir `cbo.md`.

## Structure validée

- **Une seule campagne large en ABO** (`campagne.nom`, objectif prospects, enchère au plus bas coût), **un ad set par niche** au budget `campagne.budget_jour_par_niche`. Pas une campagne par niche : le dirigeant a corrigé ce point, l'ABO garde le budget de chaque niche fixe et lisible, et chaque niche se coupe sans toucher aux autres.
- **Ad set** (repris d'un ad set qui tournait déjà sur un vrai compte) : optimisation `QUALITY_LEAD` (prospects de qualité), destination `ON_AD` (formulaire instantané), facturation à l'impression, attribution 1 jour après clic, page de l'agence en objet promu, champs DSA (bénéficiaire et payeur, obligatoires dans l'UE).
- **Ciblage large** : pays du projet, lieu de résidence ou récent, âge `age_min`–`age_max`, langues `langues_meta` si données, **aucun intérêt**, Advantage+ audience coupé, Facebook et Instagram seulement (pas d'Audience Network), placements fil, stories, reels, vidéo in-stream, marketplace. C'est la créative qui cible : la niche est nommée en tête de chaque image et de chaque texte.
- **Publicités** : une par créative finale de la niche (10 + 2 variantes « performance »), image unique, texte de `textes_pub`, bouton « En savoir plus » vers le formulaire final de la niche, **toutes les améliorations automatiques de Meta refusées** (`assets/creative_sans_ameliorations.json` : la publicité reste exactement l'image et le texte écrits). Si Meta refuse ces réglages, le script réessaie sans.

## Texte des publicités (généré par `lib/projet.py` → `textes_pub`)

```
{cible_pub} : {volume_garanti} {unite_longue} en {duree_jours} jours.

{ligne_metier}

{garantie} : {remboursement_par_unite} € remboursés par {unite_manquante}, ou {prolongation_jours} jours de plus sans frais.
{installation}.
{budget_pub}

{consigne_pub}
```

Titre : `{volume_garanti} {unite_courte} en {duree_jours} jours` ; description : la garantie courte. Pour une variante `-performance`, la garantie devient `offre.variante_performance`. Une niche hors modèle (garantie différente, cible sans volume) met un `texte_pub` complet dans son `resume.json`. **Toujours montrer les textes (`meta_campagne.py <projet> textes`) à la personne avant `pubs`.**

## Ordre des étapes

Commence toujours par la simulation complète, sans clé :

```bash
python3 scripts/meta_campagne.py <projet> parcours --dry-run
```

Puis, en réel, une étape à la fois, en relisant chaque sortie :

```bash
python3 scripts/meta_campagne.py <projet> verifier          # lecture seule : resume.json, jeton, compte, page, formulaires
python3 scripts/meta_campagne.py <projet> textes            # à faire valider
python3 scripts/meta_campagne.py <projet> regles            # la logique attendue de chaque formulaire
python3 scripts/meta_campagne.py <projet> campagne          # en pause
python3 scripts/meta_campagne.py <projet> adsets            # en pause, un par niche
python3 scripts/meta_campagne.py <projet> formulaires       # bases par l'API (liens de réservation avec campagne et ad set)
python3 scripts/meta_campagne.py <projet> logique           # éditeur Meta dans le navigateur, ~4 min par niche
python3 scripts/meta_campagne.py <projet> trouver --ecrire  # filet : retrouve les formulaires finaux par leur nom
python3 scripts/meta_campagne.py <projet> images
python3 scripts/meta_campagne.py <projet> pubs              # publicités actives DANS des ad sets en pause : rien ne diffuse
python3 scripts/meta_campagne.py <projet> controle          # tout doit être « sur le bon formulaire » et « large : oui »
python3 scripts/meta_campagne.py <projet> archiver_bases    # bases inutilisées
python3 scripts/meta_campagne.py <projet> activer --oui     # SEULEMENT sur accord explicite : dépense réelle
```

Chaque étape accepte une liste de niches (`… pubs salles-de-sport paysagistes`) et ne recrée jamais ce qui est noté dans `_meta/etat.json`. Chaque identifiant y est écrit dès que Meta le renvoie : après une coupure, relance la même commande.

## Activer : la règle

L'activation dépense de l'argent et publie des publicités : elle demande l'accord explicite de la personne, **pour cette campagne et ce budget**, même si elle a dit « go » pour la préparation. Avant de demander, donner : nombre d'ad sets, budget total par jour, phrases de garantie affichées, et ce qui n'est pas encore branché (CRM, calendrier, e-mails). Un accord donné pour un lot de niches ne vaut pas pour un autre lot ajouté plus tard. `activer` refuse sans `--oui`, refuse une niche incomplète, active les ad sets puis la campagne **en dernier**.

## Ajouter des niches à une campagne qui tourne

Ajouter la niche dans `projet.json`, puis `adsets <niche>` (en pause), `formulaires <niche>`, `logique <niche>`, `images <niche>`, `pubs <niche>`, `controle`, et demander l'accord avant `activer --oui <niche>` (n'active que les ad sets de ces niches, la campagne l'est déjà). Pour « déplacer » des ad sets d'une autre campagne : Meta ne déplace pas un ad set ; on recrée dans la campagne cible avec les mêmes réglages, et l'ancienne campagne reste en pause. Pour copier un ad set existant sans ses publicités et comparer ses réglages, `lead_form.py copy-adset` et `diff-adsets` d'autonomous-meta-launch font le travail.

## Contrôles après lancement

- `controle` : statut effectif de chaque publicité (`PENDING_REVIEW` puis `ACTIVE`, jamais `DISAPPROVED`), formulaire de chaque publicité, budget actif total. Ne dis jamais « les publicités sont en ligne » sur la seule foi de la réponse d'activation : donne le décompte relu, par statut.
- Premier prospect : vérifier qu'il arrive dans l'outil de l'équipe (CRM, alerte) avec la niche, le profil et le chiffre d'affaires ; s'il n'existe pas d'outil, `GET /<formulaire>/leads` avec le jeton de page.
- Ne pas toucher aux campagnes existantes du compte qui ont déjà de la dépense, sauf demande explicite.
