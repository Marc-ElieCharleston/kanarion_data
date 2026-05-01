#!/usr/bin/env python3
"""
Bloc 0 — Skill Content Validator
Validates all player skills against the canonical schema defined in REFACTO_PLAN.
Designed to run in CI and locally.

Exit code 0 = all valid
Exit code 1 = errors found
"""

import json
import glob
import sys
import os

# ============================================================
# WHITELISTS — Canonical schema (from REFACTO_PLAN section 2, Decision 3)
# These lists define what fields are ALLOWED in a skill JSON.
# Any field not in these lists = ERROR.
# ============================================================

# Standard fields every skill can have
ALLOWED_STANDARD_FIELDS = {
    # Identity
    "id", "name_fr", "name_en", "tier", "subclass",
    # Targeting
    "target", "pattern", "range",
    # Damage/scaling
    "damage_type", "scaling_stat", "base_power", "scaling_percent",
    "percent_per_level", "power_per_level",
    # Cost
    "mana_cost", "mana_cost_per_level",
    # Timing
    "cooldown", "cooldown_per_level", "cast_time", "cast_interruptible",
    # Heal
    "heal_scaling_percent", "heal_scaling_per_level", "heal_scaling_stat",
    "base_heal",
    # Effects (canonical pipeline)
    "effects",
    # Text
    "description_fr", "description_en",
    # Tags & meta
    "tags", "vfx_type", "is_signature",
    # Required weapon
    "required_weapon", "required_class",
}

# Metadata fields allowed top-level (Decision 3 — skill behavior modifiers)
# These stay in JSON permanently, parsed into SkillData C++ struct.
ALLOWED_METADATA_FIELDS = {
    # LoS bypass
    "ignore_los",
    # Multi-hit
    "hit_count", "each_hit_can_crit", "damage_per_hit_bonus",
    # Execute
    "execute_threshold", "execute_bonus_percent",
    # Penetration
    "armor_pen", "shield_break", "ignore_shields",
    # Conditional bonus (object or simple fields)
    "conditional_bonus", "bonus_condition",
    "bonus_damage_percent", "few_targets_bonus", "few_targets_threshold",
    "bonus_if_armor_broken", "double_damage_if_armor_broken",
    "bonus_damage_vs_challenged", "damage_mult_if_challenged",
    "damage_mult_if_challenged_and_exposed",
    # Chain/bounce
    "chain_bounces", "damage_per_bounce", "can_bounce_same_target",
    "bounce_if_adjacent", "bounce_returns",
    # Charges/momentum
    "generates_charges", "consumes_charges", "max_charges_consumed",
    "generates_momentum",
    "bonus_per_charge", "bonus_per_charge_per_level",
    "bonus_damage_per_charge", "bonus_damage_per_momentum",
    "bonus_stacks_per_charge", "bonus_lifesteal_per_charge",
    "bonus_double_hit_per_charge",
    # Double hit / crit
    "double_hit_chance", "guaranteed_crit", "cd_reset_on_kill",
    "crit_damage_bonus",
    # Counter/reflect
    "counter_chance", "counter_chance_vs_challenged", "counter_type",
    "reflects_damage", "reflects_debuffs", "reflect_bonus_vs_challenged",
    # Self-sacrifice / drain (Martyr)
    "sacrifice_hp_percent", "drain_to_all_allies", "dot_heals_lowest_ally",
    "drain_heal_percent",
    # Conditional damage scaling
    "damage_per_bleed_stack", "bonus_damage_per_debuff", "max_debuff_bonus",
    "damage_per_missing_hp_percent", "max_missing_hp_bonus",
    "damage_per_adjacent_ally", "damage_per_adjacent_ally_per_level",
    "max_adjacent_bonus",
    # Stealth
    "stealth_bonus_damage",
    # Random pools (Cardmaster)
    "random_buffs_min", "random_buffs_max", "buff_pool",
    "random_buffs_min_at_level_5",
    "random_debuffs_min", "random_debuffs_max", "debuff_pool",
    "random_debuffs_min_at_level_5",
    "random_debuffs", "random_debuff_count_min", "random_debuff_count_max",
    "status_duration", "status_chance",
    "interrupts_on_double_hit",
    # Redirect (Trickster)
    "redirect_to",
    # Resurrect
    "resurrect", "resurrect_percent_hp",
    # Mark system (Rogue)
    "mark_ignore_los", "mark_refresh_on_hit", "mark_spread_on_kill",
    "marked_bonus_percent",
    # DoT sub-fields (Martyr/special)
    "dot_type", "dot_percent", "dot_duration",
    # Detonate (Alchemist)
    "detonates_toxin", "detonate_consumes_stacks",
    "detonate_damage_base", "detonate_damage_per_stack",
    # Reaver (consumes bleed stacks for bonus damage)
    "consumes_bleed_stacks", "bleed_consume_damage_per_stack",
    # Stun chance (per-skill)
    "stun_chance", "stun_chance_per_level", "stun_duration",
    # Disarm chance
    "disarm_chance", "disarm_chance_per_level", "disarm_duration",
    # Buff steal
    "steal_buff_chance", "steal_buff_count",
    # Apply order
    "apply_debuff_before_damage",
    # Dual effect (skill applies 2 different things)
    "dual_effect",
    # Thorn/shield special
    "thorn_reflect_percent", "shield_on_cross",
    # Team amp
    "team_damage_amp", "team_damage_amp_per_level",
    # Applies blind (standalone)
    "applies_blind", "blind_duration",
    # Buff untargetable
    "buff_untargetable",
    # Spellblade enchanted blade specifics
    "buff_attack_speed", "buff_magic_on_autos", "buff_magic_pen",
    "autos_generate_momentum",
    # ClassRegistry metadata (Phase 4.0 whitelist 2026-04-30)
    # Written by content_loader at parse time, present in skills.json for traceability.
    "base_class_id", "subclass_id", "tier3_id", "source_scope", "targeting",
    # Misc skill-specific fields (also Phase 4.0 whitelist)
    "exclude_caster",   # Artisan resource_share: heal allies but not caster
    "dot_heal_percent", # Martyr intercession: % of DoT damage redirected as healing
}

# Legacy fields: BLOCKED after Bloc 5 cleanup.
# These fields have been migrated to effects[] pipeline.
# Any remaining usage is an ERROR.
LEGACY_FIELDS_BLOCKED = {
    # DoT stacks (Bloc 1.1)
    "applies_bleed_stacks",
    "applies_burn_stacks",
    "applies_toxin_stacks",
    "applies_corruption_stacks",
    "applies_chill_stacks",
    # Buff/debuff custom values (Bloc 1.2)
    "buff_value_atk", "buff_value_speed", "buff_value_damage_percent",
    "buff_value_flat_dr",
    "buff_scaling_percent",
    "defense_reduction", "defense_reduction_per_level",
    "debuff_damage_taken", "debuff_stacks",
    # HoT legacy (Bloc 1.3)
    "hot_percent", "hot_duration", "hot_percent_per_level",
    "hot_duration_per_level", "hot_duration_scaling",
    "hot_base", "hot_scaling", "hot_scaling_percent", "hot_scaling_stat",
    "hot_amplify_percent",
    # Allies HoT/buff (composite skill fields)
    "allies_hot_base", "allies_hot_duration", "allies_hot_scaling_percent",
    "allies_buff", "allies_buff_value", "allies_buff_duration",
    "allies_buff_duration_scaling",
    # Enemies debuff
    "enemies_debuff", "enemies_debuff_value", "enemies_debuff_duration",
    "enemies_debuff_duration_scaling",
    # Shield legacy (Bloc 1.4)
    "shield_scaling_percent", "shield_scaling_per_level",
    "shield_scaling_stat", "shield_duration", "shield_duration_per_level",
    "shield_base", "shield_value_per_level",
    "self_shield_scaling_percent", "self_shield_scaling_per_level",
    "self_shield_scaling_stat", "self_shield_base", "self_shield_duration",
    "self_shield",
    "ally_shield_scaling_percent", "ally_shield_base",
    "ally_shield_duration", "ally_shield_scaling_stat",
    # Utility legacy (Bloc 2)
    "cleanse_count", "purge_count", "interrupts_cast",
    "mana_steal_percent", "mana_steal_flat",
    "mana_steal_flat_per_level", "mana_steal_per_level",
    "mana_steal_fallback", "mana_steal_fallback_value",
    "lifesteal_percent", "lifesteal_per_level",
    "lifesteal_percent_per_level", "lifesteal_target",
    # Mana restore/regen legacy
    "mana_restore_scaling_percent", "mana_restore_scaling_stat",
    "mana_restore_per_level",
    "mana_regen_percent", "mana_regen_duration",
    # Legacy single-value shortcuts
    "effect", "buff", "debuff",
    "effect_duration", "buff_duration",
    "buff_duration_per_level", "debuff_duration",
    "debuff_duration_per_level",
    # Misc legacy
    "shield_value",
}

# Allowed effects[].type values
ALLOWED_EFFECT_TYPES = {"buff", "debuff", "utility"}

# ============================================================
# VALIDATION
# ============================================================

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_effect_ids(db_root):
    """Load all valid effect stat IDs from stats/status_effects.json"""
    path = os.path.join(db_root, "stats", "status_effects.json")
    data = load_json(path)
    ids = set()
    for cat, cat_data in data.get("effects", {}).items():
        if isinstance(cat_data, dict):
            for k in cat_data.keys():
                if not k.startswith("_"):
                    ids.add(k)
    return ids


def load_canonical_grid(db_root):
    """Load _meta.canonical_grid from stats/status_effects.json (Phase 3 Option A).
    Returns dict: effect_id -> {value_per_stack, max_stacks, unit}.
    Used to validate that skills use stacks_to_apply correctly per CTO contract.
    """
    path = os.path.join(db_root, "stats", "status_effects.json")
    data = load_json(path)
    grid = {}
    canonical = data.get("_meta", {}).get("canonical_grid", {})
    for category, effects in canonical.items():
        if category.startswith("_"):
            continue
        if category == "non_stackable_special_effects":
            continue
        if not isinstance(effects, dict):
            continue
        for effect_id, defn in effects.items():
            if effect_id.startswith("_"):
                continue
            if not isinstance(defn, dict):
                continue
            max_stacks = defn.get("max_stacks", 0)
            if max_stacks <= 0:
                continue
            grid[effect_id] = {
                "value_per_stack": defn.get("value_per_stack", 0),
                "max_stacks": max_stacks,
                "unit": defn.get("unit", "percent"),
            }
    return grid


def extract_all_skills(data):
    """Extract all skill dicts from a skills.json file."""
    skills = []
    for skill in data.get("base_skills", []):
        if isinstance(skill, dict):
            skills.append(skill)
    for sub_id, sub_data in data.get("subclass_skills", {}).items():
        if isinstance(sub_data, list):
            for skill in sub_data:
                if isinstance(skill, dict):
                    skills.append(skill)
        elif isinstance(sub_data, dict):
            for skill in sub_data.get("skills", []):
                if isinstance(skill, dict):
                    skills.append(skill)
    return skills


def validate_skill_fields(skill, file_path, errors, warnings):
    """Check that every field in a skill is in an allowed whitelist."""
    sid = skill.get("id", "???")
    all_allowed = ALLOWED_STANDARD_FIELDS | ALLOWED_METADATA_FIELDS | LEGACY_FIELDS_BLOCKED

    for field in skill.keys():
        if field in ALLOWED_STANDARD_FIELDS:
            continue
        if field in ALLOWED_METADATA_FIELDS:
            continue
        if field in LEGACY_FIELDS_BLOCKED:
            errors.append(f"{file_path}: skill '{sid}' uses LEGACY field '{field}' — must be migrated to effects[]")
            continue
        # Unknown field = ERROR
        errors.append(f"{file_path}: skill '{sid}' has UNKNOWN field '{field}' — not in any whitelist")


def validate_effects_array(skill, file_path, valid_effect_ids, canonical_grid, errors, warnings):
    """Validate the effects[] array of a skill.
    Phase 3 Option A (CTO 2026-04-30): enforces canonical contract bidirectionally.
    """
    sid = skill.get("id", "???")
    effects = skill.get("effects")

    if effects is None:
        return  # No effects is valid (pure damage skill)

    if not isinstance(effects, list):
        errors.append(f"{file_path}: skill '{sid}' has effects that is not an array")
        return

    for i, effect in enumerate(effects):
        if not isinstance(effect, dict):
            errors.append(f"{file_path}: skill '{sid}' effects[{i}] is not an object")
            continue

        # Check type
        etype = effect.get("type")
        if not etype:
            errors.append(f"{file_path}: skill '{sid}' effects[{i}] missing 'type'")
        elif etype not in ALLOWED_EFFECT_TYPES:
            errors.append(f"{file_path}: skill '{sid}' effects[{i}] has unknown type '{etype}' (allowed: {sorted(ALLOWED_EFFECT_TYPES)})")

        # Check stat references valid effect ID
        stat = effect.get("stat")
        if not stat:
            errors.append(f"{file_path}: skill '{sid}' effects[{i}] missing 'stat'")
        elif stat not in valid_effect_ids:
            # Utility stats are "action" types, not in status_effects.json
            utility_stats = {
                "cleanse", "purge", "steal_buff",
                "mana_steal", "mana_restore", "mana_regen",
                "lifesteal", "resurrect", "interrupt",
            }
            if etype == "utility" and stat in utility_stats:
                pass  # Valid utility action
            else:
                errors.append(f"{file_path}: skill '{sid}' effects[{i}] stat '{stat}' not found in status_effects.json")

        # Allowed fields in an effect entry
        allowed_effect_fields = {
            "type", "stat",
            # Phase 3 Option A: stacks_to_apply replaces value/value_override for canonical
            "stacks_to_apply",
            # value still authorized for non-canonical (utility, legacy non-canonical types)
            "value", "value_per_level",
            # PR2 BUG-5 (CTO 2026-05-01): pct = scaling percent for typed scaled effects
            # (heal_over_time_mag, heal_over_time_max_hp, shield_def/mag/max_hp/max_mp).
            # Used together with value (flat base): result = value + (stat * pct / 100).
            "pct",
            "duration", "duration_per_level", "duration_scaling",
            "scaling", "target", "chance", "condition",
            "base_value",  # legacy field for shield base, kept for compat
        }
        for field in effect.keys():
            if field not in allowed_effect_fields:
                errors.append(f"{file_path}: skill '{sid}' effects[{i}] has unknown field '{field}'")

        # Phase 3 Option A — strict bidirectional contract
        if stat and stat in canonical_grid and etype in ("buff", "debuff"):
            grid_entry = canonical_grid[stat]
            max_stacks = grid_entry["max_stacks"]
            # canonical → value/value_override FORBIDDEN
            if "value" in effect:
                errors.append(
                    f"{file_path}: skill '{sid}' effects[{i}] uses 'value' on canonical stackable "
                    f"effect '{stat}' — use 'stacks_to_apply' instead (Option A contract)")
            if "value_override" in effect:
                errors.append(
                    f"{file_path}: skill '{sid}' effects[{i}] uses 'value_override' on canonical "
                    f"stackable effect '{stat}' — use 'stacks_to_apply' instead (Option A contract)")
            if "value_per_level" in effect:
                errors.append(
                    f"{file_path}: skill '{sid}' effects[{i}] uses 'value_per_level' on canonical "
                    f"stackable effect '{stat}' — value_per_level was retired in Phase 2 Option A")
            # stacks_to_apply REQUIRED
            if "stacks_to_apply" not in effect:
                errors.append(
                    f"{file_path}: skill '{sid}' effects[{i}] applies canonical stackable effect "
                    f"'{stat}' but missing 'stacks_to_apply' field (required, range [1, {max_stacks}])")
            else:
                stacks = effect["stacks_to_apply"]
                if not isinstance(stacks, int) or stacks <= 0 or stacks > max_stacks:
                    errors.append(
                        f"{file_path}: skill '{sid}' effects[{i}] effect '{stat}' has "
                        f"stacks_to_apply={stacks} out of range [1, {max_stacks}]")
        elif stat and etype in ("buff", "debuff"):
            # Non-canonical buff/debuff: stacks_to_apply FORBIDDEN
            if "stacks_to_apply" in effect:
                errors.append(
                    f"{file_path}: skill '{sid}' effects[{i}] uses 'stacks_to_apply' on "
                    f"non-canonical effect '{stat}' — stacks_to_apply is reserved for canonical "
                    f"stackable effects only")


def validate_legacy_contradiction(skill, file_path, errors):
    """If both legacy field AND effects[] describe the same mechanic with different values, flag."""
    sid = skill.get("id", "???")
    effects = skill.get("effects", [])
    if not isinstance(effects, list):
        return
    effect_stats = {e.get("stat") for e in effects if isinstance(e, dict)}

    # Check DoT contradictions
    for dot_type in ["bleed", "burn", "toxin", "corruption", "chill"]:
        legacy_key = f"applies_{dot_type}_stacks"
        if skill.get(legacy_key) and dot_type in effect_stats:
            legacy_val = skill.get(legacy_key)
            for e in effects:
                if e.get("stat") == dot_type and e.get("value") is not None and e.get("value") != legacy_val:
                    errors.append(
                        f"{file_path}: skill '{sid}' CONTRADICTION — "
                        f"{legacy_key}={legacy_val} but effects[].{dot_type}.value={e.get('value')}"
                    )


def main():
    # Determine database root
    db_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(db_root)

    errors = []
    warnings = []

    # Load valid effect IDs
    valid_effect_ids = load_effect_ids(db_root)
    print(f"Loaded {len(valid_effect_ids)} valid effect IDs from stats/status_effects.json")

    # Phase 3 Option A: load canonical grid for strict contract validation
    canonical_grid = load_canonical_grid(db_root)
    print(f"Loaded {len(canonical_grid)} canonical stackable effects from _meta.canonical_grid")

    # Process all class skill files
    skill_files = sorted(glob.glob("classes/*/skills.json"))
    total_skills = 0
    legacy_count = 0
    legacy_field_usage = {}

    for skill_file in skill_files:
        data = load_json(skill_file)
        skills = extract_all_skills(data)
        total_skills += len(skills)

        for skill in skills:
            validate_skill_fields(skill, skill_file, errors, warnings)
            validate_effects_array(skill, skill_file, valid_effect_ids, canonical_grid, errors, warnings)
            validate_legacy_contradiction(skill, skill_file, errors)

            # Count legacy usage
            for f in skill.keys():
                if f in LEGACY_FIELDS_BLOCKED:
                    legacy_field_usage[f] = legacy_field_usage.get(f, 0) + 1
            has_legacy = any(f in skill for f in LEGACY_FIELDS_BLOCKED)
            if has_legacy:
                legacy_count += 1

    # Summary
    print(f"\nValidated {total_skills} skills across {len(skill_files)} class files")
    print(f"  Legacy fields still present: {legacy_count} skills (migration pending)")

    if legacy_field_usage:
        print(f"\n  Legacy field usage breakdown:")
        for field, count in sorted(legacy_field_usage.items(), key=lambda x: -x[1]):
            print(f"    {field}: {count} skills")

    print(f"\n  Warnings: {len(warnings)}")
    print(f"  Errors: {len(errors)}")

    if warnings and "--verbose" in sys.argv:
        print(f"\n--- WARNINGS ({len(warnings)}) ---")
        for w in warnings:
            print(f"  [WARN] {w}")

    if errors:
        print(f"\n--- ERRORS ({len(errors)}) ---")
        for e in errors:
            print(f"  [ERROR] {e}")
        print(f"\nVALIDATION FAILED — {len(errors)} errors")
        sys.exit(1)
    else:
        print(f"\nVALIDATION PASSED — 0 errors ({len(warnings)} legacy warnings)")
        sys.exit(0)


if __name__ == "__main__":
    main()
