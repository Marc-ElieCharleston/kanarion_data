"""Souffle cost of class skills: rank-1 price by tier, per-rank cost by power.

Rules (owner: config/skill_system.json mana_cost_scaling; note: _meta/carnet/souffle_par_niveau.md):

  per_rank_rule   mana_cost_per_level = round_half_up( mana_cost x (G - 1) / (max_level - 1) )
                  G = power gain of the skill from rank 1 to max rank, from the per-rank
                  fields the server applies (percent_per_level on scaling_percent or
                  heal_scaling_percent; pct/value/duration_per_level of each effect; the
                  largest). A skill carrying percent_per_level carries rank_scaling_enabled
                  (room.cpp effective_scaling ignores the gain without it).
  tier_order      at rank 1, within a kit (base + subclass + specialization), a skill costs
                  strictly less than the most expensive skill of its family at the nearest
                  higher tier that has one; above that, its mana_cost is brought to that
                  ceiling minus 1. Checked as well: the median of each family rises strictly
                  from tier to tier, at rank 1 and at max rank.
  no copy         a description never restates the cost (the client shows mana fields).

Scope: classes/<6 classes>/skills.json, base, subclass and tier-3 skills, mana_cost > 0,
max_level != 1.

Usage (from the repo root):
    python -X utf8 scripts/balance/souffle_per_level.py            # apply
    python -X utf8 scripts/balance/souffle_per_level.py --check    # exit 1 if a rule fails
    python -X utf8 scripts/balance/souffle_per_level.py --report   # per-skill and per-tier tables
    python -X utf8 scripts/balance/souffle_per_level.py --budget   # Souffle budget model, levels 1-100
                    (out of combat: mp_regen_out_of_combat with and without the Pass, systems/premium.json;
                    the most useful Breath-regen set a character of the level can wear, items/panoplies.json;
                    regen in % of max (mp_regen_percent) and the rank rule rank_system.regen_forms: per-class
                    ceilings at level 100, the percent sets against them, the deviations to settle;
                    phase 3 autonomy by range, config/skill_system.json mana_cost_scaling.autonomy_by_range)

Edits are textual (one number per field, one inserted line for a missing field, one
sentence removed), so formatting and line endings are preserved.
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


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


SKILL_SYSTEM = load("config/skill_system.json")
MAX_RANK = SKILL_SYSTEM["skill_levels"]["max_level"]
TIER_ORDER = SKILL_SYSTEM["mana_cost_scaling"]["tier_order"]
TIERS = TIER_ORDER["tiers"]
FAMILIES = {k: v for k, v in TIER_ORDER["families"].items() if not k.startswith("_")}


def round_half_up(x):
    return int(math.floor(x + 0.5))


# ---------------------------------------------------------------- data

def iter_skills(cls):
    """Yield (tier, subclass, spec, skill) for every class skill of the file. tier is a
    skill_system.json skill_categories key."""
    d = load(f"classes/{cls}/skills.json")
    for s in d.get("base_skills", []):
        yield "base", "", "", s
    for sub, sd in d.get("subclass_skills", {}).items():
        for s in sd.get("skills", []):
            yield "subclass", sub, "", s
        for spec, td in (sd.get("tier3") or {}).items():
            for s in td.get("skills", []):
                yield "tier3", sub, spec, s


def kits(cls):
    """[(subclass, spec, {tier: [skills]})], one per specialization."""
    d = load(f"classes/{cls}/skills.json")
    out = []
    for sub, sd in d["subclass_skills"].items():
        for spec, td in sd["tier3"].items():
            out.append((sub, spec, {"base": d["base_skills"], "subclass": sd["skills"], "tier3": td["skills"]}))
    return out


def in_scope(s):
    return (s.get("mana_cost") or 0) > 0 and s.get("max_level", MAX_RANK) != 1


def family(s):
    for name, f in FAMILIES.items():
        if not f or s.get("tier") in f.get("tier", []) or set(s.get("tags") or []) & set(f.get("tag", [])):
            return name
    raise ValueError(f"{s['id']}: no family (tier_order.families needs a catch-all)")


def power_gain(s):
    """Max-rank / rank-1 power ratio, from the per-rank fields the server applies. The
    main scaling counts because the rule gives rank_scaling_enabled to every skill that
    carries percent_per_level."""
    g = 1.0
    main = (s.get("scaling_percent") or 0) or (s.get("heal_scaling_percent") or 0)
    ppl = s.get("percent_per_level") or 0
    if main > 0 and ppl > 0:
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


def per_rank(mana_cost, s):
    return round_half_up(mana_cost * (power_gain(s) - 1) / (MAX_RANK - 1))


def cost(s, rank, mc=None, mpl=None):
    mc = s["mana_cost"] if mc is None else mc
    mpl = (s.get("mana_cost_per_level") or 0) if mpl is None else mpl
    return mc + mpl * (rank - 1)


def above(cls):
    """{skill_id: (tier index, {higher tier: [skills]})}: for each skill, the skills of the
    higher tiers in the kits that contain it (a base skill sees the whole class, a
    subclass skill its own specializations)."""
    out = {}
    for _, _, kit in kits(cls):
        for i, tier in enumerate(TIERS):
            for s in kit[tier]:
                _, up = out.setdefault(s["id"], (i, {}))
                for higher in TIERS[i + 1:]:
                    seen = up.setdefault(higher, {})
                    seen.update({r["id"]: r for r in kit[higher]})
    return out


def tier_ceilings(cls, mc):
    """{skill_id: (ceiling, reference skill id)} from the tier_order rule, given the rank-1
    costs mc (already capped for the higher tiers): the most expensive skill of the same
    family at the nearest higher tier that has one, minus 1."""
    out = {}
    skills = {s["id"]: s for _, _, _, s in iter_skills(cls)}
    for sid, (_, up) in above(cls).items():
        s = skills[sid]
        if not in_scope(s):
            continue
        for higher in TIERS:
            ref = [r for r in up.get(higher, {}).values() if in_scope(r) and family(r) == family(s)]
            if ref:
                top = max(ref, key=lambda r: mc[r["id"]])
                out[sid] = (mc[top["id"]] - 1, top["id"])
                break
    return out


def targets():
    """{class: {skill_id: {"mana_cost", "mana_cost_per_level", "rank_scaling_enabled"?}}}"""
    out = {}
    for cls in CLASSES:
        skills = {s["id"]: s for _, _, _, s in iter_skills(cls) if in_scope(s)}
        mc = {k: s["mana_cost"] for k, s in skills.items()}
        # top-down: a tier is capped by the higher tier once that one is final
        tier_of = {sid: i for sid, (i, _) in above(cls).items()}
        for i in range(len(TIERS) - 2, -1, -1):
            for sid, (c, _) in tier_ceilings(cls, mc).items():
                if tier_of[sid] == i and mc[sid] > c:
                    mc[sid] = c
        out[cls] = {}
        for k, s in skills.items():
            t = {"mana_cost": mc[k], "mana_cost_per_level": per_rank(mc[k], s)}
            if (s.get("percent_per_level") or 0) > 0:
                t["rank_scaling_enabled"] = True
            out[cls][k] = t
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


# A description restating the cost is a copy of mana_cost / mana_cost_per_level.
COST_SENTENCE = re.compile(r" ?(?:Coût : \d+ Souffle|Cost: \d+ Breath)[^.\"]*\.")


def top_level_field(block, key):
    """Match of `"key": value` at the skill's own indentation (not inside an effect)."""
    first = re.search(r'^([ \t]*)"id"\s*:', block, re.M)
    return re.search(r'^' + re.escape(first.group(1)) + r'"' + re.escape(key) + r'"\s*:\s*([^,\r\n]+)', block, re.M)


def edit_skill(block, want, nl):
    """Return block with the target fields set, and the cost sentences removed."""
    for key in ("mana_cost", "mana_cost_per_level", "rank_scaling_enabled"):
        if key not in want:
            continue
        val = json.dumps(want[key])
        m = top_level_field(block, key)
        if m:
            if m.group(1).strip() != val:
                block = block[:m.start(1)] + val + block[m.end(1):]
            continue
        anchor = {"mana_cost_per_level": "mana_cost", "rank_scaling_enabled": "percent_per_level"}[key]
        a = top_level_field(block, anchor)
        if not a:
            raise ValueError(f"no {anchor} line to anchor {key}")
        indent = re.match(r"[ \t]*", a.group(0)).group(0)
        if block[a.end(1):a.end(1) + 1] == ",":  # the anchor has fields after it
            eol = block.index(nl, a.end(1)) + len(nl)
            block = block[:eol] + f'{indent}"{key}": {val},{nl}' + block[eol:]
        else:  # the anchor is the last field
            block = block[:a.end(1)] + f',{nl}{indent}"{key}": {val}' + block[a.end(1):]
    return COST_SENTENCE.sub("", block)


def differences():
    """[(class, skill_id, field, have, want)] between the data and the rules."""
    tg = targets()
    out = []
    for cls in CLASSES:
        current = {s["id"]: s for _, _, _, s in iter_skills(cls)}
        for sid, want in tg[cls].items():
            for k, v in want.items():
                if current[sid].get(k) != v:
                    out.append((cls, sid, k, current[sid].get(k), v))
        for sid, s in current.items():
            for k in ("description_fr", "description_en"):
                if COST_SENTENCE.search(s.get(k) or ""):
                    out.append((cls, sid, k, "restates the cost", "no cost sentence"))
    return out


def apply():
    tg = targets()
    diffs = differences()
    touched = {}
    for cls, sid, *_ in diffs:
        touched.setdefault(cls, set()).add(sid)
    new = {}
    for cls, ids in touched.items():
        path = ROOT / f"classes/{cls}/skills.json"
        text = path.read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in text else "\n"
        for sid in sorted(ids):
            hits = [m.start() for m in re.finditer(r'"id"\s*:\s*"' + re.escape(sid) + '"', text)]
            if len(hits) != 1:
                raise ValueError(f"{sid}: {len(hits)} occurrences of its id")
            a, b = object_span(text, hits[0])
            if json.loads(text[a:b]).get("id") != sid:
                raise ValueError(f"{sid}: object span does not match the skill")
            text = text[:a] + edit_skill(text[a:b], tg[cls].get(sid, {}), nl) + text[b:]
        json.loads(text)  # still valid JSON
        new[path] = text
    for path, text in new.items():  # all or nothing
        path.write_bytes(text.encode("utf-8"))
    left = differences()
    if left:
        raise SystemExit(f"post-check failed: {left[:5]}")
    return diffs


# ---------------------------------------------------------------- tier order checks

def family_costs(rank):
    """{(family, tier): [cost at rank]} over every in-scope skill (each counted once)."""
    out = {}
    for cls in CLASSES:
        seen = set()
        for tier, _, _, s in iter_skills(cls):
            if in_scope(s) and s["id"] not in seen:
                seen.add(s["id"])
                out.setdefault((family(s), tier), []).append(cost(s, rank))
    return out


def tier_order_violations():
    """Rule failures: rank-1 kit ceilings, and family medians that do not rise with the tier."""
    bad = []
    for cls in CLASSES:
        mc = {s["id"]: s["mana_cost"] for _, _, _, s in iter_skills(cls) if in_scope(s)}
        for sid, (ceil, ref) in tier_ceilings(cls, mc).items():
            if mc[sid] > ceil:
                bad.append(f"{sid}: {mc[sid]} at rank 1, not below {ref} ({ceil + 1})")
    for rank in (1, MAX_RANK):
        fc = family_costs(rank)
        for fam in FAMILIES:
            meds = [(t, st.median(fc[(fam, t)])) for t in TIERS if (fam, t) in fc]
            for (t0, m0), (t1, m1) in zip(meds, meds[1:]):
                if m0 >= m1:
                    bad.append(f"family {fam}, rank {rank}: median {t0} {m0:g} >= {t1} {m1:g}")
    return bad


def kit_inversions(rank):
    """Per kit, lower-tier skills dearer at this rank than every same-family skill of the
    next tier (information: above rank 1 the per-rank cost follows each skill's power)."""
    out = set()
    for cls in CLASSES:
        for sub, spec, kit in kits(cls):
            for i, tier in enumerate(TIERS[:-1]):
                for s in kit[tier]:
                    if not in_scope(s):
                        continue
                    for higher in TIERS[i + 1:]:
                        ref = [r for r in kit[higher] if in_scope(r) and family(r) == family(s)]
                        if ref:
                            top = max(ref, key=lambda r: cost(r, rank))
                            if cost(s, rank) >= cost(top, rank):
                                out.add((s["id"], cost(s, rank), power_gain(s), top["id"], cost(top, rank), power_gain(top)))
                            break
    return sorted(out)


# ---------------------------------------------------------------- report

def report():
    print(f"| classe | sort | tier | famille | cout rang 1 | G (rang {MAX_RANK}/1) | +/rang | cout rang {MAX_RANK} |")
    print("|---|---|---|---|---|---|---|---|")
    for cls in CLASSES:
        seen = set()
        for tier, sub, spec, s in iter_skills(cls):
            if in_scope(s) and s["id"] not in seen:
                seen.add(s["id"])
                print(f"| {cls} | {s['id'][6:]} | {spec or sub or tier} ({tier}) | {family(s)} | {s['mana_cost']} | "
                      f"{power_gain(s):.2f} | {s.get('mana_cost_per_level') or 0} | {cost(s, MAX_RANK)} |")
    for rank in (1, 5, MAX_RANK):
        print(f"\n## Cout par famille et par tier, rang {rank} (n, min, mediane, max)")
        fc = family_costs(rank)
        for fam in FAMILIES:
            print(f"- {fam} : " + " | ".join(
                f"{t} n={len(fc[(fam, t)])} {min(fc[(fam, t)])} / {st.median(fc[(fam, t)]):g} / {max(fc[(fam, t)])}"
                for t in TIERS if (fam, t) in fc))
    inv = kit_inversions(MAX_RANK)
    print(f"\n## Rang {MAX_RANK} : sort plus cher que tout son tier superieur dans un kit ({len(inv)}, "
          "information : le cout par rang suit la puissance)")
    for sid, c, g, ref, rc, rg in inv:
        print(f"- {sid} {c} (G {g:.2f}) >= {ref} {rc} (G {rg:.2f})")
    bad = tier_order_violations()
    print(f"\n## Regle tier_order : {len(bad)} ecart(s)")
    for b in bad:
        print("- " + b)


# ---------------------------------------------------------------- budget model

LEVELS = [1, 20, 40, 60, 100]
ARMOR = {"warrior": "heavy", "mage": "light", "healer": "light", "archer": "medium", "rogue": "medium", "artisan": "medium"}
OFF = {"warrior": "atk", "mage": "mag", "healer": "mag", "archer": "atk", "rogue": "atk", "artisan": "atk"}
WEAPON = {"warrior": "sword", "mage": "staff", "healer": "scepter", "archer": "bow", "rogue": "dagger", "artisan": "sword"}
# Expected gear (pve_matrix.GEAR_PROFILES): common +0 while levelling, rare +5 from level 40.
GEAR_AT = {1: "mal", 20: "mal", 40: "moyen", 60: "moyen", 100: "moyen"}
# Typical skill ranks (base, tier 2, tier 3): 1 point per level, spread over the unlocked
# tiers (skill_system.json skill_categories). Sums: 20, 40, 60, 100 points.
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


def spells(kit, level):
    out = []
    for tier, rank in zip(TIERS, RANKS[level]):
        if rank <= 0:
            continue
        for s in kit[tier]:
            if in_scope(s):
                out.append((cost(s, rank), float(s.get("cooldown") or 0), float(s.get("cast_time") or 0),
                            family(s) == "remplissage"))
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


def regen_rule():
    """items/panoplies.json _meta.rank_system: ({band label: (first level, regen form)},
    {form: {resource: stat}}). Owner rule (2026-10-15): flat regen at ranks I-III, percent
    of the maximum at ranks IV-V; each rank carries its form, regen_forms names the stats."""
    rs = load("items/panoplies.json")["_meta"]["rank_system"]
    forms = {k: v for k, v in rs["regen_forms"].items() if not k.startswith("_")}
    bands = {}
    for k, v in rs.items():
        if k.startswith("rang_"):
            if v["regen_form"] not in forms:
                raise ValueError(f"rank_system.{k}.regen_form {v['regen_form']!r} is not a regen_forms key")
            bands[v["rank_label"]] = (v["level_range"][0], v["regen_form"])
    return bands, forms


def regen_rule_deviations():
    """[(set id, band, threshold, stat, form of the band)]: a regen stat of a set that is not
    of the form of the set's band."""
    bands, forms = regen_rule()
    stat_form = {stat: form for form, by_res in forms.items() for stat in by_res.values()}
    out = []
    for sid, s in load("items/panoplies.json")["sets"].items():
        if not isinstance(s, dict) or s.get("band") not in bands:
            continue
        want = bands[s["band"]][1]
        for thr, b in s["bonuses"].items():
            out += [(sid, s["band"], thr, k, want) for k in b if k in stat_form and stat_form[k] != want]
    return out


def souffle_sets():
    """[(level_min, set id, flat Breath regen /s, Breath regen in % of max /s)] of the full
    lootable sets that give Breath regen, with the first level of their band."""
    bands, forms = regen_rule()
    flat, pct = forms["flat"]["mp"], forms["percent"]["mp"]
    out = []
    for sid, s in load("items/panoplies.json")["sets"].items():
        if not isinstance(s, dict) or s.get("band") not in bands:
            continue
        f = sum(b.get(flat, 0) for b in s["bonuses"].values())
        p = sum(b.get(pct, 0) for b in s["bonuses"].values())
        if f or p:
            out.append((bands[s["band"]][0], sid, f, p))
    return sorted(out)


def set_regen(flat, pct, pool):
    """Breath per second of a set for a pool: flat + pool x % / 100 (the server formula,
    shared/gameplay/resource_regen.hpp)."""
    return flat + pool * pct / 100


def best_set(sets, level, pool):
    """(regen /s, set id, flat, %) of the Breath-regen set worth the most for this pool, among
    the sets a character of this level can wear."""
    ok = [(set_regen(f, p, pool), sid, f, p) for lmin, sid, f, p in sets if lmin <= level]
    return max(ok) if ok else (0, "", 0, 0)


def tte(pool, demand_s, regen):
    """Seconds of sustained rotation before the pool runs dry (inf: never)."""
    return math.inf if demand_s <= regen else pool / (demand_s - regen)


def fmt_s(t):
    return "jamais" if t == math.inf else f"{t:.0f} s"


def class_budgets(P, Gear, level, _gears={}):
    """{class: {pool0, pool1, regen, gear_regen, demand, big}} at this level: Souffle max with
    0 / 1 point per level, flat regen (class + growth + expected gear), rotation demand /s
    and biggest spell (medians over the 8 specializations)."""
    base, growth = load("stats/class_base_stats.json"), load("stats/class_growth.json")
    pv = load("config/game.json")["stats_definition"]["mp"]["point_value"]
    out = {}
    for cls in CLASSES:
        w = ARMOR[cls]
        _gears.setdefault(w, Gear(w))
        g = _gears[w].expected(w, OFF[cls], GEAR_AT[level], level, WEAPON[cls], n=200)
        b, gr = base[cls], growth[cls]
        pool0 = b["mp"] + math.floor(gr["mp"] * (level - 1)) + g.get("mp", 0)
        ks = [k for _, _, k in kits(cls)]
        out[cls] = {
            "pool0": pool0, "pool1": pool0 + (level - 1) * pv,
            "regen": b["mp_regen"] + gr.get("mp_regen", 0) * (level - 1) + round(g.get("mp_regen", 0)),
            "gear_regen": round(g.get("mp_regen", 0)),
            "demand": st.median(demand(spells(k, level)) for k in ks),
            "big": st.median(max(x[0] for x in spells(k, level)) for k in ks),
        }
    return out


def budget():
    P, Gear = _budget_tools()
    # Out of combat: the snapshot's mp_regen_out_of_combat = mp_regen without bonus
    # (no out-of-combat buff in the model), times the Pass benefit (systems/premium.json).
    pass_mult = load("systems/premium.json")["benefits"]["out_of_combat_regen_multiplier"]
    sets = souffle_sets()
    budgets, durations = {}, {}
    for level in LEVELS:
        fd = durations[level] = fight_durations(P, level)
        cb = budgets[level] = class_budgets(P, Gear, level)
        print(f"\n### Niveau {level}  (sorts de base rang {RANKS[level][0]}, tier 2 rang {RANKS[level][1]}, "
              f"tier 3 rang {RANKS[level][2]} ; equipement {GEAR_AT[level]})")
        print("Durees (s) : " + ", ".join(f"{k} {v:.0f}" for k, v in fd.items()))
        print("| classe | Souffle max (0 pt / 1 pt par niv) | regen /s (equipement) | rotation /s "
              "| a sec (0 pt / 1 pt) | tient un pack | a sec sur un combat long | plein hors combat (sans / avec pass) "
              "| avec la panoplie de Souffle la plus utile : set, regen, a sec (0 pt), tient un pack | plus gros sort / max |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for cls, c in cb.items():
            d, regen, pool0 = c["demand"], c["regen"], c["pool0"]
            t0, t1 = tte(pool0, d, regen), tte(c["pool1"], d, regen)
            sr, sid, _, _ = best_set(sets, level, pool0)
            ts = tte(pool0, d, regen + sr)
            set_col = f"{sid}, {regen + sr:.1f}, {fmt_s(ts)}, {'oui' if ts >= fd['pack'] else 'non'}" if sid else ""
            print(f"| {cls} | {pool0:.0f} / {c['pool1']:.0f} | {regen:.0f} ({c['gear_regen']}) | {d:.1f} | "
                  f"{fmt_s(t0)} / {fmt_s(t1)} | {'oui' if t0 >= fd['pack'] else 'non'} | "
                  f"{'oui' if t0 < max(fd['elite'], fd['5star']) else 'non'} | "
                  f"{pool0 / regen:.0f} s / {pool0 / (regen * pass_mult):.0f} s | {set_col} | {c['big'] / pool0:.0%} |")
    percent_sets(sets, budgets, durations)
    autonomy(budgets)


def percent_sets(sets, budgets, durations, level=100):
    """Breath regen in % (rank IV-V sets): per class at `level`, the % above which the class no
    longer runs dry before the end of a long fight (elite or 5 star), and above which it never
    runs dry; the full percent sets and the game cap of mp_regen_percent (stats/definitions.json)
    against them; then the deviations from the rank rule."""
    cb, fd = budgets[level], durations[level]
    long_fight = max(fd["elite"], fd["5star"])
    cap = load("stats/definitions.json")["stats"]["resources"]["mp_regen_percent"]["cap"]
    print(f"\n### Regen de Souffle en %, niveau {level} (combat long {long_fight:.0f} s)")
    print("Plafond par classe = % du Souffle max par seconde au-dessus duquel la classe n'est plus a sec avant la fin "
          "du combat long (sec), ou plus jamais a sec (inepuisable).")
    print("| classe | plafond sec (0 pt / 1 pt) | plafond inepuisable (0 pt / 1 pt) |")
    print("|---|---|---|")
    dry, never = [], []
    for cls, c in cb.items():
        row = []
        for pool in (c["pool0"], c["pool1"]):
            dry.append(100 * (c["demand"] - c["regen"] - pool / long_fight) / pool)
            never.append(100 * (c["demand"] - c["regen"]) / pool)
            row.append((dry[-1], never[-1]))
        print(f"| {cls} | {row[0][0]:.3f} / {row[1][0]:.3f} | {row[0][1]:.3f} / {row[1][1]:.3f} |")
    print(f"Plafond commun : sec {min(dry):.3f} %/s, inepuisable {min(never):.3f} %/s ; "
          f"plafond de jeu mp_regen_percent {cap:g} ({'sous' if cap < min(never) else 'AU-DESSUS de'} l'inepuisable).")
    for lmin, sid, f, p in sets:
        if not p:
            continue
        verdict = "respecte" if p < min(dry) else "DEPASSE"
        print(f"\n{sid} (des le niveau {lmin}) : {f:g} /s + {p:g} % du Souffle max /s, {verdict} le plafond sec ; "
              f"{p / cap:.0%} du plafond de jeu.")
        print("| classe | regen sans / avec (0 pt) | a sec sans / avec (0 pt) | regen sans / avec (1 pt) | a sec sans / avec (1 pt) |")
        print("|---|---|---|---|---|")
        for cls, c in cb.items():
            cells = []
            for pool in (c["pool0"], c["pool1"]):
                r = c["regen"] + set_regen(f, p, pool)
                cells += [f"{c['regen']:.0f} / {r:.1f}",
                          f"{fmt_s(tte(pool, c['demand'], c['regen']))} / {fmt_s(tte(pool, c['demand'], r))}"]
            print(f"| {cls} | " + " | ".join(cells) + " |")
    dev = regen_rule_deviations()
    print(f"\nRegle de forme des panoplies (rank_system.regen_forms) : {len(dev)} ecart(s) a trancher")
    for sid, band, thr, stat, want in dev:
        print(f"- {sid} ({band}, palier {thr}) : {stat}, la bande demande la forme {want}")


def autonomy(budgets):
    """Phase 3 constraint (config/skill_system.json mana_cost_scaling.autonomy_by_range): per
    class, autonomy (seconds of sustained rotation before running dry) and share of the pool
    spent per second; per base_range (config/roles.json), the median autonomy against the
    nearest shorter range. Information: costs are not changed here."""
    rule = SKILL_SYSTEM["mana_cost_scaling"]["autonomy_by_range"]
    roles = load("config/roles.json")
    pv = load("config/game.json")["stats_definition"]["mp"]["point_value"]
    rng = {cls: roles[cls]["base_range"] for cls in CLASSES}
    print(f"\n### Autonomie par classe et par portee (phase 3, {rule['points_in_souffle_per_level']} pt de Souffle "
          f"par niveau, sans panoplie ; regle : mediane d'une portee <= {rule['max_ratio_to_shorter_range']:g} x "
          f"celle de la portee inferieure)")
    print("Cellule : a sec apres, part du Souffle max depensee par seconde.")
    print("| niveau | " + " | ".join(f"{c} (portee {rng[c]})" for c in CLASSES) + " | ecarts |")
    print("|---|" + "---|" * (len(CLASSES) + 1))
    for level in rule["measure_levels"]:
        cb = budgets[level]
        auto, cells = {}, []
        for cls, c in cb.items():
            pool = c["pool0"] + (level - 1) * pv * rule["points_in_souffle_per_level"]
            auto[cls] = tte(pool, c["demand"], c["regen"])
            cells.append(f"{fmt_s(auto[cls])}, {c['demand'] / pool:.1%}/s")
        by_range = {}
        for cls, t in auto.items():
            by_range.setdefault(rng[cls], []).append(t)
        med = sorted((r, st.median(v)) for r, v in by_range.items())
        bad = [f"portee {r1} {fmt_s(m1)} > {rule['max_ratio_to_shorter_range']:g} x portee {r0} {fmt_s(m0)}"
               for (r0, m0), (r1, m1) in zip(med, med[1:]) if m1 > rule["max_ratio_to_shorter_range"] * m0]
        print(f"| {level} | " + " | ".join(cells) + f" | {'; '.join(bad) or 'aucun'} |")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="report rule failures, write nothing, exit 1 if any")
    ap.add_argument("--report", action="store_true", help="per-skill and per-tier tables")
    ap.add_argument("--budget", action="store_true", help="Souffle budget model by level")
    a = ap.parse_args()
    if a.report:
        report()
        return
    if a.budget:
        budget()
        return
    diffs = differences() if a.check else apply()
    for cls, sid, field, have, want in diffs:
        print(f"{cls:8} {sid:52} {field:22} {have!s:>6} -> {want}")
    bad = tier_order_violations()
    for b in bad:
        print("tier_order: " + b)
    n = sum(len(v) for v in targets().values())
    print(f"{len(diffs)} difference(s) {'found' if a.check else 'applied'}, {len(bad)} tier_order failure(s), {n} skills in scope.")
    if diffs and a.check or bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
