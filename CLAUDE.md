# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KanarionDB (`kanarion_data`) is a JSON-based game database for "Kanarion Online" (a mobile 2D MMORPG). This repo contains **only the JSON data** — the web editor is in a separate repo: [`kanarion-tool`](https://github.com/Marc-ElieCharleston/kanarion-tool).

## Commands

```bash
# Regenerate content hash after editing JSON
./scripts/gen_hash.sh

# Commit (pre-commit hook validates hash)
git add . && git commit -m "feat: add mob_dragon"
```

## Architecture

### Structure

This repo is **pure data** (JSON). No application code.

### Database Structure

- **`_meta/`** - Project metadata, version info, ideas backlog
- **`classes/`** - 6 base classes (warrior, mage, healer, archer, rogue, artisan), each with `skills.json` and `passives.json`
- **`combat/`** - Targeting system (4x4 grid), Line of Sight mechanics
- **`config/`** - Combat formulas (`combat.json`), game constants (`game.json`), monster AI (`monster_ai.json`), status effects rules
- **`entities/`** - Monsters, NPCs, boss mechanics, monster archetypes
- **`items/`** - Equipment, consumables, materials, affixes, panoplies, loot tables
- **`stats/`** - 40+ stat definitions, class base stats, growth rates, status effects
- **`systems/`** - Economy, guilds, achievements, PvP, leaderboards, enhancement, keystones
- **`world/`** - Zones, quests, dungeons, lore

## Game Systems Knowledge

### Combat System
- **Grid**: 4x4 (16 slots, max 10 players per team)
- **Rows**: front, mid_front, mid_back, back (positioning matters for tanks/healers)
- **Type**: Real-time with 2.0s Global Cooldown (GCD), drag-and-drop targeting
- **Line of Sight (LoS)**: Auto-attacks blocked if target has units in front (same column on target's grid)
- **Damage types**: Physical (ATK-based, reduced by armor) and Magical (MAG-based, reduced by magic_resist) - no elemental rock-paper-scissors
- **AOE patterns**: single, row, column, rect, cross, ring, diagonal, chain, random, positional (front_row, back_row, mid_rows), t_pattern, v_pattern, etc.

### Stats System
- 40+ stats across 6 categories: resources, offensive, defensive, precision, support, special
- Bonus types: flat, percent, or both
- Many stats have caps (crit 100%, armor_pen 70%, damage_reduction 75%, CDR 40%, etc.)
- Damage pipeline: base → crit → damage% → penetration → armor/mr → damage_reduction → block/parry → shield → HP → lifesteal/reflect

### Status Effects
- Stacking system: 10% per stack, max 10 stacks (+100%), duration refreshes on reapply
- Hard CC: stun, freeze, sleep, petrify, knockdown
- Soft CC: slow, silence, blind, taunt, root, fear, confusion, disarm
- DoTs: poison (% max HP), bleed (ATK-based), burn (MAG-based) - each has max stacks
- Counter effects: heal_reduction, heal_block, shield_block
- Immunity effects: evasion, invulnerable, untargetable, cc_immune

### Naming Conventions
- Monsters: `mob_*`
- Skills: `skill_*`
- Zones: `zone_*`
- Items: `item_*`, `mat_*`, `cons_*`
- NPCs: `npc_*`

## Notes

- Some content has bilingual FR/EN text (name_en / name_fr)
- Combat balance formulas are complex - review `config/combat.json` before modifying damage calculations
- Content hash in `_meta/version.json` is validated by pre-commit hook — run `./scripts/gen_hash.sh` after edits
- The web editor ([kanarion-tool](https://github.com/Marc-ElieCharleston/kanarion-tool)) reads this data via `DB_ROOT` env var
