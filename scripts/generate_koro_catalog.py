"""Generate five Koro ranks for every authored active class skill.

The gameplay rules live in systems/koro.json. Existing item IDs are retained.
Run from any directory; --check refuses a stale generated catalog.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def active_skills(node, in_tier3=False):
    """Yield (skill, in_tier3). in_tier3: the skill sits under a `tier3` specialization block."""
    if isinstance(node, dict):
        if str(node.get('id', '')).startswith('skill_') and 'target' in node:
            yield node, in_tier3
            return
        for key, value in node.items():
            if not key.startswith('_'):
                yield from active_skills(value, in_tier3 or key == 'tier3')
    elif isinstance(node, list):
        for value in node:
            yield from active_skills(value, in_tier3)


def generate():
    rules = json.loads((ROOT / 'systems/koro.json').read_text(encoding='utf8'))
    generation = rules['card_generation']
    # A card cannot lend a skill earlier than its own class gets it: tier 3
    # (specialization) skills wait for the tier 3 unlock level (config/skill_system.json).
    categories = json.loads((ROOT / 'config/skill_system.json').read_text(encoding='utf8'))['skill_categories']
    koro_level = rules['equipment']['slot_unlock_levels'][0]
    tier3_level = max(koro_level, categories['tier3']['unlock_at_player_level'])
    cards = []
    seen = set()
    excluded = set(generation.get('excluded_skill_classes', []))
    for path in sorted((ROOT / 'classes').glob('*/skills.json')):
        if path.parent.name in excluded:
            continue
        for skill, in_tier3 in active_skills(json.loads(path.read_text(encoding='utf8'))):
            sid = skill['id']
            if sid in seen:
                raise ValueError(f'duplicate active skill: {sid}')
            seen.add(sid)
            for rank, percent in generation['rank_percents'].items():
                key = sid + ':' + rank
                card_id = generation['legacy_ids'].get(key, 'koro_' + sid.removeprefix('skill_') + '_' + rank.lower())
                card = dict(id=card_id, name_fr=f"Koro : {skill['name_fr']} ({rank})",
                    name_en=f"Koro: {skill.get('name_en', skill['name_fr'])} ({rank})",
                    base_skill_id=sid, base_class_id=path.parent.name, rank=rank, rank_percent=percent,
                    level_req=tier3_level if in_tier3 else koro_level, tradeable=True, hdv_listable=True, sell_price=0,
                    skill_tier=skill.get('tier', 'active'),
                    drop_weight=generation['skill_weight_by_tier'].get(skill.get('tier', ''), 2),
                    icon=f"res://assets/icons/koro/koro_rank_{rank.lower()}.png",
                    description_fr=f"Prête {skill['name_fr']}. Dégâts, soins et durée des effets temporaires : {percent}% de la technique au niveau 1. Les techniques sans dégâts ni soins ont une recharge divisée par ce facteur. La carte doit rester équipée.",
                    description_en=f"Lends {skill.get('name_en', skill['name_fr'])}. Damage, healing and temporary effect duration: {percent}% of the level-1 technique. Non-damaging, non-healing techniques divide their cooldown by this factor. The card must remain equipped.")
                if sid in generation['merchant_skills'] and rank in ['C', 'B']:
                    card['buy_price'] = generation['merchant_prices'][rank]
                cards.append(card)
    return {'_meta': {'version': '2.0', 'generated_by': 'scripts/generate_koro_catalog.py',
        'slot_type': 'koro', 'max_equipped': rules['equipment']['max_equipped'], 'active_skill_count': len(seen),
        'description': 'One active skill per removable card; every skill exists at C/B/A/S/SS. Rules: systems/koro.json.'}, 'koro_cards': cards}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    target = ROOT / 'items/koro_cards.json'
    result = generate()
    if args.check:
        if json.loads(target.read_text(encoding='utf8')) != result:
            raise SystemExit('Koro catalog is stale; run scripts/generate_koro_catalog.py')
    else:
        target.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
    print(f"Koro catalog: {result['_meta']['active_skill_count']} active skills, {len(result['koro_cards'])} cards")
