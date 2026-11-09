#!/usr/bin/env python3
"""Textes joueur « rang I a V » ecrits en TRANCHE DE NIVEAU (0.21.3, decision Charleston).

Les rangs I..V des failles et des objets ne s'affichent plus en chiffres romains :
le joueur lit la tranche de niveau. Forme courte « niv. 41-60 » dans les titres et
les noms, forme longue « niveau 41 a 60 » dans les phrases (descriptions).

SOURCE DES TRANCHES
-------------------
Une seule : items/panoplies.json _meta.rank_system.rang_N.level_range (le client
la lit aussi, via ItemDatabase.get_rank_bands()). Ce script ne contient AUCUN
nombre de niveau : il recopie la tranche dans les textes qui la citent. Changer
une tranche = la changer la-bas, puis relancer ce script.

TEXTES PRODUITS (seule la partie « niveau » est reecrite, le reste de la phrase
est garde tel quel)
  - items/materials.json enhancement_stones[] (stone_rank rank_N) :
      description_fr « .... Utilisable sur les objets de niveau <max> ou moins. »
      description_en « .... Usable on items of level <max> or lower. »
      <max> = plus haut niveau REQUIS accepte par le serveur
      (systems/enhancement_system.json equipment_rank_gate, verifie egal aux
      tranches ci-dessus)
  - items/profession_recipes.json new_items[] mat_rift_ember_r<N> (rank N) :
      description_fr « ... en refermant une faille de niveau <min> a <max>. »
      description_en « ... while sealing a level <min> to <max> rift. »
      source         « ... interieur de faille de niveau <min> a <max> »
  - world/zones.json zones[] type rift_interior (rift_rank N) :
      name_fr « Interieur de faille (niv. <min>-<max>) »
      name_en « Rift Interior (Lv. <min>-<max>) »

Le rang d'une faille est ceil(niveau max de l'aire / 20) (world/rift_events.json),
soit le meme decoupage que les tranches ci-dessus : le validateur le verifie.

Les rangs de METIER (outils, lanternes, Braise de Faille I..V, ressources) restent
« rang I a V » : ce sont les paliers du metier, pas des niveaux de personnage.

Ecriture : remplacement de la seule valeur de chaque champ dans le texte brut du
fichier, pour ne pas reformater le JSON.

Usage :
  python scripts/gen_rank_level_texts.py           # reecrit les textes
  python scripts/gen_rank_level_texts.py --check   # sort 1 si un texte n'est pas a jour
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Clause « niveau » d'une phrase : on accepte l'ancienne forme (rang romain) et la
# nouvelle (niveau), pour que le script soit idempotent.
ROMAN = r"(?:I|II|III|IV|V)"
NUM = r"\d+"

STONE_FR = re.compile(r"(?:, sur un objet de (?:rang " + ROMAN + r"(?: ou inférieur)?|niveau " + NUM + r" ou moins)|\. Utilisable sur les objets de niveau " + NUM + r" ou moins)\.$")
STONE_EN = re.compile(r"(?:, on an item of (?:rank " + ROMAN + r"(?: or lower)?|level " + NUM + r" or lower)|\. Usable on items of level " + NUM + r" or lower)\.$")
EMBER_FR = re.compile(r"une faille de (?:rang " + ROMAN + r"|niveau " + NUM + r" à " + NUM + r")\.$")
EMBER_EN = re.compile(r"sealing a (?:rank " + ROMAN + r"|level " + NUM + r" to " + NUM + r") rift\.$")
EMBER_SRC = re.compile(r"interieur de faille de (?:rang " + ROMAN + r"|niveau " + NUM + r" a " + NUM + r")$")


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def bands():
    rs = load("items/panoplies.json")["_meta"]["rank_system"]
    out = {}
    for n in range(1, 6):
        span = rs["rang_%d" % n]["level_range"]
        out[n] = (int(span[0]), int(span[1]))
    return out


def stone_level_caps():
    """Plus haut NIVEAU REQUIS d'objet qu'une pierre de rang N accepte.

    C'est la valeur que compare le serveur (economy handle_enhance_item :
    EnhancementRules::required_rank(level_req, +N)) : le niveau requis de l'objet
    (level_req) donne un rang de pierre minimum par systems/enhancement_system.json
    equipment_rank_gate.min_stone_rank_by_level_req. Une pierre de rang N passe
    donc tout objet dont le niveau requis est sous le seuil du rang N+1 (la tranche
    du +N vise peut encore exiger plus : c'est le « jusqu'a +8 » de la phrase).
    Le dernier rang va jusqu'au bout de sa tranche. Les seuils doivent etre ceux des
    tranches de rank_system, sinon le script s'arrete (deux sources divergentes).
    """
    b = bands()
    gate = load("systems/enhancement_system.json")["equipment_rank_gate"]["min_stone_rank_by_level_req"]
    mins = {int(str(g["stone_rank"]).replace("rank_", "")): int(g["min_level_req"]) for g in gate}
    for n in range(1, 6):
        if mins.get(n) != b[n][0]:
            raise SystemExit("systems/enhancement_system.json equipment_rank_gate rank_%d (%s) != debut de la "
                             "tranche items/panoplies.json rang_%d (%d)" % (n, mins.get(n), n, b[n][0]))
    return {n: (mins[n + 1] - 1 if n + 1 in mins else b[n][1]) for n in range(1, 6)}


def sub_one(rx, text, repl, where):
    new, count = rx.subn(repl, text)
    if count != 1:
        raise SystemExit("%s : clause de niveau introuvable dans %r" % (where, text))
    return new


def expected():
    """[(fichier, ancienne valeur, nouvelle valeur, ou)]."""
    b = bands()
    out = []

    caps = stone_level_caps()
    for s in load("items/materials.json")["enhancement_stones"]:
        n = int(str(s["stone_rank"]).replace("rank_", ""))
        hi = caps[n]
        where = "items/materials.json %s" % s["id"]
        out.append(("items/materials.json", s["description_fr"],
                    sub_one(STONE_FR, s["description_fr"], ". Utilisable sur les objets de niveau %d ou moins." % hi, where), where))
        out.append(("items/materials.json", s["description_en"],
                    sub_one(STONE_EN, s["description_en"], ". Usable on items of level %d or lower." % hi, where), where))

    for it in load("items/profession_recipes.json")["new_items"]:
        if not str(it.get("id", "")).startswith("mat_rift_ember_r"):
            continue
        lo, hi = b[int(it["rank"])]
        where = "items/profession_recipes.json %s" % it["id"]
        f = "items/profession_recipes.json"
        out.append((f, it["description_fr"],
                    sub_one(EMBER_FR, it["description_fr"], "une faille de niveau %d à %d." % (lo, hi), where), where))
        out.append((f, it["description_en"],
                    sub_one(EMBER_EN, it["description_en"], "sealing a level %d to %d rift." % (lo, hi), where), where))
        out.append((f, it["source"],
                    sub_one(EMBER_SRC, it["source"], "interieur de faille de niveau %d a %d" % (lo, hi), where), where))

    for z in load("world/zones.json")["zones"]:
        if z.get("type") != "rift_interior":
            continue
        lo, hi = b[int(z["rift_rank"])]
        where = "world/zones.json %s" % z["id"]
        out.append(("world/zones.json", z["name_fr"], "Intérieur de faille (niv. %d-%d)" % (lo, hi), where))
        out.append(("world/zones.json", z["name_en"], "Rift Interior (Lv. %d-%d)" % (lo, hi), where))
    return out


def check_rift_rule():
    """Le rang d'une faille = ceil(niveau max / 20) : la tranche affichee doit etre ce decoupage."""
    b = bands()
    for n in range(1, 6):
        lo, hi = b[n]
        if -(-hi // 20) != n or -(-lo // 20) != n:
            raise SystemExit("items/panoplies.json rang_%d %s ne suit plus le rang de faille "
                             "ceil(niveau / 20) de world/rift_events.json" % (n, b[n]))


def main():
    check = "--check" in sys.argv
    check_rift_rule()
    todo = [e for e in expected() if e[1] != e[2]]
    if check:
        for _, old, new, where in todo:
            print("PAS A JOUR %s : %r -> %r" % (where, old, new))
        if todo:
            print("Lancer : python scripts/gen_rank_level_texts.py")
            return 1
        print("OK : textes en tranche de niveau a jour")
        return 0
    by_file = {}
    for f, old, new, where in todo:
        by_file.setdefault(f, []).append((old, new, where))
    for f, edits in by_file.items():
        path = ROOT / f
        raw = path.read_bytes().decode("utf-8")
        for old, new, where in edits:
            enc_old = json.dumps(old, ensure_ascii=False)
            enc_new = json.dumps(new, ensure_ascii=False)
            if raw.count(enc_old) < 1:
                raise SystemExit("%s : valeur introuvable dans le texte brut" % where)
            raw = raw.replace(enc_old, enc_new, 1)
        path.write_bytes(raw.encode("utf-8"))
        print("%s : %d texte(s) reecrit(s)" % (f, len(edits)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
