"""Simulation de l'arbre des passifs V2 (modele a distance).

Les bras absents du fichier (cites par les ponts) sont clones depuis Attaque, pour tester la geometrie.
Si le fichier contient les 5 bras (arbre_v2.json), ce sont les vrais bras qui sont simules.
Un petit noeud coute tous ses rangs (il ne laisse passer qu'au rang max). Le cout d'un build est
celui de l'arbre de Steiner glouton qui relie le centre aux notables vises.
Usage : python -I sim_arbre_v2.py arbre_v2_attaque.json
"""
import heapq
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
tree = json.load(open(sys.argv[1], encoding="utf-8"))
rules = tree["rules"]
costs = rules["costs"]
budget = rules["points"]["max_points"]
NOTABLES = ("notable_15", "notable_30", "notable_50", "mega", "side", "hybrid")

nodes = {n["id"]: n for n in tree["nodes"]}
edges = [tuple(e) for e in tree["edges"]]
PREFIX_ARM = {"def": "defense", "deb": "debuff", "sup": "support"}
present = {n.get("arm") for n in tree["nodes"]}
for prefix in ("def", "deb", "sup"):
    if PREFIX_ARM[prefix] in present:
        continue  # vrai bras dans le fichier : pas de clone
    for n in tree["nodes"]:
        if n.get("arm") == "attack":
            c = dict(n, id=n["id"].replace("pt2_atk_", f"pt2_{prefix}_"), arm=prefix)
            if "choice" in n:
                c["choice"] = {"group": n["choice"]["group"] + "_" + prefix, "option": n["choice"]["option"]}
            nodes[c["id"]] = c
    for a, b in tree["edges"]:
        if (a.startswith("pt2_atk_") or a == "pt_center") and b.startswith("pt2_atk_"):
            edges.append((a.replace("pt2_atk_", f"pt2_{prefix}_"), b.replace("pt2_atk_", f"pt2_{prefix}_")))
adj = {k: set() for k in nodes}
for a, b in edges:
    if a in adj and b in adj:
        adj[a].add(b)
        adj[b].add(a)


def cost(n):
    if n["kind"] in ("small", "bridge_small"):
        return n["max_rank"] * costs["small_per_rank"]
    return costs.get(n["kind"], 0)


def blocked(n, owned, mega):
    if mega and n["kind"] in ("bridge_small", "hybrid"):
        return True
    ch = n.get("choice")
    return bool(ch) and any(nodes[o].get("choice", {}).get("group") == ch["group"] and o != n["id"] for o in owned)


def cheapest(owned, target, mega=False):
    """Chemin le moins cher depuis les noeuds acquis ; on peut traverser un notable deja acquis ou
    le payer pour passer (il est alors acquis aussi, et compte dans le cout)."""
    dist = {o: 0 for o in owned}
    prev = {}
    heap = [(0, o) for o in owned]
    while heap:
        d, u = heapq.heappop(heap)
        if u == target:
            path = []
            while u not in owned:
                path.append(u)
                u = prev[u]
            return d, path
        if d > dist.get(u, 1e9):
            continue
        for v in adj[u]:
            if v in owned or blocked(nodes[v], owned | {u}, mega):
                continue
            nd = d + cost(nodes[v])
            if nd < dist.get(v, 1e9):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    return None, None


def build(targets, mega=False):
    owned = {"pt_center"}
    total = 0
    for t in targets:
        if t in owned:
            continue
        d, path = cheapest(owned, t, mega)
        if d is None:
            return None
        total += d
        owned |= set(path)
    return total, owned


ARMS = [a["id"] for a in tree["arms"]]
print("== Profondeur des notables (cout du chemin depuis le centre, noeud compris) ==")
target = rules["depth_targets"]
for n in tree["nodes"]:
    if n["arm"] in ARMS and n["kind"] in NOTABLES:
        d, _ = cheapest({"pt_center"}, n["id"])
        want = target.get(n["kind"])
        flag = "" if want is None or d == want else f"  <- vise {want}"
        print(f"   {n['arm']:<8} {n['kind']:<11} {n['name_fr']:<28} {d:>3} pts{flag}")

N = lambda arm, key: f"pt2_{arm}_{key}"
if len(ARMS) == 5:
    # Vrais bras : on prend le 1er notable de chaque palier, le 2e mega, et les hybrides de chaque pont.
    first = lambda arm, kind, i=0: [n["id"] for n in tree["nodes"] if n["arm"] == arm and n["kind"] == kind][i]
    hyb = lambda a, b: [n["id"] for n in tree["nodes"] if n["kind"] == "hybrid" and set(n.get("arms", [])) == {a, b}]
    HYB_ATK = {"defense": ["pt2_hyb_atk_def", "pt2_hyb_atk_def_side"], "debuff": ["pt2_hyb_atk_deb", "pt2_hyb_atk_deb_side"]}
    def hybrids(a, b):
        if "attack" in (a, b):
            return HYB_ATK[b if a == "attack" else a]
        return hyb(a, b)
    scen = []
    for i, arm in enumerate(ARMS):
        scen.append((f"All-in {arm} (mega 2)", [first(arm, "mega", 1)], True))
        nxt = ARMS[(i + 1) % 5]
        scen.append((f"All-in {arm} + notable 15 de {nxt}", [first(arm, "mega", 1), first(nxt, "notable_15")], True))
        scen.append((f"All-in {arm} + notable 30 de {nxt} (doit echouer)", [first(arm, "mega", 1), first(nxt, "notable_30")], True))
        h = hybrids(arm, nxt)
        scen.append((f"Hybride voisin : {arm} 50 + {nxt} 50 + hybride", [first(arm, "notable_50"), h[0], first(nxt, "notable_50")], False))
        scen.append((f"Hybride voisin : {arm} 50 + {nxt} 50 + les 2 hybrides", [first(arm, "notable_50"), h[0], h[1], first(nxt, "notable_50")], False))
        far = ARMS[(i + 2) % 5]
        scen.append((f"Hybride eloigne : {arm} 50 + {far} 50", [first(arm, "notable_50"), first(far, "notable_50")], False))
    scen.append(("Hybride a 3 bras : defense 50 + healing 50 + support 30",
                 [first("defense", "notable_50"), hybrids("defense", "healing")[0], first("healing", "notable_50"),
                  hybrids("healing", "support")[0], first("support", "notable_30")], False))
scen = scen if len(ARMS) == 5 else [
    ("All-in Attaque (mega)", [N("atk", "mega_unleashed")], True),
    ("All-in + notable 15 du voisin", [N("atk", "mega_unleashed"), N("def", "execution")], True),
    ("All-in + notable 30 du voisin (doit echouer)", [N("atk", "mega_unleashed"), N("def", "killer_instinct")], True),
    ("Hybride eloigne : Attaque 50 + Soutien 50, pas de pont", [N("atk", "relentless"), N("sup", "relentless")], False),
    ("Hybride voisin : Attaque 50 + Defense 50 + Affaiblissement 30",
     [N("atk", "relentless"), "pt2_hyb_atk_def", N("def", "relentless"), "pt2_hyb_atk_deb", N("deb", "killer_instinct")], False),
    ("Hybride voisin : Attaque 50 + Defense 50 + les 2 hybrides du pont",
     [N("atk", "relentless"), "pt2_hyb_atk_def", "pt2_hyb_atk_def_side", N("def", "relentless")], False),
]
print(f"\n== Builds avec {budget} points ==")
for label, targets, mega in scen:
    r = build(targets, mega)
    if r is None:
        print(f"   {label} : impossible (chemin ferme)")
        continue
    total, owned = r
    notables = sorted(nodes[o]["name_fr"] + f" ({nodes[o]['arm'] or 'pont'})" for o in owned if nodes[o]["kind"] in NOTABLES)
    verdict = "OK" if total <= budget else "TROP CHER"
    print(f"   {label} : {total} pts -> {verdict}, reste {budget - total}")
    print(f"      notables : {', '.join(notables)}")
