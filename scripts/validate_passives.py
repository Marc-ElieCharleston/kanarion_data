#!/usr/bin/env python3
"""
Validateur des passifs — cree le 2026-08-02.

AVANT ce script, AUCUN validateur ne regardait les passifs : 126 entrees reparties
dans 31 fichiers, zero controle automatique. Meme angle mort que les sorts tier3,
mais total. C'est ce genre de trou qui laisse vivre de la donnee morte pendant des
mois (voir le champ attack_speed, inerte depuis le retrait des auto-attaques).

Ce qu'il verifie :
  1. chaque `stat` existe dans stats/definitions.json
  2. chaque `effect_id` existe dans stats/status_effects.json
  3. aucune stat connue comme MORTE n'est utilisee
  4. `op` est add_flat ou add_percent
  5. les passifs levelables ont un max_level (les innes n'en ont pas, c'est voulu)
  6. aucun id de passif en double dans toute la base

Exit 0 = tout va bien, exit 1 = erreurs.
"""

import json
import glob
import os
import sys
import collections

DB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Stats mortes cote moteur. Les utiliser = un joueur investit pour rien.
#   attack_speed : n'alimente que `haste`, lui-meme consomme uniquement par
#                  l'ordonnanceur d'auto-attaques, desactive par defaut
#                  (auto_attack_enabled=false, room.hpp:279, 2026-07-30).
#                  Confirme par le back le 2026-08-02.
DEAD_STATS = {
    "attack_speed": "auto-attaques desactivees : haste n'est plus consomme",
    # Ajoutes le 2026-08-03 apres une regression que j'ai moi-meme introduite :
    # en migrant les passifs attack_speed j'ai choisi ces deux stats comme
    # "heritier de la cadence" sans revalider. Elles sont mortes pour la meme
    # raison : room.cpp:3304 ne roule le proc QUE si skill.id == "basic_attack"
    # ("Skills — including multi-hit ones — are unaffected"), et les auto-attaques
    # sont coupees. Le champ de SORT double_hit_chance n'est meme pas parse.
    "double_attack_chance": "ne procque que sur basic_attack, et les auto-attaques sont coupees",
    "double_hit_chance": "ne procque que sur basic_attack, et les auto-attaques sont coupees",
    "triple_attack_chance": "meme chemin que double_attack_chance, mort pour les memes raisons",
}

# Stats parsees mais pas encore APPLIQUEES en prod. Tolerees (la stat est legitime,
# le portage moteur est attendu) mais listees ici pour qu'on n'oublie pas.
# Vide depuis le 2026-08-03 : cooldown_reduction a ete portee par le back (2b7f65a),
# elle est desormais appliquee au cooldown pour les 6 classes, l'equipement, les
# panoplies et les affixes. Les 3 passifs qui l'utilisent fonctionnent enfin.
PENDING_STATS = {}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect_stat_names(defs):
    """Les stats sont les CLES sous chaque categorie, pas des objets avec un `id`."""
    names = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, dict):
                    # une feuille de stat porte un name/description, pas des sous-stats
                    if "name" in value or "description" in value or "name_en" in value:
                        names.add(key)
                    walk(value)
    walk(defs.get("stats", defs))
    return names


def collect_effect_ids(status_effects):
    ids = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, dict):
                    if "impl" in value or "polarity" in value or "name_fr" in value:
                        ids.add(key)
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk({k: v for k, v in status_effects.items() if k != "_meta"})
    return ids


def extract_passives(data):
    """Tout dict portant un id commencant par p_ est un passif, a n'importe quelle profondeur."""
    out = []

    def walk(node):
        if isinstance(node, dict):
            if str(node.get("id", "")).startswith("p_"):
                out.append(node)
                return
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(data)
    return out


def main():
    os.chdir(DB)
    valid_stats = collect_stat_names(load("stats/definitions.json"))
    valid_effects = collect_effect_ids(load("stats/status_effects.json"))

    errors, warnings = [], []
    seen_ids = {}
    total = 0

    files = sorted(glob.glob("classes/**/*passives*.json", recursive=True))
    for path in files:
        data = load(path)
        for p in extract_passives(data):
            total += 1
            pid = p["id"]

            if pid in seen_ids:
                errors.append(f"{path}: id '{pid}' en DOUBLE (deja vu dans {seen_ids[pid]})")
            seen_ids[pid] = path

            is_innate = bool(p.get("trigger_rule") or p.get("conditions"))
            if not is_innate and not p.get("max_level"):
                errors.append(f"{path}: passif '{pid}' levelable SANS max_level")

            for i, e in enumerate(p.get("effects") or []):
                if not isinstance(e, dict):
                    continue
                stat = e.get("stat")
                op = e.get("op")
                if stat is not None:
                    if stat in DEAD_STATS:
                        errors.append(
                            f"{path}: passif '{pid}' effects[{i}] utilise la stat MORTE "
                            f"'{stat}' — {DEAD_STATS[stat]}"
                        )
                    elif stat in PENDING_STATS:
                        warnings.append(
                            f"{path}: passif '{pid}' utilise '{stat}' — {PENDING_STATS[stat]}"
                        )
                    elif stat not in valid_stats and stat not in valid_effects:
                        errors.append(
                            f"{path}: passif '{pid}' effects[{i}] stat inconnue '{stat}'"
                        )
                if op is not None and op not in ("add_flat", "add_percent"):
                    errors.append(f"{path}: passif '{pid}' effects[{i}] op invalide '{op}'")

            # declencheurs (innes, et bientot sous-classes)
            for name, cond in (p.get("conditions") or {}).items():
                if not isinstance(cond, dict):
                    continue
                eid = cond.get("effect_id")
                if eid and eid not in valid_effects:
                    errors.append(
                        f"{path}: passif '{pid}' condition '{name}' effect_id inconnu '{eid}'"
                    )

    print(f"{total} passifs verifies dans {len(files)} fichiers")
    print(f"  stats connues : {len(valid_stats)} | effets connus : {len(valid_effects)}")

    if warnings:
        print(f"\n--- AVERTISSEMENTS ({len(warnings)}) ---")
        for w in warnings:
            print(f"  [WARN] {w}")
    if errors:
        print(f"\n--- ERREURS ({len(errors)}) ---")
        for e in errors:
            print(f"  [ERROR] {e}")
        print(f"\nVALIDATION FAILED — {len(errors)} erreurs")
        return 1
    print(f"\nVALIDATION PASSED — 0 erreur ({len(warnings)} avertissement(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
