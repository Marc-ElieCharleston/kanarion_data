"""Zero-sum game over candidate builds: value and mixed strategies via LP (HiGHS)."""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog


def solve_zero_sum(P):
    """P[i, j] = probability that row player wins with row build i vs column build j.
    Returns (value, row_strategy, col_strategy). value = row's equilibrium win probability."""
    P = np.asarray(P, dtype=float)
    P = np.where(np.isfinite(P), P, 0.5).clip(0.0, 1.0)
    m, n = P.shape
    # row: maximize v s.t. sum_i x_i P[i,j] >= v for all j, sum x = 1, x >= 0
    c = np.zeros(m + 1); c[-1] = -1.0
    A_ub = np.hstack([-P.T, np.ones((n, 1))])
    b_ub = np.zeros(n)
    A_eq = np.zeros((1, m + 1)); A_eq[0, :m] = 1.0
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[1.0],
                  bounds=[(0, None)] * m + [(None, None)], method="highs")
    if res.x is None:                      # solver failure: fall back to pure maximin
        i = int(np.argmax(P.min(axis=1))); j = int(np.argmin(P.max(axis=0)))
        x = np.zeros(m); x[i] = 1.0; y = np.zeros(n); y[j] = 1.0
        return float(P[i, j]), x, y
    x = res.x[:m]; v = res.x[-1]
    # column: minimize u s.t. sum_j P[i,j] y_j <= u for all i
    c2 = np.zeros(n + 1); c2[-1] = 1.0
    A_ub2 = np.hstack([P, -np.ones((m, 1))])
    A_eq2 = np.zeros((1, n + 1)); A_eq2[0, :n] = 1.0
    res2 = linprog(c2, A_ub=A_ub2, b_ub=np.zeros(m), A_eq=A_eq2, b_eq=[1.0],
                   bounds=[(0, None)] * n + [(None, None)], method="highs")
    y = res2.x[:n] if res2.x is not None else np.full(n, 1.0 / n)
    return float(v), x, y


def win_prob(margin, tau=2.0):
    """Map a TTFK margin in seconds to a win probability; tau = one GCD."""
    z = np.clip(np.asarray(margin, dtype=float) / tau, -60, 60)
    return 1.0 / (1.0 + np.exp(-z))
