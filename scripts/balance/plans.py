"""Rotation plans: for each subclass, Souffle level, fight horizon T and support
weight w, the integer cast counts that maximize HP-equivalent value under the
cooldown, GCD and Souffle constraints. Solved as a MILP with HiGHS
(scipy.optimize.milp). Plans are aggregated into numeric components that the
matchup evaluator prices exactly against any target.
"""
from __future__ import annotations

import math
import os
import pickle

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from kdata import GCD, HIT_CHANCE, MP_REGEN, STAT_POINTS, Subclass, load_subclasses

SCALING = ["atk", "mag", "max_hp", "def", "armor", "max_mp", "current_shield"]
SIDX = {s: i for i, s in enumerate(SCALING)}
DT = {"physical": 0, "magical": 1}
TGT = {"self": 0, "ally": 1, "allies": 2, "all": 2}
BUFFS = ["atk_up", "mag_up", "damage_percent_up", "crit_chance_up", "crit_damage_up",
         "armor_up", "magic_resist_up", "damage_reduction_up", "def_up", "evasion_up", "lifesteal", "heal_power_up",
         "atk_down", "mag_down", "def_down", "damage_percent_down"]   # last four: self-inflicted maluses
BIDX = {b: i for i, b in enumerate(BUFFS)}
DEBUFFS = ["armor_down", "magic_resist_down", "def_down", "dmg_taken", "atk_down", "mag_down",
           "damage_percent_down", "heal_reduction", "damage_reduction_down", "crit_chance_down", "crit_damage_down"]
DIDX = {d: i for i, d in enumerate(DEBUFFS)}
CAPS = {"atk_up": 25, "mag_up": 25, "damage_percent_up": 25, "crit_chance_up": 15, "crit_damage_up": 50,
        "armor_up": 25, "magic_resist_up": 25, "damage_reduction_up": 50, "def_up": 25, "evasion_up": 15,
        "lifesteal": 25, "heal_power_up": 25, "atk_down": 25, "mag_down": 25, "def_down": 25, "damage_percent_down": 25,
        "armor_down": 25, "magic_resist_down": 25, "dmg_taken": 60, "mag_down": 25,
        "damage_percent_down": 25, "heal_reduction": 45, "damage_reduction_down": 15, "crit_chance_down": 15,
        "crit_damage_down": 30}
T_GRID = [4.0, 6.0, 8.0, 10.0, 13.0, 16.0, 20.0, 26.0, 34.0, 45.0, 60.0]
W_GRID = [0.5, 1.0, 2.0]
MAX_POINTS = STAT_POINTS        # level 20: 57 points, budgets only go down from there
MP_LEVELS = MAX_POINTS + 1      # rows in the tables: points in mp 0..MAX_POINTS

# Reference opponent used only to RANK skills inside the rotation MILP.
REF = {"armor": 20.0, "mr": 26.0, "def": 15.0, "hp": 230.0, "enemy_dps": 22.0, "partner_dps": 22.0, "heal_rate": 8.0}


def mitig(x):
    return 100.0 / (100.0 + x)


def skill_value(sub: Subclass, sk, st, dps0, w, T):
    """HP-equivalent value of one cast vs the reference opponent. dps0 = own DPS estimate (pass 1)."""
    ecrit = 1 + st["crit"] / 100 * (st["crit_dmg"] - 100) / 100
    amp = (1 + st["damage_percent"] / 100) * ecrit * HIT_CHANCE
    v = 0.0
    for dtype, stat, coef, pen in sk.direct:
        s = st.get(stat, 0.0) if stat != "current_shield" else 0.15 * st["max_hp"]
        raw = coef * s * amp
        if dtype == "physical":
            p = min(70, st["armor_pen"] + pen)
            per_hit = raw / sk.hit_count
            hit = max(0.1 * per_hit, per_hit - 0.5 * REF["def"]) * sk.hit_count
            v += hit * mitig(REF["armor"] * (1 - p / 100))
        else:
            v += raw * mitig(REF["mr"] * (1 - min(70, st["magic_pen"]) / 100))
    for dtype, stat, coef, dur in sk.dots:
        s = REF["hp"] if stat == "max_hp_target" else st.get(stat, 0.0)
        v += coef * min(dur, T) * s * amp / ecrit * (mitig(REF["armor"]) if dtype == "physical" else mitig(REF["mr"]))
    # heals / shields (support currency, weight w)
    heal = sum((h["flat"] + sum(c * st.get(s, 0.0) for s, c in h["coef"].items()) + h["hot_pct"] / 100 * REF["hp"])
               * (min(h["dur"], T) if h["dur"] > 0 else 1.0) for h in sk.heals)
    heal *= (1 + st["heal_pct"] / 100)
    shield = sum(h["flat"] + sum(c * st.get(s, 0.0) for s, c in h["coef"].items()) for h in sk.shields)
    shield *= (1 + st["shield_pct"] / 100)
    v += w * (heal + shield)
    # buffs: offensive on self valued vs own DPS, on ally vs partner reference DPS; defensive vs enemy DPS
    def buff_val(book, dps_ref):
        val = 0.0
        for stat, (amt, dur0) in book.items():
            dur = min(dur0, T)
            if stat in ("atk_up", "mag_up", "damage_percent_up"):
                val += amt / 100 * dur * dps_ref
            elif stat == "crit_chance_up":
                val += amt / 100 * (st["crit_dmg"] - 100) / 100 * dur * dps_ref
            elif stat == "crit_damage_up":
                val += st["crit"] / 100 * amt / 100 * dur * dps_ref
            elif stat in ("damage_reduction_up",):
                val += w * amt / 100 * dur * REF["enemy_dps"]
            elif stat in ("armor_up", "magic_resist_up"):
                base = REF["armor"]
                val += w * (mitig(base) - mitig(base * (1 + amt / 100))) / mitig(base) * dur * REF["enemy_dps"] * 0.5
            elif stat == "def_up":
                val += w * 0.5 * amt * 0.5 * dur * 0.5     # flat per hit * ~0.5 hits/s * half physical
            elif stat == "evasion_up":
                val += w * amt / 100 * dur * REF["enemy_dps"]
            elif stat == "lifesteal":
                val += w * amt / 100 * dur * dps_ref * 0.8
            elif stat == "heal_power_up":
                val += w * amt / 100 * dur * REF["heal_rate"]
            elif stat in ("atk_down", "mag_down", "damage_percent_down"):      # self malus
                val -= amt / 100 * dur * dps_ref
            elif stat == "def_down":
                val -= w * 0.5 * amt * 0.25 * dur
        return val
    v += buff_val(sk.self_buffs, dps0)
    v += buff_val(sk.ally_buffs, REF["partner_dps"])
    team_dps = dps0 + REF["partner_dps"]
    for stat, (amt, dur0) in sk.debuffs.items():
        dur = min(dur0, T)
        if stat == "dmg_taken":
            v += amt / 100 * dur * team_dps
        elif stat in ("armor_down", "magic_resist_down"):
            base = REF["armor"]
            v += (mitig(base * (1 - amt / 100)) - mitig(base)) / mitig(base) * dur * team_dps * 0.5
        elif stat == "def_down":
            v += 0.5 * amt * 0.5 * dur * 0.5
        elif stat in ("atk_down", "mag_down", "damage_percent_down"):
            v += w * amt / 100 * dur * REF["enemy_dps"] * (0.5 if stat != "damage_percent_down" else 1.0)
        elif stat == "damage_reduction_down":
            v += amt / 100 * dur * team_dps
        elif stat == "heal_reduction":
            v += w * amt / 100 * dur * REF["heal_rate"] * 0.5
        elif stat in ("crit_chance_down", "crit_damage_down"):
            v += w * amt / 100 * 0.5 * dur * REF["enemy_dps"] * 0.1
    v += w * sk.hard_cc * REF["enemy_dps"]
    v += w * sk.blind * REF["enemy_dps"] * (1 - 0.25 / HIT_CHANCE)
    v += w * sk.taunt * REF["enemy_dps"] * 0.5
    v += w * sk.confusion * REF["enemy_dps"] * 0.5
    v += w * sk.disarm * REF["enemy_dps"] * 0.4
    v += w * sk.slow_seconds / (GCD + 0.3) * REF["enemy_dps"]
    v += w * sk.redirect_pct / 100 * sk.redirect_dur * REF["enemy_dps"] * 0.5
    # lifesteal riders on the skill's own damage
    if sk.lifesteal_on_skill and sk.direct:
        v += w * sk.lifesteal_on_skill / 100 * v * 0.5
    return v


def solve_plan(sub: Subclass, st, mp_total, T, w):
    """Integer cast counts maximizing value over horizon T. Two passes so buffs are priced vs own DPS."""
    skills = sub.skills
    n = len(skills)
    caps = np.array([1 + math.floor(T / sk.cooldown) if sk.cooldown > 0 else math.floor(T / GCD) for sk in skills], float)
    time = np.array([sk.time_cost for sk in skills])
    mana = np.array([sk.mana - sk.mana_restore / 100 * st["max_mp"] for sk in skills])
    budget = mp_total + MP_REGEN * T
    dps0 = 0.0
    x = np.zeros(n)
    for _ in range(2):
        vals = np.array([skill_value(sub, sk, st, dps0, w, T) for sk in skills])
        A = np.vstack([time, mana])
        cons = LinearConstraint(A, [0, 0], [T, budget])
        res = milp(c=-vals, constraints=cons, integrality=np.ones(n), bounds=Bounds(np.zeros(n), caps))
        if res.status != 0:
            break
        x = np.round(res.x)
        # own damage-only DPS estimate for pass 2
        dmg = 0.0
        for sk, k in zip(skills, x):
            if k <= 0:
                continue
            dmg += k * skill_value(sub, sk, st, 0.0, 0.0, T) if (sk.direct or sk.dots) else 0.0
        dps0 = dmg / T
    return x, vals


def aggregate(sub: Subclass, st, x, T):
    """Turn cast counts into pricing components. Buff/debuff entries are average amplitude over T."""
    sk = sub.skills
    c = {
        "dmg": np.zeros((2, len(SCALING))), "hits": np.zeros(2), "pen_num": np.zeros(2),
        "dot": np.zeros((2, len(SCALING))), "poison_pct": 0.0,
        "heal_flat": np.zeros(3), "heal_coef": np.zeros((3, len(SCALING))), "hot_pct": np.zeros(3),
        "shield_flat": np.zeros(3), "shield_coef": np.zeros((3, len(SCALING))),
        "self_buff": np.zeros(len(BUFFS)), "ally_buff": np.zeros(len(BUFFS)), "debuff": np.zeros(len(DEBUFFS)),
        "cc": 0.0, "blind": 0.0, "taunt": 0.0, "confusion": 0.0, "disarm": 0.0, "slow": 0.0, "redirect": 0.0,
        "ls_skill": np.zeros((2, len(SCALING))), "mp_used": 0.0, "time_used": 0.0, "casts": x.copy(),
    }
    for s, k in zip(sk, x):
        if k <= 0:
            continue
        for dtype, stat, coef, pen in s.direct:
            d = DT[dtype]
            c["dmg"][d, SIDX[stat]] += k * coef
            c["hits"][d] += k * s.hit_count
            c["pen_num"][d] += k * coef * pen
            if s.lifesteal_on_skill:
                c["ls_skill"][d, SIDX[stat]] += k * coef * s.lifesteal_on_skill / 100
        for dtype, stat, coef, dur in s.dots:
            tot = coef * min(dur, T)
            if stat == "max_hp_target":
                c["poison_pct"] += k * tot                       # fraction of target max hp
            else:
                c["dot"][DT[dtype], SIDX[stat]] += k * tot
        for h in s.heals:
            t = TGT.get(h["tgt"], 1)
            f = min(h["dur"], T) if h["dur"] > 0 else 1.0
            c["heal_flat"][t] += k * h["flat"] * f; c["hot_pct"][t] += k * h["hot_pct"] * f
            for stat, coef in h["coef"].items():
                c["heal_coef"][t, SIDX[stat]] += k * coef * f
        for h in s.shields:
            t = TGT.get(h["tgt"], 1)
            c["shield_flat"][t] += k * h["flat"]
            for stat, coef in h["coef"].items():
                c["shield_coef"][t, SIDX[stat]] += k * coef
        for book, arr in ((s.self_buffs, c["self_buff"]), (s.ally_buffs, c["ally_buff"])):
            for stat, (amt, dur) in book.items():
                if stat in BIDX:
                    arr[BIDX[stat]] += amt * min(1.0, k * dur / T)
        for stat, (amt, dur) in s.debuffs.items():
            if stat in DIDX:
                c["debuff"][DIDX[stat]] += amt * min(1.0, k * dur / T)
        c["cc"] += k * s.hard_cc; c["blind"] += k * s.blind; c["taunt"] += k * s.taunt
        c["confusion"] += k * s.confusion; c["disarm"] += k * s.disarm; c["slow"] += k * s.slow_seconds
        c["redirect"] += min(1.0, k * s.redirect_dur / T) * s.redirect_pct / 100
        c["mp_used"] += k * s.mana; c["time_used"] += k * s.time_cost
    for name, lst in (("self_buff", BUFFS), ("ally_buff", BUFFS), ("debuff", DEBUFFS)):
        for i, b in enumerate(lst):
            c[name][i] = min(c[name][i], CAPS.get(b, 1e9))
    return c


def build_tables(subs, out_path, verbose=True):
    """plans[sid][(Ti, wi)] = dict of arrays stacked over MP level (axis 0)."""
    plans = {}
    total = len(subs) * len(T_GRID) * len(W_GRID) * MP_LEVELS
    done = 0
    for sid, sub in subs.items():
        plans[sid] = {}
        # stats used to rank skills: 'typical' allocation (main offensive stat + hp), mp varies
        main = main_stat(sub)
        for ti, T in enumerate(T_GRID):
            for wi, w in enumerate(W_GRID):
                rows = []
                for mp_pts in range(MP_LEVELS):
                    rest = max(0, STAT_POINTS - mp_pts)
                    st = sub.stats({"hp": rest // 2, main: rest - rest // 2, "mp": mp_pts})
                    x, _ = solve_plan(sub, st, st["mp"], T, w)
                    rows.append(aggregate(sub, st, x, T))
                    done += 1
                plans[sid][(ti, wi)] = {k: np.stack([r[k] for r in rows]) if isinstance(rows[0][k], np.ndarray)
                                        else np.array([r[k] for r in rows]) for k in rows[0]}
            if verbose:
                print(f"  {sid:14s} T={T:5.1f} done {done}/{total}", flush=True)
    with open(out_path, "wb") as f:
        pickle.dump(plans, f)
    return plans


def main_stat(sub: Subclass):
    """Offensive stat the kit scales with the most (atk or mag)."""
    tot = {"atk": 0.0, "mag": 0.0}
    for s in sub.skills:
        for dtype, stat, coef, pen in s.direct:
            if stat in tot: tot[stat] += coef
        for dtype, stat, coef, dur in s.dots:
            if stat in tot: tot[stat] += coef * dur
        for h in s.heals:
            for stat, coef in h["coef"].items():
                if stat in tot: tot[stat] += coef
        for h in s.shields:
            for stat, coef in h["coef"].items():
                if stat in tot: tot[stat] += coef
    return "atk" if tot["atk"] >= tot["mag"] else "mag"


if __name__ == "__main__":
    import sys, time as _t
    subs = load_subclasses()
    for sid in (sys.argv[1:] or ["berserker", "lifewarden"]):
        sub = subs[sid]
        main = main_stat(sub)
        for mp_pts in (0, 20, 57):
            rest = STAT_POINTS - mp_pts
            st = sub.stats({"hp": rest // 2, main: rest - rest // 2, "mp": mp_pts})
            for T in (10.0, 20.0, 45.0):
                t0 = _t.time(); x, vals = solve_plan(sub, st, st["mp"], T, 1.0); dt = _t.time() - t0
                casts = ", ".join(f"{s.id.split('_')[-1]}x{int(k)}" for s, k in zip(sub.skills, x) if k > 0)
                agg = aggregate(sub, st, x, T)
                print(f"{sid} main={main} mp_pts={mp_pts:2d} MP={st['mp']:.0f} T={T:4.0f} ({dt*1000:.0f} ms) mp_used={agg['mp_used']:.0f}/{st['mp']+T:.0f} time={agg['time_used']:.0f}/{T:.0f} | {casts}")
                print("    values:", ", ".join(f"{s.id.split('_')[-1]}={v:.0f}" for s, v in zip(sub.skills, vals)))
