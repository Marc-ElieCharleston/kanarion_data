"""Validate systems/premium_pass.json (premium pass, owner rules 2026-10-13 / 2026-10-15).

The pass gives comfort and time, never combat power. The server knows a fixed list of
benefits (each one needs code); anything else is refused here instead of being silently
ignored in game. Also checks the weekly Passage Key item and the pre-registration bonus.

Usage: python scripts/validate_premium_pass.py [--data <root>]
Exit code 1 on any error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# benefit id -> (python type, min, max). Mirrors kanarion_back services/economy/src/premium.
BENEFITS = {
    'out_of_combat_regen_multiplier': ((int, float), 1, 3),
    'familiar_out_of_combat_regen_multiplier': ((int, float), 1, 3),
    'teleport_free': (bool, None, None),
    'npc_buy_discount_percent': (int, 0, 50),
    'weekly_keys': (int, 0, 7),
}
WEEKDAYS = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}
ISO_UTC = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')


def load(root, rel):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def is_type(value, kind):
    if kind is bool:
        return isinstance(value, bool)
    return isinstance(value, kind) and not isinstance(value, bool)


def validate(root):
    errors = []
    d = load(root, 'systems/premium_pass.json')
    rules = d.get('rules', {})
    banked = rules.get('max_banked_days')
    if not is_type(banked, int) or banked < 1:
        errors.append('rules.max_banked_days must be a positive integer')

    passes = d.get('passes', [])
    if not passes:
        errors.append('passes: at least one pass')
    ids = set()
    for p in passes:
        pid = p.get('id')
        if not pid or pid in ids:
            errors.append(f'passes: missing or duplicate id {pid!r}')
        ids.add(pid)
        for f in ('name_fr', 'name_en'):
            if not p.get(f):
                errors.append(f'{pid}: {f} required')
        days = p.get('duration_days')
        if not is_type(days, int) or days < 1 or (is_type(banked, int) and days > banked):
            errors.append(f'{pid}: duration_days must be 1..max_banked_days')
        benefits = p.get('benefits')
        if not isinstance(benefits, dict) or not benefits:
            errors.append(f'{pid}: benefits must be a non-empty object')
            continue
        for b, v in benefits.items():
            if b not in BENEFITS:
                errors.append(f'{pid}: unknown benefit {b!r} (the server only knows {sorted(BENEFITS)}); '
                              f'a combat bonus is never allowed')
                continue
            kind, lo, hi = BENEFITS[b]
            if not is_type(v, kind) or (lo is not None and not lo <= v <= hi):
                errors.append(f'{pid}: {b} = {v!r} out of range' + (f' {lo}..{hi}' if lo is not None else ''))

    wk = d.get('weekly_key', {})
    keys = {k['id']: k for k in load(root, 'items/consumables.json').get('dungeon_keys', [])}
    item = keys.get(wk.get('item_id'))
    if item is None:
        errors.append(f'weekly_key.item_id {wk.get("item_id")!r} is not in items/consumables.json dungeon_keys')
    else:
        # Real money must never become gold: the key cannot be traded or resold.
        if item.get('tradeable') is not False or item.get('hdv_listable') is not False or item.get('sell_price') != 0:
            errors.append(f'{item["id"]}: must be tradeable false, hdv_listable false, sell_price 0')
        if item.get('effect', {}).get('type') != 'dungeon_key_any':
            errors.append(f'{item["id"]}: effect.type must be dungeon_key_any')
    reset = wk.get('reset', {})
    if reset.get('weekday') not in WEEKDAYS:
        errors.append('weekly_key.reset.weekday must be a weekday name')
    if not is_type(reset.get('hour'), int) or not 0 <= reset['hour'] <= 23:
        errors.append('weekly_key.reset.hour must be 0..23')
    if reset.get('timezone') != 'Europe/Paris':
        errors.append('weekly_key.reset.timezone must be Europe/Paris (the only zone the server computes)')
    if not is_type(wk.get('max_held'), int) or wk['max_held'] < 1:
        errors.append('weekly_key.max_held must be a positive integer')
    if any(p.get('benefits', {}).get('weekly_keys', 0) > wk.get('max_held', 0) for p in passes
           if isinstance(p.get('benefits'), dict) and is_type(p['benefits'].get('weekly_keys', 0), int)):
        errors.append('a pass gives more weekly_keys than weekly_key.max_held')

    pre = d.get('preregistration_bonus', {})
    if not is_type(pre.get('diamonds'), int) or pre['diamonds'] < 0:
        errors.append('preregistration_bonus.diamonds must be an integer >= 0')
    if pre.get('pass_id') not in ids:
        errors.append(f'preregistration_bonus.pass_id {pre.get("pass_id")!r} is not a pass')
    if not is_type(pre.get('pass_days'), int) or pre['pass_days'] < 0:
        errors.append('preregistration_bonus.pass_days must be an integer >= 0')
    rel = pre.get('release_at')
    if rel is not None and not (isinstance(rel, str) and ISO_UTC.match(rel)):
        errors.append('preregistration_bonus.release_at must be null or "YYYY-MM-DDTHH:MM:SSZ"')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data', type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.data)
    for e in errors:
        print('ERROR:', e)
    if errors:
        return 1
    print('OK: systems/premium_pass.json valid')
    return 0


if __name__ == '__main__':
    sys.exit(main())
