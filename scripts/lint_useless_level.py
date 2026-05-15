#!/usr/bin/env python3
"""
lint_useless_level.py — flag "level-trap" skills.

A level-trap skill is one where leveling up only increases the Souffle
(mana) cost without scaling ANY actual mechanic — the player wastes a
skill point making the same skill more expensive to cast.

Heuristic
---------
A skill is flagged when :
    mana_cost_per_level > 0  (or absent — loader applies a +4/level default)
AND every per-level scaling field is 0 / absent :
    power_per_level
    percent_per_level
    effect_power_per_level
    duration_per_level
    shield_value_per_level
    hot_duration_per_level
    hot_duration_scaling

It also reports a secondary category :
    DoT-static : dot_percent > 0 but no dot_percent_per_level /
                 dot_duration_per_level (those fields don't exist in the
                 current schema — flagged for designers to consider
                 extending Skill).
    HoT-static : symmetric for hot_percent without hot_duration_per_level.

Usage
-----
    python scripts/lint_useless_level.py           # report
    python scripts/lint_useless_level.py --strict  # exit 1 on hits
    python scripts/lint_useless_level.py --json    # machine-readable

Scope
-----
    classes/<class>/skills.json   (6 base classes + familiar)
    skills/pet_skills.json
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


# Default applied by skill.gd loader when mana_cost_per_level is missing.
DEFAULT_MP_COST_PER_LEVEL = 4

# Per-level fields at the SKILL ROOT that count as "scales something useful".
# Source of truth = kanarion_front/scripts/skills/skill.gd loader (any field the
# loader actually reads). NOTE: heal_scaling_per_level is intentionally NOT here
# — neither client (skill.gd) nor backend (room.cpp) reads it; it is dead data.
POSITIVE_PER_LEVEL_FIELDS = [
    "power_per_level",
    "percent_per_level",
    "effect_power_per_level",
    "duration_per_level",
    "buff_duration_per_level",
    "debuff_duration_per_level",
    "shield_value_per_level",
    "hot_duration_per_level",
    "hot_duration_scaling",
    "success_chance_per_level",
    "lifesteal_per_level",
    "lifesteal_percent_per_level",
    "disarm_chance_per_level",
    "stun_chance_per_level",
    "defense_reduction_per_level",
    # Niche skill-specific scalings (used on a small number of skills)
    "damage_per_adjacent_ally_per_level",
    "team_damage_amp_per_level",
    "bonus_per_charge_per_level",
]

# Skill-root fields where a NEGATIVE per-level value is the "good" direction
# (lower cooldown = better for the player). Keeping them separate because the
# generic "> 0" check would otherwise treat them as missing.
NEGATIVE_IS_POSITIVE_FIELDS = [
    "cooldown_per_level",
]

# Per-level fields that may live INSIDE an entry of `effects[]` (per-effect override).
# Loader reads `duration_per_level` in skill.gd around line 830
# (entry.get("duration_per_level", ...)). The other entries scale per-effect
# value/pct on non-canonical effects (shields, HoT pct, mana_restore, lifesteal,
# counter chance).
NESTED_POSITIVE_PER_LEVEL_FIELDS = [
    "duration_per_level",
    "pct_per_level",
    "value_per_level",
    "counter_chance_per_level",
]


@dataclass
class Hit:
    file: Path
    skill_id: str
    category: str          # "level-trap" | "dot-static" | "hot-static"
    detail: str            # one-liner explanation

    def to_dict(self) -> dict:
        return {
            "file": str(self.file),
            "skill_id": self.skill_id,
            "category": self.category,
            "detail": self.detail,
        }


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def iter_skill_objects(node) -> Iterator[dict]:
    if isinstance(node, dict):
        if "id" in node and ("description_fr" in node or "description_en" in node):
            yield node
        for v in node.values():
            yield from iter_skill_objects(v)
    elif isinstance(node, list):
        for v in node:
            yield from iter_skill_objects(v)


def positive_per_level_summary(skill: dict) -> dict[str, float]:
    """Return {field_name: value} for every per-level field that is > 0.

    Looks at:
      - root-level skill fields (POSITIVE_PER_LEVEL_FIELDS)
      - nested effects[].* fields (NESTED_POSITIVE_PER_LEVEL_FIELDS) — keyed
        as "effects[i].<field>" so the report shows where the scaling lives.
    """
    out: dict[str, float] = {}
    for name in POSITIVE_PER_LEVEL_FIELDS:
        v = skill.get(name)
        if isinstance(v, (int, float)) and float(v) > 0:
            out[name] = float(v)
    for name in NEGATIVE_IS_POSITIVE_FIELDS:
        v = skill.get(name)
        if isinstance(v, (int, float)) and float(v) < 0:
            out[name] = float(v)
    effects = skill.get("effects")
    if isinstance(effects, list):
        for i, entry in enumerate(effects):
            if not isinstance(entry, dict):
                continue
            for name in NESTED_POSITIVE_PER_LEVEL_FIELDS:
                v = entry.get(name)
                if isinstance(v, (int, float)) and float(v) > 0:
                    out[f"effects[{i}].{name}"] = float(v)
    return out


def cost_scales(skill: dict) -> tuple[bool, str]:
    """True if leveling raises the cost. Returns (scales, reason_str)."""
    mc = skill.get("mana_cost_per_level")
    if mc is None:
        return True, f"mana_cost_per_level missing -> loader default +{DEFAULT_MP_COST_PER_LEVEL}/lvl"
    if isinstance(mc, (int, float)) and float(mc) > 0:
        return True, f"mana_cost_per_level={mc}"
    return False, "cost flat (mana_cost_per_level=0)"


def lint_skill(path: Path, skill: dict) -> list[Hit]:
    hits: list[Hit] = []
    sid = str(skill.get("id", "<no-id>"))
    cost_up, cost_reason = cost_scales(skill)
    per_level = positive_per_level_summary(skill)

    # Heuristic 1 — level trap : cost rises but no mechanic per-level field is positive.
    if cost_up and not per_level:
        ctx = _mechanic_context(skill)
        hits.append(Hit(
            file=path,
            skill_id=sid,
            category="level-trap",
            detail=f"{cost_reason} ; aucun *_per_level positif" + (f" ; mechanic ctx : {ctx}" if ctx else ""),
        ))

    # Heuristic 2 — DoT static : has DoT but no per-level scaling on it.
    dot_pct = float(skill.get("dot_percent", 0) or 0)
    if dot_pct > 0:
        has_dot_per_level = any(
            isinstance(skill.get(k), (int, float)) and float(skill.get(k, 0)) > 0
            for k in ("dot_percent_per_level", "dot_duration_per_level")
        )
        if not has_dot_per_level:
            hits.append(Hit(
                file=path,
                skill_id=sid,
                category="dot-static",
                detail=f"dot_percent={dot_pct}, dot_duration={skill.get('dot_duration', 0)} — pas de per-level sur le DoT (schema Skill manque dot_percent_per_level / dot_duration_per_level)",
            ))

    # Heuristic 3 — HoT static : has HoT but no per-level scaling on it.
    hot_pct = float(skill.get("hot_percent", 0) or 0)
    if hot_pct > 0:
        has_hot_per_level = any(
            isinstance(skill.get(k), (int, float)) and float(skill.get(k, 0)) > 0
            for k in ("hot_percent_per_level", "hot_duration_per_level", "hot_duration_scaling")
        )
        if not has_hot_per_level:
            hits.append(Hit(
                file=path,
                skill_id=sid,
                category="hot-static",
                detail=f"hot_percent={hot_pct}, hot_duration={skill.get('hot_duration', 0)} — pas de per-level sur le HoT",
            ))

    return hits


def _mechanic_context(skill: dict) -> str:
    """Pull the most relevant numeric mechanic fields for the report so
    the designer sees what the skill DOES at a glance."""
    parts: list[str] = []
    for key in ("base_power", "scaling_percent", "heal_base", "heal_scaling_percent",
                "shield_base", "shield_scaling_percent",
                "dot_percent", "dot_duration",
                "hot_percent", "hot_duration"):
        v = skill.get(key)
        if isinstance(v, (int, float)) and float(v) > 0:
            parts.append(f"{key}={v}")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# File walking
# ---------------------------------------------------------------------------

def lint_file(path: Path) -> list[Hit]:
    out: list[Hit] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[lint] WARNING: could not parse {path}: {exc}", file=sys.stderr)
        return out
    for skill in iter_skill_objects(data):
        out.extend(lint_skill(path, skill))
    return out


def discover_files(root: Path) -> list[Path]:
    files: list[Path] = []
    classes_dir = root / "classes"
    if classes_dir.is_dir():
        for sub in sorted(classes_dir.iterdir()):
            if sub.is_dir():
                p = sub / "skills.json"
                if p.is_file():
                    files.append(p)
    pet = root / "skills" / "pet_skills.json"
    if pet.is_file():
        files.append(pet)
    return files


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_text(hits: list[Hit], root: Path) -> int:
    by_cat: dict[str, list[Hit]] = {}
    for h in hits:
        by_cat.setdefault(h.category, []).append(h)

    if not hits:
        print("OK — no level-trap, no static DoT/HoT.")
        return 0

    order = ["level-trap", "dot-static", "hot-static"]
    for cat in order:
        if cat not in by_cat:
            continue
        bucket = by_cat[cat]
        print(f"\n[{cat}]  {len(bucket)} hit{'s' if len(bucket) != 1 else ''}")
        print("-" * 60)
        for h in bucket:
            print(f"  {h.skill_id}")
            print(f"    file  : {_rel(h.file, root)}")
            print(f"    detail: {h.detail}")

    print("\n" + "=" * 60)
    print(f"  Total : {len(hits)} hits across {len(by_cat)} categor{'ies' if len(by_cat) != 1 else 'y'}")
    for cat in order:
        if cat in by_cat:
            print(f"    {len(by_cat[cat]):4d}  {cat}")
    print("=" * 60)
    return len(hits)


def print_json(hits: list[Hit]) -> int:
    payload = {
        "hits": [h.to_dict() for h in hits],
        "total": len(hits),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return len(hits)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[1],
                        help="kanarion_database root (default: derived from script location)")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 if any hit was emitted (for CI gating)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of human-readable text")
    args = parser.parse_args(argv)

    files = discover_files(args.root)
    if not files:
        print(f"[lint] No skill files found under {args.root}", file=sys.stderr)
        return 0

    hits: list[Hit] = []
    for p in files:
        hits.extend(lint_file(p))

    total = print_json(hits) if args.json else print_text(hits, args.root)

    if args.strict and total > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
