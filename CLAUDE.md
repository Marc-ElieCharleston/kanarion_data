# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
- **`config/`** — Combat formulas (`combat.json`), game constants (`game.json`), monster AI (`monster_ai.json`), skill system (`skill_system.json`), skill templates (`skill_templates.json`), role tags (`roles.json`), monster archetypes, monster skill scaling, status effect rules
- **`entities/`** — Monsters (`monsters.json`), NPCs, boss mechanics, summons (`summons.json`: max 6/team), monster archetypes/variants, healer/support monsters
- **`items/`** — Equipment (10 slots, 5 rarities, T1-T5 scaling), consumables, materials, affixes, panoplies (25 sets with intentional Hebrew names), loot tables, currencies, substat crafting system
- **`stats/`** — 40+ stat definitions, class base stats, growth rates, status effect definitions with IDs (referenced by skills — `stats/status_effects.json` defines effect IDs, while `config/status_effects.json` defines balance rules like durations and stacking)
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

### Passive Structure
- **Per character:** 10 class-specific + 10 common = 20 passives, max level 20 each
- **Effect ops:** `add_percent`, `add_flat`
- **Fields:** `id`, `name_fr`, `name_en`, `max_level`, `description_fr`, `description_en`, `effects[]` (each with `stat`, `op`, `value_per_level`)

### Monster Structure
- **Required fields:** `id`, `name_fr`, `name_en`, `category`, `base_level`, `danger_level`, `tags[]`, `ai_role`, `xp_weight` (0.5-2.0), `gold_weight` (0.0-3.0), `base_stats{}`, `drops[]`
- **Tags catalog:** beast, humanoid, undead, elemental, demon, corrupted, ranged, melee, caster, tank, swarm, elite, boss, assassin, healer, support, artillery
- Loot table `item_id` references must exist in items files (CI validates this)

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

### Status Effects
- Stacking: 10% per stack, max 10 stacks (+100%), duration refreshes on reapply
- Hard CC: stun, freeze, sleep, petrify, knockdown
- Soft CC: slow, silence, blind, taunt, root, fear, confusion, disarm
- DoTs: poison (% max HP), bleed (ATK-based), burn (MAG-based) — each has max stacks
- Counter effects: heal_reduction, heal_block, shield_block
- Immunity effects: evasion, invulnerable, untargetable, cc_immune

## Claude Code on Windows — Known Issues & Workarounds

This project runs on **Windows 11** with Git Bash. Claude Code's Bash tool has specific quirks on this platform. Follow these rules strictly to avoid wasting time on broken commands.

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
