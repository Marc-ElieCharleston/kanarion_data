#!/usr/bin/env python3
"""Generate draft social media posts (X / Twitter + Instagram) from a changelog patch.

Reads the canonical patch notes file (`_meta/changelog.json`), picks a patch
(newest by default), selects the most player-facing highlights and formats them
into ready-to-edit drafts for X and Instagram, in EN and/or FR.

The output is a DRAFT. It reuses the changelog wording as-is (which is already
sober and player-facing) so you keep your voice. Read it, tweak it, then paste
it into your scheduler (Publer / Metricool). Nothing here posts anything.

Usage:
    python scripts/gen_social_posts.py
    python scripts/gen_social_posts.py --version 0.6.2.0 --lang both
    python scripts/gen_social_posts.py --link https://discord.gg/xxxx --limit 4
    python scripts/gen_social_posts.py --out drafts.md

Stdlib only. No external dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Script lives in kanarion_database/scripts/, so the repo root is one level up.
REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_PATH = REPO_ROOT / "_meta" / "changelog.json"

# Which change types are worth putting in a promo post, most compelling first.
# `feat` = new stuff players can see; `balance` = they care about; `fix` fills in.
# `perf` / `refactor` are excluded from highlights by default (not marketing-worthy).
TYPE_PRIORITY = ["feat", "balance", "fix"]

# X counts a link as 23 chars no matter its real length. Budget accordingly.
X_LIMIT = 280
X_LINK_COST = 23

HASHTAGS = {
    "en": "#IndieGame #gamedev #MMORPG #pixelart #madewithGodot",
    "fr": "#jeuindé #gamedev #MMORPG #pixelart #madewithGodot",
}

LABELS = {
    "en": {
        "whatsnew": "What's new",
        "join": "Play / join the Discord",
        "patch": "Patch",
    },
    "fr": {
        "whatsnew": "Au programme",
        "join": "Jouer / rejoindre le Discord",
        "patch": "Patch",
    },
}


def load_patches() -> list[dict]:
    if not CHANGELOG_PATH.exists():
        sys.exit(f"error: changelog not found at {CHANGELOG_PATH}")
    try:
        data = json.loads(CHANGELOG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"error: could not parse {CHANGELOG_PATH}: {exc}")
    patches = data.get("patches", [])
    if not patches:
        sys.exit("error: changelog has no patches")
    return patches


def pick_patch(patches: list[dict], version: str | None) -> dict:
    if version is None:
        return patches[0]  # stored newest-first
    for patch in patches:
        if patch.get("version") == version:
            return patch
    sys.exit(f"error: version {version!r} not found in changelog")


def select_highlights(entries: list[dict], limit: int) -> list[dict]:
    """Pick up to `limit` entries, ordered by TYPE_PRIORITY then original order."""
    ordered: list[dict] = []
    for wanted in TYPE_PRIORITY:
        for entry in entries:
            if entry.get("type") == wanted:
                ordered.append(entry)
    return ordered[:limit]


def field(obj: dict, base: str, lang: str) -> str:
    return obj.get(f"{base}_{lang}", "").strip()


def build_x_single(patch: dict, highlights: list[dict], lang: str, link: str) -> tuple[str, int]:
    """One-shot tweet. Trims bullets to respect the char budget."""
    title = field(patch, "title", lang)
    tags = HASHTAGS[lang]
    footer = f"▶ {link}\n{tags}"
    header = f"{title}"

    # Budget: total limit minus header, footer, separators, and link-cost adjustment.
    # We approximate link length with X_LINK_COST so a long URL doesn't blow the count.
    def rendered_len(bullets: list[str]) -> int:
        body = "\n".join(bullets)
        text = f"{header}\n\n{body}\n\n{footer}"
        # X shortens links to 23 chars; correct for the difference.
        return len(text) - len(link) + X_LINK_COST

    bullets = [f"• {field(e, 'text', lang)}" for e in highlights]
    while bullets and rendered_len(bullets) > X_LIMIT:
        bullets.pop()  # drop the least-important trailing bullet until it fits

    body = "\n".join(bullets)
    text = f"{header}\n\n{body}\n\n{footer}" if bullets else f"{header}\n\n{footer}"
    return text, rendered_len(bullets) if bullets else (len(text) - len(link) + X_LINK_COST)


def build_x_thread(patch: dict, highlights: list[dict], lang: str, link: str) -> list[str]:
    """Intro tweet + one tweet per highlight + closing tweet with the link."""
    version = patch.get("version", "?")
    title = field(patch, "title", lang)
    lbl = LABELS[lang]
    tweets = [f"{lbl['patch']} v{version} — {title} \U0001f9f5⬇️"]
    for i, entry in enumerate(highlights, start=1):
        tweets.append(f"{i}. {field(entry, 'text', lang)}")
    tweets.append(f"▶ {lbl['join']}: {link}\n{HASHTAGS[lang]}")
    return tweets


def build_instagram(patch: dict, highlights: list[dict], lang: str, link: str) -> str:
    version = patch.get("version", "?")
    title = field(patch, "title", lang)
    lbl = LABELS[lang]
    lines = [f"\U0001f6e0️ {lbl['patch']} v{version} — {title}", "", f"{lbl['whatsnew']} :" if lang == "fr" else f"{lbl['whatsnew']}:"]
    for entry in highlights:
        lines.append(f"• {field(entry, 'text', lang)}")
    lines += ["", f"\U0001f3ae {lbl['join']}: {link}", "", HASHTAGS[lang]]
    return "\n".join(lines)


def render(patch: dict, langs: list[str], link: str, limit: int) -> str:
    entries = patch.get("entries", [])
    highlights = select_highlights(entries, limit)
    version = patch.get("version", "?")
    date = patch.get("date", "?")

    out: list[str] = []
    out.append(f"# Social drafts — v{version} ({date})")
    out.append(f"_{len(highlights)} highlights selected from {len(entries)} changelog lines. Edit before posting._")
    out.append("")

    for lang in langs:
        lang_name = "English" if lang == "en" else "Français"
        out.append(f"## {lang_name}")
        out.append("")

        x_single, count = build_x_single(patch, highlights, lang, link)
        warn = "  ⚠️ OVER LIMIT" if count > X_LIMIT else ""
        out.append(f"### X — single post ({count}/{X_LIMIT} chars){warn}")
        out.append("```")
        out.append(x_single)
        out.append("```")
        out.append("")

        out.append("### X — thread")
        for i, tweet in enumerate(build_x_thread(patch, highlights, lang, link), start=1):
            out.append(f"**{i}/**")
            out.append("```")
            out.append(tweet)
            out.append("```")
        out.append("")

        out.append("### Instagram — caption")
        out.append("```")
        out.append(build_instagram(patch, highlights, lang, link))
        out.append("```")
        out.append("")

    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate X/Instagram draft posts from a changelog patch.")
    parser.add_argument("--version", help="Patch version (default: newest).")
    parser.add_argument("--lang", choices=["en", "fr", "both"], default="both", help="Output language(s).")
    parser.add_argument("--limit", type=int, default=4, help="Max highlights to include (default: 4).")
    parser.add_argument("--link", default="https://discord.gg/YOUR_INVITE", help="CTA link (your Discord invite).")
    parser.add_argument("--out", help="Write to this file instead of stdout.")
    args = parser.parse_args()

    # Windows consoles default to cp1252, which chokes on the emoji in the
    # drafts. Force UTF-8 on stdout so `--out`-less runs print cleanly.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    patches = load_patches()
    patch = pick_patch(patches, args.version)
    langs = ["en", "fr"] if args.lang == "both" else [args.lang]

    text = render(patch, langs, args.link, args.limit)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote drafts to {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
