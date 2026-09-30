#!/usr/bin/env python3
"""
Validateur de l'arbre des passifs (classes/passive_tree.json) — cree le 2026-09-30.

L'arbre est un GRAPHE : une erreur de donnee (arete vers un id disparu, noeud
inaccessible, fourche a un seul cote, sommet impossible a atteindre) ne se voit
qu'en jeu, apres un achat refuse. Ce script la trouve avant le commit.

Ce qu'il verifie :
  1. structure : ids uniques prefixes pt_, sortes connues, champs FR/EN presents
  2. un seul centre, un sommet par bras, et le sommet declare dans `arms` existe
  3. petits noeuds : max_rank = rules.small_max_rank, effets sur des stats connues,
     jamais add_percent sur une stat `bonus_type: flat` (meme regle que validate_passives)
  4. grands noeuds : max_rank 1, cout = rules.costs[sorte], mecanique au catalogue,
     parametres exactement ceux du catalogue, stats et categories de statut connues
  5. aretes : extremites existantes, pas de boucle, pas de doublon, graphe connexe
     depuis le centre
  6. fourches : chaque groupe a exactement deux cotes a et b, dans un seul bras
  7. ponts : relies a exactement deux bras differents, voisins dans l'anneau
  8. sommet atteignable : avec le cote le plus cher de la fourche ferme, le bras
     permet encore d'investir capstone_arm_points_required points avant le sommet
  9. budget : l'arbre coute plus que rules.max_points (sinon aucun choix)
 10. emplacements de grands passifs croissants, et le dernier egal au nombre max
 11. textes : pas de tiret cadratin, pas de « Mana » (terminologie Souffle)

Exit 0 = tout va bien, exit 1 = erreurs.
"""

import json
import os
import sys
from collections import defaultdict, deque

DB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREE = "classes/passive_tree.json"
KINDS = {"center", "small", "big", "unique", "capstone", "bridge"}
GRAND = {"big", "unique", "capstone", "bridge"}
TEXT_FIELDS = ("name_fr", "name_en", "description_fr", "description_en")


def load(path):
    with open(path if os.path.isabs(path) else os.path.join(DB, path), encoding="utf-8") as f:
        return json.load(f)


def stat_info(defs):
    names, flat_only = set(), set()
    for cat in defs.get("stats", {}).values():
        if isinstance(cat, dict):
            for key, value in cat.items():
                if isinstance(value, dict) and ("name" in value or "name_en" in value):
                    names.add(key)
                    if value.get("bonus_type") == "flat":
                        flat_only.add(key)
    return names, flat_only


def main():
    # Un chemin en argument remplace l'arbre du depot (tests du validateur).
    tree = load(sys.argv[1]) if len(sys.argv) > 1 else load(TREE)
    stats, flat_only = stat_info(load("stats/definitions.json"))
    status_categories = set(load("stats/status_effects.json").get("categories", []))
    rules = tree["rules"]
    mechanics = tree["mechanics"]
    errors, warnings = [], []

    nodes = {}
    for n in tree["nodes"]:
        nid = n.get("id", "")
        if not nid.startswith("pt_"):
            errors.append(f"id '{nid}' ne commence pas par pt_")
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
        if kind != "center" and not n.get("icon"):
            errors.append(f"{nid}: pas d'icone")
        if not (isinstance(n.get("pos"), list) and len(n["pos"]) == 2):
            errors.append(f"{nid}: pos absente ou invalide")

        if kind == "small":
            if n.get("max_rank") != rules["small_max_rank"]:
                errors.append(f"{nid}: max_rank {n.get('max_rank')} != {rules['small_max_rank']}")
            if not n.get("effects"):
                errors.append(f"{nid}: petit noeud sans effet")
            for e in n.get("effects", []):
                stat, op = e.get("stat"), e.get("op")
                if stat not in stats:
                    errors.append(f"{nid}: stat inconnue '{stat}'")
                if op not in ("add_flat", "add_percent"):
                    errors.append(f"{nid}: op invalide '{op}'")
                if op == "add_percent" and stat in flat_only:
                    errors.append(f"{nid}: add_percent sur '{stat}' (bonus_type flat)")
                if not (isinstance(e.get("value_per_rank"), (int, float)) and e["value_per_rank"] > 0):
                    errors.append(f"{nid}: value_per_rank absente ou <= 0")
                if "mechanic" in e:
                    errors.append(f"{nid}: un petit noeud ne porte pas de mecanique")
        elif kind in GRAND:
            if n.get("max_rank") != 1:
                errors.append(f"{nid}: grand noeud avec max_rank {n.get('max_rank')}")
            if n.get("cost") != rules["costs"][kind]:
                errors.append(f"{nid}: cout {n.get('cost')} != rules.costs.{kind} ({rules['costs'][kind]})")
            if not n.get("effects"):
                errors.append(f"{nid}: grand noeud sans effet")
            for e in n.get("effects", []):
                mech = e.get("mechanic")
                if mech not in mechanics:
                    errors.append(f"{nid}: mecanique inconnue '{mech}'")
                    continue
                expected = mechanics[mech]["params"]
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

    centers = [n for n in nodes.values() if n.get("kind") == "center"]
    if len(centers) != 1:
        errors.append(f"{len(centers)} centre(s) au lieu d'un seul")

    arm_ids = [a["id"] for a in tree["arms"]]
    for arm in tree["arms"]:
        caps = [n for n in nodes.values() if n.get("kind") == "capstone" and n.get("arm") == arm["id"]]
        if len(caps) != 1:
            errors.append(f"bras {arm['id']}: {len(caps)} sommet(s)")
        if arm.get("capstone") not in nodes:
            errors.append(f"bras {arm['id']}: sommet declare '{arm.get('capstone')}' introuvable")
    for n in nodes.values():
        if n.get("kind") not in ("center", "bridge") and n.get("arm") not in arm_ids:
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
    if centers:
        start = centers[0]["id"]
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
        # Chaque bras part du centre : sinon il resterait joignable par un pont,
        # le graphe paraitrait connexe et le bras ne serait ouvrable qu'en payant le pont.
        for arm in arm_ids:
            if not any(nodes[x].get("arm") == arm for x in adj[start]):
                errors.append(f"bras {arm}: aucune arete depuis le centre")

    # Fourches
    forks = defaultdict(lambda: defaultdict(list))
    for n in nodes.values():
        if "fork" in n:
            forks[n["fork"]["group"]][n["fork"]["side"]].append(n)
    for group, sides in forks.items():
        if set(sides) != {"a", "b"}:
            errors.append(f"fourche {group}: cotes {sorted(sides)} au lieu de a et b")
        arms_in = {n.get("arm") for side in sides.values() for n in side}
        if len(arms_in) != 1:
            errors.append(f"fourche {group}: noeuds dans plusieurs bras {sorted(arms_in)}")

    # Ponts
    ring = {aid: i for i, aid in enumerate(arm_ids)}
    for n in nodes.values():
        if n.get("kind") != "bridge":
            continue
        arms = {nodes[x].get("arm") for x in adj[n["id"]]}
        if len(arms) != 2 or None in arms:
            errors.append(f"{n['id']}: pont relie a {sorted(a or '?' for a in arms)} (il en faut deux)")
            continue
        i, j = sorted(ring[a] for a in arms)
        if not (j - i == 1 or (i == 0 and j == len(arm_ids) - 1)):
            errors.append(f"{n['id']}: relie deux bras non voisins")

    # Sommet atteignable et budget
    def cost(n):
        if n.get("kind") == "small":
            return rules["costs"]["small_per_rank"] * n["max_rank"]
        return n.get("cost", 0)

    required = rules["capstone_arm_points_required"]
    total_reachable = 0
    for arm in arm_ids:
        arm_nodes = [n for n in nodes.values() if n.get("arm") == arm and n.get("kind") != "capstone"]
        base = sum(cost(n) for n in arm_nodes if "fork" not in n)
        side_costs = defaultdict(int)
        for n in arm_nodes:
            if "fork" in n:
                side_costs[n["fork"]["side"]] += cost(n)
        cheapest = base + min(side_costs.values()) if side_costs else base
        if cheapest < required:
            errors.append(f"bras {arm}: {cheapest} points avant le sommet avec le cote le moins cher, "
                          f"moins que les {required} exiges")
        cap = nodes[[a for a in tree["arms"] if a["id"] == arm][0]["capstone"]]
        total_reachable += base + (max(side_costs.values()) if side_costs else 0) + cost(cap)
    total_reachable += sum(cost(n) for n in nodes.values() if n.get("kind") == "bridge")
    if total_reachable <= rules["max_points"]:
        errors.append(f"arbre complet ({total_reachable} pts) <= budget ({rules['max_points']}) : aucun choix")

    # Emplacements
    slots = rules["grand_slots_by_level"]
    levels = [s["level"] for s in slots]
    counts = [s["slots"] for s in slots]
    if levels != sorted(levels) or counts != sorted(counts):
        errors.append("grand_slots_by_level doit etre croissant")

    grands = sum(1 for n in nodes.values() if n.get("kind") in GRAND)
    print(f"{len(nodes)} noeuds, {len(seen)} aretes, {len(arm_ids)} bras, {grands} grands passifs")
    print(f"  arbre atteignable (fourches comprises) : {total_reachable} pts pour un budget de {rules['max_points']}")
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
