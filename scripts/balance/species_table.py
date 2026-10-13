"""Species table for the monster V2 model: species x stage x archetype.

    monster lv1 stat = archetype profile (lv1) x species multiplier x stage multiplier

- SPECIES: every monster id grouped into a species (hand-written from names,
  categories and portraits; 2026-10-02). A species carries the identity: a
  golem is tanky whatever its role, a rat is frail.
- Species identity (SPECIES_IDENTITY): core multipliers (hp, atk, armor, mr)
  and rate bonuses, proposed by coherence (name, category, portraits, lore).
  The CSV also keeps the MEASURED multipliers for reference: geometric mean of
  the members' current factors (out/monster_stats_v2.csv), stage removed.
- STAGE: prefix multiplier on every core stat (jeune 0.7 ... geant 1.5).
- Archetype: from out/monster_review.csv (archetype_proposed).

Outputs: out/species_table.csv (one row per species) and
out/species_monsters.csv (one row per monster: species, stage, archetype,
lv1 stats, HP at lv 10/40/70/100 with its tier). Read-only on the game data.
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"

SPECIES = {
    # --- Bêtes du départ ---
    "rat": ["mob_rat", "mob_rat_jeune", "mob_rat_tutorial", "mob_rat_alpha", "mob_rat_soigneur",
            "mob_rat_mage", "mob_rat_rongeur", "mob_rat_assassin", "mob_rat_cuirasse"],
    "scarabee": ["mob_scarab", "mob_scarab_larve", "mob_scarab_geant", "mob_dust_beetle"],
    "serpent": ["mob_serpent"],
    "chien": ["mob_wild_dog"],
    "corbeau": ["mob_scavenger_crow"],
    "renard": ["mob_misty_fox", "mob_renard"],
    "sanglier": ["mob_boar", "mob_enraged_boar"],
    "loup": ["mob_wolf", "mob_frothing_wolf", "mob_wolf_packleader", "mob_wolf_soigneur",
             "boss_alpha_wolf", "mob_wolf_corrupted", "boss_fangmark_den"],
    "hyene": ["mob_alpha_hyena", "mob_hyene", "mob_hyene_scavenger", "mob_hyene_jackal", "mob_hyene_soigneur"],
    "scorpion": ["mob_rock_scorpion"],
    "ovin_caprin": ["mob_belier", "mob_chevre", "mob_brebis", "mob_bouc"],
    "bovin": ["mob_taureau", "mob_vache"],
    "tortue": ["mob_tortue_de_pierre"],
    "cervide": ["mob_cerf", "mob_cerf_obscur", "mob_cerf_obscur_soigneur", "mob_biche"],
    "tatou": ["mob_armadillo"],
    "cheval": ["mob_cheval_sauvage"],
    "sanglier_loup": ["mob_boar_wolf", "mob_boar_stalker"],
    "batracien": ["mob_grenouille", "mob_grenouille_cornue", "mob_grenouille_soigneuse", "mob_crapaud_cracheur"],
    "loutre": ["mob_loutre"],
    "cochon": ["mob_cochon"],
    "lievre": ["mob_lievre"],
    "blaireau": ["mob_blaireau"],
    "araignee": ["mob_spider_small", "mob_spider_queen", "boss_spider_queen"],
    "loup_garou": ["mob_loup_humain"],
    # --- Humanoïdes ---
    "gobelin": ["mob_goblin", "mob_goblin_warior", "mob_goblin_bomber", "mob_goblin_banner_bearer",
                "mob_shaman_goblin", "boss_goblin_king", "boss_goblin_warlord"],
    "bandit": ["mob_bandit_lookout", "mob_bandit_thug", "mob_bandit_archer", "mob_bandit_enforcer",
               "mob_bandit_cutpurse", "mob_bandit_brawler", "mob_bandit_witch_doctor", "mob_bandit_chief",
               "mob_bandit_warlord", "mob_bandit", "mob_bandit_raider", "boss_bandit_warlord"],
    "tribal": ["mob_brute_tribal", "mob_tribal_warlord", "mob_goblin_witch", "mob_bandit_hunter",
               "mob_bandit_warchief"],
    "hors_la_loi": ["mob_poacher", "mob_deserter", "mob_outlaw_archer", "mob_crossbowman", "mob_mercenary",
                    "mob_gang_leader", "mob_voleur"],
    "homme_lezard": ["mob_lizardman", "mob_lizardman_shaman"],
    "converti": ["mob_converted_blacksmith", "mob_converted_farmer", "mob_converted_herbalist",
                 "mob_converted_zealot", "mob_converted_hunter", "mob_converted_archer", "mob_converted_elder",
                 "mob_plague_doctor"],
    "zelote": ["mob_zealot_guard", "mob_zealot_ritualist", "mob_zealot_acolyte", "mob_zealot_warrior",
               "mob_fanatic_inquisitor", "mob_tower_fanatic", "mob_exalted_preacher"],
    "edric": ["mob_edric_chosen_guard", "mob_edric_chosen_ritualist", "mob_edric_warlord",
              "boss_edric_tower", "boss_inquisitor_edric"],
    "chevalier_dechu": ["mob_shattered_knight", "mob_corrupted_paladin", "mob_sentinel"],
    "culte_obscur": ["mob_dark_priest", "mob_dark_cultist"],
    # --- Morts-vivants ---
    "squelette": ["mob_archer_squelette", "mob_guerrier_skull", "mob_guerrier_skull_raider",
                  "mob_skeleton_necromancer", "mob_bone_colossus", "mob_hollow_sentinel", "boss_cursed_champion"],
    "spectre": ["mob_spectral_wolf", "mob_void_revenant", "mob_soul_harvester"],
    # --- Élémentaires ---
    "golem": ["mob_golem", "mob_golem_runique", "mob_golem_sentinel", "mob_golem_corrupted", "mob_bell_guardian"],
    "elementaire": ["mob_crystal_wolf", "mob_ember_hound"],
    "esprit_sylvestre": ["boss_forest_guardian"],
    # --- Faille, Vide, Abîme ---
    "faille": ["mob_rift_warden", "mob_rift_stalker", "mob_rift_stitcher", "mob_rift_maw", "mob_nightmare_horse",
               "mob_nightmare_stag"],
    "vide": ["mob_void_hound", "mob_void_executioner", "mob_void_spawn", "mob_void_priest",
             "mob_lesser_void_titan", "mob_nether_caller"],
    "abyssal": ["mob_abyssal_scholar", "mob_abyssal_charger", "mob_abyssal_warlock", "mob_abyssal_seraph",
                "mob_abyssal_reaver", "mob_abyssal_juggernaut", "mob_abyssal_archon", "mob_abyssal_sovereign",
                "mob_abyss_swarmling", "mob_maw_of_the_abyss"],
    "effroi": ["mob_dread_horror", "mob_dread_matron", "mob_dread_stalker"],
    "demon": ["mob_lesser_demon", "mob_soul_devourer"],
    "archonte_dechu": ["mob_wrathful_archon", "mob_grieving_sentinel", "mob_throne_sentinel"],
}
# Species identity PROPOSED by coherence (name, category, portraits, lore), 2026-10-02.
# Core multipliers on the archetype profile: (hp, atk, armor, magic_resist), plus flat
# identity bonuses on rate stats (added to the archetype's value, same caps).
# The same identity is meant for the familiar of that species (capture a golem for a
# tank, a high-MR species against mages). Measured values stay in the CSV for reference.
SPECIES_IDENTITY = {
    # Bêtes du départ : frêles, vives
    "rat":              ((0.6, 0.8, 0.8, 0.8),   {"evasion": 5},                       "frêle et vif, toujours en nombre"),
    "scarabee":         ((0.6, 0.8, 1.3, 0.7),   {"block_chance": 5},                  "carapace : armure, pas de RM"),
    "serpent":          ((0.8, 1.0, 0.8, 0.9),   {"evasion": 5, "crit": 5},            "venin, esquive"),
    "chien":            ((0.9, 1.0, 0.8, 0.8),   {"crit": 3},                          "mord vite"),
    "corbeau":          ((0.7, 0.9, 0.7, 1.0),   {"evasion": 10},                      "volant, insaisissable"),
    "renard":           ((0.8, 1.0, 0.8, 1.1),   {"evasion": 8},                       "rusé, touche de brume"),
    "sanglier":         ((1.2, 1.1, 1.1, 0.8),   {"tenacity": 5},                      "charge, encaisse"),
    "loup":             ((1.0, 1.1, 0.9, 0.9),   {"crit": 5, "crit_damage": 10},       "chasseur de meute"),
    "hyene":            ((0.9, 1.05, 0.9, 0.9),  {"crit": 3, "armor_pen": 5},          "charognard, déchire"),
    "scorpion":         ((1.0, 1.0, 1.4, 0.8),   {"armor_pen": 5},                     "carapace et dard"),
    "ovin_caprin":      ((1.1, 0.9, 1.1, 0.9),   {"tenacity": 5, "block_chance": 3},   "cornes, têtu"),
    "bovin":            ((1.4, 1.1, 1.1, 0.8),   {"tenacity": 10},                     "masse, inébranlable"),
    "tortue":           ((1.3, 0.7, 1.6, 0.7),   {"block_chance": 10},                 "carapace de pierre"),
    "cervide":          ((1.0, 0.9, 0.9, 1.2),   {"evasion": 5},                       "agile, liens avec la forêt"),
    "tatou":            ((1.1, 0.8, 1.5, 0.8),   {"block_chance": 8},                  "se roule en boule"),
    "cheval":           ((1.2, 1.0, 0.9, 0.9),   {"evasion": 5},                       "rapide, ruade"),
    "sanglier_loup":    ((1.2, 1.15, 1.0, 0.8),  {"crit": 3, "tenacity": 5},           "hybride, brutal"),
    "batracien":        ((0.9, 0.9, 0.8, 1.2),   {"evasion": 5},                       "visqueux, crache"),
    "loutre":           ((0.9, 1.0, 0.9, 1.0),   {"evasion": 8},                       "joueuse, glissante"),
    "cochon":           ((1.2, 0.9, 0.9, 0.9),   {"tenacity": 3},                      "solide, lent"),
    "lievre":           ((0.6, 0.8, 0.6, 0.8),   {"evasion": 15},                      "fuyant"),
    "blaireau":         ((1.1, 1.0, 1.2, 0.9),   {"tenacity": 5},                      "teigneux"),
    "araignee":         ((0.8, 1.0, 0.9, 1.0),   {"crit": 5, "evasion": 5},            "toiles et poison"),
    "loup_garou":       ((1.3, 1.2, 1.0, 0.8),   {"lifesteal": 5, "crit": 5},          "bête maudite, se régénère"),
    # Humanoïdes
    "gobelin":          ((0.8, 0.9, 0.9, 0.8),   {"evasion": 5},                       "petits, nombreux, sournois"),
    "bandit":           ((0.9, 1.0, 0.9, 0.8),   {"crit": 5},                          "coups bas"),
    "tribal":           ((1.1, 1.05, 0.9, 0.9),  {"tenacity": 5},                      "guerriers endurcis"),
    "hors_la_loi":      ((1.0, 1.0, 1.0, 0.9),   {"armor_pen": 5},                     "arbalètes, armes lourdes"),
    "homme_lezard":     ((1.1, 1.0, 1.2, 1.0),   {"tenacity": 5},                      "écailles"),
    "converti":         ((1.0, 0.95, 1.0, 1.1),  {"tenacity": 5},                      "villageois tenus par la Fissure"),
    "zelote":           ((1.05, 1.0, 1.05, 1.15), {"tenacity": 10},                    "fanatiques"),
    "edric":            ((1.15, 1.1, 1.15, 1.1), {"crit": 5, "tenacity": 10},          "élite de la Tour"),
    "chevalier_dechu":  ((1.2, 1.05, 1.3, 1.0),  {"block_chance": 8, "parry_chance": 3}, "armure lourde"),
    "culte_obscur":     ((0.8, 0.9, 0.7, 1.4),   {"magic_pen": 5},                     "magie noire"),
    # Morts-vivants
    "squelette":        ((0.9, 1.0, 0.9, 1.2),   {"tenacity": 15},                     "ne connaît pas la peur"),
    "spectre":          ((0.8, 1.0, 0.5, 1.5),   {"evasion": 10},                      "intangible : armure inutile, RM forte"),
    # Élémentaires
    "golem":            ((1.3, 0.8, 1.5, 1.0),   {"block_chance": 10, "tenacity": 10}, "pierre : le tank naturel"),
    "elementaire":      ((1.0, 1.1, 1.0, 1.3),   {"magic_pen": 5},                     "énergie brute"),
    "esprit_sylvestre": ((1.3, 0.9, 1.1, 1.3),   {"tenacity": 10},                     "gardien ancien"),
    # Le sud : Faille, Vide, Abîme
    "faille":           ((1.1, 1.1, 1.0, 1.2),   {"shield_pierce": 5},                 "déchire les protections"),
    "vide":             ((1.0, 1.15, 0.9, 1.2),  {"magic_pen": 5, "armor_pen": 5},     "le vide traverse tout"),
    "abyssal":          ((1.15, 1.1, 1.1, 1.15), {"crit_damage": 10},                  "puissance de l'Abîme"),
    "effroi":           ((0.9, 1.15, 0.8, 1.1),  {"crit": 5, "evasion": 5},            "terreur, frappe dans l'ombre"),
    "demon":            ((1.2, 1.15, 1.0, 1.4),  {"lifesteal": 5},                     "se nourrit de la vie"),
    "archonte_dechu":   ((1.25, 1.15, 1.2, 1.25), {"tenacity": 15, "reflect": 5},      "anciens gardiens corrompus"),
}
STAGE = {"jeune": 0.7, "larve": 0.7, "tutorial": 0.6, "small": 0.7, "alpha": 1.3, "geant": 1.5,
         "giant": 1.5, "ancient": 1.4, "lesser": 0.8, "corrupted": 1.2, "packleader": 1.3, "chief": 1.3,
         "warchief": 1.4, "warlord": 1.5, "king": 1.5, "queen": 1.5, "matron": 1.4}
CORE = ["hp", "atk", "armor", "magic_resist"]
SHOW = [1, 10, 40, 70, 100]


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def read_csv(name):
    with open(OUT / name, encoding="utf-8-sig") as f:
        return {r["id"]: r for r in csv.DictReader(f, delimiter=";")}


def interpolate(anchors, level):
    pts = sorted((int(k), float(v)) for k, v in anchors.items() if k.isdigit())
    if level <= pts[0][0]:
        return pts[0][1]
    if level >= pts[-1][0]:
        return pts[-1][1]
    for (l0, v0), (l1, v1) in zip(pts, pts[1:]):
        if l0 <= level <= l1:
            return v0 + (level - l0) / (l1 - l0) * (v1 - v0)


def main():
    model = load("config/monster_scaling_model.json")
    arch_lv1 = {k: v for k, v in model["archetypes_lv1_standard"].items() if not k.startswith("_")}
    tiers = model["tier_multipliers"]
    hp_curve = model["level_curve"]["anchors_hp"]
    v2 = read_csv("monster_stats_v2.csv")
    review = read_csv("monster_review.csv")
    owner = {mid: sp for sp, ids in SPECIES.items() for mid in ids}

    # Species multipliers from the members' current factors, stage removed.
    logs = defaultdict(lambda: defaultdict(list))
    for mid, sp in owner.items():
        if mid not in v2:
            continue
        stage_mult = STAGE.get(review[mid]["stage"], 1.0) if mid in review else 1.0
        for stat in CORE:
            f = float(v2[mid][f"f_{stat}"]) / stage_mult
            logs[sp][stat].append(math.log(max(0.05, f)))
    species_rows = []
    species_mult = {}
    for sp, ids in SPECIES.items():
        measured = {stat: round(math.exp(sum(v) / len(v)), 2) if (v := logs[sp][stat]) else 1.0 for stat in CORE}
        core, bonus, note = SPECIES_IDENTITY[sp]
        mult = dict(zip(CORE, core))
        species_mult[sp] = mult
        members = [m for m in ids if m in review]
        species_rows.append({
            "species": sp, "members": len(members), "category": review[members[0]]["category"] if members else "",
            **{f"x_{s}": mult[s] for s in CORE},
            "identity_bonus": " ".join(f"{k}+{v}" for k, v in bonus.items()),
            "identity": note,
            **{f"measured_{s}": measured[s] for s in CORE},
            "archetypes": " ".join(sorted({review[m]["archetype_proposed"] for m in members})),
            "ids": " ".join(members),
        })

    # Per-monster lv1 stats in the V2 model. New archetypes not yet in the model fall back
    # to their closest existing profile until their own profile is written.
    fallback = {"gardien": "tank", "berserker": "brute", "soigneur": "support", "enchanteur": "support",
                "controleur": "controller", "invocateur": "mage"}
    mon_rows = []
    for mid, r in review.items():
        sp = owner.get(mid, "")
        arch = r["archetype_proposed"]
        prof = arch_lv1.get(arch) or arch_lv1[fallback.get(arch, "brute")]
        stage = r["stage"]
        sm = STAGE.get(stage, 1.0)
        mult = species_mult.get(sp, {s: 1.0 for s in CORE})
        lv1 = {
            "hp": prof["hp"] * mult["hp"] * sm,
            "off": prof["atk"] * mult["atk"] * sm,
            "armor": prof["def"] * mult["armor"] * sm,
            "magic_resist": prof["magic_resist"] * mult["magic_resist"] * sm,
        }
        t = tiers.get(r["tier"], tiers["standard"])["hp"]
        row = {"id": mid, "name_fr": r["name_fr"], "status": r["status"], "species": sp or "(sans espèce)",
               "stage": stage, "stage_mult": sm, "archetype": arch, "tier": r["tier"],
               "base_level": r["base_level"], **{f"lv1_{k}": round(v, 1) for k, v in lv1.items()}}
        for L in SHOW:
            row[f"hp@{L}"] = round(lv1["hp"] * interpolate(hp_curve, L) * t)
        mon_rows.append(row)

    OUT.mkdir(exist_ok=True)
    for name, rows in (("species_table.csv", species_rows), ("species_monsters.csv", mon_rows)):
        with open(OUT / name, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
            w.writeheader()
            w.writerows(rows)
    unassigned = [m for m, r in review.items() if r["status"] == "active" and m not in owner]
    print(f"{len(species_rows)} species, {len(mon_rows)} monsters; active without species: {unassigned}")


if __name__ == "__main__":
    main()
