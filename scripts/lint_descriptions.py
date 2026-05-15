#!/usr/bin/env python3
"""
lint_descriptions.py — flag mechanical numbers in skill descriptions.

PR4 helper for PLAN_SKILL_TAB_REFACTOR.md §13. Scans every skill's
`description_fr` and `description_en` in the player-facing skills files
and prints a warning whenever a pattern that should now live in the
SkillMechanicsRenderer leaks back into the lore text.

Usage:
    python scripts/lint_descriptions.py             # report only
    python scripts/lint_descriptions.py --strict    # exit 1 on warnings (CI)
    python scripts/lint_descriptions.py --json      # machine-readable

Files scanned:
    classes/<class>/skills.json     (6 base classes + familiar)
    skills/pet_skills.json          (pool of familiar skills)

Files NOT scanned:
    skills/monster_skills.json      (vu seulement en tooltip combat,
                                     pas dans l'onglet Skills joueur)

The script is intentionally non-blocking by default — the cleanup pass
is editorial and some matches will be intentional (lore-style mention
of a numbered concept). Use --strict to gate CI once a clean baseline
has been reached.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


# ---------------------------------------------------------------------------
# Patterns — keep these aligned with PLAN_SKILL_TAB_REFACTOR.md §13.
# Each entry: (pattern_id, regex, language).
# ---------------------------------------------------------------------------

PATTERNS_FR: list[tuple[str, re.Pattern[str]]] = [
    ("scaling_pct_stat", re.compile(r"\d+\s*%\s*(ATK|MAG|DEF|HP|MP|PV)", re.IGNORECASE)),
    ("flat_resource",    re.compile(r"\+?\d+\s*(HP|MP|PV|Souffle)\b", re.IGNORECASE)),
    ("stacks",           re.compile(r"\d+\s*(stacks?|charges?)", re.IGNORECASE)),
    ("duration_pendant", re.compile(r"pendant\s+\d+(?:[.,]\d+)?\s*s\b", re.IGNORECASE)),
    ("chance_pct",       re.compile(r"chance\s+\d+\s*%", re.IGNORECASE)),
    ("aoe_zone",         re.compile(r"zone\s+\d+\s*x\s*\d+", re.IGNORECASE)),
    ("aoe_ligne",        re.compile(r"ligne\s+de\s+\d+", re.IGNORECASE)),
    ("cooldown_word",    re.compile(r"\b(?:cooldown|CD)\b", re.IGNORECASE)),
    ("mana_word",        re.compile(r"\bmana\b", re.IGNORECASE)),
    ("per_level",        re.compile(r"/\s*(niv|lvl|level)\b", re.IGNORECASE)),
    ("max_n",            re.compile(r"\(\s*max\s+\d+\s*\)", re.IGNORECASE)),
    ("paren_seconds",    re.compile(r"\(\s*\d+(?:[.,]\d+)?\s*s\b", re.IGNORECASE)),
]

PATTERNS_EN: list[tuple[str, re.Pattern[str]]] = [
    ("scaling_pct_stat", re.compile(r"\d+\s*%\s*(ATK|MAG|DEF|HP|MP)", re.IGNORECASE)),
    ("flat_resource",    re.compile(r"\+?\d+\s*(HP|MP|breath|mana)\b", re.IGNORECASE)),
    ("stacks",           re.compile(r"\d+\s*(stacks?|charges?)", re.IGNORECASE)),
    ("duration_for",     re.compile(r"for\s+\d+(?:\.\d+)?\s*seconds?", re.IGNORECASE)),
    ("aoe_area",         re.compile(r"area\s+\d+\s*x\s*\d+", re.IGNORECASE)),
    ("aoe_line_of",      re.compile(r"line\s+of\s+\d+", re.IGNORECASE)),
    ("aoe_tile_line",    re.compile(r"\d+-tile\s+line", re.IGNORECASE)),
    ("mana_cost_phrase", re.compile(r"\b(?:mana|breath)\s+cost\b", re.IGNORECASE)),
    ("cooldown_word",    re.compile(r"\bcooldown\b", re.IGNORECASE)),
    ("per_level",        re.compile(r"/\s*(?:lvl|level)\b", re.IGNORECASE)),
    ("max_n",            re.compile(r"\(\s*max\s+\d+\s*\)", re.IGNORECASE)),
    ("paren_seconds",    re.compile(r"\(\s*\d+(?:\.\d+)?\s*s\b", re.IGNORECASE)),
]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Hit:
    file: Path
    skill_id: str
    field: str          # "description_fr" or "description_en"
    pattern_id: str
    matched_text: str
    description_excerpt: str

    def to_dict(self) -> dict:
        return {
            "file": str(self.file),
            "skill_id": self.skill_id,
            "field": self.field,
            "pattern": self.pattern_id,
            "matched": self.matched_text,
            "excerpt": self.description_excerpt,
        }


@dataclass
class FileReport:
    file: Path
    hits: list[Hit] = field(default_factory=list)

    @property
    def hit_count(self) -> int:
        return len(self.hits)


# ---------------------------------------------------------------------------
# Walking
# ---------------------------------------------------------------------------

def iter_skill_objects(node) -> Iterator[dict]:
    """Yield every dict in `node` that looks like a skill (has an id and at
    least one description field)."""
    if isinstance(node, dict):
        if "id" in node and ("description_fr" in node or "description_en" in node):
            yield node
        for v in node.values():
            yield from iter_skill_objects(v)
    elif isinstance(node, list):
        for v in node:
            yield from iter_skill_objects(v)


def lint_file(path: Path) -> FileReport:
    report = FileReport(file=path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        # Don't fail the whole run on a single broken file — surface and move on.
        print(f"[lint] WARNING: could not parse {path}: {exc}", file=sys.stderr)
        return report

    for skill in iter_skill_objects(data):
        skill_id = str(skill.get("id", "<no-id>"))
        for field_name, patterns in (
            ("description_fr", PATTERNS_FR),
            ("description_en", PATTERNS_EN),
        ):
            text = skill.get(field_name)
            if not isinstance(text, str) or not text:
                continue
            for pattern_id, regex in patterns:
                for m in regex.finditer(text):
                    excerpt = _surrounding_excerpt(text, m.start(), m.end())
                    report.hits.append(Hit(
                        file=path,
                        skill_id=skill_id,
                        field=field_name,
                        pattern_id=pattern_id,
                        matched_text=m.group(0),
                        description_excerpt=excerpt,
                    ))
    return report


def _surrounding_excerpt(text: str, start: int, end: int, radius: int = 30) -> str:
    """Return ~radius chars on each side of [start:end] for context."""
    a = max(0, start - radius)
    b = min(len(text), end + radius)
    snippet = text[a:b].replace("\n", " ")
    prefix = "…" if a > 0 else ""
    suffix = "…" if b < len(text) else ""
    return f"{prefix}{snippet}{suffix}"


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_text_report(reports: list[FileReport]) -> int:
    total = 0
    by_pattern: dict[str, int] = {}
    for rep in reports:
        if not rep.hits:
            print(f"  OK  {rep.file.relative_to(_repo_root(rep.file))}")
            continue
        rel = rep.file.relative_to(_repo_root(rep.file))
        print(f"\n[{rep.hit_count} hits] {rel}")
        for hit in rep.hits:
            by_pattern[hit.pattern_id] = by_pattern.get(hit.pattern_id, 0) + 1
            print(f"    {hit.skill_id} :: {hit.field} :: {hit.pattern_id}")
            print(f"       matched: {hit.matched_text!r}")
            print(f"       context: {hit.description_excerpt}")
        total += rep.hit_count

    print("\n" + "=" * 60)
    print(f"  Total warnings: {total}")
    if by_pattern:
        print("  By pattern:")
        for pid, count in sorted(by_pattern.items(), key=lambda x: -x[1]):
            print(f"    {count:4d}  {pid}")
    print("=" * 60)
    return total


def print_json_report(reports: list[FileReport]) -> int:
    payload = {
        "files": [
            {
                "path": str(rep.file),
                "hit_count": rep.hit_count,
                "hits": [h.to_dict() for h in rep.hits],
            }
            for rep in reports
        ],
        "total": sum(rep.hit_count for rep in reports),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload["total"]


def _repo_root(any_path: Path) -> Path:
    """Walk up to find the kanarion_database root (the nearest dir containing
    `_meta` and `classes`)."""
    p = any_path.resolve()
    for parent in [p, *p.parents]:
        if (parent / "_meta").is_dir() and (parent / "classes").is_dir():
            return parent
    return p.parent


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    # Windows default cp1252 stdout chokes on UTF-8 chars in skill descriptions
    # (≤, é, →, etc.). Force UTF-8 with replace so the lint never crashes mid-report.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="kanarion_database root (default: derived from script location)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any warning was emitted (for CI gating)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable text",
    )
    args = parser.parse_args(argv)

    files = discover_files(args.root)
    if not files:
        print(f"[lint] No skill files found under {args.root}", file=sys.stderr)
        return 0

    reports = [lint_file(p) for p in files]
    total = print_json_report(reports) if args.json else print_text_report(reports)

    if args.strict and total > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
