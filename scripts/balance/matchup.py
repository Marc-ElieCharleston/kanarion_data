"""Optimal allocations for one 2v2 matchup, computed against the exact opponent pair.

    python3 matchup.py berserker lifewarden vs elementalist guardian [--rounds 4] [--step 3]

Both teams iterate best responses against each other; every build visited (plus the
generic and reference-based candidates from the full run, if present) enters a
zero-sum game solved by LP. The result is the equilibrium: a pure pair of builds when
the iteration converges, a mixed recommendation otherwise.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np

from evalmodel import explain
from game import solve_zero_sum, win_prob
from kdata import load_subclasses
from plans import T_GRID, W_GRID, main_stat
from run_tournament import OUT, alloc_str, derived, generic_builds, load_candidates, load_plans, members_from_key, team_key
from search import best_response, default_build, make_member


def rotation(m, ti):
    p = m.plan(ti)
    casts = np.ravel(p["casts"]) if p["casts"].ndim == 1 else p["casts"][0]
    return [(sk.name, int(k)) for sk, k in zip(m.sub.skills, casts) if k > 0]


def main():
    argv = sys.argv[1:]
    if "vs" not in argv or len(argv) < 5:
        print(__doc__); sys.exit(1)
    i = argv.index("vs")
    A, B = tuple(argv[:i]), tuple(argv[i + 1:i + 3])
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--step", type=int, default=3)
    ap.add_argument("--tau", type=float, default=2.0)
    ap.add_argument("--balance", action="store_true", help="lock all four allocations so the matchup is a coin flip")
    ap.add_argument("--tol", type=float, default=0.25, help="balance: acceptable |margin| in seconds")
    args = ap.parse_args(argv[i + 3:])
    subs = load_subclasses()
    for s in A + B:
        if s not in subs:
            sys.exit(f"unknown subclass {s}; known: {', '.join(sorted(subs))}")
    plans = load_plans(os.path.join(OUT, "plans.pkl"))
    sA, sB = [subs[s] for s in A], [subs[s] for s in B]

    pools = {"A": {}, "B": {}}
    cand_path = os.path.join(OUT, "candidates.csv")
    if os.path.exists(cand_path):
        allc = load_candidates(cand_path)
        for side, comp in (("A", A), ("B", B)):
            key = tuple(sorted(comp))
            for k, tag in allc.get(key, {}).items():
                if key != comp:                       # stored sorted; swap slots back
                    k = (k[2], k[3], k[0], k[1])
                pools[side][k] = tag
    for side, ss in (("A", sA), ("B", sB)):
        for name in generic_builds(57):
            pools[side].setdefault(team_key([make_member(s, plans, [generic_builds(57)[name]], 1) for s in ss]), name)
        pools[side].setdefault(team_key([default_build(s, plans) for s in ss]), "default")

    curA = [default_build(s, plans) for s in sA]
    curB = [default_build(s, plans) for s in sB]
    print(f"best-response iteration, {args.rounds} rounds:")
    for r in range(args.rounds):
        curA, mA = best_response(sA, curB, plans, start=curA, rounds=2, step=args.step)
        pools["A"].setdefault(team_key(curA), f"br:round{r}")
        curB, mB = best_response(sB, curA, plans, start=curB, rounds=2, step=args.step)
        pools["B"].setdefault(team_key(curB), f"br:round{r}")
        print(f"  round {r}: A responds -> edge {mA:+.2f} per s of fight | B responds -> edge {mB:+.2f} (for B)")

    ka, kb = list(pools["A"]), list(pools["B"])
    M = np.zeros((len(ka), len(kb)))
    for x, key_a in enumerate(ka):
        for y, key_b in enumerate(kb):
            e = explain(members_from_key(subs, plans, A, key_a), members_from_key(subs, plans, B, key_b))
            kX = 2.0 * np.ceil(e["ttfk_X"] / 2.0) - 2.0; kY = 2.0 * np.ceil(e["ttfk_Y"] / 2.0) - 2.0
            M[x, y] = kY - kX
    P = win_prob(M, args.tau)
    v, xs, ys = solve_zero_sum(P)
    print(f"\nequilibrium over {len(ka)} x {len(kb)} builds: P({'+'.join(A)} wins) = {v:.3f}")

    def report(side, comp, keys, strat):
        order = [o for o in np.argsort(-strat) if strat[o] >= 0.05]
        print(f"\n== team {side}: {' + '.join(comp)} ==  " + ("pure build" if len(order) == 1 else f"mixed, {len(order)} builds"))
        for o in order:
            k = keys[o]
            print(f"  weight {strat[o]:.2f}  [{pools[side][k]}]")
            for slot, s in enumerate(comp):
                pts, wi = k[2 * slot], k[2 * slot + 1]
                d = derived(subs[s], pts)
                print(f"    {s:13s} points hp {pts[0]:2d} / souffle {pts[1]:2d} / {main_stat(subs[s])} {pts[2]:2d} / def {pts[3]:2d}   "
                      f"-> HP {d['hp']:.0f}  Souffle {d['mp']:.0f}  ATK {d['atk']:.0f}  MAG {d['mag']:.0f}  armor {d['armor']:.0f}  MR {d['magic_resist']:.0f}")
        return keys[order[0]]

    top_a = report("A", A, ka, xs)
    top_b = report("B", B, kb, ys)
    mA, mB = members_from_key(subs, plans, A, top_a), members_from_key(subs, plans, B, top_b)
    e = explain(mA, mB)
    print(f"\n== top builds head to head (fight horizon {e['T']:.0f} s) ==")
    for side, comp, ms, enemy in (("A", A, mA, B), ("B", B, mB, A)):
        d = e["sides"][0 if side == "A" else 1]
        print(f"  team {side} kills {enemy[d['focus']]} in {min(d['ttfk_per_target']):.1f} s "
              f"(per target: " + ", ".join(f"{enemy[t]} {d['ttfk_per_target'][t]:.1f} s" for t in (0, 1)) + ")")
        for slot, m in enumerate(ms):
            rot = ", ".join(f"{n} x{c}" for n, c in rotation(m, e["ti"]))
            print(f"    {comp[slot]:13s} casts: {rot}")
    print(f"  margin {e['margin']:+.1f} s in favour of team {'A' if e['margin'] > 0 else 'B'}")

    if args.balance:
        from balance import balance_matchup, alloc_pts
        print(f"\n== balancing: lock allocations so P(win) = 0.5 (tolerance {args.tol} s) ==")
        res = balance_matchup(sA, sB, mA, mB, plans, tol=args.tol, verbose=True)
        e = res["explain"]
        p = 1 / (1 + np.exp(-res["margin"] / args.tau))
        print(f"  favoured side was {res['strong']} by {abs(res['margin0']):.1f} s; locked margin {res['margin']:+.2f} s, "
              f"P({'+'.join(A)} wins) = {p:.2f}; points moved: team A {res['moved_A']}, team B {res['moved_B']}")
        for side, comp, ms, refs in (("A", A, res["A"], res["refA"]), ("B", B, res["B"], res["refB"])):
            print(f"  team {side}: {' + '.join(comp)}")
            for slot, m in enumerate(ms):
                pts, ref = alloc_pts(m), refs[slot]
                d = derived(subs[comp[slot]], tuple(pts))
                delta = "" if (pts == ref).all() else f"   (was {ref[0]}/{ref[1]}/{ref[2]}/{ref[3]})"
                print(f"    {comp[slot]:13s} LOCK hp {pts[0]:2d} / souffle {pts[1]:2d} / {main_stat(subs[comp[slot]])} {pts[2]:2d} / def {pts[3]:2d}"
                      f"   -> HP {d['hp']:.0f}  Souffle {d['mp']:.0f}  ATK {d['atk']:.0f}  MAG {d['mag']:.0f}  armor {d['armor']:.0f}  MR {d['magic_resist']:.0f}{delta}")
                rot = ", ".join(f"{n} x{c}" for n, c in rotation(m, e["ti"]))
                print(f"    {'':13s} casts: {rot}")
        for side, enemy in (("A", B), ("B", A)):
            d = e["sides"][0 if side == "A" else 1]
            print(f"  team {side} kills {enemy[d['focus']]} in {min(d['ttfk_per_target']):.1f} s (horizon {e['T']:.0f} s)")


if __name__ == "__main__":
    main()
