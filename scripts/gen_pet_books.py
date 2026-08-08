#!/usr/bin/env python3
"""Generateur deterministe des grimoires de familier.

Produit 32 competences x 5 rangs = 160 grimoires dans items/pet_books.json
(idempotent : le tableau "pet_books" est integralement remplace).

Schema d'un grimoire :
  id           = book_<nom_court>_rank_<c|b|a|s|ss>   (nom_court = skill_familiar_<X>)
  category     = "pet_book"
  book_type    = "skill"
  teaches_id   = l'id du skill enseigne (doit exister dans classes/familiar/skills.json)
  rank         = "C" | "B" | "A" | "S" | "SS"
  rank_percent = 100 / 115 / 130 / 150 / 175 (multiplicateur de puissance, comme les cartes Koro)

CE QUI N'EST VOLONTAIREMENT PAS DANS LE FICHIER
-----------------------------------------------
`role` : le rang du grimoire dit sa PUISSANCE, pas a qui il s'adresse. Le role du
skill enseigne vit dans classes/familiar/skills.json (champ `role`) et nulle part
ailleurs. Le recopier ici creerait une seconde source de verite qui se mettrait a
mentir au premier reequilibrage — exactement ce qui a rendu deux tests
d'integration rouges le 2026-08-08 (un multiplicateur de rarete et un id de potion
figes dans le test alors que la data avait bouge). Le serveur derive le role du
pool de skills qu'il charge deja ; le client fait le meme lookup pour l'affichage.

`icon` : le client resout par RANG (5 icones pour 160 objets), exactement comme les
145 empreintes se resolvent par rarete. Voir item_database.gd _resolve_item_icon.

Lancer depuis n'importe ou :
  python scripts/gen_pet_books.py
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "classes" / "familiar" / "skills.json"
OUT = ROOT / "items" / "pet_books.json"

SKILL_PREFIX = "skill_familiar_"

# Rang -> (suffixe d'id, % de puissance, rarete, prix d'achat, prix de vente)
#
# Le rank_percent suit la meme echelle que les cartes Koro (systems/koro.json) et
# est consomme de la meme facon : puissance = base x rank_percent / 100.
#
# UN RANG = UNE RARETE. Le rang porte deja toute l'information (puissance, prix,
# frequence de drop) ; lui accoler la rarete correspondante lui donne gratuitement
# la couleur et le tri du systeme de rarete existant, sans inventer un second axe.
# La rarete vit ICI et non dans un mapping code : le chargeur economy la deduisait
# du rang en C++ (une table figee de plus, invisible depuis la data).
#
# Prix de vente = 40% du prix d'achat, comme les consommables.
RANKS = [
    ("C",  "c",  100, "common",      150,   60),
    ("B",  "b",  115, "uncommon",    450,  180),
    ("A",  "a",  130, "rare",       1250,  500),
    ("S",  "s",  150, "epic",       3500, 1400),
    ("SS", "ss", 175, "legendary", 10000, 4000),
]


def build_books(skills):
    books = []
    for skill in skills:
        sid = skill["id"]
        if not sid.startswith(SKILL_PREFIX):
            raise SystemExit(f"id de skill inattendu (prefixe {SKILL_PREFIX} requis) : {sid}")
        short = sid[len(SKILL_PREFIX):]
        name_fr = skill.get("name_fr", short)
        name_en = skill.get("name_en", short)

        for rank, suffix, pct, rarity, buy, sell in RANKS:
            books.append({
                "id": f"book_{short}_rank_{suffix}",
                "name_fr": f"Grimoire : {name_fr} ({rank})",
                "name_en": f"Tome: {name_en} ({rank})",
                "category": "pet_book",
                "book_type": "skill",
                "teaches_id": sid,
                "rank": rank,
                "rank_percent": pct,
                "rarity": rarity,
                "description_fr": (
                    f"Enseigne « {name_fr} » au rang {rank} a un familier dont c'est le role. "
                    f"Puissance {pct}% de la competence de base. Si le familier connait deja "
                    f"cette competence a un rang inferieur, elle est amelioree ; si ses "
                    f"emplacements sont pleins, vous choisissez celle qu'elle remplace."
                ),
                "description_en": (
                    f"Teaches \"{name_en}\" at rank {rank} to a familiar of the matching role. "
                    f"Power {pct}% of the base skill. If the familiar already knows it at a lower "
                    f"rank, it is upgraded; if its slots are full, you choose which one it replaces."
                ),
                "buy_price": buy,
                "sell_price": sell,
                "tradeable": True,
                "stackable": False,
                "acquisition": ["loot"] if rank != "C" else ["loot", "vendor"],
            })
    return books


def main():
    if not SKILLS.exists():
        raise SystemExit(f"introuvable : {SKILLS}")
    skills = json.loads(SKILLS.read_text(encoding="utf-8"))["base_skills"]
    books = build_books(skills)

    ids = [b["id"] for b in books]
    if len(ids) != len(set(ids)):
        raise SystemExit("ids de grimoires en double — generation avortee")

    payload = {
        "_meta": {
            "version": "2.0",
            "description": (
                "Grimoires de familier : 32 competences x 5 rangs (C/B/A/S/SS). "
                "Un grimoire ENSEIGNE une competence a un familier DU MEME ROLE, ou "
                "l'ameliore si elle est deja connue a un rang inferieur. Emplacements "
                "pleins : le joueur choisit la competence remplacee. Le role n'est PAS "
                "duplique ici, il est derive de classes/familiar/skills.json. Le rang "
                "porte la puissance via rank_percent (meme echelle que les cartes Koro)."
            ),
            "generated_by": "scripts/gen_pet_books.py",
            "count": len(books),
            "ranks": {r[0]: {"rank_percent": r[2], "rarity": r[3]} for r in RANKS},
            "acquisition_note": (
                "Rang C achetable chez Colette (plancher garanti : toute competence de "
                "son role est accessible au rang de base). B/A/S/SS uniquement au drop, "
                "rang pondere par le tier du monstre (items/loot_tables.json "
                "pet_book_drops)."
            ),
        },
        "pet_books": books,
    }

    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(books)} grimoires ecrits dans {OUT.relative_to(ROOT)}")
    by_rank = {}
    for b in books:
        by_rank[b["rank"]] = by_rank.get(b["rank"], 0) + 1
    print("par rang :", by_rank)


if __name__ == "__main__":
    sys.exit(main())
