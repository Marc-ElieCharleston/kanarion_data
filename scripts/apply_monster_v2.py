"""Apply the monster V2 refactor (validated review of 2026-10-02) to the game data.

Re-runnable and idempotent: run it again after merging new monsters (e.g. the
wolf den) and it rewrites the same fields from the same sources.

Sources (all under _meta/refonte_monstres/ unless noted):
- kits_tous.csv            per monster: species, stage, archetype_final, kit (validated, 4 lots)
- DECISIONS.md             owner decisions; the ones that touch data are encoded below
                           (REMOVED, RENAMES, SPECIES_FIX) — keep both in sync
- new_skills.json          24 new monster skills + modified_existing (Headbutt)
- scripts/balance/species_table.py   SPECIES_IDENTITY and STAGE

Writes:
- entities/monster_species.json   NEW: species identity (hp/atk/armor/mr multipliers, rate
                                  bonuses, capturable), stage multipliers, archetype names.
- entities/monsters.json          per monster: stat_archetype (11 ids), ai_role, species,
                                  stage, skills (kit); legacy base_stats get a `mag` when a
                                  magical archetype had none (the loader falls back to atk/2);
                                  removed monsters -> roster_status shelved; renames.
- skills/monster_skills.json      new skills in the blocks the server loads (basic_skills,
                                  role_basic_skills.<arch>, archetype_skills.<arch>.pool),
                                  modified existing skills replaced in place.

Not touched: zones / dungeons / placements (the new map is on the office PC), monster
base_stats numbers (the V2 server computes stats from species x archetype x stage x level),
bosses' fight scripts, familiars.

Usage:  python scripts/apply_monster_v2.py          apply
        python scripts/apply_monster_v2.py --check  exit 1 if applying would change a file
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "_meta" / "refonte_monstres"
sys.path.insert(0, str(ROOT / "scripts" / "balance"))
import species_table as st  # noqa: E402  (SPECIES_IDENTITY, STAGE)

# Review labels (French) -> stat_archetype ids in config/monster_scaling_model.json.
ARCHETYPE_ID = {
    "tank": "tank", "gardien": "guardian", "brute": "brute", "berserker": "berserker",
    "assassin": "assassin", "archer": "archer", "mage": "mage", "controleur": "controller",
    "contrôleur": "controller", "soigneur": "healer", "invocateur": "summoner", "enchanteur": "enchanter",
}
# stat_archetype -> ai_role (must exist in config/monster_ai.json ai_roles).
AI_ROLE = {
    "tank": "tank", "guardian": "tank", "brute": "brute", "berserker": "berserker",
    "assassin": "assassin", "archer": "artillery", "mage": "caster", "controller": "controller",
    "healer": "healer", "summoner": "caster", "enchanter": "support",
}
MAGICAL = {"mage", "controller", "healer", "summoner", "enchanter"}
# Owner decisions (DECISIONS.md) that change data.
REMOVED = {  # -> roster_status shelved (kept for references: zones, loot, quests)
    "mob_spider_small": "araignées supprimées (PixelLab ne gère pas les 8 pattes), famille à remplacer",
    "mob_spider_queen": "araignées supprimées (PixelLab ne gère pas les 8 pattes), famille à remplacer",
    "boss_spider_queen": "araignées supprimées (PixelLab ne gère pas les 8 pattes), famille à remplacer",
    "mob_dust_beetle": "doublon du scarabée (une seule espèce de scarabée, au début)",
}
RENAMES = {"mob_bandit_enforcer": ("Homme de main", "Henchman")}
SPECIES_FIX = {  # monsters the reviewers left without a valid species
    "mob_corrupted_matriarch": "faille", "mob_rift_behemoth": "faille", "mob_rift_pack": "faille",
    "mob_void_hunter": "vide", "mob_corrupted_cleric": "zelote", "mob_fallen_zealot": "zelote",
    "mob_nightmare_weaver": "culte_obscur",
    "mob_crystal_wolf": "cristal", "mob_ember_hound": "braise",  # elementals split (lot 4)
}
EXTRA_SPECIES = {  # split of `elementaire` (lot 4)
    "cristal": ((1.0, 1.0, 1.1, 1.3), {"magic_pen": 5}, "glace : résiste à la magie"),
    "braise": ((1.0, 1.15, 0.9, 1.2), {"magic_pen": 5}, "feu : frappe fort, armure fragile"),
    # 2026-10-13 : faune ajoutée pendant les vacances (vac_monstres-nouveaux). Valeurs
    # reprises telles quelles de monster_species.json (saisies à la main par une autre
    # session, absentes de cette source : le script les croyait inconnues).
    "ours": ((1.3, 1.1, 1.1, 0.9), {"tenacity": 10}, "masse et force, lent à tomber"),
    "chat_sauvage": ((0.8, 1.1, 0.8, 0.9), {"crit": 5, "evasion": 5}, "griffes vives, bondit"),
    "herisson": ((0.8, 0.8, 1.4, 0.9), {"block_chance": 5}, "piquants : armure, petit"),
    "belette": ((0.6, 1.0, 0.7, 0.8), {"evasion": 10}, "minuscule et insaisissable"),
    "ragondin": ((1.0, 0.9, 1.0, 0.9), {"tenacity": 3}, "rongeur des berges, têtu"),
}
HUMANS = {"bandit", "hors_la_loi", "converti", "zelote", "edric", "chevalier_dechu", "culte_obscur"}
UNDECIDED_CAPTURE = {"tribal"}  # human or not: owner decides on the sprites
SKIP = {"mob_training_dummy"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(path, data):
    """Same formatting as the repo files: indent 2, CRLF, trailing newline."""
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").replace("\n", "\r\n").encode("utf-8")


def species_file(kit_rows):
    identity = dict(st.SPECIES_IDENTITY)
    identity.pop("elementaire", None)
    identity.update(EXTRA_SPECIES)
    category = {}
    for r in kit_rows:
        sp = SPECIES_FIX.get(r["id"], r["species"])
        category.setdefault(sp, r.get("category") or "")
    model = load(ROOT / "config" / "monster_scaling_model.json")
    names = {k: v.get("name_fr", k) for k, v in model["archetypes_lv1_standard"].items()
             if not k.startswith("_") and isinstance(v, dict)}
    species = {}
    for sp, (core, bonus, note) in identity.items():
        species[sp] = {
            "identity": dict(zip(["hp", "atk", "armor", "magic_resist"], core)),
            "rate_bonus": bonus,
            "capturable": None if sp in UNDECIDED_CAPTURE else sp not in HUMANS,
            "note_fr": note,
        }
    return {
        "_meta": {
            "version": "1.0",
            "generated_by": "scripts/apply_monster_v2.py",
            "description_fr": "Espèces de monstres (modèle V2, décisions du 2026-10-02). Stat d'un monstre = profil d'archétype (config/monster_scaling_model.json) x identité d'espèce x stade x courbe de niveau x palier x étoiles x contenu. 'identity' multiplie hp / atk (et mag) / armor / magic_resist ; 'rate_bonus' s'ajoute aux taux de l'archétype (mêmes plafonds). 'capturable' : les humains ne peuvent pas devenir familiers (null = à décider). Pas encore lu par le serveur (travail V2).",
            "source": "_meta/refonte_monstres/ (revue validée), scripts/balance/species_table.py",
        },
        "archetype_names_fr": names,
        "stages": {
            "_comment": "Préfixe ou titre (même espèce, plus ou moins puissant) : multiplie toutes les stats principales. Un nom propre avec son propre sprite reste un monstre distinct, mais garde ici son multiplicateur de puissance.",
            **st.STAGE,
        },
        "species": species,
    }


def apply_monsters(monsters, kit_rows, report):
    by_id = {r["id"]: r for r in kit_rows}
    for m in monsters["monsters"]:
        mid = m["id"]
        r = by_id.get(mid)
        if mid in SKIP or r is None:
            if r is None and mid not in SKIP:
                report.append(f"absent de la revue (non modifié) : {mid}")
            continue
        arch = ARCHETYPE_ID.get(r["archetype_final"].strip())
        if not arch:
            report.append(f"archétype inconnu pour {mid} : {r['archetype_final']!r}")
            continue
        m["stat_archetype"] = arch
        m["ai_role"] = AI_ROLE[arch]
        m["species"] = SPECIES_FIX.get(mid, r["species"])
        if r["stage"]:
            m["stage"] = r["stage"]
        else:
            m.pop("stage", None)
        kit = [k for k in r["kit"].split("|") if k]
        if kit:
            m["skills"] = kit
        b = m.setdefault("base_stats", {})
        if arch in MAGICAL and not b.get("mag"):
            b["mag"] = max(b.get("atk", 0), 1)
        if mid in REMOVED:
            m["roster_status"] = "shelved"
            m["_removed_2026_10"] = REMOVED[mid]
        if mid in RENAMES:
            m["name_fr"], m["name_en"] = RENAMES[mid]


def apply_skills(skills, new):
    def upsert(lst, skill):
        for i, s in enumerate(lst):
            if s.get("id") == skill["id"]:
                lst[i] = skill
                return
        lst.append(skill)

    for s in new["species_attacks"]:
        upsert(skills["basic_skills"], s)
    for s in new.get("modified_existing", {}).get("basic_skills", []):
        upsert(skills["basic_skills"], s)
    role_key = {"gardien": "guardian", "invocateur": "summoner", "enchanteur": "enchanter"}
    for s in new["role_basics"]:
        key = role_key[s["id"].split("_")[2]]
        upsert(skills["role_basic_skills"].setdefault(key, []), s)
    ident_key = {"gardien": "guardian", "brute": "brute", "assassin": "assassin",
                 "controleur": "controller", "invocateur": "summoner", "enchanteur": "enchanter"}
    for s in new["archetype_identity"]:
        key = ident_key[s["id"].split("_")[2]]
        block = skills["archetype_skills"].setdefault(
            key, {"_comment": f"Archétype V2 '{key}' (2026-10-02) : compétences d'identité.", "pool": []})
        upsert(block.setdefault("pool", []), s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    with open(REF / "kits_tous.csv", encoding="utf-8-sig") as f:
        kit_rows = list(csv.DictReader(f, delimiter=";"))
    cat = {m["id"]: m.get("category", "") for m in load(ROOT / "entities/monsters.json")["monsters"]}
    for r in kit_rows:
        r["category"] = cat.get(r["id"], "")

    report = []
    monsters = load(ROOT / "entities/monsters.json")
    apply_monsters(monsters, kit_rows, report)
    skills = load(ROOT / "skills/monster_skills.json")
    apply_skills(skills, load(REF / "new_skills.json"))
    species = species_file(kit_rows)

    # Consistency: every kit skill must be loadable, every species must exist.
    known = set()

    def walk(o):
        if isinstance(o, dict):
            if str(o.get("id", "")).startswith("skill_"):
                known.add(o["id"])
                return
            for k, v in o.items():
                if not k.startswith("_"):
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(skills)
    for m in monsters["monsters"]:
        for s in m.get("skills", []):
            if s not in known:
                report.append(f"ERREUR compétence introuvable : {m['id']} -> {s}")
        if m.get("species") and m["species"] not in species["species"]:
            report.append(f"ERREUR espèce inconnue : {m['id']} -> {m['species']}")

    outputs = {
        ROOT / "entities/monsters.json": dump(None, monsters),
        ROOT / "skills/monster_skills.json": dump(None, skills),
        ROOT / "entities/monster_species.json": dump(None, species),
    }
    changed = [p for p, b in outputs.items() if not p.exists() or p.read_bytes() != b]
    for line in report:
        print(line)
    if any(line.startswith("ERREUR") for line in report):
        sys.exit(2)
    if args.check:
        print("à jour" if not changed else "à appliquer : " + ", ".join(str(p.relative_to(ROOT)) for p in changed))
        sys.exit(1 if changed else 0)
    for p, b in outputs.items():
        p.write_bytes(b)
    print("écrit : " + (", ".join(str(p.relative_to(ROOT)) for p in changed) or "rien (déjà à jour)"))


if __name__ == "__main__":
    main()
