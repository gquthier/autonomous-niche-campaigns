# La séquence d'e-mails après le formulaire

Six e-mails par niche, envoyés à la personne qui a rempli le formulaire instantané **sans réserver son étude**. Leur seul but : qu'elle réserve son appel de 30 minutes. Le système d'envoi arrête la séquence dès qu'elle réserve, répond ou écrit STOP. Une entrée `defaut` sert quand la niche est inconnue. La séquence ne part que si la personne a donné son e-mail dans le formulaire, c'est-à-dire seulement pour les prospects qualifiés.

Fichiers, à la racine du projet : `sequences-email/sequence-formulaire.json` (lu par les machines) et `sequences-email/sequences.md` (même contenu, pour la relecture humaine). Rédaction : un agent par lot de niches, après `resume.json` et `analyse.md`. Exemple fictif complet (trois niches dont `defaut`) : `examples/agence-exemple/sequences-email/`.

## Le calendrier

| Code | Quand | Ce que dit l'e-mail |
|---|---|---|
| E-IF-1 | Tout de suite après le formulaire | Accusé de réception, l'objectif dit avec `ligne_metier`, « Dernière étape : choisir votre créneau de 30 minutes, en visio avec moi. », le lien, et « répondez avec deux créneaux qui vous arrangent, je bloque l'un des deux » |
| E-IF-2 | 3 heures après (entre 8 h et 20 h, sinon le lendemain 8 h) | Ce qui se passe pendant l'étude, en cinq points numérotés : d'où viennent ses clients aujourd'hui (les canaux du métier), ce que sa zone peut donner dans l'unité de l'offre, les publicités que font déjà ses confrères, ce que l'agence installerait (de la publicité jusqu'au rendez-vous dans l'agenda), « vous me dites franchement si cela a du sens » |
| E-IF-3 | Lendemain, 10 h | La douleur du métier, dans ses mots, appuyée sur un fait sourcé d'`analyse.md` ; puis ce que l'infrastructure fait contre (un ou deux bonus, concrètement) ; une question courte avant le lien (« On regarde votre zone ensemble ? ») |
| E-IF-4 | J+2, 9 h 30 | L'offre « sans détour » : ce qui est installé, et en combien de temps (`offre.installation`) ; « Notre engagement : » suivi de `garantie_phrase` **mot pour mot** ; la définition de l'unité en une phrase (« Un rendez-vous compte quand… Un absent ne compte pas. ») ; le lien. **Aucun prix** |
| E-IF-5 | J+4, 11 h | L'objection principale de la niche, en objet entre « » (« on m'a déjà promis des adhérents »), et la réponse vraie tirée du tableau des objections d'`analyse.md` |
| E-IF-6 | J+7, 10 h : dernier e-mail | « Dernier message de ma part. » ; le dossier se ferme ; `promesse_pub` en rappel ; « répondez simplement « plus tard » » ; le lien reste ouvert ; « Belle journée, » avant la signature |

L'objet de chaque e-mail parle du métier (« dernière étape pour votre club », « 30 minutes sur les essais de votre club », « 40 essais tenus en 90 jours »), en minuscules au début, 60 caractères au plus.

## La voix

- **Court** : 130 mots au plus, hors pied. Une idée par e-mail.
- **Humain** : écrit par une personne de l'agence, à la première personne pour ce qu'elle fait (« je bloque », « j'estime »), « nous » pour l'agence. Phrases courtes, pas de jargon d'agence, les mots du métier.
- **Vouvoiement**, toujours. Commence par `Bonjour {prenom},` puis une ligne vide.
- **Un seul lien** : `{lien_reservation}`, seul sur sa ligne.
- **Fin fixe** : la signature (`projet.json` → `agence.signature_email`, écrite telle quelle), une ligne vide, `{pied_email}` en dernière ligne. Le dernier e-mail met « Belle journée, » juste avant la signature.
- **Typographie française** : apostrophes typographiques (’), guillemets « » avec espaces, espace avant « : », « ; », « ? ». Aucun point d'exclamation, aucun emoji, aucun guillemet droit.

## Les interdits

Chacun a coûté quelque chose ou exposerait l'agence :

| Interdit | Pourquoi |
|---|---|
| **Un chiffre ou un cas client inventé** | Chaque nombre écrit (en chiffres ou en lettres) doit exister dans `resume.json`, `offre.md`, `analyse.md`, `publicite.md` ou `projet.json` → `offre`. Seule exception : `projet.json` → `sequences.nombres_permis` (par défaut « 30 », la durée de l'étude). Un fait de marché vient d'`analyse.md`, avec sa source |
| **Un prix** | Ni le prix de l'offre, ni « HT », ni « € par mois », ni « par jour », ni le budget publicitaire chiffré. Le prix se donne pendant l'appel. Le montant remboursé par unité manquante est permis, parce qu'il fait partie de `garantie_phrase` |
| **Une fausse urgence** | « places », « limité », « dernière chance », « expire » : faux, donc trompeur |
| **Un faux « Re: »** ou « TR: » dans l'objet | Tromperie sur une conversation qui n'a pas eu lieu |
| **Un livrable qui n'existe pas** | Ni « audit », ni « rapport », ni « PDF », ni « page privée », ni « vous recevrez » : rien n'est envoyé avant l'appel |
| **« Lead »**, « closing », « tunnel » | Le métier ne parle pas comme ça : on dit demande, projet, rendez-vous |
| **La garantie dans d'autres mots** | Quand elle est évoquée, c'est avec `garantie_courte` ou `garantie_phrase`, une fois au plus par e-mail, au moins une fois dans la séquence, jamais dans les six |
| **Les mots interdits du métier** | Ceux de `resume.json` → `reglementation` et de `publicite.md` (audition : « patient » et jamais « gratuit » ; conseillers en patrimoine : aucun conseil ni produit) |

## Le format JSON

```json
{
  "_lire": "Relances après un formulaire instantané Meta rempli sans réservation : six e-mails par niche pour faire réserver l’étude de 30 minutes ; le système arrête la séquence dès une réservation, une réponse ou un STOP, et utilise « defaut » pour une niche inconnue.",
  "etapes": [
    {"code": "E-IF-1", "quand": "Tout de suite après le formulaire"},
    {"code": "E-IF-2", "quand": "3 heures après (entre 8 h et 20 h, sinon le lendemain 8 h)"},
    {"code": "E-IF-3", "quand": "Lendemain, 10 h"},
    {"code": "E-IF-4", "quand": "J+2, 9 h 30"},
    {"code": "E-IF-5", "quand": "J+4, 11 h"},
    {"code": "E-IF-6", "quand": "J+7, 10 h : dernier e-mail"}
  ],
  "niches": {
    "defaut": {"label": "Générique (niche inconnue)", "emails": {"E-IF-1": {"objet": "…", "texte": "…"}, "…": {}}},
    "<clé de niche>": {"label": "<label>", "emails": {"E-IF-1": {"objet": "…", "texte": "Bonjour {prenom},\n\n…\n{lien_reservation}\n\n…\n\nPrénom, Agence\n\n{pied_email}"}}}
  }
}
```

- Les clés de `niches` sont les `cle` de `projet.json` → `niches`, plus `defaut`.
- Chaque e-mail n'a que deux champs : `objet` et `texte`. Les sauts de ligne sont des `\n`.
- **Variables permises, et seulement elles** : `{prenom}` (le système gère un prénom vide), `{lien_reservation}` (le calendrier, avec le suivi de la niche), `{pied_email}` (le bas d'e-mail légal avec le STOP). Aucune variable dans l'objet sauf `{prenom}`.
- `defaut` ne cite aucun volume de niche : seulement ce que dit `projet.json` → `offre`, ou rien de chiffré.
- `sequences.md` reprend tout, niche par niche, chaque e-mail sous un titre `### E-IF-N · <quand>`, l'objet en gras, le texte dans un bloc ` ```text `.

## Contrôle

```bash
python3 scripts/sequences/verifier.py <projet>
```

Il vérifie : toutes les niches du projet et `defaut`, six e-mails chacune, objet et texte ; seulement les trois variables ; un seul lien ; `{pied_email}` en dernière ligne précédé de la signature du projet et d'une ligne vide ; 130 mots au plus ; objet de 60 signes au plus ; aucun mot de `sequences.mots_interdits` ; ni « Re: », ni point d'exclamation, ni emoji, ni prix ; **chaque nombre retrouvé, entier, dans les sources de sa niche** (« 6 » ne se trouve pas dans « 600 000 » ; les numéros de liste en début de ligne ne comptent pas). Un nombre « introuvable » est presque toujours un chiffre inventé ou arrondi : corrige le texte, pas la source. Corrige jusqu'à ce qu'il ne signale plus rien.

Vérifie ensuite toi-même ce qu'il ne lit pas : la typographie, l'objet (minuscule, 60 caractères), `garantie_phrase` mot pour mot dans E-IF-4, la garantie absente d'au moins un e-mail, les mots interdits du tableau ci-dessus, les nombres écrits en lettres.

Puis montre les six e-mails de chaque niche au dirigeant (`sequences.md`). **Aucun envoi avant sa relecture.** L'envoi lui-même (outil d'e-mailing, CRM, arrêt sur réservation ou réponse) n'est pas fourni par ce dépôt : branche le JSON sur l'outil de l'équipe.
