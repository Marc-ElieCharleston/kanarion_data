"""Usage : python -I _meta/conception_passifs/doc_arbre_v2.py   (depuis la racine de la base)
Reecrit, dans ARBRE_PASSIFS_V2.md, la section entre les marqueurs CONTENU-DEBUT / CONTENU-FIN depuis
classes/passive_tree.json (6 bras, 6 ponts, noeuds a valider). Rejouable."""
import json
import sys

root = sys.argv[1] if len(sys.argv) > 1 else '.'
t = json.load(open(root + '/classes/passive_tree.json', encoding='utf-8'))
p = root + '/_meta/conception_passifs/ARBRE_PASSIFS_V2.md'
s = open(p, encoding='utf-8').read()
BEGIN, END = '<!-- CONTENU-DEBUT (genere par doc_arbre_v2.py) -->', '<!-- CONTENU-FIN -->'

by_arm = {}
for n in t['nodes']:
    by_arm.setdefault(n['arm'], []).append(n)


def opt(n):
    flag = ' ⚠ à valider' if n.get('to_validate') else ''
    return f"*{n['name_fr']}* ({n['description_fr'].rstrip('.')}){flag}"


def kind(arm, k):
    return [n for n in by_arm[arm] if n['kind'] == k]


out = [BEGIN, '']
for arm in t['arms']:
    a = arm['id']
    sm = [n for n in by_arm[a] if n['kind'] == 'small' and len(t['edges']) and not n['id'].split('_', 2)[2].startswith('seed_')]
    seeds = [n for n in by_arm[a] if n['kind'] == 'small' and n['id'].split('_', 2)[2].startswith('seed_')]
    e, ra, rb, rc, rd, m = sm[0:4], sm[4:6], sm[6:8], sm[8:11], sm[11:14], sm[14:17]
    j = lambda lst: ', '.join(f"{x['name_fr']} ({x['description_fr'].rstrip('.')})" for x in lst)
    sides = kind(a, 'side')
    seed_txt = f"\n| Graine (feuille du centre) | {j(seeds)} ⚠ à valider |" if seeds else ''
    out.append(f'''## Bras {arm['name_fr']}

| Distance | Contenu |
|---|---|{seed_txt}
| 0 → 12 | {j(e)} |
| **15** | {' **ou** '.join(opt(x) for x in kind(a, 'notable_15'))}. Détour à 20 : {opt(sides[0])} |
| 15 → 30 | {j(ra)} ; ou {j(rb)} |
| **30** | 1 sur 3 : {', '.join(opt(x) for x in kind(a, 'notable_30'))} |
| 30 → 50 | {j(rc)} ; ou {j(rd)} |
| **50** | {' **ou** '.join(opt(x) for x in kind(a, 'notable_50'))}. Détour à 55 : {opt(sides[1])} |
| 50 → 75 | {j(m)} |
| **75 méga** | {' **ou** '.join(opt(x) for x in kind(a, 'mega'))} |
''')

names = {a['id']: a['name_fr'] for a in t['arms']}
hybrids = [n for n in t['nodes'] if n['kind'] == 'hybrid' and not n['id'].endswith('_side')]
rows = []
g = {n['id']: n for n in t['nodes']}
for h in hybrids:
    key = h['id'][len('pt2_hyb_'):]
    a, b = h['arms']
    pas = g[f'pt2_brg_{key}_a']['description_fr'].rstrip('.')
    rows.append(f"| {names[a]} ↔ {names[b]} | {pas} | {opt(h)} | {opt(g[h['id'] + '_side'])} |")
out.append(f'''## Ponts (les {len(rows)})

| Pont | Passage (×2, 1 pt) | Hybride sur le chemin | Hybride à côté |
|---|---|---|---|
''' + '\n'.join(rows) + '''

## Noeuds à valider

''')
for n in t['nodes']:
    if n.get('to_validate'):
        planned = f" Prévu par la V2 : {n['v2_planned']}." if n.get('v2_planned') else ''
        out.append(f"- `{n['id']}` *{n['name_fr']}* : {n['to_validate']}.{planned}\n")
out.append('\n' + END)

a = s.index(BEGIN)
b = s.index(END) + len(END)
s = s[:a] + '\n'.join(out) if False else s[:a] + ''.join(x if x.endswith('\n') else x + '\n' for x in out).rstrip('\n') + s[b:]
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
