"""Level-20 tournament data model for KanarionDB.

Loads the 24 subclasses with their level-20 base stats, the 10 skills each has
at skill level 1 (5 base + 5 subclass), and every passive at level 1, and turns
each skill into numeric "per-cast components" that the optimizer and the
matchup evaluator consume.

Rules encoded here (sources in comments):
  stats  = base + floor(growth * 19) + points * point_value   (progression.json v4.0)
  point_value: hp 5, mp 5, atk 1, mag 1, def -> +1 armor only  (progression.json v4.0)
  magic_resist = (base + growth) + 0.2 * MAG                  (progression.json v4.0)
  damage = scaling_percent% * scaling_stat                   (skill_system.json v3.0)
  status effects: Option A, value = stacks * value_per_stack (stats/status_effects.json)
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEVEL = 20
POINT_VALUE = {"hp": 5, "mp": 5, "atk": 1, "mag": 1, "def": 1}
STAT_POINTS = 3 * (LEVEL - 1)          # 57, no starting stat points
GCD = 2.0
MP_REGEN = 1.0                          # identical for all six classes
HIT_CHANCE = 0.95                       # hit 100 vs flee 10 -> 170 -> capped 95
BASE_CLASSES = ["warrior", "mage", "healer", "archer", "rogue", "artisan"]

# Free innate proc passives (classes/<class>/passives.json innate_passive) modeled
# as steady-state multipliers in a normal rotation. See README for reasoning.
INNATE = {
    "warrior": {"atk_pct": 15.0},              # +5% ATK/offensive cast, 3 stacks, 10 s
    "archer":  {"target_dmg_taken_pct": 10.0}, # +5% taken per 2 casts, ~2 stacks sustained
    "rogue":   {"dmg_pct": 12.0, "armor_pen": 8.0},  # predation 3%/2pen per stack, avg
    "mage":    {"mag_pct": 8.0},               # arcane charges +4% MAG each, ~2 held
    "healer":  {"heal_pct": 5.0},              # guardian breath, ~+5% healing output
    "artisan": {"heal_pct": 6.0, "shield_pct": 6.0},  # savoir-faire, ~3 stacks
}

# Option A canonical grid (stats/status_effects.json _meta.canonical_grid)
GRID = {
    "atk_up": (5, 5), "atk_down": (5, 5), "mag_up": (5, 5), "mag_down": (5, 5),
    "damage_percent_up": (5, 5), "damage_percent_down": (5, 5),
    "crit_chance_up": (5, 3), "crit_chance_down": (5, 3),
    "crit_damage_up": (10, 3), "crit_damage_down": (10, 3),
    "accuracy_up": (5, 5), "accuracy_down": (5, 5),
    "armor_up": (5, 5), "armor_down": (5, 5), "magic_resist_up": (5, 5), "magic_resist_down": (5, 5),
    "damage_reduction_up": (5, 3), "damage_reduction_down": (5, 3),
    "evasion_up": (3, 5), "evasion_down": (3, 5), "def_up": (5, 5), "def_down": (5, 5),
    "cast_speed_up": (5, 5), "cast_speed_down": (5, 5), "slow": (0.3, 3),
    "heal_power_up": (5, 5), "heal_power_down": (5, 5), "heal_reduction": (15, 3),
    "crit_resistance_down": (5, 3), "heal_over_time": (1, 3), "mana_regen": (2, 10),
    "vulnerable": (5, 5), "exposed": (10, 3), "marked": (10, 1), "berserk": (10, 5), "lifesteal": (5, 5),
}
# DoTs: (scaling stat, coefficient per tick per stack, max stacks, damage type)
DOTS = {
    "bleed": ("atk", 0.30, 3, "physical"), "burn": ("mag", 0.25, 3, "magical"),
    "chill": ("mag", 0.10, 3, "magical"), "corruption": ("mag", 0.15, 5, "magical"),
    "toxin": ("mag", 0.10, 5, "magical"), "poison": ("max_hp_target", 0.02, 5, "physical"),
    "curse_dot": ("mag", 0.20 * 1.5, 1, "magical"),   # 0.2/tick + 50% explosion at end
}
HARD_CC = {"stun": 3.0, "freeze": 3.0, "fear": 3.0, "silence": 5.0}   # caps from status_effects
DMG_TAKEN = {"vulnerable": (5, 5), "exposed": (10, 3), "marked": (10, 1), "hunter_mark": (15, 1)}
UNPRICED = {"cleanse", "purge", "steal_buff", "interrupt", "revealed", "cc_immune", "cc_immune_zone",
            "invisible", "cover", "riposte_active", "en_garde_stance", "enchanted_blade", "mana_steal",
            "mana_lock", "mana_drain", "root", "taunt_redirect", "challenged", "double_attack_chance",
            "invulnerable", "amplify", "cast_speed_up", "cast_speed_down", "accuracy_up", "accuracy_down",
            "crit_resistance_down", "evasion_down", "heal_block", "mana_regen", "resurrect"}


def load_json(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


@dataclass
class Skill:
    id: str
    name: str
    source: str                 # BASE / SUBCLASS
    mana: float
    cooldown: float
    cast_time: float
    target: str                 # enemy / enemies / self / ally / allies / all / self_and_enemies
    aoe: bool
    # direct damage: list of (damage_type, scaling_stat, coef_per_cast, armor_pen)
    direct: list = field(default_factory=list)
    # dots: list of (damage_type, scaling_stat, coef_per_second, duration)
    dots: list = field(default_factory=list)
    # heals: list of dict(tgt, flat, coef{stat: c}, hot_pct, dur). dur=0: instant totals; dur>0: per-second rates
    heals: list = field(default_factory=list)
    # shields: list of dict(tgt, flat, coef{stat: c})
    shields: list = field(default_factory=list)
    self_buffs: dict = field(default_factory=dict)    # stat -> (amount, duration)
    ally_buffs: dict = field(default_factory=dict)
    debuffs: dict = field(default_factory=dict)       # stat -> (amount, duration)
    hard_cc: float = 0.0                              # seconds of blocked actions per cast
    blind: float = 0.0                                # seconds of 25% hit rate
    taunt: float = 0.0                                # seconds of forced target on caster
    confusion: float = 0.0                            # seconds of random targeting
    disarm: float = 0.0
    slow_seconds: float = 0.0                         # stacks*0.3 * duration (GCD-seconds added)
    mana_restore: float = 0.0                         # % of caster max MP restored per cast
    lifesteal_on_skill: float = 0.0                   # % of this skill's damage returned
    redirect_pct: float = 0.0                         # damage_transfer: % of ally damage taken by caster
    redirect_dur: float = 0.0
    unpriced: list = field(default_factory=list)
    execute_factor: float = 1.0
    hit_count: int = 1

    @property
    def time_cost(self):
        return max(GCD, self.cast_time)

    def add_heal(self, tgt, flat=0.0, stat=None, coef=0.0, hot_pct=0.0, dur=0.0):
        self.heals.append({"tgt": tgt, "flat": flat, "coef": ({stat: coef} if stat else {}), "hot_pct": hot_pct, "dur": dur})

    def add_shield(self, tgt, flat=0.0, stat=None, coef=0.0):
        self.shields.append({"tgt": tgt, "flat": flat, "coef": ({stat: coef} if stat else {})})

    @property
    def has_support(self):
        return bool(self.heals or self.shields)


@dataclass
class Subclass:
    id: str
    base_class: str
    base: dict           # level-20 stats before allocation (flat, incl. passive flats)
    pct: dict            # passive percent bonuses per stat
    skills: list
    innate: dict
    unpriced: list

    def stats(self, x):
        """Derived stats for allocation x = dict(hp, mp, atk, mag, def) of points."""
        b, p = self.base, self.pct
        m = lambda s: 1 + p.get(s, 0) / 100.0
        atk = (b["atk"] + x.get("atk", 0)) * m("atk") * (1 + self.innate.get("atk_pct", 0) / 100)
        mag = (b["mag"] + x.get("mag", 0)) * m("mag") * (1 + self.innate.get("mag_pct", 0) / 100)
        hp = (b["hp"] + 5 * x.get("hp", 0)) * m("hp")
        mp = (b["mp"] + 5 * x.get("mp", 0)) * m("mp")
        armor = (b["armor"] + x.get("def", 0)) * m("armor")
        mr = b["magic_resist"] * m("magic_resist") + 0.2 * mag
        return {
            "hp": hp, "mp": mp, "atk": atk, "mag": mag, "def": b["def"] * m("def"), "current_shield": 0.15 * hp,
            "armor": armor, "magic_resist": mr, "max_hp": hp, "max_mp": mp,
            "crit": b["crit"], "crit_dmg": b["crit_dmg"],
            "armor_pen": b["armor_pen"] + self.innate.get("armor_pen", 0), "magic_pen": b["magic_pen"],
            "damage_percent": b["damage_percent"] + self.innate.get("dmg_pct", 0),
            "damage_reduction": b["damage_reduction"], "lifesteal": b["lifesteal"], "spell_vamp": b["spell_vamp"],
            "heal_power": b["heal_power"], "heal_pct": p.get("heal_power", 0) + self.innate.get("heal_pct", 0),
            "shield_power": b["shield_power"], "shield_pct": p.get("shield_power", 0) + self.innate.get("shield_pct", 0),
            "healing_received": b["healing_received"], "tenacity": b["tenacity"],
            "mp_regen": b["mp_regen"], "buff_duration": b["buff_duration"], "debuff_duration": b["debuff_duration"],
        }


def _level20_base(base_class, cbs, cg):
    b = dict(cbs[base_class]); g = cg.get(base_class, {})
    out = {}
    for k, v in b.items():
        if isinstance(v, (int, float)):
            out[k] = v + math.floor(g.get(k, 0) * (LEVEL - 1))
    return out


PERCENT_STATS = {"crit", "crit_dmg", "damage_reduction", "armor_pen", "magic_pen", "hit", "lifesteal",
                 "spell_vamp", "healing_received", "tenacity", "effect_chance", "effect_resist",
                 "debuff_duration", "buff_duration", "damage_percent", "block_chance", "parry_chance",
                 "heal_power", "shield_power", "cast_speed", "cooldown_reduction", "thorns"}


def _apply_passives(base, pct, passives, level=1):
    for p in passives:
        for e in p.get("effects", []):
            stat, op, v = e.get("stat"), e.get("op"), e.get("value_per_level", 0) * level
            if stat is None:
                continue
            if op == "add_flat" or stat in PERCENT_STATS:
                base[stat] = base.get(stat, 0) + v
            elif op == "add_percent":
                pct[stat] = pct.get(stat, 0) + v


def _parse_skill(s, base_class, subclass, unpriced_log):
    sk = Skill(id=s["id"], name=s.get("name_en", s["id"]), source=s.get("source_scope", "?"),
               mana=float(s.get("mana_cost", 0)), cooldown=float(s.get("cooldown", 0)),
               cast_time=float(s.get("cast_time", 0) or 0), target=s.get("target", "enemy"),
               aoe=s.get("pattern", "single") != "single")
    dtype = s.get("damage_type", "none")
    if dtype == "magic":
        dtype = "magical"
    hits = int(s.get("hit_count", 1) or 1)
    sk.hit_count = hits
    if s.get("execute_threshold") and s.get("execute_bonus_percent"):
        sk.execute_factor = 1 + s["execute_bonus_percent"] / 100 * s["execute_threshold"] / 100
    if dtype in ("physical", "magical") and s.get("scaling_stat") and s.get("scaling_percent"):
        sk.direct.append((dtype, s["scaling_stat"], s["scaling_percent"] / 100 * hits * sk.execute_factor,
                          float(s.get("armor_pen", 0))))
    def norm_tgt(t):
        return t if t in ("self", "ally", "allies", "all") else "ally"
    stgt = norm_tgt(s.get("target", "ally"))
    if s.get("heal_scaling_percent") or s.get("base_heal"):
        sk.add_heal(stgt, flat=float(s.get("base_heal", 0) or 0), stat=s.get("heal_scaling_stat", "mag"),
                    coef=float(s.get("heal_scaling_percent", 0) or 0) / 100)
    if s.get("dot_type") == "hp_dot":
        unpriced_log.append((s["id"], "hp_dot"))
    if s.get("sacrifice_hp_percent"):
        unpriced_log.append((s["id"], f"sacrifice_hp {s['sacrifice_hp_percent']}%"))
    for e in s.get("effects", []):
        et, stat = e.get("type"), e.get("stat")
        dur = float(e.get("duration", 0) or 0)
        stacks = int(e.get("stacks_to_apply", 1) or 1)
        etgt = e.get("target") or e.get("applies_to")
        tgt = norm_tgt(etgt) if etgt else stgt
        if stat in DOTS:
            sstat, coef, mx, dt = DOTS[stat]
            st = min(stacks, mx)
            d = dur if dur > 0 else 4.0
            sk.dots.append((dt, sstat, coef * st, d))
        elif stat == "holy_dot":
            d = float(dur or 6)
            sk.dots.append(("magical", "mag", sum(0.1 + 0.05 * i for i in range(int(d))) / d, d))
        elif stat in HARD_CC:
            sk.hard_cc += min(dur, HARD_CC[stat])
        elif stat == "blind":
            sk.blind += dur
        elif stat == "taunt":
            sk.taunt += dur
        elif stat == "confusion":
            sk.confusion += dur
        elif stat == "disarm":
            sk.disarm += dur
        elif stat == "slow":
            per, mx = GRID["slow"]
            sk.slow_seconds += min(stacks, mx) * per * dur
        elif stat == "heal_over_time_max_hp":
            sk.add_heal(tgt, flat=float(e.get("value", 0) or 0), hot_pct=float(e.get("pct", 0) or 0), dur=dur)
        elif stat == "heal_over_time_mag":
            sk.add_heal(tgt, flat=float(e.get("value", 0) or 0), stat="mag", coef=float(e.get("pct", 0) or 0) / 100, dur=dur)
        elif stat == "heal_over_time":
            per, mx = GRID["heal_over_time"]
            sk.add_heal(tgt, hot_pct=min(stacks, mx) * per, dur=dur)
        elif stat == "iron_stance_shield":
            sk.self_buffs["damage_reduction_up"] = (50.0, dur)
        elif stat and stat.startswith("shield"):
            src = {"shield_mag": "mag", "shield_max_hp": "max_hp", "shield_def": "def", "shield_max_mp": "max_mp",
                   "shield": "mag"}.get(stat, "mag")
            sk.add_shield(tgt, flat=float(e.get("value", 0) or 0) + float(e.get("base_value", 0) or 0),
                          stat=src, coef=float(e.get("pct", 0) or 0) / 100)
        elif stat in DMG_TAKEN:
            per, mx = DMG_TAKEN[stat]
            prev = sk.debuffs.get("dmg_taken", (0, dur))[0]
            sk.debuffs["dmg_taken"] = (prev + min(stacks, mx) * per, dur)
        elif stat == "damage_transfer":
            sk.redirect_pct, sk.redirect_dur = float(e.get("value", 0)), dur
        elif stat == "steady_aim_amplifier":
            sk.self_buffs["crit_damage_up"] = (50.0, dur)
        elif stat in ("all_stats", "all_stats_down"):
            v = float(e.get("value", 0))
            for k in ("atk", "mag", "armor", "magic_resist"):
                if stat == "all_stats":
                    sk.self_buffs[k + "_up"] = (v, dur); sk.ally_buffs[k + "_up"] = (v, dur)
                else:
                    sk.debuffs[k + "_down"] = (v, dur)
        elif stat == "lifesteal" and et == "utility":
            sk.lifesteal_on_skill += float(e.get("value", 0))
        elif stat == "mana_restore":
            sk.mana_restore += float(e.get("value", 0))
        elif stat in GRID:
            per, mx = GRID[stat]
            amt = min(stacks, mx) * per
            if et == "buff":
                if tgt == "self":
                    sk.self_buffs[stat] = (amt, dur)
                elif tgt in ("allies", "all"):
                    sk.self_buffs[stat] = (amt, dur); sk.ally_buffs[stat] = (amt, dur)
                else:
                    sk.ally_buffs[stat] = (amt, dur)
            elif etgt == "self":                       # self-inflicted malus (Frenzy, Iron Stance)
                sk.self_buffs[stat] = (amt, dur)
            else:
                sk.debuffs[stat] = (amt, dur)
        else:
            sk.unpriced.append(stat)
            unpriced_log.append((s["id"], stat))
    if s.get("scaling_stat") and s.get("scaling_percent") and dtype == "none" and not sk.has_support:
        unpriced_log.append((s["id"], f"none-type scaling {s['scaling_stat']} {s['scaling_percent']}%"))
    return sk


def load_subclasses(include_subclass_passives=True):
    reg = load_json("classes/class_registry.json")
    cbs = load_json("stats/class_base_stats.json")
    cg = load_json("stats/class_growth.json")
    commons = load_json("classes/common_passives.json")["common_passives"]
    out = {}
    for bc in reg["base_classes"]:
        cid = bc["id"]
        sk_file = load_json(f"classes/{cid}/skills.json")
        pas_file = load_json(f"classes/{cid}/passives.json")
        for sub in bc["subclasses"]:
            sid = sub["id"]
            if sid not in sk_file.get("subclass_skills", {}):
                continue
            unpriced = []
            base = _level20_base(cid, cbs, cg)
            pct = {}
            _apply_passives(base, pct, commons)
            _apply_passives(base, pct, pas_file.get("class_passives", []))
            if include_subclass_passives:
                p = os.path.join(ROOT, f"classes/{cid}/{sid}_passives.json")
                if os.path.exists(p):
                    _apply_passives(base, pct, load_json(f"classes/{cid}/{sid}_passives.json").get("subclass_passives", []))
            skills = [_parse_skill(s, cid, sid, unpriced) for s in sk_file["base_skills"]]
            skills += [_parse_skill(s, cid, sid, unpriced) for s in sk_file["subclass_skills"][sid]["skills"]]
            out[sid] = Subclass(id=sid, base_class=cid, base=base, pct=pct, skills=skills,
                                innate=INNATE.get(cid, {}), unpriced=unpriced)
    return out


if __name__ == "__main__":
    import sys
    subs = load_subclasses()
    print(len(subs), "subclasses")
    for sid in (sys.argv[1:] or ["berserker", "lifewarden", "elementalist"]):
        s = subs[sid]
        st = s.stats({"hp": 0, "mp": 0, "atk": 0, "mag": 0, "def": 0})
        print(f"\n== {sid} ({s.base_class}) no-alloc stats:", {k: round(v, 1) for k, v in st.items() if k in ('hp','mp','atk','mag','def','armor','magic_resist','crit','crit_dmg','damage_percent','armor_pen','lifesteal')})
        for k in s.skills:
            parts = []
            if k.direct: parts.append("dmg=" + ",".join(f"{t[0][:4]}:{t[2]:.2f}x{t[1]}" for t in k.direct))
            if k.dots: parts.append("dot=" + ",".join(f"{t[0][:4]}:{t[2]:.2f}x{t[1]}/s*{t[3]:.0f}s" for t in k.dots))
            for h in k.heals: parts.append(f"heal->{h['tgt']}={h['flat']}+{h['coef']} hot%hp={h['hot_pct']} dur={h['dur']}")
            for h in k.shields: parts.append(f"shield->{h['tgt']}={h['flat']}+{h['coef']}")
            if k.self_buffs: parts.append(f"self={k.self_buffs}")
            if k.ally_buffs: parts.append(f"ally={k.ally_buffs}")
            if k.debuffs: parts.append(f"debuff={k.debuffs}")
            for nm in ("hard_cc","blind","taunt","confusion","disarm","slow_seconds","lifesteal_on_skill","redirect_pct","mana_restore"):
                if getattr(k, nm): parts.append(f"{nm}={getattr(k, nm)}")
            if k.unpriced: parts.append(f"UNPRICED={k.unpriced}")
            print(f"  {k.id:45s} cd={k.cooldown:5.1f} mp={k.mana:5.1f} cast={k.cast_time:.1f} tgt={k.target:8s} | " + " ".join(parts))
    allu = {}
    for s in subs.values():
        for sid_, what in s.unpriced: allu.setdefault(what, []).append(sid_)
    print("\n== unpriced summary ==")
    for w, ids in sorted(allu.items(), key=lambda kv: -len(kv[1])): print(f"{len(ids):3d} {w}: {ids[:4]}")
