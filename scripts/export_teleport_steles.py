#!/usr/bin/env python3
"""Genere world/teleport_steles.json depuis les scenes de carte Godot.

POURQUOI CE SCRIPT EXISTE
-------------------------
Les pierres de teleportation (steles, a la maniere des zaaps) se POSENT dans
l'editeur Godot, comme les PNJ : la scene est la source de verite du placement.
Le serveur (presence) ne lit pas les scenes : il lit world/teleport_steles.json.
Ce script fait le pont, sur le modele de export_walkability.py.

Une stele est tout noeud de la scene d'une zone (world/zones.json map_path) qui
porte le script res://scripts/world/teleport_stele.gd : une instance de
scenes/world/props/teleport_stele.tscn, ou un decor existant auquel on a attache
ce script. Ses proprietes exportees donnent :
  - stele_id      identifiant stable (jamais renomme une fois en jeu) ;
  - name_fr/en    nom affiche dans la liste des destinations ;
  - arrival_offset  case d'arrivee, relative a la pierre (devant elle).

Le script ECHOUE (code 1, rien n'est ecrit) si une stele n'a pas d'id ou de nom,
si deux steles partagent un id, ou si sa case d'arrivee n'est pas marchable dans
world/walkability/<zone>.json (relancer export_walkability.py apres une retouche
des collisions). --check compare sans ecrire (garde : le fichier de data doit
etre a jour de la scene).

USAGE
    python -X utf8 scripts/export_teleport_steles.py <racine du projet Godot> [--check]
    git add world/teleport_steles.json
    python -X utf8 scripts/hash_content.py && git add _meta/version.json

Bibliotheque standard seulement. Idempotent : memes scenes -> meme fichier.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_walkability import Projet, apply, globals_xform, v2  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ZONES = ROOT / "world" / "zones.json"
OUT = ROOT / "world" / "teleport_steles.json"
WALK_DIR = ROOT / "world" / "walkability"
STELE_SCRIPT = "res://scripts/world/teleport_stele.gd"


def _godot_string(v: str | None) -> str:
    if v is None:
        return ""
    v = v.strip()
    if v.startswith("&"):
        v = v[1:]
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v[1:-1]
    return v


def default_arrival_offset(projet: Projet) -> tuple[float, float]:
    """Valeur par defaut de arrival_offset, lue dans le script (une seule source)."""
    src = projet.fichier(STELE_SCRIPT).read_text(encoding="utf-8")
    m = re.search(r"@export var arrival_offset\s*:\s*Vector2\s*=\s*Vector2\(([-0-9.]+),\s*([-0-9.]+)\)", src)
    if not m:
        raise SystemExit(f"ERREUR : {STELE_SCRIPT} sans '@export var arrival_offset: Vector2 = Vector2(x, y)'")
    return float(m[1]), float(m[2])


class Marchabilite:
    def __init__(self, path: Path):
        g = json.loads(path.read_text(encoding="utf-8"))
        self.x0, self.y0, self.cell = g["origin_x"], g["origin_y"], g["cell_size_px"]
        self.cols, self.rows, self.rle = g["cols"], g["rows"], g["rle"]

    def marchable(self, x: float, y: float) -> bool:
        c = math.floor((x - self.x0) / self.cell)
        r = math.floor((y - self.y0) / self.cell)
        if not (0 <= c < self.cols and 0 <= r < self.rows):
            return False
        pos, bloque = 0, True
        for t in self.rle[r].split(","):
            n = int(t, 36)
            if c < pos + n:
                return not bloque
            pos += n
            bloque = not bloque
        return False


def steles_de_la_scene(projet: Projet, zone_id: str, map_path: str, offset_defaut) -> list[dict]:
    tree = projet.arbre(map_path)
    gx = globals_xform(tree)
    out = []
    for path, n in sorted(tree.items()):
        ref = n["props"].get("script")
        if not ref:
            continue
        m = re.search(r'ExtResource\("([^"]+)"\)', ref)
        ctx = n.get("props_ctx", {}).get("script", n["ctx"])
        ext = projet.ressource(ctx)["ext"].get(m[1]) if m else None
        if not ext or ext["path"] != STELE_SCRIPT:
            continue
        x, y = apply(gx[path], (0.0, 0.0))
        dx, dy = v2(n["props"], "arrival_offset", offset_defaut)
        out.append({
            "id": _godot_string(n["props"].get("stele_id")),
            "zone_id": zone_id,
            "x": round(x),
            "y": round(y),
            "arrival_x": round(x + dx),
            "arrival_y": round(y + dy),
            "name_fr": _godot_string(n["props"].get("name_fr")),
            "name_en": _godot_string(n["props"].get("name_en")),
            "source": f"{map_path} :: {path}",
        })
    return out


def genere(racine: Path) -> tuple[dict, list[str]]:
    projet = Projet(racine)
    offset_defaut = default_arrival_offset(projet)
    zones = json.loads(ZONES.read_text(encoding="utf-8")).get("zones", [])
    erreurs: list[str] = []
    steles: list[dict] = []
    vues_scenes: set[str] = set()
    for z in zones:
        map_path = z.get("map_path", "")
        if not map_path or map_path in vues_scenes or not projet.fichier(map_path).exists():
            continue
        vues_scenes.add(map_path)  # une scene partagee (failles) ne compte qu'une fois
        trouvees = steles_de_la_scene(projet, z["id"], map_path, offset_defaut)
        if not trouvees:
            continue
        walk_path = WALK_DIR / f"{z['id']}.json"
        grille = Marchabilite(walk_path) if walk_path.exists() else None
        for s in trouvees:
            where = s["source"]
            if not s["id"]:
                erreurs.append(f"{where} : stele_id vide")
            if not s["name_fr"] or not s["name_en"]:
                erreurs.append(f"{where} : name_fr et name_en obligatoires")
            if grille is None:
                erreurs.append(f"{where} : pas de grille {walk_path.name} pour verifier la case d'arrivee")
            elif not grille.marchable(s["arrival_x"], s["arrival_y"]):
                erreurs.append(f"{where} : case d'arrivee ({s['arrival_x']},{s['arrival_y']}) non marchable "
                               f"(regler arrival_offset)")
        steles.extend(trouvees)
    ids: dict[str, str] = {}
    for s in steles:
        if s["id"] and s["id"] in ids:
            erreurs.append(f"id '{s['id']}' en double : {ids[s['id']]} et {s['source']}")
        ids.setdefault(s["id"], s["source"])
    steles.sort(key=lambda s: (s["zone_id"], s["id"]))

    doc = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    doc["_meta"] = doc.get("_meta", {})
    doc["_meta"]["generated_by"] = ("scripts/export_teleport_steles.py depuis les scenes de carte "
                                    "(noeuds portant scripts/world/teleport_stele.gd). NE PAS EDITER "
                                    "la liste steles a la main : poser la pierre dans la scene puis relancer.")
    doc.setdefault("rules", {})
    doc["steles"] = steles
    return doc, erreurs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("racine", type=Path, help="racine du projet Godot (kanarion_front)")
    ap.add_argument("--check", action="store_true", help="compare sans ecrire")
    a = ap.parse_args()
    doc, erreurs = genere(a.racine.resolve())
    if erreurs:
        for e in erreurs:
            print("ERREUR :", e, file=sys.stderr)
        return 1
    texte = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    actuel = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if a.check:
        if texte != actuel:
            print(f"ERREUR : {OUT.relative_to(ROOT)} n'est pas a jour des scenes : relancer sans --check",
                  file=sys.stderr)
            return 1
        print(f"OK : {len(doc['steles'])} stele(s), data a jour")
        return 0
    OUT.write_text(texte, encoding="utf-8", newline="\n")
    for s in doc["steles"]:
        print(f"  {s['id']:<28} {s['zone_id']:<10} ({s['x']},{s['y']}) arrivee ({s['arrival_x']},{s['arrival_y']})")
    print(f"{OUT.relative_to(ROOT)} : {len(doc['steles'])} stele(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
