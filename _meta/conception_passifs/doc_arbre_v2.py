"""Usage : python -I doc_arbre_v2.py   (depuis la racine de la base)
Rewrite the 4 proposed arm tables + bridges + mechanics list of ARBRE_PASSIFS_V2.md from arbre_v2.json."""
import json
import sys

root = sys.argv[1] if len(sys.argv) > 1 else '.'
t = json.load(open(root + '/_meta/conception_passifs/arbre_v2.json', encoding='utf-8'))
p = root + '/_meta/conception_passifs/ARBRE_PASSIFS_V2.md'
s = open(p, encoding='utf-8').read()

by_arm = {}
for n in t['nodes']:
    by_arm.setdefault(n['arm'], []).append(n)


def names(arm, kind):
    return [n for n in by_arm[arm] if n['kind'] == kind]


def opt(n):
    return f"*{n['name_fr']}* ({n['description_fr'].rstrip('.')})"


def smalls(arm, ids):
    return ', '.join(n['name_fr'] for n in by_arm[arm] if n['id'] in ids)


TITLES = {'defense': 'Défense', 'healing': 'Soin', 'support': 'Soutien', 'debuff': 'Affaiblissement'}
PFX = {'defense': 'def', 'healing': 'heal', 'support': 'sup', 'debuff': 'deb'}
out = []
for arm, title in TITLES.items():
    sm = [n for n in by_arm[arm] if n['kind'] == 'small']  # ordre du gabarit : e1-e4, ra, rb, rc, rd, m
    e, ra, rb, rc, rd, m = sm[0:4], sm[4:6], sm[6:8], sm[8:11], sm[11:14], sm[14:17]
    n15, n30, n50, mega = (names(arm, k) for k in ('notable_15', 'notable_30', 'notable_50', 'mega'))
    sides = names(arm, 'side')
    j = lambda lst: ', '.join(x['name_fr'] for x in lst)
    out.append(f'''## Bras {title} (proposition)

| Distance | Contenu |
|---|---|
| 0 → 12 | {j(e)} (flat, 3 rangs) |
| **15** | {' **ou** '.join(opt(x) for x in n15)}. Détour à 20 : {opt(sides[0])} |
| 15 → 30 | {j(ra)} ; ou {j(rb)} |
| **30** | 1 sur 3 : {', '.join(opt(x) for x in n30)} |
| 30 → 50 | {j(rc)} ; ou {j(rd)} |
| **50** | {' **ou** '.join(opt(x) for x in n50)}. Détour à 55 : {opt(sides[1])} |
| 50 → 75 | {j(m)} |
| **75 méga** | {' **ou** '.join(opt(x) for x in mega)} |

''')

bridges = [n for n in t['nodes'] if n['kind'] in ('bridge_small', 'hybrid')]
rows = []
for key, label in (('atk_def', 'Attaque ↔ Défense'), ('atk_deb', 'Attaque ↔ Affaiblissement'),
                   ('def_heal', 'Défense ↔ Soin'), ('heal_sup', 'Soin ↔ Soutien'), ('sup_deb', 'Soutien ↔ Affaiblissement')):
    g = {n['id']: n for n in bridges}
    pas = g[f'pt2_brg_{key}_a']['description_fr'].rstrip('.')
    rows.append(f"| {label} | {pas} | {opt(g[f'pt2_hyb_{key}'])} | {opt(g[f'pt2_hyb_{key}_side'])} |")
out.append('''## Ponts (les 5)

| Pont | Passage (×2, 1 pt) | Hybride sur le chemin | Hybride à côté |
|---|---|---|---|
''' + '\n'.join(rows) + '''

Ces tables sont **générées depuis `arbre_v2.json`** par `doc_arbre_v2.py` : modifier le contenu dans `gen_arbre_v2.py`,
relancer les deux scripts. Rendu en image : `python -I render_arbre_v2.py arbre_v2.json arbre_v2.png`.

''')

a = s.index('## Bras Défense (proposition)')
b = s.index('Les mécaniques de la V1 sont reprises')
s = s[:a] + ''.join(out) + s[b:]

i = s.index('- Pour les 4 bras proposés')  # rejouable : la ligne est reecrite a chaque passage
k = s.index('- Migration : rembourser', i)
s = s[:i] + '''- Pour les 4 bras proposés : **aucune mécanique entièrement nouvelle**, seulement 9 extensions d'une
  mécanique déjà codée (un paramètre, un événement ou une stat de plus), listées dans
  `arbre_v2.json` `_meta.new_mechanics`. Les notables sans effet spécial sont en stats (comme *Brute*).
''' + s[k:]
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
