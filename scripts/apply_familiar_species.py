"""Familiars by species (V2, owner decisions of 2026-10-02). Re-runnable, with --check.

1. Species identity: a familiar's stats = its ROLE profile x the identity of its species, the
   same identity as the monster of that species (entities/monster_species.json). Capture a golem
   for a tank, a high-MR species against mages. The role profiles (base + growth per level) live
   in config/familiar_balance.json `role_profiles` (written once from the current data, which
   had identical stats inside a role); every entry of entities/familiars.json is recomputed from
   them, and gets `monster_species`.
2. Species passive that grows: classes/familiar/passives.json `species_passives`, one per
   familiar species, with tiers at levels 1 / 20 / 50 / 100 (the skill-slot levels). NOT in the
   rolled pool (`passives`): the familiar service picks the tier matching the familiar's level
   and adds it to the rolled passives (kanarion_back vac_familiar-species-passive). Stats limited
   to hp / mp / atk / mag / armor / magic_resist: the only stats the combat host applies from a
   familiar passive today.

Usage:  python scripts/apply_familiar_species.py [--check]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Familiar species (familiars.json `species`, 65) -> monster species (monster_species.json).
FAMILIAR_TO_MONSTER = {
    "archonte_abyssal": "abyssal", "belier": "ovin_caprin", "biche": "cervide", "blaireau": "blaireau",
    "bouc": "ovin_caprin", "brebis": "ovin_caprin", "cerf": "cervide", "cerf_cauchemar": "faille",
    "cerf_obscur": "cervide", "chargeur_abyssal": "abyssal", "cheval_cauchemar": "faille",
    "cheval_sauvage": "cheval", "chevre": "ovin_caprin", "chien_braise": "braise",
    "chien_sauvage": "chien", "chien_vide": "vide", "cochon": "cochon", "colosse_os": "squelette",
    "corbeau": "corbeau", "crapaud_cracheur": "batracien", "demon_mineur": "demon",
    "devoreur_ames": "demon", "ecumeur_abyssal": "abyssal", "gardien_cloche": "golem",
    "golem": "golem", "golem_runique": "golem", "grenouille": "batracien",
    "grenouille_cornue": "batracien", "grenouille_soigneuse": "batracien", "gueule_faille": "faille",
    "horreur_effroi": "effroi", "hybride_sanglier_loup": "sanglier_loup", "hyene": "hyene",
    "invocateur_neant": "vide", "juggernaut_abyssal": "abyssal", "larve_abysse": "abyssal",
    "lievre": "lievre", "loup": "loup", "loup_cristal": "cristal", "loup_spectral": "spectre",
    "loutre": "loutre", "matrone_effroi": "effroi", "moissonneur_ames": "spectre",
    "pretre_vide": "vide", "rat": "rat", "rejeton_vide": "vide", "renard": "renard",
    "renard_brumeux": "renard", "revenant_vide": "spectre", "sanglier": "sanglier",
    "scarabee": "scarabee", "scarabee_sables": "scarabee", "scorpion": "scorpion",
    "seraphin_abyssal": "abyssal", "serpent": "serpent", "sorcier_abyssal": "abyssal",
    "squelette": "squelette", "squelette_necromancien": "squelette", "tatou": "tatou",
    "taureau": "bovin", "titan_vide": "vide", "tortue_pierre": "tortue",
    "traqueur_effroi": "effroi", "traqueur_faille": "faille", "vache": "bovin",
    # 2026-10-13 (vac_monstres-nouveaux) : faune des vacances.
    "chat_sauvage": "chat_sauvage", "herisson": "herisson", "belette": "belette", "ragondin": "ragondin",
    # Couche 1 : une famille par nouveau monstre (identité = espèce du monstre).
    "chat_sauvage_roux": "chat_sauvage", "marcassin": "sanglier", "laie": "sanglier",
    "vieux_solitaire": "sanglier", "loup_noir": "loup", "loup_blanc": "loup", "vieux_loup": "loup",
    "ours_brun": "ours", "ourse": "ours", "ours_noir": "ours", "ours_cavernes": "ours", "ourson": "ours",
    "biche_fletrie": "cervide", "cerf_fletri": "cervide", "blaireau_fletri": "blaireau",
    # Couche 2 : familles scindées des anciens monstres (le monstre de base garde la famille).
    "rat_jeune": "rat", "rat_alpha": "rat", "rat_soigneur": "rat", "rat_sorcier": "rat",
    "scarabee_larve": "scarabee", "scarabee_geant": "scarabee", "sanglier_enrage": "sanglier",
    "loup_enrage": "loup", "loup_meneur": "loup", "loup_garou": "loup_garou", "hyene_alpha": "hyene",
    "guerrier_squelette": "squelette",
    # Variantes : leur propre famille, identité de l'espèce du monstre (comme loup_cristal -> cristal).
    "ours_fissure": "ours", "grande_ourse": "ours", "ours_givre": "cristal", "cerf_givre": "cristal",
    "sanglier_braise": "braise", "taureau_braise": "braise", "chacal_faille": "hyene",
}

# Species passive per MONSTER species: (name_fr, name_en, {stat: weight}). Tier values below are
# multiplied by the weight: a one-stat passive reaches +18 % at level 100, a two-stat one +9 % each.
SPECIES_PASSIVE = {
    "rat": ("Grignoteur", "Gnawer", {"atk": 1.0}),
    "scarabee": ("Carapace", "Carapace", {"armor": 1.0}),
    "serpent": ("Venin", "Venom", {"atk": 1.0}),
    "chien": ("Mâchoires", "Jaws", {"atk": 1.0}),
    "corbeau": ("Œil du charognard", "Scavenger's Eye", {"atk": 1.0}),
    "renard": ("Ruse", "Cunning", {"atk": 0.5, "magic_resist": 0.5}),
    "sanglier": ("Charge", "Charge", {"hp": 0.5, "atk": 0.5}),
    "loup": ("Instinct de meute", "Pack Instinct", {"atk": 1.0}),
    "hyene": ("Charognard", "Scavenger", {"atk": 0.5, "hp": 0.5}),
    "scorpion": ("Chitine", "Chitin", {"armor": 0.7, "atk": 0.3}),
    "ovin_caprin": ("Toison", "Fleece", {"hp": 0.5, "armor": 0.5}),
    "bovin": ("Masse", "Bulk", {"hp": 1.0}),
    "tortue": ("Carapace de pierre", "Stone Shell", {"armor": 0.7, "hp": 0.3}),
    "cervide": ("Grâce sylvestre", "Sylvan Grace", {"magic_resist": 0.5, "mag": 0.5}),
    "tatou": ("Cuirasse", "Plating", {"armor": 1.0}),
    "cheval": ("Endurance", "Stamina", {"hp": 1.0}),
    "sanglier_loup": ("Bête hybride", "Hybrid Beast", {"atk": 0.5, "hp": 0.5}),
    "batracien": ("Peau visqueuse", "Slick Skin", {"magic_resist": 1.0}),
    "loutre": ("Agilité", "Agility", {"atk": 0.5, "magic_resist": 0.5}),
    "cochon": ("Robustesse", "Sturdiness", {"hp": 1.0}),
    "lievre": ("Vivacité", "Quickness", {"atk": 1.0}),
    "blaireau": ("Ténacité", "Tenacity", {"armor": 0.5, "hp": 0.5}),
    "loup_garou": ("Sang maudit", "Cursed Blood", {"atk": 0.5, "hp": 0.5}),
    "gobelin": ("Débrouillard", "Resourceful", {"atk": 0.5, "mag": 0.5}),
    "homme_lezard": ("Écailles", "Scales", {"armor": 0.5, "magic_resist": 0.5}),
    "squelette": ("Os durs", "Hard Bones", {"armor": 1.0}),
    "spectre": ("Intangible", "Intangible", {"magic_resist": 1.0}),
    "golem": ("Peau de pierre", "Stoneskin", {"armor": 0.7, "hp": 0.3}),
    "cristal": ("Givre", "Frost", {"magic_resist": 0.5, "mag": 0.5}),
    "braise": ("Braise", "Ember", {"mag": 1.0}),
    "esprit_sylvestre": ("Racines", "Roots", {"hp": 0.5, "magic_resist": 0.5}),
    "faille": ("Déchirure", "Rend", {"atk": 0.5, "mag": 0.5}),
    "vide": ("Néant", "Void", {"mag": 1.0}),
    "abyssal": ("Puissance abyssale", "Abyssal Might", {"atk": 0.5, "mag": 0.5}),
    "effroi": ("Terreur", "Dread", {"atk": 1.0}),
    "demon": ("Sang démoniaque", "Demon Blood", {"mag": 0.5, "magic_resist": 0.5}),
    "archonte_dechu": ("Majesté déchue", "Fallen Majesty", {"hp": 0.5, "magic_resist": 0.5}),
    "ours": ("Force de l'ours", "Bear Strength", {"hp": 0.5, "atk": 0.5}),
    "chat_sauvage": ("Griffes vives", "Quick Claws", {"atk": 1.0}),
    "herisson": ("Piquants", "Spines", {"armor": 1.0}),
    "belette": ("Insaisissable", "Elusive", {"atk": 0.5, "magic_resist": 0.5}),
    "ragondin": ("Têtu", "Stubborn", {"hp": 0.5, "armor": 0.5}),
}
TIERS = [(1, 4.0), (20, 8.0), (50, 12.0), (100, 18.0)]  # (min familiar level, % at weight 1.0)
STAT_FR = {"hp": "PV max", "atk": "attaque", "mag": "magie", "armor": "armure", "magic_resist": "résistance magique"}
STAT_EN = {"hp": "max HP", "atk": "attack", "mag": "magic", "armor": "armor", "magic_resist": "magic resist"}
STATS = ["hp", "mp", "atk", "mag", "armor", "magic_resist"]


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def dump(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").replace("\n", "\r\n").encode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    species = load("entities/monster_species.json")["species"]
    fams = load("entities/familiars.json")
    balance = load("config/familiar_balance.json")
    passives = load("classes/familiar/passives.json")
    errors = []

    # Role profiles: written once from the current data (identical inside a role), then source.
    if "role_profiles" not in balance:
        # Only the base `mp` differs between familiars of a role (tuned to their skills' costs):
        # it stays per familiar and is never touched; every other stat comes from the role.
        def sans_mp(d):
            return {k: v for k, v in d.items() if k != "mp"}
        profiles = {}
        for f in fams["familiars"]:
            prof = profiles.setdefault(f["role"], {"base_stats": sans_mp(f["base_stats"]), "growth": f["growth"]})
            if prof["base_stats"] != sans_mp(f["base_stats"]) or prof["growth"] != f["growth"]:
                errors.append(f"profil de rôle ambigu ({f['role']}) : {f['id']}")
        balance["role_profiles"] = {
            "_comment": "Profils de rôle des familiers (base niveau 1 + croissance par niveau), source unique depuis 2026-10-02. Le Souffle de base (mp) reste propre à chaque familier (réglé sur ses compétences). Les stats de chaque familier = profil de son rôle x identité de son espèce (entities/monster_species.json), recalculées par scripts/apply_familiar_species.py.",
            **profiles,
        }
    roles = {k: v for k, v in balance["role_profiles"].items() if not k.startswith("_")}

    for f in fams["familiars"]:
        msp = FAMILIAR_TO_MONSTER.get(f.get("species", ""))
        if not msp or msp not in species:
            errors.append(f"espèce sans correspondance : {f['id']} ({f.get('species')} -> {msp})")
            continue
        ident = species[msp]["identity"]
        mult = {"hp": ident["hp"], "mp": 1.0, "atk": ident["atk"], "mag": ident["atk"],
                "armor": ident["armor"], "magic_resist": ident["magic_resist"]}
        prof = roles[f["role"]]
        f["monster_species"] = msp
        own_mp = f["base_stats"].get("mp", 0)  # per familiar, kept as authored
        f["base_stats"] = {s: (own_mp if s == "mp" else max(1, round(prof["base_stats"][s] * mult[s])))
                           for s in STATS}
        f["growth"] = {s: round(prof["growth"][s] * mult[s], 2) for s in STATS}

    used = sorted({f.get("species") for f in fams["familiars"]})
    sp_passives = {"_comment": "Passif d'ESPÈCE de chaque familier (2026-10-02), qui monte en puissance aux niveaux 1 / 20 / 50 / 100. Hors tirage aléatoire : le service des familiers ajoute le palier correspondant au niveau du familier à ses passifs tirés (valeur x multiplicateur de rareté). Généré par scripts/apply_familiar_species.py depuis l'espèce de monstre."}
    for fsp in used:
        msp = FAMILIAR_TO_MONSTER.get(fsp)
        if msp not in SPECIES_PASSIVE:
            errors.append(f"pas de passif d'espèce pour {fsp} -> {msp}")
            continue
        name_fr, name_en, weights = SPECIES_PASSIVE[msp]
        tiers = []
        for lvl, pct in TIERS:
            effects = [{"stat": s, "op": "add_percent", "value": round(pct * w, 1)} for s, w in weights.items()]
            tiers.append({
                "min_level": lvl,
                "effects": effects,
                "description_fr": ", ".join(f"+{e['value']:g}% {STAT_FR[e['stat']]}" for e in effects),
                "description_en": ", ".join(f"+{e['value']:g}% {STAT_EN[e['stat']]}" for e in effects),
            })
        sp_passives[fsp] = {"monster_species": msp, "id": f"fsp_{msp}", "name_fr": name_fr,
                            "name_en": name_en, "tiers": tiers}
    passives["species_passives"] = sp_passives

    for e in errors:
        print("ERREUR", e)
    if errors:
        sys.exit(2)
    outputs = {
        ROOT / "entities/familiars.json": dump(fams),
        ROOT / "config/familiar_balance.json": dump(balance),
        ROOT / "classes/familiar/passives.json": dump(passives),
    }
    # Compared without CR: git stores these files with LF (Linux CI checkout) while dump()
    # writes CRLF (Windows working tree). A line-ending difference is not a data change.
    def same(p, b):
        return p.read_bytes().replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n")
    changed = [p for p, b in outputs.items() if not same(p, b)]
    if args.check:
        print("à jour" if not changed else "à appliquer : " + ", ".join(str(p.relative_to(ROOT)) for p in changed))
        sys.exit(1 if changed else 0)
    for p, b in outputs.items():
        p.write_bytes(b)
    print("écrit : " + (", ".join(str(p.relative_to(ROOT)) for p in changed) or "rien (déjà à jour)"))


if __name__ == "__main__":
    main()
