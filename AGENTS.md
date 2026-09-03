# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

KanarionDB (`kanarion_data`) is a JSON-based game database for "Kanarion Online" (a mobile 2D MMORPG). This repo contains **only the JSON data** — no application code. The web editor is in a separate repo: [`kanarion-tool`](https://github.com/Marc-ElieCharleston/kanarion-tool). Both the C++ backend and Godot frontend consume this data as a git submodule (`kanarion-meta/`), pinned to the same commit.

## Commands

```bash
# Regenerate content hash after editing any gameplay JSON
./scripts/gen_hash.sh

# Tag a release (reads version from _meta/version.json, creates db-vX.Y.Z tag)
./scripts/tag_release.sh

# Install pre-commit hook (one-time setup, NOT auto-installed)
cp scripts/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

# Workflow: edit JSON → regenerate hash → commit
./scripts/gen_hash.sh && git add . && git commit -m "feat: add mob_dragon"
```

## Content Hash System

Every gameplay JSON edit requires regenerating `content_hash` in `_meta/version.json` via `gen_hash.sh`. The hash is SHA-256 of all JSON file paths + contents (sorted, deterministic), **excluding** metadata files: `version.json`, `statistics.json`, `index.json`, `changelog.json`, `ideas_to_integrate.json`.

Validation happens at three levels:
- **Pre-commit hook** (local, must be manually installed — see Commands above)
- **CI** (`.github/workflows/validate.yml`) — also validates JSON syntax, cross-reference integrity (loot table item IDs, skill effect IDs), and enforces `version.json` bump on PRs with gameplay changes
- `gen_hash.sh` requires Python in PATH

**Trap:** If `content_hash` is set to a placeholder like `"sha256:merged"`, CI will fail. Always run `gen_hash.sh` to compute the real hash.

## Database Structure

- **`_meta/`** — Version info (`version.json`), roadmap (`ROADMAP.md`), ideas backlog, 15 design suggestions in `suggestions/`
- **`classes/`** — 6 base classes (warrior, mage, healer, archer, rogue, artisan), each with `skills.json` and `passives.json`. Also `common_passives.json` (10 universal passives) and `_classes_index.json` (6 classes x 4 subclasses x 2 tier3 = 48 tier3 specs)
- **`combat/`** — Targeting system (`targeting.json`: 4x4 grid), LoS mechanics, ability ideas
- **`config/`** — Combat formulas (`combat.json`), game constants (`game.json`), monster AI (`monster_ai.json`), skill system (`skill_system.json`), skill templates (`skill_templates.json`), role tags (`roles.json`), monster archetypes, monster skill scaling, **monster scaling model (`monster_scaling_model.json`: derived-stats architecture — see Monster Structure)**, threat tiers (`monster_tiers.json`: xp/aggro)
- **`entities/`** — Monsters (`monsters.json`), NPCs, boss mechanics, summons (`summons.json`: max 6/team), monster archetypes/variants, healer/support monsters
- **`items/`** — Equipment (10 slots, 5 rarities, T1-T5 scaling), consumables, materials, affixes, panoplies (25 sets with intentional Hebrew names), loot tables, currencies, substat crafting system
- **`stats/`** — 40+ stat definitions, class base stats, growth rates, status effect definitions with IDs (`stats/status_effects.json` is the single canonical source for all status effects — definitions, balance rules, durations, stacking, formulas)
- **`systems/`** — Economy, guilds, achievements, PvP, leaderboards, enhancement, keystones (max 1 active, radical gameplay modifiers), Koro cards (cross-class skills, C/B/A/S/SS ranks), encounter stars (0-5 difficulty), boutique/battle pass, daily rewards, social, progression
- **`ui/`** — Icon definitions (`icons.json`: 496 icons with priority/status/category/hint)
- **`world/`** — Zones, quests, dungeons, lore, whispers (found-text), world map

## JSON Conventions

### Bilingual Text (i18n)
- FR is the **source language**; EN is the translation
- Fields: `name_fr` / `name_en`, `description_fr` / `description_en`
- `correction_traduction.md` contains the canonical FR/EN glossary for stats, status effects, and internal terms — internal code terms (e.g. `row_3`, `rect_2x3`) must NEVER appear in player-facing text
- Panoplies' Hebrew names are intentional lore — do not translate
- **Resource:** The universal resource is called **Souffle** (FR) / **Breath** (EN), NOT "Mana". Field key `mp` and `mana_cost` remain as technical abbreviations but all player-facing text uses Souffle/Breath.

### Lore-Aligned Class Naming
The game is Bible-inspired but NOT preachy — dark themes exist (Occultist, Cardmaster) because the message is about love and grace, not avoidance. The lore shows consequences and redemption, not condemnation.

| Old name | New name | Reason |
|----------|----------|--------|
| Soulreaper (Healer) | **Martyr** | Self-sacrifice healing, not blood magic — fits the "no greater love" theme |

Classes kept as-is (game-sounding names, nuanced lore):
- **Occultist** — Studies the Abyss, walks a fine line between mastery and ruin
- **Cardmaster** — Reads probability patterns the Rifts introduced, card visual identity is core to the class (NOT linked to Koros)

Three sources of power in the lore:
1. **Martial mastery** (training, discipline) — Warrior, Archer, Rogue, Artisan
2. **Arcane study** (understanding Rift/Abyss forces, risky path) — Mage (Occultist is the most dangerous)
3. **Sacred gift** (inherited from the Creator's Alliance) — Healer

### Subclass Design Fields
Each subclass in `_classes_index.json` has two design-only fields:
- **`fissure_relation`** (EN) — How the subclass relates to the Fissures/Rifts. Each subclass represents a different response.
- **`souffle_usage`** (EN) — How the subclass channels Breath. Informs the writing style of player-facing descriptions.

These fields are **NOT player-facing**. They are internal design notes used to maintain lore coherence when writing `description`, `lore`, `wiki_intro`, and skill descriptions.

### Le Lien / The Bond
The thematic opposite of the Fissures. Fissures = separation, corruption, isolation. Lien = connection between beings, the Creator's other gift.

**CRITICAL:** Le Lien must NEVER be named as a game system, a stat, or an explicit mechanic. It is a narrative undercurrent woven naturally into descriptions. Examples of natural Lien expression:
- Warlord: "Avec les leurs, ils sont invincibles"
- Martyr: "donner sa vie pour ceux qu'on protège"
- Healer passive "Lien de Vie" / "Life Bond" (already exists)

### Faction System (Level 60)
Players choose a faction at level 60. Subclass lore must NOT lock players into a "good" or "bad" alignment. Descriptions should focus on technique and approach, not morality. The moral dimension comes from the faction choice.

### ID Conventions
| Entity | Prefix | Example |
|--------|--------|---------|
| Monster | `mob_` | `mob_rat` |
| Skill | `skill_<class>_` | `skill_warrior_heavy_strike` |
| Passive (class) | `p_<abbr>_` | `p_war_fortified_resolve` |
| Passive (common) | `p_common_` | `p_common_resilience` |
| Zone | `zone_` | `zone_forest` |
| Item (equipment) | `item_` | `item_iron_sword` |
| Weapon | `wpn_<type>_b<bracket>` | `wpn_sword_b1` |
| Material | `mat_` | `mat_rat_tail` |
| Consumable | `cons_` | `cons_health_potion` |
| NPC | `npc_` | `npc_merchant` |

### Skill Structure
- **Tiers:** `filler` (low CD, always usable), `basic`, `advanced`, `ultimate`
- **Per character:** 15 skills (5 base + 5 subclass + 5 tier3), max 100 skill points, 150 needed to max all (intentional -50 deficit forcing build choices)
- **Skill levels:** 0-10, 1 point each
- **Formula:** `damage = base_power + (scaling_percent% * scaling_stat)`
- **Required fields:** `id`, `name_fr`, `name_en`, `tier`, `target`, `pattern`, `damage_type`, `scaling_stat`, `base_power`, `scaling_percent`, `mana_cost`, `cooldown`, `description_fr`, `description_en`, `tags`
- **Optional fields:** `effect`, `effect_duration`, `buff`, `debuff`, `heal_power`, `shield_value`, `vfx_type`
- Skill `effect`/`buff`/`debuff` values must reference valid IDs in `stats/status_effects.json` (CI validates this)

### Portée d un sort

La portée est portée par le PERSONNAGE, pas par le sort : `config/roles.json` `base_range`, en
distance Manhattan sur le plateau 10x6 (diagonale = 2). Un sort sans champ `range` hérite du
`base_range` de son lanceur. Un `range` explicite est une dérogation, volontairement rare.

Échelle : 2 (warrior et rogue et leurs sous-classes, martyr, blacksmith) | 3 (spellblade, artisan,
alchemist, chef, musician) | 4 (mage et healer et leurs sous-classes hors martyr) | 5 (archer et
ses sous-classes). Depuis le rang 5, cela couvre respectivement 4, 9, 15 et 21 des 30 cases
ennemies.

Deux règles du moteur : une zone SANS `range` explicite est placée à `max(base_range, 5)`
(plancher AOE), et les sorts bénéfiques sur allié sautent entièrement le test de portée.

Nova centrée sur le lanceur : `target: self_and_enemies` (ou un texte disant « autour d elle » en
parlant du lanceur) doit porter `range: 0`. En revanche `target: allies` avec une cible désignée
(« l allié visé ») est centré sur la CIBLE et garde sa portée héritée. Ne jamais trancher sur la
description seule : trois sorts sur neuf étaient des faux positifs le 2026-09-02.

### Passive Structure
- **Per character:** 10 class-specific + 10 common = 20 passives, max level 20 each
- **Effect ops:** `add_percent`, `add_flat`
- **Fields:** `id`, `name_fr`, `name_en`, `max_level`, `description_fr`, `description_en`, `effects[]` (each with `stat`, `op`, `value_per_level`)

### Monster Structure
- **Required fields:** `id`, `name_fr`, `name_en`, `category`, `base_level`, `danger_level`, `tags[]`, `ai_role`, `stat_archetype`, `threat_tier`, `rarity`, `base_xp` (flat XP per kill), `gold_weight` (0.0-3.0), `base_stats{}`, `drops[]`
- **Stats DÉRIVÉES, plus de hand-authoring (pivot 2026-07-31) :** `stat(mob, lvl) = base_lv1[stat_archetype] × curve(lvl) × tier_mult × rarity_mult`. Source de vérité = **`config/monster_scaling_model.json`**. Le tuning des stats à la main par niveau est mort (dérive non-monotone lv60-100). `base_stats{}` reste comme cache/legacy le temps de la transition — le moteur bascule vers la dérivation au spawn (scaler `combat_host`). **Ne plus tuner `base_stats` à la main : ajuster `base_lv1[archetype]`, `tier_multipliers`, `rarity_multipliers`, ou la `level_curve` du modèle.**
- **`stat_archetype` (7)** : tank / brute / assassin / archer / mage / controller / support. Pilote les STATS (ratios lv1 + profil crit). **Distinct de `ai_role`** (IA + kit skills). Split archer (physique) / mage (magique). Mapping 11 `ai_role` → 7 archétypes dans `archetype_consolidation`.
- **`threat_tier` (5)** : fodder / standard / tough / elite / boss (mult hp/atk/def). **`rarity` (4)** : normal / magic / rare / champion (overlay variant, défaut `normal`). Mults dans le modèle. `monster_tiers.json` garde xp_multiplier + aggro ; les mults de STATS vivent dans `monster_scaling_model.json`.
- **Crit « comme les joueurs » :** `crit` / `crit_damage` / `armor_pen` viennent de l'archétype (assassin/archer élevés, tank quasi nul). Le moteur les applique mob→joueur. Ces 3 stats **ne scalent PAS** avec la courbe (taux). Seuls hp/atk/def/mr/mp/speed scalent.
- **Un seul stat offensif `atk`** (pas de `mag`) ; le `damage_type` du skill route vers `def` ou `magic_resist` du JOUEUR.
- **Tags catalog:** beast, humanoid, undead, elemental, demon, corrupted, ranged, melee, caster, tank, swarm, elite, boss, assassin, healer, support, artillery
- Loot table `item_id` references must exist in items files (CI validates this)

### Mercenary Structure (`entities/mercenaries.json`)
Bots IA hires par les joueurs, jouent les classes du jeu en combat (1 par character max v1, persiste 24h Redis cote backend). Reutilises pour bots PvP futurs (juste `source_mode` et `balance_profile` differents).

- **Required fields:** `id`, `archetype_id`, `name_fr`, `name_en`, `class_id`, `level_offset_from_player`, `skill_loadout[]`, `ai_profile`, `balance_profile`, `cost_gold`, `icon`, `description_fr`, `description_en`
- **Optional:** `subclass_id` (null si base class uniquement)
- **ID convention :** `merc_<class>` (ex: `merc_warrior`)
- **Class IDs valides :** warrior / mage / healer / archer / rogue / artisan
- **Skill loadout :** 3-5 skills basiques par classe (filler / basic / advanced). Le serveur les pre-resout au ROOM_SETUP (pas de DataDB lookup en combat). Cross-ref valide par CI : chaque skill_id doit exister dans `classes/<class>/skills.json`
- **Balance profile :** doit exister dans `config/mercenary_balance.json` (ex: `solo_helper_v1`)
- **AI profile :** mappe sur PlayerAI cote combat. Valeurs : warrior / mage / healer / archer / rogue / artisan

**Cost design rule (CTO 2026-05-05) :** Les 6 archetypes de base ont `cost_gold=0` (anti-frustration nouveaux joueurs sans tuto). Augmenter uniquement sur tiers avances post-MVP (ex: `merc_ranger_elite`, `merc_occultist`).

### Mercenary Balance (`config/mercenary_balance.json`)
Profils de balance applique au spawn d'un mercenaire en combat. Format :
```json
{
  "profiles": {
    "solo_helper_v1": {
      "level_offset": -2,
      "damage_multiplier": 0.85,
      "healing_multiplier": 0.95,
      "shield_multiplier": 0.95,
      "hp_multiplier": 0.95,
      "mp_multiplier": 1.0,
      "ai_intelligence_level": 3,
      "aggro_bias": 1.0,
      "uses_high_skill_synergies": false,
      "uses_consumables": false
    }
  }
}
```
**Profils prevus :**
- `solo_helper_v1` (LIVE) : aide solo PvE, plus faible qu'un joueur correct
- `pvp_filler_v1` (FUTURE) : bot PvP, stats ≈ joueur reel (level_offset=0, multipliers=1.0)

### Mercenary Potions (`items/consumables.json`)
Potions dediees au merc (le joueur les boit, l'effet va sur son merc) :
- `cons_hp_potion_merc_small` : `effect_type=heal_merc_hp_flat`, `value=50`
- `cons_mp_potion_merc_small` : `effect_type=restore_merc_mp_flat`, `value=30`

Drops dans `items/loot_tables.json` `common_consumables.drops` chance 5%.

### Familiar Structure (`entities/pets.json`)
Compagnons de combat persistants attaches au joueur. Remplacent le slot mercenaire cote joueur (les mercenaires deviennent un systeme purement serveur pour bots PvP/PvE matchmaking). Voir `world/lore.json` section `les_familiers` pour la fondation narrative (Le Lien, les Ames, le Maitre des Liens). Memoire de design : `project_familiar_system_v1.md`.

- **Required archetype fields :** `id`, `archetype_id`, `name_fr`, `name_en`, `species`, `role`, `stat_template`, `skill_pool[]`, `ai_profile`, `balance_profile`, `icon`, `description_fr`, `description_en`
- **ID convention :** `pet_<species>_<role>` (ex: `pet_rat_tank`)
- **Roles V1 :** attack / tank / heal / utility (4 roles, 1 espece rat V1)
- **Skill pool :** 6 skills par role dans `skills/pet_skills.json` (24 total). Au loot/invocation, le serveur tire aleatoirement N skills du pool selon le slot count (no duplicates). Cross-ref CI : chaque `skill_id` du `skill_pool` doit exister dans `skills/pet_skills.json`.
- **Stat template :** doit exister dans `config/pet_balance.json` `stat_templates` (4 templates V1 : `pet_attack_v1`, `pet_tank_v1`, `pet_heal_v1`, `pet_utility_v1`)
- **Balance profile :** doit exister dans `config/pet_balance.json` `profiles` (V1 : `pet_companion_v1`)
- **AI profile :** mappe sur PetAI cote combat. Valeurs V1 : `pet_attack_v1` / `pet_tank_v1` / `pet_heal_v1` / `pet_utility_v1`

**Slot progression (level-based) :** 2 slots lv1 → 3 lv20 → 4 lv50 → 5 lv100. Configuration dans `config/pet_balance.json` `slot_progression.by_level`.

**Rarete = stat multiplier seul (V1) :** commun ×1.00 / rare ×1.03 / epique ×1.06 / legendaire ×1.10. Configuration dans `config/pet_balance.json` `rarity_multipliers`. Pas de bonus loot, pas de slot bonus, pas de passif rarete-dependant.

### Familiar Skills (`skills/pet_skills.json`)
Pool de 24 skills (6 par role). Phase 3 Option A canonical (`stacks_to_apply` sur effets de `canonical_grid`, `value`/`duration` uniquement sur effets non-canonical comme stun/taunt/cleanse).

- **ID convention :** `skill_pet_<role>_<name>` (ex: `skill_pet_attack_pounce`)
- **Required fields :** identiques a un skill classe (id, name_fr/en, tier, target, pattern, damage_type, scaling_stat, base_power, scaling_percent, mana_cost, cooldown, description_fr/en, tags, targeting)
- **Specifiques pet :** `source_scope: "PET"`, `pet_role: <role>` (attack/tank/heal/utility)

### Familiar Souls (`pets/pet_souls.json`)
Items tradeable a l'HDV qui contiennent le potentiel d'un familier (rarete + role) sans son experience. Une Ame ne devient un familier qu'apres invocation chez le Maitre des Liens. Une fois invoquee, le familier est lie au compte du buyer et ne peut plus etre cede.

- **ID convention :** `pet_soul_<rarity>_<role>` (16 archetypes V1 : 4 raretes × 4 roles)
- **Required fields :** `id`, `name_fr`, `name_en`, `description_fr`, `description_en`, `rarity`, `role`, `item_type: "pet_soul"`, `summon_archetype_id`, `summon_level_gate`, `stat_multiplier`, `tradeable: true`, `hdv_listable: true`
- **Cross-ref CI :** `summon_archetype_id` doit exister dans `entities/pets.json` `pets[].id`
- **Level gate par rarete :** commun lv1, rare lv20, epique lv40, legendaire lv60 (anti-abuse pay-to-win)

**Anti-abuse stack 4 couches :**
1. Reset level=1 a l'invocation (pas de transfert de progression)
2. Reroll skills a l'invocation (pas de transfert de loadout)
3. Level gate par rarete (anti-P2W lv1+legendaire)
4. Level cap to owner en combat (`pet_balance.json` `level_cap_to_owner: true`)

### Familiar Potions & Reroll Items (`items/consumables.json`)
Potions familier (le joueur les utilise via inventaire, l'effet va sur son familier actif) :
- `cons_hp_potion_pet_small` : `effect_type=heal_pet_hp_flat`, `value=50`
- `cons_mp_potion_pet_small` : `effect_type=restore_pet_mp_flat`, `value=30`

Items de reroll skill (rerolls des skills aleatoires deja attribues) :
- `cons_pet_skill_reroll_one` : `effect={type: "pet_reroll_skill", target: "random_one"}` (uncommon, 200g)
- `cons_pet_skill_reroll_choose` : `effect={type: "pet_reroll_skill", target: "player_choice"}` (rare, 600g)

### Familiar Binding Modes (lore + technique)
Deux modes coexistent V1 :
- **`character`** : seul cas = rat du tutoriel (lien narratif specifique au perso liberant la creature des Fissures). Jamais transferable, ni au compte ni a un autre perso. Voir `world/lore.json` `les_familiers.le_tutoriel_du_rat`.
- **`account`** : tous les autres familiers (drops, events, achats HDV, V3 taming). Stockes au niveau compte, accessibles a tous les persos via le Maitre des Liens (PNJ V2). Une fois invoque, jamais transferable hors du compte.

**Anti-pattern interdit :** convertir un familier `character` en `account` ou vice-versa. Le mode est immutable a la creation. Voir `entities/pets.json` `_meta.instance_fields.immutable_after_summon`.

## Game Systems Knowledge

### Combat System
- **Grid:** 4x4 (16 slots, max 10 players per team)
- **Rows:** front, mid_front, mid_back, back (positioning matters for tanks/healers)
- **Type:** Real-time with 2.0s Global Cooldown (GCD), drag-and-drop targeting
- **Line of Sight (LoS):** Auto-attacks blocked if target has units in front (same column on target's grid)
- **Damage types:** Physical (ATK-based, reduced by armor) and Magical (MAG-based, reduced by magic_resist) — no elemental rock-paper-scissors
- **AOE patterns:** single, row, column, rect, cross, ring, diagonal, chain, random, positional (front_row, back_row, mid_rows), t_pattern, v_pattern, etc.
- **Damage pipeline:** base -> crit -> damage% -> penetration -> armor/mr -> damage_reduction -> block/parry -> shield -> HP -> lifesteal/reflect

### Stats System
- 40+ stats across 6 categories: resources, offensive, defensive, precision, support, special
- Bonus types: flat, percent, or both
- Stat caps: crit 100%, armor_pen 70%, damage_reduction 75%, CDR 40%, etc.

### Status Effects — Option A (CTO 2026-04-30, contrat strict)

**Regle absolue.** Pour les `stat_modifier` stackables generiques listes dans `stats/status_effects.json` `_meta.canonical_grid`, la puissance d'un buff/debuff vient UNIQUEMENT du nombre de stacks appliques. Les champs `value` et `value_override` sont INTERDITS sur ces effets.

**Skills doivent utiliser :**
```json
{ "effect": "armor_down", "stacks_to_apply": 3, "duration": 8 }
```
**JAMAIS :**
```json
{ "effect": "armor_down", "value": 25, "duration": 8 }
```

**Mapping value originale → stacks_to_apply** (regle de migration) :
- `value` proche de `value_per_stack × N` → `stacks_to_apply: N`
- Exemple : `armor_down value=25` avec `value_per_stack=5` → `stacks_to_apply: 5`
- Si la value souhaitee depasse le total_max canonique, c'est une violation : creer un nouvel `effect_id` dedie (non-stackable custom).

**Grille canonique.** Voir `stats/status_effects.json` `_meta.canonical_grid` pour la table complete. Resume :
- Offensifs (atk/mag/damage_percent/accuracy) : 5%/stack × 5 = ±25%
- Crit chance : 5%/stack × 3 = ±15%. Crit damage : 10%/stack × 3 = ±30 (additif sur 150% base)
- Defensifs (armor/MR) : 5%/stack × 5 = ±25%
- damage_reduction : 5%/stack × 3 = ±15% (multiplicatif post-armor donc effet fort)
- evasion : 3%/stack × 5 = ±15%
- Tempo (atk_speed/cast_speed) : 5%/stack × 5 = ±25%
- Heal power : 5%/stack × 5 = ±25%. Heal reduction : 15%/stack × 3 = -45%
- DoT (bleed/burn/chill/poison/corruption/toxin) : 1 stack = formule existante. toxin reduit a 5 stacks max (etait 10).

**Comportement overflow stack.** Si `stacks_to_apply + current_stacks > max_stacks`, on applique ce qu'on peut jusqu'au cap, les stacks excedentaires sont perdus. Duree refresh selon `refresh_on_apply`.

**Enforcement strict (pas de dual-mode legacy) :**
- **CI** (`validate.yml`) : fail si une skill utilise `value`/`value_override` sur un effet de `canonical_grid`
- **Backend** (`SkillResolver` au load combat) : fail-fast, le combat service ne demarre pas si une skill viole le contrat
- **Runtime** : `apply_effect()` n'accepte plus `value_override` pour ces effets

**Exceptions ou `value` reste autorise :**
- Shields (absorb amount via `shield_value`)
- Heal flat ponctuels (`heal_power` skill field)
- DoT/HoT scaling (`caster_max_hp`, declare dans runtime de l'effet)
- Effets non-stackables custom listes dans `_meta.canonical_grid.non_stackable_special_effects` (shield_wall, hunter_mark, assassin_mark, guardian_breath, etc.)

**Anti-pattern critique :** ne JAMAIS reintroduire `value` libre pour donner une variante de classe a un effet stackable. Si le Hunter veut un mark plus fort que le mark generique, creer `hunter_mark` comme effect_id distinct, pas `marked` avec `value=15`. Le cumul `vulnerable + exposed + marked + berserk` ne doit pas atteindre +100% damage_taken en pratique normale (voir `_meta.rules_anti_amplification_chain`).

**Categories non-stackables (regle inchangee) :**
- Hard CC : stun, freeze, sleep, petrify, knockdown (refresh, max 1)
- Soft CC : slow, silence, blind, taunt, root, fear, confusion, disarm
- DoTs : poison (% max HP), bleed (ATK-based), burn (MAG-based) — chacun avec son max_stacks
- Counter effects : heal_reduction, heal_block, shield_block
- Immunity : evasion, invulnerable, untargetable, cc_immune

### Skill Description Conventions (alignment Option A)

Les `description_fr` / `description_en` reflètent la VALEUR EFFECTIVE appliquée, pas le nombre de stacks. Le joueur pense en % pour les buffs, en stacks pour les DoTs.

**Buffs / debuffs canonical (stat_modifier avec stacks_to_apply) :**
- Annoncer le % effectif (`stacks_to_apply × value_per_stack`)
- `atk_up stacks_to_apply: 5` (5×5%) → "+25% ATK"
- `damage_reduction_up stacks_to_apply: 3` (3×5%) → "+15% réduction de dégâts"
- `def_down stacks_to_apply: 4` (4×5 flat) → "-20 DEF" (PAS "-20%", def est flat)
- Optionnel : ajouter "(max +25%)" pour expliciter le cap quand utile (ex: Frenzy, War Anthem)

**DoTs (bleed/burn/chill/poison/corruption/toxin) :**
- Annoncer en stacks ET nom de l'effet (icônes en jeu affichent le compteur)
- `bleed stacks_to_apply: 1` → "Applique 1 charge de Saignement (max 3)"
- `toxin stacks_to_apply: 2` → "2 charges de Toxine (max 5)"
- Ne PAS annoncer en dégâts absolus (varie avec ATK/MAG)
- "(max N)" optionnel sur ultimate qui appliquent déjà le max, recommandé sur fillers

**Effets custom non-stackables nommés (iron_stance_shield, hunter_mark, steady_aim_amplifier, etc.) :**
- Souligner comme effet nommé avec parenthèse explicative
- "Active Posture de Fer (-50% dégâts subis) pendant 5s"
- "Applique Marque du Chasseur (+15% dégâts subis) pendant 8s"
- "Active Visée Stable (+50 dégâts critiques) pendant 5s"
- Le joueur doit comprendre que c'est un buff distinct avec icône/durée propre, pas un buff générique

**Scaling per-level — ce qui reste vs ce qui a disparu :**
- ✅ GARDER `(+X%/niv)` sur le scaling damage (`percent_per_level` sur `scaling_percent`)
- ✅ GARDER `(+X.Xs/niv)` sur la durée (`duration_per_level`)
- ✅ GARDER `(+X/niv)` sur le scaling heal (`heal_scaling_per_level`, `power_per_level`)
- ❌ RETIRER `(+X%/niv)` sur les valeurs d'effets canonical_grid (`value_per_level` supprimé en Phase 2 Option A)

**Unités (canonical_grid) :**
- **Percent** : atk_up/down, mag_up/down, damage_percent_up/down, accuracy_up/down, crit_chance_up/down, armor_up/down, magic_resist_up/down, damage_reduction_up/down, evasion_up/down, atk_speed_up/down, cast_speed_up/down, heal_power_up/down, heal_received_down, heal_reduction, crit_resistance_down, vulnerable, exposed, marked, berserk, lifesteal
- **Flat** : `def_up/down` (5 par stack, PAS %)
- **Crit damage** : additif sur 150% base (`crit_damage_up`: +10/stack additif, PAS %)
- **HoT** : `heal_over_time` = 1% maxHP/s par stack (scaling=max_hp)

**Skills multi-effets :**
- Lister tous les effets avec leurs valeurs effectives
- Frenzy (atk_up s.5, atk_speed_up s.4, def_down s.3) → "+25% ATK et +20% vitesse d'attaque pendant 10s. -15% DEF pendant 8s."
- Si deux effets canonical s'additionnent (Marqué + Exposé), expliciter le total : "(+20% dégâts subis cumulés)"

**Terminologie :**
- "Mana" INTERDIT en texte joueur. Utiliser "Souffle" (FR) / "Breath" (EN). Les clés techniques `mp` et `mana_cost` restent.
- Codes internes (`row_3`, `rect_2x2`, noms de patterns) JAMAIS dans les descriptions. Utiliser "ligne", "zone 2x3", "diagonale", etc.
- Voir `correction_traduction.md` pour le glossaire FR/EN canonique.

**Style :**
- Bilingue : FR source, EN traduction. Synchroniser les deux.
- Pas de tirets cadratins (—). Utiliser virgules, points, parenthèses.
- Garder l'intro narrative (lore) avant la partie mécanique (pattern existant).
- Pour DoTs avec multi-types (Brûlure + Frisson), éviter de cumuler "(max 3)" pour ne pas alourdir.

**Anti-patterns descriptions à corriger systématiquement :**
- "(+1%/niv)" sur un effet canonical_grid (le scaling per-level n'existe plus pour ces effets)
- "-25% DEF" alors que def est flat (écrire "-25 DEF")
- "Vulnérable (-15% résistances)" alors que vulnerable = +X% dégâts subis (écrire "+15% dégâts subis")
- "+50% dégâts critiques" pour `crit_damage_up` (additif, écrire "+50 dégâts critiques")
- Description annonçant +30% alors que canonical max = +25% (Frenzy avant migration : atk_up cap à +25%)

## Codex on Windows — Known Issues & Workarounds

This project runs on **Windows 11** with Git Bash. Codex's Bash tool has specific quirks on this platform. Follow these rules strictly to avoid wasting time on broken commands.

### Bash Tool Behavior

| Issue | Detail |
|-------|--------|
| **Output swallowed** | Many commands return empty stdout/stderr even on success. `pwd`, `echo`, `ls` are unreliable. |
| **Exit code 1 on success** | The Bash tool often reports `exit code 1` for commands that actually succeeded. Don't retry blindly — check the actual state. |
| **HEREDOC syntax broken** | `$(cat <<'EOF'...)` and multi-line heredocs **do not work**. Always use simple inline `-m "message"` for git commits. |
| **Piped commands fragile** | Complex pipelines (`find | sort | while read`) may silently fail or return no output. |

### Shell Scripts (.sh) — CRLF Problem

All `.sh` files have CRLF line endings (`\r\n`) because Git checks them out on Windows. Bash cannot execute them directly:
```
scripts/gen_hash.sh: line 6: $'\r': command not found
```

**Never run shell scripts directly** (`bash scripts/gen_hash.sh` → FAILS). Use the Python workaround below.

### gen_hash.sh — Use Python Replacement

The `gen_hash.sh` script **does not work** on this Windows setup (CRLF + `dirname` issues). Use this pure-Python equivalent instead:

```bash
python -c "
import hashlib, json, os, datetime
os.chdir(r'C:\Users\Charl\Documents\Kanarion Online\kanarion_database')
exclude_files = {'./_meta/version.json', './_meta/statistics.json', './_meta/index.json', './_meta/changelog.json', './_meta/ideas_to_integrate.json'}
exclude_dirs = {'.git', 'kanarion-editor', 'scripts'}
json_files = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for f in files:
        if f.endswith('.json'):
            path = os.path.join(root, f).replace(os.sep, '/')
            if path not in exclude_files:
                json_files.append(path)
json_files.sort()
content = b''
for fp in json_files:
    content += (fp + '\n').encode()
    with open(fp, 'rb') as fh:
        content += fh.read()
h = hashlib.sha256(content).hexdigest()
with open('_meta/version.json', 'r', encoding='utf-8') as f:
    v = json.load(f)
v['content_hash'] = f'sha256:{h}'
v['last_updated'] = datetime.date.today().isoformat()
with open('_meta/version.json', 'w', encoding='utf-8') as f:
    json.dump(v, f, indent=2, ensure_ascii=False)
    f.write('\n')
print(f'Updated content_hash: sha256:{h}')
"
```

### Git Commands — What Works

**Works reliably:**
```bash
git status
git add <file1> <file2>
git commit -m "short message"
git push
git push origin master
git log --oneline -5
git diff --name-only
git rm --cached <file>
```

**Does NOT work (avoid):**
```bash
# HEREDOC commit messages — BROKEN
git commit -m "$(cat <<'EOF'
message
EOF
)"

# Complex pipelines — OUTPUT SWALLOWED
git log --oneline | head -5

# Interactive flags — NOT SUPPORTED
git add -i
git rebase -i
```

### Commit Workflow (Correct Sequence)

```bash
# 1. Regenerate hash (Python — NOT gen_hash.sh)
python -c "... (see above) ..."

# 2. Stage files explicitly
git add _meta/version.json classes/warrior/skills.json  # list specific files

# 3. Commit with simple -m
git commit -m "feat(data): add new warrior skills"

# 4. Push if requested
git push origin master
```

### When Bash Fails — Use Python as Fallback

For any command where the Bash tool returns empty output or unexplained exit code 1, wrap it in Python:
```bash
python -c "
import subprocess
r = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(r.stdout)
print(r.stderr)
"
```

## Notes

- Review `config/combat.json` before modifying damage calculations — formulas are complex
- The web editor reads this data via `DB_ROOT` env var
- `gen_hash.sh` uses `sha256sum` (Linux/Git Bash) and `python` — both must be available but **the script itself fails on Windows due to CRLF** — use the Python replacement above
- On Windows, shell scripts require CRLF stripping before execution — prefer Python alternatives
