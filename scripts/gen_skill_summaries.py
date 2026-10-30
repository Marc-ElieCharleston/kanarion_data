#!/usr/bin/env python3
"""Generate the short summaries shown by the skill tooltips and sheets.

Player report 2026-10-29: tooltips and skill sheets (skill bar, spell book,
mastery, passives, familiars, Koro, keystones) showed walls of text. The client
now shows a SHORT summary by default and the full description behind a "+".

The summary is EXTRACTED from the authored description, never written: this
script only keeps or drops pieces of `description_fr` / `description_en`. It adds
no word of its own (except the ellipsis that marks a cut), so it can never say
something the full text does not say, and nothing here is hand-written per skill.

Rules, applied to both languages with the SAME decisions:
  1. split the description into sentences;
  2. keep the sentences that carry a number (the mechanics); the lore sentences
     ("The Commander calls his own...") have none and are dropped;
  3. drop parenthesised details (caps, conditions), still visible behind "+",
     but keep the ones that say how a value grows per rank or level;
  4. take the first mechanical sentence, add the next one while the whole fits;
  5. a first sentence longer than MAX_CHARS is cut on a clause boundary and ends
     with an ellipsis.
A step whose FR and EN results would disagree (different numbers) is not taken:
the summary falls back to the safer, longer form.

Output: ui/skill_summaries.json, {id: {"fr": ..., "en": ..., "whole"?: true}}.
"whole" means nothing was dropped: the client then shows no "+".
    python scripts/gen_skill_summaries.py           # write
    python scripts/gen_skill_summaries.py --check   # CI: stale file, missing
                                                    # summary, long dash, size
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'ui' / 'skill_summaries.json'

# Two to three lines of the 360 px tooltip (about 50 chars a line). Shorter cut
# whole clauses away: the first sentence usually carries the damage AND its
# status effects, a cut at 110 dropped the effects (review of the 29/10 captures).
MAX_CHARS = 140
ELLIPSIS = '…'
# Long dashes are banned from player text (Charleston): never emit one, and
# refuse a description that would carry one into a summary.
FORBIDDEN = ('—', '–')

# Every file whose entries are shown by a skill tooltip or sheet.
SOURCES = [
    'classes/*/skills.json',
    'classes/*/*passives.json',
    'classes/common_skills.json',
    'classes/common_passives.json',
    'classes/passive_tree.json',
    'classes/familiar/skills.json',
    'classes/familiar/passives.json',
    'skills/monster_skills.json',
    'items/koro_cards.json',
    'items/keystone_items.json',
    'systems/keystones.json',
]

_SENTENCE_END = re.compile(r'(?<=[.!?])\s+(?=[A-ZÀ-Ý«"(+\-0-9])')
_PAREN = re.compile(r'\s*\([^()]*\)')
# A parenthesis that says how a value GROWS with the rank stays: without it the
# summary would claim the rank 1 value for every rank ("Inflige 60% ATQ" read at
# rank 5, where the sheet says 68%).
_KEEP_PAREN = re.compile(r'\b(rang|rank|niveau|level|niv)\b|/\s*(niv|lvl|rang|rank)', re.IGNORECASE)
_NUMBER = re.compile(r'\d+(?:[.,]\d+)?')
_CLAUSE = re.compile(r'(?<=[,;:])\s+')


def entries(node):
    """Every dict carrying an id and a French description, in file order."""
    if isinstance(node, dict):
        if isinstance(node.get('id'), str) and isinstance(node.get('description_fr'), str):
            yield node
        for key, value in node.items():
            if not key.startswith('_'):
                yield from entries(value)
    elif isinstance(node, list):
        for value in node:
            yield from entries(value)


def sentences(text):
    text = ' '.join(text.split())
    return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]


def numbers(text):
    return sorted(n.replace(',', '.') for n in _NUMBER.findall(text))


def strip_details(sentence):
    out = _PAREN.sub(lambda m: m.group(0) if _KEEP_PAREN.search(m.group(0)) else '', sentence).strip()
    # Only the gap the removed group leaves before a period or a comma: the
    # French space before ':' ';' '!' '?' is kept.
    out = re.sub(r'\s+([.,])', r'\1', out)
    return out if any(c.isalnum() for c in out) else sentence


def mechanical(sentence_list):
    return [s for s in sentence_list if _NUMBER.search(s)]


def cut_clauses(sentence, count):
    parts = _CLAUSE.split(sentence)
    if count >= len(parts):
        return sentence
    kept = ' '.join(parts[:count]).rstrip(' ,;:')
    return kept + ELLIPSIS


def summarize(fr, en):
    """(summary_fr, summary_en) for one entry. Same decisions in both languages."""
    sfr, sen = sentences(fr), sentences(en)
    mfr, men = mechanical(sfr), mechanical(sen)
    paired = len(mfr) == len(men) and len(mfr) > 0
    if not paired:
        # No mechanical sentence, or the two languages do not line up: the first
        # sentence of each, which is how every description starts.
        mfr, men = sfr[:1] or [fr], sen[:1] or [en]
    mfr = [strip_details(s) for s in mfr]
    men = [strip_details(s) for s in men]

    out_fr, out_en = mfr[0], men[0]
    # Add the following mechanical sentences while both languages still fit.
    for i in range(1, min(len(mfr), len(men)) if paired else 1):
        cand_fr, cand_en = out_fr + ' ' + mfr[i], out_en + ' ' + men[i]
        if max(len(cand_fr), len(cand_en)) > MAX_CHARS:
            break
        out_fr, out_en = cand_fr, cand_en
    # A single sentence still too long: cut each language on a clause boundary,
    # keeping the longest pair that fits AND says the same numbers. The two
    # languages do not always split into the same number of clauses ("Apres
    # 2,5s d'incantation, inflige" / "After a 2.5s cast, deals"), so the cut
    # points are searched together rather than assumed to match.
    if max(len(out_fr), len(out_en)) > MAX_CHARS:
        nfr, nen = len(_CLAUSE.split(out_fr)), len(_CLAUSE.split(out_en))
        best = None
        for kf in range(1, nfr):
            a = cut_clauses(out_fr, kf)
            for ke in range(1, nen):
                b = cut_clauses(out_en, ke)
                if max(len(a), len(b)) <= MAX_CHARS and numbers(a) == numbers(b):
                    if best is None or len(a) + len(b) > len(best[0]) + len(best[1]):
                        best = (a, b)
        if best is not None:
            out_fr, out_en = best
    return out_fr, out_en


def collect():
    result = {}
    origin = {}
    texts = {}
    for pattern in SOURCES:
        for path in sorted(ROOT.glob(pattern)):
            data = json.loads(path.read_text(encoding='utf-8'))
            rel = path.relative_to(ROOT).as_posix()
            for entry in entries(data):
                eid = entry['id']
                fr = entry.get('description_fr', '').strip()
                en = (entry.get('description_en') or fr).strip()
                if not fr:
                    continue
                if eid in result:
                    if origin[eid] == rel:
                        continue  # same entry reached twice inside one file
                    # Same id in two files (shared pools): first file wins, the
                    # check below makes sure both describe the same thing.
                    continue
                texts[eid] = {'fr': fr, 'en': en}
                sfr, sen = summarize(fr, en)
                result[eid] = {'fr': sfr, 'en': sen}
                # Nothing was dropped: the client shows no "+" for this entry.
                if _norm(sfr) == _norm(fr) and _norm(sen) == _norm(en):
                    result[eid]['whole'] = True
                origin[eid] = rel
    return dict(sorted(result.items())), texts


def _norm(text):
    return ' '.join(text.split())


_WORD = re.compile(r'\w+', re.UNICODE)

# Hard ceiling, whatever the clause cuts could do (a sentence without any clause
# boundary stays whole). Above this, the description itself needs a rewrite.
HARD_MAX_CHARS = 180


def problems(summaries, sources):
    out = []
    for eid, pair in summaries.items():
        for lang in ('fr', 'en'):
            text = pair.get(lang, '')
            if not text.strip():
                out.append(f'{eid}: summary_{lang} empty')
            if any(c in text for c in FORBIDDEN):
                out.append(f'{eid}: summary_{lang} carries a long dash')
            if len(text) > HARD_MAX_CHARS:
                out.append(f'{eid}: summary_{lang} is {len(text)} chars (max {HARD_MAX_CHARS})')
            # Extracted, never invented: every word of the summary is a word of
            # the description it comes from.
            source_words = set(_WORD.findall(sources[eid][lang]))
            extra = [w for w in _WORD.findall(text) if w not in source_words]
            if extra:
                out.append(f'{eid}: summary_{lang} has words absent from the description: {extra[:5]}')
    for eid in sources:
        if eid not in summaries:
            out.append(f'{eid}: no summary')
    return out


def render(summaries):
    """One entry per line: small file, readable diff when a description changes."""
    meta = {
        'generated_by': 'scripts/gen_skill_summaries.py',
        'rule': 'extracted from description_fr/en, never hand-written; regenerate, do not edit',
        'max_chars': MAX_CHARS,
        'sources': SOURCES,
    }
    lines = ['{', '  "_meta": ' + json.dumps(meta, ensure_ascii=False) + ',', '  "summaries": {']
    items = list(summaries.items())
    for i, (eid, pair) in enumerate(items):
        comma = ',' if i < len(items) - 1 else ''
        lines.append('    ' + json.dumps(eid) + ': ' + json.dumps(pair, ensure_ascii=False) + comma)
    lines += ['  }', '}']
    return ('\n'.join(lines) + '\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--stats', action='store_true')
    args = parser.parse_args()
    summaries, texts = collect()
    issues = problems(summaries, texts)
    if args.stats:
        cut = sum(1 for p in summaries.values() if p['fr'].endswith(ELLIPSIS))
        longest = max(max(len(p['fr']), len(p['en'])) for p in summaries.values())
        over = sum(1 for p in summaries.values() if max(len(p['fr']), len(p['en'])) > MAX_CHARS)
        mismatch = sum(1 for p in summaries.values() if numbers(p['fr']) != numbers(p['en']))
        print(f'{len(summaries)} summaries, {cut} cut on a clause, {over} over {MAX_CHARS} chars '
              f'(longest {longest}), {mismatch} with FR/EN numbers that differ')
    blob = render(summaries)
    if args.check:
        if not OUT.exists() or OUT.read_bytes().replace(b'\r\n', b'\n') != blob:
            issues.append(f'{OUT.relative_to(ROOT).as_posix()} is stale: run python scripts/gen_skill_summaries.py')
        if issues:
            print('\n'.join(issues))
            return 1
        print(f'skill summaries OK ({len(summaries)} entries)')
        return 0
    if issues:
        print('\n'.join(issues))
        return 1
    OUT.write_bytes(blob)
    print(f'wrote {OUT.relative_to(ROOT).as_posix()} ({len(summaries)} entries)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
