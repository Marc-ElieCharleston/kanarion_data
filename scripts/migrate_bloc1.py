#!/usr/bin/env python3
"""
Bloc 1 — Migration Script (one-shot, jetable)
Migrates legacy custom fields to canonical effects[] format.

Strategy:
- If effects[] already has the matching entry: REMOVE legacy field only
- If effects[] exists but without the entry: APPEND to effects[]
- If effects[] does not exist: CREATE effects[] array

This script modifies files IN PLACE. Review the diff before committing.
Run: python scripts/migrate_bloc1.py [--dry-run]
"""

import json
import glob
import sys
import os
import copy

DRY_RUN = "--dry-run" in sys.argv

# ============================================================
# DEFAULT DURATIONS (from existing effects[] patterns in the codebase)
# ============================================================
DEFAULT_DOT_DURATIONS = {
    "bleed": 5.0,    # 4-6s in existing skills, 5s most common
    "burn": 6.0,     # standard medium debuff
    "toxin": 6.0,    # standard medium debuff
    "corruption": 8.0,  # longer (dark magic)
    "chill": 6.0,    # standard medium debuff
}

# ============================================================
# MIGRATION STATS
# ============================================================
stats = {
    "files_modified": 0,
    "skills_modified": 0,
    "fields_removed": 0,
    "effects_added": 0,
    "effects_already_present": 0,
}


def has_effect(skill, stat):
    """Check if effects[] already has an entry with this stat."""
    for e in skill.get("effects", []):
        if isinstance(e, dict) and e.get("stat") == stat:
            return True
    return False


def ensure_effects(skill):
    """Ensure skill has an effects[] array."""
    if "effects" not in skill:
        skill["effects"] = []


def add_effect(skill, effect_entry):
    """Add an effect entry to the skill's effects[] array."""
    ensure_effects(skill)
    skill["effects"].append(effect_entry)
    stats["effects_added"] += 1


def remove_field(skill, field):
    """Remove a legacy field from the skill."""
    if field in skill:
        del skill[field]
        stats["fields_removed"] += 1


# ============================================================
# MIGRATION RULES
# ============================================================

def migrate_dot_stacks(skill, sid):
    """Migrate applies_X_stacks -> effects[] debuff."""
    modified = False
    for dot_type, legacy_key in [
        ("bleed", "applies_bleed_stacks"),
        ("burn", "applies_burn_stacks"),
        ("toxin", "applies_toxin_stacks"),
        ("corruption", "applies_corruption_stacks"),
        ("chill", "applies_chill_stacks"),
    ]:
        if legacy_key not in skill:
            continue
        value = skill[legacy_key]
        if has_effect(skill, dot_type):
            # Coexistence: effects[] already has it, just remove legacy
            print(f"  {sid}: {legacy_key}={value} -> already in effects[], removing legacy")
            stats["effects_already_present"] += 1
        else:
            # Legacy only: create effects[] entry
            duration = DEFAULT_DOT_DURATIONS.get(dot_type, 6.0)
            entry = {"type": "debuff", "stat": dot_type, "value": value, "duration": duration}
            add_effect(skill, entry)
            print(f"  {sid}: {legacy_key}={value} -> added effects[] {{type:debuff, stat:{dot_type}, value:{value}, duration:{duration}}}")
        remove_field(skill, legacy_key)
        modified = True
    return modified


def migrate_buffs_simple(skill, sid):
    """Migrate buff_value_*, buff_scaling_percent, defense_reduction -> effects[]."""
    modified = False

    # buff_value_atk + buff_value_speed (berserker_frenzy has both)
    if "buff_value_atk" in skill:
        value = skill["buff_value_atk"]
        duration = skill.get("buff_duration", 8.0)
        if not has_effect(skill, "atk_up"):
            add_effect(skill, {"type": "buff", "stat": "atk_up", "value": value, "duration": duration})
            print(f"  {sid}: buff_value_atk={value} -> added effects[] atk_up")
        else:
            stats["effects_already_present"] += 1
        remove_field(skill, "buff_value_atk")
        modified = True

    if "buff_value_speed" in skill:
        value = skill["buff_value_speed"]
        duration = skill.get("buff_duration", 8.0)
        if not has_effect(skill, "atk_speed_up"):
            add_effect(skill, {"type": "buff", "stat": "atk_speed_up", "value": value, "duration": duration})
            print(f"  {sid}: buff_value_speed={value} -> added effects[] atk_speed_up")
        else:
            stats["effects_already_present"] += 1
        remove_field(skill, "buff_value_speed")
        modified = True

    if "buff_value_damage_percent" in skill:
        value = skill["buff_value_damage_percent"]
        duration = skill.get("buff_duration", 8.0)
        if not has_effect(skill, "damage_percent_up"):
            add_effect(skill, {"type": "buff", "stat": "damage_percent_up", "value": value, "duration": duration})
            print(f"  {sid}: buff_value_damage_percent={value} -> added effects[] damage_percent_up")
        else:
            stats["effects_already_present"] += 1
        remove_field(skill, "buff_value_damage_percent")
        modified = True

    if "buff_value_flat_dr" in skill:
        value = skill["buff_value_flat_dr"]
        duration = skill.get("buff_duration", 8.0)
        if not has_effect(skill, "flat_dr_up"):
            add_effect(skill, {"type": "buff", "stat": "flat_dr_up", "value": value, "duration": duration})
            print(f"  {sid}: buff_value_flat_dr={value} -> added effects[] flat_dr_up")
        else:
            stats["effects_already_present"] += 1
        remove_field(skill, "buff_value_flat_dr")
        modified = True

    if "buff_scaling_percent" in skill:
        value = skill["buff_scaling_percent"]
        duration = skill.get("buff_duration", 8.0)
        if not has_effect(skill, "atk_up"):
            add_effect(skill, {"type": "buff", "stat": "atk_up", "value": value, "duration": duration})
            print(f"  {sid}: buff_scaling_percent={value} -> added effects[] atk_up")
        else:
            stats["effects_already_present"] += 1
        remove_field(skill, "buff_scaling_percent")
        modified = True

    if "defense_reduction" in skill:
        value = skill["defense_reduction"]
        duration = skill.get("debuff_duration", 6.0)
        if not has_effect(skill, "def_down"):
            add_effect(skill, {"type": "debuff", "stat": "def_down", "value": value, "duration": duration})
            print(f"  {sid}: defense_reduction={value} -> added effects[] def_down")
        else:
            stats["effects_already_present"] += 1
        remove_field(skill, "defense_reduction")
        remove_field(skill, "defense_reduction_per_level")
        modified = True

    # Clean up buff_duration if we consumed it
    # (only if no other legacy field still needs it)
    # We do NOT remove buff_duration here — that happens in Bloc 5 cleanup

    return modified


def migrate_hot(skill, sid):
    """Migrate hot_percent/hot_base -> effects[] heal_over_time."""
    modified = False

    if "hot_percent" in skill or "hot_base" in skill:
        if has_effect(skill, "heal_over_time"):
            print(f"  {sid}: HoT fields -> already in effects[], removing legacy")
            stats["effects_already_present"] += 1
        else:
            # Build the HoT effect entry
            entry = {"type": "buff", "stat": "heal_over_time"}

            if "hot_percent" in skill:
                entry["value"] = skill["hot_percent"]
                entry["scaling"] = "max_hp"
            elif "hot_base" in skill:
                entry["value"] = skill["hot_base"]
                if "hot_scaling_stat" in skill:
                    entry["scaling"] = skill["hot_scaling_stat"]
                if "hot_scaling_percent" in skill:
                    entry["value"] = skill["hot_scaling_percent"]
                    if "hot_scaling_stat" in skill:
                        entry["scaling"] = skill["hot_scaling_stat"]

            if "hot_duration" in skill:
                entry["duration"] = skill["hot_duration"]
            else:
                entry["duration"] = 8.0  # default medium

            if "hot_duration_per_level" in skill:
                entry["duration_per_level"] = skill["hot_duration_per_level"]

            add_effect(skill, entry)
            print(f"  {sid}: HoT -> added effects[] heal_over_time (value={entry.get('value')}, duration={entry.get('duration')})")

        # Remove all HoT legacy fields
        for f in ["hot_percent", "hot_base", "hot_duration", "hot_scaling",
                   "hot_scaling_percent", "hot_scaling_stat",
                   "hot_percent_per_level", "hot_duration_per_level",
                   "hot_duration_scaling", "hot_amplify_percent"]:
            remove_field(skill, f)
        modified = True

    # Allies HoT (composite skill — allies_hot_*)
    if "allies_hot_base" in skill or "allies_hot_scaling_percent" in skill:
        entry = {"type": "buff", "stat": "heal_over_time", "target": "allies"}
        if "allies_hot_base" in skill:
            entry["value"] = skill["allies_hot_base"]
        if "allies_hot_scaling_percent" in skill:
            entry["value"] = skill["allies_hot_scaling_percent"]
            entry["scaling"] = "mag"
        if "allies_hot_duration" in skill:
            entry["duration"] = skill["allies_hot_duration"]
        else:
            entry["duration"] = 8.0

        if not has_effect(skill, "heal_over_time"):
            add_effect(skill, entry)
            print(f"  {sid}: allies HoT -> added effects[] heal_over_time (target=allies)")
        else:
            stats["effects_already_present"] += 1

        for f in ["allies_hot_base", "allies_hot_scaling_percent", "allies_hot_duration"]:
            remove_field(skill, f)
        modified = True

    return modified


def migrate_shield(skill, sid):
    """Migrate shield_scaling_percent/shield_base -> effects[] shield."""
    modified = False

    # Main shield
    if "shield_scaling_percent" in skill or "shield_base" in skill:
        if has_effect(skill, "shield"):
            print(f"  {sid}: shield fields -> already in effects[], removing legacy")
            stats["effects_already_present"] += 1
        else:
            entry = {"type": "buff", "stat": "shield"}
            if "shield_scaling_percent" in skill:
                entry["value"] = skill["shield_scaling_percent"]
            elif "shield_base" in skill:
                entry["value"] = skill["shield_base"]
            if "shield_scaling_stat" in skill:
                entry["scaling"] = skill["shield_scaling_stat"]
            else:
                entry["scaling"] = "mag"
            if "shield_duration" in skill:
                entry["duration"] = skill["shield_duration"]
            else:
                entry["duration"] = 8.0
            if "shield_duration_per_level" in skill:
                entry["duration_per_level"] = skill["shield_duration_per_level"]
            if "shield_scaling_per_level" in skill:
                entry["value_per_level"] = skill["shield_scaling_per_level"]

            add_effect(skill, entry)
            print(f"  {sid}: shield -> added effects[] shield (value={entry.get('value')}, scaling={entry.get('scaling')}, duration={entry.get('duration')})")

        for f in ["shield_scaling_percent", "shield_scaling_per_level",
                   "shield_scaling_stat", "shield_duration", "shield_duration_per_level",
                   "shield_base", "shield_value_per_level"]:
            remove_field(skill, f)
        modified = True

    # Self-shield
    if "self_shield_scaling_percent" in skill or "self_shield_base" in skill:
        entry = {"type": "buff", "stat": "shield", "target": "self"}
        if "self_shield_scaling_percent" in skill:
            entry["value"] = skill["self_shield_scaling_percent"]
        elif "self_shield_base" in skill:
            entry["value"] = skill["self_shield_base"]
        if "self_shield_scaling_stat" in skill:
            entry["scaling"] = skill["self_shield_scaling_stat"]
        else:
            entry["scaling"] = "mag"
        if "self_shield_duration" in skill:
            entry["duration"] = skill["self_shield_duration"]
        else:
            entry["duration"] = 8.0
        if "self_shield_scaling_per_level" in skill:
            entry["value_per_level"] = skill["self_shield_scaling_per_level"]

        add_effect(skill, entry)
        print(f"  {sid}: self_shield -> added effects[] shield (target=self, value={entry.get('value')})")

        for f in ["self_shield_scaling_percent", "self_shield_scaling_per_level",
                   "self_shield_scaling_stat", "self_shield_base", "self_shield_duration",
                   "self_shield"]:
            remove_field(skill, f)
        modified = True

    # Ally shield
    if "ally_shield_scaling_percent" in skill or "ally_shield_base" in skill:
        entry = {"type": "buff", "stat": "shield", "target": "ally"}
        if "ally_shield_scaling_percent" in skill:
            entry["value"] = skill["ally_shield_scaling_percent"]
        elif "ally_shield_base" in skill:
            entry["value"] = skill["ally_shield_base"]
        if "ally_shield_scaling_stat" in skill:
            entry["scaling"] = skill["ally_shield_scaling_stat"]
        else:
            entry["scaling"] = "mag"
        if "ally_shield_duration" in skill:
            entry["duration"] = skill["ally_shield_duration"]
        else:
            entry["duration"] = 8.0

        add_effect(skill, entry)
        print(f"  {sid}: ally_shield -> added effects[] shield (target=ally, value={entry.get('value')})")

        for f in ["ally_shield_scaling_percent", "ally_shield_base",
                   "ally_shield_scaling_stat", "ally_shield_duration"]:
            remove_field(skill, f)
        modified = True

    return modified


def migrate_allies_buff(skill, sid):
    """Migrate allies_buff/enemies_debuff composite fields."""
    modified = False

    if "allies_buff" in skill:
        stat = skill["allies_buff"]
        value = skill.get("allies_buff_value", 10)
        duration = skill.get("allies_buff_duration", 8.0)
        entry = {"type": "buff", "stat": stat, "value": value, "duration": duration, "target": "allies"}
        if "allies_buff_duration_scaling" in skill:
            entry["duration_scaling"] = skill["allies_buff_duration_scaling"]
        add_effect(skill, entry)
        print(f"  {sid}: allies_buff={stat} -> added effects[] buff (target=allies)")
        for f in ["allies_buff", "allies_buff_value", "allies_buff_duration",
                   "allies_buff_duration_scaling"]:
            remove_field(skill, f)
        modified = True

    if "enemies_debuff" in skill:
        stat = skill["enemies_debuff"]
        value = skill.get("enemies_debuff_value", 10)
        duration = skill.get("enemies_debuff_duration", 6.0)
        entry = {"type": "debuff", "stat": stat, "value": value, "duration": duration, "target": "enemies"}
        if "enemies_debuff_duration_scaling" in skill:
            entry["duration_scaling"] = skill["enemies_debuff_duration_scaling"]
        add_effect(skill, entry)
        print(f"  {sid}: enemies_debuff={stat} -> added effects[] debuff (target=enemies)")
        for f in ["enemies_debuff", "enemies_debuff_value", "enemies_debuff_duration",
                   "enemies_debuff_duration_scaling"]:
            remove_field(skill, f)
        modified = True

    return modified


# ============================================================
# MAIN
# ============================================================

def process_skill(skill):
    """Apply all Bloc 1 migrations to a single skill."""
    sid = skill.get("id", "???")
    modified = False
    modified |= migrate_dot_stacks(skill, sid)
    modified |= migrate_buffs_simple(skill, sid)
    modified |= migrate_hot(skill, sid)
    modified |= migrate_shield(skill, sid)
    modified |= migrate_allies_buff(skill, sid)
    if modified:
        stats["skills_modified"] += 1
    return modified


def process_skills_list(skills):
    """Process a list of skills."""
    modified = False
    for skill in skills:
        if isinstance(skill, dict):
            modified |= process_skill(skill)
    return modified


def main():
    db_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(db_root)

    print(f"{'DRY RUN — no files will be modified' if DRY_RUN else 'LIVE RUN — files will be modified'}")
    print(f"Working directory: {os.getcwd()}\n")

    skill_files = sorted(glob.glob("classes/*/skills.json"))

    for skill_file in skill_files:
        print(f"\n=== {skill_file} ===")
        with open(skill_file, encoding="utf-8") as f:
            data = json.load(f)

        original = json.dumps(data)
        file_modified = False

        # Process base_skills
        file_modified |= process_skills_list(data.get("base_skills", []))

        # Process subclass_skills
        for sub_id, sub_data in data.get("subclass_skills", {}).items():
            if isinstance(sub_data, list):
                file_modified |= process_skills_list(sub_data)
            elif isinstance(sub_data, dict):
                file_modified |= process_skills_list(sub_data.get("skills", []))

        if file_modified:
            stats["files_modified"] += 1
            if not DRY_RUN:
                with open(skill_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write("\n")
                print(f"  -> FILE WRITTEN")
            else:
                print(f"  -> WOULD WRITE (dry run)")

    # Summary
    print(f"\n{'='*60}")
    print(f"MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"  Files modified:          {stats['files_modified']}")
    print(f"  Skills modified:         {stats['skills_modified']}")
    print(f"  Legacy fields removed:   {stats['fields_removed']}")
    print(f"  Effects entries added:    {stats['effects_added']}")
    print(f"  Already in effects[]:    {stats['effects_already_present']}")
    print(f"")
    if DRY_RUN:
        print(f"  DRY RUN — no files were modified. Remove --dry-run to apply.")
    else:
        print(f"  DONE — files modified. Review with: git diff")
        print(f"  Then run: python scripts/validate_skills.py")


if __name__ == "__main__":
    main()
