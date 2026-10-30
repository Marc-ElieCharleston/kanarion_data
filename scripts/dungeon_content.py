"""Validate open dungeons and derive their SQL templates from the JSON.

Source of truth for an open dungeon ("type": "open_instance",
"structure.spawn_model": "fixed_groups") is world/dungeons.json:
floors, monster groups (composition + position), boss, entry position.
world/zones.json only carries the per-floor zone (gate, outline, backdrop)
and must NOT redeclare monsters. This script refuses any drift between the
two, and is the only producer of the dungeon_templates rows the dungeon
service reads at entry.

Usage:
  python scripts/dungeon_content.py                      # validate every open dungeon
  python scripts/dungeon_content.py --dungeon dungeon_rat_den
  python scripts/dungeon_content.py --front ../kanarion_front   # also check scenes exist
  python scripts/dungeon_content.py --sql out.sql        # write the template upserts
  python scripts/dungeon_content.py --check-sql <migration.sql>  # migration matches data

Exit code 1 on any error. Never writes to a database.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_GROUPS_PER_FLOOR = 6
MAX_MEMBERS_PER_GROUP = 10  # 10 entities per side (Charleston, 2026-09-24): the monster side is capped at 10


def load(root, rel):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def point_in_polygon(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def open_dungeons(content):
    return [d for d in content['dungeons']
            if d.get('type') == 'open_instance'
            and d.get('structure', {}).get('spawn_model') == 'fixed_groups']


def zone_id_for(dungeon, floor, difficulty):
    return dungeon['zone_id_pattern'].format(
        zone_prefix=dungeon['zone_prefix'], floor=floor, difficulty=difficulty)


def dungeon_keys(root):
    """items/consumables.json dungeon_keys: key id -> the dungeon its effect opens."""
    return {k['id']: k.get('effect', {}).get('dungeon_id')
            for k in load(root, 'items/consumables.json').get('dungeon_keys', [])}


def validate_tiers(root, dungeon):
    """Keys and tier order (owner, 2026-10-15): ONE key per dungeon for every keyed tier,
    and a tier opens once the player has cleared the one named by requires_cleared."""
    errors = []
    did = dungeon['id']
    keys = dungeon_keys(root)
    tiers = dungeon.get('difficulties', {})
    required = {s.get('key_required') for s in tiers.values()} - {None}
    if len(required) > 1:
        errors.append(f'{did}: one key per dungeon, its tiers ask for {sorted(required)}')
    for tier, settings in tiers.items():
        key = settings.get('key_required')
        if key is not None and keys.get(key) != did:
            errors.append(f'{did} {tier}: key_required {key!r} is not a dungeon_keys item '
                          f'whose effect.dungeon_id is {did}')
        prev = settings.get('requires_cleared')
        if prev is not None and (prev == tier or prev not in tiers):
            errors.append(f'{did} {tier}: requires_cleared {prev!r} must be another tier of {did}')
    for tier in tiers:  # requires_cleared chains must end on a free tier, never loop
        seen, cur = set(), tier
        while cur is not None and cur not in seen:
            seen.add(cur)
            cur = tiers.get(cur, {}).get('requires_cleared')
        if cur is not None:
            errors.append(f'{did} {tier}: requires_cleared loops')
            break
    return errors


def _walk_ids(node, out):
    """Every dict carrying an "id" in a nested JSON tree, by id."""
    if isinstance(node, dict):
        if isinstance(node.get('id'), str):
            out.setdefault(node['id'], node)
        for v in node.values():
            _walk_ids(v, out)
    elif isinstance(node, list):
        for v in node:
            _walk_ids(v, out)
    return out


def validate_tier_content(root, dungeon):
    """Per-tier settings (2026-10-29): same floors for every tier, a tier moves the
    monster level (mob_level_offset), may retune the star roll (star_weights) and adds
    skills to chosen monsters (extra_skills, sent by presence to combat). A tier skill
    that declares `replaces` must replace a skill the monster really has. Every tier has
    its value in config/rewards.json multiplier_families.dungeon_difficulty."""
    errors = []
    did = dungeon['id']
    skills = _walk_ids(load(root, 'skills/monster_skills.json'), {})
    monsters = _walk_ids(load(root, 'entities/monsters.json'), {})
    reward_tiers = (load(root, 'config/rewards.json').get('multiplier_families', {})
                    .get('dungeon_difficulty', {}).get('values', {}))
    present = {m for fl in dungeon.get('floors', []) for g in fl.get('monster_groups', [])
               for m in g.get('members', [])}
    top = max((fl.get('mob_level_range', [0, 0])[1] for fl in dungeon.get('floors', [])), default=0)
    for tier, settings in dungeon.get('difficulties', {}).items():
        where = f'{did} {tier}'
        if tier not in reward_tiers:
            errors.append(f'{where}: no config/rewards.json dungeon_difficulty value for this tier')
        offset = settings.get('mob_level_offset', 0)
        if not isinstance(offset, int) or offset < 0 or top + offset > 100:
            errors.append(f'{where}: mob_level_offset {offset!r} must be an int >= 0 '
                          f'keeping the top floor ({top}) at most 100')
        weights = settings.get('star_weights')
        if weights is not None:
            ok = isinstance(weights, dict) and weights and all(
                k in {'0', '1', '2', '3', '4', '5'} and isinstance(v, (int, float)) and v >= 0
                for k, v in weights.items()) and sum(weights.values()) > 0
            if not ok:
                errors.append(f'{where}: star_weights must map stars "0".."5" to weights >= 0, sum > 0')
        lr = settings.get('level_range')
        if lr is not None and not (isinstance(lr, list) and len(lr) == 2
                                   and all(isinstance(x, int) for x in lr) and lr[0] <= lr[1]):
            errors.append(f'{where}: level_range must be [min, max]')
        for mob, extra in (settings.get('extra_skills') or {}).items():
            if mob not in present:
                errors.append(f'{where}: extra_skills names {mob}, absent from the floors')
                continue
            kit = (monsters.get(mob) or {}).get('skills', [])
            for sk in extra if isinstance(extra, list) else [extra]:
                skill = skills.get(sk)
                if skill is None:
                    errors.append(f'{where}: extra skill {sk!r} of {mob} is not in monster_skills.json')
                    continue
                rep = skill.get('replaces')
                if rep is not None and rep not in kit:
                    errors.append(f'{where}: {sk} replaces {rep!r}, which {mob} does not have')
    return errors


def rank_bands(root):
    """items/equipment_scaling.json tier_system.tiers -> [(rank, level_min, level_max)], rank 1-based
    in level order: the rank of a monster is the rank of its level (same table as the loot)."""
    tiers = load(root, 'items/equipment_scaling.json')['tier_system']['tiers']
    bands = sorted((t['level_range'][0], t['level_range'][1]) for k, t in tiers.items() if not k.startswith('_'))
    return [(i + 1, lo, hi) for i, (lo, hi) in enumerate(bands)]


def rank_of(bands, level):
    for rank, lo, hi in bands:
        if level <= hi:
            return rank
    return bands[-1][0]


def validate_key_drops(root, dungeons):
    """items/loot_tables.json dungeon_key_drops (owner, 2026-10-30): a key drops on every
    monster whose RANK is at least its dungeon's rank, the chance decaying with the rank gap
    (rank_decay). The rule's rank is never below the dungeon's rank (rank of its level_range
    floor) nor above the rank of its highest monster level, and a LIVE rule only drops a key
    that a declared tier asks for (else the key falls and opens nothing). _pending_rank_drops
    waits for its tier. level_band_drops (0.20.26) is gone: the server no longer reads it."""
    errors = []
    keys = dungeon_keys(root)
    by_id = {d['id']: d for d in dungeons}
    asked = {s.get('key_required') for d in dungeons for s in d.get('difficulties', {}).values()}
    block = load(root, 'items/loot_tables.json').get('dungeon_key_drops', {})
    bands = rank_bands(root)
    if 'level_band_drops' in block or '_pending_level_band_drops' in block:
        errors.append('dungeon_key_drops: level_band_drops is replaced by rank_drops (2026-10-30), '
                      'the server no longer reads it')
    decay = block.get('rank_decay')
    if not (isinstance(decay, list) and decay and decay[0] == 1
            and all(isinstance(x, (int, float)) and 0 < x <= 1 for x in decay)
            and all(a >= b for a, b in zip(decay, decay[1:]))):
        errors.append(f'dungeon_key_drops.rank_decay {decay!r}: non-empty list in ]0, 1], '
                      f'non-increasing, first value 1')
    seen = set()
    for live, rules in ((True, block.get('rank_drops', [])),
                        (False, block.get('_pending_rank_drops', []))):
        for r in rules:
            key = r.get('key_id')
            where = f'dungeon_key_drops {key}'
            dungeon = by_id.get(keys.get(key))
            if dungeon is None:
                errors.append(f'{where}: not a dungeon_keys item of an open dungeon')
                continue
            if live and key not in asked:
                errors.append(f'{where}: no declared tier asks for this key; '
                              f'keep the rule in _pending_rank_drops')
            if live and key in seen:
                errors.append(f'{where}: a second live rank rule for the same key (one per key)')
            seen.add(key)
            rank = r.get('rank')
            floor_rank = rank_of(bands, dungeon['level_range'][0])
            top = max((fl['mob_level_range'][1] for fl in dungeon.get('floors', [])), default=1)
            top += max((t.get('mob_level_offset', 0) for t in dungeon.get('difficulties', {}).values()), default=0)
            top_rank = rank_of(bands, min(top, 100))
            if not (isinstance(rank, int) and floor_rank <= rank <= top_rank):
                errors.append(f'{where}: rank {rank!r} must lie within {floor_rank}..{top_rank} '
                              f'(rank of {dungeon["id"]} level {dungeon["level_range"][0]} up to the '
                              f'rank of its highest monster, level {top}); never below the dungeon')
            if not isinstance(r.get('chance'), (int, float)) or not 0 < r['chance'] <= 1:
                errors.append(f'{where}: chance must be in (0, 1]')
    # Boss rules (owner, 2026-10-28): the key also drops on the dungeon's boss, one roll
    # per player per kill. The monster must be the boss of the key's dungeon, one rule
    # per boss (the server would skip a second one), and a LIVE rule needs a tier.
    for live, rules in ((True, block.get('boss_drops', [])),
                        (False, block.get('_pending_boss_drops', []))):
        bosses_seen = set()
        for r in rules:
            key = r.get('key_id')
            where = f'dungeon_key_drops boss {key}'
            dungeon = by_id.get(keys.get(key))
            if dungeon is None:
                errors.append(f'{where}: not a dungeon_keys item of an open dungeon')
                continue
            if live and key not in asked:
                errors.append(f'{where}: no declared tier asks for this key; '
                              f'keep the rule in _pending_boss_drops')
            boss = (dungeon.get('boss') or {}).get('id')
            if r.get('monster_id') != boss:
                errors.append(f'{where}: monster_id {r.get("monster_id")!r} is not the boss of '
                              f'{dungeon["id"]} ({boss!r})')
            if r.get('monster_id') in bosses_seen:
                errors.append(f'{where}: a second rule for {r.get("monster_id")} (one roll per boss kill)')
            bosses_seen.add(r.get('monster_id'))
            if not isinstance(r.get('chance'), (int, float)) or not 0 < r['chance'] <= 1:
                errors.append(f'{where}: chance must be in (0, 1]')
    return errors


def validate_floor_overrides(root, dungeon):
    """Per-tier floor settings (2026-10-30, Story mode of the Sewers): difficulties.<tier>.
    floor_overrides."<floor>" may replace that floor's mob_level_range for THIS tier only,
    pin the star of all its groups (stars) and scale the HP / attack of chosen monsters of
    that floor (hp_multipliers / atk_multipliers, sent by presence as MonsterMapping.
    post_hp_multiplier / post_atk_multiplier and applied by
    combat after the scaling model and the stars). Read by presence
    (world/dungeon_fixed_groups.cpp). The other tiers keep the floor as authored."""
    errors = []
    did = dungeon['id']
    floors = {fl.get('floor'): fl for fl in dungeon.get('floors', [])}
    allowed = {'mob_level_range', 'stars', 'hp_multipliers', 'atk_multipliers'}
    for tier, settings in dungeon.get('difficulties', {}).items():
        fos = settings.get('floor_overrides')
        if fos is None:
            continue
        if not isinstance(fos, dict):
            errors.append(f'{did} {tier}: floor_overrides must be an object keyed by floor number')
            continue
        for key, fo in fos.items():
            if key.startswith('_'):
                continue
            where = f'{did} {tier} floor_overrides.{key}'
            fl = floors.get(int(key)) if key.isdigit() else None
            if fl is None or not isinstance(fo, dict):
                errors.append(f'{where}: not a floor of {did}, or not an object')
                continue
            unknown = {k for k in fo if not k.startswith('_')} - allowed
            if unknown:
                errors.append(f'{where}: unknown key(s) {sorted(unknown)} (allowed: {sorted(allowed)})')
            lr = fo.get('mob_level_range')
            offset = settings.get('mob_level_offset', 0)
            if lr is not None and not (isinstance(lr, list) and len(lr) == 2
                                       and all(isinstance(x, int) for x in lr)
                                       and 1 <= lr[0] <= lr[1] and lr[1] + offset <= 100):
                errors.append(f'{where}: mob_level_range must be [min, max] within 1..100 (offset included)')
            st = fo.get('stars')
            if st is not None and not (isinstance(st, int) and 0 <= st <= 5):
                errors.append(f'{where}: stars must be an integer 0..5')
            members = {m for g in fl.get('monster_groups', []) for m in g.get('members', [])}
            for field in ('hp_multipliers', 'atk_multipliers'):
                for mob, mult in (fo.get(field) or {}).items():
                    if mob.startswith('_'):
                        continue
                    if mob not in members:
                        errors.append(f'{where}: {field} names {mob}, absent from floor {key}')
                    if not isinstance(mult, (int, float)) or not 0.1 <= mult <= 50:
                        errors.append(f'{where}: {field}.{mob} = {mult!r} outside [0.1, 50] '
                                      f'(the combat server clamps there)')
    return errors


def validate(root, dungeon, front=None):
    errors = (validate_tiers(root, dungeon) + validate_tier_content(root, dungeon)
              + validate_floor_overrides(root, dungeon))
    zones = {z['id']: z for z in load(root, 'world/zones.json')['zones']}
    monsters = {m['id'] for m in load(root, 'entities/monsters.json')['monsters']}
    did = dungeon['id']
    structure = dungeon['structure']
    floors = dungeon.get('floors', [])
    count = structure.get('floor_count')

    if [f.get('floor') for f in floors] != list(range(1, (count or 0) + 1)):
        errors.append(f'{did}: floors must be numbered 1..floor_count ({count})')
    if structure.get('boss_floor_index') != (count or 0) - 1:
        errors.append(f'{did}: boss_floor_index must be floor_count - 1 (the last floor)')
    if structure.get('groups_needed_to_advance') != 1:
        errors.append(f'{did}: groups_needed_to_advance must be 1 (one victory clears a floor)')
    if dungeon.get('exit_zone') not in zones:
        errors.append(f'{did}: exit_zone {dungeon.get("exit_zone")!r} is not a zone')
    ex = dungeon.get('exit_position')
    if not (isinstance(ex, list) and len(ex) == 2 and all(isinstance(c, (int, float)) for c in ex)):
        errors.append(f'{did}: exit_position [x, y] in exit_zone required (arrival after exit or boss)')
    if not dungeon.get('difficulties'):
        errors.append(f'{did}: no difficulty declared')

    boss_id = dungeon.get('boss', {}).get('id')
    if boss_id not in monsters:
        errors.append(f'{did}: boss.id {boss_id!r} is not in entities/monsters.json')
    if 'adds' in dungeon.get('boss', {}):
        errors.append(f'{did}: boss.adds is a second monster list, put the adds in the boss group')

    group_ids = set()
    for floor in floors:
        n = floor.get('floor')
        groups = floor.get('monster_groups', [])
        where = f'{did} floor {n}'
        if not 1 <= len(groups) <= MAX_GROUPS_PER_FLOOR:
            errors.append(f'{where}: {len(groups)} groups, expected 1..{MAX_GROUPS_PER_FLOOR}')
        lr = floor.get('mob_level_range')
        if not (isinstance(lr, list) and len(lr) == 2 and 1 <= lr[0] <= lr[1] <= 100):
            errors.append(f'{where}: mob_level_range must be [min, max] within 1..100')
        is_last = n == count
        boss_groups = [g for g in groups if g.get('is_boss')]
        if is_last:
            if len(boss_groups) != 1:
                errors.append(f'{where}: the last floor needs exactly one is_boss group')
            elif boss_groups[0].get('members', [None])[0] != boss_id:
                errors.append(f'{where}: the boss group leader (members[0]) must be boss.id {boss_id}')
        elif boss_groups:
            errors.append(f'{where}: is_boss group outside the last floor')
        for g in groups:
            gid = g.get('id')
            if not gid or gid in group_ids:
                errors.append(f'{where}: missing or duplicate group id {gid!r}')
            group_ids.add(gid)
            members = g.get('members', [])
            if not 1 <= len(members) <= MAX_MEMBERS_PER_GROUP:
                errors.append(f'{where} {gid}: {len(members)} members, expected 1..{MAX_MEMBERS_PER_GROUP}')
            for m in members:
                if m not in monsters:
                    errors.append(f'{where} {gid}: unknown monster {m}')
            # Star: fixed ("stars") or rolled by presence at every (re)spawn from
            # star_weights (the group's, else structure.star_weights). Keys are stars 0..5.
            if 'stars' in g:
                if not isinstance(g['stars'], int) or not 0 <= g['stars'] <= 5:
                    errors.append(f'{where} {gid}: stars must be an integer 0..5')
            else:
                weights = g.get('star_weights', dungeon.get('structure', {}).get('star_weights'))
                if not isinstance(weights, dict) or not weights:
                    errors.append(f'{where} {gid}: no stars and no star_weights (group or structure)')
                else:
                    for k, v in weights.items():
                        if not (str(k).isdigit() and 0 <= int(k) <= 5) or not isinstance(v, (int, float)) or v < 0:
                            errors.append(f'{where} {gid}: star_weights {k}:{v} invalid (star 0..5, weight >= 0)')
                    if sum(v for v in weights.values() if isinstance(v, (int, float))) <= 0:
                        errors.append(f'{where} {gid}: star_weights sum to 0')
            if not (isinstance(g.get('position'), list) and len(g['position']) == 2):
                errors.append(f'{where} {gid}: position [x, y] required')

        for difficulty in dungeon.get('difficulties', {}):
            zid = zone_id_for(dungeon, n, difficulty)
            zone = zones.get(zid)
            if zone is None:
                errors.append(f'{zid}: missing zone')
                continue
            if zone.get('dungeon_id') != did or zone.get('floor') != n:
                errors.append(f'{zid}: dungeon_id/floor must be {did}/{n}')
            if zone.get('type') != 'dungeon_open':
                errors.append(f'{zid}: type must be dungeon_open')
            if zone.get('level_range', [None])[0] != dungeon.get('min_level'):
                errors.append(f'{zid}: level_range[0] is the player gate and must equal '
                              f'min_level {dungeon.get("min_level")}')
            for key in ('spawn_areas', 'mobs', 'scripted_spawns'):
                if zone.get(key):
                    errors.append(f'{zid}: declares {key}; monsters come from dungeons.json only')
            if not zone.get('combat_backdrop'):
                errors.append(f'{zid}: combat_backdrop required')
            poly = zone.get('area_limit') or []
            if len(poly) < 3:
                errors.append(f'{zid}: area_limit (floor outline) required')
            else:
                ep = floor.get('entry_position')
                if not (isinstance(ep, list) and len(ep) == 2) or not point_in_polygon(ep[0], ep[1], poly):
                    errors.append(f'{zid}: entry_position {ep} is outside area_limit')
                for g in groups:
                    p = g.get('position')
                    if isinstance(p, list) and len(p) == 2 and not point_in_polygon(p[0], p[1], poly):
                        errors.append(f'{zid}: group {g.get("id")} position {p} is outside area_limit')
            if front is not None:
                scene = front / zone.get('map_path', '').removeprefix('res://')
                if not scene.is_file():
                    errors.append(f'{zid}: scene {zone.get("map_path")} not found in {front}')
    return errors


def quote(value):
    return 'NULL' if value is None else "'" + str(value).replace("'", "''") + "'"


COLUMNS = ['id', 'name', 'difficulty', 'min_level', 'max_players', 'room_count',
           'boss_room_index', 'lockout_type', 'key_required_item_id']


def template_sql(dungeon):
    out = []
    for difficulty, settings in dungeon['difficulties'].items():
        values = [quote(dungeon['id'] + '_' + difficulty),
                  quote(dungeon.get('name_en', dungeon.get('name'))),
                  quote(difficulty),
                  str(dungeon['min_level']),
                  str(max(dungeon['recommended_party_size'])),
                  str(dungeon['structure']['floor_count']),
                  str(dungeon['structure']['boss_floor_index']),
                  quote(dungeon.get('lockout_type', '')),
                  quote(settings.get('key_required'))]
        out.append('INSERT INTO dungeon_templates (' + ', '.join(COLUMNS) + ')\nVALUES ('
                   + ', '.join(values) + ')\nON CONFLICT (id) DO UPDATE SET '
                   + ', '.join(c + ' = EXCLUDED.' + c for c in COLUMNS[1:]) + ';')
    return '\n\n'.join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data', type=Path, default=ROOT)
    parser.add_argument('--dungeon', help='limit to one dungeon id')
    parser.add_argument('--front', type=Path, help='kanarion_front root, to check the scenes exist')
    parser.add_argument('--sql', type=Path, help='write the dungeon_templates upserts here')
    parser.add_argument('--check-sql', type=Path, help='fail unless this file contains the upserts verbatim')
    args = parser.parse_args()

    content = load(args.data, 'world/dungeons.json')
    dungeons = open_dungeons(content)
    for d in content['dungeons']:
        if d.get('type') == 'open_instance' and d not in dungeons and args.dungeon in (None, d['id']):
            print(f'WARNING: {d["id"]} is open_instance but not on the fixed_groups contract; '
                  f'NOT validated, its floors run on the legacy spawn_areas path')
    if args.dungeon:
        dungeons = [d for d in dungeons if d['id'] == args.dungeon]
        if not dungeons:
            print(f'ERROR: {args.dungeon} is not an open fixed_groups dungeon')
            return 1
    errors = []
    for d in dungeons:
        errors += validate(args.data, d, args.front)
    errors += validate_key_drops(args.data, open_dungeons(content))
    sql = '\n\n'.join(template_sql(d) for d in dungeons) + '\n'
    if args.check_sql:
        text = args.check_sql.read_text(encoding='utf-8').replace('\r\n', '\n')
        for d in dungeons:
            if template_sql(d) not in text:
                errors.append(f'{args.check_sql.name}: template rows for {d["id"]} differ from the data; '
                              f'regenerate with --sql and add a new migration')
    for e in errors:
        print('ERROR:', e)
    if errors:
        return 1
    if args.sql:
        args.sql.write_text(sql, encoding='utf-8')
    print(f'OK: {len(dungeons)} open dungeon(s) valid: ' + ', '.join(d['id'] for d in dungeons))
    return 0


if __name__ == '__main__':
    sys.exit(main())
