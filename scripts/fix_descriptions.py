"""Fix all skill description/data mismatches found during audit."""
import json
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
all_fixes = []

def find_skill(data, sid):
    for s in data.get("base_skills", []):
        if s.get("id") == sid:
            return s
    subs = data.get("subclass_skills", {})
    if isinstance(subs, dict):
        for sub_id, sub_data in subs.items():
            if not isinstance(sub_data, dict):
                continue
            for s in sub_data.get("skills", []):
                if s.get("id") == sid:
                    return s
            t3 = sub_data.get("tier3_skills", {})
            if isinstance(t3, dict):
                for t3_id, t3_data in t3.items():
                    if isinstance(t3_data, dict):
                        for s in t3_data.get("skills", []):
                            if s.get("id") == sid:
                                return s
    return None

def fix_stat(data, sid, old, new):
    sk = find_skill(data, sid)
    if not sk:
        return
    for eff in sk.get("effects", []):
        if eff.get("stat") == old:
            eff["stat"] = new
            all_fixes.append(f"{sid}: {old} -> {new}")

# ============ WARRIOR ============
with open("classes/warrior/skills.json", "r", encoding="utf-8") as f:
    w = json.load(f)

# Berserker frenzy: berserk -> atk_up + add def_down
sk = find_skill(w, "skill_warrior_berserker_frenzy")
if sk:
    for eff in sk.get("effects", []):
        if eff.get("stat") == "berserk":
            eff["stat"] = "atk_up"
            eff["type"] = "buff"
            eff["value"] = 30
            all_fixes.append("berserker_frenzy: berserk -> atk_up 30")
    sk["effects"].append({"type": "debuff", "stat": "def_down", "value": 15, "duration": 8.0, "target": "self"})
    all_fixes.append("berserker_frenzy: added def_down 15")

# Warlord: def_up/down -> damage_reduction
fix_stat(w, "skill_warrior_warlord_weakening_roar", "def_down", "damage_reduction_down")
fix_stat(w, "skill_warrior_warlord_rally", "def_up", "damage_reduction_up")
fix_stat(w, "skill_warrior_warlord_war_banner", "def_up", "damage_reduction_up")

with open("classes/warrior/skills.json", "w", encoding="utf-8") as f:
    json.dump(w, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ============ HEALER ============
with open("classes/healer/skills.json", "r", encoding="utf-8") as f:
    h = json.load(f)

fix_stat(h, "skill_healer_lifewarden_regeneration", "def_up", "damage_reduction_up")
fix_stat(h, "skill_healer_lightbringer_bless", "def_up", "damage_reduction_up")

with open("classes/healer/skills.json", "w", encoding="utf-8") as f:
    json.dump(h, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ============ ARTISAN ============
with open("classes/artisan/skills.json", "r", encoding="utf-8") as f:
    a = json.load(f)

fix_stat(a, "skill_artisan_chef_blazing_aroma", "def_down", "damage_reduction_down")
fix_stat(a, "skill_artisan_chef_warming_broth", "def_up", "damage_reduction_up")

# Rallying melody: remove row_3 from descriptions
sk = find_skill(a, "skill_artisan_musician_rallying_melody")
if sk:
    fr = sk.get("description_fr", "")
    en = sk.get("description_en", "")
    if "row_3" in fr:
        sk["description_fr"] = fr.replace("Allies row_3", "3 allies en ligne").replace("Ennemis row_3", "3 ennemis en ligne").replace("row_3", "3 en ligne")
        all_fixes.append("rallying_melody FR: removed row_3")
    if "row_3" in en:
        sk["description_en"] = en.replace("Allies row_3", "3 allies in row").replace("Enemies row_3", "3 enemies in row").replace("row_3", "3 in row")
        all_fixes.append("rallying_melody EN: removed row_3")

# Living fortress: Sort -> Technique
sk = find_skill(a, "skill_artisan_forgemaster_living_fortress")
if sk:
    fr = sk.get("description_fr", "")
    if fr.startswith("Sort signature"):
        sk["description_fr"] = fr.replace("Sort signature", "Technique signature")
        all_fixes.append("living_fortress: Sort -> Technique")

with open("classes/artisan/skills.json", "w", encoding="utf-8") as f:
    json.dump(a, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ============ MAGE ============
with open("classes/mage/skills.json", "r", encoding="utf-8") as f:
    m = json.load(f)

# Spell Guard: clarify shield description
sk = find_skill(m, "skill_mage_sb_spell_guard")
if sk:
    fr = sk.get("description_fr", "")
    en = sk.get("description_en", "")
    if "Absorbe 40%" in fr:
        sk["description_fr"] = fr.replace("Absorbe 40% du Souffle max en degats pendant 8s", "Octroie un bouclier egal a 40% du Souffle max pendant 8s")
        all_fixes.append("spell_guard FR: clarified shield")
    if "Absorbs 40%" in en:
        sk["description_en"] = en.replace("Absorbs 40% of max Breath as damage for 8s", "Grants a shield equal to 40% of max Breath for 8s")
        all_fixes.append("spell_guard EN: clarified shield")

# Elemental Focus: magic damage -> MAG
sk = find_skill(m, "skill_mage_elem_elemental_focus")
if sk:
    fr = sk.get("description_fr", "")
    en = sk.get("description_en", "")
    if "degats magiques" in fr:
        sk["description_fr"] = fr.replace("+25% de degats magiques", "+25% MAG")
        all_fixes.append("elemental_focus FR: degats magiques -> MAG")
    if "magic damage" in en:
        sk["description_en"] = en.replace("+25% magic damage", "+25% MAG")
        all_fixes.append("elemental_focus EN: magic damage -> MAG")

# Curse of weakness: add generates_charges
sk = find_skill(m, "skill_mage_occ_curse_of_weakness")
if sk:
    sk["generates_charges"] = 1
    all_fixes.append("curse_of_weakness: added generates_charges: 1")

# Life drain: add value_per_level to lifesteal
sk = find_skill(m, "skill_mage_occ_life_drain")
if sk:
    for eff in sk.get("effects", []):
        if eff.get("stat") == "lifesteal":
            eff["value_per_level"] = 2
            all_fixes.append("life_drain: added lifesteal value_per_level: 2")

# Shadow pact: add value_per_level to lifesteal
sk = find_skill(m, "skill_mage_occ_shadow_pact")
if sk:
    for eff in sk.get("effects", []):
        if eff.get("stat") == "lifesteal":
            eff["value_per_level"] = 1.5
            all_fixes.append("shadow_pact: added lifesteal value_per_level: 1.5")

with open("classes/mage/skills.json", "w", encoding="utf-8") as f:
    json.dump(m, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"Total fixes: {len(all_fixes)}")
for fix in all_fixes:
    print(f"  {fix}")
