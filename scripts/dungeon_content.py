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
MAX_MEMBERS_PER_GROUP = 12  # a room holds 32 entities, players + familiars included


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


def validate(root, dungeon, front=None):
    errors = []
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
            if not isinstance(g.get('stars'), int) or not 0 <= g['stars'] <= 5:
                errors.append(f'{where} {gid}: stars must be an integer 0..5')
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
