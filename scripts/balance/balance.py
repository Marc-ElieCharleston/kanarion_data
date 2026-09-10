"""Balanced allocations for one matchup: lock all four characters' stat points so the
fight is a coin flip.

1. References: each team's play-to-win build, settled by mutual best response starting
   from the given builds.
2. Handicap: coordinate descent over all four characters. Each sweep tries every
   allocation of one character (others fixed) and keeps the one with the smallest
   kill-time margin; among allocations within `tol` seconds of zero, the one closest in
   points to the references wins. The favoured side ends up giving points up, the other
   side stays near its best build.
"""
from __future__ import annotations

import numpy as np

from evalmodel import evaluate, explain
from plans import main_stat
from search import alloc_grid, best_response, make_member


def alloc_pts(m):
    a = m.alloc
    return np.array([int(a["hp"][0]), int(a["mp"][0]), int(a[main_stat(m.sub)][0]), int(a["def"][0])])


def _pick(margin, dist, tol):
    ok = np.abs(margin) <= tol
    if ok.any():
        return int(np.argmin(np.where(ok, dist + 1e-3 * np.abs(margin), np.inf)))
    return int(np.argmin(np.abs(margin) + 1e-3 * dist))


def handicap(A, B, plans, refA, refB, tol=0.25, passes=3, step=3, refine=3):
    """Coordinate descent over the four characters. Returns (A, B, margin)."""
    cur = [A[0], A[1], B[0], B[1]]
    refs = [refA[0], refA[1], refB[0], refB[1]]
    m = float(np.ravel(evaluate(cur[:2], cur[2:])["margin"])[0])
    for _ in range(passes):
        if abs(m) <= tol:
            break
        # sweep the favoured side's characters first
        order = [0, 1, 2, 3] if m > 0 else [2, 3, 0, 1]
        for k in order:
            sub, wi = cur[k].sub, int(np.ravel(cur[k].wi)[0])
            other_dist = sum(np.abs(alloc_pts(cur[j]) - refs[j]).sum() / 2 for j in range(4) if j != k)
            for grid in (alloc_grid(step), alloc_grid(1, center=tuple(alloc_pts(cur[k])), radius=refine)):
                cand = make_member(sub, plans, grid, wi)
                team = list(cur); team[k] = cand
                r = evaluate(team[:2], team[2:])
                dist = np.abs(grid - refs[k]).sum(axis=1) / 2 + other_dist
                i = _pick(r["margin"], dist, tol)
                cur[k] = make_member(sub, plans, [tuple(grid[i])], wi)
                m = float(r["margin"][i])
            if abs(m) <= tol:
                break
    return cur[:2], cur[2:], m


def balance_matchup(subsA, subsB, A, B, plans, tol=0.25, passes=3, br_rounds=1, verbose=False):
    """A, B: starting builds (Members). Returns dict with locked builds and diagnostics."""
    wA = [int(np.ravel(m.wi)[0]) for m in A]; wB = [int(np.ravel(m.wi)[0]) for m in B]
    for _ in range(br_rounds):
        A, _ = best_response(subsA, B, plans, start=A, rounds=2, step=3, w_fixed=wA)
        B, _ = best_response(subsB, A, plans, start=B, rounds=2, step=3, w_fixed=wB)
    refA, refB = [alloc_pts(m) for m in A], [alloc_pts(m) for m in B]
    m0 = float(np.ravel(evaluate(A, B)["margin"])[0])
    A2, B2, m = handicap(A, B, plans, refA, refB, tol=tol, passes=passes)
    if verbose:
        print(f"  play-to-win margin {m0:+.2f} s -> locked margin {m:+.2f} s")
    moved_A = int(sum(np.abs(alloc_pts(x) - r).sum() / 2 for x, r in zip(A2, refA)))
    moved_B = int(sum(np.abs(alloc_pts(x) - r).sum() / 2 for x, r in zip(B2, refB)))
    return {"A": A2, "B": B2, "margin0": m0, "margin": m, "strong": "A" if m0 > 0 else ("B" if m0 < 0 else "-"),
            "points_moved": moved_A + moved_B, "moved_A": moved_A, "moved_B": moved_B,
            "explain": explain(A2, B2), "refA": refA, "refB": refB}
