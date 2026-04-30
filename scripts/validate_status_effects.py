#!/usr/bin/env python3
"""
Validate that all status effect references in skill files exist in status_effects.json
and have impl == "done".

Run from kanarion_database/:
    python scripts/validate_status_effects.py
"""

import json
import os
import sys


# Utility effect types that are NOT status effects (handled by SkillExecutor)
UTILITY_STATS = {"cleanse", "purge", "mana_steal", "mana_restore"}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_status_effect_ids(status_effects_data):
    """Extract all effect IDs and their impl status from status_effects.json."""
    effects = status_effects_data.get("effects", {})
    result = {}  # effect_id -> impl status
    for category, category_data in effects.items():
        if category.startswith("_"):
            continue
        if not isinstance(category_data, dict):
            continue
        for effect_id, effect_def in category_data.items():
            if effect_id.startswith("_"):
                continue
            if not isinstance(effect_def, dict):
                continue
            impl = effect_def.get("impl", "unknown")
            result[effect_id] = impl
    return result


def extract_effect_refs_from_skill(skill):
    """Extract non-utility effect stat references from a single skill."""
    refs = []
    effects = skill.get("effects", [])
    if not isinstance(effects, list):
        return refs
    for effect in effects:
        if not isinstance(effect, dict):
            continue
        effect_type = effect.get("type", "")
        stat = effect.get("stat", "")
        if effect_type == "utility":
            continue
        if stat in UTILITY_STATS:
            continue
        if stat:
            refs.append(stat)
    return refs


def collect_skills_from_class_file(data):
    """Collect all skills from a class skills.json (base_skills + subclass_skills.*.skills)."""
    skills = []
    # base_skills
    for skill in data.get("base_skills", []):
        if isinstance(skill, dict):
            skills.append(skill)
    # subclass_skills
    subclass_skills = data.get("subclass_skills", {})
    for subclass_name, subclass_data in subclass_skills.items():
        if not isinstance(subclass_data, dict):
            continue
        for skill in subclass_data.get("skills", []):
            if isinstance(skill, dict):
                skills.append(skill)
    return skills


def collect_skills_from_monster_file(data):
    """Collect all skills from monster_skills.json (basic_skills + archetype_skills.*.pool + signature)."""
    skills = []
    # basic_skills
    for skill in data.get("basic_skills", []):
        if isinstance(skill, dict):
            skills.append(skill)
    # archetype_skills
    archetype_skills = data.get("archetype_skills", {})
    for archetype_name, archetype_data in archetype_skills.items():
        if not isinstance(archetype_data, dict):
            continue
        for skill in archetype_data.get("pool", []):
            if isinstance(skill, dict):
                skills.append(skill)
        sig = archetype_data.get("signature")
        if isinstance(sig, dict) and "id" in sig:
            skills.append(sig)
    return skills


def main():
    # Paths relative to CWD (should be kanarion_database/)
    status_effects_path = os.path.join("stats", "status_effects.json")

    class_skill_files = [
        os.path.join("classes", cls, "skills.json")
        for cls in ["warrior", "mage", "healer", "archer", "rogue", "artisan"]
    ]
    monster_skill_file = os.path.join("skills", "monster_skills.json")

    # Load status effects
    if not os.path.exists(status_effects_path):
        print(f"ERROR: {status_effects_path} not found. Run from kanarion_database/.")
        sys.exit(1)

    status_data = load_json(status_effects_path)
    known_effects = collect_status_effect_ids(status_data)
    print(f"Loaded {len(known_effects)} status effect IDs from {status_effects_path}")

    # Collect all skills and their effect references
    violations = []
    total_skills = 0
    total_refs = 0

    skill_files = class_skill_files + [monster_skill_file]

    for skill_file in skill_files:
        if not os.path.exists(skill_file):
            print(f"WARNING: {skill_file} not found, skipping")
            continue

        data = load_json(skill_file)

        if skill_file == monster_skill_file:
            skills = collect_skills_from_monster_file(data)
        else:
            skills = collect_skills_from_class_file(data)

        total_skills += len(skills)

        for skill in skills:
            skill_id = skill.get("id", "<unknown>")
            refs = extract_effect_refs_from_skill(skill)
            total_refs += len(refs)

            for effect_id in refs:
                if effect_id not in known_effects:
                    violations.append(
                        f"  MISSING: skill '{skill_id}' in {skill_file} "
                        f"references effect '{effect_id}' — not found in status_effects.json"
                    )
                elif known_effects[effect_id] != "done":
                    violations.append(
                        f"  NOT IMPL: skill '{skill_id}' in {skill_file} "
                        f"references effect '{effect_id}' — impl is '{known_effects[effect_id]}', expected 'done'"
                    )

    # Output
    print()
    if violations:
        print(f"VIOLATIONS FOUND ({len(violations)}):")
        for v in violations:
            print(v)
        print()

    print(f"{total_skills} skills checked, {total_refs} effect references checked, {len(violations)} violations")

    if violations:
        sys.exit(1)
    else:
        print("ALL STATUS EFFECT REFERENCES VALID")
        sys.exit(0)


if __name__ == "__main__":
    main()
