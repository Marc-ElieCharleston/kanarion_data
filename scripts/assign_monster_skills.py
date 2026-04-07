"""Assign archetype skills to all monsters in monsters.json."""
import json
import sys
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open('entities/monsters.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ============================================================
# SKILL ASSIGNMENT TABLE
# Rules:
#   normal = 1 basic + 2 archetype pool
#   elite  = 1 basic + 3 archetype pool
#   boss   = 1 basic + 3 archetype pool + 1 signature
#   tacticians = hand-picked mixed skills
# ============================================================

ASSIGNMENTS = {
    # ===================== ACT 1 — DESERT (lv 1-18) =====================

    # --- Early beasts (danger 1) ---
    "mob_rat":              ["skill_mob_bite", "skill_brute_heavy_slam", "skill_brute_charge"],
    "mob_scarab":           ["skill_mob_bite", "skill_brute_heavy_slam", "skill_brute_cleave"],
    "mob_serpent":          ["skill_mob_bite", "skill_assassin_quick_strike", "skill_assassin_poison_blade"],
    "mob_misty_fox":        ["skill_mob_bite", "skill_assassin_quick_strike", "skill_assassin_ambush"],
    "mob_boar":             ["skill_mob_bite", "skill_brute_heavy_slam", "skill_brute_charge"],
    "mob_enraged_boar":     ["skill_mob_slam", "skill_brute_heavy_slam", "skill_brute_charge"],
    "mob_wolf":             ["skill_mob_bite", "skill_assassin_quick_strike", "skill_assassin_poison_blade"],
    "mob_frothing_wolf":    ["skill_mob_bite", "skill_brute_heavy_slam", "skill_brute_execute"],

    # --- Mid beasts (danger 2) ---
    "mob_rock_scorpion":    ["skill_mob_slam", "skill_tank_shield_bash", "skill_tank_defensive_stance"],
    "mob_belier":           ["skill_mob_slam", "skill_tank_shield_bash", "skill_tank_defensive_stance"],
    "mob_dust_beetle":      ["skill_mob_slam", "skill_tank_shield_bash", "skill_tank_defensive_stance"],
    "mob_wild_dog":         ["skill_mob_bite", "skill_brute_heavy_slam", "skill_brute_charge"],
    "mob_alpha_hyena":      ["skill_mob_bite", "skill_brute_cleave", "skill_brute_charge"],
    "mob_hyene":            ["skill_mob_bite", "skill_assassin_quick_strike", "skill_assassin_ambush"],
    "mob_taureau":          ["skill_mob_slam", "skill_tank_shield_bash", "skill_tank_taunt_roar"],

    # --- Early humanoids (danger 2-3) ---
    "mob_poacher":          ["skill_mob_shoot", "skill_artillery_fire_bolt", "skill_artillery_fireball"],
    "mob_deserter":         ["skill_mob_slash", "skill_brute_heavy_slam", "skill_brute_execute"],
    "mob_outlaw_archer":    ["skill_mob_shoot", "skill_artillery_fire_bolt", "skill_artillery_lightning_bolt"],
    "mob_bandit":           ["skill_mob_slash", "skill_assassin_quick_strike", "skill_assassin_poison_blade"],
    "mob_crossbowman":      ["skill_mob_shoot", "skill_artillery_fire_bolt", "skill_artillery_frost_nova"],
    "mob_mercenary":        ["skill_mob_slash", "skill_tank_shield_bash", "skill_tank_defensive_stance"],
    "mob_plague_doctor":    ["skill_mob_shoot", "skill_support_weaken", "skill_support_dispel_magic"],

    # --- Gang Leader — ELITE TACTICIAN ---
    "mob_gang_leader":      ["skill_mob_slash", "skill_brute_heavy_slam", "skill_assassin_ambush", "skill_support_weaken"],

    # --- Converted village (lv 18, danger 3) ---
    "mob_converted_blacksmith": ["skill_mob_slam", "skill_tank_shield_bash", "skill_tank_shield_wall"],
    "mob_converted_farmer":     ["skill_mob_slash", "skill_brute_heavy_slam", "skill_brute_charge"],
    "mob_converted_herbalist":  ["skill_mob_shoot", "skill_healer_heal", "skill_healer_smite"],
    "mob_converted_zealot":     ["skill_mob_shoot", "skill_support_haste", "skill_support_weaken"],
    "mob_converted_hunter":     ["skill_mob_slash", "skill_assassin_quick_strike", "skill_assassin_ambush"],
    "mob_converted_archer":     ["skill_mob_shoot", "skill_artillery_fire_bolt", "skill_artillery_fireball"],

    # --- Converted Elder — ELITE TACTICIAN ---
    "mob_converted_elder":  ["skill_mob_shoot", "skill_healer_heal", "skill_support_haste", "skill_controller_silence"],

    # --- Zealot cultists (lv 19-20, danger 3) ---
    "mob_voleur":           ["skill_mob_slash", "skill_assassin_quick_strike", "skill_assassin_ambush"],
    "mob_exalted_preacher": ["skill_mob_shoot", "skill_healer_heal", "skill_healer_group_heal"],
    "mob_tower_fanatic":    ["skill_mob_shoot", "skill_support_haste", "skill_support_shield_barrier"],
    "mob_zealot_guard":     ["skill_mob_slash", "skill_tank_shield_bash", "skill_tank_taunt_roar"],
    "mob_zealot_ritualist": ["skill_mob_shoot", "skill_support_weaken", "skill_support_dispel_magic"],
    "mob_fanatic_inquisitor": ["skill_mob_slash", "skill_brute_heavy_slam", "skill_brute_execute"],

    # ===================== ACT 2 — FORESTS/SWAMPS (lv 20-30) =====================

    "mob_goblin":           ["skill_mob_slash", "skill_brute_heavy_slam", "skill_brute_charge"],
    "mob_scavenger_crow":   ["skill_mob_bite", "skill_assassin_quick_strike", "skill_assassin_ambush"],
    "mob_shaman_goblin":    ["skill_mob_shoot", "skill_healer_heal", "skill_healer_smite"],
    "mob_goblin_warior":    ["skill_mob_slash", "skill_brute_heavy_slam", "skill_brute_cleave"],
    "mob_goblin_bomber":    ["skill_mob_shoot", "skill_artillery_fireball", "skill_artillery_frost_nova"],
    "mob_lizardman":        ["skill_mob_slash", "skill_brute_heavy_slam", "skill_brute_execute"],
    "mob_lizardman_shaman": ["skill_mob_shoot", "skill_healer_heal", "skill_healer_group_heal"],

    # --- Spider Queen — ELITE TACTICIAN ---
    "mob_spider_queen":     ["skill_mob_bite", "skill_assassin_shadow_strike", "skill_controller_shackle", "skill_assassin_poison_blade"],

    "mob_tortue_de_pierre": ["skill_mob_slam", "skill_tank_shield_bash", "skill_tank_shield_wall"],
    "mob_cerf_obscur":      ["skill_mob_bite", "skill_assassin_quick_strike", "skill_assassin_shadow_strike"],
    "mob_armadillo":        ["skill_mob_slam", "skill_tank_shield_bash", "skill_tank_defensive_stance"],
    "mob_ember_hound":      ["skill_mob_bite", "skill_artillery_fire_bolt", "skill_artillery_fireball"],
    "mob_crystal_wolf":     ["skill_mob_bite", "skill_assassin_quick_strike", "skill_assassin_shadow_strike"],
    "mob_cheval_sauvage":   ["skill_mob_slam", "skill_brute_charge", "skill_brute_heavy_slam"],

    # ===================== ACT 2-3 TRANSITION (lv 28-38) =====================

    "mob_golem":            ["skill_mob_slam", "skill_tank_shield_bash", "skill_tank_shield_wall"],
    "mob_loup_humain":      ["skill_mob_bite", "skill_assassin_quick_strike", "skill_berserker_wild_swing"],
    "mob_brute_tribal":     ["skill_mob_slash", "skill_brute_cleave", "skill_brute_execute"],
    "mob_boar_wolf":        ["skill_mob_bite", "skill_assassin_quick_strike", "skill_berserker_wild_swing"],
    "mob_golem_runique":    ["skill_mob_slam", "skill_tank_shield_bash", "skill_artillery_frost_nova"],
    "mob_nightmare_horse":  ["skill_mob_slam", "skill_assassin_shadow_strike", "skill_assassin_ambush"],

    # --- Tribal Warlord — ELITE TACTICIAN ---
    "mob_tribal_warlord":   ["skill_mob_slash", "skill_brute_heavy_slam", "skill_brute_execute", "skill_support_haste"],

    # ===================== ACT 3 — UNDEAD CRYPTS (lv 40-45) =====================

    "mob_rift_warden":      ["skill_mob_slash", "skill_tank_shield_bash", "skill_tank_taunt_roar"],
    "mob_void_hound":       ["skill_mob_bite", "skill_assassin_quick_strike", "skill_assassin_poison_blade"],
    "mob_archer_squelette": ["skill_mob_shoot", "skill_artillery_fire_bolt", "skill_artillery_lightning_bolt"],
    "mob_guerrier_skull":   ["skill_mob_slash", "skill_brute_cleave", "skill_brute_execute"],
    "mob_spectral_wolf":    ["skill_mob_bite", "skill_assassin_shadow_strike", "skill_assassin_ambush"],
    "mob_skeleton_necromancer": ["skill_mob_shoot", "skill_healer_heal", "skill_healer_group_heal"],
    "mob_rift_stalker":     ["skill_mob_bite", "skill_assassin_shadow_strike", "skill_assassin_ambush"],

    # --- Bell Guardian — ELITE TANK ---
    "mob_bell_guardian":    ["skill_mob_slam", "skill_tank_shield_bash", "skill_tank_taunt_roar", "skill_tank_shield_wall"],

    # ===================== ACT 3 — RIFT/VOID CORRUPTED (lv 42-50) =====================

    "mob_abyssal_scholar":  ["skill_mob_shoot", "skill_support_weaken", "skill_support_dispel_magic"],
    "mob_dark_priest":      ["skill_mob_shoot", "skill_healer_heal", "skill_controller_silence"],
    "mob_void_executioner": ["skill_mob_slash", "skill_brute_execute", "skill_brute_cleave"],
    "mob_nightmare_stag":   ["skill_mob_slam", "skill_support_haste", "skill_support_shield_barrier"],
    "mob_rift_stitcher":    ["skill_mob_shoot", "skill_healer_heal", "skill_healer_dispel"],
    "mob_abyssal_charger":  ["skill_mob_slam", "skill_brute_charge", "skill_brute_heavy_slam"],
    "mob_shattered_knight": ["skill_mob_slash", "skill_assassin_shadow_strike", "skill_assassin_ambush"],

    # --- Corrupted Paladin — ELITE TACTICIAN ---
    "mob_corrupted_paladin": ["skill_mob_slash", "skill_brute_heavy_slam", "skill_tank_shield_bash", "skill_healer_heal"],

    # --- Lesser Demon (danger 6, endgame brute) ---
    "mob_lesser_demon":     ["skill_mob_slam", "skill_brute_heavy_slam", "skill_brute_execute"],

    # --- Corrupted Sentinel (danger 6, endgame tank) ---
    "mob_sentinel":         ["skill_mob_slash", "skill_tank_shield_bash", "skill_tank_shield_wall"],

    # ===================== BOSS =====================

    # --- Dark Cultist Lord — BOSS TACTICIAN (3 pool + 1 signature + 1 basic) ---
    "mob_dark_cultist":     ["skill_mob_shoot", "skill_controller_fear", "skill_controller_silence", "skill_support_weaken", "skill_controller_mind_control"],
}

# Apply assignments
changed = 0
missing = []
for m in data['monsters']:
    mid = m['id']
    if mid in ASSIGNMENTS:
        m['skills'] = ASSIGNMENTS[mid]
        changed += 1
    else:
        missing.append(mid)

print(f"Assigned skills to {changed}/{len(data['monsters'])} monsters")
if missing:
    print(f"MISSING ({len(missing)}): {missing}")

# Validate all skill IDs exist in monster_skills.json
with open('skills/monster_skills.json', 'r', encoding='utf-8') as f:
    skills_data = json.load(f)

valid_ids = set(s['id'] for s in skills_data['basic_skills'])
for arch in skills_data['archetype_skills'].values():
    valid_ids.update(s['id'] for s in arch['pool'])
    if 'signature' in arch:
        valid_ids.add(arch['signature']['id'])

invalid = set()
for m in data['monsters']:
    for sid in m.get('skills', []):
        if sid not in valid_ids:
            invalid.add(sid)

if invalid:
    print(f"INVALID SKILL IDS: {invalid}")
    sys.exit(1)
else:
    print("All skill IDs are valid!")

# Verify tier rules
errors = []
for m in data['monsters']:
    mid = m['id']
    tags = m.get('tags', [])
    skills = m.get('skills', [])
    if 'boss' in tags:
        if len(skills) < 5:
            errors.append(f"{mid}: boss should have 5 skills (basic+3pool+sig), has {len(skills)}")
    elif 'elite' in tags:
        if len(skills) < 4:
            errors.append(f"{mid}: elite should have 4 skills (basic+3pool), has {len(skills)}")
    else:
        if len(skills) < 3:
            errors.append(f"{mid}: normal should have 3 skills (basic+2pool), has {len(skills)}")

if errors:
    print(f"\nTIER RULE WARNINGS ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
else:
    print("All tier rules satisfied!")

# Write back
with open('entities/monsters.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f"\nmonsters.json updated! ({changed} monsters)")
