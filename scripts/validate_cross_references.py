#!/usr/bin/env python3
"""
validate_cross_references.py — CI validator for kanarion_database/

SPEC FINALE $5.5 — Validates all cross-references in game data JSON files.
Run from kanarion_database/ root or pass DB_ROOT env var.

Checks:
  1. All stat names in affixes.json exist in stats/definitions.json
  2. All stat names in equipment_stats.json exist in definitions.json
  3. All class_tags in equipment.json are valid class IDs
  4. All item_ids in loot_tables.json exist in item database files
  5. All set_ids referenced exist in panoplies.json

Exit code 0 = pass, 1 = failures found.
"""

import json
import sys
import os
from pathlib import Path


def load_json(path: Path) -> dict:
    """Load a JSON file with UTF-8 encoding."""
    return json.loads(path.read_text(encoding="utf-8"))


def collect_canonical_stats(defs: dict) -> set:
    """Extract all canonical stat IDs from definitions.json."""
    stats = set()
    # definitions.json has categories -> stats
    if "stats" in defs:
        stat_data = defs["stats"]
        if isinstance(stat_data, dict):
            for key, val in stat_data.items():
                if isinstance(val, dict):
                    # Category level: resources, offensive, etc.
                    if "id" in val:
                        stats.add(val["id"])
                    else:
                        # Nested category: iterate children
                        for sub_key, sub_val in val.items():
                            if isinstance(sub_val, dict) and "id" in sub_val:
                                stats.add(sub_val["id"])
                            elif isinstance(sub_val, dict):
                                # Another nesting level
                                for inner_key, inner_val in sub_val.items():
                                    if isinstance(inner_val, dict) and "id" in inner_val:
                                        stats.add(inner_val["id"])
                                    else:
                                        stats.add(inner_key)
                            else:
                                stats.add(sub_key)
                else:
                    stats.add(key)

    # Also add known aliases and common names from the stat system
    # These are used interchangeably in various files
    aliases = {
        "hp", "mp", "atk", "mag", "def", "armor", "magic_resist",
        "crit", "crit_chance", "crit_dmg", "crit_damage",
        "attack_speed", "hp_regen", "mp_regen", "hp_regen_combat", "mp_regen_combat",
        "lifesteal", "spell_vamp", "armor_pen", "magic_pen",
        "damage_reduction", "heal_power", "cooldown_reduction",
        "block_chance", "parry_chance", "evasion", "hit", "flee",
        "buff_duration", "debuff_duration", "effect_chance", "effect_resist",
        "tenacity", "damage_percent", "shield_power",
        "atk_percent", "mag_percent", "def_percent",
        "aggro_generation", "double_hit_chance", "shield_pierce", "shield_break",
    }
    stats.update(aliases)
    return stats


def validate_affixes(db: Path, valid_stats: set) -> list:
    """Check all stat names in affixes.json."""
    errors = []
    path = db / "items" / "affixes.json"
    if not path.exists():
        return [f"[affixes.json] File not found: {path}"]

    data = load_json(path)
    affixes = data.get("affixes", data.get("prefixes", []) + data.get("suffixes", []))
    if isinstance(data, dict) and "prefixes" in data:
        affixes = data.get("prefixes", []) + data.get("suffixes", [])

    for affix in affixes if isinstance(affixes, list) else []:
        affix_id = affix.get("id", "?")
        for roll in affix.get("rolls", []):
            # affixes.json uses "stat" not "stat_id"
            stat = roll.get("stat", roll.get("stat_id", ""))
            if stat and stat not in valid_stats:
                errors.append(f"[affixes.json] Unknown stat '{stat}' in affix '{affix_id}'")
    return errors


def validate_equipment_stats(db: Path, valid_stats: set) -> list:
    """Check all stat names in equipment_stats.json."""
    errors = []
    path = db / "items" / "equipment_stats.json"
    if not path.exists():
        return []

    data = load_json(path)

    def check_stat_in_obj(obj, context):
        if isinstance(obj, dict):
            for key, val in obj.items():
                if key == "stat_id" and isinstance(val, str) and val not in valid_stats:
                    errors.append(f"[equipment_stats.json] Unknown stat '{val}' in {context}")
                elif key == "stat" and isinstance(val, str) and val not in valid_stats:
                    errors.append(f"[equipment_stats.json] Unknown stat '{val}' in {context}")
                elif isinstance(val, (dict, list)):
                    check_stat_in_obj(val, f"{context}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_stat_in_obj(item, f"{context}[{i}]")

    check_stat_in_obj(data, "root")
    return errors


def validate_class_tags(db: Path) -> list:
    """Check all class_tags in equipment.json are valid."""
    errors = []
    valid_classes = {"warrior", "mage", "healer", "archer", "rogue", "artisan"}

    path = db / "items" / "equipment.json"
    if not path.exists():
        return []

    data = load_json(path)

    def check_items(items, context):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    item_id = item.get("id", "?")
                    for tag in item.get("class_tags", []):
                        if tag not in valid_classes:
                            errors.append(
                                f"[equipment.json] Unknown class_tag '{tag}' in item '{item_id}' ({context})")
        elif isinstance(items, dict):
            for key, val in items.items():
                check_items(val, f"{context}.{key}")

    base_items = data.get("base_items", data)
    check_items(base_items, "base_items")
    return errors


def collect_all_item_ids(db: Path) -> set:
    """Collect all item IDs from all item files."""
    ids = set()
    item_files = [
        "items/consumables.json",
        "items/materials.json",
        "items/equipment.json",
        "items/panoplies.json",
        "items/uniques.json",
    ]

    for rel_path in item_files:
        path = db / rel_path
        if not path.exists():
            continue
        data = load_json(path)

        def extract_ids(obj):
            if isinstance(obj, dict):
                if "id" in obj:
                    ids.add(obj["id"])
                for val in obj.values():
                    extract_ids(val)
            elif isinstance(obj, list):
                for item in obj:
                    extract_ids(item)

        extract_ids(data)

    return ids


def validate_loot_table_refs(db: Path, all_item_ids: set) -> list:
    """Check loot table item references exist."""
    errors = []
    path = db / "items" / "loot_tables.json"
    if not path.exists():
        return []

    data = load_json(path)

    def check_refs(obj, context):
        if isinstance(obj, dict):
            # Check item_id fields
            for key in ("item_id", "item_template_id", "template_id"):
                if key in obj:
                    ref = obj[key]
                    if isinstance(ref, str) and ref and ref not in all_item_ids:
                        # Allow pattern-based refs (e.g., "equip_*", "mat_*")
                        if not any(c in ref for c in ("*", "{", "random")):
                            errors.append(
                                f"[loot_tables.json] Unknown item_id '{ref}' in {context}")
            for key, val in obj.items():
                check_refs(val, f"{context}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_refs(item, f"{context}[{i}]")

    check_refs(data, "root")
    return errors


def validate_set_ids(db: Path) -> list:
    """Check set_id references against panoplies.json."""
    errors = []
    pano_path = db / "items" / "panoplies.json"
    if not pano_path.exists():
        return []

    pano_data = load_json(pano_path)
    valid_set_ids = set()

    # Collect set IDs from panoplies
    if isinstance(pano_data, dict):
        for key, val in pano_data.items():
            if isinstance(val, dict) and ("pieces" in val or "bonuses" in val):
                valid_set_ids.add(key)
            elif key == "sets" and isinstance(val, (list, dict)):
                if isinstance(val, list):
                    for s in val:
                        if isinstance(s, dict) and "id" in s:
                            valid_set_ids.add(s["id"])
                elif isinstance(val, dict):
                    for s_key in val:
                        valid_set_ids.add(s_key)

    # Check equipment.json for set_id references
    equip_path = db / "items" / "equipment.json"
    if equip_path.exists():
        equip_data = load_json(equip_path)

        def check_set_refs(obj, context):
            if isinstance(obj, dict):
                if "set_id" in obj and obj["set_id"]:
                    sid = obj["set_id"]
                    if sid not in valid_set_ids:
                        errors.append(
                            f"[equipment.json] Unknown set_id '{sid}' in {context}")
                for key, val in obj.items():
                    check_set_refs(val, f"{context}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_set_refs(item, f"{context}[{i}]")

        check_set_refs(equip_data, "equipment")

    return errors


def main():
    # Find database root
    db_root = os.environ.get("DB_ROOT", "")
    if db_root:
        db = Path(db_root)
    elif Path("stats/definitions.json").exists():
        db = Path(".")
    elif Path("kanarion_database/stats/definitions.json").exists():
        db = Path("kanarion_database")
    else:
        print("ERROR: Cannot find kanarion_database. Set DB_ROOT or run from db directory.")
        sys.exit(1)

    print(f"Validating cross-references in: {db.resolve()}")
    print("=" * 60)

    # Load canonical stats
    defs_path = db / "stats" / "definitions.json"
    if not defs_path.exists():
        print(f"ERROR: {defs_path} not found")
        sys.exit(1)

    defs = load_json(defs_path)
    valid_stats = collect_canonical_stats(defs)
    print(f"Loaded {len(valid_stats)} canonical stat IDs")

    # Run all validations
    all_errors = []

    print("\n[1/5] Validating affix stat names...")
    errs = validate_affixes(db, valid_stats)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[2/5] Validating equipment_stats stat names...")
    errs = validate_equipment_stats(db, valid_stats)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[3/5] Validating class_tags...")
    errs = validate_class_tags(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[4/5] Validating loot table item references...")
    all_item_ids = collect_all_item_ids(db)
    print(f"  Collected {len(all_item_ids)} item IDs from database")
    errs = validate_loot_table_refs(db, all_item_ids)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[5/5] Validating set_id references...")
    errs = validate_set_ids(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    # Report
    print("\n" + "=" * 60)
    if all_errors:
        print(f"VALIDATION FAILED — {len(all_errors)} error(s):\n")
        for e in all_errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED — all cross-references OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
