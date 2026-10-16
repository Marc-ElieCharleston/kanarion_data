"""PvE difficulty matrix: player builds vs scaled monsters, level 10 to 100.

For every (build, level, monster archetype, threat tier) the script computes

    TTK = turns for the player to kill the monster
    TTD = turns for the monster to kill the player
    R   = TTD / TTK          (> 1 the player wins, < 1 the monster wins)
    M   = sqrt(1 / R)        power multiplier the build still needs, applied to
                             both its damage and its survival, to reach R = 1

The player side is the deterministic BASELINE only: class base stats, growth,
allocated points, expected equipment. Passives, keystones, Koro cards, buffs,
subclass skills and consumables are deliberately left out: M is the share of
power those layers must bring for the build to win the fight solo. That avoids
modeling 48 specializations one by one.

Formulas mirror the server (kanarion_back, read 2026-10-02):
  - monster stats: shared/gameplay/monster_scaling_model.cpp (base x curve x tier)
  - damage: server-combat/src/combat/damage_calculator.cpp (100/(100+armor_eff),
    pen clamp 70, evasion, block 50 %)
  - player profile: server-combat/src/domain/combat_profile_builder.cpp
    (base + floor(growth x (lvl-1)) + points x point_value, mr += 0.2 x mag)
  - equipment: server-combat/src/loot/stat_roller.cpp, expected value by Monte Carlo
  - 1 turn = 1 GCD (config/combat.json gcd_duration), one action per side per turn

Run:  python scripts/balance/pve_matrix.py            (writes out/pve_matrix.csv)
"""
import csv
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"

LEVELS = list(range(10, 101, 10))
TIERS = ["standard", "elite", "boss"]
ARCHETYPES = ["tank", "brute", "assassin", "archer", "mage", "controller", "support"]
MAGIC_ARCHETYPES = {"mage", "controller", "support"}

# Player hit = offensive stat x 1.2 (workhorse skill), same as the back reference
# harness (server-combat/tests/unit/test_player_reference_curve.cpp).
PLAYER_SKILL_MULT = 1.2
# Monster hit = 6 + atk x 100 %, the filler the scaling model was calibrated on
# (monster_scaling_model.json level_curve.calibration.damage_formula).
MOB_BASE_POWER = 6
MOB_SCALING = 1.0
# Healer throughput per turn, in MAG: mix of skill_healer_heal (110 %, 4 turns),
# light_pulse (65 %, 5 turns) and fillers. Assumption, to refine.
HEALER_HEAL_PER_TURN = 0.9

BUILDS = {
    # name: (class, offensive stat, points split per level, armor weight, damage type, weapon family)
    "dps_phys": ("rogue", "atk", {"atk": 3}, "light", "physical", "dagger"),
    "dps_mag": ("mage", "mag", {"mag": 3}, "light", "magic", "staff"),
    "equilibre": ("warrior", "atk", {"hp": 1, "atk": 1, "def": 1}, "medium", "physical", "sword"),
    "tank": ("warrior", "atk", {"hp": 2, "def": 1}, "heavy", "physical", "sword"),
    "healer": ("healer", "mag", {"mag": 2, "hp": 1}, "light", "magic", "scepter"),
}

# Gear quality at a given level. The rank (I to V) follows the level bracket;
# the rarity applies to every rank (common to legendary).
#   rarity: StatRoller roll + template base_stats x rarity_mult + affix count
#   enh: enhancement level, +3 % per level on the template base_stats
GEAR_PROFILES = {
    "mal": {"rarity": "common", "enh": 0},
    "moyen": {"rarity": "rare", "enh": 5},
    "ultra": {"rarity": "legendary", "enh": 20},
}
# Mirrors of hard-coded server values (stat_calculator.hpp, affix_roller.cpp).
RARITY_MULT = {"common": 1.0, "uncommon": 1.1, "rare": 1.25, "epic": 1.5, "legendary": 2.0}
AFFIX_COUNT = {"common": 0.5, "uncommon": 1, "rare": 1.5, "epic": 2.5, "legendary": 3.5}
ENH_PER_LEVEL = 0.03

# Which player each monster archetype hits in a group: the frontline (tank) or
# the backline. Single-target fights always hit the lone player.
BACKLINE_ARCHETYPES = {"assassin", "archer", "mage", "controller"}
# Pack used for the group pressure columns (one of each).
PACK = ["brute", "tank", "assassin", "mage"]


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def interpolate(anchors, level):
    pts = sorted((int(k), float(v)) for k, v in anchors.items() if k.lstrip("-").isdigit())
    if level <= pts[0][0]:
        return pts[0][1]
    if level >= pts[-1][0]:
        return pts[-1][1]
    for (l0, v0), (l1, v1) in zip(pts, pts[1:]):
        if l0 <= level <= l1:
            return v0 + (level - l0) / (l1 - l0) * (v1 - v0)


# ---------------------------------------------------------------- monsters

def monster(model, archetype, tier, level):
    b = model["archetypes_lv1_standard"][archetype]
    caps = model["archetypes_lv1_standard"]["_caps"]
    t = model["tier_multipliers"][tier]
    curve = model["level_curve"]
    c_hp = interpolate(curve["anchors_hp"], level)
    c_off = interpolate(curve["anchors_offense"], level)
    c_def = interpolate(curve["anchors_defense"], level)
    return {
        "hp": max(1, round(b["hp"] * c_hp * t["hp"])),
        "atk": round(b["atk"] * c_off * t["atk"]),
        "def": round(b["def"] * c_def * t["def"]),
        "mr": round(b["magic_resist"] * c_def * t["magic_resist"]),
        "crit": min(caps["crit"], b.get("crit", 0)),
        "crit_dmg": min(caps["crit_damage"], b.get("crit_damage", 150)),
        "armor_pen": min(caps["armor_pen"], b.get("armor_pen", 0)),
        "magic_pen": min(caps["magic_pen"], b.get("magic_pen", 0)),
        "evasion": b.get("evasion", 0),
        "block": b.get("block_chance", 0),
        "dtype": "magic" if archetype in MAGIC_ARCHETYPES else "physical",
    }


# ---------------------------------------------------------------- equipment

SLOTS = [("weapon", False), ("helmet", True), ("chest", True), ("legs", True),
         ("boots", True), ("belt", True), ("cape", True), ("ring_1", False),
         ("ring_2", False), ("necklace", False)]


class Gear:
    def __init__(self):
        self.stats = load("items/equipment_stats.json")
        sc = load("items/equipment_scaling.json")
        self.tiers = [(v["level_range"][0], v["level_range"][1], v["stat_multiplier"],
                       v.get("rate_stat_multiplier", 1.0))
                      for k, v in sc["tier_system"]["tiers"].items() if isinstance(v, dict)]
        self.rate_stats = set(sc["tier_system"].get("rate_stats_no_tier_scaling", []))
        # Continuous level curve (StatRoller::interpolate_curve), in place of the tier steps
        # when present, as on the server.
        curve = sc["tier_system"].get("level_curve") or {}
        self.curves = {k: curve[k] for k in ("stat", "rate") if k in curve}
        self.rarity = {k: v for k, v in sc["rarity_system"]["rarities"].items() if isinstance(v, dict)}
        self.ranges = {}
        for stat, by_rarity in self.stats["stat_ranges_by_rarity"]["main_stats"].items():
            if isinstance(by_rarity, dict):
                for rar, r in by_rarity.items():
                    if isinstance(r, list) and len(r) >= 2:
                        self.ranges.setdefault(rar, {})[stat] = r
        self.sub_mult = self.stats["stat_ranges_by_rarity"].get("substats", {}).get("multiplier", 0.5)
        self.base_items = load("items/equipment.json")["base_items"]
        aff = load("items/affixes.json")
        self.prefixes, self.suffixes = aff["prefixes"], aff["suffixes"]
        self.cache = {}

    def tier_mult(self, level, stat):
        kind = "rate" if stat in self.rate_stats else "stat"
        if kind in self.curves:
            return interpolate({str(lv): m for lv, m in self.curves[kind]}, level)
        for lo, hi, m, rm in self.tiers:
            if lo <= level <= hi:
                return rm if stat in self.rate_stats else m
        return self.tiers[-1][3] if stat in self.rate_stats else self.tiers[-1][2]

    def category(self, slot):
        slot = "ring" if slot.startswith("ring") else slot
        for name, cat in self.stats["equipment_categories"].items():
            if slot in [s.replace("ring_1", "ring").replace("ring_2", "ring") for s in cat.get("slots", [])]:
                return name, cat
        return None, None

    def main_options(self, cat, key):
        src = cat.get("main_stat_by_armor_type") or cat.get("main_stat_options") or cat.get("main_stat_types") or {}
        o = src.get(key) or src.get("default")
        if not o:
            return []
        if "options" in o:
            w = o.get("weights", [1] * len(o["options"]))
            return list(zip(o["options"], w))
        if "stat_split" in o:
            return [(s, 50) for s in o["stat_split"]]
        stat = o.get("main_stat") or o.get("stat")
        return [(stat, 100)] if stat else []

    def roll_value(self, rng, rmin, rmax, tier_mult, rarity):
        rs = self.rarity[rarity]["roll_range_percent"]
        lo, hi = rmin * tier_mult, rmax * tier_mult
        a = round(lo + (hi - lo) * rs["min"] / 100)
        b = round(lo + (hi - lo) * rs["max"] / 100)
        a, b = min(a, b), max(a, b)
        if a != b and a < 1:
            a = 1
        return a if a == b else rng.randint(a, b)

    def template(self, slot, armor_weight, weapon_family, level):
        """base_stats of the equipment.json template for this slot at this level bracket."""
        bracket = min(5, (level - 1) // 20 + 1)
        items = self.base_items
        if slot == "weapon":
            fam = items["weapons"][weapon_family]
            want = f"_b{bracket}"
        elif slot.startswith("ring"):
            fam, want = items["accessories"]["rings"], f"acc_ring_b{bracket}"
        elif slot == "necklace":
            fam, want = items["accessories"]["necklaces"], f"acc_necklace_b{bracket}"
        else:
            key = {"helmet": "head", "boots": "feet"}.get(slot, slot)
            fam, want = items["armor"][key], f"_{armor_weight}_b{bracket}"
        for it in fam:
            if it["id"].endswith(want):
                return it["base_stats"]
        return {}

    def affixes(self, slot, level, count, rng):
        """Expected affix stats: weighted draw without repeat, value x tier multiplier."""
        allowed = {"helmet": "head", "boots": "feet"}.get(slot, slot)
        if slot.startswith("ring") or slot == "necklace":
            allowed = "accessory"
        out = {}
        whole = int(count)
        n = whole + (1 if rng.random() < count - whole else 0)
        pools = [self.prefixes, self.suffixes]
        for i in range(n):
            pool = [a for a in pools[i % 2] if allowed in a.get("allowed_slots", [])
                    and a.get("level_range", [1, 100])[0] <= level <= a.get("level_range", [1, 100])[1]]
            if not pool:
                continue
            a = rng.choices(pool, [x.get("weight", 1) for x in pool])[0]
            for r in a["rolls"]:
                v = (r["min"] + r["max"]) / 2 * self.tier_mult(level, r["stat"])
                out[r["stat"]] = out.get(r["stat"], 0) + v
        return out

    def expected(self, armor_weight, off_stat, profile, level, weapon_family, n=400):
        rarity, enh = GEAR_PROFILES[profile]["rarity"], GEAR_PROFILES[profile]["enh"]
        key = (armor_weight, off_stat, profile, level, weapon_family)
        if key in self.cache:
            return self.cache[key]
        essence = "essence_force" if off_stat == "atk" else "essence_arcane"
        total = {}
        rng = random.Random(level * 7919 + len(armor_weight))
        base_mult = RARITY_MULT[rarity] * (1 + ENH_PER_LEVEL * enh)
        for slot, _ in SLOTS:
            for stat, v in self.template(slot, armor_weight, weapon_family, level).items():
                total[stat] = total.get(stat, 0) + int(v * base_mult)
            for _ in range(n // 4):
                for stat, v in self.affixes(slot, level, AFFIX_COUNT[rarity], rng).items():
                    total[stat] = total.get(stat, 0) + v / (n // 4)
        for slot, is_armor in SLOTS:
            _, cat = self.category(slot)
            lookup = armor_weight if is_armor else (essence if slot == "weapon" else ("ring" if slot.startswith("ring") else slot))
            opts = self.main_options(cat, lookup)
            pool = [(s["stat"], s.get("weight", 10)) if isinstance(s, dict) else (s, 10)
                    for s in cat.get("substat_pool", [])]
            rr = self.rarity[rarity]["substat_count"]
            for _ in range(n):
                main = rng.choices([o[0] for o in opts], [o[1] for o in opts])[0]
                r = self.ranges[rarity].get(main) or self.ranges[rarity].get("default")
                if r:
                    total[main] = total.get(main, 0) + self.roll_value(rng, r[0], r[1], self.tier_mult(level, main), rarity) / n
                p = [(s, w) for s, w in pool if s != main and w > 0]
                for _ in range(min(rng.randint(rr["min"], rr["max"]), len(p))):
                    s = rng.choices([x[0] for x in p], [x[1] for x in p])[0]
                    p = [x for x in p if x[0] != s]
                    r = self.ranges[rarity].get(s) or self.ranges[rarity].get("default") or [1, 5]
                    lo, hi = max(1, round(r[0] * self.sub_mult)), round(r[1] * self.sub_mult)
                    total[s] = total.get(s, 0) + self.roll_value(rng, lo, hi, self.tier_mult(level, s), rarity) / n
        self.cache[key] = total
        return total


# ---------------------------------------------------------------- players

def player(data, gear, build, level, profile="moyen"):
    cls, off, split, aw, dtype, weapon = BUILDS[build]
    base, growth = data["base"][cls], data["growth"][cls]
    pv = data["point_values"]
    pts = data["points_per_level"] * (level - 1)
    alloc = {k: pts * v / sum(split.values()) for k, v in split.items()}

    def bg(k):
        return base.get(k, 0) + math.floor(growth.get(k, 0) * (level - 1))

    hp = bg("hp") + alloc.get("hp", 0) * pv["hp"]
    atk = bg("atk") + alloc.get("atk", 0) * pv["atk"]
    mag = bg("mag") + alloc.get("mag", 0) * pv["mag"]
    armor = bg("armor") + alloc.get("def", 0) * pv["def"]
    mr = bg("magic_resist") + 0.2 * mag
    g = gear.expected(aw, off, profile, level, weapon)
    hp += g.get("hp", 0)
    atk = (atk + g.get("atk", 0)) * (1 + g.get("atk_percent", 0) / 100)
    mag = (mag + g.get("mag", 0)) * (1 + g.get("mag_percent", 0) / 100)
    armor = (armor + g.get("armor", 0)) * (1 + g.get("def_percent", 0) / 100)
    mr = (mr + g.get("magic_resist", 0)) * (1 + g.get("def_percent", 0) / 100)
    crit = min(100, base.get("crit", 5) + g.get("crit", 0))
    crit_dmg = base.get("crit_dmg", 150) + g.get("crit_dmg", 0)
    return {
        "hp": hp, "off": atk if off == "atk" else mag, "mag": mag, "armor": armor, "mr": mr,
        "crit": crit, "crit_dmg": crit_dmg,
        "armor_pen": min(70, g.get("armor_pen", 0)), "magic_pen": min(70, g.get("magic_pen", 0)),
        "dmg_pct": g.get("damage_percent", 0), "dr": g.get("damage_reduction", 0),
        "evasion": min(75, base.get("flee", 0) + g.get("flee", 0)), "dtype": dtype,
    }


def mitig(defense, pen):
    eff = defense * (1 - min(70, pen) / 100)
    return 100 / (100 + eff) if eff > 0 else 1.0


def crit_factor(crit, crit_dmg):
    return 1 + min(100, crit) / 100 * (crit_dmg - 100) / 100


def player_hit(p, m):
    raw = p["off"] * PLAYER_SKILL_MULT * crit_factor(p["crit"], p["crit_dmg"]) * (1 + p["dmg_pct"] / 100)
    if p["dtype"] == "physical":
        raw *= mitig(m["def"], p["armor_pen"]) * (1 - m["block"] / 100 * 0.5)
    else:
        raw *= mitig(m["mr"], p["magic_pen"])
    return raw * (1 - m["evasion"] / 100)


def mob_hit(m, p):
    raw = (MOB_BASE_POWER + m["atk"] * MOB_SCALING) * crit_factor(m["crit"], m["crit_dmg"])
    raw *= mitig(p["armor"], m["armor_pen"]) if m["dtype"] == "physical" else mitig(p["mr"], m["magic_pen"])
    return raw * (1 - p["dr"] / 100) * (1 - p["evasion"] / 100)


# ---------------------------------------------------------------- matrix

def main():
    model = load("config/monster_scaling_model.json")
    prog = load("systems/progression.json")["stat_allocation"]
    data = {
        "base": load("stats/class_base_stats.json"),
        "growth": load("stats/class_growth.json"),
        "point_values": prog["point_values"],
        "points_per_level": prog["points_per_level"],
    }
    gear = Gear()
    OUT.mkdir(exist_ok=True)
    rows = []
    for profile in GEAR_PROFILES:
        for level in LEVELS:
            players = {b: player(data, gear, b, level, profile) for b in BUILDS}
            t, h = players["tank"], players["healer"]
            heal = HEALER_HEAL_PER_TURN * h["mag"] * crit_factor(h["crit"], h["crit_dmg"])
            for tier in TIERS:
                for arch in ARCHETYPES:
                    m = monster(model, arch, tier, level)
                    row = {"gear": profile, "level": level, "tier": tier, "archetype": arch,
                           "mob_hp": m["hp"], "mob_atk": m["atk"]}
                    for b, p in players.items():
                        ttk = m["hp"] / max(0.1, player_hit(p, m))
                        hit = mob_hit(m, p)
                        ttd = p["hp"] / max(0.1, hit)
                        r = ttd / ttk
                        row[f"{b}_hit_taken"] = round(hit)
                        row[f"{b}_ttk"] = round(ttk, 1)
                        row[f"{b}_ttd"] = round(ttd, 1)
                        row[f"{b}_R"] = round(r, 2)
                        row[f"{b}_M"] = round(math.sqrt(1 / r), 2)
                    # Group of 4 vs this monster alone: it hits the tank if it is a frontline
                    # archetype, the healer otherwise (backline divers go for the healer).
                    group_dps = sum(player_hit(players[b], m) for b in ("dps_phys", "dps_mag", "tank")) \
                        + 0.3 * player_hit(h, m)
                    target = h if arch in BACKLINE_ARCHETYPES else t
                    taken = mob_hit(m, target)
                    row["group_target"] = "healer" if target is h else "tank"
                    row["group_ttk"] = round(m["hp"] / group_dps, 1)
                    row["group_heal_cover_pct"] = round(100 * heal / max(0.1, taken))
                    rows.append(row)
                # Pack pressure: one of each PACK archetype at this tier, split front / back.
                front = sum(mob_hit(monster(model, a, tier, level), t) for a in PACK if a not in BACKLINE_ARCHETYPES)
                back = sum(mob_hit(monster(model, a, tier, level), h) for a in PACK if a in BACKLINE_ARCHETYPES)
                for row in rows[-len(ARCHETYPES):]:
                    row["pack_front_dmg"] = round(front)
                    row["pack_back_dmg"] = round(back)
                    row["pack_heal_cover_pct"] = round(100 * heal / (front + back))
                    row["healer_turns_to_die_vs_pack_back"] = round(h["hp"] / back, 1)
            print(f"{profile:5} lv{level:3d}  " + "  ".join(
                f"{b}: hp {p['hp']:.0f} off {p['off']:.0f} arm {p['armor']:.0f} mr {p['mr']:.0f} crit {p['crit']:.0f}"
                for b, p in players.items() if b in ("dps_phys", "tank", "healer")))
    path = OUT / "pve_matrix.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} rows -> {path}")


if __name__ == "__main__":
    main()
