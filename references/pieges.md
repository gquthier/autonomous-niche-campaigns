# Pièges rencontrés sur un vrai compte (novembre 2026), et la parade

Lis ce fichier une fois avant l'étape des créatives : chacun de ces points a déjà coûté de l'argent, du temps ou des publicités.

## Offre et contenu

- **Prix ou garantie qui dérivent d'une niche à l'autre.** Laissés libres, des agents ont proposé du paiement au résultat avec des montants très différents d'une niche à l'autre ; le dirigeant a imposé un prix unique payé au départ et une garantie au prorata. Parade : la règle vit dans `projet.json → offre` ; chaque livrable la reprend mot pour mot ; une variante (« Payé à la performance ») est une décision explicite du dirigeant, pas une initiative.
- **Paiement au résultat illégal dans certains métiers** (immobilier de transaction, intermédiation en crédit, paiement au patient en santé). Parade : l'étude de la niche cherche la réglementation ; la garantie se rédige en remboursement d'un forfait, jamais en commission ; les variantes « performance » d'une niche à risque sont créées en pause (`variantes_performance_en_pause` dans `resume.json`) et la personne tranche.
- **La variante « Payé à la performance » contredit un forfait payé au départ.** Elle a été demandée et validée par le dirigeant, et son texte de publicité généré (« Payé à la performance : <montant> € remboursés par <unité> manquante… ») est celui qui a tourné. À chaque nouveau projet, redemander si ces variantes doivent exister, et pour quelles niches. Une niche peut imposer son propre texte avec `texte_pub` dans son `resume.json`.
- **Garantie diffusée avant l'avis d'un avocat.** La signaler à chaque livraison tant que la clause n'est pas au contrat.
- **Chiffres et cas clients inventés** dans les textes (un agent a écrit un chiffre d'affaires cumulé et un nombre de clients qui n'existaient nulle part). Interdits partout : seuls les chiffres des sources de la niche et de l'offre. `sequences/verifier.py` le contrôle pour les e-mails ; relire les présentations et les créatives avec la même règle.
- **Phrases saisonnières** (« avant le printemps ») : elles vieillissent ; les lister à la livraison.

## Créatives

- Deux agents ont écrit dans le même dossier de niche et écrasé des fichiers. Donner un dossier exclusif à chacun ; avant l'envoi, vérifier le nombre de visuels, leurs noms et leur contenu, pas seulement la présence du dossier.
- GPT Image écrit parfois un mot en plus ou oublie un accent : `check.py` (OCR) sur chaque image, et regarder l'image en cas de « manque » sur un très gros titre (faux manque fréquent).
- Le modèle ne dessine jamais le logo correctement : pied vide de 10 %, logo posé par `finish.py` seulement si le pied est vraiment vide.
- Au-delà de 4 tâches en parallèle, kie.ai ralentit fortement ; une tâche relancée reprend par son `taskId` noté (aucun double paiement).
- Une direction artistique sombre a été rejetée au profit de « lumineux, simple, offre au centre » : ne pas revenir au sombre sans demande.
- Une ligne de `expect` qui n'est pas citée telle quelle dans la consigne donne un faux « manque » à l'OCR et une image refaite pour rien : `spec_check.py` l'attrape avant de payer.

## Meta : API

- La campagne mère peut être en pause avec d'anciens ad sets encore marqués actifs. Réactiver cette campagne relancerait ces anciens ensembles aussi : lire tous les enfants avant activation et, si la demande vise un lot séparé, préparer une campagne distincte en pause.
- Plusieurs écritures simultanées dans le même état local peuvent s'écraser. Pendant la logique des formulaires, ne pas envoyer des images ou publier des annonces dans ce même projet ; attendre, puis relire les identifiants depuis le compte.
- Limite de débit (codes 4, 17, 32, 613, 80004) : attendre et rejouer. Après beaucoup d'écritures, Meta refuse aussi les **lectures** un moment : une liste vide lue à ce moment-là n'est pas une liste vide. `lib/meta.py` rejoue ; ne jamais décider d'archiver ou de recréer sur une lecture faite pendant une limite.
- Une erreur « An unexpected error has occurred » sur une mise à jour de publicité : relancer l'étape (elle ne refait que ce qui manque).
- Une campagne ABO peut exiger `is_adset_budget_sharing_enabled=false` à la création (le script réessaie avec).
- Le lien de confidentialité d'un formulaire fait à la main est illisible par l'API, et `legal_content_id` d'un autre formulaire est refusé : mettre un vrai lien dans `formulaire.lien_confidentialite`.
- Archiver un formulaire utilisé par les publicités d'une campagne montée à la main par la personne a cassé des dizaines de publicités d'un coup : `usage` avant tout archivage, sur TOUTES les campagnes du compte.

## Meta : éditeur dans le navigateur

- Voir `formulaire.md` (« Pièges rencontrés »). En bref : logique sur chaque réponse sinon publication muette, cibler la liste du menu cliqué, focus simulé pour le choix de la copie, jamais « Archiver », jamais Échap.
- Un agent qui pilote l'écran à la souris est interrompu dès que la personne touche au navigateur : le pilotage par JavaScript (`editeur/`) est plus fiable. Ne pas montrer de fenêtre de test devant la personne sans la prévenir.

## Après la mise en ligne

- Une nouvelle niche peut manquer dans le CRM même si son formulaire et ses annonces sont corrects. Avant activation, vérifier son classement et ses seuils avec une réservation de test, sans modifier les règles de qualification à la place du dirigeant.

- **Le calendrier des pages de fin doit être reconnu par l'outil de l'équipe.** Cas réel : l'événement de calendrier des formulaires n'était pas rangé par le CRM, les réservations tombaient dans « à trier » sans confirmation ni suivi. Vérifier, avant d'activer, qu'une réservation de test arrive au bon endroit, et qu'elle ne déclenche pas un parcours prévu pour une autre cible.
- Les non-qualifiés qui réservent n'existent que dans le calendrier (Meta ne transmet pas leurs coordonnées) : le dire à l'équipe.
- Les relances e-mail ne partent que sur décision explicite de la personne après relecture des textes ; une séquence qui démarre pendant que l'envoi est fermé ne repart pas seule à l'ouverture.
- **Ne pas lire les formulaires chaque minute.** Cas réel : 13 formulaires interrogés toutes les minutes, Meta a bloqué l'application pendant une dizaine d'heures et les nouveaux prospects n'arrivaient plus au CRM, donc aucune relance. Un seul passage toutes les 5 minutes pour tous les formulaires suffit. Après chaque changement, vérifier qu'un prospect réel est bien entré.
- **« C'est en ligne » se prouve par un envoi réel.** Une séquence déployée mais jamais déclenchée ressemble à une séquence qui tourne. Contrôler qu'une relance est vraiment partie pour chaque niche, depuis la bonne boîte, avec les textes de sa niche.
- **Une réservation doit arrêter la relance, quelle que soit l'adresse.** Les prospects réservent souvent avec un autre e-mail que celui du formulaire : rapprocher par e-mail, puis téléphone, puis nom, sinon ils reçoivent « votre rendez-vous n'est pas confirmé » après avoir réservé.
- **Les réponses doivent être lues par l'outil qui envoie.** Si la boîte d'envoi n'est pas reliée en lecture, un « stop » n'arrête rien. Brancher la lecture avant d'ouvrir l'envoi, et garder le lien de désinscription tant qu'elle ne marche pas.

## Recherche interrompue par un quota

Un quota mensuel Apify atteint peut interrompre toutes les recherches qui partagent ce compte. Marquer chaque niche « mesurée », « relevé partiel » ou « estimée » ; une réponse vide ou une erreur ne prouve pas l'absence de concurrents. Une recherche web peut compléter le dossier, sans être présentée comme un relevé direct de la Bibliothèque publicitaire. Signaler les autres workflows qui dépendent du même quota ; ne pas relever le plafond payant de sa propre initiative.

## Passage en CBO (novembre 2026)

Le jour du passage en CBO (voir `cbo.md`), les créatives, la copy et les scripts étaient prêts en quelques heures. Les erreurs sont venues après, entre « c'est prêt » et « c'est dans le compte ».

- **« C'est fait » alors que rien n'était dans le gestionnaire de pubs.** Cas réel : la personne a demandé trois fois si c'était fait. Au moment de la troisième question, la campagne d'une niche n'existait pas, et les deux autres n'avaient qu'un ad set chacune. Les fichiers étaient prêts en local, et l'agent avait parlé du dossier comme si c'était le compte. Parade : après chaque lot de créations, `cbo.py lire` puis `verifier`, et rien d'annoncé sans le `_meta/push-verified.json` qu'il écrit. Dis toujours si c'est « prêt en local » ou « dans le compte ».
- **La logique conditionnelle oubliée sur les nouveaux formulaires.** Cas réel : les formulaires refaits pour la CBO posaient bien la question du chiffre d'affaires, mais sans aucune règle. Sous le seuil, on envoyait ses coordonnées et Meta comptait un prospect. C'est la personne qui l'a vu. Parade : l'API ne lit pas la logique, donc on teste chaque tranche dans l'aperçu. Le relevé (`cbo.py apercu`, `_meta/apercu-formulaires.json`) est bloquant dans `verifier`.
- **Des fautes d'accents dans les formulaires.** Cas réel : « Derniere etape », « etude », relevés par la personne avant publication. Un formulaire publié ne se corrige plus, il se refait. Parade : `verifier` arrête les mots courants écrits sans accent et signale un long texte sans aucun accent. La relecture mot à mot de chaque écran dans l'aperçu reste obligatoire (`accents_relus`).
- **L'annonce et le formulaire ne promettaient pas la même chose.** Cas réel : les nouvelles annonces promettaient des « demandes préqualifiées », et les anciens formulaires des « rendez-vous tenus ». Parade : une seule phrase `promesse` par niche dans `angles.json`, reprise dans `resume.json → formulaire_intro`. L'ancienne formulation va dans `expressions_interdites`. `grille` et `verifier` refusent tout écart.
- **Le lien de politique de confidentialité ouvrait l'accueil du site.** Cas réel, sur les trois formulaires. Parade : `formulaire.lien_confidentialite` pointe vers la vraie page. `verifier` refuse une racine de domaine ou l'accueil de `agence.site`, et dans l'aperçu on clique le lien.
- **Les anciennes annonces actives restent sur l'ancien formulaire et l'ancienne offre.** Cas réel : une vingtaine d'annonces de l'ABO diffusaient encore, avec la promesse d'avant, pendant que la CBO se préparait. Parade : `verifier` les liste avec leur formulaire. Montre la liste à la personne : couper, garder ou rebrancher est sa décision. N'archive jamais leur formulaire tant qu'elles tournent (`meta_campagne.py usage`).
- **Ceux qui sont sous le seuil sortent sans laisser de trace.** Cas réel : la personne voulait une liste « non qualifiés », mais le formulaire se fermait avant les coordonnées, donc il n'y avait aucune liste. Parade : décider avant de publier (`cbo.non_qualifies`, trois choix expliqués dans `cbo.md`). `verifier` bloque tant que ce n'est pas écrit.
- **Un deuxième compte publicitaire jamais vérifié.** Cas réel : la personne parlait de « deux comptes ». Faute de nom ou d'identifiant, seul le premier a été contrôlé. Parade : demander au départ la liste des comptes concernés, et faire `lire` et `verifier` sur chacun.
- **Ajouter à une CBO déjà active.** Les nouveaux ad sets en pause ne dépensent rien, mais la campagne diffuse toujours son contenu d'avant. `verifier` le signale. Ne présente pas la niche comme « en pause ».
- **Des scripts vidéo publiés sur un site public.** Le mini-site des scripts était accessible sans connexion, et il a été partagé à l'équipe. Parade : demander avant toute publication en ligne, et n'y mettre ni identifiant, ni lien du gestionnaire de pubs, ni prix non validé.
