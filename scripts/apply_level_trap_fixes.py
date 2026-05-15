#!/usr/bin/env python3
"""
apply_level_trap_fixes.py — apply per-bucket default actions to level-trap skills.

Reads the lint output, classifies each skill by its primary effect/mechanic,
and proposes edits per the bucket decisions taken with the designer 2026-05-15:

  Bucket 1: Buffs offensifs canonical (atk_up/crit_up/atk_speed_up via stacks)
            → duration_per_level: 0.2
  Bucket 2: Buffs défensifs canonical (DR/armor/def/MR via stacks)
            → duration_per_level: 0.2
  Bucket 3: Shields flat (shield_max_hp/def/mag avec `value`)
            → effects[i].value_per_level: 1
  Bucket 4: HoT-only (heal_over_time_* avec `pct`)
            → effects[i].pct_per_level: 0.2
  Bucket 5: Debuffs/CC stat → duration_per_level: 0.2
            CC durs (fear/stun/freeze/sleep/petrify/knockdown) → 0.1
  Bucket 6: Binary utility — invisible/cc_immune/stance → duration_per_level: 0.2
            cleanse/purge/steal_buff → mana_cost_per_level: 0
  Bucket 7: DEAD heal_scaling_per_level → migrate to percent_per_level (same value)
  Bucket 8: card_lucky_draw / fate_gambler / cantor_requiem
            → mana_cost_per_level: 0 (effects intentionnellement fixes)

Usage:
  python scripts/apply_level_trap_fixes.py --dry-run  # show edits, no write
  python scripts/apply_level_trap_fixes.py            # apply edits
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANONICAL_BUFF_OFFENSIVE = {
    "atk_up", "mag_up", "atk_percent_up", "damage_percent_up", "accuracy_up",
    "crit_chance_up", "crit_damage_up", "atk_speed_up", "cast_speed_up",
    "lifesteal", "double_attack_chance",
}
CANONICAL_BUFF_DEFENSIVE = {
    "armor_up", "magic_resist_up", "damage_reduction_up", "evasion_up",
    "def_up", "heal_received_up",
}
CANONICAL_DEBUFF_STAT = {
    "atk_down", "mag_down", "damage_percent_down", "armor_down", "magic_resist_down",
    "damage_reduction_down", "atk_speed_down", "cast_speed_down", "evasion_down",
    "accuracy_down", "def_down", "crit_chance_down", "crit_damage_down",
    "vulnerable", "exposed", "marked", "heal_reduction", "heal_received_down",
    "crit_resistance_down",
}
HARD_CC = {"stun", "freeze", "sleep", "petrify", "knockdown"}
SOFT_CC = {"fear", "taunt", "silence", "blind", "root", "confusion", "disarm", "slow"}
HOT_STATS = {"heal_over_time", "heal_over_time_max_hp", "heal_over_time_mag"}
SHIELD_STATS = {"shield", "shield_def", "shield_mag", "shield_max_hp", "shield_max_mp"}
BINARY_DURATION = {"invisible", "cc_immune", "iron_stance_shield", "en_garde_stance",
                   "riposte_active", "enchanted_blade", "taunt_redirect", "cover",
                   "damage_transfer"}
BINARY_UTILITY = {"cleanse", "purge", "steal_buff"}

MYSTERY_SKILLS = {
    "skill_mage_card_lucky_draw",
    "skill_mage_fate_gambler_double_or_nothing",
    "skill_healer_cantor_requiem",
}

# Skills handled by a separate task (not by the bucket defaults).
SKIP_SKILLS = {
    # martyr_intercession is a DoT-static — Task #4 extends the schema with
    # dot_percent_per_level. The bucket defaults would set mana_cost_per_level
    # to 0 which is the wrong call (the DoT will scale once the schema lands).
    "skill_healer_martyr_intercession",
}

# Non-canonical resource buffs (regen-style) — not in the standard offensive
# or defensive set, but they should still scale per skill level.
NONCANON_RESOURCE_BUFF = {"mana_regen", "hp_regen", "heal_over_time"}


def find_skill(node, sid):
    if isinstance(node, dict):
        if node.get("id") == sid:
            return node
        for v in node.values():
            r = find_skill(v, sid)
            if r is not None:
                return r
    elif isinstance(node, list):
        for v in node:
            r = find_skill(v, sid)
            if r is not None:
                return r
    return None


def classify_skill(skill: dict) -> tuple[str, dict]:
    """Return (bucket_label, edit_dict) for a flagged skill."""
    sid = skill.get("id", "")

    # Skip skills handled by a different task.
    if sid in SKIP_SKILLS:
        return ("0-skip-other-task", {})

    # Bucket 8 — mystery skills
    if sid in MYSTERY_SKILLS:
        return ("8-mystery", {"set_root": {"mana_cost_per_level": 0}})

    # Bucket 7 — DEAD heal_scaling_per_level migration
    if "heal_scaling_per_level" in skill and isinstance(skill["heal_scaling_per_level"], (int, float)):
        v = skill["heal_scaling_per_level"]
        return ("7-dead-heal", {
            "set_root": {"percent_per_level": v},
            "delete_root": ["heal_scaling_per_level"],
        })

    effects = skill.get("effects") or []

    # Bucket 4 — HoT pct (any effect with HoT stat that has pct)
    hot_indices = []
    for i, e in enumerate(effects):
        stat = e.get("stat", "")
        if stat in HOT_STATS and e.get("pct"):
            hot_indices.append(i)

    # Bucket 3 — Shield with value (flat) or pct
    shield_indices = []
    for i, e in enumerate(effects):
        stat = e.get("stat", "")
        if stat in SHIELD_STATS:
            shield_indices.append(i)

    if shield_indices and not any(
        e.get("stat", "") in (CANONICAL_BUFF_OFFENSIVE | CANONICAL_BUFF_DEFENSIVE | CANONICAL_DEBUFF_STAT)
        for e in effects
    ):
        # Pure shield skill (or shield + binary effects only) → Bucket 3
        return ("3-shield", {
            "set_nested_in_effects": [
                (i, "value_per_level", 1) for i in shield_indices
            ],
        })

    if hot_indices and not shield_indices and not any(
        e.get("stat", "") in (CANONICAL_BUFF_OFFENSIVE | CANONICAL_BUFF_DEFENSIVE | CANONICAL_DEBUFF_STAT)
        for e in effects
    ):
        # Pure HoT (no canonical buffs/debuffs mixed in) → Bucket 4
        return ("4-hot", {
            "set_nested_in_effects": [
                (i, "pct_per_level", 0.2) for i in hot_indices
            ],
        })

    # If skill has shield AND canonical buffs (mixed) — Bucket 3 wins (scale shield)
    if shield_indices:
        return ("3-shield-mixed", {
            "set_nested_in_effects": [
                (i, "value_per_level", 1) for i in shield_indices
            ],
        })

    # If skill has HoT AND canonical effects (mixed) — Bucket 4 wins
    if hot_indices:
        return ("4-hot-mixed", {
            "set_nested_in_effects": [
                (i, "pct_per_level", 0.2) for i in hot_indices
            ],
        })

    # Categorize by canonical effects
    has_off_buff = any(e.get("stat", "") in CANONICAL_BUFF_OFFENSIVE for e in effects)
    has_def_buff = any(e.get("stat", "") in CANONICAL_BUFF_DEFENSIVE for e in effects)
    has_stat_debuff = any(e.get("stat", "") in CANONICAL_DEBUFF_STAT for e in effects)
    has_hard_cc = any(e.get("stat", "") in HARD_CC or e.get("type") == "debuff" and e.get("stat") in HARD_CC for e in effects)
    has_soft_cc = any(e.get("stat", "") in SOFT_CC for e in effects)
    has_binary_dur = any(e.get("stat", "") in BINARY_DURATION for e in effects)
    has_binary_util = any(e.get("type") in BINARY_UTILITY or e.get("stat") in BINARY_UTILITY for e in effects)

    # Bucket 6 utility — pure cleanse/purge/steal_buff
    if has_binary_util and not (has_off_buff or has_def_buff or has_stat_debuff or has_hard_cc or has_soft_cc or has_binary_dur):
        return ("6-utility-flat", {"set_root": {"mana_cost_per_level": 0}})

    # Bucket 6 binary duration — invisible/cc_immune/stance
    if has_binary_dur and not (has_off_buff or has_def_buff or has_stat_debuff or has_hard_cc):
        return ("6-binary-dur", {"set_root": {"duration_per_level": 0.2}})

    # Bucket 5 hard CC
    if has_hard_cc:
        return ("5-cc-hard", {"set_root": {"duration_per_level": 0.1}})

    # Bucket 5 soft CC + stat debuff
    if has_soft_cc or has_stat_debuff:
        return ("5-debuff", {"set_root": {"duration_per_level": 0.2}})

    # Bucket 1 offensive canonical
    if has_off_buff and not has_def_buff:
        return ("1-buff-off", {"set_root": {"duration_per_level": 0.2}})

    # Bucket 2 defensive canonical
    if has_def_buff and not has_off_buff:
        return ("2-buff-def", {"set_root": {"duration_per_level": 0.2}})

    # Mixed off + def (e.g. bloodrage_defiant_blood: atk_up + lifesteal + DR)
    if has_off_buff and has_def_buff:
        return ("1-mixed", {"set_root": {"duration_per_level": 0.2}})

    # Non-canonical resource buffs (mana_regen, hp_regen, canonical heal_over_time
    # with stacks_to_apply only — no `pct` so it didn't fall into Bucket 4).
    has_resource_buff = any(e.get("stat", "") in NONCANON_RESOURCE_BUFF for e in effects)
    if has_resource_buff:
        return ("2-noncanon-resource", {"set_root": {"duration_per_level": 0.2}})

    return ("?-uncategorized", {"set_root": {"mana_cost_per_level": 0}})


def apply_edit(skill: dict, edit: dict) -> list[str]:
    """Mutate skill in place. Return list of human-readable changes."""
    changes = []
    for k, v in edit.get("set_root", {}).items():
        old = skill.get(k, "<missing>")
        skill[k] = v
        changes.append(f"  root.{k}: {old} -> {v}")
    for k in edit.get("delete_root", []):
        if k in skill:
            old = skill.pop(k)
            changes.append(f"  root.{k}: {old} -> DELETED")
    for i, k, v in edit.get("set_nested_in_effects", []):
        if "effects" in skill and i < len(skill["effects"]):
            old = skill["effects"][i].get(k, "<missing>")
            skill["effects"][i][k] = v
            stat = skill["effects"][i].get("stat", "?")
            changes.append(f"  effects[{i}/{stat}].{k}: {old} -> {v}")
    return changes


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = parser.parse_args(argv)

    # Run lint to get fresh hits
    import subprocess
    res = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "lint_useless_level.py"), "--json"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if res.returncode != 0 and "hits" not in res.stdout:
        print(f"lint failed: {res.stderr}", file=sys.stderr)
        return 1
    data = json.loads(res.stdout)

    # Group by file, only level-trap (DoT-static handled separately)
    by_file: dict[Path, list[dict]] = {}
    for h in data["hits"]:
        if h["category"] != "level-trap":
            continue
        by_file.setdefault(Path(h["file"]), []).append(h)

    bucket_counts: dict[str, int] = {}
    total_edits = 0

    for fp, hits in sorted(by_file.items()):
        with fp.open("r", encoding="utf-8") as f:
            doc = json.load(f)
        file_changes: list[str] = []
        for h in sorted(hits, key=lambda x: x["skill_id"]):
            sid = h["skill_id"]
            skill = find_skill(doc, sid)
            if skill is None:
                print(f"!! could not find {sid} in {fp}")
                continue
            bucket, edit = classify_skill(skill)
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
            if not edit:
                file_changes.append(f"[{bucket}] {sid} (no-op, deferred)")
                continue
            changes = apply_edit(skill, edit)
            if changes:
                file_changes.append(f"[{bucket}] {sid}")
                file_changes.extend(changes)
                total_edits += 1
        if file_changes:
            print(f"\n=== {fp.relative_to(ROOT)} ===")
            for line in file_changes:
                print(line)
            if not args.dry_run:
                with fp.open("w", encoding="utf-8") as f:
                    json.dump(doc, f, indent=2, ensure_ascii=False)
                    f.write("\n")

    # Sweep 2 — purge dead heal_scaling_per_level even on skills not flagged
    # by the lint (they have OTHER valid scaling but still carry the dead field).
    extra_dead_heal = 0
    for fp in [ROOT / "classes" / "familiar" / "skills.json", ROOT / "skills" / "pet_skills.json"]:
        if not fp.is_file():
            continue
        with fp.open("r", encoding="utf-8") as f:
            doc = json.load(f)
        sweep_changes: list[str] = []

        def visit(node):
            nonlocal extra_dead_heal
            if isinstance(node, dict):
                if "heal_scaling_per_level" in node and "id" in node:
                    sid = node["id"]
                    v = node.pop("heal_scaling_per_level")
                    # Only set percent_per_level if not already present
                    if "percent_per_level" not in node:
                        node["percent_per_level"] = v
                        sweep_changes.append(f"[7-sweep] {sid}: heal_scaling_per_level={v} -> percent_per_level={v}")
                    else:
                        sweep_changes.append(f"[7-sweep] {sid}: heal_scaling_per_level={v} -> DELETED (percent_per_level already {node['percent_per_level']})")
                    extra_dead_heal += 1
                for v in node.values():
                    visit(v)
            elif isinstance(node, list):
                for v in node:
                    visit(v)

        visit(doc)
        # Filter out skills we already fixed in sweep 1 (they're already migrated)
        if sweep_changes:
            still_remaining = [c for c in sweep_changes if "DELETED" not in c]
            if still_remaining or sweep_changes:
                print(f"\n=== {fp.relative_to(ROOT)} (sweep 2 — dead heal_scaling_per_level) ===")
                for c in sweep_changes:
                    print(c)
            if not args.dry_run:
                with fp.open("w", encoding="utf-8") as f:
                    json.dump(doc, f, indent=2, ensure_ascii=False)
                    f.write("\n")

    print(f"\n=== Summary ===")
    print(f"Total skills edited (sweep 1, level-trap): {total_edits}")
    print(f"Total skills swept (sweep 2, dead heal_scaling_per_level): {extra_dead_heal}")
    for b in sorted(bucket_counts):
        print(f"  {b}: {bucket_counts[b]}")
    print(f"\nMode: {'DRY-RUN (no files written)' if args.dry_run else 'APPLIED'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
