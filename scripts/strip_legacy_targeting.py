#!/usr/bin/env python3
"""
Strip legacy targeting fields from skills now that the "targeting" block exists.

Removes: ignore_los, ignores_frontline (at skill level only, not nested effects).
Keeps: pattern (still used by enum fallback in from_legacy + display).

Usage:
  cd kanarion_database
  python scripts/strip_legacy_targeting.py --dry-run
  python scripts/strip_legacy_targeting.py
"""

import json
import os
import sys

DB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASSES_DIR = os.path.join(DB_ROOT, "classes")
LEGACY_FIELDS = {"ignore_los", "ignores_frontline"}


def strip_skill(skill):
    """Remove legacy targeting fields from a skill dict. Returns count removed."""
    if "targeting" not in skill:
        return 0  # Only strip if targeting block exists (safety)
    removed = 0
    for field in LEGACY_FIELDS:
        if field in skill:
            del skill[field]
            removed += 1
    return removed


def walk_and_strip(data):
    count = 0
    if isinstance(data, dict):
        if "pattern" in data and "name_fr" in data and "targeting" in data:
            count += strip_skill(data)
        for v in data.values():
            count += walk_and_strip(v)
    elif isinstance(data, list):
        for item in data:
            count += walk_and_strip(item)
    return count


def main():
    dry_run = "--dry-run" in sys.argv
    total = 0

    for cls_name in sorted(os.listdir(CLASSES_DIR)):
        skills_path = os.path.join(CLASSES_DIR, cls_name, "skills.json")
        if not os.path.isfile(skills_path):
            continue

        with open(skills_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = walk_and_strip(data)
        total += count

        if count > 0 and not dry_run:
            with open(skills_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

        status = "DRY-RUN" if dry_run else "WRITTEN"
        print(f"  {cls_name}/skills.json: {count} fields removed [{status}]")

    print(f"\nTotal: {total} legacy fields removed")
    if dry_run:
        print("(dry-run mode)")


if __name__ == "__main__":
    main()
