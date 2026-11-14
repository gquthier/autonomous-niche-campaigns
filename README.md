<div align="center">

<img src="https://img.shields.io/badge/MARKETING-META%20ADS-1877F2?style=flat-square&labelColor=1877F2&color=0A0A0A" alt="MARKETING · META ADS">

# Autonomous Niche Campaigns

### Une niche de métier, une offre garantie, un ad set qui trie ses prospects tout seul.

L'étude des concurrents, l'offre, la présentation et dix créatives par niche.<br>
Un formulaire instantané qui écarte les petits comptes sans les compter comme prospects.<br>
Une campagne ABO à un ad set par niche, créée en pause, et six e-mails de relance.

**[Installer le skill](#installation)** · **[Lire le playbook](SKILL.md)** · **[Voir le formulaire qualifiant](references/formulaire.md)**

<sub>Claude Code · Bibliothèque publicitaire · offre « Plein 90 » · 10 créatives GPT Image + 2 variantes · logique conditionnelle sur le chiffre d'affaires · ABO un ad set par niche · 6 e-mails contrôlés · simulation complète sans clé · MIT</sub>

<br><br>

<a href="https://bizos.cc"><img src="https://img.shields.io/badge/BizOS-build%20autonomous%20companies-0A0A0A?style=for-the-badge&labelColor=0A0A0A" alt="BizOS — build autonomous companies"></a>

<br><br>

<a href="https://x.com/gauthierthiry"><img src="https://img.shields.io/badge/@gauthierthiry-0A0A0A?style=flat-square&logo=x&logoColor=white" alt="X"></a>
<a href="https://youtube.com/@gquthier"><img src="https://img.shields.io/badge/@gquthier-FF0000?style=flat-square&logo=youtube&logoColor=white" alt="YouTube"></a>

</div>

---

## Ce que ça fait

Vous vendez des rendez-vous ou des demandes qualifiées à des professionnels, et vous voulez tester plusieurs métiers à la fois. Chaque niche demande une offre qui parle son langage, des publicités qui la nomment, un formulaire qui écarte ceux qui ne pourront pas payer, et un suivi. Fait à la main, c'est une semaine par niche, et les prix, les garanties et les chiffres dérivent d'une niche à l'autre.

Ce skill donne à un agent de code le chemin complet, niche par niche, avec des agents en parallèle :

- **Une étude qui sert l'offre.** Marché, argent du métier, réglementation, vocabulaire, et les concurrents relevés dans la Bibliothèque publicitaire Meta. Chaque chiffre porte sa source et son niveau, ou s'écrit « inconnu ».
- **Une offre « Plein 90 ».** Un prix unique payé au départ, le même pour toutes les niches. Un volume un peu au-dessus de ce que le marché promet déjà, une garantie remboursée au prorata, quatre bonus 100 % numériques tenus par des agents IA.
- **Une présentation de 15 pages** façon Hormozi : la preuve avant le prix, la pile de valeur, la garantie mot pour mot.
- **Dix créatives bas de funnel par niche, plus deux variantes.** Lumineuses, la cible nommée en haut, l'offre au centre. Un premier jet des dix consignes GPT Image sort du `resume.json` de la niche. Un contrôle bloque le prix, les mots interdits et les textes non demandés avant de payer une image, puis l'OCR relit chaque image.
- **Un formulaire instantané qui qualifie.** « Vous êtes ? », puis le chiffre d'affaires. Sous le seuil, la personne voit la même page de fin et peut réserver, mais Meta ne compte aucun prospect, et l'algorithme n'apprend pas à chercher ce profil. L'API ne sait pas poser cette logique : un éditeur piloté dans votre navigateur le fait, vérifie chaque règle, puis publie.
- **Une campagne ABO, un ad set par niche.** Ciblage large, Facebook et Instagram, aucune amélioration automatique sur les créatives. Tout est créé en pause, chaque identifiant est noté dès que Meta le renvoie, et une relance ne recrée rien.
- **Six e-mails de relance par niche.** Un contrôle refuse un prix, une fausse urgence, un faux « Re: », et tout nombre introuvable dans les sources de la niche.

L'activation est la dernière étape. Elle exige `--oui`, donc l'accord explicite de la personne.

## Il complète autonomous-meta-launch

[**autonomous-meta-launch**](https://github.com/gquthier/autonomous-meta-launch) lance des pubs vidéo par l'API et bascule une campagne existante vers un formulaire instantané. Il contient aussi le guide pour créer son token Meta avec un agent qui pilote l'écran. Ce dépôt ne le duplique pas : il couvre ce qui vient avant et à côté.

| | autonomous-meta-launch | autonomous-niche-campaigns |
|---|---|---|
| Étude de niche, offre, présentation | Non | Oui |
| Créatives image générées et contrôlées par OCR | Non | Oui, 10 + 2 par niche |
| Pubs vidéo, vertical et horizontal appariés | Oui | Non |
| Formulaire instantané à logique conditionnelle | Non | Oui, par l'éditeur Meta |
| Recopier une campagne existante vers un formulaire | Oui | Non |
| Structure ABO, un ad set par niche | Non | Oui |
| Reprise après interruption | Oui | Oui, `_meta/etat.json` |
| Séquence e-mail contrôlée | Non | Oui |
| Simulation sans clé | Oui | Oui |

## Installation

```bash
git clone https://github.com/gquthier/autonomous-niche-campaigns.git ~/.claude/skills/autonomous-niche-campaigns
```

Puis demandez à Claude Code : *« Lance des campagnes Meta sur trois niches : paysagistes, salles de sport et toiletteurs. Mon offre est dans ce dossier. »*

## Prérequis et clés

- Python 3.9 ou plus. La partie Meta, les contrôles et la simulation n'ont aucune dépendance.
- Pillow pour les aperçus, la finition et les planches (`pip install Pillow`).
- macOS pour deux étapes : l'OCR des créatives (Vision, compilé avec `swiftc`), et l'éditeur de formulaires, qui pilote Arc ou Google Chrome. L'interface de Meta doit être en français.
- Node et Playwright pour rendre les présentations en PDF, avec le script de rendu d'[autonomous-sales-proposal](https://github.com/gquthier/autonomous-sales-proposal).
- Un compte publicitaire avec un moyen de paiement et une Page Facebook.
- Les variables d'environnement, listées dans [`.env.example`](.env.example) :

| Variable | Contenu | Pour |
|---|---|---|
| `META_ACCESS_TOKEN` | Token d'utilisateur système | Campagne, formulaires, publicités |
| `META_AD_ACCOUNT`, `META_PAGE_ID` | Compte `act_...`, Page | Si laissés vides dans `projet.json` |
| `META_INSTAGRAM_ID`, `META_BUSINESS_ID` | Compte Instagram, Business | Facultatifs |
| `KIE_API_KEY` | Clé kie.ai | Créatives GPT Image (environ 18 crédits l'image) |
| `APIFY_TOKEN` | Jeton Apify | Relevé de la Bibliothèque publicitaire, facultatif |

Le token Meta a besoin de `ads_management`, `ads_read`, `business_management`, `leads_retrieval`, `pages_manage_ads`, `pages_read_engagement`, `pages_show_list` et `pages_manage_metadata`. Vous ne l'avez jamais créé ? Suivez [le guide d'autonomous-meta-launch](https://github.com/gquthier/autonomous-meta-launch/blob/main/references/token-meta-computer-use.md).

## Utilisation

Essayez d'abord la simulation, sans clé ni réseau, sur l'exemple fictif : une agence, deux niches, salles de sport et paysagistes.

```bash
cd ~/.claude/skills/autonomous-niche-campaigns
python3 scripts/meta_campagne.py examples/agence-exemple parcours --dry-run
```

```text
### logique
===== Salles de sport
  [à blanc] Club de fitness indépendant → Q2 Quel est votre chiffre d'affaires annuel ?
  ...
  [à blanc] Moins de 150 000 € → Fermer le formulaire → page de fin des non-prospects [aucun prospect]
  [à blanc] 150 000 à 300 000 € → Envoyer le formulaire → page de fin des prospects [prospect]
  ...
### controle
CAMPAGNE Instant Form - ABO | Niches | Novembre 2026 | PAUSED PAUSED | OUTCOME_LEADS
  Agence Exemple | Salles de sport | PAUSED PAUSED | 15 €/j | QUALITY_LEAD ON_AD | ['BE', 'FR'] 25-60 | large : oui | 12 pubs {'ADSET_PAUSED': 12} | sur « IF - Salles de sport » : 12/12
  Agence Exemple | Paysagistes | PAUSED PAUSED | 15 €/j | QUALITY_LEAD ON_AD | ['BE', 'FR'] 25-60 | large : oui | 12 pubs {'ADSET_PAUSED': 12} | sur « IF - Paysagistes » : 12/12
TOTAL : 24 publicités, 24 sur le bon formulaire ; dépense des ad sets actifs : 0 €/jour
```

Relancez la même commande : rien n'est recréé. Les autres contrôles tournent aussi sans clé :

```bash
python3 scripts/meta_campagne.py examples/agence-exemple textes                # le texte de chaque publicité
python3 scripts/meta_campagne.py examples/agence-exemple regles                # la logique de chaque formulaire
python3 scripts/creatives/build_spec.py examples/agence-exemple salles-de-sport --stdout   # premier jet des 10 consignes
python3 scripts/creatives/spec_check.py examples/agence-exemple salles-de-sport            # contrôle avant de payer
python3 scripts/creatives/gen.py examples/agence-exemple salles-de-sport --dry-run         # coût en crédits
python3 scripts/sequences/verifier.py examples/agence-exemple                  # les 18 e-mails de l'exemple
python3 -m unittest discover -s tests
```

En réel, sur votre dossier de travail (hors du dépôt), dans l'ordre :

| Commande | Effet |
|---|---|
| `recherche/adlib.py` puis `digest.py` | Relève et résume les annonces des concurrents |
| `meta_campagne.py verifier` | Contrôle les `resume.json`, le token, le compte, la Page |
| `creatives/build_spec.py`, `spec_check.py` | Écrit puis contrôle les dix consignes d'une niche |
| `creatives/gen.py`, `check.py`, `finish.py` | Génère, relit par OCR, pose le logo, fait la planche |
| `creatives/variantes.py gen\|check\|finish` | Deux variantes « Payé à la performance » par niche |
| `meta_campagne.py textes`, `regles` | Textes et logique à faire valider |
| `meta_campagne.py campagne`, `adsets` | Campagne ABO et un ad set par niche, en pause |
| `meta_campagne.py formulaires`, `logique` | Formulaire de base par l'API, puis logique par l'éditeur |
| `meta_campagne.py images`, `pubs`, `controle` | Publicités dans les ad sets en pause, puis relecture |
| `meta_campagne.py activer --oui` | Active les ad sets, puis la campagne en dernier |
| `sequences/verifier.py` | Contrôle les six e-mails de chaque niche |

L'étude, l'offre et la présentation sont faites par des agents, une niche par agent, en suivant les fichiers de [`references/`](references/). Le détail est dans [le playbook](SKILL.md), les écueils dans [les pièges](references/pieges.md).

## Limites honnêtes

- **Ce dépôt n'a pas été exécuté contre la vraie API Meta sous sa forme publiée.** Il généralise des scripts qui ont réellement créé une campagne ABO, ses ad sets, ses formulaires et plus d'une centaine de publicités en novembre 2026. Sa version publique a été testée en simulation et par des tests unitaires. Commencez par une seule niche.
- **L'éditeur de formulaires dépend de l'interface de Meta.** Il cherche des libellés en français, sur macOS, dans Arc ou Chrome. Il a publié une vingtaine de formulaires en novembre 2026. Si Meta change un écran, il s'arrête sans publier, et il faut adapter les libellés.
- **La simulation imite Meta, elle ne le remplace pas.** Elle valide l'enchaînement, les identifiants, la logique et le décompte. Elle ne dira pas qu'un texte sera refusé par l'examen des publicités.
- **L'OCR des créatives ne tourne que sur macOS.** Ailleurs, regardez chaque image vous-même.
- **L'étude, l'offre et la présentation sont du travail d'agent.** Leur qualité dépend du modèle et des sources trouvées. Les contrôles attrapent les incohérences de chiffres, pas un mauvais choix de niche.
- **Les règles juridiques citées ont été relevées en France en novembre 2026.** La garantie, le rappel téléphonique et le paiement au résultat sont à faire valider par un avocat avant le premier client.
- **L'envoi des e-mails n'est pas fourni.** Le dépôt écrit et contrôle la séquence. Branchez-la sur votre outil d'e-mailing, avec l'arrêt sur réservation ou réponse.
- **Les noms de modèles et les tarifs de kie.ai évoluent.** Vérifiez le modèle dans `scripts/creatives/kie.py` et le solde avant de lancer plusieurs niches.
- **L'exemple est fictif** : agence, niches, prix, volumes, concurrents et e-mails sont inventés pour montrer le format.

## Licence

MIT
