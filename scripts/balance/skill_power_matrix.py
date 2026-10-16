"""Skill power matrix: one power value per class skill and per rank, from what the server does.

Owner of every weight: config/skill_power_model.json (no weight lives here). Note:
_meta/carnet/matrice_sorts.md. Skill iteration, kits, rank cost and Souffle families come
from souffle_per_level.py (one owner each).

Power unit: 1 point = 1 % of the caster's offensive stat dealt as damage to one target.
Components (points, per cast): degats, dot, soin, hot, bouclier, controle, buff_offensif,
buff_defensif, debuff_offensif, debuff_defensif, utilitaire. Raw power = their sum; net
power = raw minus the cast cost (time past the GCD, expected interruption loss).

Usage (from the repo root):
    python -X utf8 scripts/balance/skill_power_matrix.py            # write out/skill_power_matrix.json
    python -X utf8 scripts/balance/skill_power_matrix.py --check    # exit 1 if the file is stale
    python -X utf8 scripts/balance/skill_power_matrix.py --report   # inconsistencies, distributions, spam
"""
import argparse
import json
import math
import re
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import souffle_per_level as S  # noqa: E402  (iter_skills, kits, family, cost, MAX_RANK, TIERS)

ROOT = S.ROOT
OUT = Path(__file__).resolve().parent / "out" / "skill_power_matrix.json"
load = S.load

M = load("config/skill_power_model.json")
COMBAT = load("config/combat.json")["settings"]
GAME = load("config/game.json")
ROLES_CFG = load("config/roles.json")
PATTERNS = load("combat/targeting.json")["patterns"]
STATUS = {k: dict(e, category=c) for c, es in load("stats/status_effects.json")["effects"].items()
          for k, e in es.items() if not k.startswith("_")}
BASE, GROWTH = load("stats/class_base_stats.json"), load("stats/class_growth.json")

GCD = COMBAT["gcd_duration"]
CDR_CAP = COMBAT["abilities"]["cooldown_reduction_cap"] / 100
REF = M["reference"]
REF_DPS = REF["reference_hit_percent"] / GCD          # points per second of an ordinary action
GRID = GAME["combat_grids"]["available"][GAME["combat_grids"]["default"]]
SIDE_ROWS, COLS = GRID["rows"] // 2, GRID["cols"]
SKILL_BAR = GAME["skill_bar"]["slots_count"]
RANKS = range(1, S.MAX_RANK + 1)
COMPONENTS = ["degats", "dot", "soin", "hot", "bouclier", "controle", "buff_offensif",
              "buff_defensif", "debuff_offensif", "debuff_defensif", "utilitaire"]
HOSTILE_TYPES = ("physical", "magical", "magic")
SOUFFLE_KEYS = ["_souffle_self", "_souffle_ally"]   # Souffle given, by receiver, before conversion
ALLY_TARGETS = ("ally", "allies", "all", "self")


def pub(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}


# ---------------------------------------------------------------- class stats

def class_stats(cls):
    """Stats at the reference level (base + floor(growth x (level-1)), as the server builds)."""
    lv = REF["reference_level"]
    return {k: v + math.floor(GROWTH[cls].get(k, 0) * (lv - 1))
            for k, v in BASE[cls].items() if isinstance(v, (int, float))}


def offense_stat(cls):
    b = BASE[cls]
    return "atk" if b["atk"] >= b["mag"] else "mag"


def ratio(cls, stat):
    """Value of 1 % of `stat` in % of the class's offensive stat."""
    cs = class_stats(cls)
    alias = {"max_hp": "hp", "caster_max_hp": "hp", "target_max_hp": "hp", "max_mp": "mp",
             "caster_max_mp": "mp", "caster_def": "def", "caster_mag": "mag", "magic_power": "mag"}
    return cs[alias.get(stat, stat)] / cs[offense_stat(cls)]


def damage_stat(dtype):
    return "atk" if dtype == "physical" else "mag"   # room.cpp: anything else is magic


# ---------------------------------------------------------------- geometry

def reach(r):
    """Enemy cells within Manhattan range r, caster at its front row, central column."""
    col = (COLS - 1) // 2
    return sum(1 for dr in range(SIDE_ROWS) for c in range(COLS) if 1 + dr + abs(c - col) <= r)


def pattern_cells(pid):
    p = PATTERNS.get(pid) or PATTERNS["single"]
    t = p.get("tiles")
    if isinstance(t, list):
        return t
    if t == "all":
        return [[r, c] for r in range(SIDE_ROWS) for c in range(COLS)]
    return None  # dynamic: chain / random / adjacent


def area(n):
    return math.sqrt(min(n, M["targets"]["area_cell_cap"]))


def targets(s, side, distinct=False):
    """distinct: count each target once (effects), even when hits may repeat on it."""
    """Expected number of targets on `side` ('enemy' or 'ally') for the skill's pattern."""
    T = M["targets"]
    pid = s["pattern"]
    p = PATTERNS.get(pid) or PATTERNS["single"]
    if s["target"] == "self" and side == "ally":
        return 1.0
    if pid == "single" or pid not in PATTERNS:
        return 1.0
    cells = pattern_cells(pid)
    if cells is None:
        n = s.get("chain_bounces") or p.get("bounces") or p.get("random_targets") or (
            (1 if p.get("include_center") else 0) + p.get("random_adjacent", 0)) or 1
        return float(n) if p.get("can_repeat_targets") and not distinct else float(min(n, T["entity_cap"]))
    if side == "ally":
        return float(T["ally_group_size"]) if pid == "all" else area(len(cells))
    if s.get("range") == 0:   # nova centred on the caster, caster at the front
        top = max(r for r, _ in cells)
        cells = [c for c in cells if c[0] > top - T["nova_enemy_rows"]] if top > 0 else []
        return area(len(cells)) if cells else 0.0
    return area(len(cells))


def base_range(s):
    for k in (s.get("tier3_id"), s.get("subclass_id"), s.get("base_class_id")):
        if k and k in ROLES_CFG:
            return ROLES_CFG[k]["base_range"]
    raise KeyError(f"{s['id']}: no base_range in config/roles.json")


def reach_factor(s):
    R = M["reach"]
    if s["damage_type"] not in HOSTILE_TYPES and s["target"] not in ("enemy", "enemies", "self_and_enemies"):
        return 1.0   # beneficial: no range test (room.cpp is_valid_target)
    br = base_range(s)
    rng = s.get("range", -1)
    if rng == 0:
        return 1.0
    placement = rng if rng > 0 else (max(br, R["aoe_range_floor"]) if s["pattern"] != "single" else br)
    f = (reach(placement) / reach(br)) ** R["exponent"]
    t = s.get("targeting") or {}
    p = PATTERNS.get(s["pattern"], {})
    los = (t.get("requires_line_of_sight") or (s["pattern"] != "single" and p.get("needs_los"))) \
        and not t.get("bypasses_los")
    return f * (R["line_of_sight_factor"] if los else 1.0)


# ---------------------------------------------------------------- effects

def at_rank(e, key, rank):
    return (e.get(key) or 0) + (e.get(key + "_per_level") or 0) * (rank - 1)


def duration(e, rank):
    d = at_rank(e, "duration", rank)
    if d <= 0:
        d = M["dot"]["default_duration_by_category"].get(STATUS.get(e["stat"], {}).get("category"), 0)
    cap = re.search(r"max (\d+(?:\.\d+)?)s", STATUS.get(e["stat"], {}).get("formula", ""))
    return min(d, float(cap.group(1))) if cap and STATUS[e["stat"]]["category"] in ("control", "aggro") else d


def stacks(e, d):
    return min(e.get("stacks_to_apply") or 1, d.get("max_stacks") or 1)


def receiver(s, e):
    """'self', 'ally' or 'enemy': who receives the effect."""
    t = e.get("target")
    if t == "self":
        return "self"
    if t in ("allies", "ally", "all_allies"):
        return "ally"
    if t in ("enemies", "enemy", "repeated_target"):
        return "enemy"
    if s["target"] == "self":
        return "self"
    hostile = s["target"] in ("enemy", "enemies", "self_and_enemies")
    if e["type"] == "debuff":
        return "enemy" if hostile else "self"
    if e["type"] == "buff":
        return "self" if hostile else "ally"
    return "enemy" if hostile else "ally"


def n_receivers(s, who):
    if who == "self":
        return 1.0
    return targets(s, "enemy" if who == "enemy" else "ally", distinct=True) * (reach_factor(s) if who == "enemy" else 1.0)


def tick_coef(d):
    """(coefficient per tick per stack in % of a stat, stat) from the status definition."""
    rt = d.get("runtime", {})
    f = d.get("formula", "")
    if rt.get("tick_percent"):
        return rt["tick_percent"] * 100, rt.get("scaling_stat")
    if rt.get("scaling_percent"):
        return rt["scaling_percent"] * 100, rt.get("scaling_stat", "mag")
    m = re.search(r"\b(ATK|MAG)\s*\*\s*([\d.]+)", f)
    if m:
        return float(m.group(2)) * 100, m.group(1).lower()
    m = re.search(r"([\d.]+)%\s*max HP", f)
    if m:
        return float(m.group(1)), "target_max_hp_enemy"
    m = re.search(r"max_MP\s*\*\s*([\d.]+)", f)
    if m:
        return float(m.group(1)) * 100, "max_mp"
    return None, None


def stat_mod_magnitude(expr, key, e, d, cls, rank):
    """Signed magnitude in % points of the receiver's stat, or None if not a number."""
    canonical = d.get("value_per_stack") is not None
    val = stacks(e, d) * d["value_per_stack"] if canonical else at_rank(e, "value", rank)
    if isinstance(expr, (int, float)):
        mag = expr * 100 if key.endswith("_percent") else expr
    elif isinstance(expr, str) and "value" in expr:
        mag = -val if expr.startswith("-") else val
        if key == "bonus_magic_flat":     # enchanted_blade: value + pct % MAG
            return at_rank(e, "pct", rank) + val / class_stats(cls)["mag"] * 100
    else:
        return None
    ref = pub(M["modifiers"]["flat_reference_stat"]).get(key, "")
    if ref:
        mag = mag / class_stats(cls)[ref] * 100
    return mag


def price_effect(s, e, cls, rank, comp, unpriced, damage_points):
    stat = e["stat"]
    d = STATUS.get(stat, {})
    cat = d.get("category")
    rt = d.get("runtime", {})
    who = receiver(s, e)
    n = n_receivers(s, who)
    dur = duration(e, rank)
    sp = M["special_effects"]
    ovh = M["heal_and_shield"]["overheal_factor"]

    if e["type"] == "utility" or stat in pub(sp["per_cast"]):
        if stat in pub(sp["per_cast"]):
            c = sp["per_cast"][stat]
            if e.get("target") not in sp["per_cast_area_targets"]:   # room.cpp: primary target only
                n = reach_factor(s) if who == "enemy" else 1.0
            comp[c["component"]] += c["points"] * n
        elif stat == "resurrect":
            comp["soin"] += sp["resurrect_points_at_full_hp"] * min(at_rank(e, "value", rank), 100) / 100
        elif stat == "lifesteal":
            comp[sp["lifesteal_component"]] += damage_points * at_rank(e, "value", rank) / 100 * ovh
        elif stat in ("mana_restore", "mana_steal"):
            v = at_rank(e, "value", rank)
            if e.get("scaling") == "caster_max_mp":
                v = v / 100 * class_stats(cls)["mp"]
            elif e.get("scaling") in ("mag", "atk"):
                v = v / 100 * class_stats(cls)[e["scaling"]]
            comp["_souffle_" + ("ally" if stat == "mana_restore" and who == "ally" else "self")] += \
                v * (n if stat == "mana_restore" else 1)
        else:
            unpriced.append(stat)
        return

    if cat in ("dot", "hot"):
        coef, base_stat = tick_coef(d)
        if coef is None and cat == "hot":   # heal_over_time_mag / _max_hp: value + pct % stat
            coef, base_stat = at_rank(e, "pct", rank), rt.get("scaling_stat")
        if coef is None:
            unpriced.append(stat)
            return
        tick = d.get("tick_interval") or rt.get("tick_rate") or 1.0
        ticks = dur / tick
        if rt.get("scaling_behavior") == "ramp":
            per = sum(coef + rt["ramp_per_tick"] * 100 * i for i in range(int(ticks))) / max(ticks, 1)
        else:
            per = coef
        if base_stat == "target_max_hp_enemy":
            per *= M["dot"]["percent_of_target_max_hp_to_points"]
            conv = 1.0
        else:
            conv = ratio(cls, base_stat)
        total = per * conv * stacks(e, d) * ticks * n
        if rt.get("on_expire") == "explosion":
            total *= 1 + rt.get("explosion_percent", 0)
        if cat == "dot":
            comp["dot"] += total
        else:
            comp["hot"] += total * ovh
        return

    if stat.startswith("shield"):
        if rt.get("scaling_stat"):
            pts = at_rank(e, "pct", rank) * ratio(cls, rt["scaling_stat"])
        else:
            pts = 0.0
        pts += at_rank(e, "value", rank) / class_stats(cls)[offense_stat(cls)] * 100
        comp["bouclier"] += pts * n * ovh
        return

    priced_mods = set(rt.get("stat_mods") or {}) & set(pub(M["modifiers"]["by_stat_mod"]))
    if cat in ("control", "aggro") and (rt.get("cc_type") or cat == "aggro") and not priced_mods:
        # a control that only moves a priced stat (blind: accuracy - value %) is a debuff, below
        C = M["control"]
        if rt.get("gcd_penalty_seconds_per_stack"):
            frac = rt["gcd_penalty_seconds_per_stack"] * stacks(e, d) / GCD
            comp["controle"] += frac * dur * REF_DPS * n
        else:
            eff = C["hard_efficiency"] if rt.get("blocks_skills") else C["soft_efficiency"]
            comp[C["component_by_category"].get(cat, "controle")] += eff * dur * REF_DPS * n
        return

    if stat in pub(sp["per_second"]):
        c = sp["per_second"][stat]
        pts = c["points"] if "points" in c else c["points_per_value"] * at_rank(e, "value", rank)
        comp[c["component"]] += pts * dur * n
        return

    if stat == "mana_regen":
        coef, _ = tick_coef(d)
        comp["_souffle_" + ("ally" if who == "ally" else "self")] += \
            coef / 100 * class_stats(cls)["mp"] * stacks(e, d) * dur * n
        return

    mods = rt.get("stat_mods") or M["modifiers"]["implicit_stat_mods"].get(stat) or {}
    priced = False
    for key, expr in mods.items():
        cfg = M["modifiers"]["by_stat_mod"].get(key)
        if cfg is None:
            continue
        mag = stat_mod_magnitude(expr, key, e, d, cls, rank)
        if mag is None:
            continue
        priced = True
        good = -mag if key in M["modifiers"]["harmful_when_positive"] else mag   # good for the receiver
        pts = good / 100 * REF_DPS * cfg["efficiency"] * dur * n
        if who == "enemy":
            comp["debuff_offensif" if cfg["axis"] == "defense" else "debuff_defensif"] += -pts
        else:
            comp["buff_offensif" if cfg["axis"] == "offense" else "buff_defensif"] += pts
    if not priced:
        unpriced.append(stat)


# ---------------------------------------------------------------- skill power

def scaling_at(s, base, rank):
    if not base:
        return 0.0
    return base + ((s.get("percent_per_level") or 0) * (rank - 1) if s.get("rank_scaling_enabled") else 0)


def direct_damage(s, cls, rank):
    if s["damage_type"] not in HOSTILE_TYPES:
        return 0.0
    D = M["damage"]
    stat = damage_stat(s["damage_type"])
    pct = scaling_at(s, s.get("scaling_percent", 100), rank) + \
        (s.get("base_power") or 0) / class_stats(cls)[stat] * 100
    pct *= ratio(cls, stat)
    hits = max(1, s.get("hit_count") or 1)
    ramp = s.get("damage_per_hit_bonus") or 0
    per_hit = sum(1 + ramp * i / 100 for i in range(hits))
    bonus = 1 + (s.get("execute_bonus_percent") or 0) / 100 * D["execute_uptime"]
    for f, up in pub(D["conditional_bonus_uptime"]).items():
        bonus += (s.get(f) or 0) / 100 * up
    n = targets(s, "enemy")
    bounce = s.get("damage_percent_per_bounce") or 0
    if bounce and n > 1:
        n = sum(1 + bounce * i / 100 for i in range(int(round(n))))
    return pct * per_hit * bonus * n * reach_factor(s)


def components(s, cls, rank):
    comp = dict.fromkeys(COMPONENTS + SOUFFLE_KEYS, 0.0)
    unpriced = []
    comp["degats"] = direct_damage(s, cls, rank)
    if "heal_scaling_percent" in s:
        side = "self" if s["target"] == "self" else "ally"
        pct = scaling_at(s, s["heal_scaling_percent"], rank) + \
            s.get("base_heal", 1) / class_stats(cls)["mag"] * 100
        comp["soin"] += pct * ratio(cls, "mag") * n_receivers(s, side) * M["heal_and_shield"]["overheal_factor"]
    if s.get("self_heal_percent"):
        comp["soin"] += comp["degats"] * s["self_heal_percent"] / 100 * M["heal_and_shield"]["overheal_factor"]
    for e in s.get("effects") or []:
        price_effect(s, e, cls, rank, comp, unpriced, comp["degats"])
    return comp, unpriced


def cast_cost(s, cast=None):
    """Points lost to casting; `cast` overrides the skill's cast_time (what-if)."""
    c = (s.get("cast_time") or 0) if cast is None else cast
    C = M["casting"]
    return max(0.0, c - GCD) * C["time_cost_per_second"] + C["interrupt_rate_per_second"] * c * c * REF_DPS


def dominant(comp):
    groups = pub(M["roles"]["components"])
    score = {g: sum(max(0.0, comp[k]) for k in ks) for g, ks in groups.items()}
    return max(score, key=lambda g: (score[g], g)) if any(score.values()) else "utilitaire"


def role(s, palier, dom):
    for name in M["roles"]["order"]:
        r = M["roles"]["rules"][name]
        field = [k for k in ("tier", "tag") if k in r]
        ok = not field or s["tier"] in r.get("tier", []) or bool(set(s.get("tags") or []) & set(r.get("tag", [])))
        ok = ok and (not r.get("palier") or palier in r["palier"])
        ok = ok and (not r.get("dominant") or dom in r["dominant"])
        if ok:
            return name
    raise ValueError(f"{s['id']}: no role (roles.order needs a catch-all)")


def all_skills():
    """[(class, palier, subclass, spec, skill)], each skill once."""
    out, seen = [], set()
    for cls in S.CLASSES:
        for palier, sub, spec, s in S.iter_skills(cls):
            if s["id"] not in seen:
                seen.add(s["id"])
                out.append((cls, palier, sub, spec, s))
    return out


def r2(x):
    return round(x, 1)


def build():
    rows, unpriced_all = [], {}
    raw = {}
    for cls, palier, sub, spec, s in all_skills():
        per_rank = [components(s, cls, r) for r in RANKS]
        raw[s["id"]] = (cls, palier, sub, spec, s, per_rank)
        for u in per_rank[0][1]:
            unpriced_all.setdefault(u, []).append(s["id"])
    # Souffle -> points at the median yield of the roster (rank 1, paying skills, Souffle excluded)
    yields = [sum(v for k, v in pr[0][0].items() if k in COMPONENTS) / s["mana_cost"]
              for cls, _, _, _, s, pr in raw.values() if (s.get("mana_cost") or 0) > 0]
    yields = [y for y in yields if y > 0]
    pts_per_souffle = st.median(yields)
    for sid, (cls, palier, sub, spec, s, per_rank) in raw.items():
        powers, comp1 = [], None
        for comp, _ in per_rank:
            sp = M["special_effects"]
            for key in SOUFFLE_KEYS:
                comp[sp["souffle_component"][key.rsplit("_", 1)[1]]] += \
                    comp.pop(key) * pts_per_souffle * sp["souffle_value_factor"]
            powers.append(sum(comp.values()))
            comp1 = comp1 or comp
        dom = dominant(comp1)
        rl = role(s, palier, dom)
        cc = cast_cost(s)
        cost1, costm = S.cost(s, 1), S.cost(s, S.MAX_RANK)
        rows.append({
            "id": sid, "class": cls, "palier": palier, "subclass": sub, "spec": spec,
            "tier": s["tier"], "target": s["target"], "range": s.get("range", -1), "souffle_family": S.family(s), "role": rl, "dominant": dom,
            "cooldown": s["cooldown"], "cast_time": s.get("cast_time") or 0,
            "mana_cost_r1": cost1, f"mana_cost_r{S.MAX_RANK}": costm,
            "targets_enemy": r2(targets(s, "enemy")) if s["damage_type"] in HOSTILE_TYPES else 0,
            "reach_factor": round(reach_factor(s), 3),
            "components_r1": {k: r2(v) for k, v in comp1.items() if abs(v) >= 0.05},
            "power": [r2(p) for p in powers],
            "cast_cost": r2(cc),
            "net_power_r1": r2(powers[0] - cc), f"net_power_r{S.MAX_RANK}": r2(powers[-1] - cc),
            "density_r1": r2(powers[0] / s["cooldown"]) if s["cooldown"] else None,
            "souffle_per_100_power_r1": r2(cost1 / powers[0] * 100) if powers[0] > 0 else None,
        })
    return {
        "_meta": {
            "generated_by": "scripts/balance/skill_power_matrix.py",
            "model": "config/skill_power_model.json",
            "unit": M["_meta"]["unit"],
            "points_per_souffle_median": round(pts_per_souffle, 3),
            "reference_dps_points_per_second": REF_DPS,
            "unpriced_effects": {k: sorted(v) for k, v in sorted(unpriced_all.items())},
        },
        "skills": sorted(rows, key=lambda r: r["id"]),
    }


# ---------------------------------------------------------------- report

def q(v, p):
    v = sorted(v)
    if not v:
        return float("nan")
    k = (len(v) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def spam_fraction(kit, cdr, dur):
    """Share of combat time spent casting non-filler skills, greedy (most powerful ready
    first), Souffle unlimited. kit = [(cooldown, cast, power)]."""
    t, busy, ready = 0.0, 0.0, [0.0] * len(kit)
    order = sorted(range(len(kit)), key=lambda i: -kit[i][2])
    while t < dur:
        ok = [i for i in order if ready[i] <= t + 1e-9]
        if ok:
            i = ok[0]
            ready[i] = t + kit[i][0] * (1 - cdr)
            step = max(GCD, kit[i][1])
            busy += min(step, dur - t)
            t += step
        else:
            t += GCD   # a filler (or nothing) fills this GCD
    return busy / dur


def kit_rows(rows):
    by = {r["id"]: r for r in rows}
    out = []
    for cls in S.CLASSES:
        for sub, spec, kit in S.kits(cls):
            out.append((cls, sub, spec, {t: [by[s["id"]] for s in kit[t]] for t in S.TIERS}))
    return out


# Skill bars by level band: the tiers unlocked (config/skill_system.json skill_categories).
LEVEL_BARS = (("niv 20-59 (base + sous-classe)", S.TIERS[:2]), ("niv 60+ (15 sorts)", S.TIERS))


def bar(kit, tiers):
    """Non-filler skills of the kit's unlocked tiers that fill the skill bar, shortest
    cooldowns first (the worst case for spam)."""
    sk = [r for t in tiers for r in kit[t] if r["role"] != "remplissage"]
    return sorted(sk, key=lambda r: r["cooldown"])[:SKILL_BAR]


def kit_load(rows, cdr=0.0, weight=None):
    """Sum of max(GCD, cast) / cooldown: above 1, a non-filler skill is always ready.
    weight(row), when given, scales each skill's share (skill_timing: reactive skills)."""
    return sum(max(GCD, r["cast_time"]) / (r["cooldown"] * (1 - cdr)) * (weight(r) if weight else 1.0)
               for r in rows)


def fmt_dist(v, thresholds):
    return (f"{len(v)} | {q(v, .25):g} | {q(v, .5):g} | {q(v, .75):g} | "
            + " | ".join(f"{sum(x < th for x in v) / len(v):.0%}" for th in thresholds))


def report(data):
    rows = data["skills"]
    R = M["report"]
    th = R["cooldown_thresholds_seconds"]
    p1 = lambda r: r["power"][0]
    pm = lambda r: r["power"][-1]
    print(f"# Matrice de puissance des sorts ({len(rows)} sorts)\n")
    print(f"Unite : % de la stat offensive en degats sur une cible. Debit de reference {REF_DPS:g} pts/s. "
          f"1 Souffle = {data['_meta']['points_per_souffle_median']} pts (mediane mesuree).\n")

    print("## Roles\n")
    print("| role | n | paliers | puissance r1 (q1/med/q3) | puissance r10 med | cooldown med | cast med | Souffle r1 med |")
    print("|---|---|---|---|---|---|---|---|")
    for rl in M["roles"]["order"]:
        g = [r for r in rows if r["role"] == rl]
        if not g:
            continue
        pal = {p: sum(r["palier"] == p for r in g) for p in S.TIERS}
        print(f"| {rl} | {len(g)} | {' / '.join(f'{k} {v}' for k, v in pal.items() if v)} | "
              f"{q([p1(r) for r in g], .25):.0f} / {q([p1(r) for r in g], .5):.0f} / {q([p1(r) for r in g], .75):.0f} | "
              f"{q([pm(r) for r in g], .5):.0f} | {q([r['cooldown'] for r in g], .5):g} | "
              f"{q([r['cast_time'] for r in g], .5):g} | {q([r['mana_cost_r1'] for r in g], .5):g} |")

    print("\n## Cooldowns hors remplissage (s) : n | q1 | mediane | q3 | " + " | ".join(f"< {t} s" for t in th))
    print("\n| groupe | n | q1 | med | q3 | " + " | ".join(f"< {t} s" for t in th) + " |")
    print("|---|---|---|---|---|" + "---|" * len(th))
    nf = [r for r in rows if r["role"] != "remplissage"]
    print(f"| tous, CDR 0 | {fmt_dist([r['cooldown'] for r in nf], th)} |")
    print(f"| tous, CDR {CDR_CAP:.0%} | {fmt_dist([r['cooldown'] * (1 - CDR_CAP) for r in nf], th)} |")
    for p in S.TIERS:
        g = [r["cooldown"] for r in nf if r["palier"] == p]
        print(f"| palier {p} | {fmt_dist(g, th)} |")
    for rl in M["roles"]["order"]:
        g = [r["cooldown"] for r in nf if r["role"] == rl]
        if g:
            print(f"| role {rl} | {fmt_dist(g, th)} |")
    for t in sorted({r["tier"] for r in nf}):
        g = [r["cooldown"] for r in nf if r["tier"] == t]
        print(f"| tier {t} | {fmt_dist(g, th)} |")

    print(f"\n## Enchainement de sorts hors remplissage (GCD {GCD:g} s, barre de {SKILL_BAR} cases, Souffle illimite)\n")
    print("Part du temps de combat passee a lancer des sorts hors remplissage, en lancant a chaque GCD le plus "
          "puissant pret. Charge = somme(max(GCD, cast) / cooldown) : au-dela de 1, il y a TOUJOURS un sort "
          "hors remplissage pret.\n")
    print("| kit | CDR | charge med (min-max) | part du temps med | q1 | q3 | kits a 100 % |")
    print("|---|---|---|---|---|---|---|")
    kits = kit_rows(rows)
    dur = R["spam_duration_seconds"]
    spam_detail = {}
    for label, tiers in LEVEL_BARS:
        for cdr in (0.0, CDR_CAP):
            fr, ch = [], []
            for cls, sub, spec, kit in kits:
                sk = bar(kit, tiers)
                ch.append(kit_load(sk, cdr))
                fr.append(spam_fraction([(r["cooldown"], r["cast_time"], p1(r)) for r in sk], cdr, dur))
                spam_detail[(label, cdr, spec)] = fr[-1]
            print(f"| {label} | {cdr:.0%} | {q(ch, .5):.2f} ({min(ch):.2f}-{max(ch):.2f}) | {q(fr, .5):.0%} | "
                  f"{q(fr, .25):.0%} | {q(fr, .75):.0%} | {sum(f >= 0.999 for f in fr)}/{len(fr)} |")

    print("\n## Incoherences\n")
    pr = [p1(r) for r in rows]
    strong, top = q(pr, R["strong_power_quantile"]), q(pr, R["top_power_quantile"])
    mn = R["min_power_for_comparison"]

    print(f"### 1. Meme cout, puissance tres differente (ratio >= {R['same_cost_power_ratio']:g}, puissance >= {mn})\n")
    by_cost = {}
    for r in rows:
        if p1(r) >= mn and r["mana_cost_r1"] > 0:
            by_cost.setdefault(r["mana_cost_r1"], []).append(r)
    pairs = []
    for c, g in by_cost.items():
        lo, hi = min(g, key=p1), max(g, key=p1)
        if p1(hi) / p1(lo) >= R["same_cost_power_ratio"]:
            pairs.append((p1(hi) / p1(lo), c, lo, hi, len(g)))
    for ratio_, c, lo, hi, n in sorted(pairs, key=lambda x: -x[0])[:R["top_n"]]:
        print(f"- Souffle {c} ({n} sorts) : {hi['id']} {p1(hi):.0f} ({hi['role']}, CD {hi['cooldown']:g}) "
              f"vs {lo['id']} {p1(lo):.0f} ({lo['role']}, CD {lo['cooldown']:g}) : x{ratio_:.1f}")
    print(f"\n{len(pairs)} couts sur {len(by_cost)} portent un ecart >= x{R['same_cost_power_ratio']:g}.")
    same = {}
    for r in rows:
        if p1(r) >= mn and r["mana_cost_r1"] > 0:
            same.setdefault((r["mana_cost_r1"], r["role"]), []).append(r)
    sp = sorted(((p1(max(g, key=p1)) / p1(min(g, key=p1)), k, min(g, key=p1), max(g, key=p1))
                 for k, g in same.items() if len(g) > 1), key=lambda x: -x[0])
    print(f"\nA role egal (meme cout ET meme role), ecart >= x{R['same_cost_power_ratio']:g} : "
          f"{sum(x[0] >= R['same_cost_power_ratio'] for x in sp)} groupes sur {len(sp)}.")
    for ratio_, (c, rl), lo, hi in sp[:R["top_n"]]:
        if ratio_ < R["same_cost_power_ratio"]:
            break
        print(f"- {rl}, Souffle {c} : {hi['id']} {p1(hi):.0f} (CD {hi['cooldown']:g}, cast {hi['cast_time']:g}) "
              f"vs {lo['id']} {p1(lo):.0f} (CD {lo['cooldown']:g}, cast {lo['cast_time']:g}) : x{ratio_:.1f}")

    print(f"\n### 2. Tres puissants a cooldown court (puissance r1 >= q{R['strong_power_quantile'] * 100:.0f} = {strong:.0f}, "
          f"CD < {R['short_cooldown_seconds']} s)\n")
    g = sorted([r for r in rows if p1(r) >= strong and r["cooldown"] < R["short_cooldown_seconds"]],
               key=lambda r: -p1(r) / r["cooldown"])
    for r in g[:R["top_n"]]:
        print(f"- {r['id']} ({r['role']}, {r['palier']}) : {p1(r):.0f} pts toutes les {r['cooldown']:g} s "
              f"(densite {p1(r) / r['cooldown']:.1f}/s, {r['dominant']})")
    print(f"\n{len(g)} sorts. Au-dessus du q{R['top_power_quantile'] * 100:.0f} ({top:.0f} pts) : "
          f"{sum(1 for r in rows if p1(r) >= top)} sorts, dont {sum(1 for r in rows if p1(r) >= top and r['cooldown'] < R['ultimate_min_cooldown_seconds'])} "
          f"a CD < {R['ultimate_min_cooldown_seconds']} s.")
    ult = [r for r in rows if r["role"] == "ultime"]
    print(f"\nUltimes (signatures de specialisation) : {len(ult)}, CD {min(r['cooldown'] for r in ult):g}-"
          f"{max(r['cooldown'] for r in ult):g} s, mediane {q([r['cooldown'] for r in ult], .5):g} s ; "
          f"{sum(r['cooldown'] < R['ultimate_min_cooldown_seconds'] for r in ult)} sous {R['ultimate_min_cooldown_seconds']} s. "
          f"Sorts non ultimes plus puissants que l'ultime median ({q([p1(r) for r in ult], .5):.0f}) : "
          f"{sum(1 for r in rows if r['role'] != 'ultime' and p1(r) > q([p1(x) for x in ult], .5))}.")
    dens = sorted([r for r in rows if r["role"] != "remplissage"], key=lambda r: -r["density_r1"])
    print(f"\nDensite (puissance r1 / cooldown, pts/s ; debit de reference {REF_DPS:g}) hors remplissage, les plus fortes :")
    for r in dens[:R["top_n"]]:
        print(f"- {r['id']} ({r['role']}, {r['palier']}) : {r['density_r1']:.1f}/s = {p1(r):.0f} pts / {r['cooldown']:g} s")
    hot = sorted([r for r in rows if r["role"] != "ultime" and p1(r) >= top], key=lambda r: r["cooldown"])
    print("\nSorts non ultimes du top puissance, CD le plus court d'abord :")
    for r in hot[:R["top_n"]]:
        print(f"- {r['id']} ({r['role']}, {r['palier']}) : {p1(r):.0f} pts, CD {r['cooldown']:g} s, cast {r['cast_time']:g} s")

    print("\n### 3. Temps d'incantation et puissance\n")
    cast = [r for r in rows if r["cast_time"] > 0]
    def rank_of(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0] * len(v)
        for i, j in enumerate(o):
            rk[j] = i
        return rk
    if len(cast) > 2:
        a, b = rank_of([p1(r) for r in cast]), rank_of([r["cast_time"] for r in cast])
        rho = st.correlation(a, b)
        print(f"{len(cast)} sorts incantes. Correlation de rang puissance / cast : {rho:.2f}.")
    med = q(pr, .5)
    low = sorted([r for r in cast if r["cast_time"] > GCD and p1(r) < med], key=p1)
    print(f"\nCast au-dela du GCD pour une puissance sous la mediane ({med:.0f}) : {len(low)}")
    for r in low[:R["top_n"]]:
        print(f"- {r['id']} ({r['role']}) : cast {r['cast_time']:g} s, {p1(r):.0f} pts")
    free = sorted([r for r in rows if r["cast_time"] <= GCD and p1(r) >= top], key=lambda r: -p1(r))
    print(f"\nPuissance >= q{R['top_power_quantile'] * 100:.0f} ({top:.0f}) sans cast au-dela du GCD : {len(free)} "
          f"(dont {sum(r['cast_time'] == 0 for r in free)} instantanes)")
    for r in free[:R["top_n"]]:
        print(f"- {r['id']} ({r['role']}, {r['class']}) : {p1(r):.0f} pts, cast {r['cast_time']:g} s, CD {r['cooldown']:g} s")

    print(f"\n### 4. Souffle par 100 points de puissance, hors norme par palier et role (bande x{R['cost_per_power_band'][0]:g}-x{R['cost_per_power_band'][1]:g} de la mediane)\n")
    groups = {}
    for r in rows:
        if r["souffle_per_100_power_r1"] and p1(r) >= mn:
            groups.setdefault((r["palier"], r["role"]), []).append(r)
    print("| palier | role | n | Souffle / 100 pts (q1/med/q3) |")
    print("|---|---|---|---|")
    out = []
    for (pal, rl), g in sorted(groups.items()):
        v = [r["souffle_per_100_power_r1"] for r in g]
        m_ = q(v, .5)
        print(f"| {pal} | {rl} | {len(g)} | {q(v, .25):.1f} / {m_:.1f} / {q(v, .75):.1f} |")
        for r in g:
            x = r["souffle_per_100_power_r1"] / m_
            if not R["cost_per_power_band"][0] <= x <= R["cost_per_power_band"][1]:
                out.append((x, r, m_))
    print(f"\n{len(out)} sorts hors bande. Les plus ecartes :")
    for x, r, m_ in sorted(out, key=lambda t: -abs(math.log(t[0])))[:R["top_n"]]:
        print(f"- {r['id']} ({r['palier']}, {r['role']}) : {r['souffle_per_100_power_r1']:.1f} Souffle/100 pts, "
              f"x{x:.2f} la mediane ({m_:.1f}) ; cout {r['mana_cost_r1']}, {p1(r):.0f} pts")

    nova = [r for r in rows if r["target"] == "self_and_enemies" and r["range"] != 0]
    print(f"\n### 5. Novas centrees sur le lanceur posees au plancher de zone "
          f"(target self_and_enemies sans range 0) : {len(nova)}\n")
    for r in nova:
        print(f"- {r['id']} : posee a max(base_range, {M['reach']['aoe_range_floor']}), "
              f"facteur de portee x{r['reach_factor']:g}, {p1(r):.0f} pts")
    print("\n### 6. Champs morts cote serveur encore presents dans la data\n")
    for f in M["server_dead_fields"]["fields"]:
        n = sum(1 for *_, s in all_skills() if f in s)
        print(f"- {f} : {n} sorts")
    print("\n### 7. Effets non prices par le modele\n")
    for k, v in data["_meta"]["unpriced_effects"].items():
        print(f"- {k} : {len(v)} sorts ({', '.join(v[:4])}{'...' if len(v) > 4 else ''})")


# ---------------------------------------------------------------- main

def dump(data):
    return json.dumps(data, ensure_ascii=False, indent=1, sort_keys=False) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the generated matrix is stale")
    ap.add_argument("--report", action="store_true", help="inconsistencies, distributions, spam")
    a = ap.parse_args()
    data = build()
    text = dump(data)
    if a.report:
        report(data)
        return
    if a.check:
        have = OUT.read_bytes().decode("utf-8").replace("\r\n", "\n") if OUT.exists() else ""
        if have != text:
            print(f"{OUT.relative_to(ROOT)} is stale: run python -X utf8 scripts/balance/skill_power_matrix.py")
            sys.exit(1)
        print(f"{OUT.relative_to(ROOT)} up to date ({len(data['skills'])} skills).")
        return
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(text.encode("utf-8"))
    print(f"wrote {OUT.relative_to(ROOT)} ({len(data['skills'])} skills)")


if __name__ == "__main__":
    main()
