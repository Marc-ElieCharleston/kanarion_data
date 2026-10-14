"""Cuit les prix de revente PNJ (systems/npc_resale.json) dans le sell_price de chaque objet.

Materiaux (selon le niveau du monstre le plus bas qui les lache), pierres de forge,
potions / nourriture / gemmes de boutique, livres de familier, empreintes, stigmates.
L equipement n est PAS cuit : le serveur le calcule a la vente (bloc `equipment`).
Garde le formatage des fichiers. A relancer apres ajout de monstres ou de materiaux.

Usage (racine du depot) : python -I scripts/reprice_npc_resale.py [--check]
  --check : n ecrit rien, sort en erreur si un prix n est pas a jour (CI / pre-commit).

Aucune valeur de secours : un champ absent, une table de loot introuvable, un materiau
sans niveau ou un point fixe qui ne converge pas arretent le script.
"""
import json, re, sys, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Fichiers dont le script ecrit le sell_price. Les recettes y sont : leur objet fabrique
# peut etre plafonne. keystone_items est le seul a ne pas toujours porter de sell_price.
PRICED_FILES = ('items/materials.json', 'items/consumables.json', 'items/pet_books.json',
                'items/keystone_items.json', 'items/profession_recipes.json')
INSERT_IF_MISSING = 'items/keystone_items.json'
# Prix deja en place lus pour le plafond des objets fabriques (ingredients non recalcules ici).
PRICE_SOURCES = PRICED_FILES + ('items/koro_cards.json',)
FIXPOINT_MAX = 50


def load(db, f):
    with open(os.path.join(db, f), encoding='utf-8') as fh:
        return json.load(fh)


def g(L, c):
    """Courbe de l or des monstres, lue dans config/rewards.json base_gold."""
    return c['curve_base'] + c['curve_coef'] * max(1, L) ** c['curve_exponent']


def loot_table_of(m, tables):
    """Meme resolution que le serveur et validate_cross_references : loot_table_id, sinon
    l id sans mob_ / boss_. Plus de table `default` (2026-10-13) : introuvable = erreur."""
    k = m.get('loot_table_id')
    if k:
        if k not in tables:
            sys.exit(f'{m["id"]} : loot_table_id {k} introuvable')
        return k
    s = m['id'].removeprefix('mob_').removeprefix('boss_')
    if s not in tables:
        sys.exit(f'{m["id"]} : aucune table de loot ({s})')
    return s


def material_levels(db):
    """item_id -> niveaux des monstres qui le lachent (tables de loot), et id de monstre ->
    niveau (pour le champ `sources` des materiaux)."""
    tables = load(db, 'items/loot_tables.json')['monster_loot_tables']
    mons = load(db, 'entities/monsters.json')['monsters']
    lv = collections.defaultdict(list)
    for m in mons:
        for d in tables[loot_table_of(m, tables)]:
            lv[d['item_id']].append(m['base_level'])
    return lv, {m['id']: m['base_level'] for m in mons}


def compute(db):
    R = load(db, 'systems/npc_resale.json')
    curve = load(db, 'config/rewards.json')['base_gold']
    lv, level_of = material_levels(db)
    no_drop = {k: v for k, v in R['materials']['no_drop_level'].items() if not k.startswith('_')}
    out = {}
    mat = load(db, 'items/materials.json')
    nolvl = []
    for b in ('common', 'uncommon', 'rare'):
        k = R['materials'][b]
        for x in mat[b]:
            # Niveau : tables de loot, sinon les monstres declares dans `sources`.
            levels = lv.get(x['id']) or [level_of[m] for m in x.get('sources', []) if m in level_of]
            if levels:
                if x['id'] in no_drop:
                    sys.exit(f'{x["id"]} a un monstre source : le retirer de materials.no_drop_level')
                lvl = min(levels)
            elif x['id'] in no_drop:
                lvl = no_drop[x['id']]
            else:
                nolvl.append(x['id'])
                continue
            out[x['id']] = max(k['min'], round(k['factor'] * g(lvl, curve)))
    for x in mat['enhancement_stones']:
        out[x['id']] = R['enhancement_stones'][x['stone_rank']]
    ratio = R['shop_items']['sell_ratio_of_buy']
    for x in mat['gems']:
        if x.get('buy_price'):  # seules les gemmes vendues en boutique ont un prix d achat
            out[x['id']] = max(1, round(ratio * x['buy_price']))
    c = load(db, 'items/consumables.json')
    for b in ('potions', 'food'):
        for x in c[b]:
            if x.get('buy_price'):
                out[x['id']] = max(1, round(ratio * x['buy_price']))
    for x in c['familiar_traces']:
        out[x['id']] = R['familiar_traces'][x['trace_rarity']]
    for x in load(db, 'items/pet_books.json')['pet_books']:
        if x.get('buy_price'):
            out[x['id']] = max(1, round(R['pet_books']['sell_ratio_of_buy'] * x['buy_price']))
    for x in load(db, 'items/keystone_items.json')['keystone_items']:
        out[x['id']] = R['keystones'][x['rank']]
    # Fabrication (profession_recipes.json) : un objet fabrique ne se revend JAMAIS plus
    # que cap_of_inputs x (or de la recette + revente des ingredients) / quantite.
    # Ne fait que baisser. Point fixe : un ingredient peut lui-meme etre fabrique.
    cap = R['crafted']['cap_of_inputs']
    price = {}
    for f in PRICE_SOURCES:
        for o in walk(load(db, f)):
            if 'id' in o and isinstance(o.get('sell_price'), int):
                price[o['id']] = o['sell_price']
    price.update(out)
    recipes = load(db, 'items/profession_recipes.json')['recipes']
    for _ in range(FIXPOINT_MAX):
        moved = False
        for r in recipes:
            o = r['output_item']
            if o not in price or price[o] <= 0:
                continue  # pas de prix = pas revendable, rien a plafonner
            mats = r['materials']
            if any(m['id'] not in price for m in mats):
                continue  # ingredient sans prix (equipement, monnaie) : pas de plafond calculable
            inputs = r['gold_cost'] + sum(price[m['id']] * m['qty'] for m in mats)
            ceiling = max(1, int(cap * inputs / r['output_qty']))
            if price[o] > ceiling:
                price[o] = ceiling; out[o] = ceiling; moved = True
        if not moved:
            break
    else:
        sys.exit(f'plafond des objets fabriques : pas de point fixe en {FIXPOINT_MAX} passes (recette circulaire ?)')
    return out, nolvl


def walk(o):
    """Tous les objets JSON (dict) d un document, en profondeur."""
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


ID = re.compile(r'"id": "([^"]+)"')
SP = re.compile(r'"sell_price": -?\d+')


def rewrite(f, s, new):
    """Remplace le sell_price de chaque objet de `new` dans le texte `s`, formatage garde.
    Un segment va d un "id" au suivant ; un id sans sell_price dans son segment est une
    reference (ingredient de recette), sauf dans INSERT_IF_MISSING ou on l insere."""
    nl = '\r\n' if '\r\n' in s else '\n'
    ids = list(ID.finditer(s))
    parts, last, changed = [], 0, 0
    for i, m in enumerate(ids):
        iid = m.group(1)
        if iid not in new:
            continue
        end = ids[i + 1].start() if i + 1 < len(ids) else len(s)
        seg = s[m.start():end]
        val = new[iid]
        if SP.search(seg):
            seg2 = SP.sub(f'"sell_price": {val}', seg, count=1)
        elif f == INSERT_IF_MISSING:
            lm = re.search(r'( *)"level_req": \d+,' + re.escape(nl), seg)
            if not lm:
                sys.exit(f'{f} {iid} : ni sell_price ni level_req pour l inserer')
            seg2 = seg[:lm.end()] + f'{lm.group(1)}"sell_price": {val},{nl}' + seg[lm.end():]
        else:
            continue
        changed += seg2 != seg
        parts += [s[last:m.start()], seg2]
        last = end
    parts.append(s[last:])
    return ''.join(parts), changed


def verify(f, text, new):
    """Le texte reecrit est du JSON valide et chaque objet repris porte exactement son prix."""
    for o in walk(json.loads(text)):
        if o.get('id') in new and 'sell_price' in o and o['sell_price'] != new[o['id']]:
            sys.exit(f'{f} {o["id"]} : sell_price {o["sell_price"]} au lieu de {new[o["id"]]}')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    check = '--check' in sys.argv
    new, nolvl = compute(ROOT)
    if nolvl:
        sys.exit('sans niveau (aucun monstre ne les lache, absents de materials.no_drop_level) : '
                 + ', '.join(nolvl))
    changed = 0
    for f in PRICED_FILES:
        p = os.path.join(ROOT, f)
        with open(p, encoding='utf-8', newline='') as fh:
            s = fh.read()
        s2, n = rewrite(f, s, new)
        verify(f, s2, new)
        changed += n
        if not check and s2 != s:
            with open(p, 'w', encoding='utf-8', newline='') as fh:
                fh.write(s2)
    if check and changed:
        sys.exit(f'{changed} prix de revente pas a jour : python -I scripts/reprice_npc_resale.py')
    print(('a jour' if check else 'modifies'), changed, 'sur', len(new))


if __name__ == '__main__':
    main()
