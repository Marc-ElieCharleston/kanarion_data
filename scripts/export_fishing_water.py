#!/usr/bin/env python3
"""Extrait de la carte Godot l'eau PECHABLE de chaque zone (peche en cliquant sur l'eau).

POURQUOI CE SCRIPT EXISTE
-------------------------
Decision de Charleston du 2026-11-01 (0.20.30) : toute eau visible se peche, sans
point de peche pose a la main. Il peint beaucoup de petites mares sur la carte de
Havreden ; le serveur doit pourtant verifier lui-meme qu'un joueur est au bord
d'une VRAIE eau. Ce script transcrit l'eau de la carte en donnee serveur, comme
export_walkability.py le fait pour les murs.

Une case de la grille est de l'eau quand :
  - le calque de sol le plus HAUT (gather_nodes.json water_fishing.extraction.layers,
    z_index puis ordre de la scene) qui a une tuile a cet endroit y pose une tuile
    d'un type d'eau (water_types[*].textures, reconnu par l'image d'atlas) : de
    l'eau recouverte de sol n'est pas de l'eau visible ;
  - ou elle est dans un CollisionPolygon2D d'une scene d'eau (water_types[*].scenes,
    le lac anime) posee dans la carte.
Les alternatives de tuile de skip_alternatives (eau sous un ponton) sont ignorees.

Les cases d'eau sont regroupees en PLANS D'EAU (composantes connexes, 8 voisins),
numerotes dans l'ordre de lecture de la grille. Le serveur fait de chaque plan
d'eau un point de recolte (prises partagees, epuisement, rang de l'aire mz_*).

Resultat : world/fishing_water/<zone_id>.json. Idempotent : meme carte et memes
regles -> octet pour octet le meme fichier (aucun horodatage, aucun commit).

USAGE
    python -X utf8 scripts/export_fishing_water.py <racine du projet Godot>          # ecrit
    python -X utf8 scripts/export_fishing_water.py <racine du projet Godot> --check  # 1 si perime
    python -X utf8 scripts/export_fishing_water.py <racine> --png apercu.png          # apercu
    git add world/fishing_water && python -X utf8 scripts/hash_content.py && git add _meta/version.json

--check sert de garde (kanarion_front tools/check_fishing_water_export.py) : il
echoue des que la carte et l'export divergent (eau repeinte sans relancer).

Bibliotheque standard seulement (reutilise le lecteur de scenes d'export_walkability.py).
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True  # pas de __pycache__ dans la data (lu aussi depuis le submodule)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_walkability as W  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ZONES = ROOT / "world" / "zones.json"
GATHER = ROOT / "world" / "gather_nodes.json"
OUT_DIR = ROOT / "world" / "fishing_water"

DOC = ("GENERE par scripts/export_fishing_water.py depuis la carte Godot : ne pas editer a la main, relancer le "
       "script (regles : world/gather_nodes.json water_fishing). Eau pechable de la zone, lue par presence (serveur) "
       "et par le client. Grille de cell_size_px depuis (origin_x, origin_y). rle : une chaine par ligne (y croissant), "
       "jetons separes par ',' : 'n' = n cases sans eau, 'n:b' = n cases du plan d'eau b (base 36 tous deux). "
       "Ligne vide = aucune eau ; au-dela de la fin d'une ligne, aucune eau. bodies : plans d'eau (composantes "
       "connexes a 8 voisins), id = b ; x, y = centre de la case du plan la plus proche de son barycentre ; "
       "bounds = [x_min, y_min, x_max, y_max] en px monde.")


def regles() -> dict:
    g = json.loads(GATHER.read_text(encoding="utf-8"))
    wf = g.get("water_fishing")
    if not isinstance(wf, dict) or not isinstance(wf.get("extraction"), dict):
        raise SystemExit("ERREUR : world/gather_nodes.json sans water_fishing.extraction")
    return wf


# =============================================================================
# Calques de tuiles : quelle tuile est AU-DESSUS en un point
# =============================================================================

def textures_sources(projet: W.Projet, ctx: str, ref: str) -> dict:
    """source_id de l'atlas -> chemin res:// de son image."""
    import re
    m = re.search(r'ExtResource\("([^"]+)"\)', ref)
    if m:
        path = projet.ressource(ctx)["ext"][m[1]]["path"]
        doc = projet.ressource(path)
        res = doc["resource"]
    else:
        m = re.search(r'SubResource\("([^"]+)"\)', ref)
        doc = projet.ressource(ctx)
        res = doc["sub"][m[1]]["props"]
    out = {}
    for k, v in res.items():
        km = re.match(r"sources/(\d+)$", k)
        if not km:
            continue
        sm = re.search(r'SubResource\("([^"]+)"\)', v)
        if not sm:
            continue
        src = doc["sub"].get(sm[1])
        if not src:
            continue
        tex = src["props"].get("texture", "")
        tm = re.search(r'ExtResource\("([^"]+)"\)', tex)
        if tm:
            out[int(km[1])] = doc["ext"][tm[1]]["path"]
    return out


# Repere des tuiles tel que Godot le calcule (TileMapLayer.map_to_local / local_to_map).
# En isometrique DIAMOND_DOWN, Godot place le CENTRE de la case (0, 0) en (w/2, h/2) :
# verifie dans Godot 4.5 sur havreden_terrain_v2 (64 x 30) : map_to_local((0,0)) = (32, 15),
# local_to_map((0,0)) = (-1, 0). TileSetInfo d'export_walkability.py omet ce demi-pas.

def godot_map_to_local(ts, cx: int, cy: int):
    w, h = ts.size
    if ts.shape == 1 and ts.layout == 5:
        return ((cx - cy) * w / 2.0 + w / 2.0, (cx + cy) * h / 2.0 + h / 2.0)
    return ts.map_to_local(cx, cy)


def godot_local_to_map(ts, x: float, y: float):
    w, h = ts.size
    if ts.shape == 1 and ts.layout == 5:
        u, v = (x - w / 2.0) / (w / 2.0), (y - h / 2.0) / (h / 2.0)
        return (math.floor((u + v) / 2.0 + 0.5), math.floor((v - u) / 2.0 + 0.5))
    return ts.local_to_map(x, y)


class Calque:
    def __init__(self, path, n, ts, cells, xform, order, textures):
        self.path = path
        self.z = int(W.num(n["props"], "z_index", 0))
        self.order = order
        self.ts = ts
        self.inv = W.inverse(xform)
        self.xform = xform
        self.cells = {(c[0], c[1]): c for c in cells}
        self.textures = textures

    def tuile(self, x, y):
        lx, ly = W.apply(self.inv, (x, y))
        return self.cells.get(godot_local_to_map(self.ts, lx, ly))


def type_eau(regle_types: dict) -> dict:
    """image d'atlas -> type d'eau."""
    out = {}
    for t, r in regle_types.items():
        for tex in r.get("textures", []):
            if tex in out:
                raise SystemExit(f"ERREUR : image {tex} dans deux types d'eau")
            out[tex] = t
    return out


# =============================================================================
# Extraction
# =============================================================================

def exporte_zone(projet: W.Projet, zone: dict, wf: dict):
    ext = wf["extraction"]
    cell = float(ext["cell_size_px"])
    skip = {int(a) for a in ext.get("skip_alternatives", [])}
    types = ext["water_types"]
    par_image = type_eau(types)
    par_scene = {s: t for t, r in types.items() for s in r.get("scenes", [])}
    noms = list(ext["layers"])

    tree = projet.arbre(zone["map_path"])
    gx = W.globals_xform(tree)

    calques = []
    for order, (path, n) in enumerate(tree.items()):
        if n["type"] != "TileMapLayer" or path.split("/")[-1] not in noms:
            continue
        if not W.boolean(n["props"], "enabled", True):
            continue
        ref = n["props"].get("tile_set")
        if not ref:
            continue
        ctx = n["props_ctx"].get("tile_set", n["ctx"])
        ts = W.tileset_de(projet, ctx, ref, 0)
        calques.append(Calque(path, n, ts, W.cases_calque(n["props"]), gx[path], order,
                              textures_sources(projet, ctx, ref)))
    if not calques:
        raise SystemExit(f"ERREUR : zone {zone['id']} : aucun calque parmi {noms}")
    haut_en_bas = sorted(calques, key=lambda c: (c.z, c.order), reverse=True)

    def eau_au_point(x, y):
        for c in haut_en_bas:
            t = c.tuile(x, y)
            if t is None:
                continue
            if (t[5] & 0x0FFF) in skip:
                return None
            return par_image.get(c.textures.get(t[2], ""))
        return None

    # Candidats : centres des tuiles d'eau de chaque calque, et polygones des scenes d'eau.
    rapport = {"tuiles_eau": 0, "polygones_scene": 0}
    cases: dict[tuple[int, int], str] = {}

    def case_de(x, y):
        return (int(math.floor(x / cell)), int(math.floor(y / cell)))

    for c in calques:
        hw, hh = c.ts.size[0] / 2.0, c.ts.size[1] / 2.0
        for (cx, cy), t in c.cells.items():
            if par_image.get(c.textures.get(t[2], "")) is None:
                continue
            rapport["tuiles_eau"] += 1
            ox, oy = godot_map_to_local(c.ts, cx, cy)
            coins = [W.apply(c.xform, p) for p in ((ox, oy - hh), (ox + hw, oy), (ox, oy + hh), (ox - hw, oy))]
            xs = [p[0] for p in coins]
            ys = [p[1] for p in coins]
            for gy in range(int(math.floor(min(ys) / cell)), int(math.floor(max(ys) / cell)) + 1):
                for gxx in range(int(math.floor(min(xs) / cell)), int(math.floor(max(xs) / cell)) + 1):
                    px, py = (gxx + 0.5) * cell, (gy + 0.5) * cell
                    if not W.dans(px, py, coins):
                        continue
                    t_eau = eau_au_point(px, py)
                    if t_eau is not None:
                        cases[(gxx, gy)] = t_eau

    for path, n in tree.items():
        if n["type"] != "CollisionPolygon2D" or n["ctx"] not in par_scene:
            continue
        if W.boolean(n["props"], "disabled", False):
            continue
        poly = [W.apply(gx[path], q) for q in W.pts(n["props"].get("polygon", ""))]
        if len(poly) < 3:
            continue
        rapport["polygones_scene"] += 1
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        for gy in range(int(math.floor(min(ys) / cell)), int(math.floor(max(ys) / cell)) + 1):
            for gxx in range(int(math.floor(min(xs) / cell)), int(math.floor(max(xs) / cell)) + 1):
                if W.dans((gxx + 0.5) * cell, (gy + 0.5) * cell, poly):
                    cases[(gxx, gy)] = par_scene[n["ctx"]]

    if not cases:
        return {"_doc": DOC, "zone_id": zone["id"], "map_path": zone["map_path"], "cell_size_px": cell,
                "origin_x": 0.0, "origin_y": 0.0, "cols": 0, "rows": 0, "types": sorted(types),
                "stats": {"cases_eau": 0, "plans_eau": 0}, "bodies": [], "rle": []}, rapport

    c0 = min(k[0] for k in cases)
    r0 = min(k[1] for k in cases)
    cols = max(k[0] for k in cases) - c0 + 1
    rows = max(k[1] for k in cases) - r0 + 1

    # Plans d'eau : composantes a 8 voisins, numerotees dans l'ordre de lecture.
    corps: dict[tuple[int, int], int] = {}
    plans = []
    for key in sorted(cases, key=lambda k: (k[1], k[0])):
        if key in corps:
            continue
        bid = len(plans) + 1
        pile = [key]
        corps[key] = bid
        membres = []
        while pile:
            k = pile.pop()
            membres.append(k)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    v = (k[0] + dx, k[1] + dy)
                    if v in cases and v not in corps:
                        corps[v] = bid
                        pile.append(v)
        plans.append(membres)

    bodies = []
    for i, membres in enumerate(plans, start=1):
        mx = sum(k[0] for k in membres) / len(membres)
        my = sum(k[1] for k in membres) / len(membres)
        ancre = min(membres, key=lambda k: ((k[0] - mx) ** 2 + (k[1] - my) ** 2, k[1], k[0]))
        compte = Counter(cases[k] for k in membres)
        t = sorted(compte.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        bodies.append({
            "id": i,
            "type": t,
            "cells": len(membres),
            "x": (ancre[0] + 0.5) * cell,
            "y": (ancre[1] + 0.5) * cell,
            "bounds": [min(k[0] for k in membres) * cell, min(k[1] for k in membres) * cell,
                       (max(k[0] for k in membres) + 1) * cell, (max(k[1] for k in membres) + 1) * cell],
        })

    rle = []
    for r in range(rows):
        jetons, run, cur = [], 0, 0
        for c in range(cols):
            b = corps.get((c0 + c, r0 + r), 0)
            if b == cur:
                run += 1
                continue
            if run:
                jetons.append(_jeton(run, cur))
            cur, run = b, 1
        if cur:  # une plage sans eau en fin de ligne ne s'ecrit pas
            jetons.append(_jeton(run, cur))
        rle.append(",".join(jetons))

    doc = {
        "_doc": DOC,
        "zone_id": zone["id"],
        "map_path": zone["map_path"],
        "cell_size_px": cell,
        "origin_x": c0 * cell,
        "origin_y": r0 * cell,
        "cols": cols,
        "rows": rows,
        "types": sorted(types),
        "stats": {"cases_eau": len(cases), "plans_eau": len(plans),
                  "par_type": dict(sorted(Counter(cases.values()).items()))},
        "bodies": bodies,
        "rle": rle,
    }
    return doc, rapport


def _jeton(n: int, b: int) -> str:
    return W._b36(n) if b == 0 else f"{W._b36(n)}:{W._b36(b)}"


def texte(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=1) + "\n"


def _png(doc: dict, out: Path):
    cols, rows = doc["cols"], doc["rows"]
    raw = bytearray()
    for r in range(rows):
        raw.append(0)
        c = 0
        ligne = [(30, 30, 30)] * cols
        for tok in filter(None, doc["rle"][r].split(",")):
            n, _, b = tok.partition(":")
            n = int(n, 36)
            if b:
                h = int(b, 36) * 2654435761 & 0xFFFFFF
                col = (60 + (h & 0x7F), 90 + ((h >> 8) & 0x7F), 160 + ((h >> 16) & 0x5F))
                for k in range(c, c + n):
                    ligne[k] = col
            c += n
        for px in ligne:
            raw += bytes(px)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    out.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", cols, rows, 8, 2, 0, 0, 0))
                    + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projet", help="racine du projet Godot (kanarion_front)")
    ap.add_argument("--zone", action="append", help="zone a exporter (defaut : water_fishing.zones)")
    ap.add_argument("--check", action="store_true", help="n'ecrit rien ; code 1 si un fichier differe de la carte")
    ap.add_argument("--png", help="apercu PNG (une couleur par plan d'eau)")
    a = ap.parse_args()

    wf = regles()
    zones = {z["id"]: z for z in json.loads(ZONES.read_text(encoding="utf-8"))["zones"]}
    projet = W.Projet(Path(a.projet).resolve())
    perimes = []
    for zid in a.zone or wf["zones"]:
        if zid not in zones or not zones[zid].get("map_path"):
            raise SystemExit(f"ERREUR : zone {zid} inconnue ou sans map_path")
        doc, rap = exporte_zone(projet, zones[zid], wf)
        t = texte(doc)
        out = OUT_DIR / f"{zid}.json"
        s = doc["stats"]
        print(f"[{zid}] {s['cases_eau']} cases d'eau en {s['plans_eau']} plan(s) d'eau "
              f"({doc['cols']}x{doc['rows']} cases de {doc['cell_size_px']:g} px) ; "
              f"tuiles d'eau {rap['tuiles_eau']}, polygones de scene {rap['polygones_scene']} ; "
              f"{len(t.encode('utf-8')) / 1024:.0f} Ko")
        if s.get("par_type"):
            print("  " + ", ".join(f"{k} {v}" for k, v in s["par_type"].items()))
        if a.png:
            _png(doc, Path(a.png))
        if a.check:
            if not out.is_file() or out.read_text(encoding="utf-8") != t:
                perimes.append(str(out.relative_to(ROOT)))
            continue
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out.write_text(t, encoding="utf-8", newline="\n")
        print(f"  ecrit {out.relative_to(ROOT)}")
    if a.check:
        if perimes:
            print("EAU PECHABLE PERIMEE : la carte a change depuis l'export. Relancer :")
            print("  python -X utf8 scripts/export_fishing_water.py <racine kanarion_front>")
            for p in perimes:
                print("  " + p)
            return 1
        print("Eau pechable : l'export correspond a la carte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
