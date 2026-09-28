#!/usr/bin/env python3
"""Generateur deterministe des grimoires de familier (items/pet_books.json).

SOURCE DE VERITE
----------------
Ce script est la source de verite de items/pet_books.json. Le fichier JSON est
un PRODUIT : toute correction de texte, de prix ou de champ se fait ICI, puis on
regenere. Corriger le JSON a la main sans reporter la correction ici revient a
la perdre a la prochaine regeneration (c'est arrive : accents, `universal`,
`pet_role` retire du grimoire starter, champs boutique... ont ete corriges dans
le JSON seul, et une relance les aurait tous effaces).

Les seules entrees venues d'ailleurs sont :
  - classes/familiar/skills.json (`base_skills`) : id, nom FR/EN et role de
    chaque competence enseignee. L'ordre du fichier fixe l'ordre des grimoires.
  - les tables de ce script (rangs, prix, libelles de role, textes).

`python scripts/gen_pet_books.py --check` ne touche a rien et sort 1 si le
fichier commite differe de ce que le script produit (comparaison du JSON parse).
A lancer apres toute modification de skills.json ou de ce script.

CE QUE LE SCRIPT PRODUIT
------------------------
Pour chaque competence non signature de skills.json, dans l'ordre du fichier :
  - le grimoire starter (skill_familiar_starter_heal) : UNE entree ecrite a la
    main (STARTER_BOOK), universelle, offerte par quete, sans pet_role ;
  - une competence du catalogue d'origine (LEGACY_SKILLS, 32 competences) :
    5 rangs, rang C achetable chez Colette, description longue (amelioration /
    remplacement), pas d'icone propre ;
  - toute autre competence (catalogue etendu) : 5 rangs, loot seul, description
    courte, icone = icone du skill.
Les signatures (`is_signature`) ne s'apprennent pas par grimoire.

Schema d'un grimoire :
  id           = book_<nom_court>_rank_<c|b|a|s|ss>   (nom_court = skill_familiar_<X>)
  teaches_id   = l'id du skill enseigne
  rank         = "C" | "B" | "A" | "S" | "SS"
  rank_percent = 100 / 115 / 130 / 150 / 175 (meme echelle que les cartes Koro)
  pet_role     = miroir INFORMATIF du role du skill (la reference reste
                 skills.json ; le serveur derive le role du pool qu'il charge).

Usage :
  python scripts/gen_pet_books.py            # regenere items/pet_books.json
  python scripts/gen_pet_books.py --check    # sort 1 si le fichier n'est pas a jour
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "classes" / "familiar" / "skills.json"
OUT = ROOT / "items" / "pet_books.json"

SKILL_PREFIX = "skill_familiar_"

# Rang -> (suffixe d'id, % de puissance, rarete, prix d'achat, prix de vente)
# UN RANG = UNE RARETE. Prix de vente = 40% du prix d'achat, comme les consommables.
RANKS = [
    ("C",  "c",  100, "common",      150,   60),
    ("B",  "b",  115, "uncommon",    450,  180),
    ("A",  "a",  130, "rare",       1250,  500),
    ("S",  "s",  150, "epic",       3500, 1400),
    ("SS", "ss", 175, "legendary", 10000, 4000),
]

# role du skill -> (libelle FR du nom, libelle EN du nom, adjectif EN de la description)
ROLES = {
    "attaque":    ("Attaque",    "Attack",  "attack"),
    "tank":       ("Tank",       "Tank",    "tank"),
    "heal":       ("Soin",       "Healing", "healing"),
    "utilitaire": ("Utilitaire", "Utility", "utility"),
}

# Catalogue d'origine (commit b7fd581) : rang C vendu par Colette, description
# longue. Les competences ajoutees ensuite sont loot seul.
LEGACY_SKILLS = (
    "bite", "pounce", "frenzy_bites", "body_slam", "shrill_cry", "bristled_fur",
    "restorative_lick", "soothing_aura", "rescue_instinct", "breath_screen",
    "invigorating_presence", "paralyzing_bite", "tail_swipe", "furious_charge",
    "quick_bleed", "stubborn_stance", "sharp_taunt", "makeshift_shell",
    "vital_breath", "regen_wave", "calming_embrace", "alert_cry", "light_step",
    "tactical_sniff", "muzzle", "disarming_fang", "thieving_claw",
    "thirsting_bite", "festering_fangs", "mending_pulse", "guarding_lick",
    "unnerving_nip",
)

STARTER_SKILL = "skill_familiar_starter_heal"
STARTER_BOOK = {
    "id": "book_starter_heal",
    "name_fr": "Grimoire Soin : Souffle Réparateur (C)",
    "name_en": "Healing Tome: Mending Breath (C)",
    "category": "pet_book",
    "book_type": "skill",
    "teaches_id": STARTER_SKILL,
    "rank": "C",
    "rank_percent": 100,
    "rarity": "common",
    "universal": True,
    "description_fr": (
        "Enseigne un petit soin à n'importe quel familier, quel que soit son rôle. "
        "Offert pour aider les premiers pas de votre compagnon. Si le familier le "
        "connaît déjà, il est rafraîchi ; si ses emplacements sont pleins, vous "
        "choisissez celui qu'il remplace."
    ),
    "description_en": (
        "Teaches a small heal to any familiar, whatever its role. A gift to help "
        "your companion's first steps. If the familiar already knows it, it is "
        "refreshed; if its slots are full, you choose which one it replaces."
    ),
    "buy_price": 0,
    "sell_price": 0,
    "tradeable": False,
    "stackable": False,
    "acquisition": ["quest"],
}

UPGRADE_FR = (
    " Si le familier connaît déjà cette compétence à un rang inférieur, elle est "
    "améliorée ; si ses emplacements sont pleins, vous choisissez celle qu'elle remplace."
)
UPGRADE_EN = (
    " If the familiar already knows it at a lower rank, it is upgraded; if its "
    "slots are full, you choose which one it replaces."
)


def article(word):
    # "an attack", mais "a utility" (u prononce "you") : on ne teste que a/e/i/o.
    return "an" if word[:1].lower() in "aeio" else "a"


def build_books(skills):
    books = []
    for skill in skills:
        if skill.get("is_signature"):
            continue
        sid = skill["id"]
        if sid == STARTER_SKILL:
            books.append(dict(STARTER_BOOK))
            continue
        if not sid.startswith(SKILL_PREFIX):
            raise SystemExit(f"id de skill inattendu (prefixe {SKILL_PREFIX} requis) : {sid}")
        role = skill.get("role")
        if role not in ROLES:
            raise SystemExit(f"role inconnu pour {sid} : {role!r}")
        short = sid[len(SKILL_PREFIX):]
        legacy = short in LEGACY_SKILLS
        name_fr = skill["name_fr"]
        name_en = skill["name_en"]
        role_fr, role_en, role_adj = ROLES[role]

        for rank, suffix, pct, rarity, buy, sell in RANKS:
            desc_fr = (
                f"Enseigne « {name_fr} » au rang {rank} à un familier de rôle {role_fr}. "
                f"Puissance {pct}% de la compétence de base."
            )
            desc_en = (
                f"Teaches \"{name_en}\" at rank {rank} to {article(role_adj)} {role_adj} "
                f"familiar. Power {pct}% of the base skill."
            )
            if legacy:
                desc_fr += UPGRADE_FR
                desc_en += UPGRADE_EN
            book = {
                "id": f"book_{short}_rank_{suffix}",
                "name_fr": f"Grimoire {role_fr} : {name_fr} ({rank})",
                "name_en": f"{role_en} Tome: {name_en} ({rank})",
                "category": "pet_book",
                "book_type": "skill",
                "teaches_id": sid,
                "rank": rank,
                "rank_percent": pct,
                "rarity": rarity,
                "description_fr": desc_fr,
                "description_en": desc_en,
                "buy_price": buy,
                "sell_price": sell,
                "tradeable": True,
                "stackable": False,
                "acquisition": ["loot", "vendor"] if (legacy and rank == "C") else ["loot"],
            }
            if not legacy:
                book["icon"] = skill.get("icon", short)
            book["pet_role"] = role
            books.append(book)
    return books


def build_payload():
    if not SKILLS.exists():
        raise SystemExit(f"introuvable : {SKILLS}")
    skills = json.loads(SKILLS.read_text(encoding="utf-8"))["base_skills"]
    books = build_books(skills)

    ids = [b["id"] for b in books]
    if len(ids) != len(set(ids)):
        raise SystemExit("ids de grimoires en double : generation avortee")

    return {
        "_meta": {
            "version": "2.0",
            "description": (
                "Grimoires de familier : competences x 5 rangs (C/B/A/S/SS). "
                "Un grimoire ENSEIGNE une competence a un familier DU MEME ROLE, ou "
                "l'ameliore si elle est deja connue a un rang inferieur. Exception : "
                "un grimoire marque \"universal\": true (book_starter_heal) s'enseigne "
                "a un familier de N'IMPORTE QUEL role, et ne porte donc pas de pet_role. "
                "Emplacements pleins : le joueur choisit la competence remplacee. "
                "pet_role est un miroir informatif du role, la reference reste "
                "classes/familiar/skills.json. Le rang porte la puissance via "
                "rank_percent (meme echelle que les cartes Koro)."
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


def diff_report(current, wanted):
    """Liste lisible des ecarts entre le fichier commite et la sortie du script."""
    lines = []
    if current.get("_meta") != wanted["_meta"]:
        for k in sorted(set(current.get("_meta", {})) | set(wanted["_meta"])):
            if current.get("_meta", {}).get(k) != wanted["_meta"].get(k):
                lines.append(f"  _meta.{k} differe")
    cur = {b.get("id"): b for b in current.get("pet_books", [])}
    new = {b["id"]: b for b in wanted["pet_books"]}
    for i in sorted(set(cur) - set(new)):
        lines.append(f"  en trop dans le fichier : {i}")
    for i in sorted(set(new) - set(cur)):
        lines.append(f"  manquant dans le fichier : {i}")
    for i in new:
        if i in cur and cur[i] != new[i]:
            keys = sorted(k for k in set(cur[i]) | set(new[i]) if cur[i].get(k) != new[i].get(k))
            lines.append(f"  {i} : {', '.join(keys)}")
    if not lines and [b.get("id") for b in current.get("pet_books", [])] != list(new):
        lines.append("  ordre des grimoires different")
    return lines


def main():
    check = "--check" in sys.argv[1:]
    payload = build_payload()

    if check:
        current = json.loads(OUT.read_text(encoding="utf-8"))
        if current == payload:
            print(f"--check : a jour ({len(payload['pet_books'])} grimoires)")
            return 0
        lines = diff_report(current, payload)
        print(f"--check : {OUT.relative_to(ROOT)} differe de la sortie du script "
              f"({len(lines)} ecart(s))")
        for line in lines[:50]:
            print(line)
        return 1

    # Mode texte : sous Windows, \n devient \r\n, ce qui preserve les fins de
    # ligne CRLF de la copie de travail.
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    books = payload["pet_books"]
    print(f"{len(books)} grimoires ecrits dans {OUT.relative_to(ROOT)}")
    by_rank = {}
    for b in books:
        by_rank[b["rank"]] = by_rank.get(b["rank"], 0) + 1
    print("par rang :", by_rank)
    return 0


if __name__ == "__main__":
    sys.exit(main())
