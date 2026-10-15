"""Souffle cost per skill rank (mana_cost_per_level) for base and tier-2 class skills.

Rule (see _meta/carnet/souffle_par_niveau.md):

    mana_cost_per_level = round_half_up( mana_cost x (G - 1) / 9 )

where G is the LIVE power gain of the skill from rank 1 to rank 10, so that the cost at
rank 10 is mana_cost x G: the Souffle paid per unit of effect stays the same at every
rank. G is read from the skill data, with the same per-rank fields the server applies:

  - main scaling: (P + 9 x percent_per_level) / P, P = scaling_percent or
    heal_scaling_percent. Only counted when rank_scaling_enabled is true (otherwise
    room.cpp effective_scaling ignores percent_per_level, unless the BE1 env gate is on);
  - each effect: product of its (pct, pct_per_level), (value, value_per_level) and
    (duration, duration_per_level) gains (room.cpp applies those on every path);
  - G = the largest of these gains (1.0 when nothing grows: the skill costs the same at
    every rank, since there is nothing more to pay for).

Scope: classes/<6 classes>/skills.json, base_skills and subclass_skills.<sub>.skills,
mana_cost > 0, max_level != 1. Tier 3 is NOT written: --report compares it to the rule.

Usage (from the repo root):
    python -X utf8 scripts/balance/souffle_per_level.py            # apply
    python -X utf8 scripts/balance/souffle_per_level.py --check    # exit 1 if a value differs
    python -X utf8 scripts/balance/souffle_per_level.py --report   # per-skill table + tier-3 review
    python -X utf8 scripts/balance/souffle_per_level.py --budget   # Souffle budget model, levels 1-100

Edits are textual (one number per skill, or one inserted line when the field is absent),
so formatting and line endings are preserved. The "Coût : N Souffle à tous les rangs."
sentence of a description is rewritten when the skill now costs more per rank.
"""
import argparse
import json
import math
import re
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLASSES = ["warrior", "mage", "healer", "archer", "rogue", "artisan"]
MAX_RANK = 10


def round_half_up(x):
    return int(math.floor(x + 0.5))


# ---------------------------------------------------------------- data

def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def iter_skills(cls):
    """Yield (scope, subclass, spec, skill) for every class skill of the file."""
    d = load(f"classes/{cls}/skills.json")
    for s in d.get("base_skills", []):
        yield "BASE", "", "", s
    for sub, sd in d.get("subclass_skills", {}).items():
        for s in sd.get("skills", []):
            yield "SUBCLASS", sub, "", s
        for spec, td in (sd.get("tier3") or {}).items():
            for s in td.get("skills", []):
                yield "TIER3", sub, spec, s


def power_gain(s, live=True):
    """Rank-10 / rank-1 power ratio, from the per-rank fields the server applies."""
    g = 1.0
    main = (s.get("scaling_percent") or 0) or (s.get("heal_scaling_percent") or 0)
    ppl = s.get("percent_per_level") or 0
    if main > 0 and ppl > 0 and (s.get("rank_scaling_enabled") or not live):
        g = max(g, (main + (MAX_RANK - 1) * ppl) / main)
    for e in s.get("effects") or []:
        eg = 1.0
        for base_key, per_key in (("pct", "pct_per_level"), ("value", "value_per_level"),
                                  ("duration", "duration_per_level")):
            base, per = e.get(base_key) or 0, e.get(per_key) or 0
            if isinstance(base, (int, float)) and base > 0 and per:
                eg *= (base + (MAX_RANK - 1) * per) / base
        g = max(g, eg)
    return g


def in_scope(scope, s):
    return (scope in ("BASE", "SUBCLASS") and (s.get("mana_cost") or 0) > 0
            and s.get("max_level", MAX_RANK) != 1)


def rule(s, live=True):
    return round_half_up(s["mana_cost"] * (power_gain(s, live) - 1) / (MAX_RANK - 1))


def cost(s, rank, mpl=None):
    m = (s.get("mana_cost_per_level") or 0) if mpl is None else mpl
    return s["mana_cost"] + m * (rank - 1)


def targets():
    """{class: {skill_id: new_mpl}} for every in-scope skill."""
    out = {}
    for cls in CLASSES:
        out[cls] = {s["id"]: rule(s) for scope, _, _, s in iter_skills(cls) if in_scope(scope, s)}
    return out


# ---------------------------------------------------------------- text edit

def object_span(text, idx):
    """Span of the innermost JSON object that contains position idx."""
    depth, i, in_str = 0, idx, False
    # walk backwards to the opening brace (skills hold no braces inside strings before "id")
    while i >= 0:
        c = text[i]
        if c == "}":
            depth += 1
        elif c == "{":
            if depth == 0:
                break
            depth -= 1
        i -= 1
    start = i
    depth, j = 0, start
    while j < len(text):
        c = text[j]
        if in_str:
            if c == "\\":
                j += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return start, j + 1
        j += 1
    raise ValueError("unbalanced JSON object")


DESC_FR = re.compile(r"Coût : (\d+) Souffle à tous les rangs\.")
DESC_EN = re.compile(r"Cost: (\d+) Breath at every rank\.")


def edit_skill(block, mpl, nl):
    """Return block with mana_cost_per_level = mpl (and its cost sentence updated)."""
    m = re.search(r'("mana_cost_per_level"\s*:\s*)(-?\d+)', block)
    if m:
        if int(m.group(2)) != mpl:
            block = block[:m.start(2)] + str(mpl) + block[m.end(2):]
    else:
        mc = re.search(r'^([ \t]*)"mana_cost"\s*:\s*\d+,[ \t]*' + re.escape(nl), block, re.M)
        if not mc:
            raise ValueError("no mana_cost line to anchor the insertion")
        line = f'{mc.group(1)}"mana_cost_per_level": {mpl},{nl}'
        block = block[:mc.end()] + line + block[mc.end():]
    if mpl > 0:
        block = DESC_FR.sub(lambda x: f"Coût : {x.group(1)} Souffle (+{mpl} par rang).", block)
        block = DESC_EN.sub(lambda x: f"Cost: {x.group(1)} Breath (+{mpl} per rank).", block)
    return block


def apply(check_only):
    tg = targets()
    diffs = []
    for cls in CLASSES:
        path = ROOT / f"classes/{cls}/skills.json"
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        nl = "\r\n" if "\r\n" in text else "\n"
        new = text
        current = {s["id"]: s for _, _, _, s in iter_skills(cls)}
        for sid, mpl in tg[cls].items():
            have = current[sid].get("mana_cost_per_level")
            stale_text = mpl > 0 and any(DESC_FR.search(current[sid].get(k) or "") or DESC_EN.search(current[sid].get(k) or "")
                                         for k in ("description_fr", "description_en"))
            if have == mpl and not stale_text:
                continue
            diffs.append((cls, sid, have, mpl))
            if check_only:
                continue
            hits = [m.start() for m in re.finditer(r'"id"\s*:\s*"' + re.escape(sid) + '"', new)]
            if len(hits) != 1:
                raise ValueError(f"{sid}: {len(hits)} occurrences of its id")
            a, b = object_span(new, hits[0])
            if json.loads(new[a:b]).get("id") != sid:
                raise ValueError(f"{sid}: object span does not match the skill")
            new = new[:a] + edit_skill(new[a:b], mpl, nl) + new[b:]
        if not check_only and new != text:
            json.loads(new)  # still valid JSON
            path.write_bytes(new.encode("utf-8"))
    if not check_only:
        tg2 = targets()
        for cls in CLASSES:
            got = {s["id"]: s.get("mana_cost_per_level") for scope, _, _, s in iter_skills(cls) if in_scope(scope, s)}
            bad = [k for k, v in tg2[cls].items() if got.get(k) != v]
            if bad:
                raise SystemExit(f"post-check failed for {cls}: {bad}")
    return diffs


# ---------------------------------------------------------------- report

def report():
    print("| classe | sort | scope | tier | cout niv1 | G (niv10/niv1) | +/niv | cout niv10 |")
    print("|---|---|---|---|---|---|---|---|")
    for cls in CLASSES:
        for scope, sub, _, s in iter_skills(cls):
            if not in_scope(scope, s):
                continue
            m = rule(s)
            print(f"| {cls} | {s['id'][6:]} | {scope if scope == 'BASE' else sub} | {s.get('tier')} | "
                  f"{s['mana_cost']} | {power_gain(s):.2f} | {m} | {cost(s, 10, m)} |")
    print("\n## Tier 3 against the rule")
    seen, rows = set(), []
    for cls in CLASSES:
        for scope, sub, spec, s in iter_skills(cls):
            if scope != "TIER3" or s["id"] in seen or (s.get("mana_cost") or 0) <= 0:
                continue
            seen.add(s["id"])
            rows.append((cls, spec, s, power_gain(s, live=True), power_gain(s, live=False)))
    no_live = [r for r in rows if r[3] <= 1.0001 and (r[2].get("mana_cost_per_level") or 0) > 0]
    no_gain = [r for r in rows if r[4] <= 1.0001 and (r[2].get("mana_cost_per_level") or 0) > 0]
    zero = [r for r in rows if (r[2].get("mana_cost_per_level") or 0) == 0]
    print(f"tier-3 paid skills: {len(rows)}")
    print(f"  mana_cost_per_level 0: {len(zero)} -> " + ", ".join(r[2]['id'] for r in zero))
    print(f"  paying per rank with NO per-rank gain at all: {len(no_gain)} -> "
          + ", ".join(r[2]['id'] for r in no_gain))
    print(f"  paying per rank, gain only through percent_per_level WITHOUT rank_scaling_enabled "
          f"(inert unless BE1_PER_LEVEL_SCALING): {len(no_live) - len(no_gain)}")
    by_cost = {}
    for cls, spec, s, gl, gd in rows:
        if gd > 1.0001 and (s.get("mana_cost_per_level") or 0) > 0:
            c10 = cost(s, 10) / s["mana_cost"]
            by_cost.setdefault(s["mana_cost"], []).append((c10, gd, s.get("mana_cost_per_level"), rule(s, live=False)))
    print("  cost x(niv10/niv1) vs design power gain, by base cost (rule value with BE1 on):")
    for mc in sorted(by_cost):
        v = by_cost[mc]
        print(f"    cost {mc:3}: n={len(v):3} cost x{st.median(x[0] for x in v):.2f}  power x{st.median(x[1] for x in v):.2f}"
              f"  data +{st.median(x[2] for x in v):g}/niv  rule +{st.median(x[3] for x in v):g}/niv")


# ---------------------------------------------------------------- budget model

LEVELS = [1, 20, 40, 60, 100]
ARMOR = {"warrior": "heavy", "mage": "light", "healer": "light", "archer": "medium", "rogue": "medium", "artisan": "medium"}
OFF = {"warrior": "atk", "mage": "mag", "healer": "mag", "archer": "atk", "rogue": "atk", "artisan": "atk"}
WEAPON = {"warrior": "sword", "mage": "staff", "healer": "scepter", "archer": "bow", "rogue": "dagger", "artisan": "sword"}
# Expected gear (pve_matrix.GEAR_PROFILES): common +0 while levelling, rare +5 from level 40.
GEAR_AT = {1: "mal", 20: "mal", 40: "moyen", 60: "moyen", 100: "moyen"}
# Typical skill ranks (base, tier 2, tier 3): 1 point per level, base unlocked at 1,
# tier 2 at 20, tier 3 at 60 (skill_system.json). Sums: 20, 40, 60, 100 points.
RANKS = {1: (1, 0, 0), 20: (4, 0, 0), 40: (6, 2, 0), 60: (8, 4, 0), 100: (8, 6, 6)}
GCD = 2.0


def _budget_tools():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import pve_matrix as P

    class Gear(P.Gear):
        """pve_matrix.Gear plus the per-armor-weight substat multipliers (2026-09-28)."""
        def __init__(self, weight):
            super().__init__()
            arm = self.stats["equipment_categories"]["armor"]
            mult = arm.get("substat_weight_multipliers", {}).get(weight, {})
            arm["substat_pool"] = [dict(s, weight=s["weight"] * mult.get(s["stat"], 1)) for s in arm["substat_pool"]]
    return P, Gear


def fight_durations(P, level):
    """Seconds, from monster HP (config/monster_scaling_model.json, median of the 7
    archetypes) and the reference player damage per GCD (level_curve.calibration,
    socle + passifs + gear). Group content = 3 damage dealers."""
    model = load("config/monster_scaling_model.json")
    ref = model["level_curve"]["calibration"]["player_ref_equilibre"]["dps_per_turn"]
    dpt = P.interpolate(ref, level)
    hp = {t: st.median(P.monster(model, a, t, level)["hp"] for a in P.ARCHETYPES) for t in P.TIERS}
    std, elite, boss = (hp[t] / dpt * GCD for t in ("standard", "elite", "boss"))
    return {
        "pack": 2.5 * std,                                   # 1-2 star: 2-3 standard mobs, solo
        "elite": elite + 2 * std,                            # 3 star: 1 elite + 2 standard, solo
        "boss": boss / 3,                                    # dungeon boss, group of 3 damage dealers
        "5star": 1.25 * (boss + 3 * elite + 5 * std) / 3,    # 1 boss 3 elites 5 standard, +25% HP, group
    }


def kits(cls):
    d = load(f"classes/{cls}/skills.json")
    for sub, sd in d["subclass_skills"].items():
        for spec, td in sd["tier3"].items():
            yield d["base_skills"], sd["skills"], td["skills"]


def spells(kit, level, use_rule):
    out = []
    for group, rank in zip(kit, RANKS[level]):
        if rank <= 0:
            continue
        for s in group:
            if (s.get("mana_cost") or 0) <= 0 or s.get("max_level", MAX_RANK) == 1:
                continue
            m = s.get("mana_cost_per_level") or 0
            if s.get("source_scope") != "TIER3":
                m = rule(s) if use_rule else 0
            out.append((cost(s, rank, m), float(s.get("cooldown") or 0), float(s.get("cast_time") or 0),
                        s.get("tier") == "filler"))
    return out


def demand(sp, dur=120.0):
    """Souffle per second of a sustained rotation: every GCD, the most expensive ready
    skill (fillers last), with an unlimited pool."""
    t, spent, ready = 0.0, 0, [0.0] * len(sp)
    order = sorted(range(len(sp)), key=lambda i: (sp[i][3], -sp[i][0]))
    while t < dur:
        ok = [i for i in order if ready[i] <= t + 1e-9]
        if ok:
            i = ok[0]
            spent += sp[i][0]
            ready[i] = t + sp[i][1]
            t += max(GCD, sp[i][2])
        else:
            t = min(ready)
    return spent / dur


def budget():
    P, Gear = _budget_tools()
    base, growth = load("stats/class_base_stats.json"), load("stats/class_growth.json")
    pv = load("config/game.json")["stats_definition"]["mp"]["point_value"]
    gears = {}
    for level in LEVELS:
        fd = fight_durations(P, level)
        print(f"\n### Niveau {level}  (sorts de base rang {RANKS[level][0]}, tier 2 rang {RANKS[level][1]}, "
              f"tier 3 rang {RANKS[level][2]} ; equipement {GEAR_AT[level]})")
        print("Durees (s) : " + ", ".join(f"{k} {v:.0f}" for k, v in fd.items()))
        print("| classe | Souffle max (0 pt) | Souffle max (1 pt/niv) | regen /s | rotation /s avant -> apres "
              "| a sec apres (0 pt) | a sec apres (1 pt/niv) | plein hors combat | plus gros sort / max |")
        print("|---|---|---|---|---|---|---|---|---|")
        for cls in CLASSES:
            w = ARMOR[cls]
            gears.setdefault(w, Gear(w))
            g = gears[w].expected(w, OFF[cls], GEAR_AT[level], level, WEAPON[cls], n=200)
            b, gr = base[cls], growth[cls]
            pool0 = b["mp"] + math.floor(gr["mp"] * (level - 1)) + g.get("mp", 0)
            pool1 = pool0 + (level - 1) * pv
            regen = b["mp_regen"] + gr.get("mp_regen", 0) * (level - 1) + round(g.get("mp_regen", 0))
            ks = list(kits(cls))
            d0 = st.median(demand(spells(k, level, False)) for k in ks)
            d1 = st.median(demand(spells(k, level, True)) for k in ks)
            big = st.median(max(x[0] for x in spells(k, level, True)) for k in ks)

            def tte(pool):
                return "jamais" if d1 <= regen else f"{pool / (d1 - regen):.0f} s"
            print(f"| {cls} | {pool0:.0f} | {pool1:.0f} | {regen:.0f} | {d0:.1f} -> {d1:.1f} | {tte(pool0)} | "
                  f"{tte(pool1)} | {pool0 / regen:.0f} s | {big / pool0:.0%} |")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="report differences, write nothing, exit 1 if any")
    ap.add_argument("--report", action="store_true", help="per-skill table and tier-3 review")
    ap.add_argument("--budget", action="store_true", help="Souffle budget model by level")
    a = ap.parse_args()
    if a.report:
        report()
        return
    if a.budget:
        budget()
        return
    diffs = apply(check_only=a.check)
    for cls, sid, have, mpl in diffs:
        print(f"{cls:8} {sid:48} {have!s:>5} -> {mpl}")
    n = sum(len(v) for v in targets().values())
    print(f"{len(diffs)} skill(s) {'to change' if a.check else 'changed'}, {n} in scope.")
    if a.check and diffs:
        sys.exit(1)


if __name__ == "__main__":
    main()
