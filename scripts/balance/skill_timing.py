"""Cooldowns and cast times of class skills, from the skill power matrix (phase 2).

Rules (owner: config/skill_power_model.json timing; note: _meta/carnet/matrice_sorts.md):

  cast       reflex skills (filler, counter, self emergency) are instant. Otherwise
             c = the longest grid step such that grid(raw power r1 - cast cost(c)) >= c
             (a fixed point, independent of the current value), floored by role and by
             effect (resurrection), capped for melee subclasses. A cast above the GCD
             becomes max(current, c); a cast at or under the GCD is free (it runs during
             the GCD) and becomes c, at least min_real_cast_seconds when it cast already.
  cooldown   target = net power r1 / (role density x identity factor), within the role
             bounds, rounded up to the scale step; cooldown = max(current, target), or the
             role's upper bound when above it (the only shortening). The identity factor
             grows with the share of the skill's power in its class's identity (roles.json
             role and role_tags, the dominant of the kit the skill belongs to).
  kit load   per kit and level band, sum of max(GCD, cast) / cooldown x weight over the
             bar (reactive skills weigh less), no cooldown reduction, <= budget; otherwise
             the kit lowers the admitted density (scale k >= min_density_scale) of the
             skills the band makes it pay for (the subclass, then the specialization; never
             the base kit every kit shares) that are strong for their role: the weak ones
             keep their cooldown. A shared skill takes the lowest k.
  copies     description sentences restating cast_time or cooldown follow the field.

Every number comes from the model; the matrix (skill_power_matrix.py) gives power, role
and dominant, souffle_per_level.py the textual field writer.

Usage (from the repo root):
    python -X utf8 scripts/balance/skill_timing.py            # apply
    python -X utf8 scripts/balance/skill_timing.py --check    # exit 1 if a skill differs from the rules
    python -X utf8 scripts/balance/skill_timing.py --report   # current -> rule, kit load, spam, CDR

After an apply, regenerate the matrix (python -X utf8 scripts/balance/skill_power_matrix.py):
it reads cooldown and cast_time.
"""
import argparse
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skill_power_matrix as P  # noqa: E402  (build, roles, cast_cost, kit_rows, bar, kit_load, spam_fraction)

S = P.S
T = P.M["timing"]
CD, LOAD, CAST, COPIES = T["cooldown"], T["kit_load"], T["cast"], T["description_copies"]
FIELDS = ("cooldown", "cast_time")
# Skills whose written cooldown / cast_time the owner fixed against the rule (owner rule
# 2026-10-21: cooldown capped at 4-5x the effect duration, no inflation by the model).
EXCEPTIONS = tuple(T.get("exceptions", {}).get("skills", []))


# ---------------------------------------------------------------- scale

def step_of(x):
    for r in CD["rounding"]:
        if r["below"] is None or x < r["below"]:
            return r["step"]


def round_up(x):
    s = step_of(x)
    return math.ceil(x / s - 1e-9) * s


# ---------------------------------------------------------------- class identity

def class_entry(row):
    """config/roles.json entry of the skill's subclass (its class for a base skill)."""
    return P.ROLES_CFG[row["subclass"] or row["class"]]


SUBCLASSES = {cls: sorted({sub for sub, _, _ in S.kits(cls)}) for cls in S.CLASSES}


KIT_DOMINANT = {}   # (class, subclass, spec) -> dominant group of that kit's own skills; set by plan()


def kit_dominants(rows):
    """Dominant group of the summed positive power (rank 1) of the skills each kit adds (base,
    a subclass, a specialization), roles of identity.kit_dominant_excluded_roles left out."""
    groups = P.pub(P.M["roles"]["components"])
    excl = set(CD["identity"]["kit_dominant_excluded_roles"])
    acc = {}
    for r in rows:
        if r["role"] in excl:
            continue
        g = acc.setdefault((r["class"], r["subclass"], r["spec"]), dict.fromkeys(groups, 0.0))
        for name, ks in groups.items():
            g[name] += sum(max(0.0, r["components_r1"].get(k, 0.0)) for k in ks)
    return {k: max(v, key=lambda n: (v[n], n)) for k, v in acc.items() if any(v.values())}


def identity_dominants(row):
    """Dominant groups that carry the identity of the skill's class: the role and role_tags of
    its subclass in config/roles.json (for a base skill, of its class and of every subclass that
    inherits it: the base kit is their common trunk), plus the dominant of the kit the skill
    belongs to (a specialization's own skills, a subclass's, the base kit's): a support whose
    specialization deals damage, a tank whose specialization strikes, read from the data."""
    idt = CD["identity"]
    keys = [row["subclass"]] if row["subclass"] else [row["class"]] + SUBCLASSES[row["class"]]
    out = set()
    for k in keys:
        e = P.ROLES_CFG[k]
        out |= set(idt["dominants_by_class_role"].get(e["role"], []))
        for tag in e.get("role_tags", []):
            out |= set(idt["dominants_by_role_tag"].get(tag, []))
    kd = KIT_DOMINANT.get((row["class"], row["subclass"], row["spec"]))
    return out | ({kd} if kd else set())


def identity_share(row):
    """Share of the skill's positive power (rank 1) carried by the dominants of its class."""
    idt = CD["identity"]
    if row["role"] not in idt["roles"]:
        return 0.0
    doms = identity_dominants(row)
    groups = P.pub(P.M["roles"]["components"])
    pos = {k: max(0.0, v) for k, v in row["components_r1"].items()}
    total = sum(pos.values())
    return sum(pos.get(k, 0.0) for g in doms for k in groups[g]) / total if total else 0.0


def density(row):
    """Points of net power allowed per second of cooldown: the role's density, times up to the
    identity factor in proportion to the power the skill puts into its class's role."""
    d = CD["density_points_per_second"][row["role"]]
    return d * (1 + (CD["identity"]["factor"] - 1) * identity_share(row))


def bounds(row):
    return CD["bounds_seconds"][row["role"]]


# ---------------------------------------------------------------- rules

def grid_cast(net):
    for g in CAST["grid"]:
        if g["max_net_power"] is None or net <= g["max_net_power"]:
            return g["cast"]


def is_reflex(s, row):
    rf = CAST["reflex"]
    return row["role"] in rf["roles"] or bool(set(s.get("tags") or []) & set(rf["tags"])) or \
        (row["role"] in rf["self_target_roles"] and s["target"] == "self")


def cast_rule(s, row):
    """Reflex skills are instant. Otherwise c = the grid's fixed point, floored by role and
    effect, capped for melee; a cast above the GCD only lengthens; a cast at or under the
    GCD (free: it runs during the GCD) becomes c, at least min_real_cast_seconds."""
    cur = s.get("cast_time") or 0
    if is_reflex(s, row):
        return 0
    raw = row["power"][0]
    steps = sorted({g["cast"] for g in CAST["grid"]})
    c = max(x for x in steps if x <= grid_cast(raw - P.cast_cost(s, x)))
    c = max(c, CAST["floor_by_role"].get(row["role"], 0))
    cap = CAST["melee_cap"]
    if set(class_entry(row).get("role_tags", [])) & set(cap["role_tags"]):
        c = min(c, cap["seconds"])
    effects = {e["stat"] for e in s.get("effects") or []}
    c = max([c] + [v for k, v in CAST["floor_by_effect"].items() if k in effects])
    if cur > P.GCD:
        return max(cur, c)
    if cur > 0 or 0 < c <= P.GCD:
        c = max(c, CAST["min_real_cast_seconds"])
    return c


def cooldown_target(row, net, scale=1.0):
    lo, hi = bounds(row)
    return round_up(min(max(max(net, 0.0) / (density(row) * scale), lo), hi))


def cooldown_rule(row, net, scale=1.0):
    """max(current, target); a cooldown above its role's upper bound comes back to it."""
    hi = bounds(row)[1]
    return hi if row["cooldown"] > hi else max(row["cooldown"], cooldown_target(row, net, scale))


def load_weight(row):
    """Share of a skill in its kit's load: a reactive skill (kit_load.reactive_roles: a heal,
    a shield, a cleanse, a defensive buff) is cast when someone takes damage, not as soon as it
    is ready; it weighs reactive_weight."""
    return LOAD["reactive_weight"] if row["role"] in LOAD["reactive_roles"] else 1.0


ROLE_STRONG = {}   # role -> net power r1 from which a skill is strong for its role; set by plan()


def strong(row):
    """A skill the kit budget may lengthen: not of kit_load.unscaled_roles, and net power r1 at
    least the role's kit_load.strong_role_quantile (a weak skill keeps the cooldown its power
    gives it)."""
    return row["role"] not in LOAD["unscaled_roles"] and row["net_power_r1"] >= ROLE_STRONG.get(row["role"], 0.0)


def kit_scale(kit, tiers, scaled_tiers):
    """Largest density scale k in [min_density_scale, 1] whose cooldowns fit the kit's bar in
    the budget, k lowering the admitted density of the skills of `scaled_tiers` only: it
    lengthens the skills strong for their role (strong()), never the weak ones."""
    def load(k):
        scaled = {t: [dict(r, cooldown=cooldown_rule(r, r["net_power_r1"], k)) if t in scaled_tiers and strong(r) else r
                      for r in kit[t]] for t in tiers}
        return P.kit_load(P.bar(scaled, tiers), weight=load_weight)
    if load(1.0) <= LOAD["budget"] + 1e-9:
        return 1.0
    lo, hi = LOAD["min_density_scale"], 1.0
    if load(lo) > LOAD["budget"] + 1e-9:
        return lo
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if load(mid) <= LOAD["budget"] + 1e-9 else (lo, mid)
    return lo


def enforce_budget(rows):
    """Level bands in order, each on the cooldowns the earlier ones set. In a band, each kit over
    budget lowers the admitted density of its strong skills of the tiers the band makes it pay
    for (kit_load.scaled_tiers): the subclass at level 20-59, the subclass and specialization
    at 60, never the base kit all eight kits of the class share. A skill shared by several kits
    takes the lowest scale."""
    for (_, tiers), scaled_tiers in zip(P.LEVEL_BARS, LOAD["scaled_tiers"]):
        scale = {}
        for *_, kit in P.kit_rows(list(rows.values())):
            k = kit_scale(kit, tiers, scaled_tiers)
            for t in scaled_tiers:
                for r in kit[t]:
                    if strong(r):
                        scale[r["id"]] = min(scale.get(r["id"], 1.0), k)
        for sid, k in scale.items():
            if k < 1.0:
                rows[sid]["cooldown"] = cooldown_rule(rows[sid], rows[sid]["net_power_r1"], k)


def plan():
    """(current rows, ruled rows) by skill id. Ruled rows carry the new cooldown, cast_time
    and net_power_r1."""
    data = P.build()
    skills = {s["id"]: s for *_, s in P.all_skills()}
    cur = {r["id"]: r for r in data["skills"]}
    KIT_DOMINANT.clear()
    KIT_DOMINANT.update(kit_dominants(data["skills"]))
    new = {}
    for sid, r in cur.items():
        s = skills[sid]
        cast = cast_rule(s, r)
        net = r["power"][0] - P.cast_cost(s, cast)
        new[sid] = dict(r, cast_time=cast, net_power_r1=net, cooldown=cooldown_rule(r, net))
    ROLE_STRONG.clear()
    for rl in {r["role"] for r in new.values()}:
        ROLE_STRONG[rl] = P.q([r["net_power_r1"] for r in new.values() if r["role"] == rl], LOAD["strong_role_quantile"])
    enforce_budget(new)
    # Owner exceptions (config/skill_power_model.json timing.exceptions.skills): the written
    # cooldown and cast_time stand, the rule keeps them as they are (kit load above already ran
    # on the rule's values, so an exception never moves another skill).
    for sid in EXCEPTIONS:
        if sid not in new:
            raise SystemExit(f"timing.exceptions: unknown skill '{sid}'")
        new[sid]["cooldown"] = cur[sid]["cooldown"]
        new[sid]["cast_time"] = cur[sid]["cast_time"]
    return cur, new, skills


# ---------------------------------------------------------------- description copies

def fix_copies(text, desc_field, want):
    """text with every copy of cast_time / cooldown in `desc_field` following the wanted
    value: dropped when the value is 0, else set to it. Works on the decoded string and on
    the raw JSON value alike (copies hold no escape)."""
    for field, rules in COPIES["drop_when_zero"].items():
        if want[field] == 0:
            for rule in (r for r in rules if r["field"] == desc_field):
                text = re.sub(rule["pattern"], lambda m: (m.groupdict().get("next") or "").upper(), text)
    for field, rules in COPIES["sync"].items():
        for rule in (r for r in rules if r["field"] == desc_field):
            def fix(m, rule=rule, v=want[field]):
                n = m.group("n")
                if float(n.replace(",", ".")) == v:
                    return m.group(0)
                sep = "," if "," in n else "." if "." in n else rule["decimal"]
                num = f"{v:g}".replace(".", sep)
                out, a = m.group(0), m.start("n") - m.start()
                out = out[:a] + num + out[m.end("n") - m.start():]
                if "article_an" in rule:   # English article before the new number
                    art = "an" if any(num.startswith(x) for x in rule["article_an"]) else "a"
                    s0, e0 = m.start("art") - m.start(), m.end("art") - m.start()
                    out = out[:s0] + (art.capitalize() if out[s0].isupper() else art) + out[e0:]
                return out
            text = re.sub(rule["pattern"], fix, text)
    return text


def desc_fields():
    return sorted({r["field"] for kind in ("sync", "drop_when_zero")
                   for rules in COPIES[kind].values() for r in rules})


# ---------------------------------------------------------------- apply / check

def typed(old, v):
    return int(v) if isinstance(old, int) and float(v).is_integer() else float(v)


def differences(state=None):
    """[(class, skill_id, field, have, want)]"""
    cur, new, skills = state or plan()
    out = []
    for sid, r in sorted(new.items()):
        s = skills[sid]
        for f in FIELDS:
            if (s.get(f) or 0) != r[f]:
                out.append((r["class"], sid, f, s.get(f) or 0, r[f]))
        for f in desc_fields():
            text = s.get(f) or ""
            if fix_copies(text, f, r) != text:
                out.append((r["class"], sid, f, text, fix_copies(text, f, r)))
    return out


def edit_block(s, want):
    def edit(block, nl):
        block = S.set_fields(block, {f: typed(s.get(f), want[f]) for f in FIELDS
                                     if (s.get(f) or 0) != want[f]}, nl, {"cast_time": "cooldown"})
        for f in desc_fields():
            m = S.top_level_field(block, f, value=r'("(?:[^"\\]|\\.)*")')
            if m:
                block = block[:m.start(1)] + fix_copies(m.group(1), f, want) + block[m.end(1):]
        return block
    return edit


def apply():
    state = plan()
    _, new, skills = state
    diffs = differences(state)
    edits = {}
    for cls, sid, *_ in diffs:
        edits.setdefault(cls, {})[sid] = edit_block(skills[sid], new[sid])
    S.rewrite_skills(edits)
    left = differences()
    if left:
        raise SystemExit(f"post-check failed: {left[:5]}")
    return diffs


# ---------------------------------------------------------------- report

q = P.q


def bands(rows, cdr_of):
    """{band label: (kit loads, share of time on non-filler skills)}, cooldowns reduced by
    cdr_of(row)."""
    scaled = {k: dict(r, cooldown=r["cooldown"] * (1 - cdr_of(r))) for k, r in rows.items()}
    dur = P.M["report"]["spam_duration_seconds"]
    out = {}
    for label, tiers in P.LEVEL_BARS:
        loads, share = [], []
        for *_, kit in P.kit_rows(list(scaled.values())):
            b = P.bar(kit, tiers)
            loads.append(P.kit_load(b, weight=load_weight))
            share.append(P.spam_fraction([(r["cooldown"], r["cast_time"], r["power"][0]) for r in b], 0.0, dur))
        out[label] = (loads, share)
    return out


def cdr_options():
    """[(label, cdr_of)]: no reduction, the current cap, then the model's options."""
    opts = [("CDR 0", lambda r: 0.0), (f"CDR {P.CDR_CAP:.0%} (plafond actuel)", lambda r: P.CDR_CAP)]
    for o in T["cdr_options"]["options"]:
        cap, excl = o["cap_percent"] / 100, set(o.get("excluded_roles", []))
        opts.append((o["label"], lambda r, cap=cap, excl=excl: 0.0 if r["role"] in excl else cap))
    return opts


def print_bands(title, rows, opts):
    print(f"\n### {title}\n")
    print("| barre | reduction | charge med (min-max) | part du temps med (q1-q3) | kits a 100 % | kits > budget |")
    print("|---|---|---|---|---|---|")
    for label, cdr_of in opts:
        for band, (ld, sh) in bands(rows, cdr_of).items():
            print(f"| {band} | {label} | {q(ld, .5):.2f} ({min(ld):.2f}-{max(ld):.2f}) | "
                  f"{q(sh, .5):.0%} ({q(sh, .25):.0%}-{q(sh, .75):.0%}) | {sum(x >= 0.999 for x in sh)}/{len(sh)} | "
                  f"{sum(x > LOAD['budget'] + 1e-9 for x in ld)}/{len(ld)} |")


def report():
    cur, new, skills = plan()
    R = P.M["report"]
    ch_cd = [k for k in new if new[k]["cooldown"] != cur[k]["cooldown"]]
    ch_cast = [k for k in new if new[k]["cast_time"] != cur[k]["cast_time"]]
    print(f"# Cooldowns et incantations : regle de config/skill_power_model.json timing ({len(new)} sorts)\n")
    print(f"Cooldown change : {len(ch_cd)} (dont {sum(new[k]['cooldown'] < cur[k]['cooldown'] for k in ch_cd)} "
          f"raccourcis) ; incantation changee : {len(ch_cast)} ; sorts touches : {len(set(ch_cd) | set(ch_cast))}.")
    copies = [d for d in differences((cur, new, skills)) if d[2] not in FIELDS]
    print(f"Copies de description a aligner : {len(copies)}.")

    print("\n## Par role (cooldown en s : actuel -> regle)\n")
    print("| role | n | q1 | mediane | q3 | min-max | changes | cast med (actuel -> regle) |")
    print("|---|---|---|---|---|---|---|---|")
    for rl in P.M["roles"]["order"]:
        ids = [k for k in new if new[k]["role"] == rl]
        a, b = [cur[k]["cooldown"] for k in ids], [new[k]["cooldown"] for k in ids]
        print(f"| {rl} | {len(ids)} | {q(a, .25):g} -> {q(b, .25):g} | {q(a, .5):g} -> {q(b, .5):g} | "
              f"{q(a, .75):g} -> {q(b, .75):g} | {min(a):g}-{max(a):g} -> {min(b):g}-{max(b):g} | "
              f"{sum(x != y for x, y in zip(a, b))} | {q([cur[k]['cast_time'] for k in ids], .5):g} -> "
              f"{q([new[k]['cast_time'] for k in ids], .5):g} |")

    print(f"\n## Enchainement hors remplissage (GCD {P.GCD:g} s, barre de {P.SKILL_BAR} cases, Souffle illimite, "
          f"budget de charge {LOAD['budget']:g} sans reduction)")
    opts = cdr_options()
    print_bands("Actuel", cur, opts[:2])
    print_bands("Regle", new, opts)

    print(f"\n## Les {R['top_n']} plus gros changements (rapport nouveau / ancien cooldown)\n")
    top = sorted(set(ch_cd) | set(ch_cast), key=lambda k: (-new[k]["cooldown"] / cur[k]["cooldown"], k))
    for k in top[:R["top_n"]]:
        a, b = cur[k], new[k]
        cast = f", cast {a['cast_time']:g} -> {b['cast_time']:g} s" if a["cast_time"] != b["cast_time"] else ""
        print(f"- {k} ({b['role']}, {b['dominant']}) : {a['cooldown']:g} -> {b['cooldown']:g} s{cast} ; "
              f"puissance nette r1 {b['net_power_r1']:.0f}, densite {a['net_power_r1'] / a['cooldown']:.1f} -> "
              f"{b['net_power_r1'] / b['cooldown']:.1f}/s (admise {density(b):g})")
    long_cast = R["long_cast_seconds"]

    def bucket(c):
        return "instantane" if c == 0 else f"<= {P.GCD:g} s" if c <= P.GCD else \
            f"{P.GCD:g}-{long_cast:g} s" if c < long_cast else f">= {long_cast:g} s"
    names = ["instantane", f"<= {P.GCD:g} s", f"{P.GCD:g}-{long_cast:g} s", f">= {long_cast:g} s"]
    print(f"\n## Incantations : repartition (actuel -> regle), {len(ch_cast)} changees\n")
    print("| classe | " + " | ".join(names) + " |")
    print("|---|" + "---|" * len(names))
    for cls in S.CLASSES + ["toutes"]:
        ids = [k for k in new if cls in ("toutes", new[k]["class"])]
        a_, b_ = ([bucket(src[k]["cast_time"]) for k in ids] for src in (cur, new))
        print(f"| {cls} | " + " | ".join(f"{a_.count(n)} -> {b_.count(n)}" for n in names) + " |")
    reflex = [k for k in new if is_reflex(skills[k], new[k])]
    print(f"\nReflexes (toujours instantanes) : {len(reflex)} ; incantes avant, passes a 0 : "
          f"{sum(cur[k]['cast_time'] > 0 for k in reflex)}.")
    cap = CAST["melee_cap"]
    prep = [k for k in new if new[k]["cast_time"] > 0 and set(class_entry(new[k]).get("role_tags", [])) & set(cap["role_tags"])]
    print(f"Preparations de contact (sous-classes {'/'.join(cap['role_tags'])}, plafond {cap['seconds']:g} s) : {len(prep)}, "
          f"dont {sum(cur[k]['cast_time'] == 0 for k in prep)} instantanes avant.")
    print("\nIncantations les plus allongees :")
    for k in sorted(ch_cast, key=lambda k: (cur[k]["cast_time"] - new[k]["cast_time"], k))[:R["top_n"]]:
        print(f"- {k} ({new[k]['role']}, {new[k]['class']}) : {cur[k]['cast_time']:g} -> {new[k]['cast_time']:g} s, "
              f"puissance brute r1 {new[k]['power'][0]:.0f}")
    floor = CAST["floor_by_role"]
    loose = [k for k in new if new[k]["role"] in floor and new[k]["cast_time"] < floor[new[k]["role"]]]
    print(f"\nSorts sous le plancher de leur role (reflexes) : {len(loose)}" + "".join(f"\n- {k}" for k in sorted(loose)))

    over = []
    for cls, sub, spec, kit in P.kit_rows(list(new.values())):
        for band, tiers in P.LEVEL_BARS:
            b = P.bar(kit, tiers)
            ld = P.kit_load(b, weight=load_weight)
            if ld > LOAD["budget"] + 1e-9:
                over.append(f"{spec} ({band}) {ld:.2f}, dont sorts forts "
                            f"{P.kit_load([r for r in b if strong(r)], weight=load_weight):.2f}")
    print(f"\n## Kits au-dessus du budget apres la regle : {len(over)} (charge ponderee, sorts reactifs "
          f"x{LOAD['reactive_weight']:g} ; le reste vient de sorts faibles, que le budget n'allonge pas)")
    for o in over:
        print("- " + o)
    if copies:
        print("\n## Copies de description")
        for cls, sid, f, have, want in copies:
            print(f"- {sid} {f} : {want}")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if a skill differs from the rules, write nothing")
    ap.add_argument("--report", action="store_true", help="current -> rule, kit load, spam, CDR options")
    a = ap.parse_args()
    if a.report:
        report()
        return
    diffs = differences() if a.check else apply()
    for cls, sid, field, have, want in diffs:
        if field in FIELDS:
            print(f"{cls:8} {sid:52} {field:10} {have!s:>6} -> {want:g}")
        else:
            print(f"{cls:8} {sid:52} {field}: {want}")
    print(f"{len(diffs)} difference(s) {'found' if a.check else 'applied'}"
          + ("" if a.check or not diffs else " ; regenerate the matrix: python -X utf8 scripts/balance/skill_power_matrix.py"))
    if diffs and a.check:
        sys.exit(1)


if __name__ == "__main__":
    main()
