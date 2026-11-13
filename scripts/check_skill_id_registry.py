#!/usr/bin/env python3
"""Garde des identifiants de sorts : aucun id ne disparait de la data sans etre declare.

Pourquoi (P0-2 du 12/11/2026) : `skill_archer_aimed_shot` et `skill_archer_quickshot`
ont ete fusionnes en `skill_archer_precise_shot` le 28/03/2026 (commit 4a2dadc) sans
migration. Huit mois plus tard, 73 + 12 personnages portaient encore l'ancien id dans
`characters.skill_allocations` (et 7 dans `hotbar_slots`) : un point de competence
bloque sur un sort qui n'existe plus, deux erreurs client a chaque connexion.

Le registre `_meta/skill_id_renames.json` porte :
  - `known_ids`  : tous les ids de sorts deja livres (definis sous classes/) ;
  - `renames`    : ancien id -> {"to": nouvel id, ...} ;
  - `removed`    : id retire sans successeur -> {"reason": ..., ...}.

Regles (--check, defaut, lance par la CI) :
  1. un id de `known_ids` absent de la data doit etre dans `renames` ou `removed` ;
  2. la cible d'un renommage doit exister dans la data ;
  3. un id de la data absent de `known_ids` est refuse : lancer --update pour
     l'enregistrer (le registre ne fait que grandir) ;
  4. un renommage ou un retrait declare doit porter une `migration` (chemin d'une
     migration SQL de kanarion_back qui remappe ou rembourse l'id dans
     skill_allocations ET hotbar_slots, ou "a ecrire" tant qu'elle n'existe pas :
     la CI le signale, elle ne le refuse pas).

Declarer un renommage : ajouter l'entree dans `renames` (ou `removed`) AVANT de
retirer l'id de la data, puis ecrire la migration cote back (inerte au rejeu :
deploy2.sh rejoue toutes les migrations, et `jsonb ||` ecrase, la droite gagne).

Usage :
    python scripts/check_skill_id_registry.py           # verifie (CI)
    python scripts/check_skill_id_registry.py --update  # enregistre les nouveaux ids
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "_meta" / "skill_id_renames.json"
SCAN_DIR = ROOT / "classes"


def current_skill_ids() -> set:
    """Tout objet {"id": "skill_..."} sous classes/ (sorts de classe, de sous-classe,
    de specialisation, communs, familier) : ce sont les ids qu'un personnage peut
    porter dans skill_allocations / hotbar_slots."""
    ids = set()

    def walk(o):
        if isinstance(o, dict):
            i = o.get("id")
            if isinstance(i, str) and i.startswith("skill_"):
                ids.add(i)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for f in sorted(SCAN_DIR.rglob("*.json")):
        with open(f, encoding="utf-8") as fh:
            walk(json.load(fh))
    return ids


def load_registry() -> dict:
    with open(REGISTRY, encoding="utf-8") as fh:
        return json.load(fh)


def check(reg: dict, ids: set) -> tuple:
    errors, warnings = [], []
    known = set(reg.get("known_ids", []))
    renames = reg.get("renames", {})
    removed = reg.get("removed", {})
    for old, entry in sorted(renames.items()):
        to = entry.get("to") if isinstance(entry, dict) else None
        if not to:
            errors.append(f"renames.{old} : champ 'to' manquant")
        elif to not in ids:
            errors.append(f"renames.{old} -> {to} : la cible n'existe pas dans classes/")
        if old in ids:
            errors.append(f"renames.{old} : l'ancien id existe encore dans la data")
        if old in removed:
            errors.append(f"{old} : a la fois renomme et retire")
    for old, entry in sorted(renames.items()) + sorted(removed.items()):
        mig = entry.get("migration") if isinstance(entry, dict) else None
        if not mig:
            errors.append(f"{old} : champ 'migration' manquant (chemin ou \"a ecrire\")")
        elif mig.strip().lower() in ("a ecrire", "à écrire", "todo"):
            warnings.append(f"{old} : migration des donnees joueur encore a ecrire")
    for old in sorted(removed):
        if old in ids:
            errors.append(f"removed.{old} : l'id existe encore dans la data")
    for gone in sorted(known - ids):
        if gone not in renames and gone not in removed:
            errors.append(
                f"{gone} a disparu de classes/ sans etre declare : ajouter une entree dans "
                f"_meta/skill_id_renames.json (renames ou removed) et la migration des donnees "
                f"joueur (skill_allocations, hotbar_slots) cote kanarion_back")
    new = sorted(ids - known)
    if new:
        errors.append(
            f"{len(new)} id(s) de sort absent(s) du registre ({', '.join(new[:5])}"
            f"{', ...' if len(new) > 5 else ''}) : lancer "
            f"python scripts/check_skill_id_registry.py --update")
    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--update", action="store_true",
                    help="ajoute les nouveaux ids au registre (n'en retire jamais)")
    args = ap.parse_args()
    reg = load_registry()
    ids = current_skill_ids()
    if args.update:
        known = set(reg.get("known_ids", []))
        added = sorted(ids - known)
        reg["known_ids"] = sorted(known | ids)
        text = json.dumps(reg, ensure_ascii=False, indent=2) + "\n"
        with open(REGISTRY, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"registre : {len(added)} id(s) ajoute(s), {len(reg['known_ids'])} au total")
    errors, warnings = check(reg, ids)
    for w in warnings:
        print(f"AVERTISSEMENT : {w}")
    if errors:
        print(f"ECHEC : {len(errors)} erreur(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK : {len(ids)} ids de sorts, aucun ne disparait sans declaration "
          f"({len(reg.get('renames', {}))} renommage(s), {len(reg.get('removed', {}))} retrait(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
