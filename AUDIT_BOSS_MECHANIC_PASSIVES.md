# AUDIT / SPEC — Passifs de mécanique de boss

> Rédigé par l'agent DATA (2026-07-29) à passer au backend (server-combat).
> **La data ne fait que DÉCLARER. Rien ne s'exécute tant que le moteur combat ne câble pas ces passifs.**
> Source data : `entities/boss_mechanics.json` → `mechanic_passives` (catalog + assignments).

## Contexte

Les 18 bosses ont chacun **1 passif de mécanique signature** (complexité croissante avec le
niveau). Objectif : un boss n'est pas juste un sac de PV avec 4 skills, il a une **règle** qui
change la façon de le tuer (tuer un add d'abord, appliquer 3 debuffs, alterner le type de dégâts…).

Aujourd'hui : **inerte** (comme `level_range` côté presence). Le champ existe, le combat l'ignore.

## Où câbler (server-combat)

- Un **processeur dédié** `boss_mechanic_processor` appelé dans la tick loop (phase 2
  `process_status_effects` ou une phase 2b), qui lit le passif du boss au ROOM_SETUP et applique
  sa règle chaque tick.
- Chargement : au `ContentLoader`, résoudre `boss_mechanics.json mechanic_passives.assignments[<mob_id>]`
  et l'attacher à l'entité boss (comme un composant `BossMechanicComponent`).
- La plupart des types touchent le **pipeline de dégâts** (`damage_calculator.cpp`) : il faut un
  hook "dégâts entrants sur un boss" qui consulte le passif avant d'appliquer.

## Catalogue — contrat d'exécution par type

| Type | Params | Ce que le moteur doit faire |
|---|---|---|
| **enrage_below_hp** | hp_threshold_pct, damage_mult, haste_pct | Quand HP boss < seuil : appliquer un buff permanent (dégâts ×mult, +haste). One-shot, ne se retire pas. |
| **summon_adds** | add_id, count, interval_s, hp_trigger_pct | Spawn `count`×`add_id` toutes les `interval_s` (si >0) et/ou au passage sous `hp_trigger_pct`. Réutilise le spawn monstre existant, team = ENEMIES. |
| **conditional_invuln_add** | guardian_add_id, guardian_count | Le boss est **invulnérable** tant qu'au moins 1 `guardian_add_id` est vivant. Spawn les gardiens au début. Dégâts sur le boss = 0 tant que garde vivant. |
| **debuff_gate** | required_distinct_debuffs, reduced_damage_pct | Compter les debuffs **distincts** actifs sur le boss. Si < N : dégâts subis réduits de `reduced_damage_pct`%. Si >= N : dégâts pleins. |
| **damage_type_ward** | warded_type (physical/magical), reduced_pct, swaps_each_phase | Réduit les dégâts du `warded_type` de `reduced_pct`%. Si `swaps_each_phase` : le type gardé alterne à chaque changement de phase. |
| **reflect_thorns** | reflect_pct | Renvoie `reflect_pct`% des dégâts subis à l'attaquant (post-mitigation). |
| **execute_immunity** | floor_pct, unlock_condition | Le boss ne peut pas descendre sous `floor_pct`% HP tant que `unlock_condition` (ex: `kill_all_adds`) n'est pas rempli. Clamp les dégâts. |
| **phase_shift** | thresholds_pct[], phase_effects[] | Aux seuils de HP, activer l'effet de phase (ward, summon, enrage). Le boss final `the_first_fissure` combine ward physique → ward magique + invocation → enrage. |

## Assignations (18 bosses)

Voir `boss_mechanics.json mechanic_passives.assignments`. Résumé :
- **enrage_below_hp** : alpha_wolf, bandit_warlord(dungeon), fangmark_den
- **summon_adds** : goblin_king, bandit_warlord(mob), spider_queen (spiderlings mob_spider_small), edric_warlord
- **reflect_thorns** : goblin_warlord
- **damage_type_ward** : forest_guardian (physique), inquisitor_edric (magique), avatar_of_the_rift (alterne)
- **debuff_gate** : cursed_champion (2), dark_cultist (3), herald_of_the_fissure (3)
- **conditional_invuln_add** : edric_tower (ritualiste), maw_of_the_abyss (void_spawns)
- **execute_immunity** : abyssal_sovereign
- **phase_shift** : the_first_fissure (boss final lv100, 3 phases)

## Dépendances déjà en place (rien à re-livrer côté data)
- Les adds référencés (`mob_goblin_warior`, `mob_bandit`, `mob_spider_small`, `mob_edric_chosen_*`,
  `mob_void_spawn`, `mob_shard_of_severance`) **existent tous** dans monsters.json (cross-ref validé).
- Les `mechanic_types` / `target_patterns` / `aoe_patterns` de boss_mechanics.json restent valides
  pour les attaques spéciales (déjà là).

## Ordre de livraison conseillé
1. **enrage_below_hp** + **summon_adds** (les plus simples, couvrent 7 bosses, réutilisent buff + spawn existants).
2. **reflect_thorns** + **damage_type_ward** + **debuff_gate** (hooks pipeline de dégâts).
3. **conditional_invuln_add** + **execute_immunity** (invuln conditionnelle).
4. **phase_shift** (le boss final, combine les briques ci-dessus).
