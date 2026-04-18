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
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANGELOG_PATH = REPO_ROOT / "_meta" / "changelog.json"
POSTED_PATH = REPO_ROOT / "scripts" / ".posted_versions"
DOTENV_PATH = REPO_ROOT / ".env"

# Delay between posts when iterating multiple patches. Discord webhooks are
# rate-limited around 5 req/2s — 1.5s is comfortably under.
POST_DELAY_SECONDS = 1.5


def load_dotenv_if_present() -> None:
    """Minimal .env loader — no external deps. Only populates vars that are
    not already set so shell overrides still win."""
    if not DOTENV_PATH.exists():
        return
    try:
        for line in DOTENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except OSError:
        pass

# Kanarion gold — matches the UI theme so the embed ribbon is on-brand.
EMBED_COLOR = 0xC8A84E

# Maps the raw entry type to a section label per language. Unknown types
# fall through into the "Other" bucket so the script never drops an entry
# silently. Each locale carries its own section-order array so the
# presentation stays native.
TYPE_LABELS_EN: dict[str, str] = {
    "feat": "New Features",
    "fix": "Fixes",
    "balance": "Balance",
    "nerf": "Balance",
    "buff": "Balance",
    "content": "Content",
    "perf": "Performance",
}
TYPE_LABELS_FR: dict[str, str] = {
    "feat": "Nouveautés",
    "fix": "Corrections",
    "balance": "Équilibrage",
    "nerf": "Équilibrage",
    "buff": "Équilibrage",
    "content": "Contenu",
    "perf": "Performances",
}

SECTION_ORDER_EN = ["New Features", "Content", "Balance", "Fixes", "Performance", "Other"]
SECTION_ORDER_FR = ["Nouveautés", "Contenu", "Équilibrage", "Corrections", "Performances", "Autres"]

FALLBACK_EN = "Other"
FALLBACK_FR = "Autres"

MONTHS_EN = [
    "",
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
MONTHS_FR = [
    "",
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
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


def format_date(iso_date: str, lang: str) -> str:
    # iso_date is "YYYY-MM-DD". Hand-format to avoid locale-dependent libc.
    try:
        y, m, d = iso_date.split("-")
        month_i = int(m)
        day_i = int(d)
    except (ValueError, IndexError):
        return iso_date
    if lang == "fr":
        return f"{day_i} {MONTHS_FR[month_i]} {y}"
    return f"{MONTHS_EN[month_i]} {day_i}, {y}"


def group_entries(entries: list[dict], lang: str) -> dict[str, list[str]]:
    labels = TYPE_LABELS_FR if lang == "fr" else TYPE_LABELS_EN
    fallback = FALLBACK_FR if lang == "fr" else FALLBACK_EN
    # If the primary translation is missing, fall back to the other language
    # rather than dropping the line silently.
    primary_key = "text_fr" if lang == "fr" else "text_en"
    secondary_key = "text_en" if lang == "fr" else "text_fr"

    groups: dict[str, list[str]] = {}
    for e in entries:
        raw_type = str(e.get("type", "")).lower()
        section = labels.get(raw_type, fallback)
        text = e.get(primary_key) or e.get(secondary_key) or ""
        if not text:
            continue
        groups.setdefault(section, []).append(text)
    return groups


def build_single_embed(patch: dict, lang: str) -> dict:
    """One embed in the given language (en or fr)."""
    version = patch.get("version", "")
    if lang == "fr":
        title = patch.get("title_fr") or patch.get("title_en") or ""
        order = SECTION_ORDER_FR
        footer_tpl = "Sortie le {date}"
    else:
        title = patch.get("title_en") or patch.get("title_fr") or ""
        order = SECTION_ORDER_EN
        footer_tpl = "Released {date}"

    date = format_date(patch.get("date", ""), lang)
    groups = group_entries(patch.get("entries", []), lang)

    lines: list[str] = []
    if title:
        lines.append(f"*{title}*")
        lines.append("")
    for section in order:
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
        embed["footer"] = {"text": footer_tpl.format(date=date)}
    return embed


def build_embeds(patch: dict) -> list[dict]:
    """Build two embeds — English first, French second — for the bilingual
    webhook message. Discord stacks them visually, each with its own gold
    ribbon so players spot their language instantly.
    """
    return [build_single_embed(patch, "en"), build_single_embed(patch, "fr")]


def post_embeds(webhook_url: str, embeds: list[dict]) -> None:
    """POST one Discord webhook message containing up to 10 embeds."""
    payload = json.dumps({"embeds": embeds}).encode("utf-8")
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
    parser.add_argument("version", nargs="?",
                        help="Version to post (default: latest).")
    parser.add_argument("--all", action="store_true",
                        help="Post every unposted patch oldest-to-newest.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the embed JSON instead of posting.")
    parser.add_argument("--force", action="store_true",
                        help="Post even if the version was already posted.")
    args = parser.parse_args()

    if args.all and args.version:
        sys.exit("--all and a version argument are mutually exclusive")

    load_dotenv_if_present()
    changelog = load_changelog()

    if args.all:
        # changelog stores patches newest-first. Reverse so Discord reads as
        # history: oldest at top, newest at the bottom of the channel.
        patches_to_post = list(reversed(changelog.get("patches", [])))
        if not patches_to_post:
            sys.exit("changelog has no patches")
    else:
        patches_to_post = [pick_patch(changelog, args.version)]

    if args.dry_run:
        for patch in patches_to_post:
            print(f"=== v{patch.get('version', '?')} ===")
            print(json.dumps({"embeds": build_embeds(patch)},
                             indent=2, ensure_ascii=False))
        return

    webhook_url = os.environ.get("DISCORD_PATCH_WEBHOOK_URL", "").strip()
    if not webhook_url:
        sys.exit("DISCORD_PATCH_WEBHOOK_URL env var is required")

    posted = load_posted()
    sent = 0
    skipped = 0

    for i, patch in enumerate(patches_to_post):
        version = patch.get("version", "")
        if not args.force and version in posted:
            print(f"skip v{version} (already posted — use --force to re-post)")
            skipped += 1
            continue
        post_embeds(webhook_url, build_embeds(patch))
        mark_posted(version)
        sent += 1
        print(f"posted v{version} to Discord (EN + FR)")
        # Pace ourselves between posts when iterating; no delay on the last one.
        if i < len(patches_to_post) - 1:
            time.sleep(POST_DELAY_SECONDS)

    if args.all:
        print(f"done: {sent} posted, {skipped} skipped")


if __name__ == "__main__":
    main()
