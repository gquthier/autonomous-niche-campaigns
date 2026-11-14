# L'offre d'une niche : structure « Plein 90 »

Une offre par niche, toutes bâties sur la même structure, adaptée au métier et à son marché. Le nom (« <Nom> Plein 90 ») n'est pas obligatoire : sur le projet d'origine, l'étude a conseillé de l'abandonner dans une niche où le mot éloignait la cible haut de gamme. Ce qui compte, c'est la structure.

**Positionnement, à tenir partout** : l'agence installe chez le client **une infrastructure d'acquisition tenue par des agents IA**. Les comptes, les annonces, le formulaire et l'historique sont au nom du client et lui restent.

À lire avant : `analyse.md` de la niche (chiffres, avatar, concurrents, réglementation), puis `projet.json` → `offre`.

## 1. Les règles fixes (elles viennent de `projet.json` → `offre`)

Le dirigeant les a tranchées ; aucun agent ne les change.

1. **Prix unique, réglé au départ** : `offre.prix` (exemple fictif : « 3 600 € HT pour 90 jours, réglés au départ »), le même pour toutes les niches. L'agence encaisse au départ. Aucune formule au rendez-vous tenu, à la signature, à l'unité vendue, en pourcentage du chantier ; pas de « 0 € à la commande », pas de « rien à la signature », pas de facture à 0,00 €.
2. **Garantie remboursée au prorata** (`garantie_mecanique: "prorata"`) : le volume promis en `duree_jours`, **ou** `remboursement_par_unite` € remboursés par unité manquante, **ou** `prolongation_jours` jours de plus sans frais, au choix du client.
   `remboursement_par_unite = prix_ht ÷ volume_garanti`, arrondi à l'euro (exemple : 3 600 ÷ 40 = 90 ; ÷ 24 = 150). Plafond : le prix payé.
3. **Dans les publicités**, la garantie se dit `offre.garantie_courte` (« Garantis ou remboursés. »), accordée à l'unité (« Garanties ou remboursées. » pour des visites). On n'y écrit pas « vous ne payez que si… », « payé au résultat », ni aucun prix à l'unité. La variante `offre.variante_performance` ne sert qu'aux deux créatives de test par niche et à leurs publicités (voir `creatives.md`).
4. **Toujours dire** `offre.installation` (« Mise en place en 5 jours » dans l'exemple) et `offre.budget_pub` (le budget publicitaire est en plus, réglé directement à Meta par le client).
5. **Jamais de rémunération au résultat qui ferait tomber l'agence sous une réglementation** (section 8). Un forfait fixe réglé au départ les respecte toutes. Les garanties sont **à faire valider par un avocat** avant le premier client.

## 2. Les huit blocs de l'offre

| Bloc | Ce qu'il dit | Règle |
|---|---|---|
| **Promesse** | Une phrase : le volume, l'unité dans les mots du métier, la durée, la garantie | Unité qui parle au métier (« essais encadrés tenus dans votre club », « visites de jardin qualifiées chez des propriétaires »), jamais « leads » |
| **Pour qui (ICP)** | Critères chiffrés et exclusions | Statut, sites, chiffre d'affaires, panier, vendeurs, créneaux, zone, budget publicitaire. Exclure ceux dont un siège pilote la publicité, les paniers trop bas, ceux qui ne peuvent pas recevoir le volume |
| **Unité comptée** | La définition exacte de ce qui compte | Conditions vérifiables, preuve, cas limites (section 4) |
| **Livrables** | Ce que l'agence installe | Le cœur, sans rien y ajouter (section 5) |
| **Bonus** | Quatre bonus du métier | 100 % numériques, tenus par des agents IA (section 6) |
| **Garantie** | La phrase complète et ses conditions | Prorata, conditions finies, la garantie ne tombe jamais (section 7) |
| **Prix** | `offre.prix` + budget publicitaire minimum de la niche | Le budget minimum se calcule (section 3) |
| **Économie du client et exposition de l'agence** | Ce que le client gagne dans trois scénarios ; ce que la garantie coûte à l'agence | Calculs écrits, hypothèses marquées |

## 3. Le volume : un peu au-dessus du marché

**Règle** : promettre **un peu plus** que ce que les concurrents promettent déjà **sur la même unité**. Si le marché promet 30 essais en 90 jours, promets-en 40. Un tiers de plus se lit sans calcul ; un chiffre deux fois plus gros n'est pas cru, et le budget publicitaire ne le tient pas. Le dirigeant du projet d'origine a corrigé dans ce sens un premier volume jugé trop timide.

Comment le fixer, dans `offre.md` :
1. **Choisis l'unité.** Tableau des unités possibles (demande remplie, prospect qualifié, rendez-vous tenu, signature) avec ce que le budget peut donner, le pour, le contre, la décision. Retiens l'unité que le marché vend déjà (comparaison directe) et qui dépend de l'agence. La signature se suit et se rend au bilan, elle ne se garantit pas : elle se fait sans l'agence, se déclare, arrive tard.
2. **Calcule le coût probable d'une unité** : coût d'une demande ÷ (part qui prend rendez-vous × part qui vient). Trois hypothèses (favorable, centrale, défavorable), sources et niveaux.
3. **Vérifie que le volume tient dans le budget** : `budget publicitaire sur 90 jours ÷ volume` = coût par unité supposé. Il doit tomber au milieu de la fourchette, pas au bas. Tableau « Pourquoi pas plus » : publicité nécessaire à un volume plus haut.
4. **Fixe le budget publicitaire minimum** : `volume × coût central`, sur 90 jours, ramené au mois et arrondi à un chiffre qui se dit (exemple fictif : 40 × 90 € = 3 600 € sur 90 jours, soit 1 200 € par mois).
5. **Vérifie que le client peut les recevoir** : unités par semaine ÷ vendeurs.

## 4. L'unité comptée

Écris les conditions qui font compter une unité (six conditions dans le projet d'origine) : **origine** (vient des campagnes de l'agence), **qualité** (propriétaire, majeur, emprunteur avec apport…), **budget ou montant** déclaré au-dessus d'un plancher, **délai** du projet, **zone**, **présence** (la personne est venue et a été reçue).

Puis : la **preuve** (l'agent IA demande au vendeur si la personne est venue et à la personne si elle a été reçue ; contestation sous 48 heures ouvrées ; le silence vaut validation) et les **cas limites** écrits d'avance (absent, reporté, doublon, un seul conjoint, le client annule lui-même, la personne signe ou non). Écris « annoncé » et non « vérifié » quand le budget est seulement déclaré.

## 5. Le cœur (ne rien ajouter)

1. Campagnes Facebook et Instagram, sur le compte du client, à son nom.
2. Formulaire de préqualification bâti sur ses critères (besoin, zone, délai, budget), avec les cases de consentement exigées par la loi.
3. Agent IA de qualification : répond par écrit en quelques minutes, se présente comme assistant automatique, vérifie les critères, écarte ceux qui ne veulent qu'un prix, réserve le rendez-vous, transmet une fiche complète.
4. Suivi : point chaque semaine avec les chiffres, ligne directe avec l'équipe ; comptes et annonces restent au client.
5. Mise en place dans le délai de `offre.installation`.

Écris aussi **« Votre part »** (une heure au démarrage, les accès, des photos, des créneaux, répondre « venu » ou « pas venu ») : elle réduit l'effort perçu et conditionne la garantie.

## 6. Les bonus

Cadre Hormozi : chaque bonus répond à une objection, ou à un problème que le résultat crée (plus de rendez-vous = plus de devis à relancer, plus d'appels manqués), ou à une faiblesse des offres concurrentes. Il se présente par la **situation désirée**.

- **100 % numériques, faits par des agents IA**, sans tournage, déplacement, commercial ni téléphoniste. Seul coût : des clés d'API et des jetons, absorbés par l'agence.
- Des choses que d'autres facturent cher. Le prix « ailleurs » est un **prix de marché sourcé** (lien, date de lecture), jamais la valeur de l'offre.
- Propose **6 à 8 pistes**, retiens **les 4 meilleures** dans un tableau (piste, problème, prix ailleurs, décision et pourquoi). Écarte ce qui est illégal (réactivation téléphonique d'anciens contacts sans consentement) ou trompeur (image générée présentée comme un plan ou une réalisation).
- Pistes qui reviennent : dossier préparé avant le rendez-vous et rappels ; relance des devis jusqu'à la signature ; standard téléphonique automatique (il décroche, il n'appelle jamais) ; fiche Google et avis demandés à tous, sans tri ni contrepartie ; référencement automatique sur Google et dans les assistants IA ; préqualification par messagerie ; relecture de conformité des annonces (métiers réglementés).

Fiche de chaque bonus retenu : le problème (dans les mots du client), ce que fait l'agent concrètement, la situation désirée (titre de la diapositive), ce que cela remplace et son prix avec la source, l'effort et le coût d'API pour l'agence, l'objection qu'il lève, sa limite légale. Termine par **la pile** : tableau bonus / ailleurs sur 90 jours / source, avec le total.

## 7. La garantie, ses conditions

Phrase complète (gabarit, reprise mot pour mot partout) :
`{volume_garanti} {unite_longue} en {duree_jours} jours, ou {remboursement_par_unite} € remboursés par {unite_manquante}, ou {prolongation_jours} jours de plus sans frais, à votre choix. {budget_pub}`

Conditions finies et mesurables : budget publicitaire minimum réellement dépensé, sans coupure de plus de 3 jours ; créneaux ouverts chaque semaine ; rendez-vous possible sous 7 jours ; confirmation ou contestation sous 48 heures ouvrées ; accès ouverts et annonces validées sous 48 heures ; zone et critères inchangés sans accord écrit.

**Si le client manque à une condition, la période est prolongée d'autant : la garantie ne tombe pas.** Le remboursement s'écrit comme une réduction de prix, pas comme une pénalité **[avocat]**. **Aucune garantie sur les ventes.** Dis-le.

## 8. Pièges réglementaires (exemples relevés en France, novembre 2026)

| Métier | Ce qui interdit le paiement au résultat ou contraint l'offre |
|---|---|
| Immobilier de transaction | Loi Hoguet : un prestataire ne peut être payé ni au mandat, ni à la vente, ni en pourcentage. Catégorie Logement de Meta (rayon d'au moins 15 km, ni âge ni genre) |
| Courtage en crédit | Des honoraires liés au prêt, ou un agent qui conseille, feraient de l'agence un intermédiaire en crédit non immatriculé. Catégorie Crédit ; le formulaire Meta ne demande ni revenus ni dettes |
| Conseil en patrimoine | Rien de lié à une souscription ni à la collecte (partage de commission). Aucun produit, taux ni « garanti » dans les annonces du client ; montant à placer demandé par l'agent, pas par le formulaire |
| Santé (exemple : audition) | Payer un intermédiaire au patient est tenu pour illégal par la profession. Ni « gratuit », ni remboursement, ni question de santé ; on dit « patient » |
| Habitat (travaux, piscine, jardin) | Ni financement ni mensualité dans les publicités du client ; catégorie Logement possible |

Partout : rappel d'un particulier seulement après un consentement préalable nommant le client et l'agence ; l'agent IA dit qu'il est une IA dès le premier message ; aucun appel sortant par agent vocal ; consentement distinct pour WhatsApp et SMS ; dans la publicité de l'agence, « garanti » n'est vrai qu'avec ses conditions à portée de clic et le budget publicitaire dit. Ces points ont été relevés par des agents à une date donnée : **un avocat les valide avant le premier client**.

## 9. Le format d'`offre.md`

1. La promesse. 2. Le volume (unité, pourquoi ce chiffre, pourquoi pas plus, ce que la garantie coûte à l'agence). 3. Pour qui (tableau critère / seuil / pourquoi) et exclus. 4. L'unité comptée (conditions, preuve, cas limites). 5. Ce que l'agence installe (tableau « dit pour ce métier »), votre part. 6. Les bonus (pistes, quatre fiches, la pile). 7. La garantie (phrase, conditions). 8. Prix et budget publicitaire (tableau par poste, total client, suite proposée après 90 jours). 9. L'économie pour le client : trois scénarios (objectif atteint, médian, bas) avec unités, taux de signature, ventes, coût total, marge et multiple ; le panier sous lequel l'offre perd de l'argent. 10. L'exposition de l'agence : tableau unités tenues → somme rendue ; coût de service ; point mort ; pire cas. 11. Risques et parades (tableau). 12. Le plan des 90 jours (tableau moment / ce qui se passe / ce qu'on regarde, avec les seuils d'alerte au 30e et au 45e jour).

Les chiffres de marché portent source et niveau ; les chiffres de l'offre sont des propositions avec le calcul qui y mène.

## 10. Le format de `publicite.md`

1. **La phrase de promesse** : `promesse_pub`, sa version courte pour l'image, et pourquoi chaque mot (cible en premier, chiffre comparé au marché, mot du métier, « tenus »).
2. **Cinq titres** de moins de 40 caractères, nombre de caractères entre parenthèses.
3. **La garantie** : phrase courte, phrase complète, et tableau des phrases demandées vérifiées contre l'offre (vraie ? ce qu'il faut pour la dire).
4. **Le formulaire** : Q1 « Vous êtes ? » avec ses quatre réponses (la sous-niche visée, celle d'à côté, celle à écarter, « Autre ») et un tableau rôle / pourquoi ; Q2 les tranches de `projet.json` → `formulaire.tranches_ca` (sauf si le métier exige d'autres bornes) ; la tranche minimale retenue et pourquoi ; ce que l'appel vérifie ensuite. Le détail technique est dans `formulaire.md`.
5. **Dix idées de créatives** : format, visuel, objets du métier, texte exact à l'image, pourquoi elle arrête le bon regard ; ordre de test conseillé.
6. **Mots et images à éviter** : jargon d'agence (lead, closing, tunnel), promesses déjà prises par les concurrents, fausse urgence, faux clients, logos d'enseignes, registre de la peur.

## 11. `resume.json` : schéma exact

Les scripts le lisent : clés exactes, valeurs en français. Exemple fictif complet : `examples/agence-exemple/1-salles-de-sport/resume.json` ; version réduite aux clés lues : `examples/agence-exemple/2-paysagistes/resume.json`.

| Clé | Type | Lue par | Contenu |
|---|---|---|---|
| `label` | texte | tous | Même valeur que `projet.json` → `niches[].label` |
| `cible_pub` | texte | publicité, formulaire | La cible nommée en tête de publicité : « Salles de sport », « Paysagistes » |
| `unite_longue` | texte | publicité | « essais encadrés tenus dans votre club » |
| `unite_courte` | texte | titre de la publicité | « essais tenus » |
| `unite_manquante` | texte | garantie | « essai manquant », « visite manquante » |
| `volume_garanti` | entier | tous | 40 |
| `remboursement_par_unite` | entier | tous | `offre.prix_ht ÷ volume_garanti`, arrondi |
| `prix_ht` | texte | présentation | Copie de `projet.json` → `offre.prix` (une phrase, pas un nombre) |
| `garantie_courte` | texte | publicité, e-mails, créatives | `offre.garantie_courte`, accordée à l'unité |
| `garantie_phrase` | texte | présentation, e-mails | La phrase complète de la section 7, mot pour mot |
| `promesse_pub` | texte | créatives, e-mails | `{cible_pub} : {volume} {unite_courte} en {duree_jours} jours. {garantie_courte}` |
| `ligne_metier` | texte | publicité, e-mails | Une phrase concrète sur ce que reçoit le client |
| `formulaire_q1_options` | liste de 4 | formulaire | Trois sous-niches puis « Autre » |
| `profils_vises` | liste | tri dans le CRM, appel | Les réponses de Q1 que l'offre vise (la cible et celle d'à côté). Q1 ne bloque personne dans le formulaire |
| `formulaire_q2_options` | liste | formulaire | Les tranches de chiffre d'affaires (copie de `formulaire.tranches_ca` sauf exception) |
| `formulaire_ca_min` | texte | contrôle | La plus basse tranche qualifiée, valeur exacte de `formulaire_q2_options`. Le formulaire coupe par position (`formulaire.tranches_non_qualifiees`) : les deux doivent dire la même chose |
| `bonus` | liste de 4 | présentation | `{nom, probleme, ce_que_fait_l_agent, situation_desiree, prix_ailleurs, source, cout}` |
| `budget_media_min_mois` | entier | présentation, garantie | Budget publicitaire minimum par mois, en euros |

Clés utiles, à remplir aussi : `niche` (nom long), `cible` (l'ICP en une ligne), `unite` (définition complète de l'unité), `duree_jours`, `titres` (5), `formulaire_q1`, `formulaire_q2` (intitulés), `avatar` (3 lignes), `objets_metier`, `reglementation` (liste courte, phrases applicables), `concurrents` (`{nom, promesse, prix, garantie, lien}`), `risque_principal`.

Clés facultatives :
- `texte_pub` (`{body, title, desc, card_title, card}`) remplace le texte de publicité généré, quand le métier impose des mentions ou sort du modèle ;
- `variantes_performance` (liste de deux `id` de `creatives/spec.json`) : les créatives qui reçoivent une variante « performance » ; à défaut, les deux premières de la spec ;
- `variantes_performance_en_pause` (booléen) : crée les publicités « performance » en pause. À mettre à `true` dans toute niche où le paiement au résultat est réglementé (section 8) ; le dirigeant tranche ;
- `creatives_en` (`accent`, `accent_nom`, `scene`, `objets`, `objet_porteur`, `table`, en anglais) et `notifications` (en français) : les détails visuels du métier que lit `build_spec.py`.

Contrôle avant de rendre la main : `python3 scripts/meta_campagne.py <projet> verifier --dry-run` relit chaque `resume.json` sans clé (remboursement × volume ≈ prix, `formulaire_ca_min` au rang qui suit les tranches non qualifiées, `profils_vises` dans Q1, mêmes chiffres dans `promesse_pub` et `garantie_phrase`, clés obligatoires). Puis `textes` montre la publicité qui en sort.
