"""Monster stats V2 proposal: species base (lv1) x level growth x tier.

    stat(monster, L) = species_lv1[stat] x growth(stat, archetype, L) x tier_mult

1. species_lv1 = archetype lv1 profile (config/monster_scaling_model.json)
   x species factor. The factor keeps each species' identity from the hand-made
   base_stats in entities/monsters.json: it is the monster's value divided by
   what a typical monster of the SAME archetype and tier would have at its
   base_level (log-linear fit over the roster). A golem with factor 1.4 on HP
   is 40% tankier than a typical tank, at every level. Rates (crit, pen,
   tenacity...) keep the species' own value when it has one, else the
   archetype default.
2. Core stats (hp, atk, mag, armor, magic_resist) follow the level curves of
   the scaling model (anchors_hp / anchors_offense / anchors_defense).
3. Rate stats grow additively every 10 levels, generic + per-archetype bonus,
   clamped by caps (RATE_GROWTH below, a proposal to discuss).

Output: out/monster_stats_v2.csv (one row per monster) and the growth tables
printed on stdout. Read-only on the game data.
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"

CORE = ["hp", "atk", "armor", "magic_resist"]
MAGIC_ARCHETYPES = {"mage", "controller", "support"}
RATES = ["crit", "crit_damage", "armor_pen", "magic_pen", "shield_pierce",
         "evasion", "block_chance", "parry_chance", "tenacity", "lifesteal", "reflect"]
# Species keys in monsters.json base_stats -> V2 names.
SPECIES_RATE_KEYS = {"crit_chance": "crit", "crit_damage": "crit_damage", "armor_pen": "armor_pen",
                     "magic_pen": "magic_pen", "evasion": "evasion", "block_chance": "block_chance",
                     "parry_chance": "parry_chance", "lifesteal_percent": "lifesteal",
                     "reflect_percent": "reflect", "tenacity": "tenacity", "shield_pierce": "shield_pierce"}

# Rate growth per 10 levels: generic for everyone + archetype bonus. PROPOSAL.
RATE_GROWTH_GENERIC = {"crit": 0.5, "tenacity": 1.0}
RATE_GROWTH_ARCHETYPE = {
    "tank":       {"tenacity": 3.0, "block_chance": 1.5, "parry_chance": 0.5},
    "brute":      {"armor_pen": 2.0, "shield_pierce": 1.5, "crit_damage": 3.0, "tenacity": 1.0},
    "assassin":   {"crit": 1.5, "crit_damage": 4.0, "evasion": 1.0, "armor_pen": 1.0},
    "archer":     {"crit": 1.0, "crit_damage": 3.0, "armor_pen": 2.0},
    "mage":       {"magic_pen": 2.5, "crit_damage": 2.0},
    "controller": {"tenacity": 2.0, "magic_pen": 1.5},
    "support":    {"tenacity": 2.0, "magic_pen": 0.5},
}
CAPS = {"crit": 60, "crit_damage": 220, "armor_pen": 70, "magic_pen": 70, "shield_pierce": 60,
        "evasion": 40, "block_chance": 50, "parry_chance": 25, "tenacity": 80,
        "lifesteal": 30, "reflect": 30}
SHOW_LEVELS = [1, 5, 10, 30, 50, 100]
FACTOR_CLAMP = (0.4, 2.5)


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def interpolate(anchors, level):
    pts = sorted((int(k), float(v)) for k, v in anchors.items() if k.isdigit())
    if level <= pts[0][0]:
        return pts[0][1]
    if level >= pts[-1][0]:
        return pts[-1][1]
    for (l0, v0), (l1, v1) in zip(pts, pts[1:]):
        if l0 <= level <= l1:
            return v0 + (level - l0) / (l1 - l0) * (v1 - v0)


def fit(rows):
    """Least squares log(v) = c[arch,tier] + b*log(level). Returns predict(arch, tier, level)."""
    groups = sorted({(r[0], r[1]) for r in rows})
    gi = {g: i for i, g in enumerate(groups)}
    n = len(groups) + 1
    # Normal equations, small dense system solved by Gaussian elimination.
    ata = [[0.0] * n for _ in range(n)]
    aty = [0.0] * n
    for arch, tier, lvl, v in rows:
        x = [0.0] * n
        x[gi[(arch, tier)]] = 1.0
        x[-1] = math.log(max(1, lvl))
        y = math.log(v)
        for i in range(n):
            aty[i] += x[i] * y
            for j in range(n):
                ata[i][j] += x[i] * x[j]
    for i in range(n):
        ata[i][i] += 1e-6
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(ata[r][c]))
        ata[c], ata[p] = ata[p], ata[c]
        aty[c], aty[p] = aty[p], aty[c]
        for r in range(n):
            if r != c and ata[c][c]:
                f = ata[r][c] / ata[c][c]
                for k in range(c, n):
                    ata[r][k] -= f * ata[c][k]
                aty[r] -= f * aty[c]
    coef = [aty[i] / ata[i][i] for i in range(n)]
    fallback = sum(coef[:-1]) / max(1, len(coef) - 1)

    def predict(arch, tier, lvl):
        c = coef[gi[(arch, tier)]] if (arch, tier) in gi else fallback
        return math.exp(c + coef[-1] * math.log(max(1, lvl)))
    return predict


def main():
    model = load("config/monster_scaling_model.json")
    arch_lv1 = {k: v for k, v in model["archetypes_lv1_standard"].items() if not k.startswith("_")}
    tiers = model["tier_multipliers"]
    curve = model["level_curve"]
    curve_of = {"hp": curve["anchors_hp"], "atk": curve["anchors_offense"], "mag": curve["anchors_offense"],
                "armor": curve["anchors_defense"], "magic_resist": curve["anchors_defense"]}
    # low_level_relief (2026-10-22): world monsters only, the scripted tutorial fights opt out.
    relief = curve.get("low_level_relief", {})
    relief_hp = relief.get("hp", {"1": 1.0})
    relief_atk = relief.get("atk", {"1": 1.0})
    mons = load("entities/monsters.json")["monsters"]

    def raw(m, stat):
        b = m.get("base_stats", {})
        if stat == "armor":
            return b.get("armor", b.get("def"))
        if stat == "atk":  # offensive identity: the higher of atk/mag
            return max(b.get("atk", 0) or 0, b.get("mag", 0) or 0)
        return b.get(stat)

    usable = [m for m in mons if m.get("stat_archetype") in arch_lv1 and m.get("base_stats", {}).get("hp", 0) < 99999]
    predictors = {}
    for stat in CORE:
        rows = [(m["stat_archetype"], m.get("threat_tier", "standard"), m.get("base_level", 1), raw(m, stat))
                for m in usable if (raw(m, stat) or 0) > 0]
        predictors[stat] = fit(rows)

    OUT.mkdir(exist_ok=True)
    out_rows = []
    for m in mons:
        arch = m.get("stat_archetype")
        if arch not in arch_lv1:
            continue
        tier = m.get("threat_tier", "standard")
        lvl = m.get("base_level", 1)
        a = arch_lv1[arch]
        row = {"id": m["id"], "name_fr": m.get("name_fr", ""), "archetype": arch, "tier": tier,
               "base_level": lvl, "roster_status": m.get("roster_status", "")}
        flags = []
        lv1 = {}
        for stat in CORE:
            v = raw(m, stat)
            if v and v > 0 and m in usable:
                f = v / predictors[stat](arch, tier, lvl)
            else:
                f = 1.0
                flags.append(f"{stat}:absent")
            if not FACTOR_CLAMP[0] <= f <= FACTOR_CLAMP[1]:
                flags.append(f"{stat}:clamp{f:.2f}")
                f = min(FACTOR_CLAMP[1], max(FACTOR_CLAMP[0], f))
            row[f"f_{stat}"] = round(f, 2)
            base_key = {"armor": "def"}.get(stat, stat)
            lv1[stat] = a[base_key] * f
        # Offense split: magical archetypes put it on MAG, physical ones on ATK.
        off = lv1.pop("atk")
        lv1["atk"], lv1["mag"] = (off * 0.3, off) if arch in MAGIC_ARCHETYPES else (off, 0.0)
        species = m.get("base_stats", {})
        for stat in RATES:
            own = next((species[k] for k, v in SPECIES_RATE_KEYS.items() if v == stat and k in species), None)
            dflt = a.get({"crit": "crit"}.get(stat, stat), 0) or 0
            lv1[stat] = own if own is not None else dflt
        for k in ["hp", "atk", "mag", "armor", "magic_resist"] + RATES:
            row[f"lv1_{k}"] = round(lv1[k], 1)
        tm = tiers.get(tier, tiers["standard"])
        tmult = {"hp": tm["hp"], "atk": tm["atk"], "mag": tm["atk"], "armor": tm["def"],
                 "magic_resist": tm["magic_resist"]}
        today = raw(m, "hp")
        for L in SHOW_LEVELS + [lvl]:
            row[f"hp@{L}"] = round(lv1["hp"] * interpolate(curve_of["hp"], L) * tmult["hp"]
                                   * interpolate(relief_hp, L))
            row[f"off@{L}"] = round(max(lv1["atk"], lv1["mag"]) * interpolate(curve_of["atk"], L) * tmult["atk"]
                                    * interpolate(relief_atk, L))
        row["hp_today_at_base_level"] = today
        row["flags"] = " ".join(flags)
        out_rows.append(row)

    keys = list(out_rows[0].keys())
    for r in out_rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    path = OUT / "monster_stats_v2.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)
    print(f"{len(out_rows)} monsters -> {path}")

    print("\nLevel ratio (x lv1):")
    print(" lvl " + " ".join(f"{L:>6}" for L in [1, 2, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]))
    for name, key in [("hp", "hp"), ("atk/mag", "atk"), ("armor/mr", "armor")]:
        print(f" {name:8}" + " ".join(f"{interpolate(curve_of[key], L):6.1f}"
                                     for L in [1, 2, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]))

    print("\nRate stats lv1 -> lv50 -> lv100 per archetype (with caps):")
    for arch, a in arch_lv1.items():
        parts = []
        for stat in RATES:
            g = RATE_GROWTH_GENERIC.get(stat, 0) + RATE_GROWTH_ARCHETYPE.get(arch, {}).get(stat, 0)
            base = a.get(stat, 0) or 0
            if g or base:
                v50 = min(CAPS[stat], base + g * 4.9)
                v100 = min(CAPS[stat], base + g * 9.9)
                parts.append(f"{stat} {base:g}->{v50:.0f}->{v100:.0f}")
        print(f" {arch:10} " + ", ".join(parts))


if __name__ == "__main__":
    main()
