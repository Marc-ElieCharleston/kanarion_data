#!/usr/bin/env python3
"""
Recalculate all monster DEF/MR values using a formula-based approach.

Problem: The armor formula is damage * 100/(100+armor). With current DEF values
of 3-15 for early monsters, reduction is only 2.9%-13% — negligible.

Solution: New values based on level * K + floor, scaled by danger and lore profile.

Target reductions:
  - Lv1 trash (FAST): ~10% phys
  - Lv5 normal (BAL): ~15% phys
  - Lv5 tanky (PHYS): ~20% phys
  - Lv10 tank (PHYS_TANK): ~30% phys
  - Lv28 golem (PHYS_TANK d4): ~55% phys
  - Lv50 sentinel (PHYS_TANK d6): ~70% phys
"""

import json
import os
import math

# ── Danger scaling: (K_def, floor_def, K_mr, floor_mr) ──
DANGER_SCALING = {
    1: (0.8, 15, 0.6, 12),
    2: (1.0, 18, 0.8, 14),
    3: (1.2, 20, 1.0, 16),
    4: (1.5, 24, 1.2, 18),
    5: (1.8, 28, 1.5, 22),
    6: (2.0, 32, 1.8, 26),
}

# ── Lore profiles: (def_mult, mr_mult) ──
PROFILES = {
    "PHYS_TANK": (1.8, 0.5),   # Stone/shell/heavy armor tanks
    "PHYS":      (1.4, 0.6),   # Armored beasts, heavy warriors
    "BAL_TANK":  (1.3, 1.0),   # Balanced tanks (runic golem, mercenary)
    "BAL":       (1.0, 1.0),   # Balanced humanoids
    "MAG":       (0.5, 1.5),   # Casters, magical, spectral
    "FAST":      (0.7, 0.7),   # Agile assassins, squishy beasts
}

# ── Monster profile assignments ──
MONSTER_PROFILES = {
    # --- Danger 1 (early game, lv1-5) ---
    "mob_rat":           "FAST",       # Squishy rat
    "mob_scarab":        "PHYS_TANK",  # Hard carapace
    "mob_goblin":        "BAL",        # Balanced humanoid
    "mob_scavenger_crow":"FAST",       # Agile bird
    "mob_misty_fox":     "FAST",       # Agile beast
    "mob_boar":          "PHYS",       # Thick hide
    "mob_enraged_boar":  "PHYS",       # Thick hide, aggressive
    "mob_wolf":          "FAST",       # Fast predator

    # --- Danger 2 (lv6-15) ---
    "mob_frothing_wolf":    "PHYS",       # Tougher wolf variant
    "mob_rock_scorpion":    "PHYS_TANK",  # Armored shell
    "mob_belier":           "PHYS_TANK",  # Ram - thick skull
    "mob_shaman_goblin":    "MAG",        # Caster
    "mob_alpha_hyena":      "PHYS",       # Tough alpha beast
    "mob_goblin_warior":    "PHYS",       # Armored goblin
    "mob_hyene":            "FAST",       # Fast predator
    "mob_goblin_bomber":    "MAG",        # Caster/artillery
    "mob_archer_squelette": "BAL",        # Undead ranged
    "mob_lizardman":        "BAL",        # Balanced humanoid
    "mob_taureau":          "PHYS_TANK",  # Big armored beast
    "mob_lizardman_shaman": "MAG",        # Caster
    "mob_tortue_de_pierre": "PHYS_TANK",  # Stone shell
    "mob_outlaw_archer":    "BAL",        # Balanced humanoid
    "mob_bandit":           "FAST",       # Agile bandit
    "mob_crossbowman":      "BAL",        # Balanced ranged

    # --- Danger 3 (lv12-26) ---
    "mob_plague_doctor":       "MAG",        # Caster/support
    "mob_spider_queen":        "MAG",        # Magical spider
    "mob_mercenary":           "BAL_TANK",   # Armored mercenary
    "mob_cerf_obscur":         "FAST",       # Fast corrupted beast
    "mob_gang_leader":         "BAL",        # Elite balanced
    "mob_converted_blacksmith":"PHYS_TANK",  # Heavy armor
    "mob_converted_farmer":    "BAL",        # Balanced humanoid
    "mob_converted_herbalist": "MAG",        # Caster/healer
    "mob_converted_zealot":    "MAG",        # Caster/support
    "mob_converted_hunter":    "FAST",       # Agile assassin
    "mob_converted_archer":    "BAL",        # Balanced ranged
    "mob_voleur":              "FAST",       # Very agile thief
    "mob_exalted_preacher":    "MAG",        # Caster/healer
    "mob_tower_fanatic":       "MAG",        # Caster/support
    "mob_zealot_guard":        "PHYS_TANK",  # Tank
    "mob_converted_elder":     "MAG",        # Caster/elite
    "mob_spectral_wolf":       "MAG",        # Spectral = high MR
    "mob_guerrier_skull":      "PHYS",       # Undead warrior, armored
    "mob_zealot_ritualist":    "MAG",        # Caster/support
    "mob_fanatic_inquisitor":  "BAL",        # Balanced brute
    "mob_crystal_wolf":        "MAG",        # Crystal = high MR
    "mob_armadillo":           "PHYS_TANK",  # Armored shell
    "mob_ember_hound":         "MAG",        # Fire elemental
    "mob_cheval_sauvage":      "PHYS",       # Wild horse, tough

    # --- Danger 4 (lv28-35) ---
    "mob_golem":          "PHYS_TANK",  # Stone golem
    "mob_loup_humain":    "BAL",        # Werewolf - balanced
    "mob_brute_tribal":   "PHYS",       # Armored brute
    "mob_boar_wolf":      "PHYS",       # Tough hybrid
    "mob_golem_runique":  "BAL_TANK",   # Runic = balanced def/mr

    # --- Danger 5 (lv36-45) ---
    "mob_nightmare_horse":     "MAG",        # Nightmare = magical
    "mob_tribal_warlord":      "BAL_TANK",   # Elite balanced
    "mob_bell_guardian":       "PHYS_TANK",  # Elemental tank
    "mob_skeleton_necromancer":"MAG",        # Caster
    "mob_dark_priest":         "MAG",        # Caster

    # --- Danger 6 (lv48-50) ---
    "mob_dark_cultist":  "MAG",        # Boss caster
    "mob_lesser_demon":  "BAL_TANK",   # Demon - tough everywhere
    "mob_sentinel":      "PHYS_TANK",  # Corrupted tank
}


def calculate_defense(level, danger, profile_name):
    """Calculate new DEF and MR for a monster."""
    if danger not in DANGER_SCALING:
        danger = min(danger, 6)
    k_def, floor_def, k_mr, floor_mr = DANGER_SCALING[danger]
    def_mult, mr_mult = PROFILES[profile_name]

    raw_def = level * k_def + floor_def
    raw_mr = level * k_mr + floor_mr

    new_def = round(raw_def * def_mult)
    new_mr = round(raw_mr * mr_mult)

    return new_def, new_mr


def reduction_pct(armor):
    """Calculate the % damage reduction from armor."""
    return armor / (armor + 100) * 100


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    monsters_path = os.path.join(script_dir, "..", "entities", "monsters.json")

    with open(monsters_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    monsters = data["monsters"]
    changes = []

    for m in monsters:
        mid = m["id"]
        level = m["base_level"]
        danger = m["danger_level"]
        old_def = m["base_stats"].get("def", 0)
        old_mr = m["base_stats"].get("magic_resist", 0)

        # Get profile (default to BAL if unknown)
        profile = MONSTER_PROFILES.get(mid, "BAL")

        new_def, new_mr = calculate_defense(level, danger, profile)

        # Apply changes
        m["base_stats"]["def"] = new_def
        m["base_stats"]["magic_resist"] = new_mr

        old_def_pct = reduction_pct(old_def)
        new_def_pct = reduction_pct(new_def)
        old_mr_pct = reduction_pct(old_mr)
        new_mr_pct = reduction_pct(new_mr)

        changes.append({
            "id": mid,
            "level": level,
            "danger": danger,
            "profile": profile,
            "def": f"{old_def}->{new_def} ({old_def_pct:.1f}%->{new_def_pct:.1f}%)",
            "mr": f"{old_mr}->{new_mr} ({old_mr_pct:.1f}%->{new_mr_pct:.1f}%)",
        })

    # Update scaling section
    if "scaling" in data:
        data["scaling"]["def_per_level"] = 1.0
        data["scaling"]["mr_per_level"] = 0.8
        data["scaling"]["_formula"] = "final_stat = base_stat + (per_level * (monster_level - base_level))"

    # Update version
    data["_meta"]["version"] = "5.0"
    data["_meta"]["balance_note"] = "v5.0: DEF/MR recalculated with formula (level*K+floor)*profile. Target: 10% reduction for trash, 20-30% for normals, 40-55% for tanks. Scaling: def_per_level 1.0, mr_per_level 0.8"

    # Write back
    with open(monsters_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Print summary
    print(f"Updated {len(changes)} monsters\n")
    print(f"{'ID':<30} {'Lv':>3} {'D':>1} {'Profile':<12} {'DEF change':<28} {'MR change':<28}")
    print("-" * 110)
    for c in changes:
        print(f"{c['id']:<30} {c['level']:>3} {c['danger']:>1} {c['profile']:<12} {c['def']:<28} {c['mr']:<28}")


if __name__ == "__main__":
    main()
