"""Matchup evaluator: given two teams of two characters with allocations (vectorized
along a candidate axis) and their rotation plans, compute each side's time to first
kill under focus fire, using the combat.json damage pipeline.
"""
from __future__ import annotations

import numpy as np

from kdata import GCD, HIT_CHANCE
from plans import BIDX, BUFFS, DIDX, SCALING, SIDX, T_GRID, W_GRID


def stack_plans(plans):
    """Convert build_tables output plans[sid][(ti, wi)] into plans[sid][ti][k] arrays of shape (nW, nMP, ...)."""
    out = {}
    for sid, tab in plans.items():
        out[sid] = {}
        for ti in range(len(T_GRID)):
            keys = tab[(ti, 0)].keys()
            out[sid][ti] = {k: np.stack([tab[(ti, wi)][k] for wi in range(len(W_GRID))]) for k in keys}
    return out

PHYS, MAG = 0, 1
SELF, ALLY, ALLIES = 0, 1, 2
EPS = 1e-9


def mitig(x):
    return 100.0 / (100.0 + np.maximum(x, 0.0))


class Member:
    """A character whose allocation may be a vector of candidates (arrays of shape (N,))."""

    def __init__(self, sub, alloc, plans_sub, wi):
        """plans_sub: stacked tables, plans_sub[ti][component] has shape (nW, nMP, ...).
        wi: support-weight index, scalar or array aligned with the allocation vectors."""
        self.sub = sub
        self.alloc = {k: np.asarray(v, dtype=float) for k, v in alloc.items()}
        self.st = sub.stats(self.alloc)
        self.mp_idx = np.asarray(alloc["mp"], dtype=int)
        self.plans_sub = plans_sub
        self.wi = np.asarray(wi, dtype=int)
        self.innate = sub.innate

    def plan(self, ti):
        P = self.plans_sub[ti]
        wi = np.broadcast_to(self.wi, self.mp_idx.shape)
        return {k: v[wi, self.mp_idx] for k, v in P.items()}

    def stat_matrix(self, extra=None):
        """(N, len(SCALING)) matrix of the scaling stats."""
        cols = [np.asarray(self.st[s]) for s in SCALING]
        return np.stack(np.broadcast_arrays(*cols), axis=-1)


def _bcast(*arrs):
    return np.broadcast_arrays(*[np.asarray(a, dtype=float) for a in arrs])


def side_context(members, T, ti):
    """Per-member plans and received buffs for one side."""
    plans = [m.plan(ti) for m in members]
    ctx = []
    for k, m in enumerate(members):
        partner = 1 - k
        buff = plans[k]["self_buff"] + plans[partner]["ally_buff"]
        ctx.append({"m": m, "plan": plans[k], "buff": buff})
    # team-wide control totals (seconds) and offensive debuffs applied to the enemy focus target
    tot = {key: sum(p[key] for p in plans) for key in ("cc", "blind", "taunt", "confusion", "disarm", "slow", "redirect")}
    tot["debuff"] = sum(p["debuff"] for p in plans)
    return ctx, tot


def support_on(target_idx, ctx, T, heal_red):
    """Heals + shields landing on member target_idx of a side over T (absorb-equivalent HP)."""
    tm = ctx[target_idx]["m"]
    hp_t = tm.st["hp"]
    total = 0.0
    for k, c in enumerate(ctx):
        m, p = c["m"], c["plan"]
        S = m.stat_matrix()                     # (N, 7)
        if k == target_idx:
            tsel = [SELF, ALLY, ALLIES]         # own self/ally/allies heals all reach me if I'm focused
        else:
            tsel = [ALLY, ALLIES]
        heal = 0.0; shield = 0.0
        for t in tsel:
            heal = heal + p["heal_flat"][..., t] + np.einsum("...s,...s->...", p["heal_coef"][..., t, :], S) \
                   + p["hot_pct"][..., t] / 100.0 * hp_t
            shield = shield + p["shield_flat"][..., t] + np.einsum("...s,...s->...", p["shield_coef"][..., t, :], S)
        # heals are reactive: nothing lands during the first GCD of the fight
        heal = heal * (1 + m.st["heal_pct"] / 100.0) * (1 + tm.st["healing_received"] / 100.0) * (1 - heal_red / 100.0) \
               * max(0.0, T - GCD) / T
        shield = shield * (1 + m.st["shield_pct"] / 100.0)
        total = total + heal + shield
    return total


def damage_on(att_ctx, att_tot, tgt_ctx, tgt_tot, target_idx, T, carry_idx):
    """Damage from every attacker of one side onto member target_idx of the other side over T.
    Returns (damage_on_target, lifesteal_gains_per_attacker)."""
    tc = tgt_ctx[target_idx]
    tm, tbuff = tc["m"], tc["buff"]
    deb = att_tot["debuff"]                     # offensive debuffs from the attacking side on the target
    # target defensive numbers
    armor_t = tm.st["armor"] * (1 + (tbuff[..., BIDX["armor_up"]] - deb[..., DIDX["armor_down"]]) / 100.0)
    mr_t = tm.st["magic_resist"] * (1 + (tbuff[..., BIDX["magic_resist_up"]] - deb[..., DIDX["magic_resist_down"]]) / 100.0)
    def_t = tm.st["def"] + tbuff[..., BIDX["def_up"]] - tbuff[..., BIDX["def_down"]] - deb[..., DIDX["def_down"]]
    dr_t = np.minimum(75.0, tm.st["damage_reduction"] + tbuff[..., BIDX["damage_reduction_up"]] - deb[..., DIDX["damage_reduction_down"]])
    taken_t = 1 + deb[..., DIDX["dmg_taken"]] / 100.0
    evade_t = tbuff[..., BIDX["evasion_up"]] / 100.0
    total = 0.0
    gains = []
    for k, c in enumerate(att_ctx):
        m, p, buff = c["m"], c["plan"], c["buff"]
        S = m.stat_matrix()
        # debuffs the target side applies to this attacker (defensive debuffs land on the enemy carry)
        d_on_me = tgt_tot["debuff"] if k == carry_idx else 0.0 * tgt_tot["debuff"]
        atk_mult = 1 + (buff[..., BIDX["atk_up"]] - buff[..., BIDX["atk_down"]] - d_on_me[..., DIDX["atk_down"]]) / 100.0
        mag_mult = 1 + (buff[..., BIDX["mag_up"]] - buff[..., BIDX["mag_down"]] - d_on_me[..., DIDX["mag_down"]]) / 100.0
        shp = np.broadcast_shapes(S.shape[:-1], np.shape(atk_mult), np.shape(mag_mult))
        Se = np.broadcast_to(S, shp + (S.shape[-1],)).copy()
        Se[..., SIDX["atk"]] = Se[..., SIDX["atk"]] * np.broadcast_to(atk_mult, shp)
        Se[..., SIDX["mag"]] = Se[..., SIDX["mag"]] * np.broadcast_to(mag_mult, shp)
        amp = 1 + (m.st["damage_percent"] + buff[..., BIDX["damage_percent_up"]] - buff[..., BIDX["damage_percent_down"]]
                   - d_on_me[..., DIDX["damage_percent_down"]]) / 100.0
        crit = np.minimum(100.0, m.st["crit"] + buff[..., BIDX["crit_chance_up"]] - d_on_me[..., DIDX["crit_chance_down"]])
        cdmg = m.st["crit_dmg"] + buff[..., BIDX["crit_damage_up"]] - d_on_me[..., DIDX["crit_damage_down"]]
        ecrit = 1 + crit / 100.0 * (cdmg - 100.0) / 100.0
        # control applied on this attacker by the target side (lands on the carry)
        if k == carry_idx:
            act = np.clip(1 - tgt_tot["cc"] / T - tgt_tot["slow"] / (T * (GCD + 0.3)) - tgt_tot["disarm"] / T * 0.5, 0.1, 1.0)
            hit = HIT_CHANCE * (1 - np.minimum(1.0, tgt_tot["blind"] / T) * (1 - 0.25 / HIT_CHANCE))
        else:
            act, hit = 1.0, HIT_CHANCE
        hit = hit * (1 - evade_t)
        taken = taken_t * (1 + m.innate.get("target_dmg_taken_pct", 0) / 100.0)
        direct = np.einsum("...ds,...s->...d", p["dmg"], Se) * (amp * ecrit * hit * act)[..., None]
        dots = np.einsum("...ds,...s->...d", p["dot"], Se) * (amp * hit * act)[..., None]
        hits = p["hits"] * (hit * act)[..., None]
        pen = np.where(p["dmg"].sum(-1) > 0, p["pen_num"] / np.maximum(p["dmg"].sum(-1), EPS), 0.0)
        apen = np.minimum(70.0, m.st["armor_pen"] + pen[..., PHYS])
        mpen = np.minimum(70.0, m.st["magic_pen"] + pen[..., MAG])
        flat = 0.5 * def_t * hits[..., PHYS]
        phys = np.maximum(0.1 * direct[..., PHYS], direct[..., PHYS] - flat) * mitig(armor_t * (1 - apen / 100.0)) \
               + dots[..., PHYS] * mitig(armor_t) + p["poison_pct"] * tm.st["hp"] * mitig(armor_t) * hit * act
        magd = direct[..., MAG] * mitig(mr_t * (1 - mpen / 100.0)) + dots[..., MAG] * mitig(mr_t)
        dmg = (phys + magd) * (1 - dr_t / 100.0) * taken
        ls = (m.st["lifesteal"] + buff[..., BIDX["lifesteal"]]) / 100.0
        ls_skill = np.einsum("...s,...s->...", p["ls_skill"][..., PHYS, :], Se) * amp * ecrit * hit * act * mitig(armor_t) * (1 - dr_t / 100.0)
        gains.append(phys * (1 - dr_t / 100.0) * ls + ls_skill + magd * (1 - dr_t / 100.0) * m.st["spell_vamp"] / 100.0)
        total = total + dmg
    return total, gains


def evaluate_bucket(X, Y, ti, redirect_cap=0.85, details=None):
    """TTFK for side X killing Y and for Y killing X at horizon bucket ti. Returns (ttfk_X, ttfk_Y).
    If `details` is a list, per-target dicts are appended (one per attacking side)."""
    T = T_GRID[ti]
    cx, tx = side_context(X, T, ti)
    cy, ty = side_context(Y, T, ti)
    out = []
    for att_ctx, att_tot, tgt_ctx, tgt_tot in ((cx, tx, cy, ty), (cy, ty, cx, tx)):
        # carry = the attacker with the larger raw damage coefficient sum (enemy CC/debuffs land on it)
        raw = [np.einsum("...ds,...s->...", c["plan"]["dmg"] + c["plan"]["dot"], c["m"].stat_matrix()) for c in att_ctx]
        raw0, raw1 = _bcast(raw[0], raw[1])
        carry_mask = raw1 > raw0                                      # True -> member 1 is the carry
        best = None
        for t in (0, 1):
            d0, g0 = damage_on(att_ctx, att_tot, tgt_ctx, tgt_tot, t, T, carry_idx=0)
            d1, g1 = damage_on(att_ctx, att_tot, tgt_ctx, tgt_tot, t, T, carry_idx=1)
            dmg = np.where(carry_mask, d1, d0)
            # protection of the focus target by its partner: taunt / confusion / damage transfer
            protector = 1 - t
            prot = tgt_ctx[protector]["plan"]
            u = np.minimum(1.0, prot["taunt"] / T) + 0.5 * np.minimum(1.0, prot["confusion"] / T) + prot["redirect"]
            u = np.minimum(redirect_cap, u)
            dmg = dmg * (1 - u)
            heal_red = att_tot["debuff"][..., DIDX["heal_reduction"]]
            ehp = tgt_ctx[t]["m"].st["hp"] + support_on(t, tgt_ctx, T, heal_red)
            ttfk = T * ehp / np.maximum(dmg, EPS)
            if details is not None:
                det = details[-1] if (details and details[-1].get("_side") is att_ctx) else None
                if det is None:
                    det = {"_side": att_ctx, "T": T, "ttfk": [], "dmg": [], "ehp": [], "protect": []}
                    details.append(det)
                det["ttfk"].append(ttfk); det["dmg"].append(dmg); det["ehp"].append(ehp); det["protect"].append(u)
            best = ttfk if best is None else np.minimum(best, ttfk)
        out.append(best)
    return out[0], out[1]


def evaluate(X, Y):
    """Fixed-point on the horizon: pick the bucket whose T is closest to the fight length it implies.
    Returns dict with margin (ttfk_Y - ttfk_X, >0 means X wins), ttfk_X, ttfk_Y, ti."""
    tx_all, ty_all = [], []
    for ti in range(len(T_GRID)):
        a, b = evaluate_bucket(X, Y, ti)
        a, b = _bcast(a, b)
        tx_all.append(a); ty_all.append(b)
    tx_all = np.stack(tx_all); ty_all = np.stack(ty_all)          # (nT, N)
    fight = np.minimum(tx_all, ty_all)
    Ts = np.array(T_GRID)[:, None]
    gap = np.abs(np.log(np.maximum(fight, 1.0)) - np.log(Ts))
    ti = np.argmin(gap, axis=0)
    idx = (ti, np.arange(tx_all.shape[1]))
    tX, tY = tx_all[idx], ty_all[idx]
    # volley discretization: instant skills land at t = 0, 2, 4, ... so a kill happens at the volley
    # that completes the damage. Continuous TTFK <= 2 s means the first volley kills (t = 0).
    kX = GCD * np.ceil(tX / GCD) - GCD
    kY = GCD * np.ceil(tY / GCD) - GCD
    return {"margin": tY - tX, "margin_d": kY - kX, "ttfk_X": tX, "ttfk_Y": tY, "kill_X": kX, "kill_Y": kY, "ti": ti}


def explain(X, Y):
    """Single-build diagnostics at the fixed-point horizon: per side, kill time per enemy target,
    damage and effective HP over the horizon, and the focus target."""
    r = evaluate(X, Y)
    ti = int(np.ravel(r["ti"])[0])
    det = []
    evaluate_bucket(X, Y, ti, details=det)
    out = {"ti": ti, "T": T_GRID[ti], "margin": float(np.ravel(r["margin"])[0]),
           "ttfk_X": float(np.ravel(r["ttfk_X"])[0]), "ttfk_Y": float(np.ravel(r["ttfk_Y"])[0]), "sides": []}
    for d in det:
        tt = [float(np.ravel(v)[0]) for v in d["ttfk"]]
        out["sides"].append({"ttfk_per_target": tt, "focus": int(np.argmin(tt)),
                             "dmg_per_target": [float(np.ravel(v)[0]) for v in d["dmg"]],
                             "ehp_per_target": [float(np.ravel(v)[0]) for v in d["ehp"]],
                             "protect_per_target": [float(np.ravel(v)[0]) for v in d["protect"]]})
    return out
