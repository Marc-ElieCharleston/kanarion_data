"""Cuit les prix de revente PNJ (systems/npc_resale.json) dans le sell_price de chaque objet.

Materiaux (selon le niveau du monstre le plus bas qui les lache), pierres de forge,
potions / nourriture / gemmes de boutique, livres de familier, empreintes, stigmates.
L equipement n est PAS cuit : le serveur le calcule a la vente (bloc `equipment`).
Garde le formatage des fichiers. A relancer apres ajout de monstres ou de materiaux.

Usage (racine du depot) : python -I scripts/reprice_npc_resale.py [--check]
  --check : n ecrit rien, sort en erreur si un prix n est pas a jour (CI / pre-commit).
"""
import json, re, sys, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = json.load(open(os.path.join(ROOT, 'systems', 'npc_resale.json'), encoding='utf-8'))


def g(L, c):
    return c['curve_base'] + c['curve_coef'] * max(1, L) ** c['curve_exponent']


def material_levels(db):
    L = lambda f: json.load(open(db + '/' + f, encoding='utf-8'))
    lt = L('items/loot_tables.json')['monster_loot_tables']
    mons = L('entities/monsters.json')['monsters']
    lv = collections.defaultdict(list)

    def tbl(m):
        k = m.get('loot_table_id') or ''
        if k in lt: return k
        s = m['id']; s = s[4:] if s.startswith('mob_') else (s[5:] if s.startswith('boss_') else s)
        return s if s in lt else 'default'
    for m in mons:
        if 'tutorial' in m['id'] or 'dummy' in m['id']: continue
        for d in lt.get(tbl(m), []):
            lv[d['item_id']].append(m['base_level'])
    byid = {m['id']: m['base_level'] for m in mons}
    return lv, byid


def compute(db):
    L = lambda f: json.load(open(db + '/' + f, encoding='utf-8'))
    R = RULES
    lv, byid = material_levels(db)
    out, why = {}, {}
    mat = L('items/materials.json')
    nolvl = []
    for b in ('common', 'uncommon', 'rare'):
        k = R['materials'][b]
        for x in mat.get(b, []):
            levels = lv.get(x['id']) or [byid[s] for s in x.get('sources', []) if s in byid]
            if not levels:
                nolvl.append(x['id']); continue
            lvl = min(levels)
            out[x['id']] = max(k['min'], round(k['factor'] * g(lvl, R['curve'])))
            why[x['id']] = f'{b} L{lvl}'
    for x in mat.get('enhancement_stones', []):
        out[x['id']] = R['enhancement_stones'][x['stone_rank']]; why[x['id']] = x['stone_rank']
    ratio = R['shop_items']['sell_ratio_of_buy']
    for x in mat.get('gems', []):
        if x.get('buy_price'):
            out[x['id']] = max(1, round(ratio * x['buy_price'])); why[x['id']] = 'buy ratio'
    c = L('items/consumables.json')
    for b in ('potions', 'food'):
        for x in c.get(b, []):
            if x.get('buy_price'):
                out[x['id']] = max(1, round(ratio * x['buy_price'])); why[x['id']] = 'buy ratio'
    for x in c.get('familiar_traces', []):
        out[x['id']] = R['familiar_traces'][x.get('trace_rarity') or x.get('rarity')]; why[x['id']] = 'trace'
    for x in L('items/pet_books.json')['pet_books']:
        if x.get('buy_price'):
            out[x['id']] = max(1, round(R['pet_books']['sell_ratio_of_buy'] * x['buy_price'])); why[x['id']] = 'book'
    for x in L('items/keystone_items.json')['keystone_items']:
        out[x['id']] = R['keystones'][x['rank']]; why[x['id']] = 'keystone'
    # Fabrication (profession_recipes.json) : un objet fabrique ne se revend JAMAIS plus
    # que crafted_cap_of_inputs x (or de la recette + revente des ingredients) / quantite.
    # Ne fait que baisser. Point fixe : un ingredient peut lui-meme etre fabrique.
    cap = R['crafted']['cap_of_inputs']
    pr = L('items/profession_recipes.json')
    price = {}
    def collect(o):
        if isinstance(o, dict):
            if 'id' in o and isinstance(o.get('sell_price'), int): price[o['id']] = o['sell_price']
            for v in o.values(): collect(v)
        elif isinstance(o, list):
            for v in o: collect(v)
    for f in ('items/materials.json', 'items/consumables.json', 'items/pet_books.json',
              'items/keystone_items.json', 'items/koro_cards.json', 'items/profession_recipes.json'):
        collect(L(f))
    price.update(out)
    for _ in range(10):
        moved = False
        for r in pr.get('recipes', []):
            o = r.get('output_item')
            if o not in price or price[o] <= 0: continue
            mats = r.get('materials', [])
            if any(m['id'] not in price for m in mats): continue
            inputs = r.get('gold_cost', 0) + sum(price[m['id']] * m['qty'] for m in mats)
            ceiling = max(1, int(cap * inputs / max(1, r.get('output_qty', 1))))
            if price[o] > ceiling:
                price[o] = ceiling; out[o] = ceiling; why[o] = 'crafted cap'; moved = True
        if not moved: break
    return out, why, nolvl

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    repo = ROOT
    new, why, nolvl = compute(repo)
    if nolvl:
        sys.exit('sans niveau (aucun monstre ne les lache) : ' + ', '.join(nolvl))
    check = '--check' in sys.argv
    ID = re.compile(r'"id": "([^"]+)"')
    SP = re.compile(r'"sell_price": -?\d+')
    changed = 0
    for f in ('items/materials.json', 'items/consumables.json', 'items/pet_books.json', 'items/keystone_items.json',
              'items/profession_recipes.json'):
        p = os.path.join(repo, f)
        s = open(p, encoding='utf-8', newline='').read()
        nl = '\r\n' if '\r\n' in s else '\n'
        ids = list(ID.finditer(s))
        out, last = [], 0
        for i, m in enumerate(ids):
            iid = m.group(1)
            end = ids[i + 1].start() if i + 1 < len(ids) else len(s)
            if iid not in new: continue
            seg = s[m.start():end]
            val = new[iid]
            if SP.search(seg):
                seg2 = SP.sub(f'"sell_price": {val}', seg, count=1)
            elif f != 'items/keystone_items.json':
                continue  # a reference (recipe ingredient), not the item itself
            else:
                lm = re.search(r'( *)"level_req": \d+,' + re.escape(nl), seg)
                assert lm, (f, iid)
                ins = f'{lm.group(1)}"sell_price": {val},{nl}'
                seg2 = seg[:lm.end()] + ins + seg[lm.end():]
            if seg2 != seg:
                changed += 1
            out.append(s[last:m.start()]); out.append(seg2); last = end
        out.append(s[last:])
        s2 = ''.join(out)
        if not check:
            open(p, 'w', encoding='utf-8', newline='').write(s2)
        # verify: every repriced id in this file now carries exactly its new price
        j = json.loads(s2)
        def walk(o):
            if isinstance(o, dict):
                if o.get('id') in new and 'sell_price' in o:
                    assert o.get('sell_price') == new[o['id']], (f, o['id'], o.get('sell_price'), new[o['id']])
                for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        if not check:
            walk(j)
    if check and changed:
        sys.exit(f'{changed} prix de revente pas a jour : python -I scripts/reprice_npc_resale.py')
    print(('a jour' if check else 'modifies'), changed, 'sur', len(new))
