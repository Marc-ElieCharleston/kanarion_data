"""Export the level-20 stats and rotation tables to one binary file for the C++ tool (cpp/kbal).

Layout: a text header (lines) ending with a line "BIN", then little-endian float64 arrays:
  stats [nSub][nStat], plans [nSub][nT][nW][nMP][NCOMP], casts [nSub][nT][nW][nMP][nSkillMax]
"""
from __future__ import annotations

import os
import pickle

import numpy as np

from evalmodel import stack_plans
from kdata import load_subclasses
from plans import BUFFS, DEBUFFS, SCALING, T_GRID, W_GRID, MP_LEVELS, main_stat

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
STAT_KEYS = ["hp", "mp", "atk", "mag", "def", "armor", "magic_resist", "crit", "crit_dmg", "armor_pen", "magic_pen",
             "damage_percent", "damage_reduction", "lifesteal", "spell_vamp", "healing_received", "tenacity"]
PCT_KEYS = ["atk", "mag", "hp", "mp", "armor", "magic_resist", "def", "heal_power", "shield_power"]
INNATE_KEYS = ["atk_pct", "mag_pct", "target_dmg_taken_pct", "dmg_pct", "armor_pen", "heal_pct", "shield_pct"]
COMP_ORDER = ["dmg", "hits", "pen_num", "dot", "poison_pct", "heal_flat", "heal_coef", "hot_pct", "shield_flat", "shield_coef",
              "self_buff", "ally_buff", "debuff", "cc", "blind", "taunt", "confusion", "disarm", "slow", "redirect",
              "ls_skill", "mp_used", "time_used"]


def main(path=os.path.join(OUT, "tables.bin")):
    subs = load_subclasses()
    with open(os.path.join(OUT, "plans.pkl"), "rb") as f:
        plans = stack_plans(pickle.load(f))
    ids = sorted(subs)
    nS = len(SCALING); nT, nW, nMP = len(T_GRID), len(W_GRID), MP_LEVELS
    n_skill = max(len(subs[s].skills) for s in ids)
    stats = np.zeros((len(ids), len(STAT_KEYS) + len(PCT_KEYS) + len(INNATE_KEYS)))
    for i, sid in enumerate(ids):
        sub = subs[sid]
        stats[i, :len(STAT_KEYS)] = [sub.base.get(k, 0.0) for k in STAT_KEYS]
        stats[i, len(STAT_KEYS):len(STAT_KEYS) + len(PCT_KEYS)] = [sub.pct.get(k, 0.0) for k in PCT_KEYS]
        stats[i, len(STAT_KEYS) + len(PCT_KEYS):] = [sub.innate.get(k, 0.0) for k in INNATE_KEYS]
    ncomp = None
    P = None; C = np.zeros((len(ids), nT, nW, nMP, n_skill))
    for i, sid in enumerate(ids):
        for ti in range(nT):
            comps = plans[sid][ti]
            parts = [comps[k].reshape(nW, nMP, -1) for k in COMP_ORDER]
            block = np.concatenate(parts, axis=-1)
            if ncomp is None:
                ncomp = block.shape[-1]; P = np.zeros((len(ids), nT, nW, nMP, ncomp))
            P[i, ti] = block
            C[i, ti, :, :, :comps["casts"].shape[-1]] = comps["casts"]
    with open(path, "wb") as f:
        f.write(b"KBAL1\n")
        f.write(f"{len(ids)} {nT} {nW} {nMP} {len(BUFFS)} {len(DEBUFFS)} {nS} {n_skill} {stats.shape[1]} {ncomp}\n".encode())
        f.write((" ".join(f"{t}" for t in T_GRID) + "\n").encode())
        f.write((" ".join(f"{w}" for w in W_GRID) + "\n").encode())
        for sid in ids:
            sub = subs[sid]
            f.write(f"{sid} {sub.base_class} {0 if main_stat(sub) == 'atk' else 1} {len(sub.skills)} ".encode()
                    + ",".join(s.name.replace(",", " ").replace(" ", "_") for s in sub.skills).encode() + b"\n")
        f.write(b"BIN\n")
        f.write(stats.astype("<f8").tobytes()); f.write(P.astype("<f8").tobytes()); f.write(C.astype("<f8").tobytes())
    print(f"wrote {path}: {len(ids)} subclasses, plans {P.shape}, {os.path.getsize(path) / 1e6:.1f} MB, ncomp={ncomp}")
    # sanity: component offsets for the C++ side
    off = 0
    for k in COMP_ORDER:
        n = plans[ids[0]][0][k].reshape(nW, nMP, -1).shape[-1]
        print(f"  {k:12s} offset {off:3d} size {n}")
        off += n


if __name__ == "__main__":
    main()
