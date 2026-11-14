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

- GPT Image écrit parfois un mot en plus ou oublie un accent : `check.py` (OCR) sur chaque image, et regarder l'image en cas de « manque » sur un très gros titre (faux manque fréquent).
- Le modèle ne dessine jamais le logo correctement : pied vide de 10 %, logo posé par `finish.py` seulement si le pied est vraiment vide.
- Au-delà de 4 tâches en parallèle, kie.ai ralentit fortement ; une tâche relancée reprend par son `taskId` noté (aucun double paiement).
- Une direction artistique sombre a été rejetée au profit de « lumineux, simple, offre au centre » : ne pas revenir au sombre sans demande.
- Une ligne de `expect` qui n'est pas citée telle quelle dans la consigne donne un faux « manque » à l'OCR et une image refaite pour rien : `spec_check.py` l'attrape avant de payer.

## Meta : API

- Limite de débit (codes 4, 17, 32, 613, 80004) : attendre et rejouer. Après beaucoup d'écritures, Meta refuse aussi les **lectures** un moment : une liste vide lue à ce moment-là n'est pas une liste vide. `lib/meta.py` rejoue ; ne jamais décider d'archiver ou de recréer sur une lecture faite pendant une limite.
- Une erreur « An unexpected error has occurred » sur une mise à jour de publicité : relancer l'étape (elle ne refait que ce qui manque).
- Une campagne ABO peut exiger `is_adset_budget_sharing_enabled=false` à la création (le script réessaie avec).
- Le lien de confidentialité d'un formulaire fait à la main est illisible par l'API, et `legal_content_id` d'un autre formulaire est refusé : mettre un vrai lien dans `formulaire.lien_confidentialite`.
- Archiver un formulaire utilisé par les publicités d'une campagne montée à la main par la personne a cassé des dizaines de publicités d'un coup : `usage` avant tout archivage, sur TOUTES les campagnes du compte.

## Meta : éditeur dans le navigateur

- Voir `formulaire.md` (« Pièges rencontrés »). En bref : logique sur chaque réponse sinon publication muette, cibler la liste du menu cliqué, focus simulé pour le choix de la copie, jamais « Archiver », jamais Échap.
- Un agent qui pilote l'écran à la souris est interrompu dès que la personne touche au navigateur : le pilotage par JavaScript (`editeur/`) est plus fiable. Ne pas montrer de fenêtre de test devant la personne sans la prévenir.

## Après la mise en ligne

- **Le calendrier des pages de fin doit être reconnu par l'outil de l'équipe.** Cas réel : l'événement de calendrier des formulaires n'était pas rangé par le CRM, les réservations tombaient dans « à trier » sans confirmation ni suivi. Vérifier, avant d'activer, qu'une réservation de test arrive au bon endroit, et qu'elle ne déclenche pas un parcours prévu pour une autre cible.
- Les non-qualifiés qui réservent n'existent que dans le calendrier (Meta ne transmet pas leurs coordonnées) : le dire à l'équipe.
- Les relances e-mail ne partent que sur décision explicite de la personne après relecture des textes ; une séquence qui démarre pendant que l'envoi est fermé ne repart pas seule à l'ouverture.
