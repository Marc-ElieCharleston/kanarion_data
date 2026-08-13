#!/usr/bin/env python3
"""
validate_cross_references.py — CI validator for kanarion_database/

SPEC FINALE $5.5 — Validates all cross-references in game data JSON files.
Run from kanarion_database/ root or pass DB_ROOT env var.

Checks:
  1. All stat names in affixes.json exist in stats/definitions.json
  2. All stat names in equipment_stats.json exist in definitions.json
  3. All class_tags in equipment.json are valid class IDs
  4. All item_ids in loot_tables.json exist in item database files
  5. All set_ids referenced exist in panoplies.json
  6. All output_item in recipes.json exist in item database files
  7. The 5 item-rank bands (C->SS) agree across their 3 copies
  8. config/rewards.json is coherent and matches the blocks it replaces

Exit code 0 = pass, 1 = failures found.
"""

import json
import sys
import os
from pathlib import Path


def load_json(path: Path) -> dict:
    """Load a JSON file with UTF-8 encoding."""
    return json.loads(path.read_text(encoding="utf-8"))


def collect_canonical_stats(defs: dict) -> set:
    """Extract all canonical stat IDs from definitions.json."""
    stats = set()
    # definitions.json has categories -> stats
    if "stats" in defs:
        stat_data = defs["stats"]
        if isinstance(stat_data, dict):
            for key, val in stat_data.items():
                if isinstance(val, dict):
                    # Category level: resources, offensive, etc.
                    if "id" in val:
                        stats.add(val["id"])
                    else:
                        # Nested category: iterate children
                        for sub_key, sub_val in val.items():
                            if isinstance(sub_val, dict) and "id" in sub_val:
                                stats.add(sub_val["id"])
                            elif isinstance(sub_val, dict):
                                # Une entree de stat SANS champ `id` : la cle EST
                                # l'identifiant (definitions.json n'utilise pas de
                                # champ `id`, aucune des 39 stats n'en porte).
                                # Bug historique : on descendait ici d'un niveau de
                                # trop et on ajoutait les noms de CHAMPS (`name`,
                                # `description`, `bonus_type`...) au lieu du nom de
                                # la stat. Consequence : seules les stats presentes
                                # dans la liste d'alias en dur passaient, et `luck`,
                                # `thorns`, `cast_speed`, `reflect` faisaient echouer
                                # la CI sans qu'aucune data soit fautive.
                                stats.add(sub_key)
                            else:
                                stats.add(sub_key)
                else:
                    stats.add(key)

    # Also add known aliases and common names from the stat system
    # These are used interchangeably in various files
    aliases = {
        "hp", "mp", "atk", "mag", "def", "armor", "magic_resist",
        "crit", "crit_chance", "crit_dmg", "crit_damage",
        "attack_speed", "hp_regen", "mp_regen",
        "lifesteal", "spell_vamp", "armor_pen", "magic_pen",
        "damage_reduction", "heal_power", "cooldown_reduction",
        "block_chance", "parry_chance", "evasion", "hit", "flee",
        "buff_duration", "debuff_duration", "effect_chance", "effect_resist",
        "tenacity", "damage_percent", "shield_power",
        "atk_percent", "mag_percent", "def_percent",
        "aggro_generation", "double_hit_chance", "shield_pierce", "shield_break",
    }
    stats.update(aliases)
    return stats


def validate_affixes(db: Path, valid_stats: set) -> list:
    """Check all stat names in affixes.json."""
    errors = []
    path = db / "items" / "affixes.json"
    if not path.exists():
        return [f"[affixes.json] File not found: {path}"]

    data = load_json(path)
    affixes = data.get("affixes", data.get("prefixes", []) + data.get("suffixes", []))
    if isinstance(data, dict) and "prefixes" in data:
        affixes = data.get("prefixes", []) + data.get("suffixes", [])

    for affix in affixes if isinstance(affixes, list) else []:
        affix_id = affix.get("id", "?")
        for roll in affix.get("rolls", []):
            # affixes.json uses "stat" not "stat_id"
            stat = roll.get("stat", roll.get("stat_id", ""))
            if stat and stat not in valid_stats:
                errors.append(f"[affixes.json] Unknown stat '{stat}' in affix '{affix_id}'")
    return errors


def validate_equipment_stats(db: Path, valid_stats: set) -> list:
    """Check all stat names in equipment_stats.json."""
    errors = []
    path = db / "items" / "equipment_stats.json"
    if not path.exists():
        return []

    data = load_json(path)

    def check_stat_in_obj(obj, context):
        if isinstance(obj, dict):
            for key, val in obj.items():
                if key == "stat_id" and isinstance(val, str) and val not in valid_stats:
                    errors.append(f"[equipment_stats.json] Unknown stat '{val}' in {context}")
                elif key == "stat" and isinstance(val, str) and val not in valid_stats:
                    errors.append(f"[equipment_stats.json] Unknown stat '{val}' in {context}")
                elif isinstance(val, (dict, list)):
                    check_stat_in_obj(val, f"{context}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_stat_in_obj(item, f"{context}[{i}]")

    check_stat_in_obj(data, "root")
    return errors


def validate_class_tags(db: Path) -> list:
    """Check all class_tags in equipment.json are valid."""
    errors = []
    valid_classes = {"warrior", "mage", "healer", "archer", "rogue", "artisan"}

    path = db / "items" / "equipment.json"
    if not path.exists():
        return []

    data = load_json(path)

    def check_items(items, context):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    item_id = item.get("id", "?")
                    for tag in item.get("class_tags", []):
                        if tag not in valid_classes:
                            errors.append(
                                f"[equipment.json] Unknown class_tag '{tag}' in item '{item_id}' ({context})")
        elif isinstance(items, dict):
            for key, val in items.items():
                check_items(val, f"{context}.{key}")

    base_items = data.get("base_items", data)
    check_items(base_items, "base_items")
    return errors


def collect_all_item_ids(db: Path) -> set:
    """Collect all item IDs from all item files."""
    ids = set()
    item_files = [
        "items/consumables.json",
        "items/materials.json",
        "items/equipment.json",
        "items/panoplies.json",
        "items/uniques.json",
    ]

    for rel_path in item_files:
        path = db / rel_path
        if not path.exists():
            continue
        data = load_json(path)

        def extract_ids(obj):
            if isinstance(obj, dict):
                if "id" in obj:
                    ids.add(obj["id"])
                for val in obj.values():
                    extract_ids(val)
            elif isinstance(obj, list):
                for item in obj:
                    extract_ids(item)

        extract_ids(data)

    return ids


def validate_loot_table_refs(db: Path, all_item_ids: set) -> list:
    """Check loot table item references exist."""
    errors = []
    path = db / "items" / "loot_tables.json"
    if not path.exists():
        return []

    data = load_json(path)

    def check_refs(obj, context):
        if isinstance(obj, dict):
            # Check item_id fields
            for key in ("item_id", "item_template_id", "template_id"):
                if key in obj:
                    ref = obj[key]
                    if isinstance(ref, str) and ref and ref not in all_item_ids:
                        # Allow pattern-based refs (e.g., "equip_*", "mat_*")
                        if not any(c in ref for c in ("*", "{", "random")):
                            errors.append(
                                f"[loot_tables.json] Unknown item_id '{ref}' in {context}")
            for key, val in obj.items():
                check_refs(val, f"{context}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_refs(item, f"{context}[{i}]")

    check_refs(data, "root")
    return errors


def validate_set_ids(db: Path) -> list:
    """Check set_id references against panoplies.json."""
    errors = []
    pano_path = db / "items" / "panoplies.json"
    if not pano_path.exists():
        return []

    pano_data = load_json(pano_path)
    valid_set_ids = set()

    # Collect set IDs from panoplies
    if isinstance(pano_data, dict):
        for key, val in pano_data.items():
            if isinstance(val, dict) and ("pieces" in val or "bonuses" in val):
                valid_set_ids.add(key)
            elif key == "sets" and isinstance(val, (list, dict)):
                if isinstance(val, list):
                    for s in val:
                        if isinstance(s, dict) and "id" in s:
                            valid_set_ids.add(s["id"])
                elif isinstance(val, dict):
                    for s_key in val:
                        valid_set_ids.add(s_key)

    # Check equipment.json for set_id references
    equip_path = db / "items" / "equipment.json"
    if equip_path.exists():
        equip_data = load_json(equip_path)

        def check_set_refs(obj, context):
            if isinstance(obj, dict):
                if "set_id" in obj and obj["set_id"]:
                    sid = obj["set_id"]
                    if sid not in valid_set_ids:
                        errors.append(
                            f"[equipment.json] Unknown set_id '{sid}' in {context}")
                for key, val in obj.items():
                    check_set_refs(val, f"{context}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_set_refs(item, f"{context}[{i}]")

        check_set_refs(equip_data, "equipment")

    return errors


def validate_recipe_outputs(db: Path, all_item_ids: set) -> list:
    """Check all recipe output_item references exist in the item database.

    Bug historique (2026-08-03) : la nomenclature des capes est passee de
    cloth/silk a light/medium/heavy sans que les recettes suivent. Deux recettes
    produisaient un item fantome (cape_cloth_b1, cape_silk_b3) -> pas de nom, pas
    d'icone, pas de stats cote client. loot_tables etait valide mais PAS les
    output_item des recettes. Cette passe ferme le trou.
    """
    errors = []
    path = db / "items" / "recipes.json"
    if not path.exists():
        return []

    data = load_json(path)

    # Une recette n'a PAS de nom a elle : elle s'affiche par son output_item, qui porte
    # deja name_fr/name_en. Ecrire un nom ici creerait une deuxieme source pour le meme
    # texte, a traduire et a maintenir deux fois — et a laisser deriver. Audit client du
    # 2026-08-14 : "110 recettes sans name_fr/name_en" remonte comme un defaut. Il y en a
    # 49, et l'absence est le comportement correct ; c'est cote client que le nom se
    # resout depuis output_item.
    for recipe in data.get("recipes", []):
        if not isinstance(recipe, dict):
            continue
        named = [k for k in ("name_fr", "name_en") if k in recipe]
        if named:
            errors.append(
                f"[recipes.json] la recette '{recipe.get('id', '?')}' porte {named} : une "
                f"recette s'affiche par le nom de son output_item, pas par un nom propre. "
                f"Deux sources pour le meme texte = derive garantie.")

    def check_recipes(obj, context):
        if isinstance(obj, dict):
            out = obj.get("output_item")
            if isinstance(out, str) and out and out not in all_item_ids:
                if not any(c in out for c in ("*", "{", "random")):
                    rid = obj.get("id", "?")
                    errors.append(
                        f"[recipes.json] Unknown output_item '{out}' in recipe '{rid}' ({context})")
            for key, val in obj.items():
                check_recipes(val, f"{context}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_recipes(item, f"{context}[{i}]")

    check_recipes(data, "root")
    return errors


# Sequence canonique des labels de rang. Ce n'est PAS une 4e copie de la table :
# c'est le contrat que le CLIENT code en dur (`RANK_LETTERS` dans
# kanarion_front/scripts/data/loaders/item_database.gd) pour traduire un label en
# numero de rang. Si un label derive dans la data, le client ne resout plus le
# rang et l'item retombe silencieusement a 0 — d'ou le check ici.
CANONICAL_RANK_LABELS = ["C", "B", "A", "S", "SS"]


def validate_item_ranks(db: Path) -> list:
    """Verifie que les 5 paliers de rang d'item concordent entre leurs 3 copies.

    Les memes bandes de niveau (lv1-20 / 21-40 / 41-60 / 61-80 / 81-100 = C->SS)
    sont recopiees dans trois fichiers, chacun lu par des consommateurs distincts :

      - items/panoplies.json        `_meta.rank_system.rang_N`
        -> shared/domain/panoplie_registry.cpp, item_database.gd (bandes
           GENERALES de rang cote client), inventory_screen.gd
      - items/uniques.json          `_meta.rank_system.rang_N`
        -> unique_item_registry.cpp, unique_static_registry.cpp,
           unique_effect_text.gd
      - items/equipment_scaling.json `tier_system.tiers.TN`
        -> stat_roller.cpp, affix_roller.cpp

    Personne ne lit la table d'un autre : ce sont trois copies independantes.
    Aujourd'hui elles concordent. Le risque n'est pas le desordre, c'est la
    DERIVE SILENCIEUSE : le jour ou l'une bouge seule, rien ne le signale et le
    bug se manifeste comme un ecart de multiplicateur invisible en test. Cette
    passe est la garde. Elle ne remplace pas le rangement propre
    (_meta/item_ranks.json), elle rend son absence sans danger.

    Verifie : les bornes de niveau, les labels C->SS, les stat_multiplier, la
    contiguite des bandes sur 1..100, et l'absence de retour de l'homonyme
    `rank_system` dans recipes.json (rangs de CRAFT, semantique incompatible,
    renomme `craft_ranks` le 2026-08-13).
    """
    errors = []

    def band_key(i):
        return "rang_%d" % i

    # --- Chargement des 3 tables -------------------------------------------
    pano_path = db / "items" / "panoplies.json"
    uniq_path = db / "items" / "uniques.json"
    scal_path = db / "items" / "equipment_scaling.json"

    tables = {}  # nom affiche -> { rank_index -> {level_range, rank_label, stat_multiplier} }

    if pano_path.exists():
        rs = load_json(pano_path).get("_meta", {}).get("rank_system", {})
        tables["panoplies.json _meta.rank_system"] = {
            i: rs[band_key(i)] for i in range(1, 6)
            if isinstance(rs.get(band_key(i)), dict)
        }
    if uniq_path.exists():
        rs = load_json(uniq_path).get("_meta", {}).get("rank_system", {})
        tables["uniques.json _meta.rank_system"] = {
            i: rs[band_key(i)] for i in range(1, 6)
            if isinstance(rs.get(band_key(i)), dict)
        }
    if scal_path.exists():
        tiers = load_json(scal_path).get("tier_system", {}).get("tiers", {})
        tables["equipment_scaling.json tier_system.tiers"] = {
            i: tiers["T%d" % i] for i in range(1, 6)
            if isinstance(tiers.get("T%d" % i), dict)
        }

    if not tables:
        return ["[item_ranks] Aucune table de rang trouvee (les 3 fichiers sont absents ?)"]

    for name, bands in tables.items():
        missing = [i for i in range(1, 6) if i not in bands]
        if missing:
            errors.append(
                f"[item_ranks] {name} : rang(s) manquant(s) {missing} — la table doit "
                f"couvrir les 5 paliers C->SS")

    # --- Bornes de niveau identiques partout -------------------------------
    for i in range(1, 6):
        seen = {}
        for name, bands in tables.items():
            band = bands.get(i)
            if not band:
                continue
            span = band.get("level_range")
            if not (isinstance(span, list) and len(span) == 2):
                errors.append(f"[item_ranks] {name} rang {i} : level_range absent ou malforme")
                continue
            seen[name] = (int(span[0]), int(span[1]))
        if len(set(seen.values())) > 1:
            detail = ", ".join(f"{n}={v}" for n, v in sorted(seen.items()))
            errors.append(
                f"[item_ranks] DERIVE rang {i} : les bornes de niveau divergent — {detail}")

    # --- Labels C->SS ------------------------------------------------------
    # Le champ dont le client se sert pour resoudre le rang : une derive ici est
    # silencieuse cote joueur (rang non resolu, pas d'erreur).
    for i in range(1, 6):
        expected = CANONICAL_RANK_LABELS[i - 1]
        for name, bands in tables.items():
            band = bands.get(i)
            if not band:
                continue
            if "rank_label" not in band:
                # equipment_scaling n'a jamais porte de label (ses cles sont T1..T5).
                # On n'en exige un que sur les tables qui en declarent au moins un.
                if any("rank_label" in b for b in bands.values()):
                    errors.append(f"[item_ranks] {name} rang {i} : rank_label manquant")
                continue
            actual = str(band["rank_label"])
            if actual != expected:
                errors.append(
                    f"[item_ranks] DERIVE rang {i} : {name} porte rank_label "
                    f"'{actual}', attendu '{expected}' (contrat RANK_LETTERS du client)")

    # --- Multiplicateurs de stats ------------------------------------------
    for i in range(1, 6):
        seen = {}
        for name, bands in tables.items():
            band = bands.get(i)
            if band and "stat_multiplier" in band:
                seen[name] = float(band["stat_multiplier"])
        if len(set(seen.values())) > 1:
            detail = ", ".join(f"{n}={v}" for n, v in sorted(seen.items()))
            errors.append(
                f"[item_ranks] DERIVE rang {i} : les stat_multiplier divergent — {detail}")

    # --- Contiguite des bandes sur 1..100 ----------------------------------
    for name, bands in tables.items():
        spans = []
        for i in range(1, 6):
            band = bands.get(i)
            span = band.get("level_range") if band else None
            if isinstance(span, list) and len(span) == 2:
                spans.append((i, int(span[0]), int(span[1])))
        if len(spans) != 5:
            continue
        if spans[0][1] != 1:
            errors.append(f"[item_ranks] {name} : la premiere bande demarre a {spans[0][1]}, attendu 1")
        if spans[-1][2] != 100:
            errors.append(f"[item_ranks] {name} : la derniere bande finit a {spans[-1][2]}, attendu 100")
        for (i, lo, hi), (j, next_lo, _) in zip(spans, spans[1:]):
            if hi >= next_lo:
                errors.append(
                    f"[item_ranks] {name} : rang {i} ({lo}-{hi}) chevauche rang {j} (demarre a {next_lo})")
            elif next_lo != hi + 1:
                errors.append(
                    f"[item_ranks] {name} : trou de niveaux entre rang {i} (finit a {hi}) "
                    f"et rang {j} (demarre a {next_lo})")

    # --- L'homonyme ne doit pas revenir ------------------------------------
    rec_path = db / "items" / "recipes.json"
    if rec_path.exists():
        if "rank_system" in load_json(rec_path).get("_meta", {}):
            errors.append(
                "[item_ranks] recipes.json _meta.rank_system est de retour : ce sont les rangs "
                "de CRAFT (bandes de 10 niveaux), semantique incompatible avec les 5 rangs "
                "d'item C->SS. Utiliser la cle `craft_ranks`.")

    return errors


def validate_rewards(db: Path) -> list:
    """Verifie le contrat de config/rewards.json, proprietaire unique des recompenses.

    Trois familles de checks :

    1. COHERENCE INTERNE — toute famille nommee dans formula.families_order existe dans
       multiplier_families, et toute famille declaree est nommee dans l'ordre. Sans ca, une
       famille ajoutee mais oubliee de l'ordre serait silencieusement ignoree par le moteur :
       exactement le mode de panne qu'on vient de passer trois jours a extirper.

    2. EGALITE AVEC LES SOURCES D'ORIGINE — pendant l'etape 1/2 de la migration, rewards.json
       et les blocs qu'il remplace coexistent. Cette passe est la preuve MECANISEE que le
       refactor est un no-op : si un chiffre diverge, la CI le dit. Quand un bloc d'origine
       disparait (etape 2), son check se desactive tout seul.

    3. DERIVATION DE L'XP PAR MONSTRE — le xp_multiplier d'un mob doit valoir celui de son
       threat_tier, sauf override declare. C'est ce qui empeche les 180 copies manuelles de
       reapparaitre et de deriver comme l'avaient fait mob_wolf_soigneur et mob_hyene_soigneur
       (1.5 au lieu de 1.6, sans trace de decision).
    """
    errors = []
    rw_path = db / "config" / "rewards.json"
    if not rw_path.exists():
        return ["[rewards] config/rewards.json est introuvable — c'est le proprietaire unique "
                "des recompenses, il ne peut pas manquer"]

    rw = load_json(rw_path)
    families = rw.get("multiplier_families", {})
    order = rw.get("formula", {}).get("families_order", [])

    # --- 1. Coherence interne ----------------------------------------------
    for name in order:
        if name not in families:
            errors.append(f"[rewards] formula.families_order nomme '{name}', absente de "
                          f"multiplier_families — le moteur composerait un facteur inexistant")
    for name in families:
        if name not in order:
            errors.append(f"[rewards] la famille '{name}' est declaree mais absente de "
                          f"formula.families_order — elle serait silencieusement ignoree")

    def fam_values(name):
        return families.get(name, {}).get("values", {})

    # --- 2. Egalite avec les sources d'origine ------------------------------
    def compare(label, live, new, keys):
        """Compare deux tables de multiplicateurs sur les clefs demandees."""
        for entry, src in live.items():
            if entry in ("description", "reference") or entry.startswith("_"):
                continue
            dst = new.get(entry)
            if dst is None:
                errors.append(f"[rewards] {label} : '{entry}' existe dans la source d'origine "
                              f"mais pas dans rewards.json")
                continue
            for k in keys:
                if k not in src:
                    continue
                if abs(float(src[k]) - float(dst.get(k, "nan" if False else 0))) > 1e-6:
                    errors.append(f"[rewards] DERIVE {label}.{entry}.{k} : origine={src[k]} "
                                  f"rewards.json={dst.get(k)} — le refactor devait etre un no-op")

    lt_path = db / "items" / "loot_tables.json"
    if lt_path.exists():
        lt = load_json(lt_path)
        mults = lt.get("multipliers", {})
        num = ("gold", "xp", "drop_chance", "rarity_boost")
        for legacy, fam in (("monster_state", "monster_state"),
                            ("encounter_stars", "encounter_stars"),
                            ("dungeon_difficulty", "dungeon_difficulty")):
            if legacy in mults:
                compare(legacy, mults[legacy], fam_values(fam), num)
        if "act_progression" in mults:
            compare("act_progression", mults["act_progression"],
                    fam_values("act_progression"), ("gold",))
        if "global_cap" in mults:
            a = float(mults["global_cap"].get("max_total_multiplier", 0))
            b = float(rw.get("global_cap", {}).get("max_total_multiplier", -1))
            if abs(a - b) > 1e-6:
                errors.append(f"[rewards] DERIVE global_cap : origine={a} rewards.json={b}")
        if "level_difference" in mults:
            ld_live, ld_new = mults["level_difference"], rw.get("level_difference", {})
            for k in ("no_penalty_range", "penalty_per_level", "max_penalty"):
                if k in ld_live and abs(float(ld_live[k]) - float(ld_new.get(k, -1))) > 1e-6:
                    errors.append(f"[rewards] DERIVE level_difference.{k} : "
                                  f"origine={ld_live[k]} rewards.json={ld_new.get(k)}")
        ev_live = lt.get("events", {}).get("event_types", {})
        ev_new = fam_values("events")
        for name, body in ev_live.items():
            if name.startswith("_") or not isinstance(body, dict):
                continue
            compare("events", {name: body.get("bonuses", {})}, ev_new, num)

    # Bonus de groupe : ancre sur les CONSTANTES DU MOTEUR, pas sur la table de loot_tables.
    #
    # La v1.0 de ce check comparait a 0.05, la valeur de items/loot_tables.json — une table
    # morte, que content_loader.cpp:1527 charge pourtant dans un champ
    # (group_size_bonus_per_player) qu'aucun code ne lit ensuite. Le moteur applique en
    # realite 1 + (N-1) * 0.055 plafonne a 1.5, depuis des defauts de struct
    # (loot_types.hpp:209-210) qu'aucun fichier ne charge. Le check etait donc aveugle a un
    # ecart reel : 1.165 contre 1.20 a quatre joueurs. Attrape par une contre-lecture du
    # backend le 2026-08-14, pas par cette garde — d'ou la reecriture.
    #
    # Tant que le moteur ne lit pas ces deux valeurs depuis la donnee (etape 2), l'ancre est
    # manuelle : elle fige ce que le C++ applique, pour qu'une edition de la donnee seule ne
    # puisse pas se croire effective.
    ENGINE_GROUP_BONUS_PER_EXTRA = 0.055   # loot_types.hpp:209
    ENGINE_GROUP_CAP = 1.5                 # loot_types.hpp:210
    gs = families.get("group_size", {})
    for field, engine, where in (("bonus_per_extra_player", ENGINE_GROUP_BONUS_PER_EXTRA,
                                  "loot_types.hpp:209"),
                                 ("cap", ENGINE_GROUP_CAP, "loot_types.hpp:210")):
        if field not in gs:
            errors.append(f"[rewards] group_size.{field} est absent — le moteur applique "
                          f"{engine} ({where}), la donnee doit le dire")
        elif abs(float(gs[field]) - engine) > 1e-9:
            errors.append(f"[rewards] group_size.{field}={gs[field]} alors que le moteur "
                          f"applique {engine} ({where}). Changer la donnee seule ne change "
                          f"rien au jeu : ces valeurs sont encore des constantes C++.")
    if "bonus_per_player" in gs or "max_players" in gs:
        errors.append("[rewards] group_size porte bonus_per_player/max_players : c'est la "
                      "forme de la table MORTE de loot_tables (1 + N * 0.05). Le moteur "
                      "applique 1 + (N-1) * 0.055 plafonne. Utiliser "
                      "bonus_per_extra_player + cap.")

    mt_path = db / "config" / "monster_tiers.json"
    tier_xp = {}
    if mt_path.exists():
        for name, body in load_json(mt_path).get("threat_tiers", {}).items():
            if isinstance(body, dict) and "xp_multiplier" in body:
                tier_xp[name] = float(body["xp_multiplier"])
        for name, live in tier_xp.items():
            new = fam_values("monster_threat_tier").get(name, {}).get("xp")
            if new is None or abs(live - float(new)) > 1e-6:
                errors.append(f"[rewards] DERIVE monster_threat_tier.{name}.xp : "
                              f"origine={live} rewards.json={new}")
    if not tier_xp:
        tier_xp = {n: float(v.get("xp", 1.0))
                   for n, v in fam_values("monster_threat_tier").items()}

    # --- 3. Derivation de l'XP par monstre ----------------------------------
    overrides = (rw.get("inputs_declared_elsewhere", {})
                   .get("xp_multiplier_par_monstre", {})
                   .get("known_overrides", {}))
    mon_path = db / "entities" / "monsters.json"
    if mon_path.exists() and tier_xp:
        data = load_json(mon_path)
        monsters = data.get("monsters", data)
        if isinstance(monsters, dict):
            monsters = list(monsters.values())
        for mon in monsters if isinstance(monsters, list) else []:
            if not isinstance(mon, dict) or "xp_multiplier" not in mon:
                continue
            mid = mon.get("id", "?")
            tier = mon.get("threat_tier")
            if tier not in tier_xp:
                continue
            if abs(float(mon["xp_multiplier"]) - tier_xp[tier]) <= 1e-6:
                continue
            if mid not in overrides:
                errors.append(
                    f"[rewards] {mid} porte xp_multiplier={mon['xp_multiplier']} alors que son "
                    f"palier '{tier}' vaut {tier_xp[tier]}, et il n'est pas declare comme "
                    f"override dans rewards.json inputs_declared_elsewhere. Soit c'est une "
                    f"copie qui a derive, soit c'est un choix — dans ce cas, declare-le.")

    return errors


def main():
    # Find database root
    db_root = os.environ.get("DB_ROOT", "")
    if db_root:
        db = Path(db_root)
    elif Path("stats/definitions.json").exists():
        db = Path(".")
    elif Path("kanarion_database/stats/definitions.json").exists():
        db = Path("kanarion_database")
    else:
        print("ERROR: Cannot find kanarion_database. Set DB_ROOT or run from db directory.")
        sys.exit(1)

    print(f"Validating cross-references in: {db.resolve()}")
    print("=" * 60)

    # Load canonical stats
    defs_path = db / "stats" / "definitions.json"
    if not defs_path.exists():
        print(f"ERROR: {defs_path} not found")
        sys.exit(1)

    defs = load_json(defs_path)
    valid_stats = collect_canonical_stats(defs)
    print(f"Loaded {len(valid_stats)} canonical stat IDs")

    # Run all validations
    all_errors = []

    print("\n[1/8] Validating affix stat names...")
    errs = validate_affixes(db, valid_stats)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[2/8] Validating equipment_stats stat names...")
    errs = validate_equipment_stats(db, valid_stats)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[3/8] Validating class_tags...")
    errs = validate_class_tags(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[4/8] Validating loot table item references...")
    all_item_ids = collect_all_item_ids(db)
    print(f"  Collected {len(all_item_ids)} item IDs from database")
    errs = validate_loot_table_refs(db, all_item_ids)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[5/8] Validating set_id references...")
    errs = validate_set_ids(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[6/8] Validating recipe output_item references...")
    errs = validate_recipe_outputs(db, all_item_ids)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[7/8] Validating item rank bands (C->SS) across their 3 copies...")
    errs = validate_item_ranks(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[8/8] Validating rewards contract (config/rewards.json)...")
    errs = validate_rewards(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    # Report
    print("\n" + "=" * 60)
    if all_errors:
        print(f"VALIDATION FAILED — {len(all_errors)} error(s):\n")
        for e in all_errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED — all cross-references OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
