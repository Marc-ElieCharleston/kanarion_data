"""Best-response search: for a team X facing a fixed team Y, find the stat allocation
(57 points over hp/mp/main-offense/def) and support weight of each member that
maximizes the time-to-first-kill margin. Coordinate descent over the two members,
each step an exhaustive vectorized sweep of the allocation grid.
"""
from __future__ import annotations

import itertools

import numpy as np

from evalmodel import Member, evaluate
from kdata import STAT_POINTS
from plans import W_GRID, main_stat


def alloc_grid(step, total=STAT_POINTS, center=None, radius=None):
    """All (hp, mp, off, def) point splits summing to `total` on a grid of the given step.
    With center/radius, a local grid around a point (step 1)."""
    pts = []
    if center is None:
        vals = range(0, total + 1, step)
        for mp, off, de in itertools.product(vals, vals, vals):
            hp = total - mp - off - de
            if hp >= 0:
                pts.append((hp, mp, off, de))
    else:
        c = center
        rng = lambda v: range(max(0, v - radius), min(total, v + radius) + 1)
        for mp, off, de in itertools.product(rng(c[1]), rng(c[2]), rng(c[3])):
            hp = total - mp - off - de
            if hp >= 0:
                pts.append((hp, mp, off, de))
    return np.array(sorted(set(pts)), dtype=int)


def make_member(sub, plans, pts, wi):
    main = main_stat(sub)
    other = "mag" if main == "atk" else "atk"
    pts = np.atleast_2d(pts)
    alloc = {"hp": pts[:, 0], "mp": pts[:, 1], main: pts[:, 2], other: np.zeros(len(pts), int), "def": pts[:, 3]}
    return Member(sub, alloc, plans[sub.id], wi)


def default_build(sub, plans, wi=1, budget=STAT_POINTS):
    """Balanced starting point: ~40% HP, ~45% main offense, ~15% Souffle."""
    mp = round(0.15 * budget); off = round(0.45 * budget); hp = budget - mp - off
    return make_member(sub, plans, [(hp, mp, off, 0)], wi)


def objective(res):
    """Play-to-win score: kill-time margin per second of fight (scale-free), so a 4 s edge in an
    8 s fight beats a 12 s edge in a 32 s slugfest."""
    fight = np.maximum(np.minimum(res["ttfk_X"], res["ttfk_Y"]), 2.0)
    return res["margin"] / fight


def best_response(subsX, Y, plans, start=None, rounds=3, step=3, refine=3, verbose=False, budgets=None, w_fixed=None):
    """subsX: two Subclass objects. Y: list of two fixed Members. budgets: points per member.
    w_fixed: optional [wi_member0, wi_member1] to skip the support-weight sweep.
    Returns (members, score) with score = margin / fight length."""
    budgets = list(budgets) if budgets else [STAT_POINTS, STAT_POINTS]
    cur = list(start) if start else [default_build(s, plans, budget=b) for s, b in zip(subsX, budgets)]
    best_margin = -np.inf
    for r in range(rounds):
        improved = False
        for k in (0, 1):
            other = cur[1 - k]
            best_local = None
            for wi in ([w_fixed[k]] if w_fixed else range(len(W_GRID))):
                for grid in (alloc_grid(step, budgets[k]),):
                    cand = make_member(subsX[k], plans, grid, wi)
                    X = [cand, other] if k == 0 else [other, cand]
                    res = evaluate(X, Y)
                    sc = objective(res)
                    i = int(np.argmax(sc))
                    if best_local is None or sc[i] > best_local[0]:
                        best_local = (sc[i], grid[i], wi)
            # local refinement at step 1 around the best coarse point
            m0, pt, wi = best_local
            grid = alloc_grid(1, budgets[k], center=pt, radius=refine)
            cand = make_member(subsX[k], plans, grid, wi)
            X = [cand, other] if k == 0 else [other, cand]
            res = evaluate(X, Y)
            sc = objective(res)
            i = int(np.argmax(sc))
            if sc[i] > best_margin + 1e-9:
                best_margin = float(sc[i]); improved = True
                cur[k] = make_member(subsX[k], plans, [tuple(grid[i])], wi)
        if verbose:
            print(f"    round {r}: score={best_margin:.3f} " + " | ".join(describe(m) for m in cur))
        if not improved:
            break
    return cur, best_margin


def describe(m: Member):
    a = m.alloc
    main = main_stat(m.sub)
    return f"{m.sub.id}[hp{int(a['hp'][0])} mp{int(a['mp'][0])} {main}{int(a[main][0])} def{int(a['def'][0])} w{W_GRID[int(np.ravel(m.wi)[0])]}]"
