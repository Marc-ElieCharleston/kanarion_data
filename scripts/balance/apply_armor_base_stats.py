#!/usr/bin/env python3
"""Stats fixes de base (PV, armure, RM) des pieces d'armure, depuis UNE table.

Source unique : items/equipment_scaling.json `armor_base_stats` (decision Charleston du
2026-11-26). Ce script recopie la table dans items/equipment.json
base_items.armor.<emplacement>[].base_stats. Le socle d'une piece d'armure ne porte QUE les
cles de armor_base_stats.base_stats_keys (hp / armor / magic_resist / mp) : toute autre cle
(MAG, esquive, regen de Souffle) est retiree. Les sous-stats font la difference.

    valeur = unit_by_weight[poids][stat] x slot_weight[emplacement] x tier_mult[palier]
    arrondi a l'entier le plus proche (moitie vers le haut), minimum 1

  - poids   : champ `weight` de la piece ; pour une piece de tournoi
              (tournoi_<emplacement>_role_<role>), tournament_weight_by_role[role], et le
              champ `weight` de la piece est aligne dessus ;
  - palier  : suffixe _b1.._b5 du modele, sinon la tranche de equipment_system.level_brackets
              qui contient son level_req ; tournament pour les pieces de tournoi.

La rarete et l'amelioration ne sont PAS dans la table : le serveur les applique ensuite au
modele (economy StatCalculator), comme avant.

Usage (depuis la racine du depot de data) :
    python scripts/balance/apply_armor_base_stats.py           # ecrit items/equipment.json
    python scripts/balance/apply_armor_base_stats.py --check   # CI : code 1 si une piece differe
    python scripts/balance/apply_armor_base_stats.py --table   # affiche la table calculee
"""
import argparse
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EQUIPMENT = ROOT / "items" / "equipment.json"
SCALING = ROOT / "items" / "equipment_scaling.json"
STATS = ("hp", "armor", "magic_resist")  # remplace par base_stats_keys de la table
TOURNAMENT = re.compile(r"^tournoi_[a-z]+_role_(?P<role>[a-z_]+)$")
BRACKET = re.compile(r"_(?P<b>b[1-5])$")


def load(path):
    raw = path.read_bytes().decode("utf-8")
    return json.loads(raw), ("\r\n" if "\r\n" in raw else "\n")


def rnd(x):
    return max(1, int(Decimal(repr(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))


def tier_of(piece, brackets):
    m = BRACKET.search(piece["id"])
    if m:
        return m.group("b")
    lvl = piece.get("level_req", 1)
    for b in brackets:
        if b["min"] <= lvl <= b["max"]:
            return b["id"]
    raise SystemExit(f"{piece['id']}: level_req {lvl} hors de toute tranche")


def expected(table, slot, weight, tier):
    unit = table["unit_by_weight"][weight]
    return {s: rnd(unit[s] * table["slot_weight"][slot] * table["tier_mult"][tier]) for s in STATS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--table", action="store_true")
    args = ap.parse_args()

    table = load(SCALING)[0]["armor_base_stats"]
    global STATS
    STATS = tuple(table["base_stats_keys"])
    eq, nl = load(EQUIPMENT)
    brackets = eq["equipment_system"]["level_brackets"]

    if args.table:
        tiers = [t for t in table["tier_mult"] if not t.startswith("_")]
        slots = [s for s in table["slot_weight"] if not s.startswith("_")]
        for w in table["unit_by_weight"]:
            print(f"\n{w} ({' / '.join(STATS)}, avant rarete)")
            print("  " + "emplacement".ljust(12) + "".join(t.rjust(16) for t in tiers))
            for s in slots:
                cells = []
                for t in tiers:
                    e = expected(table, s, w, t)
                    cells.append("/".join(str(e[k]) for k in STATS).rjust(16))
                print("  " + s.ljust(12) + "".join(cells))
            tot = {t: {k: sum(expected(table, s, w, t)[k] for s in slots) for k in STATS} for t in tiers}
            print("  " + "6 pieces".ljust(12) + "".join("/".join(str(v[k]) for k in STATS).rjust(16) for v in tot.values()))
        return 0

    diffs = []
    for slot, pieces in eq["base_items"]["armor"].items():
        if slot not in table["slot_weight"]:
            raise SystemExit(f"emplacement {slot} absent de armor_base_stats.slot_weight")
        for piece in pieces:
            m = TOURNAMENT.match(piece["id"])
            if m:
                weight, tier = table["tournament_weight_by_role"][m.group("role")], "tournament"
                if piece.get("weight") != weight:
                    diffs.append((piece["id"], "weight", piece.get("weight"), weight))
                    piece["weight"] = weight
            else:
                weight, tier = piece["weight"], tier_of(piece, brackets)
            want = expected(table, slot, weight, tier)
            bs = piece.setdefault("base_stats", {})
            for s in [k for k in bs if k not in STATS]:
                diffs.append((piece["id"], s, bs[s], None))
                del bs[s]
            for s in STATS:
                if bs.get(s) != want[s]:
                    diffs.append((piece["id"], s, bs.get(s), want[s]))
                    bs[s] = want[s]

    if args.check:
        for d in diffs:
            print(f"DIFF {d[0]} {d[1]}: {d[2]} -> table {d[3]}")
        print(f"{len(diffs)} ecart(s) avec items/equipment_scaling.json armor_base_stats")
        return 1 if diffs else 0

    text = json.dumps(eq, indent=2, ensure_ascii=False) + "\n"
    EQUIPMENT.write_bytes(text.replace("\n", nl).encode("utf-8"))
    print(f"{len(diffs)} valeur(s) ecrite(s) dans {EQUIPMENT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
