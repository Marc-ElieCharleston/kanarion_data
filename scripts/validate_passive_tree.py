#!/usr/bin/env python3
"""
Validateur de l'arbre des passifs V2 (classes/passive_tree.json) — V1 le 2026-09-30, V2 le 2026-10-20.

L'arbre est un GRAPHE genere par _meta/conception_passifs/gen_arbre_v2.py. Une erreur de donnee
(arete vers un id disparu, notable a la mauvaise distance, mecanique que le combat ne sait pas jouer)
ne se voit qu'en jeu, apres un achat refuse ou un effet muet. Ce script la trouve avant le commit.

Ce qu'il verifie :
  1. structure : ids uniques prefixes pt_ / pt2_, sortes connues, champs FR/EN presents, icone, pos
  2. petits noeuds (small, bridge_small) : 1 a 5 rangs, uniquement des stats connues, jamais
     add_percent sur une stat `bonus_type: flat` ni sur une stat dont la base vaut 0
  3. autres noeuds : 1 rang, cout = rules.costs[sorte], effets = stats connues (value) et/ou
     mecaniques du catalogue `mechanics`, parametres exactement ceux du catalogue, et valeurs des
     parametres discriminants dans `variants` (= ce que le combat sait jouer : une mecanique ou une
     variante absente du catalogue est INTERDITE, elle serait muette en jeu)
  4. stacking « single » : une meme mecanique (meme variante) portee par un seul noeud de l'arbre,
     sinon le composant de combat ecraserait l'une par l'autre
  5. bras : chaque noeud de bras dans un bras declare ; ponts relies a deux bras VOISINS dans l'anneau
  6. aretes : extremites existantes, pas de boucle, pas de doublon, graphe connexe depuis le centre,
     chaque bras part du centre
  7. groupes de choix : au moins deux options, un seul bras, une seule sorte
  8. un groupe de mega par bras ; rules.mega_max present
  9. distances : chaque notable tombe a rules.depth_targets[sorte] points du centre (petits noeuds
     payes a leur rang max, regle « passage au rang max »)
 10. budget : l'arbre coute plus que rules.points.max_points (sinon aucun choix)
 11. textes : pas de tiret cadratin, pas de « Mana » (terminologie Souffle)

Exit 0 = tout va bien, exit 1 = erreurs.
"""

import heapq
import json
import os
import sys
from collections import defaultdict, deque

DB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREE = "classes/passive_tree.json"
SMALL = {"small", "bridge_small"}
NOTABLE = {"notable_15", "notable_30", "notable_50", "side", "hybrid", "mega"}
KINDS = {"center"} | SMALL | NOTABLE
BRIDGE = {"bridge_small", "hybrid"}
TEXT_FIELDS = ("name_fr", "name_en", "description_fr", "description_en")


def load(path):
    with open(path if os.path.isabs(path) else os.path.join(DB, path), encoding="utf-8") as f:
        return json.load(f)


def stat_info(defs):
    names, flat_only, zero_base = set(), set(), set()
    for cat in defs.get("stats", {}).values():
        if isinstance(cat, dict):
            for key, value in cat.items():
                if isinstance(value, dict) and ("name" in value or "name_en" in value):
                    names.add(key)
                    if value.get("bonus_type") == "flat":
                        flat_only.add(key)
                    if value.get("default") == 0:
                        zero_base.add(key)
    return names, flat_only, zero_base


def check_stat_effect(nid, e, small, stats, flat_only, zero_base, errors):
    stat, op = e.get("stat"), e.get("op")
    if stat not in stats:
        errors.append(f"{nid}: stat inconnue '{stat}'")
    if op not in ("add_flat", "add_percent"):
        errors.append(f"{nid}: op invalide '{op}'")
    if op == "add_percent" and stat in flat_only:
        errors.append(f"{nid}: add_percent sur '{stat}' (bonus_type flat)")
    elif op == "add_percent" and stat in zero_base:
        errors.append(f"{nid}: add_percent sur '{stat}' dont la base vaut 0 : le bonus vaut 0")
    key = "value_per_rank" if small else "value"
    v = e.get(key)
    if not isinstance(v, (int, float)) or v == 0:
        errors.append(f"{nid}: {key} absente ou nulle")
    elif small and v < 0:
        errors.append(f"{nid}: un petit noeud ne porte pas de malus")


def main():
    # Un chemin en argument remplace l'arbre du depot (tests du validateur).
    tree = load(sys.argv[1]) if len(sys.argv) > 1 else load(TREE)
    stats, flat_only, zero_base = stat_info(load("stats/definitions.json"))
    status_categories = set(load("stats/status_effects.json").get("categories", []))
    rules = tree["rules"]
    costs = rules["costs"]
    mechanics = tree["mechanics"]
    errors, warnings = [], []

    nodes = {}
    single_users = defaultdict(list)
    for n in tree["nodes"]:
        nid = n.get("id", "")
        if not (nid.startswith("pt_") or nid.startswith("pt2_")):
            errors.append(f"id '{nid}' ne commence pas par pt_ ou pt2_")
        if nid in nodes:
            errors.append(f"id '{nid}' en DOUBLE")
        nodes[nid] = n
        kind = n.get("kind")
        if kind not in KINDS:
            errors.append(f"{nid}: sorte inconnue '{kind}'")
            continue
        for field in TEXT_FIELDS:
            text = n.get(field, "")
            if not text:
                errors.append(f"{nid}: champ {field} vide")
            if "—" in text:
                errors.append(f"{nid}: tiret cadratin dans {field}")
            if "Mana" in text or "mana" in text:
                errors.append(f"{nid}: 'mana' dans {field} (dire Souffle / Breath)")
        if not n.get("icon"):
            errors.append(f"{nid}: pas d'icone")
        if not (isinstance(n.get("pos"), list) and len(n["pos"]) == 2):
            errors.append(f"{nid}: pos absente ou invalide")
        if kind == "center":
            continue

        if kind in SMALL:
            if not (isinstance(n.get("max_rank"), int) and 1 <= n["max_rank"] <= 5):
                errors.append(f"{nid}: max_rank {n.get('max_rank')} hors de 1..5")
            if "cost" in n:
                errors.append(f"{nid}: un petit noeud se paie au rang (rules.costs.small_per_rank), pas de champ cost")
            if not n.get("effects"):
                errors.append(f"{nid}: petit noeud sans effet")
            for e in n.get("effects", []):
                if "mechanic" in e:
                    errors.append(f"{nid}: un petit noeud ne porte pas de mecanique")
                    continue
                check_stat_effect(nid, e, True, stats, flat_only, zero_base, errors)
            continue

        if n.get("max_rank") != 1:
            errors.append(f"{nid}: notable avec max_rank {n.get('max_rank')}")
        if kind not in costs:
            errors.append(f"{nid}: rules.costs n'a pas de prix pour '{kind}'")
        elif n.get("cost") != costs[kind]:
            errors.append(f"{nid}: cout {n.get('cost')} != rules.costs.{kind} ({costs[kind]})")
        if not n.get("effects"):
            errors.append(f"{nid}: notable sans effet")
        for e in n.get("effects", []):
            if "stat" in e:
                check_stat_effect(nid, e, False, stats, flat_only, zero_base, errors)
                continue
            mech = e.get("mechanic")
            if mech not in mechanics:
                errors.append(f"{nid}: mecanique '{mech}' absente du catalogue (non branchee en combat)")
                continue
            spec = mechanics[mech]
            expected = spec["params"]
            params = e.get("params", {})
            if set(params) != set(expected):
                errors.append(f"{nid}: parametres {sorted(params)} != catalogue {sorted(expected)}")
            for pname, ptype in expected.items():
                if pname not in params:
                    continue
                value = params[pname]
                if ptype == "stat" and value not in stats:
                    errors.append(f"{nid}: parametre {pname} = stat inconnue '{value}'")
                if ptype == "status_category" and value not in status_categories:
                    errors.append(f"{nid}: categorie de statut inconnue '{value}'")
                if ptype in ("number", "int") and not isinstance(value, (int, float)):
                    errors.append(f"{nid}: parametre {pname} non numerique")
            variant = []
            for pname, allowed in spec.get("variants", {}).items():
                value = params.get(pname)
                if value not in allowed:
                    errors.append(f"{nid}: {mech}.{pname} = {value!r} : le combat ne sait jouer que {allowed}")
                variant.append(json.dumps(value))
            if "pairs" in spec and [params.get("event"), params.get("scope")] not in spec["pairs"]:
                errors.append(f"{nid}: {mech} event/scope {params.get('event')}/{params.get('scope')} non branche")
            if spec.get("stacking") == "single":
                single_users[(mech, tuple(variant))].append(nid)
            elif spec.get("stacking") not in ("additive", "max"):
                errors.append(f"catalogue {mech}: stacking '{spec.get('stacking')}' inconnu")

    for (mech, variant), users in single_users.items():
        if len(users) > 1:
            errors.append(f"{mech} {list(variant)} porte par {users} : le combat n'en garde qu'un (stacking single)")

    centers = [n for n in nodes.values() if n.get("kind") == "center"]
    if len(centers) != 1:
        errors.append(f"{len(centers)} centre(s) au lieu d'un seul")

    arm_ids = [a["id"] for a in tree["arms"]]
    ring = {aid: i for i, aid in enumerate(arm_ids)}

    def neighbours(a, b):
        i, j = sorted((ring[a], ring[b]))
        return j - i == 1 or (i == 0 and j == len(arm_ids) - 1)

    for n in nodes.values():
        kind = n.get("kind")
        if kind == "center":
            continue
        if kind in BRIDGE:
            arms = n.get("arms", [])
            if n.get("arm") is not None or len(arms) != 2 or any(a not in ring for a in arms):
                errors.append(f"{n['id']}: un pont porte arm=null et arms=[deux bras declares]")
            elif not neighbours(*arms):
                errors.append(f"{n['id']}: relie deux bras non voisins {arms}")
        elif n.get("arm") not in ring:
            errors.append(f"{n['id']}: bras inconnu '{n.get('arm')}'")

    # Aretes
    adj = defaultdict(set)
    seen = set()
    for a, b in tree["edges"]:
        if a not in nodes or b not in nodes:
            errors.append(f"arete {a} - {b} : extremite inconnue")
            continue
        if a == b:
            errors.append(f"arete en boucle sur {a}")
        key = tuple(sorted((a, b)))
        if key in seen:
            errors.append(f"arete en double {a} - {b}")
        seen.add(key)
        adj[a].add(b)
        adj[b].add(a)
    for n in nodes.values():  # un pont ne touche que ses deux bras (ou son propre pont)
        if n.get("kind") in BRIDGE and len(n.get("arms", [])) == 2:
            for x in adj[n["id"]]:
                o = nodes[x]
                if o.get("kind") in BRIDGE:
                    if sorted(o.get("arms", [])) != sorted(n["arms"]):
                        errors.append(f"{n['id']}: relie au pont d'autres bras ({x})")
                elif o.get("arm") not in n["arms"]:
                    errors.append(f"{n['id']}: relie a {x} hors de ses bras {n['arms']}")
    start = centers[0]["id"] if centers else None
    if start:
        reached, queue = {start}, deque([start])
        while queue:
            cur = queue.popleft()
            for nxt in adj[cur]:
                if nxt not in reached:
                    reached.add(nxt)
                    queue.append(nxt)
        for nid in nodes:
            if nid not in reached:
                errors.append(f"{nid}: inaccessible depuis le centre")
        for arm in arm_ids:
            if not any(nodes[x].get("arm") == arm for x in adj[start]):
                errors.append(f"bras {arm}: aucune arete depuis le centre")

    # Groupes de choix
    groups = defaultdict(list)
    for n in nodes.values():
        if "choice" in n:
            groups[n["choice"]["group"]].append(n)
    for group, members in groups.items():
        if len(members) < 2:
            errors.append(f"groupe de choix {group}: une seule option")
        if len({m.get("arm") for m in members}) != 1:
            errors.append(f"groupe de choix {group}: options dans plusieurs bras")
        if len({m.get("kind") for m in members}) != 1:
            errors.append(f"groupe de choix {group}: options de sortes differentes")
    if not isinstance(rules.get("mega_max"), int) or rules["mega_max"] < 1:
        errors.append("rules.mega_max absent")
    for arm in arm_ids:
        megas = [n for n in nodes.values() if n.get("kind") == "mega" and n.get("arm") == arm]
        if not megas:
            errors.append(f"bras {arm}: aucun mega")
        elif len({m.get("choice", {}).get("group") for m in megas}) != 1 or any("choice" not in m for m in megas):
            errors.append(f"bras {arm}: les megas doivent former un seul groupe de choix")

    # Distances (cout du chemin le moins cher, petits noeuds payes a leur rang max)
    def cost(n):
        if n.get("kind") in SMALL:
            return costs["small_per_rank"] * n["max_rank"]
        return n.get("cost", 0)

    if start:
        dist = {start: 0}
        heap = [(0, start)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist.get(u, 1 << 30):
                continue
            for v in adj[u]:
                if nodes[v].get("kind") in BRIDGE:
                    continue  # la distance d'un bras se mesure dans le bras
                nd = d + cost(nodes[v])
                if nd < dist.get(v, 1 << 30):
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))
        targets = rules.get("depth_targets", {})
        for n in nodes.values():
            want = targets.get(n.get("kind"))
            if want is not None and dist.get(n["id"]) != want:
                errors.append(f"{n['id']}: a {dist.get(n['id'])} pts du centre au lieu de {want}")

    budget = rules["points"]["max_points"]
    total = sum(cost(n) for n in nodes.values() if n.get("kind") != "center")
    if total <= budget:
        errors.append(f"arbre complet ({total} pts) <= budget ({budget}) : aucun choix")

    to_validate = [n["id"] for n in nodes.values() if n.get("to_validate")]
    notables = sum(1 for n in nodes.values() if n.get("kind") in NOTABLE)
    print(f"{len(nodes)} noeuds, {len(seen)} aretes, {len(arm_ids)} bras, {notables} notables")
    print(f"  arbre complet : {total} pts pour un budget de {budget}")
    print(f"  {len(to_validate)} noeud(s) marques to_validate (choix d'integration a faire valider)")
    for w in warnings:
        print(f"  [WARN] {w}")
    if errors:
        print(f"\n--- ERREURS ({len(errors)}) ---")
        for e in errors:
            print(f"  [ERROR] {e}")
        print(f"\nVALIDATION FAILED - {len(errors)} erreurs")
        return 1
    print("\nVALIDATION PASSED - 0 erreur")
    return 0


if __name__ == "__main__":
    sys.exit(main())
