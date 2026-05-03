"""
Hydrate `effects.<section>.<eid>.{max_stacks,formula}` depuis `_meta.canonical_grid`.

Source de verite : `_meta.canonical_grid` (utilisee par le backend).
Cible : `effects.stat_modifiers` / `effects.tempo` / `effects.special` / `effects.hot` /
        `effects.defensive` / `effects.dot` (tooltips client).

Regles d'update :
- `max_stacks` : remplace par la valeur de la grid (toujours).
- `formula` : pour les unites simples (`percent`, `flat`, `percent_dmg_taken`, `percent_both`,
              `percent_additive_on_base`), reecrite avec la vps de la grid en preservant
              le label de la stat. Pour les unites complexes (HoT/DoT/reflect/lifesteal),
              la formula textuelle est preservee (semantique differente).
- Aucun autre champ n'est touche.
"""

import json
import os
import re
from collections import OrderedDict

ROOT = r"C:\Users\Charl\Documents\Kanarion Online\kanarion_database"
PATH = os.path.join(ROOT, "stats", "status_effects.json")

with open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

grid = {}
for cat, effs in data["_meta"]["canonical_grid"].items():
    if isinstance(effs, dict) and cat != "_note":
        for eid, spec in effs.items():
            if isinstance(spec, dict) and "value_per_stack" in spec:
                grid[eid] = spec

# Locate each canonical effect in catalog
effects = data["effects"]
loc = {}
for sec_name, sec in effects.items():
    if isinstance(sec, dict):
        for eid in grid:
            if eid in sec:
                loc[eid] = (sec_name, sec[eid])

# Etiquettes utilisees dans formula (preservees lors de la reecriture)
LABELS = {
    "atk_up": "ATK", "atk_down": "ATK",
    "atk_percent_up": "ATK", "atk_percent_down": "ATK",
    "mag_up": "MAG", "mag_down": "MAG",
    "armor_up": "armor", "armor_down": "armor",
    "magic_resist_up": "magic resist", "magic_resist_down": "magic resist",
    "atk_speed_up": "attack speed", "atk_speed_down": "attack speed",
    "cast_speed_up": "cast speed", "cast_speed_down": "cast speed",
    "crit_chance_up": "crit chance", "crit_chance_down": "crit chance",
    "evasion_up": "evasion", "evasion_down": "evasion",
    "accuracy_up": "accuracy", "accuracy_down": "accuracy",
    "heal_power_up": "heal power", "heal_power_down": "heal power",
    "heal_received_down": "healing received",
    "damage_percent_up": "all damage", "damage_percent_down": "all damage",
    "damage_reduction_up": "damage reduction", "damage_reduction_down": "damage reduction",
    "crit_resistance_down": "crit resistance",
    "def_up": "DEF", "def_down": "DEF",
    "crit_damage_up": "crit damage", "crit_damage_down": "crit damage",
    "vulnerable": "ALL damage taken",
    "exposed": "damage taken",
    "marked": "damage taken",
}

# Formules complexes a NE PAS reecrire (semantique non-mappable a un per-stack simple)
KEEP_FORMULA = {
    "heal_over_time", "regen", "thorns", "lifesteal", "heal_reduction", "berserk",
}


def make_formula(eid, spec):
    """Genere une formula textuelle a partir de la grid spec."""
    vps = spec["value_per_stack"]
    unit = spec.get("unit", "percent")
    sign = "+" if eid.endswith("_up") or eid in ("vulnerable", "exposed", "marked", "berserk") else "-"
    if eid.endswith("_down") and not eid.endswith("speed_down") and not eid.endswith("chance_down") and not eid.endswith("damage_down") and not eid.endswith("resist_down") and not eid.endswith("received_down") and not eid.endswith("resistance_down") and not eid.endswith("power_down") and not eid.endswith("racy_down"):
        sign = "-"
    # simple regex-friendly sign deduction
    if "_down" in eid:
        sign = "-"
    elif "_up" in eid:
        sign = "+"
    elif eid in ("vulnerable", "exposed", "marked"):
        sign = "+"

    label = LABELS.get(eid, eid)

    if unit == "percent":
        return f"{sign}{vps}% {label} per stack"
    if unit == "flat":
        return f"{sign}{vps} {label} flat per stack"
    if unit == "percent_additive_on_base":
        return f"{sign}{vps} {label} additive per stack (on 150% base)"
    if unit == "percent_dmg_taken":
        return f"{sign}{vps}% {label} per stack"
    if unit == "percent_both":
        return f"{sign}{vps}% damage dealt and damage taken per stack"
    return None


changes = []

for eid in sorted(grid.keys()):
    if eid not in loc:
        continue
    sec_name, entry = loc[eid]
    spec = grid[eid]
    target_max = spec["max_stacks"]
    cur_max = entry.get("max_stacks")

    # Update max_stacks
    if cur_max != target_max:
        entry["max_stacks"] = target_max
        changes.append((eid, sec_name, "max_stacks", cur_max, target_max))

    # Update formula (sauf cas complexes)
    if eid not in KEEP_FORMULA:
        new_formula = make_formula(eid, spec)
        if new_formula:
            cur_formula = entry.get("formula")
            if cur_formula != new_formula:
                entry["formula"] = new_formula
                changes.append((eid, sec_name, "formula", cur_formula, new_formula))

# Add value_per_stack as authoritative field on catalog (mirror grid) for client convenience
for eid, (sec_name, entry) in loc.items():
    spec = grid[eid]
    cur = entry.get("value_per_stack")
    if cur != spec["value_per_stack"]:
        entry["value_per_stack"] = spec["value_per_stack"]
        changes.append((eid, sec_name, "value_per_stack", cur, spec["value_per_stack"]))

# Print summary
print(f"=== HYDRATATION CATALOG — {len(changes)} changes ===\n")
for eid, sec, field, old, new in changes:
    old_s = repr(old) if not isinstance(old, str) or len(old) < 50 else old[:47] + "..."
    new_s = repr(new) if not isinstance(new, str) or len(new) < 50 else new[:47] + "..."
    print(f"  [{sec}] {eid}.{field}: {old_s} -> {new_s}")

# Write back
with open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"\n=> {PATH} updated")
