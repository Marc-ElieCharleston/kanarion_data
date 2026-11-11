"""Rank milestones of the class skills: what ranks 5 and 10 add (Charleston, 2026-11-08).

Owner of the numbers: config/skill_system.json
  skill_levels.milestone_ranks   the milestone ranks, declared ONCE ([5, 10])
  rank_milestones                the rules below (bonus sizes, complements), all "a valider"

This script expands those rules into the `rank_milestones` list of every class skill
(classes/<class>/skills.json). The combat server reads ONLY the per-skill list (content_loader
refuses an incoherent one); the client only displays it. `--check` (CI) fails when a skill's
list differs from what the rules give, so a hand edit cannot drift from the rules.

Entry grammar (one bonus = one entry, cumulative: every entry whose rank <= the skill rank applies)
  {"rank": 5,  "bonus": "extra_stacks",     "stat": <effect>, "value": 1}
        +value stacks on that effect entry of the skill (canonical stackable, never above
        its max_stacks, stats/status_effects.json _meta.canonical_grid)
  {"rank": 5,  "bonus": "extra_duration",   "stat": <effect>, "value": 2}
        +value seconds on that effect (or on the top-level dot_type)
  {"rank": 10, "bonus": "extra_effect",     "stat": <effect>, "value": 1, "with": <effect>}
        also applies `value` stacks of a complementary canonical effect, with the duration and
        target of the `with` effect of the skill (a capped buff gains an effect, not power)
  {"rank": 10, "bonus": "cooldown_percent", "value": -15}
        cooldown x (1 + value / 100), proportional so it follows any later cooldown change

Rules (rank_milestones block of skill_system.json):
  stackable effect under its cap (buff, debuff, DoT)  +stack_bonus stack at each milestone rank
  slow (soft control)                                 rank 5: +stack_bonus stack (or +soft_cc
                                                      seconds when capped); rank 10: +soft_cc s
  other soft control (blind, taunt, challenge)        +soft_cc_duration_seconds at each milestone
  every stackable effect of the skill already capped  primary capped effect (first in effects[]):
      buff / debuff  rank 5: +capped_effect_duration_seconds if the duration rule allows it,
                     else a complement; rank 10: a complement (complements[<effect>], first one
                     the skill does not already apply)
      DoT            +dot_capped_duration_seconds at each milestone the duration rule allows
  debuff the skill puts on its own caster (a price)    never grows
  hard control (stun, silence, disarm, fear, confusion, freeze, root)
                                                      cooldown_percent hard_cc_cooldown_percent
                                                      at hard_cc_rank
  immunity                                            same cooldown bonus (if no hard control)
  skill that still grows with nothing at all          no_growth_cooldown_percent at hard_cc_rank
  damage, heal, shield, HoT                           linear (percent_per_level, pct_per_level):
                                                      no milestone
A duration bonus is only given when the duration stays inside stats/status_effects.json
_meta.duration_rule at every rank and the cooldown stays strictly longer than the longest
duration (cooldown_rule, exempt fillers excepted); a cooldown bonus only when the same holds
with the reduced cooldown (and the immunity uptime rule of validate_cross_references).

Scope: base, subclass and tier-3 skills of the six classes, max_level != 1 (signature
movements and familiar skills are cast at rank 1: no milestone).

Usage (from the repo root):
    python -X utf8 scripts/balance/rank_milestones.py            # write the per-skill lists
    python -X utf8 scripts/balance/rank_milestones.py --check    # exit 1 when a list is stale
    python -X utf8 scripts/balance/rank_milestones.py --report   # per-skill table
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLASSES = ["warrior", "mage", "healer", "archer", "rogue", "artisan"]
EPS = 1e-6


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


SKILL_SYSTEM = load("config/skill_system.json")
MAX_RANK = SKILL_SYSTEM["skill_levels"]["max_level"]
MILESTONES = SKILL_SYSTEM["skill_levels"]["milestone_ranks"]
RULES = SKILL_SYSTEM["rank_milestones"]
STATUS = load("stats/status_effects.json")
DURATION_RULE = STATUS["_meta"]["duration_rule"]
SOFT = tuple(DURATION_RULE["soft_seconds"])
HARD = tuple(DURATION_RULE["hard_cc_seconds"])
EXCLUDED = set(DURATION_RULE.get("excluded_categories", []))
CD_EXEMPT = set(DURATION_RULE.get("cooldown_rule_exempt_skills", []))
IMMUNITY_CAP = (load("stats/definitions.json")["stats"]["support"]["buff_duration"]
                ["cap_by_effect_type"].get("immunity", 0))

GRID = {}          # effect -> (grid group, max_stacks)
for group, block in STATUS["_meta"]["canonical_grid"].items():
    if group.startswith("_") or group == "non_stackable_special_effects" or not isinstance(block, dict):
        continue
    for eid, d in block.items():
        if not eid.startswith("_") and isinstance(d, dict) and d.get("max_stacks", 0) > 0:
            GRID[eid] = (group, d["max_stacks"])
CATEGORY, HARD_CC = {}, set()
for cat, block in STATUS["effects"].items():
    for eid, d in block.items():
        if eid.startswith("_") or not isinstance(d, dict):
            continue
        CATEGORY[eid] = cat
        if (d.get("runtime") or {}).get("is_hard_cc"):
            HARD_CC.add(eid)
SOFT_CC = {e for e, c in CATEGORY.items() if c in ("control", "aggro") and e not in HARD_CC
           and e not in ("slow", "interrupt")}
# Linear families: their growth is percent_per_level / pct_per_level, never a milestone.
LINEAR = {"heal_over_time", "heal_over_time_mag", "heal_over_time_max_hp", "mana_regen"}


def iter_skills(data):
    for s in data.get("base_skills", []):
        yield s
    for sd in data.get("subclass_skills", {}).values():
        yield from sd.get("skills", [])
        for td in (sd.get("tier3") or {}).values():
            yield from td.get("skills", [])


def in_scope(s):
    return s.get("max_level", MAX_RANK) != 1


def stat_of(e):
    return e.get("stat") or e.get("status_id")


def self_drawback(s, e):
    """A debuff the skill puts on its own caster (Iron Stance, Frenzy ...): a price, not an
    effect. A milestone never makes it bigger."""
    return e.get("type") == "debuff" and (e.get("target") == "self" or s.get("target") == "self")


def kind(e, s=None):
    """Milestone family of one effects[] entry."""
    st = stat_of(e)
    if e.get("type") == "utility" or st in LINEAR:
        return None
    if s is not None and self_drawback(s, e):
        return None
    if st in GRID:
        group = GRID[st][0]
        if group == "dot":
            return "dot"
        if st == "slow":
            return "slow"
        return "mod"
    if st in HARD_CC:
        return "hard_cc"
    if st in SOFT_CC:
        return "soft_cc"
    if CATEGORY.get(st) == "immunity":
        return "immunity"
    if CATEGORY.get(st) == "dot":
        return "dot_flat"   # non-canonical DoT (holy_dot, curse_dot): duration only
    return None


def has_linear_growth(s):
    if (s.get("percent_per_level") or 0) > 0 and s.get("rank_scaling_enabled"):
        return True
    for e in s.get("effects") or []:
        if any((e.get(k) or 0) > 0 for k in ("duration_per_level", "pct_per_level", "value_per_level")):
            return True
    return any((s.get(k) or 0) > 0 for k in ("bonus_per_charge_per_level", "damage_per_adjacent_ally_per_level",
                                              "counter_chance_per_level", "dot_duration_per_level",
                                              "random_buffs_min_at_level_5", "random_debuffs_min_at_level_5"))


# ---------------------------------------------------------------- rules check

def effect_durations(s, entries, rank):
    """[(stat, kind, seconds)] the skill applies at `rank`, milestones included."""
    extra = {}
    for m in entries:
        if m["rank"] <= rank and m["bonus"] == "extra_duration":
            extra[m["stat"]] = extra.get(m["stat"], 0) + m["value"]
    out = []
    for e in s.get("effects") or []:
        st = stat_of(e)
        if e.get("type") == "utility" or not e.get("duration"):
            continue
        d = float(e["duration"]) + float(e.get("duration_per_level") or 0) * (rank - 1) + extra.get(st, 0)
        out.append((st, "hard" if st in HARD_CC else "soft", d))
    if s.get("dot_duration"):
        d = float(s["dot_duration"]) + float(s.get("dot_duration_per_level") or 0) * (rank - 1)
        out.append(("dot_duration", "soft", d + extra.get(s.get("dot_type"), 0)))
    for k in ("random_buffs_duration", "random_debuffs_duration"):
        if s.get(k):
            out.append((k, "soft", float(s[k])))
    return out


def cooldown_at(s, entries, rank):
    pct = sum(m["value"] for m in entries if m["rank"] <= rank and m["bonus"] == "cooldown_percent")
    return float(s.get("cooldown") or 0) * (1 + pct / 100)


def respects_rules(s, entries):
    """True when the duration rule, the cooldown rule and the immunity uptime rule hold at
    every rank with these milestones."""
    for rank in range(1, MAX_RANK + 1):
        durs = effect_durations(s, entries, rank)
        longest = max([d for _, _, d in durs], default=0)
        for st, k, d in durs:
            if CATEGORY.get(st) in EXCLUDED:
                continue
            lo, hi = SOFT if k == "soft" else HARD
            if d < lo - EPS or d > hi + EPS:
                return False
        cd = cooldown_at(s, entries, rank)
        if longest > 0 and cd <= longest + EPS and s["id"] not in CD_EXEMPT:
            return False
        for e in s.get("effects") or []:
            if CATEGORY.get(stat_of(e)) == "immunity" and e.get("duration"):
                dur = float(e["duration"]) + float(e.get("duration_per_level") or 0) * (rank - 1)
                if cd > 0 and dur * (1 + IMMUNITY_CAP / 100) >= cd:
                    return False
    return True


def try_add(s, entries, entry):
    """Append entry when the rules still hold with it."""
    if respects_rules(s, entries + [entry]):
        entries.append(entry)
        return True
    return False


# ---------------------------------------------------------------- expansion

def milestones_for(s):
    """The rank_milestones list the rules give to skill s (possibly empty)."""
    if not in_scope(s):
        return []
    effects = [e for e in s.get("effects") or [] if stat_of(e)]
    present = {stat_of(e) for e in effects}
    stack_bonus = RULES["stack_bonus"]
    entries = []
    stacks = {}
    for e in effects:
        if kind(e, s) in ("mod", "dot", "slow"):
            stacks.setdefault(stat_of(e), e.get("stacks_to_apply") or 0)
    complements_used = {}

    for rank in MILESTONES:
        grew = False
        # 1. stackable effects under their cap: +1 stack (slow: rank 5 only)
        for e in effects:
            k, st = kind(e, s), stat_of(e)
            if k not in ("mod", "dot", "slow") or st in [m.get("stat") for m in entries
                                                          if m["rank"] == rank and m["bonus"] == "extra_stacks"]:
                continue
            if k == "slow" and rank != MILESTONES[0]:
                continue
            cap = GRID[st][1]
            if stacks[st] < cap:
                add = min(stack_bonus, cap - stacks[st])
                entries.append({"rank": rank, "bonus": "extra_stacks", "stat": st, "value": add})
                stacks[st] += add
                grew = True
        # 2. slow: +soft_cc s at the last milestone, or when capped at the first one
        for e in effects:
            st = stat_of(e)
            if kind(e, s) != "slow":
                continue
            if e.get("duration") and (rank != MILESTONES[0] or
                                      not any(m["rank"] == rank and m.get("stat") == st for m in entries)):
                if try_add(s, entries, {"rank": rank, "bonus": "extra_duration", "stat": st,
                                        "value": RULES["soft_cc_duration_seconds"]}):
                    grew = True
        # 3. other soft control: +soft_cc s at each milestone
        for e in effects:
            if kind(e, s) == "soft_cc" and e.get("duration"):
                if try_add(s, entries, {"rank": rank, "bonus": "extra_duration", "stat": stat_of(e),
                                        "value": RULES["soft_cc_duration_seconds"]}):
                    grew = True
        # 4. every stackable effect capped: the primary capped one gains duration or an effect
        capped = [e for e in effects if kind(e, s) in ("mod", "dot") and stacks[stat_of(e)] >= GRID[stat_of(e)][1]]
        stack_grew = any(m["rank"] == rank and m["bonus"] == "extra_stacks" for m in entries)
        if capped and not stack_grew:
            prim = capped[0]
            st = stat_of(prim)
            if kind(prim, s) == "dot":
                if prim.get("duration") and try_add(s, entries, {"rank": rank, "bonus": "extra_duration", "stat": st,
                                        "value": RULES["dot_capped_duration_seconds"]}):
                    grew = True
            else:
                done = False
                if rank == MILESTONES[0] and prim.get("duration"):
                    done = try_add(s, entries, {"rank": rank, "bonus": "extra_duration", "stat": st,
                                                "value": RULES["capped_effect_duration_seconds"]})
                if not done:
                    comp = complements_used.get(st)
                    if comp is None:
                        comp = next((c for c in RULES["complements"].get(st, [])
                                     if c not in present), None)
                    if comp is not None:
                        complements_used[st] = comp
                        entries.append({"rank": rank, "bonus": "extra_effect", "stat": comp,
                                        "value": stack_bonus, "with": st})
                        done = True
                if not done and prim.get("duration"):
                    # no complement left: the duration bonus, if the rule allows it
                    done = try_add(s, entries, {"rank": rank, "bonus": "extra_duration", "stat": st,
                                                "value": RULES["capped_effect_duration_seconds"]})
                grew = grew or done
        # 4b. non-canonical DoT: +dot_capped s
        for e in effects:
            if kind(e, s) == "dot_flat" and e.get("duration"):
                if try_add(s, entries, {"rank": rank, "bonus": "extra_duration", "stat": stat_of(e),
                                        "value": RULES["dot_capped_duration_seconds"]}):
                    grew = True
    # 5. hard control / immunity: proportional cooldown cut at hard_cc_rank
    kinds = {kind(e, s) for e in effects}
    cd_rank = RULES["hard_cc_rank"]
    if (s.get("cooldown") or 0) > 0 and kinds & {"hard_cc", "immunity"}:
        try_add(s, entries, {"rank": cd_rank, "bonus": "cooldown_percent",
                             "value": RULES["hard_cc_cooldown_percent"]})
    # 6. a skill its rank still does nothing for: the same cooldown cut
    if not entries and not has_linear_growth(s) and (s.get("cooldown") or 0) > 0:
        try_add(s, entries, {"rank": cd_rank, "bonus": "cooldown_percent",
                             "value": RULES["no_growth_cooldown_percent"]})
    entries.sort(key=lambda m: (m["rank"], ["extra_stacks", "extra_duration", "extra_effect",
                                            "cooldown_percent"].index(m["bonus"])))
    return entries


# ---------------------------------------------------------------- io

def write_file(path, data, raw):
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if b"\r\n" in raw:
        out = out.replace("\n", "\r\n")
    path.write_bytes(out.encode("utf-8"))


def place(s, entries):
    """Put rank_milestones right after `effects` (or at the end), drop it when empty."""
    items = [(k, v) for k, v in s.items() if k != "rank_milestones"]
    if entries:
        idx = next((i + 1 for i, (k, _) in enumerate(items) if k == "effects"), len(items))
        items.insert(idx, ("rank_milestones", entries))
    s.clear()
    s.update(items)


def run(check=False, report=False):
    stale = []
    rows = []
    for cls in CLASSES:
        path = ROOT / "classes" / cls / "skills.json"
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
        changed = False
        for s in iter_skills(data):
            want = milestones_for(s)
            have = s.get("rank_milestones", [])
            rows.append((cls, s["id"], want))
            if have != want:
                stale.append(s["id"])
                if not check:
                    place(s, want)
                    changed = True
        if changed:
            write_file(path, data, raw)
    if report:
        for cls, sid, want in rows:
            txt = "; ".join(f"r{m['rank']} {m['bonus']} {m.get('stat', '')} {m['value']:+g}"
                            + (f" (avec {m['with']})" if m.get("with") else "") for m in want)
            print(f"{cls:8s} {sid:55s} {txt or '-'}")
    n = sum(1 for *_, w in rows if w)
    if check:
        if stale:
            print(f"{len(stale)} skill(s) with a stale rank_milestones list: {', '.join(stale[:10])}"
                  f"{' ...' if len(stale) > 10 else ''} (run scripts/balance/rank_milestones.py)")
            return 1
        print(f"rank_milestones up to date ({n} skills with milestones, {len(rows)} skills).")
        return 0
    print(f"{len(stale)} skill(s) rewritten, {n} skills with milestones.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    sys.exit(run(check=a.check, report=a.report))


if __name__ == "__main__":
    main()
