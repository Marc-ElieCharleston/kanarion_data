#!/usr/bin/env python3
"""Post a patch note to Discord via webhook.

Reads _meta/changelog.json, picks a version (latest by default), formats it
as a Discord embed in French, and POSTs it to the channel's webhook.

Usage:
    # Latest version
    DISCORD_PATCH_WEBHOOK_URL="https://discord.com/api/webhooks/..." \
        python3 scripts/post_patch_to_discord.py

    # Specific version
    python3 scripts/post_patch_to_discord.py 0.4.7.6

    # Preview without posting
    python3 scripts/post_patch_to_discord.py --dry-run

    # Force re-post even if already posted
    python3 scripts/post_patch_to_discord.py 0.4.7.6 --force

The webhook URL is read from the DISCORD_PATCH_WEBHOOK_URL env var. Never
hardcoded — a leaked webhook lets anyone spam the channel.

Posted versions are tracked in scripts/.posted_versions so a rerun of the
same version refuses to double-post. Use --force to override.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANGELOG_PATH = REPO_ROOT / "_meta" / "changelog.json"
POSTED_PATH = REPO_ROOT / "scripts" / ".posted_versions"

# Kanarion gold — matches the UI theme so the embed ribbon is on-brand.
EMBED_COLOR = 0xC8A84E

# Map the raw entry type to a French section label. Unknown types fall
# through into "Autres" so the script never drops an entry silently.
TYPE_LABELS: dict[str, str] = {
    "feat": "Nouveautes",
    "fix": "Corrections",
    "balance": "Equilibrage",
    "nerf": "Equilibrage",
    "buff": "Equilibrage",
    "content": "Contenu",
    "perf": "Performances",
}

# Preferred section order — groups show up in the embed in this order.
SECTION_ORDER = ["Nouveautes", "Contenu", "Equilibrage", "Corrections", "Performances", "Autres"]

# Short French month names for the footer date line.
MONTHS_FR = [
    "",
    "janvier", "fevrier", "mars", "avril", "mai", "juin",
    "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
]


def load_changelog() -> dict:
    if not CHANGELOG_PATH.exists():
        sys.exit(f"changelog not found at {CHANGELOG_PATH}")
    with CHANGELOG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def pick_patch(changelog: dict, version: str | None) -> dict:
    patches = changelog.get("patches", [])
    if not patches:
        sys.exit("changelog has no patches")
    if version is None:
        return patches[0]
    for p in patches:
        if p.get("version") == version:
            return p
    sys.exit(f"version {version} not found in changelog")


def format_date_fr(iso_date: str) -> str:
    # iso_date is "YYYY-MM-DD". Avoid locale pitfalls by hand-formatting.
    try:
        y, m, d = iso_date.split("-")
        return f"{int(d)} {MONTHS_FR[int(m)]} {y}"
    except (ValueError, IndexError):
        return iso_date


def group_entries(entries: list[dict]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for e in entries:
        raw_type = str(e.get("type", "")).lower()
        section = TYPE_LABELS.get(raw_type, "Autres")
        text = e.get("text_fr") or e.get("text_en") or ""
        if not text:
            continue
        groups.setdefault(section, []).append(text)
    return groups


def build_embed(patch: dict) -> dict:
    version = patch.get("version", "")
    title_fr = patch.get("title_fr") or patch.get("title_en") or ""
    date = format_date_fr(patch.get("date", ""))
    groups = group_entries(patch.get("entries", []))

    # Compose the embed description by stacking sections in the preferred order.
    # Each section is a bold label + bullet list. No emojis — pure text.
    lines: list[str] = []
    if title_fr:
        lines.append(f"*{title_fr}*")
        lines.append("")
    for section in SECTION_ORDER:
        items = groups.get(section)
        if not items:
            continue
        lines.append(f"**{section}**")
        for text in items:
            lines.append(f"- {text}")
        lines.append("")

    description = "\n".join(lines).strip()
    # Discord embed descriptions are capped at 4096 chars. Truncate with a
    # clear marker rather than silently losing content.
    if len(description) > 4000:
        description = description[:3990] + "\n\n(...)"

    embed = {
        "title": f"Kanarion Online — v{version}",
        "description": description,
        "color": EMBED_COLOR,
    }
    if date:
        embed["footer"] = {"text": f"Patch du {date}"}
    return embed


def post_embed(webhook_url: str, embed: dict) -> None:
    payload = json.dumps({"embeds": [embed]}).encode("utf-8")
    # Cloudflare (in front of Discord) blocks the default Python-urllib UA as
    # bot-like and returns HTTP 403 error code 1010. A normal-looking UA fixes
    # it without hiding what we are.
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "KanarionPatchBot/1.0 (+https://www.kanariononline.com)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status >= 400:
                sys.exit(f"Discord returned HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        sys.exit(f"Discord HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error reaching Discord: {e}")


def load_posted() -> set[str]:
    if not POSTED_PATH.exists():
        return set()
    return {line.strip() for line in POSTED_PATH.read_text().splitlines() if line.strip()}


def mark_posted(version: str) -> None:
    existing = load_posted()
    existing.add(version)
    POSTED_PATH.write_text("\n".join(sorted(existing)) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a patch note to Discord.")
    parser.add_argument("version", nargs="?", help="Version to post (default: latest).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the embed JSON instead of posting.")
    parser.add_argument("--force", action="store_true",
                        help="Post even if version was already posted.")
    args = parser.parse_args()

    changelog = load_changelog()
    patch = pick_patch(changelog, args.version)
    version = patch.get("version", "")

    embed = build_embed(patch)

    if args.dry_run:
        print(json.dumps(embed, indent=2, ensure_ascii=False))
        return

    webhook_url = os.environ.get("DISCORD_PATCH_WEBHOOK_URL", "").strip()
    if not webhook_url:
        sys.exit("DISCORD_PATCH_WEBHOOK_URL env var is required")

    if not args.force and version in load_posted():
        sys.exit(
            f"version {version} already posted — use --force to re-post "
            f"(tracked in {POSTED_PATH.name})"
        )

    post_embed(webhook_url, embed)
    mark_posted(version)
    print(f"posted v{version} to Discord")


if __name__ == "__main__":
    main()
