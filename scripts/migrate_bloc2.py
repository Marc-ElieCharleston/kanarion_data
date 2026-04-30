#!/usr/bin/env python3
"""
Bloc 2 — Migrate remaining legacy utility fields to effects[] format.

Handles:
- cleanse_count → effects[]: {"type":"utility","stat":"cleanse","value":N}
- purge_count → effects[]: {"type":"utility","stat":"purge","value":N}
- lifesteal_percent → effects[]: {"type":"utility","stat":"lifesteal","value":N}
- mana_steal_percent/flat → effects[]: {"type":"utility","stat":"mana_steal","value":N}
- mana_restore_* → effects[]: {"type":"utility","stat":"mana_restore",...}
- mana_regen_* → effects[]: {"type":"utility","stat":"mana_regen",...}
- interrupts_cast → effects[]: {"type":"utility","stat":"interrupt","value":1}
- buff_duration/debuff_duration (standalone) → absorbed into existing effects[].duration
- debuff_damage_taken → effects[]: {"type":"debuff","stat":"damage_taken_up","value":N,"duration":D}
- debuff_stacks → absorbed into existing effects[].value
- shield_value_per_level → kept as legacy (level scaling, Bloc 5)

One-shot script. Run with --dry-run to preview changes.
"""

import json
import glob
import sys
import os
import copy

DRY_RUN = "--dry-run" in sys.argv

# Track stats
stats = {
    "files_modified": 0,
    "skills_modified": 0,
    "legacy_fields_removed": 0,
    "effects_added": 0,
    "already_has_utility": 0,
}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def has_utility_effect(skill, stat):
    """Check if skill already has a utility effect with this stat."""
    for eff in skill.get("effects", []):
        if eff.get("type") == "utility" and eff.get("stat") == stat:
            return True
    return False


def has_effect_stat(skill, stat):
    """Check if skill already has any effect with this stat."""
    for eff in skill.get("effects", []):
        if eff.get("stat") == stat:
            return True
    return False


def ensure_effects(skill):
    """Ensure skill has an effects[] array."""
    if "effects" not in skill:
        skill["effects"] = []


def migrate_skill(skill):
    """Migrate a single skill's legacy utility fields to effects[]. Returns True if modified."""
    modified = False
    sid = skill.get("id", "???")

    # ---- cleanse_count → utility:cleanse ----
    if "cleanse_count" in skill and not has_utility_effect(skill, "cleanse"):
        ensure_effects(skill)
        skill["effects"].append({
            "type": "utility",
            "stat": "cleanse",
            "value": skill["cleanse_count"]
        })
        stats["effects_added"] += 1
        modified = True
    if "cleanse_count" in skill:
        del skill["cleanse_count"]
        stats["legacy_fields_removed"] += 1

    # ---- purge_count → utility:purge ----
    if "purge_count" in skill and not has_utility_effect(skill, "purge"):
        ensure_effects(skill)
        skill["effects"].append({
            "type": "utility",
            "stat": "purge",
            "value": skill["purge_count"]
        })
        stats["effects_added"] += 1
        modified = True
    if "purge_count" in skill:
        del skill["purge_count"]
        stats["legacy_fields_removed"] += 1

    # ---- lifesteal_percent → utility:lifesteal ----
    if "lifesteal_percent" in skill and not has_utility_effect(skill, "lifesteal"):
        ensure_effects(skill)
        eff = {
            "type": "utility",
            "stat": "lifesteal",
            "value": skill["lifesteal_percent"]
        }
        if "lifesteal_target" in skill:
            eff["target"] = skill["lifesteal_target"]
        skill["effects"].append(eff)
        stats["effects_added"] += 1
        modified = True
    for f in ["lifesteal_percent", "lifesteal_per_level", "lifesteal_percent_per_level", "lifesteal_target"]:
        if f in skill:
            del skill[f]
            stats["legacy_fields_removed"] += 1

    # ---- mana_steal_percent / mana_steal_flat → utility:mana_steal ----
    if ("mana_steal_percent" in skill or "mana_steal_flat" in skill) and not has_utility_effect(skill, "mana_steal"):
        ensure_effects(skill)
        val = skill.get("mana_steal_percent", skill.get("mana_steal_flat", 0))
        skill["effects"].append({
            "type": "utility",
            "stat": "mana_steal",
            "value": val
        })
        stats["effects_added"] += 1
        modified = True
    for f in ["mana_steal_percent", "mana_steal_flat", "mana_steal_per_level",
              "mana_steal_flat_per_level", "mana_steal_fallback", "mana_steal_fallback_value"]:
        if f in skill:
            del skill[f]
            stats["legacy_fields_removed"] += 1

    # ---- mana_restore_* → utility:mana_restore ----
    if "mana_restore_scaling_percent" in skill and not has_utility_effect(skill, "mana_restore"):
        ensure_effects(skill)
        eff = {
            "type": "utility",
            "stat": "mana_restore",
            "value": skill["mana_restore_scaling_percent"]
        }
        if "mana_restore_scaling_stat" in skill:
            eff["scaling"] = skill["mana_restore_scaling_stat"]
        skill["effects"].append(eff)
        stats["effects_added"] += 1
        modified = True
    for f in ["mana_restore_scaling_percent", "mana_restore_scaling_stat", "mana_restore_per_level"]:
        if f in skill:
            del skill[f]
            stats["legacy_fields_removed"] += 1

    # ---- mana_regen_percent + mana_regen_duration → utility:mana_regen ----
    if "mana_regen_percent" in skill and not has_utility_effect(skill, "mana_regen"):
        ensure_effects(skill)
        eff = {
            "type": "utility",
            "stat": "mana_regen",
            "value": skill["mana_regen_percent"]
        }
        if "mana_regen_duration" in skill:
            eff["duration"] = skill["mana_regen_duration"]
        skill["effects"].append(eff)
        stats["effects_added"] += 1
        modified = True
    for f in ["mana_regen_percent", "mana_regen_duration"]:
        if f in skill:
            del skill[f]
            stats["legacy_fields_removed"] += 1

    # ---- interrupts_cast → utility:interrupt ----
    if "interrupts_cast" in skill and not has_utility_effect(skill, "interrupt"):
        if skill["interrupts_cast"]:
            ensure_effects(skill)
            skill["effects"].append({
                "type": "utility",
                "stat": "interrupt",
                "value": 1
            })
            stats["effects_added"] += 1
            modified = True
    if "interrupts_cast" in skill:
        del skill["interrupts_cast"]
        stats["legacy_fields_removed"] += 1

    # ---- debuff_damage_taken → debuff:damage_taken_up ----
    if "debuff_damage_taken" in skill and not has_effect_stat(skill, "damage_taken_up"):
        ensure_effects(skill)
        eff = {
            "type": "debuff",
            "stat": "damage_taken_up",
            "value": skill["debuff_damage_taken"]
        }
        dur = skill.get("debuff_duration", 0)
        if dur:
            eff["duration"] = dur
        skill["effects"].append(eff)
        stats["effects_added"] += 1
        modified = True
    if "debuff_damage_taken" in skill:
        del skill["debuff_damage_taken"]
        stats["legacy_fields_removed"] += 1

    # ---- buff_duration / debuff_duration: update existing effects[] entries ----
    # These are standalone duration fields that should be absorbed into effects[].duration
    # Only remove them if every effect already has a duration set
    for dur_field, eff_type in [("buff_duration", "buff"), ("debuff_duration", "debuff")]:
        if dur_field in skill:
            dur_val = skill[dur_field]
            # Apply to any effect of matching type that lacks a duration
            for eff in skill.get("effects", []):
                if eff.get("type") == eff_type and "duration" not in eff:
                    eff["duration"] = dur_val
                    modified = True
            del skill[dur_field]
            stats["legacy_fields_removed"] += 1

    # ---- debuff_stacks: absorb into existing effects[].value ----
    if "debuff_stacks" in skill:
        stacks = skill["debuff_stacks"]
        for eff in skill.get("effects", []):
            if eff.get("type") == "debuff" and "value" not in eff:
                eff["value"] = stacks
                modified = True
        del skill["debuff_stacks"]
        stats["legacy_fields_removed"] += 1

    # ---- *_per_level fields: keep as legacy for now (level scaling = Bloc 5) ----
    # buff_duration_per_level, debuff_duration_per_level, shield_value_per_level
    # These are kept intentionally — they will be handled in Bloc 5 when we have
    # a proper level scaling system. For now they don't cause validation errors
    # because they're in LEGACY_FIELDS_COEXISTENCE.

    return modified


def process_skills_list(skills_list, file_path):
    """Process a list of skill dicts."""
    modified_count = 0
    for skill in skills_list:
        if not isinstance(skill, dict):
            continue
        if migrate_skill(skill):
            modified_count += 1
            stats["skills_modified"] += 1
            if DRY_RUN:
                print(f"  [DRY-RUN] Would modify: {skill.get('id', '???')}")
    return modified_count


def process_file(file_path):
    """Process a single skills.json file."""
    data = load_json(file_path)
    total_modified = 0

    # base_skills
    total_modified += process_skills_list(data.get("base_skills", []), file_path)

    # subclass_skills
    for sub_id, sub_data in data.get("subclass_skills", {}).items():
        if isinstance(sub_data, list):
            total_modified += process_skills_list(sub_data, file_path)
        elif isinstance(sub_data, dict):
            total_modified += process_skills_list(sub_data.get("skills", []), file_path)

    if total_modified > 0:
        stats["files_modified"] += 1
        if not DRY_RUN:
            save_json(file_path, data)
        print(f"  {file_path}: {total_modified} skills modified")

    return total_modified


def main():
    db_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(db_root)

    print(f"Bloc 2 Migration -- Legacy utility fields -> effects[]")
    print(f"{'DRY RUN' if DRY_RUN else 'LIVE RUN'}")
    print()

    skill_files = sorted(glob.glob("classes/*/skills.json"))
    for f in skill_files:
        process_file(f)

    print(f"\n--- Summary ---")
    print(f"  Files modified: {stats['files_modified']}")
    print(f"  Skills modified: {stats['skills_modified']}")
    print(f"  Legacy fields removed: {stats['legacy_fields_removed']}")
    print(f"  Effects entries added: {stats['effects_added']}")


if __name__ == "__main__":
    main()
