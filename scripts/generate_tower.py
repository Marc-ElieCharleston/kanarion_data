"""Generate the fixed floors of the Rift Tower (world/tower_floors.json), floors 1..authored_floors.

Tour v1 (2026-11-16): a palier every structure.guardian_every floors (guardian on its last
floor), the level jumps at each palier, the stat multiplier rises a little inside a block
and jumps at each palier once the level is capped (difficulty.stat_steps).

Rules live in systems/tower.json, monsters in entities/monsters.json.
The output is deterministic: the same inputs always give the same floors,
so every group fights the same floor N. Hand edits go in
systems/tower.json floor_overrides, never in the generated file.
Run from any directory; --check refuses a stale floors file.
"""
import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'world' / 'tower_floors.json'

FRONT = {'tank', 'brute', 'berserker'}
BACK = {'artillery', 'caster', 'controller'}
HEAL = {'healer', 'support'}
FAST = {'assassin'}


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf8'))


def monsters():
    data = load('entities/monsters.json')
    return data['monsters'] if isinstance(data, dict) else data


def pools_for(f, diff, by_id):
    names = next(row['pools'] for row in diff['floor_pools'] if row['floors'][0] <= f <= row['floors'][1])
    pool = sorted({mid for name in names for mid in diff['pools'][name]})
    members = [by_id[mid] for mid in pool]

    def of(roles):
        return [m for m in members if m.get('ai_role') in roles]
    return {'front': of(FRONT), 'back': of(BACK), 'heal': of(HEAL), 'fast': of(FAST),
            'elite': [m for m in members if m.get('threat_tier') == 'elite'],
            'all': members}


def entry(template, level, stars, mult, elite=False, boss=False, hp_extra=1.0, atk_extra=1.0, cap=50.0):
    return {'template_id': template, 'level': level, 'star_level': stars,
            'is_elite': elite, 'is_boss': boss,
            'hp_multiplier': round(min(cap, mult * hp_extra), 4),
            'atk_multiplier': round(min(cap, mult * atk_extra), 4),
            'def_multiplier': round(min(cap, mult), 4)}


def growth_multiplier(f, diff, every):
    """Stat multiplier of floor f (Tour v1, 2026-11-16): per_palier ** (palier floors p,
    multiples of `every`, with from_floor <= p < f) * (1 + in_palier_per_floor) ** (rank of f
    in its block - 1), capped at stat_multiplier_cap. A small rise inside a block of `every`
    floors, a big jump at each palier. The server computes the same thing
    (TowerRules::growth_multiplier)."""
    steps = diff['stat_steps']
    rank = (f - 1) % every
    first = max(steps['from_floor'], every)
    first += (-first) % every
    paliers = max(0, (f - 1 - first) // every + 1) if f > first else 0
    mult = (steps['per_palier'] ** paliers) * ((1.0 + steps['in_palier_per_floor']) ** rank)
    return min(diff['stat_multiplier_cap'], mult)


def floor(f, rules, roster):
    """Composition of floor f: fixed, derived only from the rules and the seed."""
    diff = rules['difficulty']
    every = rules['structure']['guardian_every']
    block, step = (f - 1) // every, (f - 1) % every + 1
    guardian = step == every
    level = min(diff['level_cap'], diff['level_base'] + 1 + diff['level_per_palier'] * block)
    stars_table = diff['stars_by_decade']
    stars = stars_table[min((f - 1) // 10, len(stars_table) - 1)]
    if guardian:
        stars = min(5, stars + diff['guardian_extra_stars'])
    mult = growth_multiplier(f, diff, every)
    count_rule = diff['monster_count']
    count = count_rule['first_floor'] + ((step - 1) // 2) * count_rule['per_two_floors_in_palier']
    count += sum(1 for x in count_rule['extra_from_floors'] if f >= x)
    count = min(count, count_rule['max'], rules['access']['max_monsters'])

    by_id = {m['id']: m for m in roster}
    pool = pools_for(f, diff, by_id)
    rng = random.Random(diff['seed'] * 100003 + f)
    cap = diff['stat_multiplier_cap']
    picked = []

    def take(group, **flags):
        choices = pool[group] or pool['all']
        picked.append(entry(rng.choice(choices)['id'], level, stars, mult, cap=cap, **flags))

    if guardian:
        table = diff['guardians_by_palier']
        boss_ids = table[min(block, len(table) - 1)]
        for boss_id in boss_ids:
            picked.append(entry(boss_id, level, stars, mult, boss=True,
                                hp_extra=diff['guardian_hp_multiplier'],
                                atk_extra=diff.get('guardian_atk_multiplier', 1.0), cap=cap))
        take('elite', elite=True)
        take('heal')
    take('front')
    if not guardian and step >= diff['healer_from_step_in_palier']:
        take('heal')
    if not guardian and step >= diff['elites_from_step_in_palier']:
        take('elite', elite=True)
    cycle = ['back', 'fast', 'front', 'back', 'fast']
    i = 0
    while len(picked) < count:
        take(cycle[i % len(cycle)])
        i += 1
    limit = count_rule['max'] if guardian else count
    return {'floor': f, 'guardian': guardian, 'level': level, 'stars': stars,
            'monsters': picked[:limit]}


def generate():
    rules = load('systems/tower.json')
    roster = monsters()
    known = {m['id'] for m in roster}
    floors = []
    for f in range(1, rules['structure']['authored_floors'] + 1):
        spec = floor(f, rules, roster)
        override = rules.get('floor_overrides', {}).get(str(f))
        if override:
            spec.update(override)
            spec['overridden'] = True
        for m in spec['monsters']:
            if m['template_id'] not in known:
                raise ValueError(f"floor {f}: unknown monster {m['template_id']}")
        floors.append(spec)
    return {'_meta': {'generated_by': 'scripts/generate_tower.py',
                      'rules': 'systems/tower.json',
                      'note': 'GENERATED. Edit systems/tower.json (floor_overrides for a single floor), then rerun the script.'},
            'floors': floors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='fail if world/tower_floors.json is stale')
    args = parser.parse_args()
    text = json.dumps(generate(), ensure_ascii=False, indent=2) + '\n'
    if args.check:
        current = OUT.read_text(encoding='utf8') if OUT.exists() else ''
        if current != text:
            raise SystemExit('world/tower_floors.json is stale: run python scripts/generate_tower.py')
        print('tower floors up to date')
        return
    OUT.write_text(text, encoding='utf8', newline='\n')
    print(f'wrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
