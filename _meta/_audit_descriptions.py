"""
Audit complet des descriptions de skills vs canonical_grid (Option A).
Ecrit la liste structuree des violations et un dump JSON pour traitement.
"""

import json
import os
import re
import sys
from collections import defaultdict

ROOT = r"C:\Users\Charl\Documents\Kanarion Online\kanarion_database"

# ---------- Load canonical grid ----------
with open(os.path.join(ROOT, "stats", "status_effects.json"), "r", encoding="utf-8") as f:
    se = json.load(f)

grid_raw = se["_meta"]["canonical_grid"]
CANONICAL = {}
for cat_name, cat in grid_raw.items():
    if not isinstance(cat, dict) or cat_name == "_note":
        continue
    for eff_id, spec in cat.items():
        if isinstance(spec, dict) and "value_per_stack" in spec:
            CANONICAL[eff_id] = {
                "vps": spec.get("value_per_stack", 0),
                "max_stacks": spec.get("max_stacks", 0),
                "unit": spec.get("unit", "percent"),
                "total_max": spec.get("total_max", ""),
                "category": cat_name,
            }

FLAT_EFFECTS = {"def_up", "def_down"}
ADDITIVE_NOT_PERCENT = {"crit_damage_up", "crit_damage_down"}
DAMAGE_TAKEN_EFFECTS = {"vulnerable", "exposed", "marked", "berserk"}
DOT_EFFECTS = {"bleed", "burn", "chill", "poison", "corruption", "toxin"}

# ---------- Find skills + passives ----------
SKILL_FILES = []
for cls in ["warrior", "mage", "healer", "archer", "rogue", "artisan"]:
    p = os.path.join(ROOT, "classes", cls, "skills.json")
    if os.path.exists(p):
        SKILL_FILES.append((cls, p, "skills"))
    p = os.path.join(ROOT, "classes", cls, "passives.json")
    if os.path.exists(p):
        SKILL_FILES.append((cls, p, "passives"))
common = os.path.join(ROOT, "classes", "common_passives.json")
if os.path.exists(common):
    SKILL_FILES.append(("common", common, "passives"))


def iter_skills(node, path=""):
    if isinstance(node, dict):
        if "id" in node and ("effects" in node or "description_fr" in node):
            yield path, node
        for k, v in node.items():
            yield from iter_skills(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_skills(v, f"{path}[{i}]")


violations = []


def add(file, sid, rule, detail, lang="", expected=None, found=None):
    violations.append({
        "file": file, "id": sid, "rule": rule, "detail": detail,
        "lang": lang, "expected": expected, "found": found
    })


STAT_LABEL_MAP = {
    "atk_up":          (["ATK", r"attaque(?!\s*speed)", "puissance d'attaque"], "%"),
    "atk_down":        (["ATK", r"attaque(?!\s*speed)", "puissance d'attaque"], "%"),
    "mag_up":          (["MAG", "magique", r"puissance\s+magique"], "%"),
    "mag_down":        (["MAG", "magique", r"puissance\s+magique"], "%"),
    "atk_percent_up":  (["ATK", r"attaque"], "%"),
    "atk_percent_down":(["ATK", r"attaque"], "%"),
    "armor_up":        (["armure", "armor"], "%"),
    "armor_down":      (["armure", "armor"], "%"),
    "magic_resist_up": [r"resistance\s+magique", r"resi\s+mag", r"magic\s+resist"],
    "magic_resist_down": [r"resistance\s+magique", r"resi\s+mag", r"magic\s+resist"],
    "atk_speed_up":    [r"vitesse\s+d'attaque", r"attack\s+speed"],
    "atk_speed_down":  [r"vitesse\s+d'attaque", r"attack\s+speed"],
    "cast_speed_up":   [r"vitesse\s+d'incantation", r"cast\s+speed"],
    "cast_speed_down": [r"vitesse\s+d'incantation", r"cast\s+speed"],
    "crit_chance_up":  [r"crit", r"chance\s+critique", r"taux\s+critique"],
    "crit_chance_down":[r"crit", r"chance\s+critique"],
    "evasion_up":      [r"esquive", r"evasion"],
    "evasion_down":    [r"esquive", r"evasion"],
    "heal_power_up":   [r"soin", r"heal\s+power", r"puissance\s+de\s+soin"],
    "heal_power_down": [r"soin", r"heal\s+power"],
    "damage_percent_up":   [r"degats(?:\s+infliges)?", r"damage(?:\s+dealt)?"],
    "damage_percent_down": [r"degats", r"damage"],
    "accuracy_up":     [r"precision", r"accuracy"],
    "accuracy_down":   [r"precision", r"accuracy"],
    "damage_reduction_up":   [r"reduction\s+(?:de\s+)?degats", r"degats\s+subis", r"damage\s+reduction", r"damage\s+taken"],
    "damage_reduction_down": [r"reduction\s+(?:de\s+)?degats", r"degats\s+subis", r"damage\s+reduction"],
    "lifesteal":       [r"vol\s+de\s+vie", r"lifesteal", r"vole.+(?:HP|hp|vie)"],
    "thorns":          [r"epines", r"thorns"],
    "regen":           [r"regen"],
    "heal_received_down": [r"soins\s+recus", r"healing\s+received"],
    "heal_reduction":  [r"soins?\s+recus", r"healing\s+received"],
    "vulnerable":      [r"vulnerable", r"degats\s+subis"],
    "exposed":         [r"expose", r"exposed", r"degats\s+subis"],
    "marked":          [r"marque", r"marked", r"degats\s+subis"],
    "berserk":         [r"berserk"],
}


def normalize_labels(entry):
    if isinstance(entry, tuple):
        return entry[0]
    return entry


def check_skill(file, skill, top_class):
    sid = skill.get("id", "?")
    desc_fr = (skill.get("description_fr") or "").replace("\n", " ")
    desc_en = (skill.get("description_en") or "").replace("\n", " ")
    effects = skill.get("effects", []) or []
    if not isinstance(effects, list):
        return

    canonical_effects_in_skill = []  # (eff_id, stacks, effective_value)

    for eff in effects:
        if not isinstance(eff, dict):
            continue
        eff_id = eff.get("effect") or eff.get("stat")
        if not eff_id or eff_id not in CANONICAL:
            continue

        spec = CANONICAL[eff_id]
        stacks = eff.get("stacks_to_apply")
        etype = eff.get("type")

        # R0 : value/value_override interdits sur canonical buff/debuff (utility = one-shot autorise)
        if etype in ("buff", "debuff") and ("value" in eff or "value_override" in eff):
            add(file, sid, "R0_value_forbidden",
                f"effect '{eff_id}' (type={etype}) uses value/value_override (Option A interdit)")
            continue
        if etype == "utility":
            # Utility: lifesteal-on-hit, mana_restore, etc — value autorisee, pas de check stacks
            continue

        if stacks is None:
            continue

        effective = stacks * spec["vps"]
        cap = spec["max_stacks"] * spec["vps"]

        # R7 : cap canonical respecte (stacks_to_apply <= max_stacks)
        if stacks > spec["max_stacks"]:
            add(file, sid, "R7_cap_exceeded",
                f"'{eff_id}' stacks_to_apply={stacks} > max_stacks={spec['max_stacks']}")

        # R2 : pas de value_per_level / pct_per_level sur canonical
        if eff.get("value_per_level") or eff.get("pct_per_level"):
            add(file, sid, "R2_no_per_level_canonical",
                f"'{eff_id}' utilise value_per_level/pct_per_level (interdit canonical Phase 2)")

        canonical_effects_in_skill.append((eff_id, stacks, effective))

    # ---- Description checks ----
    for desc, lang in [(desc_fr, "fr"), (desc_en, "en")]:
        if not desc:
            continue

        # R3 : def_up/down ne doit JAMAIS apparaitre comme '-X% DEF'
        for eff_id, stacks, effective in canonical_effects_in_skill:
            if eff_id in FLAT_EFFECTS:
                bad_pat = re.compile(r"[+\-]\s*\d+\s*%\s*DEF\b", re.I)
                if bad_pat.search(desc):
                    add(file, sid, "R3_def_must_be_flat",
                        f"[{lang}] '{eff_id}' s={stacks} -> {effective} DEF flat (description utilise %)",
                        lang=lang, expected=f"{effective} DEF (flat)", found="N% DEF")

            # R4 : crit_damage = additif, ecrit '+X degats critiques' pas '+X%'
            if eff_id in ADDITIVE_NOT_PERCENT:
                bad_pat = re.compile(r"[+\-]\s*\d+\s*%\s*(?:de\s+)?(?:degats?\s*)?critiques?", re.I)
                bad_pat_en = re.compile(r"[+\-]\s*\d+\s*%\s*crit\s*(?:damage)?", re.I)
                if bad_pat.search(desc) or bad_pat_en.search(desc):
                    add(file, sid, "R4_crit_damage_additive",
                        f"[{lang}] '{eff_id}' additif: ecrire +{effective} degats critiques (PAS %)",
                        lang=lang, expected=f"+{effective} degats critiques", found="X% critiques")

            # R5 : vulnerable/exposed/marked/berserk = '+X% degats subis', pas reduction de resistance
            if eff_id in DAMAGE_TAKEN_EFFECTS:
                bad_pat = re.compile(r"reduction\s+(?:de\s+)?(?:la\s+)?resistance|reduit\s+(?:la\s+|sa\s+)?resistance", re.I)
                if bad_pat.search(desc):
                    add(file, sid, "R5_damage_taken_not_resist",
                        f"[{lang}] '{eff_id}' parle de 'reduction de resistance' au lieu de '+{effective}% degats subis'",
                        lang=lang)

            # R1 : description doit annoncer le % effectif
            entry = STAT_LABEL_MAP.get(eff_id)
            if not entry: continue
            labels = normalize_labels(entry)
            if eff_id in FLAT_EFFECTS or eff_id in ADDITIVE_NOT_PERCENT or eff_id in DOT_EFFECTS:
                continue
            for label in labels:
                # Strict : [+-]N% [optional small connector] LABEL — pas de '%' intervenant
                pat = re.compile(rf"([+\-])\s*(\d+(?:\.\d+)?)\s*%\s+(?:de\s+|of\s+|the\s+|la\s+|le\s+|les\s+|to\s+)?(?:{label})", re.I)
                for m in pat.finditer(desc):
                    sign, num = m.group(1), m.group(2)
                    n = float(num)
                    if "_up" in eff_id and sign != "+": continue
                    if "_down" in eff_id and sign != "-": continue
                    if abs(n - effective) > 0.01:
                        # tolerance : si description annonce le cap (acceptable pour ultimate qui applique max)
                        if abs(n - (CANONICAL[eff_id]["max_stacks"] * CANONICAL[eff_id]["vps"])) < 0.01 and stacks == CANONICAL[eff_id]["max_stacks"]:
                            continue
                        add(file, sid, "R1_wrong_pct",
                            f"[{lang}] '{eff_id}' s={stacks} -> attendu {sign}{int(effective) if effective == int(effective) else effective}% / desc dit {sign}{num}% (label={label})",
                            lang=lang, expected=f"{sign}{effective}%", found=f"{sign}{num}%")

        # R2_per_level : '+X%/niv' ou '(+X%/niv)' rapproche d'un label de stat canonical
        if canonical_effects_in_skill:
            for m in re.finditer(r"\(?[+\-]?\d+(?:\.\d+)?\s*%\s*/\s*niv\)?", desc):
                start = max(0, m.start() - 60)
                ctx = desc[start:m.end()]
                # Stats canonical labels condensed
                stat_re = r"ATK\b|MAG\b|armure|resistance\s+magique|esquive|crit|critique|reduction|degats\s+subis|precision|soin|vitesse\s+d'attaque|vitesse\s+d'incantation|degats\s+infliges?"
                # On exclut le scaling damage (`X% ATK degats`, `X% MAG`) — c'est OK
                # On flag uniquement si le %/niv suit un buff (genre '+25% ATK (+1%/niv)')
                if re.search(stat_re, ctx, re.I):
                    # Heuristique : exclure si le contexte contient 'ATK degats' / 'MAG degats' (scaling damage)
                    if re.search(r"%\s*ATK\s+(?:degats|damage)|%\s*MAG\s+(?:degats|damage)", ctx, re.I):
                        continue
                    # Exclure si '+X%/niv' suit immediatement un nombre format scaling like '140% ATK (+5%/niv)'
                    if re.search(r"\d+\s*%\s*ATK\s*\(\+", ctx) or re.search(r"\d+\s*%\s*MAG\s*\(\+", ctx):
                        continue
                    add(file, sid, "R2_per_level_in_desc",
                        f"[{lang}] suspect '+X%/niv' sur stat canonical: ...{ctx[-60:]}",
                        lang=lang)


for cls, fp, kind in SKILL_FILES:
    rel = os.path.relpath(fp, ROOT).replace(os.sep, "/")
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)
    for path, skill in iter_skills(data):
        check_skill(rel, skill, cls)

# ---------- Output ----------
by_file = defaultdict(list)
for v in violations:
    by_file[v["file"]].append(v)

print(f"=== AUDIT DESCRIPTIONS — {len(violations)} violations ===\n")
rule_counts = defaultdict(int)
for v in violations:
    rule_counts[v["rule"]] += 1
for r, c in sorted(rule_counts.items()):
    print(f"  {r}: {c}")
print()

for fp in sorted(by_file.keys()):
    items = by_file[fp]
    print(f"\n--- {fp} ({len(items)} violations) ---")
    by_id = defaultdict(list)
    for v in items:
        by_id[v["id"]].append(v)
    for sid in sorted(by_id.keys()):
        for v in by_id[sid]:
            print(f"  [{v['rule']}] {sid}: {v['detail']}")

out = os.path.join(ROOT, "_meta", "_audit_descriptions_results.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(violations, f, indent=2, ensure_ascii=False)
print(f"\n=> {out}")
