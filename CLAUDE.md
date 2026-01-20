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

### Two-Part Structure

1. **`kanarion_database/`** - JSON files containing all game data (classes, skills, stats, monsters, items, etc.)
2. **`kanarion-editor/`** - Next.js 16 (App Router) frontend that reads/writes the JSON database

### Editor Architecture (Next.js)

- **API Routes** (`src/app/api/*/route.ts`): Server-side handlers that read from JSON database
  - `GET /api/classes` - All classes with stats
  - `GET /api/classes/[classId]/skills` - Skills for a class
  - `GET /api/effects` - Status effects
  - `GET /api/stats` - Stat definitions
- **Pages** (`src/app/*/page.tsx`): Route pages for classes, stats, effects, patterns
- **Components** (`src/components/`): Reusable UI (Sidebar, AoeGrid, SkillCard, etc.)
- **Database Utility** (`src/lib/database.ts`): Centralized file I/O for JSON read/write operations

### Key Components

- **AoeGrid.tsx**: Visualizes combat patterns on 4x4 grid
- **SkillCard.tsx**: Displays skill details with patterns and VFX
- **Sidebar.tsx**: Navigation with class submenu

### Database Structure

```
kanarion_database/
├── classes/       # 6 base classes (warrior, mage, healer, archer, rogue, artisan)
│                  # Each has skills.json and passives.json
├── combat/        # Targeting system (4x4 grid), Line of Sight mechanics
├── config/        # Combat formulas, monster AI, status effects rules
├── entities/      # Monsters (50+), NPCs, boss mechanics
├── items/         # Equipment, consumables, materials, affixes
├── stats/         # 40+ stat definitions, class base stats, growth rates
├── systems/       # Economy, guilds, achievements, PvP, leaderboards
├── world/         # Zones, quests, maps
└── schemas/       # JSON Schema validation
```

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
- Hard CC: stun, freeze, sleep, petrify, knockdown (diminishing returns on some)
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

- Database path from editor: `../kanarion_database/` (relative)
- Some content has bilingual FR/EN text
- Combat balance formulas are complex - review `config/combat.json` before modifying damage calculations
