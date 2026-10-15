"""Simulation de l'arbre des passifs V2 (brouillon).

Verifie, pour chaque bras du fichier : que chaque seuil de palier est atteignable quelle que soit la
combinaison de choix, le cout d'un all-in (capstone), la marge laissee, et que all-in et hybride
s'excluent avec le budget de points. Usage : python -I sim_arbre_v2.py arbre_v2_attaque.json
"""
import itertools
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
tree = json.load(open(sys.argv[1], encoding="utf-8"))
rules = tree["rules"]
costs = rules["costs"]
gates = rules["tier_gates"]
budget = rules["points"]["max_points"]
hyb_req = rules["hybrid"]["requires_points_in_each_arm"]
TIERS = [0, 1, 2, 3]


def cost(node):
    if node["kind"] == "small":
        return node["max_rank"] * costs["small_per_rank"]
    return costs[node["kind"]]


def min_cost(node):
    return costs["small_per_rank"] if node["kind"] == "small" else costs[node["kind"]]


for arm in tree["arms"]:
    nodes = [n for n in tree["nodes"] if n["arm"] == arm["id"]]
    groups = {}
    for n in nodes:
        if "choice" in n:
            groups.setdefault(n["choice"]["group"], set()).add(n["choice"]["option"])
    names = sorted(groups)
    combos = list(itertools.product(*(sorted(groups[g]) for g in names)))
    print(f"== Bras {arm['name_fr']} : {len(nodes)} noeuds, groupes de choix "
          + ", ".join(f"{g} ({len(groups[g])})" for g in names))
    print(f"   Variantes all-in (une option par groupe) : {len(combos)}")
    worst = None
    for combo in combos:
        pick = dict(zip(names, combo))
        keep = [n for n in nodes if "choice" not in n or pick[n["choice"]["group"]] == n["choice"]["option"]]
        by_tier = {t: sum(cost(n) for n in keep if n["tier"] == t) for t in TIERS}
        ok = True
        avail = 0
        for t in TIERS:
            if avail < gates[str(t)]:
                ok = False
                print(f"   !! {pick} : palier {t} inatteignable ({avail} < {gates[str(t)]})")
            avail += by_tier[t]
        pre_cap = avail
        if pre_cap < gates["capstone"]:
            ok = False
            print(f"   !! {pick} : capstone inatteignable ({pre_cap} < {gates['capstone']})")
        slack = pre_cap - gates["capstone"]
        if worst is None or slack < worst[0]:
            worst = (slack, pick, pre_cap)
    pre_cap = worst[2]
    allin_min = gates["capstone"] + costs["capstone"]
    print(f"   Bras complet hors capstone (chemin choisi) : {pre_cap} pts, seuil capstone {gates['capstone']}"
          f" -> marge {worst[0]} pts (pire combinaison)")
    print(f"   All-in : {allin_min} a {pre_cap + costs['capstone']} pts, reste {budget - allin_min} pts maximum pour le reste")
    print(f"   All-in + hybride : {allin_min} + {hyb_req} + {costs['hybrid']} = {allin_min + hyb_req + costs['hybrid']}"
          f" -> {'IMPOSSIBLE' if allin_min + hyb_req + costs['hybrid'] > budget else 'POSSIBLE (!)'} avec {budget} pts")
    big = [n for n in nodes if n["kind"] in ("medium", "large")]
    print("   Ce qu'on peut viser par profondeur investie :")
    for pts in (12, 25, 42, 62):
        reach = [t for t in TIERS if gates[str(t)] <= pts]
        print(f"     {pts:>2} pts : paliers {reach}, gros/moyens accessibles : "
              + ", ".join(sorted({n['name_fr'] for n in big if n['tier'] in reach and gates[str(n['tier'])] + min_cost(n) <= pts})))

print("\n== Formes hybrides (si les 5 bras ont le meme gabarit) ==")
h = costs["hybrid"]
for label, arms_pts, n_hyb in (("2 bras", [42, 42], 2), ("3 bras", [25, 30, 25], 2), ("2 bras + 1 entree", [36, 36], 2)):
    total = sum(arms_pts) + n_hyb * h
    print(f"   {label} : bras {arms_pts} + {n_hyb} hybride(s) = {total} pts -> {'OK' if total <= budget else 'trop cher'}, reste {budget - total}")
