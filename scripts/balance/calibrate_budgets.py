"""Per-subclass point budgets: iterate full tournament runs, nudging each subclass's
stat-point budget against its mean equilibrium win probability until the spread
between the strongest and weakest subclass falls under a target.

    python3 calibrate_budgets.py --rounds 6 --target 0.10

Level 20 gives 57 points, so budgets never exceed 57: the weakest subclass keeps 57 and the
strong ones lose points. Each round writes out/calib/round_<k>/ and out/budgets.csv (latest).
"""
from __future__ import annotations

import argparse
import csv
import os
import time

import numpy as np

from kdata import STAT_POINTS, load_subclasses
from run_tournament import OUT, run_pipeline

MIN_B, MAX_B = 10, STAT_POINTS      # level 20 gives 57 points: budgets can only be reduced


def write_budgets(path, budgets, scores=None):
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["subclass", "budget", "mean_win_prob"])
        for s in sorted(budgets):
            w.writerow([s, budgets[s], f"{scores[s]:.3f}" if scores and s in scores else ""])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--target", type=float, default=0.10, help="stop when max-min subclass mean win prob <= target")
    ap.add_argument("--gain", type=float, default=60.0, help="points moved per 1.0 of win-prob deviation, round 1")
    ap.add_argument("--damping", type=float, default=0.75)
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() - 1))
    ap.add_argument("--start", default="", help="budgets CSV to start from")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    ids = sorted(load_subclasses())
    budgets = {s: STAT_POINTS for s in ids}
    if args.start:
        with open(args.start, newline="") as f:
            for row in csv.DictReader(f):
                budgets[row["subclass"]] = int(row["budget"])
    calib = os.path.join(OUT, "calib"); os.makedirs(calib, exist_ok=True)
    history = []
    gain = args.gain
    for k in range(args.rounds + 1):
        t0 = time.time()
        out_dir = os.path.join(calib, f"round_{k}")
        comps, comp_score, sub_score = run_pipeline(budgets, out_dir=out_dir, workers=args.workers, limit=args.limit, quiet=True)
        vals = np.array([sub_score[s] for s in ids])
        spread = float(vals.max() - vals.min())
        history.append((k, spread, dict(budgets), dict(sub_score)))
        write_budgets(os.path.join(OUT, "budgets.csv"), budgets, sub_score)
        write_budgets(os.path.join(out_dir, "budgets.csv"), budgets, sub_score)
        order = sorted(ids, key=lambda s: -sub_score[s])
        print(f"round {k}: spread {spread:.3f} (min {vals.min():.3f} max {vals.max():.3f}, sd {vals.std():.3f}) in {time.time() - t0:.0f}s", flush=True)
        print("   top: " + ", ".join(f"{s} {sub_score[s]:.2f}@{budgets[s]}" for s in order[:4]) +
              " | bottom: " + ", ".join(f"{s} {sub_score[s]:.2f}@{budgets[s]}" for s in order[-4:]), flush=True)
        if spread <= args.target or k == args.rounds:
            break
        # nudge budgets against the deviation from 0.5, then shift so the weakest subclass keeps
        # the full 57 points and the strong ones give points up
        new = {s: budgets[s] - gain * (sub_score[s] - 0.5) for s in ids}
        shift = MAX_B - max(new.values())
        budgets = {s: int(round(min(MAX_B, max(MIN_B, new[s] + shift)))) for s in ids}
        gain *= args.damping
    with open(os.path.join(OUT, "calibration_history.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["round", "spread"] + [f"budget_{s}" for s in ids] + [f"p_{s}" for s in ids])
        for k, spread, b, sc in history:
            w.writerow([k, f"{spread:.3f}"] + [b[s] for s in ids] + [f"{sc[s]:.3f}" for s in ids])
    print("final budgets in out/budgets.csv; history in out/calibration_history.csv")


if __name__ == "__main__":
    main()
