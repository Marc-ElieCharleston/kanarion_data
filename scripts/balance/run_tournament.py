"""Level-20 2v2 tournament balance table.

Stage 1: for every composition (pair of subclasses) build a small set of candidate
         allocations: best responses (HiGHS MILP rotations + exhaustive allocation
         sweep) against a fixed panel of reference opponents, plus generic builds.
Stage 2: for every matchup (composition vs composition) evaluate all candidate
         pairs, map the TTFK margin to a win probability, and solve the zero-sum
         game (HiGHS LP) for the equilibrium value and builds.

Outputs (scripts/balance/out/): matchups.csv, compositions.csv, subclasses.csv,
candidates.csv, report.md
"""
from __future__ import annotations

import argparse
import csv
import itertools
import os
import pickle
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import multiprocessing as mp

import numpy as np

from balance import alloc_pts, balance_matchup
from evalmodel import Member, evaluate, stack_plans
from game import solve_zero_sum, win_prob
from kdata import STAT_POINTS, load_subclasses
from plans import T_GRID, W_GRID, build_tables, main_stat
from search import best_response, default_build, make_member

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
REFERENCE_OPPONENTS = [("guardian", "lifewarden"), ("berserker", "ranger"), ("elementalist", "occultist"),
                       ("shadowblade", "lightbringer"), ("weaponmaster", "cantor"), ("gunslinger", "alchemist")]
def generic_builds(b):
    """Generic allocations scaled to a budget b."""
    third = b // 3
    return {"tank": (b, 0, 0, 0), "glass": (0, 0, b, 0), "breath": (b - 2 * third, third, third, 0), "wall": (b - b // 2, 0, 0, b // 2)}

_G = {}   # worker globals, filled by init_worker


def load_plans(pk):
    with open(pk, "rb") as f:
        return stack_plans(pickle.load(f))


def init_worker(pk, ref_keys, budgets, comps=None, cands=None, tau=2.0, refine=0, balance=False, tol=0.5):
    subs = load_subclasses()
    plans = load_plans(pk)
    refs = [(name, members_from_key(subs, plans, comp, key)) for name, comp, key in ref_keys]
    _G.update(subs=subs, plans=plans, refs=refs, budgets=budgets, comps=comps, cands=cands, tau=tau, refine=refine,
              balance=balance, tol=tol)


def fmt_t(t):
    """Time to first kill; 'none' when a side cannot kill within a minute."""
    return f"{t:.1f}" if t < 99.0 else "none"


def alloc_tuple(m: Member):
    a = m.alloc
    return (int(a["hp"][0]), int(a["mp"][0]), int(a[main_stat(m.sub)][0]), int(a["def"][0]))


def team_key(ms):
    return (alloc_tuple(ms[0]), int(np.ravel(ms[0].wi)[0]), alloc_tuple(ms[1]), int(np.ravel(ms[1].wi)[0]))


def derived(sub, pts):
    main = main_stat(sub)
    x = {"hp": pts[0], "mp": pts[1], main: pts[2], "def": pts[3], ("mag" if main == "atk" else "atk"): 0}
    st = sub.stats(x)
    return {k: round(float(st[k]), 1) for k in ("hp", "mp", "atk", "mag", "armor", "magic_resist")}


def alloc_str(sub, pts, wi):
    return f"hp{pts[0]}/mp{pts[1]}/{main_stat(sub)}{pts[2]}/def{pts[3]}/w{W_GRID[wi]}"


def parse_alloc(a):
    parts = a.split("/")
    pts = tuple(int("".join(ch for ch in q if ch.isdigit())) for q in parts[:4])
    wi = W_GRID.index(float(parts[4][1:]))
    return pts, wi


def load_candidates(path):
    cands = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            comp = (row["subclass_1"], row["subclass_2"])
            (p1, w1), (p2, w2) = parse_alloc(row["alloc_1"]), parse_alloc(row["alloc_2"])
            cands.setdefault(comp, {})[(p1, w1, p2, w2)] = row["tag"]
    return cands


def stage1_comp(comp):
    subs, plans, refs, budgets = _G["subs"], _G["plans"], _G["refs"], _G["budgets"]
    sX = [subs[comp[0]], subs[comp[1]]]
    bX = [budgets[comp[0]], budgets[comp[1]]]
    cands = {}
    def add(ms, tag):
        cands.setdefault(team_key(ms), tag)
    add([default_build(s, plans, budget=b) for s, b in zip(sX, bX)], "default")
    for name in generic_builds(57):
        add([make_member(s, plans, [generic_builds(b)[name]], 1) for s, b in zip(sX, bX)], name)
    for rname, Y in refs:
        X, m = best_response(sX, Y, plans, rounds=3, budgets=bX)
        add(X, f"br:{rname}")
    return comp, cands


def members_from_key(subs, plans, comp, key):
    return [make_member(subs[comp[0]], plans, [key[0]], key[1]), make_member(subs[comp[1]], plans, [key[2]], key[3])]


def stage2_pair(args):
    ci, cj = args
    subs, plans, comps, cands, tau = _G["subs"], _G["plans"], _G["comps"], _G["cands"], _G["tau"]
    A, B = comps[ci], comps[cj]
    ka, kb = list(cands[A].keys()), list(cands[B].keys())
    def side(comp, keys, idx):
        ms = []
        for slot in (0, 1):
            pts = np.array([keys[i][2 * slot] for i in idx]); wis = np.array([keys[i][2 * slot + 1] for i in idx])
            ms.append(make_member(subs[comp[slot]], plans, pts, wis))
        return ms
    def payoff(ka, kb):
        na, nb = len(ka), len(kb)
        ia = np.repeat(np.arange(na), nb); ib = np.tile(np.arange(nb), na)
        r = evaluate(side(A, ka, ia), side(B, kb, ib))
        return r, r["margin_d"].reshape(na, nb)
    r, M = payoff(ka, kb)
    P = win_prob(M, tau)
    v, x, y = solve_zero_sum(P)
    if _G.get("refine", 0) > 0:
        # best responses against the exact opponent, starting from the pool equilibrium
        budgets = _G["budgets"]
        curA = members_from_key(subs, plans, A, ka[int(np.argmax(x))])
        curB = members_from_key(subs, plans, B, kb[int(np.argmax(y))])
        for _ in range(_G["refine"]):
            curA, _m = best_response([subs[A[0]], subs[A[1]]], curB, plans, start=curA, rounds=2, step=4,
                                     budgets=[budgets[A[0]], budgets[A[1]]], w_fixed=[int(np.ravel(m.wi)[0]) for m in curA])
            if team_key(curA) not in cands[A]:
                ka.append(team_key(curA))
            curB, _m = best_response([subs[B[0]], subs[B[1]]], curA, plans, start=curB, rounds=2, step=4,
                                     budgets=[budgets[B[0]], budgets[B[1]]], w_fixed=[int(np.ravel(m.wi)[0]) for m in curB])
            if team_key(curB) not in cands[B]:
                kb.append(team_key(curB))
        ka = list(dict.fromkeys(ka)); kb = list(dict.fromkeys(kb))
        r, M = payoff(ka, kb)
        P = win_prob(M, tau)
        v, x, y = solve_zero_sum(P)
    na, nb = len(ka), len(kb)
    i, j = int(np.argmax(x)), int(np.argmax(y))
    tag = lambda comp, k: cands[comp].get(k, "br:opponent")
    bal = None
    if _G.get("balance"):
        mA = members_from_key(subs, plans, A, ka[i]); mB = members_from_key(subs, plans, B, kb[j])
        res = balance_matchup([subs[A[0]], subs[A[1]]], [subs[B[0]], subs[B[1]]], mA, mB, plans, tol=_G.get("tol", 0.5))
        e = res["explain"]
        bal = {"allocA": [tuple(alloc_pts(m)) for m in res["A"]], "allocB": [tuple(alloc_pts(m)) for m in res["B"]],
               "wA": [int(np.ravel(m.wi)[0]) for m in res["A"]], "wB": [int(np.ravel(m.wi)[0]) for m in res["B"]],
               "margin": res["margin"], "margin0": res["margin0"], "strong": res["strong"], "moved": res["points_moved"],
               "moved_A": res["moved_A"], "moved_B": res["moved_B"],
               "ttfk_A": e["ttfk_X"], "ttfk_B": e["ttfk_Y"], "T": e["T"]}
    def mix(strat, keys, comp):
        order = np.argsort(-strat)
        return "; ".join(f"{strat[o]:.2f}:{alloc_str(subs[comp[0]], keys[o][0], keys[o][1])}+{alloc_str(subs[comp[1]], keys[o][2], keys[o][3])}"
                         for o in order if strat[o] >= 0.05)
    return {
        "A": A, "B": B, "value": v, "keyA": ka[i], "keyB": kb[j],
        "margin": float(M[i, j]), "ttfk_A": float(r["ttfk_X"].reshape(na, nb)[i, j]), "ttfk_B": float(r["ttfk_Y"].reshape(na, nb)[i, j]),
        "mixed_A": bool(x.max() < 0.99), "mixed_B": bool(y.max() < 0.99),
        "tagA": tag(A, ka[i]), "tagB": tag(B, kb[j]), "mixA": mix(x, ka, A), "mixB": mix(y, kb, B), "bal": bal,
    }


def load_budgets(path, ids):
    budgets = {s: STAT_POINTS for s in ids}
    if path:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                budgets[row["subclass"]] = int(row["budget"])
    return budgets


def run_pipeline(budgets, out_dir=OUT, workers=None, tau=2.0, no_repeats=False, limit=0, from_candidates=False, quiet=False, refine=0,
                 balance=False, tol=0.5):
    """Full two-stage run with per-subclass point budgets. Returns (comps, comp_score, sub_score dict)."""
    workers = workers or max(1, os.cpu_count() - 1)
    log = (lambda *a: None) if quiet else (lambda *a: print(*a, flush=True))
    os.makedirs(out_dir, exist_ok=True)
    subs = load_subclasses()
    ids = sorted(subs)
    _G["subs"] = subs
    pk = os.path.join(OUT, "plans.pkl")
    if not os.path.exists(pk):
        log("building rotation tables (HiGHS MILP)...")
        build_tables(subs, pk, verbose=not quiet)
    plans = load_plans(pk)
    _G["plans"] = plans
    comps = [c for c in itertools.combinations_with_replacement(ids, 2) if not (no_repeats and c[0] == c[1])]
    if limit:
        comps = comps[:limit]
    log(f"{len(comps)} compositions, {len(comps) * (len(comps) + 1) // 2} matchups")

    ref_members = {r: [default_build(subs[r[0]], plans, budget=budgets[r[0]]), default_build(subs[r[1]], plans, budget=budgets[r[1]])]
                   for r in REFERENCE_OPPONENTS}
    for r in REFERENCE_OPPONENTS:
        others = [m for rr, m in ref_members.items() if rr != r]
        X, _ = best_response([subs[r[0]], subs[r[1]]], others[0], plans, rounds=2, budgets=[budgets[r[0]], budgets[r[1]]])
        ref_members[r] = X
    ref_keys = [(f"{r[0]}+{r[1]}", r, team_key(ref_members[r])) for r in REFERENCE_OPPONENTS]
    for name, r, key in ref_keys:
        log(f"  reference {name}: {alloc_str(subs[r[0]], key[0], key[1])} | {alloc_str(subs[r[1]], key[2], key[3])}")
    ctx = mp.get_context("spawn")

    t0 = time.time()
    cands = {}
    cand_path = os.path.join(out_dir, "candidates.csv")
    if from_candidates:
        cands = {c: cd for c, cd in load_candidates(cand_path).items() if c in set(comps)}
        comps = [c for c in comps if c in cands]
        log(f"loaded candidates for {len(comps)} compositions")
    else:
        with ctx.Pool(workers, initializer=init_worker, initargs=(pk, ref_keys, budgets)) as pool:
            for n, (comp, cd) in enumerate(pool.imap_unordered(stage1_comp, comps, chunksize=2)):
                cands[comp] = cd
                if n % 50 == 0:
                    log(f"  stage 1: {n}/{len(comps)} comps, {time.time() - t0:.0f}s")
        with open(cand_path, "w", newline="") as f:
            wr = csv.writer(f); wr.writerow(["subclass_1", "subclass_2", "tag", "alloc_1", "alloc_2", "stats_1", "stats_2"])
            for comp, cd in sorted(cands.items()):
                for key, tag in cd.items():
                    wr.writerow([comp[0], comp[1], tag, alloc_str(subs[comp[0]], key[0], key[1]), alloc_str(subs[comp[1]], key[2], key[3]),
                                 derived(subs[comp[0]], key[0]), derived(subs[comp[1]], key[2])])
        log(f"stage 1 done in {time.time() - t0:.0f}s; candidates/comp avg {np.mean([len(c) for c in cands.values()]):.1f}")

    pairs = [(i, j) for i in range(len(comps)) for j in range(i, len(comps))]
    t0 = time.time()
    rows = []
    with ctx.Pool(workers, initializer=init_worker, initargs=(pk, ref_keys, budgets, comps, cands, tau, refine, balance, tol)) as pool:
        for n, r in enumerate(pool.imap_unordered(stage2_pair, pairs, chunksize=64)):
            rows.append(r)
            if n % 10000 == 0:
                log(f"  stage 2: {n}/{len(pairs)} matchups, {time.time() - t0:.0f}s")
    log(f"stage 2 done in {time.time() - t0:.0f}s")

    if balance:
        with open(os.path.join(out_dir, "balanced.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["class1", "class2", "class3", "class4", "lock_class1", "lock_class2", "lock_class3", "lock_class4",
                        "p_team12_wins_locked", "margin_s_locked", "ttfk_team12", "ttfk_team34", "horizon_s",
                        "favoured_before", "points_moved", "points_moved_12", "points_moved_34", "p_team12_wins_free", "best_class1", "best_class2", "best_class3", "best_class4"])
            for r in sorted(rows, key=lambda r: (r["A"], r["B"])):
                A, B, b = r["A"], r["B"], r["bal"]
                p_lock = 1 / (1 + np.exp(-b["margin"] / tau))
                w.writerow([A[0], A[1], B[0], B[1],
                            alloc_str(subs[A[0]], b["allocA"][0], b["wA"][0]), alloc_str(subs[A[1]], b["allocA"][1], b["wA"][1]),
                            alloc_str(subs[B[0]], b["allocB"][0], b["wB"][0]), alloc_str(subs[B[1]], b["allocB"][1], b["wB"][1]),
                            f"{p_lock:.3f}", f"{b['margin']:+.2f}", fmt_t(b["ttfk_A"]), fmt_t(b["ttfk_B"]), f"{b['T']:.0f}",
                            b["strong"], b["moved"], b["moved_A"], b["moved_B"], f"{min(1.0, max(0.0, r['value'])):.3f}",
                            alloc_str(subs[A[0]], r["keyA"][0], r["keyA"][1]), alloc_str(subs[A[1]], r["keyA"][2], r["keyA"][3]),
                            alloc_str(subs[B[0]], r["keyB"][0], r["keyB"][1]), alloc_str(subs[B[1]], r["keyB"][2], r["keyB"][3])])
        moved = np.array([r["bal"]["moved"] for r in rows]); mg = np.array([abs(r["bal"]["margin"]) for r in rows])
        log(f"balanced: |margin| <= {tol}s in {(mg <= tol + 1e-9).mean():.0%} of matchups; points moved median {np.median(moved):.0f}, p90 {np.percentile(moved, 90):.0f}")

    with open(os.path.join(out_dir, "matchups.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["class1", "class2", "class3", "class4", "p_team12_wins", "alloc_class1", "alloc_class2", "alloc_class3", "alloc_class4",
                    "ttfk_team12", "ttfk_team34", "margin_s", "mixed_12", "mixed_34", "build_tag_12", "build_tag_34", "equilibrium_mix_12", "equilibrium_mix_34"])
        for r in sorted(rows, key=lambda r: (r["A"], r["B"])):
            A, B, ka, kb = r["A"], r["B"], r["keyA"], r["keyB"]
            w.writerow([A[0], A[1], B[0], B[1], f"{min(1.0, max(0.0, r['value'])):.3f}",
                        alloc_str(subs[A[0]], ka[0], ka[1]), alloc_str(subs[A[1]], ka[2], ka[3]),
                        alloc_str(subs[B[0]], kb[0], kb[1]), alloc_str(subs[B[1]], kb[2], kb[3]),
                        fmt_t(r['ttfk_A']), fmt_t(r['ttfk_B']), f"{max(-99.0, min(99.0, r['margin'])):.2f}",
                        int(r["mixed_A"]), int(r["mixed_B"]), r["tagA"], r["tagB"], r["mixA"], r["mixB"]])

    idx = {c: i for i, c in enumerate(comps)}
    V = np.full((len(comps), len(comps)), np.nan)
    for r in rows:
        i, j = idx[r["A"]], idx[r["B"]]
        V[i, j] = r["value"]; V[j, i] = 1 - r["value"]
    comp_score = np.nanmean(V, axis=1)
    with open(os.path.join(out_dir, "compositions.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["subclass_1", "subclass_2", "mean_win_prob", "worst_matchup", "worst_p", "best_matchup", "best_p"])
        for i in np.argsort(-comp_score):
            row = V[i].copy(); row[i] = np.nan
            wi_, bi_ = int(np.nanargmin(row)), int(np.nanargmax(row))
            w.writerow([comps[i][0], comps[i][1], f"{comp_score[i]:.3f}", "+".join(comps[wi_]), f"{row[wi_]:.3f}", "+".join(comps[bi_]), f"{row[bi_]:.3f}"])
    sub_lists = {s: [] for s in ids}
    for i, c in enumerate(comps):
        for s in set(c):
            sub_lists[s].append(comp_score[i])
    sub_score = {s: float(np.mean(v)) for s, v in sub_lists.items() if v}
    with open(os.path.join(out_dir, "subclasses.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["subclass", "base_class", "budget", "mean_win_prob_over_pairings", "best_partner", "best_pair_p"])
        for s in sorted(sub_score, key=lambda s: -sub_score[s]):
            best = max((comp_score[i], c) for i, c in enumerate(comps) if s in c)
            partner = best[1][0] if best[1][1] == s else best[1][1]
            w.writerow([s, subs[s].base_class, budgets[s], f"{sub_score[s]:.3f}", partner, f"{best[0]:.3f}"])
    with open(os.path.join(out_dir, "run_summary.txt"), "w") as f:
        f.write(f"compositions={len(comps)} matchups={len(pairs)} tau={tau} no_repeats={no_repeats}\n")
        f.write(f"budgets={budgets}\n")
        f.write(f"spread of composition mean win prob: min={comp_score.min():.3f} max={comp_score.max():.3f}\n")
        if sub_score:
            f.write(f"spread of subclass mean win prob: min={min(sub_score.values()):.3f} max={max(sub_score.values()):.3f}\n")
    log("outputs written to", out_dir)
    return comps, comp_score, sub_score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-repeats", action="store_true", help="forbid the same subclass twice in a team")
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() - 1))
    ap.add_argument("--tau", type=float, default=2.0, help="seconds of TTFK margin per logit of win probability")
    ap.add_argument("--limit", type=int, default=0, help="debug: only the first N compositions")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--from-candidates", action="store_true", help="skip stage 1, reuse out/candidates.csv")
    ap.add_argument("--budgets", default="", help="CSV with columns subclass,budget (default 57 for everyone)")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--refine", type=int, default=0, help="best-response rounds against the exact opponent per matchup (0 = pool only)")
    ap.add_argument("--balance", action="store_true", help="lock all four allocations per matchup so P(win) = 0.5; writes balanced.csv")
    ap.add_argument("--tol", type=float, default=0.5, help="balance: acceptable |kill-time margin| in seconds")
    args = ap.parse_args()
    if args.rebuild and os.path.exists(os.path.join(OUT, "plans.pkl")):
        os.remove(os.path.join(OUT, "plans.pkl"))
    budgets = load_budgets(args.budgets, sorted(load_subclasses()))
    run_pipeline(budgets, out_dir=args.out, workers=args.workers, tau=args.tau, no_repeats=args.no_repeats,
                 limit=args.limit, from_candidates=args.from_candidates, refine=args.refine, balance=args.balance, tol=args.tol)


if __name__ == "__main__":
    main()
