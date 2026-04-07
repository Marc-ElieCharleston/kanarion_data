"""Fix remaining description/data mismatches from audit."""
import json
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fixes = []

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


# ============ HEALER ============
with open("classes/healer/skills.json", "r", encoding="utf-8") as f:
    h = json.load(f)

# Smite: fix DoT duration in description (3s -> 6s)
sk = find_skill(h, "skill_healer_smite")
if sk:
    fr = sk.get("description_fr", "")
    en = sk.get("description_en", "")
    if "3s)" in fr:
        sk["description_fr"] = fr.replace("3s)", "6s)")
        fixes.append("smite FR: DoT 3s -> 6s")
    if "3s)" in en:
        sk["description_en"] = en.replace("3s)", "6s)")
        fixes.append("smite EN: DoT 3s -> 6s")

# Vine Shield: add base shield value 35 to match description
sk = find_skill(h, "skill_healer_lifewarden_vine_shield")
if sk:
    for eff in sk.get("effects", []):
        if eff.get("stat") == "shield" and eff.get("scaling") == "mag":
            if "base_value" not in eff:
                eff["base_value"] = 35
                fixes.append("vine_shield: added shield base_value: 35")

# Sacred Ward: add base shield value 25 to match description
sk = find_skill(h, "skill_healer_cantor_sacred_ward")
if sk:
    for eff in sk.get("effects", []):
        if eff.get("stat") == "shield" and eff.get("scaling") == "mag":
            if "base_value" not in eff:
                eff["base_value"] = 25
                fixes.append("sacred_ward: added shield base_value: 25")

# Restorative Strike: add value_per_level to lifesteal
sk = find_skill(h, "skill_healer_martyr_restorative_strike")
if sk:
    for eff in sk.get("effects", []):
        if eff.get("stat") == "lifesteal" or eff.get("type") == "lifesteal":
            if "value_per_level" not in eff:
                eff["value_per_level"] = 4
                fixes.append("restorative_strike: added lifesteal value_per_level: 4")

# Redemptive Wave: add cast_time mention in description
sk = find_skill(h, "skill_healer_martyr_redemptive_wave")
if sk:
    fr = sk.get("description_fr", "")
    en = sk.get("description_en", "")
    if "Incantation" not in fr and sk.get("cast_time", 0) > 0:
        sk["description_fr"] = "Incantation 2s. " + fr
        fixes.append("redemptive_wave FR: added cast time mention")
    if "Cast" not in en and "cast" not in en and sk.get("cast_time", 0) > 0:
        sk["description_en"] = "2s cast. " + en
        fixes.append("redemptive_wave EN: added cast time mention")

with open("classes/healer/skills.json", "w", encoding="utf-8") as f:
    json.dump(h, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ============ ARTISAN ============
with open("classes/artisan/skills.json", "r", encoding="utf-8") as f:
    a = json.load(f)

# Searing Slice: fix burn duration in description (5s -> 6s)
sk = find_skill(a, "skill_artisan_chef_searing_slice")
if sk:
    fr = sk.get("description_fr", "")
    en = sk.get("description_en", "")
    if "(5s)" in fr:
        sk["description_fr"] = fr.replace("(5s)", "(6s)")
        fixes.append("searing_slice FR: burn 5s -> 6s")
    if "(5s)" in en:
        sk["description_en"] = en.replace("(5s)", "(6s)")
        fixes.append("searing_slice EN: burn 5s -> 6s")

# Inferno Feast: fix HoT duration in description (10s -> 8s)
sk = find_skill(a, "skill_artisan_chef_inferno_feast")
if sk:
    fr = sk.get("description_fr", "")
    en = sk.get("description_en", "")
    if "pendant 10s" in fr:
        sk["description_fr"] = fr.replace("pendant 10s", "pendant 8s")
        fixes.append("inferno_feast FR: HoT 10s -> 8s")
    if "for 10s" in en:
        sk["description_en"] = en.replace("for 10s", "for 8s")
        fixes.append("inferno_feast EN: HoT 10s -> 8s")

with open("classes/artisan/skills.json", "w", encoding="utf-8") as f:
    json.dump(a, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ============ ROGUE ============
with open("classes/rogue/skills.json", "r", encoding="utf-8") as f:
    r = json.load(f)

# Mark Target: add duration_per_level to marked effect
sk = find_skill(r, "skill_rogue_mark_target")
if sk:
    for eff in sk.get("effects", []):
        if eff.get("stat") == "marked":
            if "duration_per_level" not in eff:
                eff["duration_per_level"] = 0.5
                fixes.append("mark_target: added marked duration_per_level: 0.5")

# Duelist Expose Weakness: add value_per_level to def_down
sk = find_skill(r, "skill_rogue_duelist_expose_weakness")
if sk:
    for eff in sk.get("effects", []):
        if eff.get("stat") == "def_down" or eff.get("stat") == "exposed":
            if "value_per_level" not in eff:
                eff["value_per_level"] = 1
                fixes.append("expose_weakness: added %s value_per_level: 1" % eff.get("stat"))

with open("classes/rogue/skills.json", "w", encoding="utf-8") as f:
    json.dump(r, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ============ ARCHER (ignore_los mentions) ============
with open("classes/archer/skills.json", "r", encoding="utf-8") as f:
    ar = json.load(f)

los_skills = [
    "skill_archer_falconer_falcon_strike",
    "skill_archer_falconer_talon_rend",
    "skill_archer_falconer_falcon_fury",
    "skill_archer_ballmaster_bounce_shot",
    "skill_archer_ballmaster_pinball",
    "skill_archer_ballmaster_ricochet",
    "skill_archer_ballmaster_focused_barrage",
    "skill_archer_ballmaster_endless_volley",
]

for sid in los_skills:
    sk = find_skill(ar, sid)
    if sk and sk.get("ignore_los"):
        fr = sk.get("description_fr", "")
        en = sk.get("description_en", "")
        if "ligne de vue" not in fr.lower() and "ignore" not in fr.lower():
            sk["description_fr"] = fr.rstrip() + "\nIgnore la ligne de vue."
            fixes.append("%s FR: added ignore_los mention" % sid.split("_")[-1])
        if "line of sight" not in en.lower() and "ignore" not in en.lower():
            sk["description_en"] = en.rstrip() + "\nIgnores line of sight."
            fixes.append("%s EN: added ignore_los mention" % sid.split("_")[-1])

with open("classes/archer/skills.json", "w", encoding="utf-8") as f:
    json.dump(ar, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("Total fixes: %d" % len(fixes))
for fix in fixes:
    print("  " + fix)
