# Structure des quêtes et des histoires

Statut : proposition (2026-10-03).

## Ce que la data sait déjà faire (`world/quests.json`)

- `type` : `main` (27), `side` (40), `repeatable` (80) ;
- `min_level` ;
- `prerequisites` : une **liste** de quêtes → une quête peut en débloquer plusieurs, et une quête peut
  en attendre plusieurs ;
- `chain_next` : la suite directe ;
- `moral_choice` / `moral_choices` : les choix ;
- `flags`, `auto_accept_on_level`, `auto_accept_on_zone_enter`, `completion_cinematic`.

## Trois niveaux

1. **La quête principale** : le fil. Elle passe par chaque lieu et fait **rencontrer** chaque
   personnage au moment de sa blessure. Tout le monde la fait.
2. **Les histoires** : des chaînes secondaires (`side`), une par personnage ou par paire. Elles ne se
   prennent pas « à tout moment » : chaque étape a **deux portes**,
   - un **niveau minimum** (la géographie : on ne va pas au hameau de la forêt au niveau 8) ;
   - une **étape de la quête principale ou d'une autre histoire** (ce que le joueur sait : on ne
     comprend les Fissures qu'à Rochebourg).
   Une fois la porte ouverte, l'étape reste disponible : le joueur la fait quand il veut.
3. **Les répétables** : contrats, tableau de quêtes.

## Les liens

- La quête principale **ouvre** les histoires (rencontre).
- Une histoire peut en **ouvrir** une autre (Lisa → Bastien : on le rencontre parmi les déserteurs
  qu'elle soigne).
- Les **conséquences remontent** dans la quête principale aux grands moments (Rochebourg, la Tour).
- Une histoire ignorée a aussi un effet (ex. frères Dorn : se taire, puis la vérité éclate à
  Rochebourg).

## Règle de production

**Une histoire = un choix principal = deux issues** ; chaque issue change une ou deux scènes plus
tard, puis les branches se rejoignent. Aucune branche n'est la bonne.

## Exemple : les frères Dorn

| Étape | Type | Porte |
|---|---|---|
| Parler aux frères (Prairie) | principale | lv ~12 |
| Le hameau de la forêt, prévenir ou non | histoire | lv 32 + avoir parlé aux frères |
| Le corps de Matthis (Brigand) | histoire | lv 40 + avoir prévenu |
| Tobias demande pardon (Rochebourg) | histoire | lv 50 + arrivée à Rochebourg (principale) |
| La vérité éclate (si on s'est tu) | principale | arrivée à Rochebourg |

## Besoin technique

- [ ] PNJ visibles ou non selon l'avancement de **chaque joueur** (phasing par joueur).
