#!/usr/bin/env python3
"""
Migration script: add explicit targeting contract to all skills.

Phase 4 of PLAN_CORRECTION_TARGETING_LOS_V2.md.

For each skill in classes/*/skills.json, adds a "targeting" block:
{
  "selection_mode": "entity" | "tile" | "self",
  "valid_target_team": "enemy" | "ally" | "self" | "any",
  "requires_line_of_sight": bool,
  "bypasses_los": bool,
  "requires_entity_on_target_tile": false,
  "aoe_pattern_id": "single" | "row_3" | etc.
}

Rules:
- selection_mode = "entity" if pattern == "single", else "tile"
  (unless target is "self"/"allies"/"all_allies" -> override)
- requires_line_of_sight = from targeting.json needs_los for the pattern
- bypasses_los = skill.ignore_los OR skill.ignores_frontline
- aoe_pattern_id = skill.pattern (resolved)
- valid_target_team deduced from skill.target field

After migration, old fields (ignore_los, ignores_frontline) are kept
for backward-compat but marked deprecated.

Usage:
  cd kanarion_database
  python scripts/migrate_targeting_contract.py
  python scripts/migrate_targeting_contract.py --dry-run
"""

import json
import os
import sys

DB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETING_JSON = os.path.join(DB_ROOT, "combat", "targeting.json")
CLASSES_DIR = os.path.join(DB_ROOT, "classes")

# Pattern alias resolution (mirrors Skill.resolve_pattern_id in GDScript)
PATTERN_ALIASES = {
    "row": "row_all",
    "row_full": "row_all",
    "col_full": "col_all",
    "column_full": "col_all",
    "column": "col_all",
    "full_map": "all",
    "around_radius_1": "ring_1_center",
}


def load_targeting_patterns():
    """Load needs_los map from targeting.json."""
    with open(TARGETING_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    patterns = data.get("patterns", data)
    needs_los_map = {}
    for name, pdef in patterns.items():
        if isinstance(pdef, dict):
            needs_los_map[name] = pdef.get("needs_los", False)
    return needs_los_map


def resolve_pattern(raw_id):
    return PATTERN_ALIASES.get(raw_id, raw_id)


def deduce_selection_mode(skill, resolved_pattern):
    target = skill.get("target", "enemy")
    if target in ("self",):
        return "self"
    if resolved_pattern != "single":
        return "tile"
    return "entity"


def deduce_target_team(skill):
    target = skill.get("target", "enemy")
    if target in ("self",):
        return "self"
    if target in ("ally", "allies", "all_allies"):
        return "ally"
    if target in ("any", "all"):
        return "any"
    return "enemy"


def migrate_skill(skill, needs_los_map):
    """Add targeting contract to a skill dict. Returns True if modified."""
    if "targeting" in skill:
        return False  # Already migrated

    raw_pattern = skill.get("pattern", "single")
    resolved = resolve_pattern(raw_pattern)
    los = needs_los_map.get(resolved, resolved == "single")
    bypass = skill.get("ignore_los", False) or skill.get("ignores_frontline", False)

    targeting = {
        "selection_mode": deduce_selection_mode(skill, resolved),
        "valid_target_team": deduce_target_team(skill),
        "requires_line_of_sight": los,
        "bypasses_los": bypass,
        "requires_entity_on_target_tile": False,
        "aoe_pattern_id": resolved,
    }

    skill["targeting"] = targeting
    return True


def walk_and_migrate(data, needs_los_map, path=""):
    """Recursively find and migrate skills in nested dicts/lists."""
    count = 0
    if isinstance(data, dict):
        # Is this a skill? Heuristic: has "pattern" + "name_fr"
        if "pattern" in data and "name_fr" in data:
            if migrate_skill(data, needs_los_map):
                count += 1
        for k, v in data.items():
            count += walk_and_migrate(v, needs_los_map, f"{path}/{k}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            count += walk_and_migrate(item, needs_los_map, f"{path}[{i}]")
    return count


def main():
    dry_run = "--dry-run" in sys.argv
    needs_los_map = load_targeting_patterns()
    print(f"Loaded {len(needs_los_map)} patterns from targeting.json")

    total = 0
    for cls_name in sorted(os.listdir(CLASSES_DIR)):
        skills_path = os.path.join(CLASSES_DIR, cls_name, "skills.json")
        if not os.path.isfile(skills_path):
            continue

        with open(skills_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = walk_and_migrate(data, needs_los_map)
        total += count

        if count > 0 and not dry_run:
            with open(skills_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

        status = "DRY-RUN" if dry_run else "WRITTEN"
        print(f"  {cls_name}/skills.json: {count} skills migrated [{status}]")

    print(f"\nTotal: {total} skills migrated")
    if dry_run:
        print("(dry-run mode — no files written)")


if __name__ == "__main__":
    main()
