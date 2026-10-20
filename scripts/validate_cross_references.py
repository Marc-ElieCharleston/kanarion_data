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
  11. Item display contract: every rollable stat has declared bounds, every
      affix is nameable and described, no socket without gem data
  13. Single sources of gameplay values: each value the server reads from ONE
      file is present there, and every client-facing mirror equals it

Exit code 0 = pass, 1 = failures found.
"""

import json
import re
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
        "hp", "mp", "atk", "mag", "armor", "magic_resist",
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
        "items/pet_books.json",
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


def validate_every_monster_has_loot_table(db: Path) -> list:
    """Every monster resolves to ITS OWN loot table (owner 2026-10-13: no 'default' fallback).

    Resolution mirrors server-combat LootRoller: `loot_table_id`, else the template id
    without its mob_ / boss_ prefix. An explicit empty list is allowed (training dummy).
    """
    errors = []
    lt_path = db / "items" / "loot_tables.json"
    mon_path = db / "entities" / "monsters.json"
    if not lt_path.exists() or not mon_path.exists():
        return errors
    tables = load_json(lt_path).get("monster_loot_tables", {})
    if "default" in tables:
        errors.append("[loot_tables.json] monster_loot_tables.default est revenue : plus de table "
                      "par defaut, chaque monstre a la sienne (decision 2026-10-13)")
    mons = load_json(mon_path)
    mons = mons.get("monsters", mons)
    entries = mons.items() if isinstance(mons, dict) else [(m.get("id"), m) for m in mons]
    for mid, m in entries:
        if not isinstance(m, dict) or not isinstance(mid, str) or mid.startswith("_"):
            continue
        tid = m.get("loot_table_id") or next(
            (mid[len(p):] for p in ("mob_", "boss_") if mid.startswith(p)), mid)
        if tid not in tables:
            errors.append(f"[loot_tables.json] le monstre '{mid}' n'a pas de table de loot "
                          f"(cherche '{tid}') : en ajouter une dans monster_loot_tables "
                          f"(liste vide explicite si le monstre ne donne rien)")
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


def validate_enhancement_rates(db: Path) -> list:
    """stone_ranks.*.success_rates : un taux par niveau de la tranche.

    Le serveur (enhancement_rules.cpp) REFUSE tout le fichier si une tranche n'a
    pas exactement un taux par niveau : la forge entiere serait coupee. On
    l'arrete donc ici, avant le push.
    """
    errors = []
    path = db / "systems" / "enhancement_system.json"
    if not path.exists():
        return ["[enhancement_system.json] fichier absent"]
    data = load_json(path)
    for rid, rank in data.get("stone_ranks", {}).items():
        band = rank.get("enhancement_range", [])
        rates = rank.get("success_rates")
        if "success_rate" in rank:
            errors.append(f"[enhancement_system.json] {rid} : 'success_rate' (un seul taux) n'est plus lu, "
                          f"utiliser 'success_rates' (un taux par niveau)")
        if not isinstance(band, list) or len(band) < 2:
            errors.append(f"[enhancement_system.json] {rid} : enhancement_range invalide")
            continue
        size = band[1] - band[0] + 1
        if not isinstance(rates, list) or len(rates) != size:
            errors.append(f"[enhancement_system.json] {rid} : success_rates doit avoir {size} valeurs "
                          f"(+{band[0]} a +{band[1]}), trouve {rates!r}")
            continue
        for i, v in enumerate(rates):
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not (0 < v <= 100):
                errors.append(f"[enhancement_system.json] {rid} +{band[0] + i} : taux {v!r} hors de ]0, 100]")
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

    # Meme regles que le serveur (services/economy/src/inventory/recipe_registry.cpp),
    # qui REJETTE une recette mal ecrite au demarrage. Les verifier ici arrete la
    # recette avant le push, au lieu de la voir disparaitre en jeu. Un champ absent
    # n'a PAS de valeur par defaut : un `qty` ecrit `quantity` rendait la recette
    # moins chere, un materiau sans `id` la rendait gratuite.
    def is_int(v, minimum):
        return isinstance(v, int) and not isinstance(v, bool) and v >= minimum

    seen = set()
    for i, recipe in enumerate(data.get("recipes", [])):
        if not isinstance(recipe, dict):
            errors.append(f"[recipes.json] entree {i} n'est pas un objet")
            continue
        rid = recipe.get("id")
        if not isinstance(rid, str) or not rid:
            errors.append(f"[recipes.json] entree {i} sans id")
            continue
        if rid in seen:
            errors.append(f"[recipes.json] id en double : '{rid}' (le serveur garde la premiere)")
        seen.add(rid)
        for key, minimum in (("output_qty", 1), ("level_req", 1), ("gold_cost", 0)):
            if not is_int(recipe.get(key), minimum):
                errors.append(f"[recipes.json] '{rid}' : '{key}' absent ou invalide "
                              f"(entier >= {minimum} attendu, trouve {recipe.get(key)!r})")
        mats = recipe.get("materials")
        if not isinstance(mats, list):
            errors.append(f"[recipes.json] '{rid}' : 'materials' absent (liste attendue)")
            continue
        for m in mats:
            mid = m.get("id") if isinstance(m, dict) else None
            if not isinstance(mid, str) or not mid:
                errors.append(f"[recipes.json] '{rid}' : materiau sans 'id' ({m!r})")
                continue
            if mid not in all_item_ids:
                errors.append(f"[recipes.json] '{rid}' : materiau inconnu '{mid}'")
            if not is_int(m.get("qty"), 1):
                errors.append(f"[recipes.json] '{rid}' : 'qty' de '{mid}' absent ou invalide ({m.get('qty')!r})")
            if mid == recipe.get("output_item"):
                errors.append(f"[recipes.json] '{rid}' consomme son propre produit '{mid}'")
        if not mats and recipe.get("gold_cost") == 0:
            errors.append(f"[recipes.json] '{rid}' ne coute rien (ni materiau ni or)")
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


# Lettre AFFICHEE d'un rang interne (decision produit 2026-10-01). L'interne reste
# C..SS partout (ids, champs `rank`, DB) ; le joueur lit D..S. Recopie ici de
# systems/professions.json quality.display_letters pour que la garde ne valide pas
# une table contre elle-meme : les deux doivent concorder.
DISPLAY_RANK_LETTERS = {"C": "D", "B": "C", "A": "B", "S": "A", "SS": "S"}

# Cles de texte joueur scannees par la garde globale.
_PLAYER_TEXT_KEY = re.compile(
    r"^(name|title|description|summary|dialogue|content|text|tooltip|hint_text|label|lines)"
    r"(_[a-z]+)*$")
# Formes qui ne peuvent venir que d'une lettre INTERNE recopiee dans un texte.
_INTERNAL_LETTER_TEXT = re.compile(
    r"\(SS\)|\b(rang|rank) SS\b|\bSS-rank\b|\b(à|to|->|→) ?SS\b|\bS et SS\b|\bS and SS\b")


def validate_rank_display(db: Path) -> list:
    """Verifie que tout texte joueur porte la lettre AFFICHEE (D..S), jamais l'interne.

    1. `quality.display_letters` (systems/professions.json) == la table canonique.
    2. Koro, grimoires, stigmates : le suffixe ' (X)' des noms et 'au rang X' /
       'at rank X' des descriptions valent DISPLAY[rank interne].
    3. Contrats : '(rang X)' / '(rank X)' du titre vaut DISPLAY[contract_rank].
    4. Variantes de ressource : name_suffix_* vaut ' (DISPLAY[id])' (vide pour C).
    5. Garde globale : aucun texte joueur ne montre '(SS)', 'rang SS', 'C a SS'...
       (le changelog, historique, est exclu).
    """
    errors = []
    tag = "[rank_display]"
    prof = load_json(db / "systems" / "professions.json")
    q = prof.get("quality", {})
    if q.get("display_letters") != DISPLAY_RANK_LETTERS:
        errors.append(f"{tag} systems/professions.json quality.display_letters != {DISPLAY_RANK_LETTERS}")
    if list(DISPLAY_RANK_LETTERS) != CANONICAL_RANK_LABELS or q.get("ranks") != CANONICAL_RANK_LABELS:
        errors.append(f"{tag} rangs internes != {CANONICAL_RANK_LABELS}")

    def check_name(where, item, key, rank):
        val = item.get(key)
        if val is None:
            return
        want = f"({DISPLAY_RANK_LETTERS.get(rank, '?')})"
        if not val.endswith(want):
            errors.append(f"{tag} {where} {item.get('id')} {key}={val!r} : attendu suffixe {want} (rang interne {rank})")

    def check_phrase(where, item, key, word, rank):
        val = item.get(key)
        if not val:
            return
        for m in re.finditer(r"\b" + word + r" (SS|S|A|B|C|D)\b", val):
            if m.group(1) != DISPLAY_RANK_LETTERS.get(rank):
                errors.append(f"{tag} {where} {item.get('id')} {key} : '{m.group(0)}' pour le rang interne {rank}")

    sources = [("items/koro_cards.json", "koro_cards"), ("items/pet_books.json", "pet_books"),
               ("items/keystone_items.json", "keystone_items")]
    for rel, list_key in sources:
        path = db / rel
        if not path.exists():
            continue
        for item in load_json(path).get(list_key, []):
            rank = item.get("rank")
            if not rank:
                continue
            if rank not in DISPLAY_RANK_LETTERS:
                errors.append(f"{tag} {rel} {item.get('id')} rang interne inconnu {rank!r}")
                continue
            for k in ("name_fr", "name_en"):
                check_name(rel, item, k, rank)
            check_phrase(rel, item, "description_fr", "au rang", rank)
            check_phrase(rel, item, "description_en", "at rank", rank)

    # Recettes a regle (fusion / revelation Koro, copie de grimoire) : chaque 'au rang X' /
    # 'at rank X' de leur texte doit etre la lettre affichee de input_rank ou output_rank.
    recipes_path = db / "items" / "profession_recipes.json"
    if recipes_path.exists():
        for rule in load_json(recipes_path).get("rule_recipes", []):
            allowed = {DISPLAY_RANK_LETTERS.get(rule.get(k)) for k in ("input_rank", "output_rank")} - {None}
            for key, word in (("description_fr", "au rang"), ("description_en", "at rank")):
                for m in re.finditer(r"\b" + word + r" (SS|S|A|B|C|D)\b", rule.get(key, "")):
                    if m.group(1) not in allowed:
                        errors.append(f"{tag} profession_recipes {rule.get('id')} {key} : '{m.group(0)}' "
                                      f"hors des rangs affiches {sorted(allowed)}")

    quests_path = db / "world" / "quests.json"
    if quests_path.exists():
        for quest in load_json(quests_path).get("quests", []):
            rank = quest.get("contract_rank")
            if not rank:
                continue
            for key, word in (("title_fr", "rang"), ("title_en", "rank")):
                want = f"({word} {DISPLAY_RANK_LETTERS.get(rank, '?')})"
                if not str(quest.get(key, "")).endswith(want):
                    errors.append(f"{tag} quests {quest.get('id')} {key} : attendu {want} (contract_rank {rank})")

    for tier in prof.get("resource_rarity", {}).get("tiers", []):
        tid = tier.get("id")
        want = "" if tid == "C" else f" ({DISPLAY_RANK_LETTERS.get(tid, '?')})"
        for key in ("name_suffix_fr", "name_suffix_en"):
            if tier.get(key) != want:
                errors.append(f"{tag} professions resource_rarity {tid} {key}={tier.get(key)!r} : attendu {want!r}")

    def scan(node, rel, key=""):
        if isinstance(node, dict):
            for k, v in node.items():
                if not k.startswith("_"):
                    scan(v, rel, k)
        elif isinstance(node, list):
            for v in node:
                scan(v, rel, key)
        elif isinstance(node, str) and _PLAYER_TEXT_KEY.match(key):
            m = _INTERNAL_LETTER_TEXT.search(node)
            if m:
                errors.append(f"{tag} {rel} {key} : lettre interne affichee '{m.group(0)}' dans {node[:80]!r}")

    for path in sorted(db.rglob("*.json")):
        rel = path.relative_to(db).as_posix()
        if rel.startswith((".", "_meta/")) or "/." in rel or "node_modules" in rel:
            continue
        try:
            scan(load_json(path), rel)
        except (ValueError, UnicodeDecodeError):
            continue

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
    # Etape 2 FAITE (2026-08-29) : le moteur lit bonus_per_extra_player + cap DEPUIS
    # config/rewards.json (server-combat content_loader.cpp:1571-1572 ; loot_types.hpp ne
    # garde que des valeurs de repli). L'ancre sur les constantes C++ empechait donc tout
    # reglage (2026-10-13 : courbe rapide jusqu'a 5 joueurs, 0.075 / 1.3). Le check verifie
    # desormais la presence et la coherence des deux valeurs, pas leur egalite au repli.
    gs = families.get("group_size", {})
    for field in ("bonus_per_extra_player", "cap"):
        if field not in gs:
            errors.append(f"[rewards] group_size.{field} est absent : le moteur retombe sur sa "
                          f"valeur de repli (loot_types.hpp), la donnee doit le dire")
    per = gs.get("bonus_per_extra_player")
    cap = gs.get("cap")
    if isinstance(per, (int, float)) and not (0 <= per <= 0.5):
        errors.append(f"[rewards] group_size.bonus_per_extra_player={per} hors de [0, 0.5]")
    if isinstance(cap, (int, float)) and not (1.0 <= cap <= 3.0):
        errors.append(f"[rewards] group_size.cap={cap} hors de [1, 3]")
    if "bonus_per_player" in gs or "max_players" in gs:
        errors.append("[rewards] group_size porte bonus_per_player/max_players : c'est la "
                      "forme de la table MORTE de loot_tables (1 + N * 0.05). Le moteur "
                      "applique 1 + (N-1) * 0.055 plafonne. Utiliser "
                      "bonus_per_extra_player + cap.")

    # config/monster_tiers.json (copie morte) supprime le 2026-10-14 : rewards.json seul.
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


def validate_mercenary_balance_slots(db: Path) -> list:
    """Etape 9 - le profil de balance mercenaire doit correspondre a son CONTEXTE.

    Deux champs, deux contextes, deux lecteurs distincts cote backend :
      - balance_profile      -> PvE, lu par CombatHost::try_spawn_mercenary_for
      - pvp_balance_profile  -> PvP, lu par le chemin arena bot-fill

    Rien dans le format n'empechait d'ecrire un pvp_filler_* dans le slot PvE, et c'est ce
    qui est arrive aux 24 archetypes subclass : un joueur qui en engageait un en PvE recevait
    un bot a x2.2-2.5 degats et x2.8-3.8 PV sans malus de niveau, la ou un mercenaire de base
    est a x1.5 / x2.0 / niveau -2. Invisible en test : les deux profils existent, les deux se
    chargent, seul le contexte est faux.
    """
    errors = []
    mercs_path = db / "entities" / "mercenaries.json"
    bal_path = db / "config" / "mercenary_balance.json"
    if not mercs_path.exists() or not bal_path.exists():
        return errors

    known = set(load_json(bal_path).get("profiles", {}).keys())

    for m in load_json(mercs_path).get("mercenaries", []):
        mid = m.get("id", "<no id>")
        pve = m.get("balance_profile") or ""
        pvp = m.get("pvp_balance_profile") or ""

        if not pve:
            errors.append(f"mercenaries.json: '{mid}' n'a pas de balance_profile (PvE)")
        elif pve.startswith("pvp_filler_"):
            errors.append(
                f"mercenaries.json: '{mid}' porte le profil PvP '{pve}' dans balance_profile "
                f"(slot PvE) - le deplacer dans pvp_balance_profile")
        elif pve not in known:
            errors.append(
                f"mercenaries.json: '{mid}' balance_profile '{pve}' absent de "
                f"config/mercenary_balance.json")

        if pvp and pvp not in known:
            errors.append(
                f"mercenaries.json: '{mid}' pvp_balance_profile '{pvp}' absent de "
                f"config/mercenary_balance.json")

    return errors


def validate_skill_patterns(db: Path) -> list:
    """Etape 10 : tout pattern reference par un sort doit exister dans targeting.json.

    Sans ce controle, un pattern renomme ou mal orthographie passe en silence, et les deux
    bouts du jeu divergent : le serveur ne resout pas l'id, retombe en CIBLE UNIQUE, pendant
    que le client resout son alias et dessine la zone entiere. L'apercu promet une rangee,
    le sort touche une case. Constate le 2026-09-04 sur 3 sorts, apres le renommage
    front_row -> row (d3ceb20) : `row` n'existe pas dans targeting.json.
    """
    errors = []
    targeting = load_json(db / 'combat' / 'targeting.json')
    canonical = {k for k, v in (targeting.get('patterns') or {}).items() if isinstance(v, dict)}
    if not canonical:
        return ["combat/targeting.json: aucun pattern canonique lu, le controle ne peut pas tourner"]

    def walk(node, path):
        if isinstance(node, dict):
            sid = node.get('id')
            if isinstance(sid, str) and sid.startswith('skill_'):
                refs = [('pattern', node.get('pattern'))]
                tgt = node.get('targeting')
                if isinstance(tgt, dict):
                    refs.append(('targeting.aoe_pattern_id', tgt.get('aoe_pattern_id')))
                for field, val in refs:
                    if val and val not in canonical:
                        errors.append(
                            f"{path}: skill '{sid}' {field}='{val}' n'existe pas dans "
                            f"combat/targeting.json patterns")
            for v in node.values():
                walk(v, path)
        elif isinstance(node, list):
            for v in node:
                walk(v, path)

    files = sorted((db / 'classes').glob('*/skills.json')) + sorted((db / 'skills').glob('*.json'))
    for f in files:
        walk(load_json(f), f.relative_to(db).as_posix())
    return errors



def validate_item_display_contract(db: Path, valid_stats: set) -> list:
    """Etape 11 : la data doit pouvoir REMPLIR la fiche d objet unifiee.

    Le client affiche desormais une seule carte d objet (nom, rarete, stats de
    base, tirage principal, substats AVEC leurs bornes, affixes nommes et
    decrits, sockets, comparaison, description). Il ne recalcule rien : chaque
    ligne doit exister quelque part, ici ou dans le payload serveur.

    Ce controle attrape les trous qui rendent une SECTION MUETTE sans jamais
    lever d erreur :
      - une stat tirable sans bornes declarees -> le moteur retombe sur son
        fallback {1,5} en dur, la valeur ignore rarete et multiplicateur substat,
        et la fiche n a aucune plage a montrer (9 cas trouves le 2026-09-07) ;
      - un affixe sans nom ou sans description localisee -> une ligne d affixe
        vide, ou pire, un identifiant interne montre au joueur ;
      - des bornes inversees (min > max) ou une echelle de rarete qui recule.
    """
    errors = []

    # --- 11a. affixes.json : nommable, decrit, tirable ---------------------
    affixes_path = db / "items" / "affixes.json"
    if affixes_path.exists():
        data = load_json(affixes_path)
        vus = {}
        for section in ("prefixes", "suffixes"):
            for affix in data.get(section, []) or []:
                aid = affix.get("id", "")
                if not aid:
                    errors.append("[affixes.json] %s: entree sans id" % section)
                    continue
                if aid in vus:
                    errors.append("[affixes.json] id duplique %s (%s et %s)" % (aid, vus[aid], section))
                vus[aid] = section
                for champ in ("name_fr", "name_en", "description_fr", "description_en"):
                    if not str(affix.get(champ, "")).strip():
                        errors.append("[affixes.json] affixe %s: %s manquant "
                                      "(la fiche d objet le lit pour nommer/decrire l affixe)"
                                      % (aid, champ))
                if not affix.get("allowed_slots"):
                    errors.append("[affixes.json] affixe %s: allowed_slots vide — "
                                  "il ne peut tomber sur aucun objet" % aid)
                if int(affix.get("weight", 0)) <= 0:
                    errors.append("[affixes.json] affixe %s: weight <= 0" % aid)
                lr = affix.get("level_range", [])
                if not (isinstance(lr, list) and len(lr) == 2 and lr[0] <= lr[1]):
                    errors.append("[affixes.json] affixe %s: level_range invalide %s" % (aid, lr))
                rolls = affix.get("rolls", [])
                if not rolls:
                    errors.append("[affixes.json] affixe %s: aucun roll — affixe inerte" % aid)
                for roll in rolls:
                    stat = roll.get("stat", roll.get("stat_id", ""))
                    if "min" not in roll or "max" not in roll:
                        errors.append("[affixes.json] affixe %s stat %s: bornes min/max manquantes"
                                      % (aid, stat))
                    elif roll["min"] > roll["max"]:
                        errors.append("[affixes.json] affixe %s stat %s: min %s > max %s"
                                      % (aid, stat, roll["min"], roll["max"]))

    # --- 11b. equipment_stats.json : toute stat tirable a ses bornes -------
    eq_path = db / "items" / "equipment_stats.json"
    if eq_path.exists():
        data = load_json(eq_path)
        ranges = data.get("stat_ranges_by_rarity", {}).get("main_stats", {})
        declarees = set(k for k in ranges if not k.startswith("_"))
        raretes = [r for r in data.get("rarity_tiers", {}) if not r.startswith("_")]

        # `hybrid` n est pas une stat : c est le marqueur d essence d equilibre,
        # que le roller eclate en atk/mag. Il n a donc pas de bornes propres.
        tirables = set()
        for cat_name, cat in (data.get("equipment_categories") or {}).items():
            for entry in cat.get("substat_pool", []) or []:
                tirables.add(entry.get("stat", ""))
            for opts in (cat.get("main_stat_options") or {}).values():
                tirables.update(opts.get("options", []))
            for opts in (cat.get("main_stat_by_armor_type") or {}).values():
                tirables.update(opts.get("options", []))
            for essence in (cat.get("main_stat_types") or {}).values():
                if essence.get("main_stat"):
                    tirables.add(essence["main_stat"])
        tirables.discard("")
        tirables.discard("hybrid")

        for stat in sorted(tirables - declarees):
            errors.append("[equipment_stats.json] stat tirable %s sans bornes dans "
                          "stat_ranges_by_rarity.main_stats — le moteur retombe sur son "
                          "fallback {1,5} (sans rarete ni x0.5 substat) et la fiche d objet "
                          "n a aucune plage a afficher" % stat)

        for stat in sorted(declarees):
            if stat not in valid_stats:
                errors.append("[equipment_stats.json] bornes declarees pour une stat inconnue %s"
                              % stat)
            precedent = None
            for rarete in raretes:
                bornes = ranges[stat].get(rarete)
                if bornes is None:
                    errors.append("[equipment_stats.json] %s: rarete %s sans bornes"
                                  % (stat, rarete))
                    continue
                if not (isinstance(bornes, list) and len(bornes) == 2):
                    errors.append("[equipment_stats.json] %s / %s: bornes malformees %s"
                                  % (stat, rarete, bornes))
                    continue
                if bornes[0] > bornes[1]:
                    errors.append("[equipment_stats.json] %s / %s: roll_min %s > roll_max %s"
                                  % (stat, rarete, bornes[0], bornes[1]))
                if precedent is not None and bornes[0] < precedent[0]:
                    errors.append("[equipment_stats.json] %s: l echelle de rarete recule a %s "
                                  "(%s apres %s)" % (stat, rarete, bornes, precedent))
                precedent = bornes

    # --- 11c. equipment.json : identite et stats de base lisibles ----------
    equip_path = db / "items" / "equipment.json"
    if equip_path.exists():
        data = load_json(equip_path)
        ids_vus = set()
        for famille, groupes in (data.get("base_items") or {}).items():
            for groupe, items in (groupes or {}).items():
                for item in items or []:
                    iid = item.get("id", "")
                    ou = "base_items.%s.%s" % (famille, groupe)
                    if not iid:
                        errors.append("[equipment.json] %s: objet sans id" % ou)
                        continue
                    if iid in ids_vus:
                        errors.append("[equipment.json] id duplique %s" % iid)
                    ids_vus.add(iid)
                    for champ in ("name_fr", "name_en"):
                        if not str(item.get(champ, "")).strip():
                            errors.append("[equipment.json] %s: %s manquant" % (iid, champ))
                    if int(item.get("level_req", 0)) < 0:
                        errors.append("[equipment.json] %s: level_req negatif" % iid)
                    base = item.get("base_stats") or {}
                    if not base:
                        errors.append("[equipment.json] %s: base_stats vide — la fiche n aurait "
                                      "aucune stat de base a montrer" % iid)
                    for stat in base:
                        if stat not in valid_stats:
                            errors.append("[equipment.json] %s: base_stats reference une stat "
                                          "inconnue %s" % (iid, stat))

    # --- 11d. sockets : rien ne doit referencer une gemme inexistante -----
    # Le systeme de sertissage n existe pas encore (aucune gemme, aucune regle
    # de deblocage, aucun effet serveur). Le controle est donc vide par
    # construction — mais il se declenchera au premier objet qui declare des
    # sockets sans que la data de gemmes suive.
    for fichier in ("equipment.json", "panoplies.json", "uniques.json"):
        chemin = db / "items" / fichier
        if not chemin.exists():
            continue
        brut = chemin.read_text(encoding="utf-8")
        if chr(34) + "sockets" + chr(34) in brut or chr(34) + "socket_slots" + chr(34) in brut:
            if not (db / "items" / "gems.json").exists():
                errors.append("[%s] declare des sockets alors qu aucune data de gemme n existe "
                              "(items/gems.json absent) : la fiche afficherait des emplacements "
                              "que rien ne peut remplir" % fichier)

    return errors


# Sources que le moteur de succes (kanarion_back services/quest, AchievementEngine) sait
# RELIRE en base. Un succes dont la source n'est pas ici n'a aucun ecrivain : il ne se
# debloquerait jamais, et personne ne le signalerait. A tenir en phase avec le moteur.
KNOWN_ACHIEVEMENT_SOURCES = {
    "char_level", "char_stat_points_spent", "char_skill_points_spent", "char_subclass_chosen",
    "quests_completed", "quests_set_completed",
    "arena_matches", "arena_wins", "arena_losses", "arena_matches_2v2", "arena_matches_4v4",
    "arena_best_win_streak",
    "familiar_hatched", "familiar_rare_plus", "familiar_epic_plus", "familiar_legendary",
    "familiar_distinct_roles", "familiar_collection",
    # Vague 2 (2026-09-30, back migr 103 + read_achievement_snapshot)
    "pve_wins", "monsters_killed", "damage_dealt_total", "healing_done_total",
    "dungeon_floors_cleared", "dungeon_runs_completed", "fissures_closed",
    "friends_count", "guild_joined", "auction_items_sold", "max_enhancement_level",
    "koro_cards_owned", "keystones_equipped", "gold_held",
    # Metiers V1 (2026-10-01, back migr 111). Sources parametrees : voir
    # PARAMETERIZED_ACHIEVEMENT_SOURCES.
    "crafts_total", "gathers_total", "recipes_distinct", "crafts_quality_top",
    "crafts_quality_second", "gathers_rarity_top", "gathers_rarity_second",
    "profession_specialties_at_100", "intermediates_crafted", "max_tool_rank_used",
    # Interieur de faille (2026-10-17) : Braises recueillies (economy) et purifications (quest).
    "rift_embers_gathered", "rifts_purified",
}
# Prefixe -> le parametre doit etre un id de metier (profession_level) ou un niveau 1..rules.level_max.
PARAMETERIZED_ACHIEVEMENT_SOURCES = ("profession_level:", "professions_at_or_above:")


def _known_achievement_source(db: Path, source) -> bool:
    if source in KNOWN_ACHIEVEMENT_SOURCES:
        return True
    if not isinstance(source, str):
        return False
    if source.startswith("profession_level:"):
        ids = {p["id"] for p in load_json(db / "systems" / "professions.json").get("professions", [])}
        return source.split(":", 1)[1] in ids
    if source.startswith("professions_at_or_above:"):
        n = source.split(":", 1)[1]
        level_max = load_json(db / "systems" / "professions.json").get("rules", {}).get("level_max", 0)
        return n.isdigit() and 1 <= int(n) <= level_max
    return False


def validate_achievements(db: Path) -> list:
    """systems/achievements.json : source connue du moteur, titre octroyable, quetes existantes."""
    errors = []
    path = db / "systems" / "achievements.json"
    if not path.exists():
        return errors
    data = load_json(path)
    cosmetics = load_json(db / "ui" / "cosmetics.json").get("cosmetics", [])
    grant_titles = {c["id"] for c in cosmetics
                    if c.get("type") == "title" and c.get("acquisition") == "grant"}
    quests = {q["id"] for q in load_json(db / "world" / "quests.json").get("quests", [])}
    categories = {c["id"] for c in data.get("categories", [])}
    seen = set()
    for a in data.get("achievements", []):
        aid = a.get("id", "?")
        if aid in seen:
            errors.append(f"[achievements.json] id en double '{aid}'")
        seen.add(aid)
        if not _known_achievement_source(db, a.get("source")):
            errors.append(f"[achievements.json] '{aid}' : source '{a.get('source')}' inconnue du moteur")
        if a.get("category") not in categories:
            errors.append(f"[achievements.json] '{aid}' : categorie '{a.get('category')}' absente")
        if not isinstance(a.get("threshold"), int) or a["threshold"] < 1:
            errors.append(f"[achievements.json] '{aid}' : threshold doit etre un entier >= 1")
        reward = a.get("reward", {})
        if "xp_percent" in reward:
            errors.append(f"[achievements.json] '{aid}' : xp_percent n'existe plus, "
                          f"la recompense est une XP fixe (reward.xp)")
        if not isinstance(reward.get("xp", 0), int) or reward.get("xp", 0) < 0:
            errors.append(f"[achievements.json] '{aid}' : reward.xp doit etre un entier >= 0")
        title = reward.get("title_id")
        if title and title not in grant_titles:
            errors.append(f"[achievements.json] '{aid}' : titre '{title}' absent de ui/cosmetics.json "
                          f"ou non octroyable (acquisition 'grant')")
        for qid in a.get("params", {}).get("quests", []):
            if qid not in quests:
                errors.append(f"[achievements.json] '{aid}' : quete '{qid}' inexistante")
        if a.get("source") == "quests_set_completed" and                 a.get("threshold") != len(a.get("params", {}).get("quests", [])):
            errors.append(f"[achievements.json] '{aid}' : threshold doit valoir le nombre de quetes")
    return errors


# --- Quest engine contract (lot 0, 2026-10-17) --------------------------------
# Mirrors the load rules of services/quest (it refuses to start on any of these),
# so a data commit fails here first. world/quests.json _meta.engine_contract is the doc.
QUEST_GRANTED_REWARD_KEYS = {"xp", "gold", "items", "item_choices", "title"}
QUEST_EVENT_KINDS = {"fissure_invasion"}
_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _npc_entries(db: Path) -> list:
    data = load_json(db / "entities" / "npcs.json")
    out = []
    for key, val in data.items():
        if key.startswith("_") or not isinstance(val, list):
            continue
        out.extend(n for n in val if isinstance(n, dict) and n.get("id"))
    return out


def _flag_list(owner: str, obj: dict, key: str, errors: list) -> list:
    if key not in obj:
        return []
    val = obj[key]
    if not isinstance(val, list) or not all(isinstance(f, str) and f for f in val):
        errors.append(f"{owner} : {key} doit etre une liste de chaines non vides")
        return []
    return val


def validate_quest_engine(db: Path, all_item_ids: set) -> list:
    """world/quests.json + entities/npcs.json : regles de chargement du service de quetes."""
    errors = []
    quests = load_json(db / "world" / "quests.json").get("quests", [])
    npcs = _npc_entries(db)
    npc_ids = {n["id"] for n in npcs}
    monsters = load_json(db / "entities" / "monsters.json").get("monsters", [])
    monster_ids = {m["id"] for m in monsters} if isinstance(monsters, list) else set(monsters)
    cosmetics = load_json(db / "ui" / "cosmetics.json").get("cosmetics", [])
    grant_titles = {c["id"] for c in cosmetics
                    if c.get("type") == "title" and c.get("acquisition") == "grant"}

    produced = set()
    wanted = []  # (owner, flag)
    for q in quests:
        qid = q.get("id", "?")
        owner = f"[quests.json] '{qid}'"
        if "auto_accept_on_level" in q:
            errors.append(f"{owner} : auto_accept_on_level n'existe pas, utiliser auto_accept_at_min_level")
        if "parked" in q and not isinstance(q["parked"], bool):
            errors.append(f"{owner} : parked doit etre un booleen")
        rewards = q.get("rewards", {})
        for k in rewards:
            if not k.startswith("_") and k not in QUEST_GRANTED_REWARD_KEYS:
                errors.append(f"{owner} : recompense '{k}' jamais versee par le serveur "
                              f"(versees : {sorted(QUEST_GRANTED_REWARD_KEYS)} ; sinon '_not_granted')")
        if "title" in rewards and rewards["title"] not in grant_titles:
            errors.append(f"{owner} : titre '{rewards['title']}' absent de ui/cosmetics.json "
                          f"ou non octroyable (acquisition 'grant')")
        window = []
        for k in ("available_from", "available_until"):
            if k in q:
                if not isinstance(q[k], str) or not _UTC_RE.match(q[k]):
                    errors.append(f"{owner} : {k} doit etre une date UTC 'AAAA-MM-JJTHH:MM:SSZ'")
                else:
                    window.append(q[k])
        if len(window) == 2 and window[0] >= window[1]:
            errors.append(f"{owner} : available_from doit preceder available_until")
        for obj in q.get("objectives", []):
            t = obj.get("template")
            if t == "deliver_item":
                if obj.get("npc_id") not in npc_ids:
                    errors.append(f"{owner} : deliver_item vers un PNJ inconnu '{obj.get('npc_id')}'")
                if obj.get("item_id") not in all_item_ids:
                    errors.append(f"{owner} : deliver_item d'un objet inconnu '{obj.get('item_id')}'")
                if not isinstance(obj.get("count"), int) or obj["count"] < 1:
                    errors.append(f"{owner} : deliver_item exige un count entier >= 1")
            elif t == "take_part_in_event":
                if obj.get("event") not in QUEST_EVENT_KINDS:
                    errors.append(f"{owner} : take_part_in_event, event '{obj.get('event')}' inconnu "
                                  f"(connus : {sorted(QUEST_EVENT_KINDS)})")
            elif t == "defeat_boss":
                boss = obj.get("boss", obj.get("boss_mob_id"))
                if boss not in monster_ids:
                    errors.append(f"{owner} : defeat_boss vers un monstre inconnu '{boss}'")
        entries = []
        if isinstance(q.get("moral_choice"), dict):
            entries.append(("", q["moral_choice"]))
        for c in q.get("moral_choices", []) or []:
            if isinstance(c, dict):
                entries.append((c.get("id", ""), c))
        for cid, c in entries:
            for key in ("a", "b"):
                opt = c.get(f"choice_{key}", {})
                produced.add(f"moral:{qid}:" + (f"{cid}:" if cid else "") + key)
                produced.update(_flag_list(f"{owner} choice_{key}", opt, "sets_flags", errors))
                if ("outcome_fr" in opt) != ("outcome_en" in opt):
                    errors.append(f"{owner} choice_{key} : outcome_fr et outcome_en vont ensemble")
        for key in ("requires_flags", "forbids_flags"):
            wanted += [(owner, f) for f in _flag_list(owner, q, key, errors)]
    for n in npcs:
        owner = f"[npcs.json] '{n['id']}'"
        for key in ("requires_flags", "forbids_flags"):
            wanted += [(owner, f) for f in _flag_list(owner, n, key, errors)]
    for owner, flag in wanted:
        if flag not in produced:
            errors.append(f"{owner} : drapeau '{flag}' pose par aucun choix de world/quests.json")
    return errors


def validate_zone_chests(db: Path, all_item_ids: set) -> list:
    """world/zone_chests.json : objets existants, zones connues, rangs 1..5 complets."""
    errors = []
    path = db / "world" / "zone_chests.json"
    if not path.exists():
        return errors
    data = load_json(path)
    zones_path = db / "world" / "zones.json"
    zone_ids = set()
    if zones_path.exists():
        zones = load_json(zones_path).get("zones", [])
        zone_ids = {z.get("id") for z in zones if isinstance(z, dict)}
    for zid in data.get("spawn", {}).get("zones", []):
        if zone_ids and zid not in zone_ids:
            errors.append(f"[zone_chests.json] zone '{zid}' absente de world/zones.json")
    tiers = {k: v for k, v in data.get("tiers", {}).items() if not k.startswith("_")}
    for rank in ("1", "2", "3", "4", "5"):
        if rank not in tiers:
            errors.append(f"[zone_chests.json] rang '{rank}' manquant (rangs 1 a 5)")
    for rank, tier in tiers.items():
        gold = tier.get("gold", [])
        if not (isinstance(gold, list) and len(gold) == 2 and 0 <= gold[0] <= gold[1]):
            errors.append(f"[zone_chests.json] rang {rank} : gold doit etre [min, max]")
        for it in tier.get("items", []):
            iid = it.get("item_id")
            if iid not in all_item_ids:
                errors.append(f"[zone_chests.json] rang {rank} : objet '{iid}' inexistant")
            if it.get("weight", 0) <= 0 or it.get("min", 1) > it.get("max", 1):
                errors.append(f"[zone_chests.json] rang {rank} : '{iid}' poids ou quantites invalides")
    return errors


def validate_teleport_steles(db: Path) -> list:
    """world/teleport_steles.json : zones connues, ids uniques, position et noms FR/EN,
    regles de portee et d'arrivee lisibles par presence."""
    errors = []
    path = db / "world" / "teleport_steles.json"
    if not path.exists():
        return errors
    data = load_json(path)
    zones_path = db / "world" / "zones.json"
    zone_ids = set()
    if zones_path.exists():
        zone_ids = {z.get("id") for z in load_json(zones_path).get("zones", []) if isinstance(z, dict)}
    rules = data.get("rules", {})
    if not isinstance(rules.get("use_range_px"), (int, float)) or rules.get("use_range_px", 0) <= 0:
        errors.append("[teleport_steles.json] rules.use_range_px doit etre un nombre > 0")
    off = rules.get("arrival_offset")
    if not (isinstance(off, list) and len(off) == 2 and all(isinstance(v, (int, float)) for v in off)):
        errors.append("[teleport_steles.json] rules.arrival_offset doit etre [dx, dy]")
    seen = set()
    for s in data.get("steles", []):
        sid = s.get("id", "")
        if not sid or sid in seen:
            errors.append(f"[teleport_steles.json] id vide ou en double : '{sid}'")
        seen.add(sid)
        if s.get("zone_id") not in zone_ids:
            errors.append(f"[teleport_steles.json] {sid} : zone '{s.get('zone_id')}' absente de world/zones.json")
        if not all(isinstance(s.get(k), (int, float)) for k in ("x", "y")):
            errors.append(f"[teleport_steles.json] {sid} : x et y doivent etre des nombres")
        if not s.get("name_fr") or not s.get("name_en"):
            errors.append(f"[teleport_steles.json] {sid} : name_fr et name_en obligatoires")
    return errors


def validate_fissure_invasions(db: Path) -> list:
    """world/fissure_invasions.json : zones connues, bornes coherentes."""
    errors = []
    path = db / "world" / "fissure_invasions.json"
    if not path.exists():
        return errors
    data = load_json(path)
    zones_path = db / "world" / "zones.json"
    zone_ids = set()
    if zones_path.exists():
        zone_ids = {z.get("id") for z in load_json(zones_path).get("zones", []) if isinstance(z, dict)}
    spawn = data.get("spawn", {})
    for zid in spawn.get("zones", []):
        if zone_ids and zid not in zone_ids:
            errors.append(f"[fissure_invasions.json] zone '{zid}' absente de world/zones.json")
    for key in ("first_start_seconds", "cooldown_seconds"):
        v = spawn.get(key, [])
        if not (isinstance(v, list) and len(v) == 2 and 0 <= v[0] <= v[1]):
            errors.append(f"[fissure_invasions.json] spawn.{key} doit etre [min, max]")
    if spawn.get("duration_seconds", 0) <= 0 or spawn.get("max_active_per_zone", 0) <= 0:
        errors.append("[fissure_invasions.json] duration_seconds et max_active_per_zone doivent etre > 0")
    obj = data.get("objective", {})
    if not (0 < obj.get("kill_target_min", 0) <= obj.get("kill_target_max", 0)):
        errors.append("[fissure_invasions.json] objective : 0 < kill_target_min <= kill_target_max")
    for rank, level in data.get("visual", {}).get("level_by_rank", {}).items():
        if not (isinstance(level, int) and 1 <= level <= 3):
            errors.append(f"[fissure_invasions.json] visual.level_by_rank[{rank}] doit valoir 1, 2 ou 3")
    eff = data.get("effects", {})
    if not (0 < eff.get("respawn_time_multiplier", 0) <= 1):
        errors.append("[fissure_invasions.json] effects.respawn_time_multiplier doit etre dans ]0, 1]")
    return errors


def _point_in_polygon(x, y, poly) -> bool:
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def validate_rift_events(db: Path) -> list:
    """world/rift_events.json (interieur de faille, 2026-10-17) : zones, tailles, seuils de palier,
    emplacements des groupes dans le contour de la carte interieure, Braises par rang, et les blocs
    de recompense lus ailleurs (config/rewards.json rift_closing / rift_level_gap,
    systems/profession_xp.json rift_xp). Le serveur refuse de charger une faille incoherente : la CI
    le dit avant."""
    errors = []
    path = db / "world" / "rift_events.json"
    if not path.exists():
        return errors
    tag = "[rift_events.json]"
    data = load_json(path)
    zones = {z.get("id"): z for z in load_json(db / "world" / "zones.json").get("zones", [])
             if isinstance(z, dict)}
    ranks = ("1", "2", "3", "4", "5")
    sizes = ("small", "medium", "large")
    sch = data.get("schedule", {})
    for zid in sch.get("zones", []):
        if zid not in zones:
            errors.append(f"{tag} schedule.zones : '{zid}' absente de world/zones.json")
        elif not zones[zid].get("spawn_areas"):
            errors.append(f"{tag} schedule.zones : '{zid}' n'a pas de spawn_areas (aucune aire ou ouvrir)")
    for r in ranks:
        v = sch.get("interval_minutes_by_rank", {}).get(r)
        if not (isinstance(v, (int, float)) and v > 0):
            errors.append(f"{tag} schedule.interval_minutes_by_rank.{r} doit etre > 0")
    fo = sch.get("first_open_minutes", [])
    if not (isinstance(fo, list) and len(fo) == 2 and 0 <= fo[0] <= fo[1]):
        errors.append(f"{tag} schedule.first_open_minutes doit etre [min, max]")
    if not (0 <= sch.get("interval_jitter", -1) < 1):
        errors.append(f"{tag} schedule.interval_jitter doit etre dans [0, 1[")
    sz = data.get("sizes", {})
    max_groups = 0
    for name in sizes:
        b = sz.get(name, {})
        if not (isinstance(b.get("target_groups"), int) and b["target_groups"] > 0
                and isinstance(b.get("duration_minutes"), (int, float)) and b["duration_minutes"] > 0):
            errors.append(f"{tag} sizes.{name} : target_groups (entier > 0) et duration_minutes (> 0) requis")
        else:
            max_groups = max(max_groups, b["target_groups"])
    for r in ranks:
        w = sz.get("weights_by_rank", {}).get(r)
        if not (isinstance(w, list) and len(w) == 3 and all(isinstance(x, (int, float)) and x >= 0 for x in w)
                and sum(w) > 0):
            errors.append(f"{tag} sizes.weights_by_rank.{r} doit etre [petite, moyenne, grande] (somme > 0)")
        sc = sz.get("duration_scale_by_rank", {}).get(r)
        if not (isinstance(sc, (int, float)) and sc > 0):
            errors.append(f"{tag} sizes.duration_scale_by_rank.{r} doit etre > 0")
    lvl = data.get("visual", {}).get("level_by_size", {})
    for name in sizes:
        if lvl.get(name) not in (1, 2, 3):
            errors.append(f"{tag} visual.level_by_size.{name} doit valoir 1, 2 ou 3")
    g = data.get("groups", {})
    gs = g.get("size", [])
    if not (isinstance(gs, list) and len(gs) == 2 and 1 <= gs[0] <= gs[1] <= 10):
        errors.append(f"{tag} groups.size doit etre [min, max] dans [1, 10] (regle 10 allies + 10 monstres)")
    off = g.get("level_offset_from_area_max", [])
    if not (isinstance(off, list) and len(off) == 2 and off[0] <= off[1] <= 0):
        errors.append(f"{tag} groups.level_offset_from_area_max doit etre [min, max] <= 0")
    sw = g.get("star_weights", [])
    if not (isinstance(sw, list) and len(sw) == 6 and all(isinstance(x, (int, float)) and x >= 0 for x in sw)
            and sum(sw) > 0):
        errors.append(f"{tag} groups.star_weights doit avoir 6 poids (0 a 5 etoiles), somme > 0")
    spare = g.get("spare_groups", -1)
    if not (isinstance(spare, int) and spare >= 0):
        errors.append(f"{tag} groups.spare_groups doit etre un entier >= 0")
        spare = 0
    it = data.get("interior", {})
    zid_by_rank = it.get("zone_id_by_rank", {})
    polys = []
    for r in ranks:
        zid = zid_by_rank.get(r)
        z = zones.get(zid)
        if not z:
            errors.append(f"{tag} interior.zone_id_by_rank.{r} : zone '{zid}' absente de world/zones.json")
            continue
        if z.get("type") != "rift_interior" or z.get("rift_rank") != int(r):
            errors.append(f"{tag} zone '{zid}' doit avoir type rift_interior et rift_rank {r}")
        if z.get("spawn_areas"):
            errors.append(f"{tag} zone '{zid}' ne doit pas avoir de spawn_areas (groupes poses par l'evenement)")
        poly = z.get("area_limit", [])
        if len(poly) < 3:
            errors.append(f"{tag} zone '{zid}' : area_limit (contour de la carte) requis")
        else:
            polys.append((zid, poly))
    slots = it.get("group_slots", [])
    if len(slots) < max_groups + spare:
        errors.append(f"{tag} interior.group_slots : {len(slots)} emplacements, il en faut au moins "
                      f"{max_groups + spare} (plus grande taille + reserve)")
    points = [("group_slots", p) for p in slots] + [("entry_point", it.get("entry_point", []))]
    points += [("exit_points", p) for p in it.get("exit_points", [])]
    if not it.get("exit_points"):
        errors.append(f"{tag} interior.exit_points : au moins une fissure de sortie")
    for label, pt in points:
        if not (isinstance(pt, list) and len(pt) == 2):
            errors.append(f"{tag} interior.{label} : point [x, y] attendu, trouve {pt!r}")
            continue
        for zid, poly in polys:
            if not _point_in_polygon(pt[0], pt[1], poly):
                errors.append(f"{tag} interior.{label} {pt} hors du contour de '{zid}'")
                break
    for key in ("entry_range_px", "exit_range_px", "admission_seconds", "close_grace_seconds",
                "exit_grace_seconds"):
        if not (isinstance(it.get(key), (int, float)) and it[key] > 0):
            errors.append(f"{tag} interior.{key} doit etre > 0")
    ent = data.get("entry", {})
    if not (isinstance(ent.get("min_level_offset"), int) and ent["min_level_offset"] <= 0
            and isinstance(ent.get("min_level_floor"), int) and ent["min_level_floor"] >= 1):
        errors.append(f"{tag} entry : min_level_offset (<= 0) et min_level_floor (>= 1) requis")
    con = data.get("contribution", {})
    for r in ranks:
        for name in sizes:
            th = con.get("tier_thresholds", {}).get(r, {}).get(name)
            if not (isinstance(th, list) and len(th) == 3 and all(isinstance(x, (int, float)) for x in th)
                    and 0 < th[0] <= th[1] <= th[2]):
                errors.append(f"{tag} contribution.tier_thresholds.{r}.{name} doit etre "
                              f"[bronze, argent, or] croissants et > 0")
            elif th[0] > 1:
                errors.append(f"{tag} contribution.tier_thresholds.{r}.{name} : le bronze s'obtient des "
                              f"1 groupe (decision Charleston 2026-10-17)")
    acf = con.get("assisted_contribution_factor")
    if not (isinstance(acf, (int, float)) and 0 <= acf <= 1):
        errors.append(f"{tag} contribution.assisted_contribution_factor doit etre dans [0, 1]")
    if data.get("failure", {}).get("mode") not in ("close", "corruption", "corruption_then_overflow"):
        errors.append(f"{tag} failure.mode inconnu")
    st = data.get("hunter", {}).get("stabilize", {})
    for r in ranks:
        if not isinstance(st.get("min_profession_level_by_rank", {}).get(r), int):
            errors.append(f"{tag} hunter.stabilize.min_profession_level_by_rank.{r} requis")
    if not (isinstance(st.get("extra_minutes"), (int, float)) and st["extra_minutes"] > 0
            and isinstance(st.get("max_per_rift"), int) and st["max_per_rift"] >= 0):
        errors.append(f"{tag} hunter.stabilize : extra_minutes (> 0) et max_per_rift (>= 0) requis")
    # Braises par rang : un objet par rang, plus l'ancien id sans rang nulle part.
    rec = load_json(db / "items" / "profession_recipes.json")
    items = {i.get("id") for i in rec.get("new_items", []) if isinstance(i, dict)}
    for r in ranks:
        if f"mat_rift_ember_r{r}" not in items:
            errors.append(f"{tag} mat_rift_ember_r{r} absent de items/profession_recipes.json new_items")
    if "mat_rift_ember" in items or '"mat_rift_ember"' in json.dumps(rec):
        errors.append(f"{tag} l'id sans rang mat_rift_ember est encore utilise : Braises par rang seulement")
    # Blocs de recompense lus par le serveur.
    rw = load_json(db / "config" / "rewards.json")
    gap = rw.get("multiplier_families", {}).get("rift_level_gap", {})
    if not (isinstance(gap.get("full_up_to"), int) and isinstance(gap.get("purification_from"), int)
            and 0 <= gap["full_up_to"] < gap["purification_from"]):
        errors.append(f"{tag} rewards.json rift_level_gap : 0 <= full_up_to < purification_from requis")
    for v in ("in_range", "over", "purification"):
        if v not in gap.get("values", {}):
            errors.append(f"{tag} rewards.json rift_level_gap.values.{v} requis")
    rc = rw.get("rift_closing", {})
    if rc.get("xp_level_basis") != "min_player_rift":
        errors.append(f"{tag} rewards.json rift_closing.xp_level_basis doit valoir min_player_rift (anti-farm)")
    for t in ("bronze", "silver", "gold"):
        b = rc.get("tiers", {}).get(t, {})
        for k in ("xp_level_fraction", "chests", "chest_gold_multiplier", "embers"):
            if not (isinstance(b.get(k), (int, float)) and b[k] >= 0):
                errors.append(f"{tag} rewards.json rift_closing.tiers.{t}.{k} requis (>= 0)")
    for name in sizes:
        if not isinstance(rc.get("size_resource_multiplier", {}).get(name), (int, float)):
            errors.append(f"{tag} rewards.json rift_closing.size_resource_multiplier.{name} requis")
    if not isinstance(rc.get("level_gap", {}).get("half_factor"), (int, float)):
        errors.append(f"{tag} rewards.json rift_closing.level_gap.half_factor requis")
    rx = load_json(db / "systems" / "profession_xp.json").get("rift_xp", {})
    for k in ("actions_per_minute", "failure_share", "daily_first_multiplier"):
        if not (isinstance(rx.get(k), (int, float)) and rx[k] >= 0):
            errors.append(f"{tag} profession_xp.json rift_xp.{k} requis (>= 0)")
    for t in ("bronze", "silver", "gold"):
        if not isinstance(rx.get("tier_share", {}).get(t), (int, float)):
            errors.append(f"{tag} profession_xp.json rift_xp.tier_share.{t} requis")
    return errors


RANK_BANDS = ((1, 19), (20, 39), (40, 59), (60, 79), (80, 100))


def _rank_of_level(level: int) -> int:
    for i, (lo, hi) in enumerate(RANK_BANDS):
        if lo <= level <= hi:
            return i + 1
    if level == 0:
        return 1  # metiers V1 : le rang I s'ouvre au niveau 0
    return 0


def _profession_data(db: Path) -> dict:
    """Charge metiers + recettes et derive producteurs, liens et rarete. Partage par les etapes 12f/12g/12i/12j."""
    prof = load_json(db / "systems" / "professions.json")
    rec_path = db / "items" / "profession_recipes.json"
    rec = load_json(rec_path) if rec_path.exists() else {}
    new_items = {i["id"]: i for i in rec.get("new_items", [])}
    producer = {}
    for iid, it in new_items.items():
        if it.get("gathered_by"):
            producer[iid] = it["gathered_by"]
        elif it.get("crafted_by"):
            producer[iid] = it["crafted_by"]
    mats = load_json(db / "items" / "materials.json")
    monster = {i["id"] for k in ("common", "uncommon", "rare") for i in mats.get(k, [])}
    rarity = prof.get("resource_rarity", {})
    suffixes = [t.get("suffix", "") for t in rarity.get("tiers", []) if t.get("suffix")]
    return {"prof": prof, "rec": rec, "new_items": new_items, "producer": producer, "monster": monster,
            "prof_ids": {p["id"] for p in prof.get("professions", [])},
            "gathering": {p["id"] for p in prof.get("professions", []) if p.get("kind") == "gathering"},
            "suffixes": suffixes}


def _derived_links(pd: dict):
    """consumes[p] / feeds[p] derives des recettes et des outils (le Glaneur produit les materiaux de monstre)."""
    consumes, uses = {}, {}
    for x in pd["rec"].get("recipes", []) + pd["rec"].get("rule_recipes", []):
        for m in x.get("materials", []):
            uses.setdefault(m.get("id"), set()).add(x.get("profession"))
            src = pd["producer"].get(m.get("id")) or ("gleaner" if m.get("id") in pd["monster"] else None)
            if src and src != x.get("profession"):
                consumes.setdefault(x.get("profession"), set()).add(src)
    for it in pd["new_items"].values():
        if it.get("kind") == "tool" and it.get("profession") and it.get("crafted_by"):
            if it["crafted_by"] != it["profession"]:
                consumes.setdefault(it["profession"], set()).add(it["crafted_by"])
    feeds = {}
    for p, srcs in consumes.items():
        for s in srcs:
            feeds.setdefault(s, set()).add(p)
    return consumes, feeds, uses


def validate_professions(db: Path) -> list:
    """systems/professions.json : usages des materiaux, liens declares = liens derives, aucun metier isole."""
    errors = []
    path = db / "systems" / "professions.json"
    if not path.exists():
        return errors
    pd = _profession_data(db)
    d = pd["prof"]
    prof_ids = pd["prof_ids"]
    uses = d.get("materials", {}).get("material_uses", {})
    ids = pd["monster"]
    tracked = {iid for iid, it in pd["new_items"].items()
               if it.get("category") == "intermediate"
               or it.get("gathered_by") in ("miner", "lumberjack", "fisher", "herbalist", "fissure_hunter")}
    for mid in sorted(ids - set(uses)):
        errors.append(f"[professions.json] materiau '{mid}' sans metier (material_uses)")
    consumes, feeds, recipe_uses = _derived_links(pd)
    for mid, profs in uses.items():
        if mid not in ids and mid not in tracked:
            errors.append(f"[professions.json] material_uses : materiau inconnu '{mid}'")
        if not profs:
            errors.append(f"[professions.json] material_uses['{mid}'] vide")
        for p in profs:
            if p not in prof_ids:
                errors.append(f"[professions.json] material_uses['{mid}'] : metier inconnu '{p}'")
        if mid in tracked and sorted(profs) != sorted(recipe_uses.get(mid, set())):
            errors.append(f"[professions.json] material_uses['{mid}'] {sorted(profs)} != recettes "
                          f"{sorted(recipe_uses.get(mid, set()))} (relancer le generateur)")
    for mid in sorted(tracked - set(uses)):
        errors.append(f"[professions.json] ressource/intermediaire '{mid}' absent de material_uses")
    for mid in sorted(tracked):
        if not recipe_uses.get(mid):
            errors.append(f"[professions.json] '{mid}' n'est consomme par aucune recette (ressource morte)")
    for p in d.get("professions", []):
        pid = p["id"]
        for key, derived in (("consumes_from", consumes), ("feeds", feeds)):
            want = sorted(derived.get(pid, set()))
            if sorted(p.get(key, [])) != want:
                errors.append(f"[professions.json] {pid}.{key} {sorted(p.get(key, []))} != derive {want}")
            if not want:
                errors.append(f"[professions.json] metier ISOLE '{pid}' : {key} vide (doit consommer d'un "
                              f"autre metier ET en nourrir un)")
    if pd["gathering"]:
        tools = {it.get("profession") for it in pd["new_items"].values() if it.get("kind") == "tool"}
        for g in sorted(pd["gathering"]):
            if g not in tools:
                errors.append(f"[professions.json] metier de recolte '{g}' sans outil (kind tool)")
    # Un fait = un proprietaire (2026-10-16) : le type d'outil vit dans tools.by_profession,
    # le nombre maximum d'Experts dans rules.expert.max_experts.
    by_prof = d.get("tools", {}).get("by_profession", {})
    tool_types = {(it.get("tool_type"), it.get("profession")) for it in pd["new_items"].values()
                  if it.get("kind") == "tool"}
    for pid, ttype in by_prof.items():
        if pid not in prof_ids:
            errors.append(f"[professions.json] tools.by_profession : metier inconnu '{pid}'")
        elif (ttype, pid) not in tool_types:
            errors.append(f"[professions.json] tools.by_profession['{pid}'] = '{ttype}' : aucun outil "
                          f"tool_{ttype}_r<rang> de ce metier")
    for p in d.get("professions", []):
        if "tool" in p:
            errors.append(f"[professions.json] {p['id']}.tool : copie interdite, le seul proprietaire est "
                          f"tools.by_profession")
    rules = d.get("rules", {})
    if "specialties" in rules:
        errors.append("[professions.json] rules.specialties : copie interdite de rules.expert.max_experts")
    if not isinstance(rules.get("expert", {}).get("max_experts"), int):
        errors.append("[professions.json] rules.expert.max_experts manquant")
    tier_rows = d.get("resource_rarity", {}).get("tiers", [])
    lmax, lpr = rules.get("level_max"), rules.get("levels_per_rank")
    if not (isinstance(lmax, int) and isinstance(lpr, int) and lpr > 0 and lmax % lpr == 0
            and lmax // lpr == len(tier_rows)):
        errors.append(f"[professions.json] rules.levels_per_rank ({lpr}) doit diviser level_max ({lmax}) en "
                      f"{len(tier_rows)} rangs (un par tier)")
    q = d.get("quality", {})
    tiers = [t.get("id") for t in tier_rows]
    if set(q.get("material_rarity_shift", {})) != set(tiers):
        errors.append(f"[professions.json] quality.material_rarity_shift {sorted(q.get('material_rarity_shift', {}))}"
                      f" != tiers de rarete {sorted(tiers)}")
    # Rarete de fabrication : UN bloc (quality) pour tout lieu de fabrication (2026-10-16).
    ms = q.get("max_shift")
    if not isinstance(ms, (int, float)) or not 0 < ms <= 1:
        errors.append("[professions.json] quality.max_shift doit etre un nombre dans ]0, 1]")
    if len(q.get("base_weights", [])) != len(tiers) or any(w < 0 for w in q.get("base_weights", [])):
        errors.append("[professions.json] quality.base_weights : un poids >= 0 par tier")
    # Aucun plancher de rarete par rang de metier (proprietaire, 2026-10-16) : la qualite fabriquee
    # est le seul tirage du metier, le plafond quality_cap reste. Les anciennes valeurs vivent sous
    # quality._superseded, lues par personne.
    if "min_rarity_by_profession_rank" in q:
        errors.append("[professions.json] quality.min_rarity_by_profession_rank : plancher supprime le "
                      "2026-10-16, la qualite fabriquee n'a pas de minimum (le serveur refuse aussi la cle)")
    scal = db / "items" / "equipment_scaling.json"
    if scal.exists() and "crafting" in load_json(scal):
        errors.append("[equipment_scaling.json] bloc crafting : second modele de rarete de fabrication, le seul "
                      "est systems/professions.json quality")
    return errors


def validate_profession_recipes(db: Path, all_item_ids: set) -> list:
    """items/profession_recipes.json : objets, niveaux et rangs, liens entre metiers (regle V2), cycles."""
    errors = []
    path = db / "items" / "profession_recipes.json"
    if not path.exists():
        return errors
    pd = _profession_data(db)
    d = pd["rec"]
    profs = pd["prof_ids"]
    new_items = pd["new_items"]
    producer = pd["producer"]
    known = all_item_ids | set(new_items)
    # Les stigmates de keystone vivent dans leur propre fichier, hors collect_all_item_ids.
    ks_path = db / "items" / "keystone_items.json"
    if ks_path.exists():
        known |= {k["id"] for k in load_json(ks_path).get("keystone_items", [])}
    for iid in new_items:
        if iid in all_item_ids:
            errors.append(f"[profession_recipes.json] new_items '{iid}' existe deja dans la base")
    seen = set()
    made_by = {}
    families = {"koro_cards", "pet_books", "keystone_items"}
    all_rows = [("recipe", r) for r in d.get("recipes", [])] + [("rule", r) for r in d.get("rule_recipes", [])]
    for kind, r in all_rows:
        rid = r.get("id", "?")
        if rid in seen:
            errors.append(f"[profession_recipes.json] recette en double '{rid}'")
        seen.add(rid)
        p = r.get("profession")
        if p not in profs:
            errors.append(f"[profession_recipes.json] '{rid}' : metier inconnu '{p}'")
        lvl = int(r.get("profession_level", 0))
        # Metiers V1 (2026-10-01) : les metiers commencent au niveau 0, rang I = 0..19.
        if not 0 <= lvl <= 100:
            errors.append(f"[profession_recipes.json] '{rid}' : profession_level hors 0..100")
        rank = r.get("rank")
        if rank != _rank_of_level(lvl):
            errors.append(f"[profession_recipes.json] '{rid}' : rank {rank} != rang du niveau {lvl} "
                          f"({_rank_of_level(lvl)})")
        if kind == "recipe":
            out = r.get("output_item")
            if out not in known:
                errors.append(f"[profession_recipes.json] '{rid}' : objet produit inconnu '{out}'")
            if r.get("quality_cap") not in ("C", "B", "A", "S", "SS"):
                errors.append(f"[profession_recipes.json] '{rid}' : quality_cap invalide")
            made_by.setdefault(out, set()).add(p)
        else:
            out = None
            if r.get("kind") not in ("fusion", "reveal", "copy") or r.get("item_family") not in families:
                errors.append(f"[profession_recipes.json] '{rid}' : kind ou item_family invalide")
        mids = [m.get("id") for m in r.get("materials", [])]
        if len(mids) != len(set(mids)):
            errors.append(f"[profession_recipes.json] '{rid}' : materiau cite deux fois")
        for mid in mids:
            if mid not in known:
                base = next((mid[: -len(s)] for s in pd["suffixes"] if mid.endswith(s)), None)
                if base and base in new_items:
                    errors.append(f"[profession_recipes.json] '{rid}' : variante de rarete '{mid}' citee, "
                                  f"ecrire l'id de base '{base}'")
                else:
                    errors.append(f"[profession_recipes.json] '{rid}' : materiau inconnu '{mid}'")
        # Regle V2 : liens entre metiers. Les materiaux de monstre ne comptent pas.
        foreign = {producer[m] for m in mids if m in producer and producer[m] != p}
        foreign_int = {producer[m] for m in mids if m in producer and producer[m] != p
                       and new_items[m].get("category") == "intermediate"}
        is_intermediate = out in new_items and new_items[out].get("category") == "intermediate"
        if isinstance(rank, int) and rank >= 2 and not foreign:
            errors.append(f"[profession_recipes.json] '{rid}' (rang {rank}) : aucun apport d'un autre metier")
        if isinstance(rank, int) and rank >= 4:
            if len(foreign) < 2:
                errors.append(f"[profession_recipes.json] '{rid}' (rang {rank}) : {len(foreign)} metier(s) "
                              f"etranger(s) {sorted(foreign)}, il en faut 2")
            if not is_intermediate and not foreign_int:
                errors.append(f"[profession_recipes.json] '{rid}' (rang {rank}) : recette finale sans "
                              f"intermediaire d'un autre metier")
    # Producteur declare = metier qui fabrique ; chaque intermediaire/outil a une recette.
    for iid, it in new_items.items():
        cb = it.get("crafted_by")
        if cb and made_by.get(iid) != {cb}:
            errors.append(f"[profession_recipes.json] '{iid}' : crafted_by '{cb}' != recette(s) "
                          f"{sorted(made_by.get(iid, set()))}")
        if it.get("category") == "intermediate" and not cb:
            errors.append(f"[profession_recipes.json] intermediaire '{iid}' sans crafted_by")
        if it.get("gathered_by") and it["gathered_by"] not in pd["gathering"]:
            errors.append(f"[profession_recipes.json] '{iid}' : gathered_by '{it['gathered_by']}' n'est pas un "
                          f"metier de recolte")
        if it.get("kind") == "tool":
            if it.get("profession") not in pd["gathering"]:
                errors.append(f"[profession_recipes.json] outil '{iid}' : profession '{it.get('profession')}' "
                              f"n'est pas un metier de recolte")
            if not isinstance(it.get("uses"), int) or it["uses"] <= 0:
                errors.append(f"[profession_recipes.json] outil '{iid}' : uses doit etre > 0")
    # Cycles : un objet NOUVEAU sans autre source (pas starter) ne doit pas dependre de lui-meme.
    # Une ressource recoltee de rang N depend de l'outil de son metier au rang N.
    deps = {}
    for r in d.get("recipes", []):
        if r.get("output_item") in new_items:
            deps.setdefault(r["output_item"], set()).update(m.get("id") for m in r.get("materials", []))
    tool_by = {(it.get("profession"), it.get("rank")): iid for iid, it in new_items.items()
               if it.get("kind") == "tool"}
    for iid, it in new_items.items():
        if it.get("gathered_by") in pd["gathering"] and isinstance(it.get("rank"), int):
            t = tool_by.get((it["gathered_by"], it["rank"])) or tool_by.get((it["gathered_by"], 1))
            if t:
                deps.setdefault(iid, set()).add(t)
    roots = {iid for iid, it in new_items.items() if it.get("starter")}
    state = {}

    def visit(node, stack):
        if node in roots or node not in deps:
            return
        if state.get(node) == 1:
            errors.append(f"[profession_recipes.json] CYCLE impossible a amorcer : {' -> '.join(stack + [node])}")
            return
        if state.get(node) == 2:
            return
        state[node] = 1
        for nxt in sorted(deps[node]):
            visit(nxt, stack + [node])
        state[node] = 2

    for node in sorted(deps):
        visit(node, [])
    return errors


def validate_resource_rarity(db: Path) -> list:
    """systems/professions.json resource_rarity : tiers coherents, suffixes uniques, aucune variante ecrite a la main."""
    errors = []
    path = db / "systems" / "professions.json"
    if not path.exists():
        return errors
    pd = _profession_data(db)
    rr = pd["prof"].get("resource_rarity")
    if not rr:
        return errors
    tiers = rr.get("tiers", [])
    if [t.get("id") for t in tiers] != ["C", "B", "A", "S", "SS"] or tiers[0].get("suffix") != "":
        errors.append("[professions.json] resource_rarity.tiers doit etre C, B, A, S, SS (echelle unique du jeu), "
                      "C sans suffixe")
    sfx = [t.get("suffix") for t in tiers]
    if len(set(sfx)) != len(sfx):
        errors.append("[professions.json] resource_rarity : suffixes en double")
    prev = 0
    for t in tiers:
        for k in ("id", "suffix", "item_rarity", "name_suffix_fr", "name_suffix_en", "xp_multiplier",
                  "sell_multiplier"):
            if k not in t:
                errors.append(f"[professions.json] resource_rarity tier '{t.get('id')}' : champ '{k}' manquant")
        xm = t.get("xp_multiplier", 0)
        if not isinstance(xm, (int, float)) or xm < prev:
            errors.append(f"[professions.json] resource_rarity tier '{t.get('id')}' : xp_multiplier doit croitre")
        prev = xm if isinstance(xm, (int, float)) else prev
        if t.get("suffix") and not t["suffix"].startswith("_"):
            errors.append(f"[professions.json] resource_rarity tier '{t.get('id')}' : le suffixe commence par '_'")
    for g in rr.get("applies_to", {}).get("gathered_by", []):
        if g not in pd["gathering"]:
            errors.append(f"[professions.json] resource_rarity.applies_to : '{g}' n'est pas un metier de recolte")
    # Aucune variante ecrite a la main : un id qui finit par un suffixe de rarete est refuse.
    # Les ids de base ne doivent pas finir par un suffixe (sinon collision avec une variante generee).
    for iid in pd["new_items"]:
        for s in pd["suffixes"]:
            if iid.endswith(s):
                errors.append(f"[professions.json] '{iid}' finit par le suffixe de rarete '{s}' : les variantes "
                              f"sont generees par regle, jamais ecrites")
    shift = pd["prof"].get("quality", {}).get("material_rarity_shift", {})
    vals = [shift.get(t.get("id")) for t in tiers]
    if any(v is None for v in vals) or vals != sorted(vals) or (vals and vals[0] != 0):
        errors.append("[professions.json] quality.material_rarity_shift doit couvrir chaque tier, partir de 0 et "
                      "croitre")
    return errors


def validate_gather_nodes(db: Path) -> list:
    """world/gather_nodes.json : metiers, outils, ressources, rangs, rarete, aires et rives."""
    errors = []
    path = db / "world" / "gather_nodes.json"
    if not path.exists():
        return errors
    g = load_json(path)
    pd = _profession_data(db)
    items = pd["new_items"]
    tiers = [t.get("id") for t in pd["prof"].get("resource_rarity", {}).get("tiers", [])]
    tool_types = {(it.get("tool_type"), it.get("profession")) for it in items.values() if it.get("kind") == "tool"}
    ranks = ("1", "2", "3", "4", "5")
    types = {k: v for k, v in g.get("node_types", {}).items() if not k.startswith("_")}
    reachable = set()
    for tname, t in types.items():
        p = t.get("profession")
        if p not in pd["gathering"]:
            errors.append(f"[gather_nodes.json] type '{tname}' : metier '{p}' inconnu ou pas de recolte")
        if "tool" in t:
            errors.append(f"[gather_nodes.json] type '{tname}' : champ tool interdit (copie de "
                          f"systems/professions.json tools.by_profession)")
        ttype = pd["prof"].get("tools", {}).get("by_profession", {}).get(p)
        if (ttype, p) not in tool_types:
            errors.append(f"[gather_nodes.json] type '{tname}' : outil '{ttype}' du metier '{p}' absent")
        if t.get("placement") not in ("ground", "water_edge"):
            errors.append(f"[gather_nodes.json] type '{tname}' : placement invalide")
        if tname == "fishing_spot" and t.get("placement") != "water_edge":
            errors.append("[gather_nodes.json] fishing_spot doit etre place au bord de l'eau (water_edge)")
        rb = t.get("resources_by_rank", {})
        for r in ranks:
            if r not in rb:
                errors.append(f"[gather_nodes.json] type '{tname}' : rang {r} manquant")
                continue
            main = rb[r].get("main")
            it = items.get(main)
            if not it:
                errors.append(f"[gather_nodes.json] type '{tname}' rang {r} : ressource '{main}' inconnue")
            else:
                reachable.add(main)
                if it.get("gathered_by") != p:
                    errors.append(f"[gather_nodes.json] '{main}' recolte par '{it.get('gathered_by')}', pas '{p}'")
                if str(it.get("rank")) != r:
                    errors.append(f"[gather_nodes.json] type '{tname}' rang {r} : '{main}' est de rang "
                                  f"{it.get('rank')}")
                if it.get("node_type") != tname:
                    errors.append(f"[gather_nodes.json] '{main}' : node_type '{it.get('node_type')}' != '{tname}'")
            for s in rb[r].get("secondary", []):
                sit = items.get(s.get("id"))
                if not sit:
                    errors.append(f"[gather_nodes.json] type '{tname}' rang {r} : secondaire '{s.get('id')}' inconnu")
                    continue
                reachable.add(s["id"])
                if sit.get("gathered_by") != p:
                    errors.append(f"[gather_nodes.json] secondaire '{s['id']}' recolte par "
                                  f"'{sit.get('gathered_by')}', pas '{p}'")
                if not 0 < s.get("chance", 0) <= 1:
                    errors.append(f"[gather_nodes.json] secondaire '{s['id']}' : chance hors ]0, 1]")
    node_profs = {t.get("profession") for t in types.values()}
    for iid, it in items.items():
        if it.get("gathered_by") in node_profs and iid not in reachable:
            errors.append(f"[gather_nodes.json] ressource '{iid}' ({it['gathered_by']}) ne tombe d'aucun point")
    w = g.get("rarity", {}).get("weights_by_rank", {})
    for r in ranks:
        row = w.get(r, {})
        if sorted(row) != sorted(tiers):
            errors.append(f"[gather_nodes.json] rarity.weights_by_rank[{r}] {sorted(row)} != tiers {sorted(tiers)}")
        if any(v < 0 for v in row.values()) or sum(row.values()) <= 0:
            errors.append(f"[gather_nodes.json] rarity.weights_by_rank[{r}] : poids invalides")
    gd = g.get("gather_duration", {})
    for r in ranks:
        if gd.get("base_ms_by_rank", {}).get(r, 0) <= 0:
            errors.append(f"[gather_nodes.json] gather_duration.base_ms_by_rank[{r}] doit etre > 0")
    for tname in types:
        if gd.get("type_multiplier", {}).get(tname, 0) <= 0:
            errors.append(f"[gather_nodes.json] gather_duration.type_multiplier : '{tname}' manquant")
    if "profession_xp" in g:
        errors.append("[gather_nodes.json] profession_xp : copie interdite, le seul proprietaire est "
                      "systems/profession_xp.json gather_xp")
    for r in ranks:
        rs = g.get("rules", {}).get("respawn_seconds", {}).get(r, [])
        if not (isinstance(rs, list) and len(rs) == 2 and 0 < rs[0] <= rs[1]):
            errors.append(f"[gather_nodes.json] rules.respawn_seconds[{r}] doit etre [min, max]")
        if g.get("rules", {}).get("charges", {}).get(r, 0) <= 0:
            errors.append(f"[gather_nodes.json] rules.charges[{r}] doit etre > 0")
    zone_ids = set()
    zp = db / "world" / "zones.json"
    if zp.exists():
        zone_ids = {z.get("id") for z in load_json(zp).get("zones", []) if isinstance(z, dict)}
    areas_by_zone = [(zid, z) for zid, z in g.get("zones", {}).items() if not zid.startswith("_")]
    ex = g.get("_example_area")
    if ex:
        areas_by_zone.append((ex.get("zone"), ex))
    seen_areas = set()
    for zid, z in areas_by_zone:
        if zone_ids and zid not in zone_ids:
            errors.append(f"[gather_nodes.json] zone '{zid}' absente de world/zones.json")
        for a in z.get("areas", []):
            aid = a.get("id", "?")
            if aid in seen_areas:
                errors.append(f"[gather_nodes.json] aire en double '{aid}'")
            seen_areas.add(aid)
            nts = [n.get("type") for n in a.get("node_types", [])]
            if not nts:
                errors.append(f"[gather_nodes.json] aire '{aid}' : node_types vide")
            for nt in nts:
                if nt not in types:
                    errors.append(f"[gather_nodes.json] aire '{aid}' : type '{nt}' inconnu")
            water = any(types.get(nt, {}).get("placement") == "water_edge" for nt in nts)
            ground = any(types.get(nt, {}).get("placement") == "ground" for nt in nts)
            if water and ground:
                errors.append(f"[gather_nodes.json] aire '{aid}' : ne pas melanger rive et terre ferme")
            if water:
                pts = a.get("points") or []
                if not pts or a.get("bounds"):
                    errors.append(f"[gather_nodes.json] aire '{aid}' : une rive se pose par points (x, y, facing), "
                                  f"jamais par bounds")
                for pt in pts:
                    if pt.get("facing") not in ("north", "south", "east", "west"):
                        errors.append(f"[gather_nodes.json] aire '{aid}' : point sans facing valide")
            if ground and not a.get("bounds"):
                errors.append(f"[gather_nodes.json] aire '{aid}' : bounds manquant")
            lr = a.get("level_range", [])
            if not (isinstance(lr, list) and len(lr) == 2 and 1 <= lr[0] <= lr[1] <= 100):
                errors.append(f"[gather_nodes.json] aire '{aid}' : level_range invalide")
    return errors


def validate_profession_xp(db: Path) -> list:
    """systems/profession_xp.json : table 2..100 complete et croissante, regle grise, modele de temps dans les cibles."""
    errors = []
    path = db / "systems" / "profession_xp.json"
    if not path.exists():
        return errors
    d = load_json(path)
    t = d.get("xp_table", {})
    prev = 0
    for lvl in range(1, 101):  # xp_table['1'] = pas 0 -> 1 (metiers au niveau 0, 2026-10-01)
        v = t.get(str(lvl))
        if not isinstance(v, int) or v <= 0:
            errors.append(f"[profession_xp.json] xp_table[{lvl}] manquant ou <= 0")
            continue
        if v < prev:
            errors.append(f"[profession_xp.json] xp_table[{lvl}] decroit ({v} < {prev})")
        prev = v
    gr = d.get("gray", {})
    if not (0 <= gr.get("full_until_levels_above", -1) < gr.get("half_at_levels_above", -1)
            < gr.get("zero_from_levels_above", -1)):
        errors.append("[profession_xp.json] gray : full_until < half_at < zero_from")
    hrs = d.get("time_model", {}).get("hours_to_level_crafting", {})
    if hrs and not (3 <= hrs.get("50", 0) <= 7 and 25 <= hrs.get("100", 0) <= 45):
        errors.append(f"[profession_xp.json] modele de temps hors cible : 50 en {hrs.get('50')} h (3-7), 100 en "
                      f"{hrs.get('100')} h (25-45)")
    return errors


def validate_contract_chests(db: Path, all_item_ids: set) -> list:
    """world/quests.json contract_chests : seuils, 5 bandes, objets existants."""
    errors = []
    cc = load_json(db / "world" / "quests.json").get("contract_chests")
    if not cc:
        return errors
    for kind in ("daily", "weekly"):
        c = cc.get(kind, {})
        if int(c.get("contracts_required", 0)) < 1:
            errors.append(f"[quests.json contract_chests.{kind}] contracts_required < 1")
        if len(c.get("gold_by_band", [])) != len(cc.get("bands", [])):
            errors.append(f"[quests.json contract_chests.{kind}] gold_by_band != nombre de bandes")
        ids = [i for pool in c.get("material", {}).get("pool_by_band", []) for i in pool]
        ids += [it["id"] for band in c.get("items_by_band", []) for it in band]
        for i in ids:
            if i not in all_item_ids:
                errors.append(f"[quests.json contract_chests.{kind}] objet inconnu '{i}'")
    return errors


def validate_recipe_chain(db: Path) -> list:
    """Chainage des rangs (Albion sur les intermediaires, 2/2/1/1 sur l'equipement) et lots de fabrication."""
    import re as _re
    errors = []
    path = db / "items" / "profession_recipes.json"
    if not path.exists():
        return errors
    d = load_json(path)
    inter = {i["id"] for i in d.get("new_items", []) if i.get("category") == "intermediate"}
    k_equip = {5: 2, 4: 2, 3: 1, 2: 1}
    batches = [(r"^cons_(hp|mp)_potion_(pet_)?t[1-5]$", 50), (r"^food_", 10), (r"^elix_", 10),
               (r"^scroll_", 10), (r"^pet_treat_", 10), (r"^cons_recall_potion$", 10)]
    eq = _re.compile(r"^((?:wpn|head|chest|legs|feet|belt|cape|acc)_[a-z_]+_b)([1-5])$")
    for r in d.get("recipes", []):
        rid, out = r.get("id", "?"), r.get("output_item", "")
        mats = {m["id"]: m["qty"] for m in r.get("materials", [])}
        m = _re.match(r"^mat_([a-z]+)_r([1-5])$", out)
        if out in inter and m and int(m.group(2)) >= 2:
            prev = f"mat_{m.group(1)}_r{int(m.group(2)) - 1}"
            if mats.get(prev, 0) < 1:
                errors.append(f"[profession_recipes.json] '{rid}' : intermediaire de rang {m.group(2)} sans '{prev}' (regle Albion)")
        m = eq.match(out)
        if m and int(m.group(2)) >= 2:
            n = int(m.group(2))
            prev = m.group(1) + str(n - 1)
            if mats.get(prev, 0) < k_equip[n]:
                errors.append(f"[profession_recipes.json] '{rid}' : piece de rang {n} sans {k_equip[n]} x '{prev}'")
        for pat, size in batches:
            if _re.match(pat, out) and r.get("output_qty") != size:
                errors.append(f"[profession_recipes.json] '{rid}' : lot de {r.get('output_qty')} au lieu de {size}")
    return errors


def validate_rest_npcs(db: Path) -> list:
    """stats/world_buffs.json granted_by_npcs : chaque PNJ de repos existe."""
    errors = []
    npc_ids = set()

    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get("id"), str) and node["id"].startswith("npc_"):
                npc_ids.add(node["id"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(load_json(db / "entities" / "npcs.json"))
    buffs = load_json(db / "stats" / "world_buffs.json").get("world_buffs", {})
    seen = {}
    for bid, d in buffs.items():
        for npc in d.get("granted_by_npcs", []):
            # npc_tavern : identifiant generique encore envoye par un vieux client.
            if npc not in npc_ids and npc != "npc_tavern":
                errors.append(f"[world_buffs.json] {bid}.granted_by_npcs : PNJ inconnu '{npc}'")
            if npc in seen:
                errors.append(f"[world_buffs.json] '{npc}' donne deux buffs de repos ({seen[npc]}, {bid})")
            seen[npc] = bid
    return errors


def _monster_skill_ids(db: Path) -> set:
    """Every skill id of skills/monster_skills.json (combat loads the whole file)."""
    ids = set()

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("id"), str) and ("tier" in o or "target" in o):
                ids.add(o["id"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    path = db / "skills" / "monster_skills.json"
    if path.exists():
        walk(load_json(path))
    return ids


def validate_tower_infinite(db: Path, rules: dict, all_item_ids: set) -> list:
    """Tour infinie (2026-10-18) : presentation, segments de croissance, points de
    reprise, cycle hebdomadaire (affixes + coffre) et classement. Le serveur
    (services/dungeon/src/tower/tower_rules.cpp) refuse les memes erreurs au demarrage."""
    errors = []
    diff = rules["difficulty"]
    pres = rules.get("presentation")
    if pres is not None:
        backdrop = pres.get("combat_backdrop", "")
        zones_text = (db / "world" / "zones.json").read_text(encoding="utf-8")
        if not isinstance(backdrop, str) or (backdrop and f'"combat_backdrop": "{backdrop}"' not in zones_text):
            errors.append(f"[tower.json] presentation.combat_backdrop '{backdrop}' : decor inconnu "
                          "(aucune zone de world/zones.json ne l'utilise)")
    segs = diff.get("stat_growth_segments")
    if segs is not None:
        if not isinstance(segs, list) or not segs:
            errors.append("[tower.json] difficulty.stat_growth_segments : liste non vide attendue")
        else:
            prev = None
            for s in segs:
                ff, pf = s.get("from_floor"), s.get("per_floor")
                if not isinstance(ff, int) or ff < 0 or not isinstance(pf, (int, float)) or not 0 <= pf <= 1:
                    errors.append(f"[tower.json] stat_growth_segments : segment invalide {s}")
                elif prev is not None and ff <= prev:
                    errors.append("[tower.json] stat_growth_segments : from_floor strictement croissants attendus")
                prev = ff if isinstance(ff, int) else prev
            if segs[0].get("from_floor") != diff.get("growth_start_floor") \
                    or segs[0].get("per_floor") != diff.get("stat_growth_per_floor"):
                errors.append("[tower.json] stat_growth_segments[0] doit reprendre growth_start_floor / "
                              "stat_growth_per_floor (compatibilite)")
    tier_size = rules["keys"]["tier_size"]
    every_g = rules["structure"]["guardian_every"]
    cp = rules.get("checkpoints")
    if cp is not None and cp.get("enabled", False):
        every = cp.get("every")
        if not isinstance(every, int) or every <= 0 or every % every_g != 0 or tier_size % every != 0:
            errors.append(f"[tower.json] checkpoints.every={every!r} : multiple de guardian_every={every_g} "
                          f"et diviseur de keys.tier_size={tier_size} attendu")
        if cp.get("scope") != "season":
            errors.append("[tower.json] checkpoints.scope : seule valeur geree 'season'")
        if cp.get("ranked") is not False:
            errors.append("[tower.json] checkpoints.ranked : doit valoir false (une reprise n'est jamais classee)")
    rk = rules.get("ranking")
    if rk is not None:
        mh = rk.get("min_humans")
        if not isinstance(mh, int) or not 1 <= mh <= rules["access"]["max_players"]:
            errors.append(f"[tower.json] ranking.min_humans={mh!r} : entier entre 1 et access.max_players attendu")
        for k in ("distinct_accounts", "distinct_ips", "roster_frozen"):
            if not isinstance(rk.get(k), bool):
                errors.append(f"[tower.json] ranking.{k} : booleen attendu")
    wk = rules.get("weekly")
    if wk is None:
        return errors
    reset = wk.get("reset", {})
    if reset.get("timezone") != "Europe/Paris" or reset.get("weekday") not in (
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday") \
            or not isinstance(reset.get("hour"), int) or not 0 <= reset["hour"] <= 23 or reset["hour"] == 2:
        errors.append("[tower.json] weekly.reset : timezone Europe/Paris, weekday valide, hour 0-23 hors 2 h attendus")
    aff = wk.get("affixes", {})
    pool = aff.get("pool", [])
    skill_ids = _monster_skill_ids(db)
    seen = set()
    for a in pool:
        aid = a.get("id")
        if not aid or aid in seen:
            errors.append(f"[tower.json] weekly.affixes : id vide ou en double '{aid}'")
        seen.add(aid)
        for k in ("name_fr", "name_en", "description_fr", "description_en"):
            if not isinstance(a.get(k), str) or not a[k].strip():
                errors.append(f"[tower.json] affixe '{aid}' : {k} manquant")
            elif "—" in a[k]:
                errors.append(f"[tower.json] affixe '{aid}' : tiret cadratin interdit dans {k}")
        if a.get("applies_to") not in ("monsters", "guardian"):
            errors.append(f"[tower.json] affixe '{aid}' : applies_to doit valoir monsters ou guardian")
        for k in ("hp_mult", "atk_mult", "def_mult"):
            v = a.get(k, 1.0)
            if not isinstance(v, (int, float)) or not 0.1 <= v <= 5.0:
                errors.append(f"[tower.json] affixe '{aid}' : {k}={v!r} hors [0.1, 5]")
        for sid in a.get("extra_skills", []):
            if sid not in skill_ids:
                errors.append(f"[tower.json] affixe '{aid}' : skill inconnu '{sid}' (skills/monster_skills.json)")
        if all(a.get(k, 1.0) == 1.0 for k in ("hp_mult", "atk_mult", "def_mult")) and not a.get("extra_skills"):
            errors.append(f"[tower.json] affixe '{aid}' : ne fait rien (multiplicateurs a 1 et aucun skill)")
    per_week = aff.get("per_week")
    froms = aff.get("from_floors", [])
    if not isinstance(per_week, int) or not 1 <= per_week <= len(pool):
        errors.append(f"[tower.json] weekly.affixes.per_week={per_week!r} : entre 1 et la taille du pool ({len(pool)})")
    if not isinstance(froms, list) or len(froms) != per_week:
        errors.append("[tower.json] weekly.affixes.from_floors : une entree par affixe tire (per_week) attendue")
    elif any(not isinstance(x, int) or x < 1 for x in froms) or any(b <= a for a, b in zip(froms, froms[1:])):
        errors.append("[tower.json] weekly.affixes.from_floors : etages >= 1 strictement croissants attendus")
    if not isinstance(aff.get("seed"), int):
        errors.append("[tower.json] weekly.affixes.seed : entier attendu")
    prev = 0
    for t in wk.get("chest", {}).get("thresholds", []):
        fl = t.get("floor")
        if not isinstance(fl, int) or fl <= prev:
            errors.append(f"[tower.json] weekly.chest : seuils strictement croissants attendus ({fl!r})")
        prev = fl if isinstance(fl, int) else prev
        if not isinstance(t.get("gold", 0), int) or t.get("gold", 0) < 0 \
                or not isinstance(t.get("arena_tokens", 0), int) or t.get("arena_tokens", 0) < 0:
            errors.append(f"[tower.json] weekly.chest seuil {fl} : or / jetons entiers >= 0 attendus")
        for it in t.get("items", []):
            if it.get("id") not in all_item_ids or not isinstance(it.get("qty"), int) or it["qty"] < 1:
                errors.append(f"[tower.json] weekly.chest seuil {fl} : objet inconnu ou quantite invalide {it}")
    return errors


def validate_tower(db: Path, all_item_ids: set) -> list:
    """systems/tower.json + world/tower_floors.json : monstres actifs, cles, bornes."""
    errors = []
    rules_path, floors_path = db / "systems" / "tower.json", db / "world" / "tower_floors.json"
    if not rules_path.exists():
        return errors
    rules = load_json(rules_path)
    mons = load_json(db / "entities" / "monsters.json")
    roster = {m["id"]: m for m in (mons["monsters"] if isinstance(mons, dict) else mons)}
    diff, access = rules["difficulty"], rules["access"]
    for name, ids in diff["pools"].items():
        for mid in ids:
            if mid not in roster:
                errors.append(f"[tower.json] pool '{name}' : monstre inconnu '{mid}'")
            elif roster[mid].get("roster_status") != "active":
                errors.append(f"[tower.json] pool '{name}' : '{mid}' n'est pas actif (pas d'art client)")
    for row in diff["floor_pools"]:
        for name in row["pools"]:
            if name not in diff["pools"]:
                errors.append(f"[tower.json] floor_pools : pool inconnu '{name}'")
    for decade in diff["guardians_by_decade"]:
        for mid in decade:
            if mid not in roster or roster[mid].get("roster_status") != "active":
                errors.append(f"[tower.json] gardien '{mid}' inconnu ou inactif")
    keys = rules["keys"]
    for tier in range(2, keys["max_tier"] + 1):
        if f"{keys['item_prefix']}{tier}" not in all_item_ids:
            errors.append(f"[tower.json] cle '{keys['item_prefix']}{tier}' absente des objets")
    for item in rules["rewards"]["guardian_chest"]["items"]:
        if item["id"] not in all_item_ids:
            errors.append(f"[tower.json] coffre de gardien : objet inconnu '{item['id']}'")
    errors += validate_tower_infinite(db, rules, all_item_ids)
    if not floors_path.exists():
        return errors + ["[tower_floors.json] absent : lancer scripts/generate_tower.py"]
    cap = diff["stat_multiplier_cap"]
    for fl in load_json(floors_path)["floors"]:
        ms = fl["monsters"]
        if not 0 < len(ms) <= access["max_monsters"]:
            errors.append(f"[tower_floors.json] etage {fl['floor']} : {len(ms)} monstres (1..{access['max_monsters']})")
        for m in ms:
            if m["template_id"] not in roster:
                errors.append(f"[tower_floors.json] etage {fl['floor']} : monstre inconnu '{m['template_id']}'")
            if not 1 <= m["level"] <= 255 or not 0 <= m["star_level"] <= 5:
                errors.append(f"[tower_floors.json] etage {fl['floor']} : niveau ou etoiles hors bornes")
            if any(not 0.1 <= m[k] <= cap for k in ("hp_multiplier", "atk_multiplier", "def_multiplier")):
                errors.append(f"[tower_floors.json] etage {fl['floor']} : multiplicateur hors [0.1, {cap}]")
    return errors


# ---------------------------------------------------------------------------
# 12w. Evenements hebdomadaires + boutique de jetons (lot 1 endgame, 2026-10-18).
# Le calendrier dit QUAND (world/event_calendar.json), rewards.json dit COMBIEN
# (multiplier_families.events). Le serveur (presence) refuse de demarrer le calendrier
# sur une valeur inconnue : la garde le dit avant.
# ---------------------------------------------------------------------------

EVENT_KEYS = ("xp", "gold", "drop_chance", "rarity_boost", "profession_xp", "rift_frequency",
              "capture_chance", "arena_tokens")
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def validate_event_calendar(db: Path) -> list:
    errors = []
    cal_path = db / "world" / "event_calendar.json"
    if not cal_path.exists():
        return errors
    cal = load_json(cal_path)
    values = load_json(db / "config" / "rewards.json").get("multiplier_families", {})         .get("events", {}).get("values", {})
    for name, body in values.items():
        if name.startswith("_") or not isinstance(body, dict):
            continue
        for k, v in body.items():
            if k.startswith("_"):
                continue
            if k not in EVENT_KEYS:
                errors.append(f"[rewards.events] {name}.{k} : clef inconnue (connues : {', '.join(EVENT_KEYS)})")
            elif k != "rarity_boost" and not (isinstance(v, (int, float)) and 0 < v <= 5):
                errors.append(f"[rewards.events] {name}.{k}={v} hors de ]0, 5]")
    weeks = cal.get("cycle", {}).get("weeks", 0)
    anchor = cal.get("cycle", {}).get("anchor_monday", "")
    try:
        import datetime
        if datetime.date.fromisoformat(anchor).weekday() != 0:
            errors.append(f"[event_calendar] cycle.anchor_monday {anchor} n'est pas un lundi")
    except ValueError:
        errors.append(f"[event_calendar] cycle.anchor_monday '{anchor}' n'est pas une date AAAA-MM-JJ")
    if not isinstance(weeks, int) or weeks < 1:
        errors.append("[event_calendar] cycle.weeks doit etre un entier >= 1")
    seen = set()
    for ev in cal.get("events", []):
        eid = ev.get("id", "")
        if eid in seen:
            errors.append(f"[event_calendar] id en double '{eid}'")
        seen.add(eid)
        if ev.get("reward_value") not in values:
            errors.append(f"[event_calendar] {eid} : reward_value '{ev.get('reward_value')}' absente de "
                          f"rewards.json multiplier_families.events.values")
        for f in ("name_fr", "name_en", "description_fr", "description_en"):
            if not ev.get(f):
                errors.append(f"[event_calendar] {eid} : {f} manquant")
            elif "—" in ev[f]:
                errors.append(f"[event_calendar] {eid} : tiret cadratin dans {f}")
        for w in ev.get("weeks", []):
            if not isinstance(w, int) or not 0 <= w < max(weeks, 1):
                errors.append(f"[event_calendar] {eid} : semaine {w} hors du cycle de {weeks}")
        if not ev.get("weeks"):
            errors.append(f"[event_calendar] {eid} : weeks vide")
        for bound in ("start", "end"):
            b = ev.get(bound, {})
            if b.get("weekday") not in WEEKDAYS:
                errors.append(f"[event_calendar] {eid}.{bound}.weekday '{b.get('weekday')}' inconnu")
            t = str(b.get("time", ""))
            ok = len(t) == 5 and t[2] == ":" and t[:2].isdigit() and t[3:].isdigit()                 and int(t[:2]) < 24 and int(t[3:]) < 60
            if not ok:
                errors.append(f"[event_calendar] {eid}.{bound}.time '{t}' n'est pas HH:MM")
            elif t[:2] == "02":
                errors.append(f"[event_calendar] {eid}.{bound}.time {t} : 02:xx tombe dans l'heure "
                              f"ambigue du changement d'heure")
    return errors


def validate_world_elites(db: Path) -> list:
    """Elites et boss des aires du monde (2026-10-18) : monstres actifs (art client), chances
    dans [0, 1]. presence lit elite_pool, elite_pack_chance et boss.{id, pack_chance}."""
    errors = []
    mons = load_json(db / "entities" / "monsters.json")
    roster = {m["id"]: m for m in (mons["monsters"] if isinstance(mons, dict) else mons)}
    for zone in load_json(db / "world" / "zones.json").get("zones", []):
        for sa in zone.get("spawn_areas", []) or []:
            where = f"[zones.json] {zone.get('id')}/{sa.get('id')}"
            ids = list(sa.get("elite_pool", []) or [])
            if isinstance(sa.get("boss"), dict) and sa["boss"].get("id"):
                ids.append(sa["boss"]["id"])
                pc = sa["boss"].get("pack_chance", 1.0)
                if not (isinstance(pc, (int, float)) and 0 <= pc <= 1):
                    errors.append(f"{where} : boss.pack_chance={pc} hors de [0, 1]")
            ec = sa.get("elite_pack_chance", 1.0)
            if not (isinstance(ec, (int, float)) and 0 <= ec <= 1):
                errors.append(f"{where} : elite_pack_chance={ec} hors de [0, 1]")
            for mid in ids:
                if mid not in roster:
                    errors.append(f"{where} : elite/boss inconnu '{mid}'")
                elif roster[mid].get("roster_status", "active") != "active":
                    errors.append(f"{where} : elite/boss '{mid}' n'est pas actif (pas d'art client)")
    return errors


def validate_arena_token_shop(db: Path, all_item_ids: set) -> list:
    errors = []
    path = db / "systems" / "arena_token_shop.json"
    if not path.exists():
        return errors
    shop = load_json(path)
    emotes = {e["id"] for e in load_json(db / "ui" / "emotes.json").get("emotes", [])}
    cosmetics = {c["id"] for c in load_json(db / "ui" / "cosmetics.json").get("cosmetics", [])}
    # Les objets des metiers (Braises, parchemins...) vivent dans profession_recipes.json new_items.
    pr = db / "items" / "profession_recipes.json"
    if pr.exists():
        all_item_ids = set(all_item_ids) | {i["id"] for i in load_json(pr).get("new_items", []) if "id" in i}
    cats = set(shop.get("categories", {}))
    seen = set()
    for o in shop.get("offers", []):
        oid = o.get("id", "")
        if oid in seen:
            errors.append(f"[arena_token_shop] offre en double '{oid}'")
        seen.add(oid)
        kind, gid = o.get("kind"), o.get("grant_id", "")
        known = {"item": all_item_ids, "emote": emotes, "cosmetic": cosmetics}.get(kind)
        if known is None:
            errors.append(f"[arena_token_shop] {oid} : kind '{kind}' inconnu (item|emote|cosmetic)")
        elif gid not in known:
            errors.append(f"[arena_token_shop] {oid} : {kind} '{gid}' introuvable")
        if not _is_pos_int(o.get("price")):
            errors.append(f"[arena_token_shop] {oid} : price doit etre un entier > 0")
        if kind == "item" and not _is_pos_int(o.get("quantity")):
            errors.append(f"[arena_token_shop] {oid} : quantity doit etre un entier > 0")
        if not _is_nonneg_int(o.get("weekly_cap", 0)) or not _is_nonneg_int(o.get("min_level", 0)):
            errors.append(f"[arena_token_shop] {oid} : weekly_cap / min_level doivent etre des entiers >= 0")
        if o.get("category") not in cats:
            errors.append(f"[arena_token_shop] {oid} : categorie '{o.get('category')}' inconnue")
        if kind == "item" and o.get("category") == "progress" and not o.get("weekly_cap"):
            errors.append(f"[arena_token_shop] {oid} : un objet de progression doit avoir un weekly_cap")
        if kind == "item" and any(gid.endswith(sfx) for sfx in ("_rank_3", "_rank_4", "_rank_5", "_r3", "_r4", "_r5")):
            errors.append(f"[arena_token_shop] {oid} : '{gid}' est de rang 3+, regle volume-jamais-puissance")
    if not _is_pos_int(shop.get("max_lots_per_purchase")):
        errors.append("[arena_token_shop] max_lots_per_purchase doit etre un entier > 0")
    return errors


# ---------------------------------------------------------------------------
# 13. Single sources of gameplay values (refacto vac_refactor-lot1, 2026-10-14).
# The server reads each of these values from ONE file and refuses to start when
# it is absent (no C++ default). These checks never pin a number: they check
# that the owner carries a usable value and that every mirror kept for the
# client says the same thing.
# ---------------------------------------------------------------------------

ALLOCATABLE_STATS = ("hp", "mp", "atk", "mag", "def")


def _is_pos_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def validate_stat_point_values(db: Path) -> list:
    """config/game.json stats_definition owns the value of one allocated point."""
    errors = []
    game = load_json(db / "config" / "game.json")
    prog = load_json(db / "systems" / "progression.json")
    sd = game.get("stats_definition")
    if not isinstance(sd, dict):
        return ["[game.json] stats_definition absent : le combat et l'economie refusent de demarrer"]
    owner = {}
    for stat in ALLOCATABLE_STATS:
        v = (sd.get(stat) or {}).get("point_value") if isinstance(sd.get(stat), dict) else None
        if not _is_pos_int(v):
            errors.append(f"[game.json] stats_definition.{stat}.point_value absent ou non entier > 0 ({v!r})")
        owner[stat] = v
    alloc = prog.get("stat_allocation", {})
    listed = alloc.get("allocatable_stats")
    if listed is not None and sorted(listed) != sorted(ALLOCATABLE_STATS):
        errors.append(f"[progression.json] stat_allocation.allocatable_stats={listed} : le serveur "
                      f"lit exactement {list(ALLOCATABLE_STATS)}")
    mirror = alloc.get("point_values")
    if isinstance(mirror, dict):
        for stat in ALLOCATABLE_STATS:
            if mirror.get(stat) != owner.get(stat):
                errors.append(f"[progression.json] DERIVE stat_allocation.point_values.{stat}="
                              f"{mirror.get(stat)!r}, source game.json={owner.get(stat)!r}")
    return errors


def _is_nonneg_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def validate_level_grants(db: Path) -> list:
    """systems/progression.json stat_allocation owns the level-up grants."""
    errors = []
    prog = load_json(db / "systems" / "progression.json")
    sa = prog.get("stat_allocation", {})
    keys = ("points_per_level", "skill_points_per_level", "passive_points_per_level", "starting_skill_points")
    for k in keys:
        if not _is_nonneg_int(sa.get(k)):
            errors.append(f"[progression.json] stat_allocation.{k} absent ou non entier >= 0 "
                          f"({sa.get(k)!r}) : economie, quete et personnage refusent de demarrer")
    if errors:
        return errors
    max_level = prog.get("leveling", {}).get("max_level")
    total = sa.get("total_stat_points_at_max_level")
    if isinstance(max_level, int) and total is not None and total != sa["points_per_level"] * (max_level - 1):
        errors.append(f"[progression.json] stat_allocation.total_stat_points_at_max_level={total}, "
                      f"attendu points_per_level x (max_level - 1) = {sa['points_per_level'] * (max_level - 1)}")
    gc = load_json(db / "config" / "game.json").get("game_constants", {})
    for mirror, owner in (("stat_points_per_level", "points_per_level"),
                          ("skill_points_per_level", "skill_points_per_level")):
        if mirror in gc and gc[mirror] != sa[owner]:
            errors.append(f"[game.json] DERIVE game_constants.{mirror}={gc[mirror]!r}, "
                          f"source progression.json stat_allocation.{owner}={sa[owner]!r}")
    sp = load_json(db / "config" / "skill_system.json").get("skill_points", {})
    for mirror, owner in (("points_per_level", "skill_points_per_level"),
                          ("starting_points", "starting_skill_points")):
        if mirror in sp and sp[mirror] != sa[owner]:
            errors.append(f"[skill_system.json] DERIVE skill_points.{mirror}={sp[mirror]!r}, "
                          f"source progression.json stat_allocation.{owner}={sa[owner]!r}")
    top = sp.get("max_player_level")
    if "total_points_available" in sp and isinstance(top, int):
        expected = sa["starting_skill_points"] + sa["skill_points_per_level"] * (top - 1)
        if sp["total_points_available"] != expected:
            errors.append(f"[skill_system.json] skill_points.total_points_available="
                          f"{sp['total_points_available']}, attendu {expected} (depart + par niveau x {top - 1})")
    return errors


ITEM_RARITIES = ("common", "uncommon", "rare", "epic", "legendary")


def validate_rarity_power(db: Path) -> list:
    """items/equipment_scaling.json rarity_system.rarities.<r>.power_mult owns the item power."""
    errors = []
    rarities = load_json(db / "items" / "equipment_scaling.json").get("rarity_system", {}).get("rarities")
    if not isinstance(rarities, dict):
        return ["[equipment_scaling.json] rarity_system.rarities absent : l'economie refuse de demarrer"]
    for r in ITEM_RARITIES:
        if r not in rarities:
            errors.append(f"[equipment_scaling.json] rarete '{r}' absente de rarity_system.rarities "
                          f"(le serveur exige les cinq)")
    power = {}
    for r, entry in rarities.items():
        if r.startswith("_"):
            continue
        v = entry.get("power_mult") if isinstance(entry, dict) else None
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
            errors.append(f"[equipment_scaling.json] rarity_system.rarities.{r}.power_mult absent "
                          f"ou <= 0 ({v!r}) : le fichier est refuse")
            continue
        power[r] = v
    ordered = [(r, power[r]) for r in ITEM_RARITIES if r in power]
    for (lo, a), (hi, b) in zip(ordered, ordered[1:]):
        if b < a:
            errors.append(f"[equipment_scaling.json] power_mult de '{hi}' ({b}) inferieur a celui de "
                          f"'{lo}' ({a}) : une rarete superieure ne peut pas valoir moins")
    return errors


def validate_star_roll_weights(db: Path) -> list:
    """entities/monster_variants.json star_system.roll_weights owns the pack star draw."""
    errors = []
    w = load_json(db / "entities" / "monster_variants.json").get("star_system", {}).get("roll_weights")
    ok = (isinstance(w, list) and len(w) == 6
          and all(isinstance(x, (int, float)) and not isinstance(x, bool) and x >= 0 for x in w)
          and sum(w) > 0)
    if not ok:
        return [f"[monster_variants.json] star_system.roll_weights={w!r} : 6 poids >= 0 de somme > 0 "
                f"attendus (etoiles 0..5), sinon presence refuse de demarrer"]
    mirror = load_json(db / "config" / "game.json").get("spawner", {}).get("star_roll_weights")
    if mirror is not None and [float(x) for x in mirror] != [float(x) for x in w]:
        errors.append(f"[game.json] DERIVE spawner.star_roll_weights={mirror}, "
                      f"source monster_variants.json star_system.roll_weights={w}")
    tiers = load_json(db / "systems" / "encounter_stars.json").get("star_tiers", {})
    for s in range(6):
        if str(s) not in tiers:
            errors.append(f"[encounter_stars.json] star_tiers.{s} absent : presence refuse de demarrer "
                          f"(plus de table de repli C++)")
    return errors


def validate_respec_cost(db: Path) -> list:
    """systems/economy.json gold_sinks.respec owns the stat / skill / passive reset price."""
    r = load_json(db / "systems" / "economy.json").get("gold_sinks", {}).get("respec")
    if not isinstance(r, dict):
        return ["[economy.json] gold_sinks.respec absent : les trois resets sont fermes"]
    errors = []
    for k in ("free_until_level", "gold_per_level_above"):
        if not _is_nonneg_int(r.get(k)):
            errors.append(f"[economy.json] gold_sinks.respec.{k} absent ou non entier >= 0 ({r.get(k)!r}) : "
                          f"les trois resets sont fermes")
    for dead in ("base_cost",):
        if dead in r:
            errors.append(f"[economy.json] gold_sinks.respec.{dead} est revenu : la regle est par niveau "
                          f"(free_until_level / gold_per_level_above), pas par nombre de resets")
    return errors


def validate_koro_equipment(db: Path) -> list:
    """systems/koro.json equipment owns the number of Koro cards and their unlock levels."""
    eq = load_json(db / "systems" / "koro.json").get("equipment")
    if not isinstance(eq, dict):
        return ["[koro.json] equipment absent : le combat refuse de demarrer, l'economie ferme les cartes"]
    errors = []
    n = eq.get("max_equipped")
    if not _is_pos_int(n):
        return [f"[koro.json] equipment.max_equipped={n!r} : entier >= 1 attendu"]
    levels = eq.get("slot_unlock_levels")
    if (not isinstance(levels, list) or len(levels) != n
            or not all(_is_pos_int(v) for v in levels)
            or any(b <= a for a, b in zip(levels, levels[1:]))):
        errors.append(f"[koro.json] equipment.slot_unlock_levels={levels!r} : {n} niveaux >= 1 strictement "
                      f"croissants attendus (un par emplacement)")
    cards_meta = load_json(db / "items" / "koro_cards.json").get("_meta", {})
    if "max_equipped" in cards_meta and cards_meta["max_equipped"] != n:
        errors.append(f"[koro_cards.json] DERIVE _meta.max_equipped={cards_meta['max_equipped']}, "
                      f"source koro.json equipment.max_equipped={n} (relancer generate_koro_catalog.py)")
    return errors


def validate_guild_rules(db: Path) -> list:
    """guild/levels.json owns the capacity by level, systems/guilds.json the creation cost."""
    errors = []
    gcfg = load_json(db / "guild" / "config.json")
    levels = load_json(db / "guild" / "levels.json").get("levels", [])
    max_level = gcfg.get("max_level")
    capacity = {}
    for row in levels:
        lvl, cap = row.get("level"), row.get("max_members")
        if not _is_pos_int(cap):
            errors.append(f"[guild/levels.json] niveau {lvl} : max_members={cap!r}, entier >= 1 attendu "
                          f"(capacite de la guilde a ce niveau)")
            continue
        capacity[lvl] = cap
    for lvl in sorted(capacity):
        if lvl - 1 in capacity and capacity[lvl] < capacity[lvl - 1]:
            errors.append(f"[guild/levels.json] la capacite baisse au niveau {lvl} "
                          f"({capacity[lvl - 1]} -> {capacity[lvl]}) : une guilde qui monte perdrait des places")
    guilds = load_json(db / "systems" / "guilds.json")
    cfg = guilds.get("config", {})
    cost = cfg.get("creation_cost")
    if not _is_nonneg_int(cost):
        errors.append(f"[guilds.json] config.creation_cost={cost!r} : entier >= 0 attendu, sinon le service "
                      f"de guilde refuse de demarrer")
    for dead in ("base_max_members",):
        if dead in cfg:
            errors.append(f"[guilds.json] config.{dead} est revenu : la capacite suit le niveau (guild/levels.json)")
    if "max_guild_level" in cfg and cfg["max_guild_level"] != max_level:
        errors.append(f"[guilds.json] DERIVE config.max_guild_level={cfg['max_guild_level']}, "
                      f"source guild/config.json max_level={max_level}")
    for key, row in guilds.get("level_data", {}).items():
        if key.startswith("_") or not isinstance(row, dict) or "max_members" not in row:
            continue
        lvl = int(key)
        if capacity.get(lvl) != row["max_members"]:
            errors.append(f"[guilds.json] DERIVE level_data.{key}.max_members={row['max_members']}, "
                          f"source guild/levels.json={capacity.get(lvl)!r}")
    eco = load_json(db / "systems" / "economy.json").get("gold_sinks", {}).get("guild", {})
    if "creation_cost" in eco and eco["creation_cost"] != cost:
        errors.append(f"[economy.json] DERIVE gold_sinks.guild.creation_cost={eco['creation_cost']}, "
                      f"source guilds.json config.creation_cost={cost!r}")
    return errors


def validate_party_size(db: Path) -> list:
    """config/game.json game_constants.max_party_size owns the party / team size."""
    n = load_json(db / "config" / "game.json").get("game_constants", {}).get("max_party_size")
    if not _is_pos_int(n):
        return [f"[game.json] game_constants.max_party_size={n!r} : entier >= 1 attendu, sinon groupe, "
                f"combat, presence, pvp et donjon refusent de demarrer"]
    errors = []
    access = load_json(db / "systems" / "tower.json").get("access", {})
    for k in ("max_allies", "max_players"):
        v = access.get(k)
        if v is not None and (not _is_pos_int(v) or v > n):
            errors.append(f"[tower.json] access.{k}={v!r} : entier entre 1 et max_party_size={n} attendu "
                          f"(le service de donjon refuse la tour sinon)")
    return errors


STAT_CAPS = [  # (category, stat, max allowed) — read by shared/gameplay/stat_caps.hpp
    ("offensive", "crit", 100), ("offensive", "crit_dmg", 1000), ("offensive", "damage_percent", 1000),
    ("offensive", "double_hit_chance", 100), ("offensive", "triple_hit_chance", 100),
    ("offensive", "armor_pen", 100), ("offensive", "magic_pen", 100), ("offensive", "debuff_duration", 1000),
    ("offensive", "shield_pierce", 100), ("defensive", "damage_reduction", 100),
    ("defensive", "block_chance", 100), ("defensive", "parry_chance", 100), ("defensive", "effect_resist", 100),
    ("defensive", "tenacity", 100), ("precision", "flee", 100), ("support", "healing_received", 1000),
    ("special", "lifesteal", 100), ("special", "spell_vamp", 100), ("special", "reflect", 100),
    ("special", "thorns", 100),
    ("special", "cast_speed", 100), ("special", "cooldown_reduction", 100),
]
BUFF_DURATION_TYPES = ("buff", "hot", "immunity", "shield")


def validate_stat_caps(db: Path) -> list:
    """stats/definitions.json owns every stat cap; combat and economy refuse to start without them."""
    errors = []
    defs = load_json(db / "stats" / "definitions.json")
    stats = defs.get("stats", {})
    for cat, stat, hi in STAT_CAPS:
        v = (stats.get(cat, {}).get(stat) or {}).get("cap")
        if not (isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= hi):
            errors.append(f"[definitions.json] stats.{cat}.{stat}.cap absent ou hors [0, {hi}] ({v!r})")
    refl = stats.get("special", {}).get("reflect") or {}
    if not (isinstance(refl.get("cap_permanent"), int) and isinstance(refl.get("cap"), int)
            and 0 <= refl["cap_permanent"] <= refl["cap"]):
        errors.append(f"[definitions.json] stats.special.reflect.cap_permanent absent ou > cap "
                      f"({refl.get('cap_permanent')!r} / {refl.get('cap')!r})")
    asp = (stats.get("offensive", {}).get("attack_speed") or {}).get("cap")
    if not (isinstance(asp, (int, float)) and 1 <= asp <= 10):
        errors.append(f"[definitions.json] stats.offensive.attack_speed.cap absent ou hors [1, 10] ({asp!r})")
    by = (stats.get("support", {}).get("buff_duration") or {}).get("cap_by_effect_type")
    if not isinstance(by, dict):
        errors.append("[definitions.json] stats.support.buff_duration.cap_by_effect_type absent")
        by = {}
    for t in BUFF_DURATION_TYPES:
        if not (isinstance(by.get(t), int) and 0 <= by[t] <= 1000):
            errors.append(f"[definitions.json] buff_duration.cap_by_effect_type.{t} absent ou invalide ({by.get(t)!r})")
    af = defs.get("effect_system", {}).get("apply_formula", {})
    lo, hi = af.get("apply_chance_min"), af.get("apply_chance_max")
    if not (isinstance(lo, int) and isinstance(hi, int) and 0 <= lo <= hi <= 100):
        errors.append(f"[definitions.json] effect_system.apply_formula.apply_chance_min/max invalides ({lo!r}, {hi!r})")
    md = defs.get("effect_system", {}).get("duration_formula", {}).get("minimum_duration")
    if not (isinstance(md, (int, float)) and 0 <= md <= 10):
        errors.append(f"[definitions.json] effect_system.duration_formula.minimum_duration invalide ({md!r})")
    clamp = (stats.get("precision", {}).get("hit") or {}).get("clamp", {})
    if not (isinstance(clamp.get("min"), int) and isinstance(clamp.get("max"), int)
            and 0 <= clamp["min"] <= clamp["max"] <= 100):
        errors.append(f"[definitions.json] stats.precision.hit.clamp invalide ({clamp!r})")

    # No permanent immunity: an immunity extended by the buff duration cap must end before
    # the skill comes back (owner, 2026-10-14).
    imm_cap = by.get("immunity") if isinstance(by.get("immunity"), int) else 0
    effects = load_json(db / "stats" / "status_effects.json").get("effects", {})
    immunity_ids = {k for k in effects.get("immunity", {}) if not k.startswith("_")}
    def skill_dicts(node):
        if isinstance(node, dict):
            if "id" in node and isinstance(node.get("effects"), list):
                yield node
            for v in node.values():
                yield from skill_dicts(v)
        elif isinstance(node, list):
            for v in node:
                yield from skill_dicts(v)

    for path in sorted((db / "classes").glob("*/*skills*.json")) + sorted((db / "skills").glob("*.json")):
        for sk in skill_dicts(load_json(path)):
            if not isinstance(sk.get("cooldown"), (int, float)):
                continue
            cd = float(sk["cooldown"])
            max_lv = sk.get("max_level", 1) if isinstance(sk.get("max_level"), int) else 1
            for eff in sk.get("effects", []) or []:
                if not isinstance(eff, dict):
                    continue
                eid = eff.get("stat") or eff.get("status") or eff.get("effect_id") or eff.get("id")
                if eid not in immunity_ids or not isinstance(eff.get("duration"), (int, float)):
                    continue
                dur = float(eff["duration"]) + float(eff.get("duration_per_level", 0) or 0) * (max_lv - 1)
                longest = dur * (1 + imm_cap / 100)
                if cd > 0 and longest >= cd:
                    errors.append(f"[{path.relative_to(db).as_posix()}] {sk.get('id')} : {eid} {dur:g} s "
                                  f"x {1 + imm_cap / 100:g} (duree des buffs max) = {longest:g} s >= recharge "
                                  f"{cd:g} s : immunite permanente")
    return errors


GCD_KEYS = (("gcd_duration", 0.1), ("familiar_gcd_duration", 0.1), ("monster_gcd_duration", 0.1),
            ("monster_gcd_jitter", 0.0), ("monster_first_gcd_jitter", 0.0), ("monster_first_gcd_bonus", 0.0))


def validate_gcd(db: Path) -> list:
    """config/combat.json settings owns every GCD; the combat service refuses to start without them."""
    s = load_json(db / "config" / "combat.json").get("settings", {})
    errors = []
    for key, lo in GCD_KEYS:
        v = s.get(key)
        if not (isinstance(v, (int, float)) and not isinstance(v, bool) and lo <= v <= 30):
            errors.append(f"[combat.json] settings.{key} absent ou hors [{lo}, 30] secondes ({v!r})")
    return errors


def validate_combat_mirrors(db: Path) -> list:
    """config/combat.json keeps a few values the client reads; each must equal its owner."""
    combat = load_json(db / "config" / "combat.json")
    defs = load_json(db / "stats" / "definitions.json")
    mirror = combat.get("settings", {}).get("damage", {}).get("damage_reduction_cap")
    owner = defs.get("stats", {}).get("defensive", {}).get("damage_reduction", {}).get("cap")
    if mirror != owner:
        return [f"[combat.json] DERIVE settings.damage.damage_reduction_cap={mirror!r}, "
                f"source definitions.json defensive.damage_reduction.cap={owner!r}"]
    return []


def validate_social_limits(db: Path) -> list:
    """systems/social.json owns the friend / block limits; the social service refuses to start without them."""
    social = load_json(db / "systems" / "social.json")
    errors = []
    for section, key in (("friends", "max_friends"), ("block_ignore", "max_blocked")):
        v = social.get(section, {}).get(key)
        if not (isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 10000):
            errors.append(f"[social.json] {section}.{key} absent ou hors [1, 10000] ({v!r})")
    return errors


SINGLE_SOURCE_CHECKS = [
    validate_stat_point_values,
    validate_level_grants,
    validate_rarity_power,
    validate_star_roll_weights,
    validate_respec_cost,
    validate_koro_equipment,
    validate_guild_rules,
    validate_party_size,
    validate_stat_caps,
    validate_gcd,
    validate_combat_mirrors,
    validate_social_limits,
]


def validate_single_sources(db: Path) -> list:
    errors = []
    for check in SINGLE_SOURCE_CHECKS:
        try:
            errors.extend(check(db))
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
            errors.append(f"[{check.__name__}] lecture impossible : {e!r}")
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

    print("\n[1/10] Validating affix stat names...")
    errs = validate_affixes(db, valid_stats)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[2/10] Validating equipment_stats stat names...")
    errs = validate_equipment_stats(db, valid_stats)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[3/10] Validating class_tags...")
    errs = validate_class_tags(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[4/10] Validating loot table item references...")
    all_item_ids = collect_all_item_ids(db)
    print(f"  Collected {len(all_item_ids)} item IDs from database")
    errs = validate_loot_table_refs(db, all_item_ids)
    all_errors.extend(errs)
    errs = validate_every_monster_has_loot_table(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[5/10] Validating set_id references...")
    errs = validate_set_ids(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[6/10] Validating recipe output_item references...")
    errs = validate_recipe_outputs(db, all_item_ids)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[6b/10] Validating enhancement success rates (one per level)...")
    errs = validate_enhancement_rates(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[7/10] Validating item rank bands (C->SS) across their 3 copies...")
    errs = validate_item_ranks(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[7b/10] Validating displayed rank letters (internal C..SS shown as D..S)...")
    errs = validate_rank_display(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[8/10] Validating rewards contract (config/rewards.json)...")
    errs = validate_rewards(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[9/10] Validating mercenary balance profile slots (PvE vs PvP)...")
    errs = validate_mercenary_balance_slots(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[10/11] Validating skill AoE patterns exist in targeting.json...")
    errs = validate_skill_patterns(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[11/11] Validating the item display contract (rolls, affixes, sockets)...")
    errs = validate_item_display_contract(db, valid_stats)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12b/12] Validating zone chests (items, zones, tiers)...")
    errs = validate_zone_chests(db, all_item_ids)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12b2/12] Validating teleport steles (zones, ids, rules)...")
    errs = validate_teleport_steles(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12c/12] Validating fissure invasions (zones, bounds)...")
    errs = validate_fissure_invasions(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12c2/12] Validating rift interiors (schedule, sizes, tiers, map slots, embers, reward blocks)...")
    errs = validate_rift_events(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12f/12] Validating professions (material uses, declared links, no isolated profession)...")
    errs = validate_professions(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12g/12] Validating profession recipes (items, ranks, cross-profession links, cycles)...")
    errs = validate_profession_recipes(db, all_item_ids)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12i/12] Validating resource rarity rule (tiers, suffixes, no hand-written variant)...")
    errs = validate_resource_rarity(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12j/12] Validating gather nodes (professions, tools, resources, ranks, rarity, areas)...")
    errs = validate_gather_nodes(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12k/12] Validating profession XP curve (table, gray rule, time model)...")
    errs = validate_profession_xp(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12l/12] Validating rank chaining and craft batches...")
    errs = validate_recipe_chain(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12h/12] Validating contract chests (daily/weekly)...")
    errs = validate_contract_chests(db, all_item_ids)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12e/12] Validating rest NPCs of world buffs (tavern, healer)...")
    errs = validate_rest_npcs(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12d/12] Validating the Rift Tower (pools, guardians, keys, floors)...")
    errs = validate_tower(db, all_item_ids)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12/12] Validating achievements (engine sources, grant titles, quests)...")
    errs = validate_achievements(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12q/12] Validating the quest engine contract (writers, rewards, flags, windows)...")
    errs = validate_quest_engine(db, all_item_ids)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[12w/12] Validating weekly events (calendar -> rewards.json events) and the token shop...")
    errs = validate_event_calendar(db) + validate_arena_token_shop(db, all_item_ids) + validate_world_elites(db)
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else f'FAIL ({len(errs)} errors)'}")

    print("[13/13] Validating single sources of gameplay values (owner present, mirrors equal)...")
    errs = validate_single_sources(db)
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
