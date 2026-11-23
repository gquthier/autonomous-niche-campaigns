# projet.json et dossier de travail

Le dossier de travail est privé : il contient l'offre, les études, les identifiants Meta créés. Il vit **hors du dépôt du skill**. L'exemple fictif complet est dans `examples/agence-exemple/`.

## Dossier de travail

```
<projet>/
  projet.json                      configuration (copie de assets/projet.exemple.json)
  _commun/
    logos/logo-clair.png, logo-noir.png      logo officiel (PNG transparent), posé par finish.py
    ads-library/<clé>/*.json                 annonces des concurrents (adlib.py)
    presentation-generique/                  présentation de l'agence (base des présentations par niche)
  <n>-<niche>/                     un dossier par niche (nom = niches[].dossier)
    analyse.md   offre.md   publicite.md   resume.json
    presentation/presentation.html, presentation.pdf, pages/
    creatives/spec.json   creatives/work/{raw,jobs,view}/   creatives/final/*.jpg
    cbo/angles.json   cbo/statiques/<angle>-S01-4x5.jpg, -9x16.jpg   (passage en CBO, voir cbo.md)
  sequences-email/sequence-formulaire.json, sequences.md
  cbo/resultats-abo.csv            export des résultats de l'ABO par annonce (gestionnaire de publicités)
  cbo/annonces.csv                 grille et copy de la CBO, une ligne par annonce (cbo.py grille)
  _meta/etat.json                  identifiants Meta créés (ne pas éditer à la main sauf réparation)
  _meta/editeur.json               onglet du navigateur piloté
  _meta/etat.dry-run.json, monde.dry-run.json   simulation (--dry-run), jamais mélangée avec l'état réel
  _meta/cbo-etat-lu.json           état réel relu par cbo.py lire (identifiants : privé)
  _meta/apercu-formulaires.json    relevé de l'aperçu de chaque formulaire, rempli après test
  _meta/push-verified.json         la preuve : écrit par cbo.py verifier seulement si tout passe
```

## Champs de projet.json

- `agence` : `nom` (préfixe des ad sets et des créatives Meta), `site`, `positionnement`, `signature_email` (fin de chaque e-mail, contrôlée), `logo_clair` / `logo_noir` (chemins relatifs au projet), `presentation_generique` (présentation de l'agence dont les présentations par niche reprennent la structure et les preuves).
- `offre` : la règle commune à toutes les niches. `prix` (phrase), `prix_ht` (nombre), `duree_jours`, `garantie_courte`, `variante_performance` (phrase des variantes de test), `garantie_mecanique` (`prorata` : prix ÷ volume par unité manquante), `prolongation_jours` (alternative au remboursement), `installation`, `budget_pub`. Une décision du dirigeant sur le prix ou la garantie se change ICI, puis se reporte dans chaque `resume.json`, présentation, créative et e-mail.
- `meta` : `token_var` (nom de la variable qui porte le jeton, `META_ACCESS_TOKEN` par défaut), `ad_account` (`act_…`), `page_id`, `instagram_user_id` (compte Instagram relié à la page, facultatif), `business_id` (facultatif, pour l'adresse de l'éditeur), `graph_version`, `dsa_beneficiary` / `dsa_payor` (nom légal affiché dans l'UE). Laissés vides, les quatre identifiants sont lus dans `META_AD_ACCOUNT`, `META_PAGE_ID`, `META_INSTAGRAM_ID`, `META_BUSINESS_ID`.
- `formulaire` : `nom` (modèle, `{label}` = libellé de la niche ; la base s'appelle « <nom> (base) »), `locale`, `question_profil`, `question_ca`, `tranches_ca`, `tranches_non_qualifiees` (combien de tranches, depuis le haut, sont sous le seuil), `lien_reservation` (calendrier sans UTM : ils sont ajoutés), `lien_confidentialite` (obligatoire), `entete_questions`, `consigne_pub` (dernière ligne des publicités), `page_fin` (`titre`, `texte`, `bouton`), `nom_page_prospects`, `navigateur` (`Arc` ou `Google Chrome`).
- `campagne` : `nom` (`{mois}` remplacé par le mois et l'année), `budget_jour_par_niche` (euros), `pays`, `age_min`, `age_max`, `langues_meta` (facultatif ; 9 et 44 : français), `prefixe_adset` (facultatif).
- `cbo` (passage en CBO, `cbo.md`) :
  - `campagne_nom`, `adset_nom`, `formulaire_nom` : modèles, avec `{label}`, `{agence}`, `{angle}` et `{titre}` ;
  - `budget_jour_par_campagne` (euros) ;
  - `angles_min` (3), `statiques_min` (4), `statiques_max` (8) ;
  - `formats` : tailles attendues, `4x5` 1080 × 1350 et `9x16` 1080 × 1920 ;
  - `bouton` ;
  - `non_qualifies` : `sans_trace`, `reservation_marquee` ou `liste`, **à décider avec la personne avant de publier** ;
  - `fraicheur_minutes` (60) : au-delà, `verifier` exige un nouveau `lire` ;
  - `accents_permis` : mots à ne pas signaler, par exemple une marque.
- `creatives` : `kie_key_var`, `par_niche` (10), `variantes_performance` (2), `reserve_credits` (gen.py refuse de descendre sous ce solde).
- `recherche` : `apify_token_var`, `pays` de la Bibliothèque publicitaire.
- `sequences` : `mots_interdits` (mots que l'agence n'écrit pas aux prospects), `nombres_permis` (nombres admis partout, par défaut « 30 », la durée de l'étude).
- `<niche>/resume.json → formulaire_intro` (facultatif) : `titre` et `texte` de la carte d'intro du formulaire, quand elle doit différer des publicités (vague CBO, nouvelle promesse).
- `<niche>/cbo/angles.json` : `code` (lettre des clés d'angle), `promesse` (dite à l'identique par les annonces et le formulaire), `expressions_interdites` (anciennes formulations), `angles[]` (`cle`, `titre`, `gagnant_de_depart`, `hypothese`, `texte_principal`, `texte_court`, `texte_long`, `description`, `statiques[]` avec `format`, `accroche`, `titre`).
- `niches[]` : `cle` (ASCII, sert dans les UTM et l'état), `dossier`, `label` (affiché : nom du formulaire, de l'ad set), `ads_library` (requêtes courtes).

## Le jeton Meta : ce qu'il lui faut

Un jeton d'utilisateur système (Business Manager > Utilisateurs système), longue durée, avec : `ads_management`, `ads_read`, `business_management`, `leads_retrieval`, `pages_manage_ads`, `pages_read_engagement`, `pages_show_list`, `pages_manage_metadata`. L'utilisateur système doit avoir le compte publicitaire et la page en actifs attribués (contrôle total). `meta_campagne.py <projet> verifier` dit ce qui manque.

Le jeton vit dans la variable d'environnement, jamais dans un fichier du projet, un message ou un commit. Pour le créer avec un agent qui pilote l'écran sans que le jeton passe par le chat, suis le guide `references/token-meta-computer-use.md` du dépôt [autonomous-meta-launch](https://github.com/gquthier/autonomous-meta-launch).

## Clés externes

- kie.ai (`KIE_API_KEY`) : génération d'images GPT Image, environ 18 crédits par image en texte vers image, 20 en image vers image. Une niche complète (10 images, quelques reprises, 2 variantes) coûte de l'ordre de 300 crédits.
- Apify (`APIFY_TOKEN`) : relevé de la Bibliothèque publicitaire, facultatif. Sans lui, l'étude des concurrents se fait à la main sur facebook.com/ads/library.
