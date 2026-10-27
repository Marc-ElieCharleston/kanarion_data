"""Souffle des compagnons (mercenaires + familiers), decision Charleston 2026-10-27.

Usage : python scripts/balance/companion_breath.py [racine_data] [new]
Sans 'new' : modele 0.20.18 (regen de classe plate, cout x1) applique aux couts actuels.
Avec 'new' : lit mp_regen_base / mp_regen_per_level / souffle_cost_multiplier des profils
(config/mercenary_balance.json solo_helper_v1, config/familiar_balance.json familiar_v1).

Rotation au plafond (comme _meta/carnet/souffle_par_niveau.md) : a chaque GCD, le sort pret
et payable le plus cher. Depart plein, fenetre 600 s. Mercenaires : mediane des 6 kits de base
et des 24 kits de sous-classe (niveau joueur - 2, GCD 2 s, Souffle max classe x mp_multiplier).
Familiers : mediane par role, signature + sorts tires du role (2/3/4 emplacements aux niveaux
10/30/60, comme le loadout_roller), GCD 3 s, Souffle max median des familiers du role.
'a sec' = premier GCD ou un sort pret n'est plus payable. pack/elite = durees de reference du
carnet (niveaux 10 et 30 interpoles)."""
import json, glob, os, sys, statistics, itertools, random
R = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != 'new' else '.'
NEW = 'new' in sys.argv[1:]
def J(p): return json.load(open(os.path.join(R, p), encoding='utf-8'))
sk = {}
def walk(o):
    if isinstance(o, dict):
        if 'id' in o and 'mana_cost' in o and 'cooldown' in o: sk[o['id']] = o
        for x in o.values(): walk(x)
    elif isinstance(o, list):
        for x in o: walk(x)
for f in glob.glob(os.path.join(R, 'classes', '*', 'skills.json')) + glob.glob(os.path.join(R, 'classes', '*', '*', 'skills.json')):
    walk(J(f))
base = J('stats/class_base_stats.json'); gr = J('stats/class_growth.json')
mbal = J('config/mercenary_balance.json')['profiles']['solo_helper_v1']
fbal = J('config/familiar_balance.json')['profiles']['familiar_v1']
GCD_M = J('config/combat.json')['settings']['gcd_duration']
GCD_F = J('config/combat.json')['settings']['familiar_gcd_duration']
REF = {10: (30, 50), 30: (63, 105), 60: (98, 164)}  # pack / elite seconds (carnet, L10/L30 interpolated)

def cost_of(s, mult):
    c = sk[s]['mana_cost']
    if c <= 0: return 0
    return max(1, int(round(c * mult)))

def sim(mp, regen, kit, gcd, mult, T=600, inf=False, start=None):
    cd = {s: 0.0 for s in kit}; t = 0.0; cur = float(mp if start is None else start)
    dry = None; casts = 0; spent = 0
    while t < T:
        ready = [s for s in kit if cd[s] <= t]
        aff = [s for s in ready if cost_of(s, mult) <= cur or inf]
        if not aff:
            if dry is None and ready: dry = t
        else:
            s = max(aff, key=lambda s: cost_of(s, mult)); c = cost_of(s, mult)
            if not inf: cur -= c
            spent += c
            cd[s] = t + sk[s]['cooldown'] + (sk[s].get('cast_time') or 0); casts += 1
        t += gcd
        cur = min(mp, cur + regen * gcd)
    return dry, casts, spent / T

def regen_at(prof, lvl, legacy):
    if NEW and 'mp_regen_base' in prof:
        return prof['mp_regen_base'] + prof.get('mp_regen_per_level', 0) * (lvl - 1)
    return legacy

rows = []
M = J('entities/mercenaries.json')['mercenaries']
mm = mbal.get('souffle_cost_multiplier', 1.0) if NEW else 1.0
for group, archs in (('merc base', [a for a in M if not a.get('subclass_id')]), ('merc subclass', [a for a in M if a.get('subclass_id')])):
    for L in (10, 30, 60):
        ml = max(1, L + mbal['level_offset'])
        res = []
        for a in archs:
            c = a['class_id']
            kit = [s for s in a['skill_loadout'] if s in sk and not sk[s].get('movement')]
            mp = int(round((base[c]['mp'] + gr[c]['mp'] * (ml - 1)) * mbal['mp_multiplier']))
            rg = regen_at(mbal, ml, base[c]['mp_regen'])
            d, n, _ = sim(mp, rg, kit, GCD_M, mm)
            _, _, spend = sim(mp, rg, kit, GCD_M, mm, inf=True)
            res.append((mp, rg, spend, d if d is not None else 9999, n))
        med = lambda i: statistics.median(r[i] for r in res)
        rows.append((group, L, med(0), med(1), med(2), med(3), med(4), min(r[3] for r in res), max(r[3] for r in res)))

F = J('entities/familiars.json')['familiars']
slots = {10: 2, 30: 3, 60: 4}
for role in ('attaque', 'tank', 'heal', 'utilitaire'):
    fs = [f for f in F if f['role'] == role and 'base_stats' in f and 'growth' in f]
    bm = statistics.median(f['base_stats']['mp'] for f in fs); g = statistics.median(f['growth']['mp'] for f in fs)
    pool = [s['id'] for s in sk.values() if s['id'].startswith('skill_familiar_') and s.get('role') == role]
    sig = 'skill_familiar_sig_bite_bleed'
    for L in (10, 30, 60):
        mp = int(round((bm + g * (L - 1)) * fbal['mp_multiplier']))
        rg = regen_at(fbal, L, 1.0)
        combos = list(itertools.combinations(pool, slots[L] - 1))
        random.seed(7)
        if len(combos) > 600: combos = random.sample(combos, 600)
        res = []
        for cmb in combos:
            kit = [sig] + list(cmb)
            d, n, _ = sim(mp, rg, kit, GCD_F, 1.0)
            _, _, spend = sim(mp, rg, kit, GCD_F, 1.0, inf=True)
            res.append((spend, d if d is not None else 9999, n))
        med = lambda i: statistics.median(r[i] for r in res)
        rows.append(('familiar ' + role, L, mp, rg, med(0), med(1), med(2), min(r[1] for r in res), max(r[1] for r in res)))

print('%-20s %3s %6s %6s %7s %6s %8s %6s %10s' % ('kit', 'lvl', 'maxB', 'regen', 'spend/s', 'ratio', 'empty_s', 'casts', 'empty min-max'))
for r in rows:
    g, L, mp, rg, sp, d, n, dmin, dmax = r
    fmt = lambda x: 'never' if x >= 9999 else '%d' % x
    print('%-20s %3d %6d %6.2f %7.2f %6.2f %8s %6d %5s-%-5s pack/elite=%s' % (g, L, mp, rg, sp, sp / rg if rg else 0, fmt(d), n, fmt(dmin), fmt(dmax), REF[L]))
