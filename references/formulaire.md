# Formulaire instantané qualifié sur le chiffre d'affaires

C'est la pièce la plus nouvelle du skill : un formulaire instantané Meta dont la **logique conditionnelle** trie les répondants sur leur chiffre d'affaires. Sous le seuil, la personne voit la même page de fin et peut réserver, mais **Meta ne compte aucun prospect** : l'algorithme n'apprend pas à chercher ce profil.

## Ce qu'on construit (une fois par niche)

- **Intro** (carte de contexte) : le titre et la phrase de la publicité (`card_title`, `card` de `textes_pub`), pour que la personne retrouve l'offre qu'elle a cliquée.
- **Question 1 « Vous êtes ? »** : trois profils précis du métier + « Autre » (`resume.json` → `formulaire_q1_options`). Elle sert à se reconnaître (« c'est bien pour moi ») et à trier ensuite dans le CRM ; elle ne bloque personne.
- **Question 2 « Quel est votre chiffre d'affaires annuel ? »** : 5 tranches (`formulaire.tranches_ca`, ou `formulaire_q2_options` de la niche). Les `tranches_non_qualifiees` premières (par défaut une) sont sous le seuil.
- **Coordonnées** : e-mail, nom complet, téléphone (préremplis par Meta).
- **Deux pages de fin identiques** : `page_fin.titre`, `page_fin.texte`, bouton `page_fin.bouton` vers le calendrier (`lien_reservation`, avec `utm_campaign=<clé de niche>`, `utm_id=<campagne>`, `utm_term=<ad set>`).

Deux questions seulement : c'est rapide, et chaque question de plus coûte des réponses.

## La logique conditionnelle (le cœur)

| Réponse | Va vers | Effet pour Meta |
|---|---|---|
| Q1, toute réponse | Q2 | — |
| Q2, tranche sous le seuil | « Fermer le formulaire » → page de fin des non-prospects | **aucun prospect** : Meta n'apprend pas à chercher ce profil, l'agence ne le paie pas comme prospect |
| Q2, tranche au-dessus | « Envoyer le formulaire » → page de fin des prospects (« Page de fin 1 ») | prospect normal, coordonnées transmises |

`meta_campagne.py <projet> regles` affiche ce tableau réponse par réponse pour chaque niche, sans clé.

Pourquoi deux pages identiques : la consigne est que les petits comptes **puissent quand même réserver**, sans que Meta les compte comme prospects. Leur lien porte `utm_medium=formulaire_instantane_non_qualifie` pour les reconnaître à la réservation. Meta ajoute de lui-même sur la page des non-prospects la ligne « Votre réponse ne sera pas envoyée à <page> » et saute l'écran des coordonnées : c'est normal, et ces personnes n'arrivent donc jamais dans le CRM par le formulaire (seulement par la réservation).

## Pourquoi un navigateur : ce que l'API ne fait pas (vérifié en novembre 2026)

L'API Graph (`POST /<page>/leadgen_forms`) crée questions, intro, page de fin unique, lien de confidentialité. Elle **ne sait ni écrire ni lire** la logique conditionnelle, ni une seconde page de fin, ni le contenu légal d'un formulaire fait à la main (champs essayés, documentation lue). D'où la méthode en deux temps :

1. `meta_campagne.py <projet> formulaires` crée par l'API « IF - <Niche> (base) » : tout sauf la logique.
2. `meta_campagne.py <projet> logique` ouvre l'éditeur de Meta Business Suite dans le navigateur de la personne (déjà connecté à Meta) et, pour chaque niche, lance `editeur/formulaire_final.py` : copie de la base, nom final « IF - <Niche> », logique, deuxième page de fin, publication, vérification par l'API, identifiant noté. Environ 4 minutes par niche, une niche à la fois.
3. `meta_campagne.py <projet> trouver --ecrire` (filet), puis `pubs`, puis `archiver_bases` une fois les publicités branchées.

En simulation (`--dry-run`), `logique` n'ouvre aucun navigateur : il affiche les règles qui seraient posées et note un formulaire fictif.

## Avant de lancer l'éditeur

- macOS. Navigateur `formulaire.navigateur` : `Arc` (rien à régler) ou `Google Chrome` (Présentation > Options pour les développeurs > « Autoriser JavaScript à partir des événements Apple »).
- La personne est connectée à Meta Business Suite dans ce navigateur, avec accès à la page. `python3 scripts/editeur/navigateur.py <projet> ouvrir` trouve ou ouvre l'onglet des formulaires instantanés de la page et le note dans `_meta/editeur.json`.
- L'interface de Meta doit être **en français** (les libellés cherchés sont dans `L` d'`editeur/editeur.py`). Dans une autre langue, adapter `L` après avoir lu le vrai texte (`navigateur.py <projet> js 'return H.dialogs().map(H.txt)'`).
- Le pilotage marche même onglet caché (vérifié), mais la personne ne doit pas cliquer dans cet onglet pendant le travail. Prévenir : « je pilote l'onglet Meta pendant environ 4 minutes par niche ».
- Ne jamais lancer deux éditeurs en même temps sur le même onglet.

## Ce que vérifie `formulaire_final.py` avant de publier (il s'arrête sinon, sans rien publier)

- la copie ouverte est bien celle de « IF - <Niche> (base) » (champ nom) ;
- autant de menus de logique que de réponses, chaque menu relu après réglage ;
- les règles affichées par Meta (« If answer is …, then go to … », en anglais même dans l'interface française) correspondent exactement au tableau ci-dessus ;
- l'aperçu montre deux fois le titre et le bouton, et la ligne « Votre réponse ne sera pas envoyée » ;
- aucun « requis » dans l'éditeur ; après « Créer le formulaire », l'éditeur se ferme ; l'API retrouve le formulaire sous son nom exact.

## Reprendre après un arrêt

L'éditeur reste ouvert sur la copie. Lire le message d'arrêt, regarder l'état (`navigateur.py <projet> js 'return H.dialogs().map(function(d){return H.txt(d).slice(0,500)})'`). Pour repartir de zéro : fermer le dialogue **à la main** par sa croix ; si Meta demande « Fermer le formulaire prospect ? », répondre « Fermer » sans enregistrer de brouillon ; ne **jamais** cliquer « Archiver » dans le menu Actions d'un formulaire existant. Puis relancer `meta_campagne.py <projet> logique <niche>`.

## Pièges rencontrés

- « Créer le formulaire » ne fait **rien, sans message**, tant qu'une seule réponse d'une question n'a pas de logique : chaque réponse de Q1 doit pointer vers Q2.
- La page des prospects doit avoir un nom (champ 0) sinon l'éditeur la marque « requis ».
- Le champ de recherche du formulaire à copier n'affiche ses choix qu'après des événements de focus simulés (`focusin`, `focus`) ; le premier « Suivant » peut ne pas ouvrir l'éditeur : le script réessaie.
- Plusieurs listes de menus restent affichées en même temps : toujours viser la liste du menu cliqué (`aria-owns`), sinon on règle la mauvaise réponse.
- Une liste restée au second niveau d'un réglage précédent : revenir au premier niveau (bouton sans texte) avant de choisir.
- Un Échap simulé ouvre « Fermer le formulaire prospect ? » : ne pas en envoyer.
- Ne pas archiver un formulaire tant qu'une publicité l'utilise, **dans aucune campagne** (y compris une campagne montée à la main par la personne) : `meta_campagne.py <projet> usage` d'abord. Archiver un formulaire utilisé casse ces publicités.
- Changer de formulaire = nouvelles créatives Meta : `pubs` le fait seul (la clé de créative contient l'identifiant du formulaire) et met à jour les publicités existantes.
- Un agent qui pilote l'écran à la souris a su trouver le chemin des menus, mais il s'arrête dès que la personne touche au navigateur et perd la fenêtre : le pilotage par JavaScript (`editeur/`) est plus fiable. Ne pas montrer de fenêtre de test devant la personne sans la prévenir.

## Refaire un formulaire (nouvelle version)

Un formulaire publié ne se modifie plus. Pour une nouvelle offre, une nouvelle promesse ou la vague CBO (`cbo.md`) :

1. Écris la nouvelle intro dans `resume.json → formulaire_intro` (`titre`, `texte`). Sans elle, l'intro reprend la carte des publicités (`textes_pub`).
2. Donne un nouveau nom dans `formulaire.nom`, par exemple « IF - {label} - CBO ».
3. Lance `meta_campagne.py <projet> formulaires <niche> --nouvelle-version`, puis `logique <niche>` et `trouver --ecrire`. L'ancienne version reste notée dans `formulaires_precedents` et reste en ligne. Une relance ne recrée rien. Si un formulaire actif porte déjà le nouveau nom, le script refuse.
4. Teste chaque tranche dans l'aperçu (`cbo.py apercu`) avant de brancher des publicités dessus.

## Relire un formulaire déjà publié

Pour vérifier la langue, les libellés et les tranches d'un formulaire avant d'y diriger des publicités existantes, utilise `lead_form.py check-form` du dépôt [autonomous-meta-launch](https://github.com/gquthier/autonomous-meta-launch) : il s'arrête sur des tranches qui se chevauchent ou un formulaire en anglais. Un formulaire publié ne se modifie plus : duplique-le et corrige la copie.
