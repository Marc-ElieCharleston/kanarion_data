# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KanarionDB is a JSON-based game database for "Kanarion Online" (a mobile 2D MMORPG) paired with a Next.js web editor for viewing and managing the data.

## Commands

All commands run from the `kanarion-editor/` directory:

```bash
npm run dev      # Start development server (localhost:3000)
npm run build    # Production build
npm run lint     # Run ESLint
```

No test suite is currently configured.

## Architecture

### Structure

The project is a **Next.js 16 (App Router)** web editor in `kanarion-editor/` that reads/writes a JSON database stored in `kanarion-editor/kanarion_database/`.

### Editor Architecture

- **API Routes** (`src/app/api/*/route.ts`): Server-side handlers that read from JSON database
- **Pages** (`src/app/*/page.tsx`): Route pages (classes, stats, effects, patterns, panoplies, skills, loot, systems, equipment-stats, ideas)
- **Components** (`src/components/`): Custom components (Sidebar, AoeGrid, SkillCard, StatsDisplay, etc.)
- **UI Components** (`src/components/ui/`): shadcn/ui primitives (Button, Card, Tabs, Select, Dialog, etc.)
- **Database Utility** (`src/lib/database.ts`): Centralized JSON file I/O with TypeScript interfaces

### Database Structure (`kanarion-editor/kanarion_database/`)

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

## Path Alias

In the editor, `@/*` maps to `./src/*` (configured in tsconfig.json).

## Notes

- Database path in code: `process.cwd()/kanarion_database/` (see `src/lib/database.ts`)
- The `prebuild` script copies the database into the editor directory for production builds
- Some content has bilingual FR/EN text
- Combat balance formulas are complex - review `config/combat.json` before modifying damage calculations
- TypeScript interfaces for database types are in `src/lib/database.ts`
