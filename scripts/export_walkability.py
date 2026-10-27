#!/usr/bin/env python3
"""Extrait de la carte Godot une grille de marchabilite pour les monstres du monde.

POURQUOI CE SCRIPT EXISTE
-------------------------
Le serveur (presence) tire la position de chaque groupe de monstres, puis le
client fait errer le monstre autour de ce point sans aucune collision. Le serveur
ne connaissait que des polygones (area_limit, villes) : il posait des monstres
dans l'eau, et le client les faisait marcher a travers l'eau et les murs.

Ce script transcrit les murs du JOUEUR en donnee serveur :
  - les corps statiques (StaticBody2D) dont le collision_layer croise le
    collision_mask du joueur, avec leurs CollisionPolygon2D / CollisionShape2D,
    y compris dans les scenes instanciees ;
  - les tuiles a collision des TileMapLayer (l'eau de havreden_terrain_v2) ;
  - le vide : un point sans tuile sur les calques de sol ;
  - tout ce qui est hors du polygone area_limit de world/zones.json.

Resultat : world/walkability/<zone_id>.json, une grille de cases de
cell_size_px (config/monster_walkability.json), encodee par plages (RLE) ligne
par ligne. Presence la lit au demarrage. La carte reste l'outil de DESSIN : apres
toute retouche des collisions, relancer ce script.

USAGE
    python -X utf8 scripts/export_walkability.py <racine du projet Godot> [--zone village] [--dry-run] [--png out.png]
    git add world/walkability config/monster_walkability.json
    python -X utf8 scripts/hash_content.py && git add _meta/version.json

Bibliotheque standard seulement. Idempotent : meme carte -> meme fichier.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import re
import struct
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONES = ROOT / "world" / "zones.json"
CONFIG = ROOT / "config" / "monster_walkability.json"
OUT_DIR = ROOT / "world" / "walkability"

# =============================================================================
# Lecture des fichiers texte Godot (.tscn / .tres)
# =============================================================================

_SECTION = re.compile(r"^\[(\w+)(.*)\]\s*$")
_ATTR = re.compile(r'(\w+)=("([^"]*)"|[^\s\]]+)')
_PROP = re.compile(r"^([A-Za-z0-9_/:.]+) = (.*)$")


def _attrs(s: str) -> dict:
    out = {}
    for m in _ATTR.finditer(s):
        out[m[1]] = m[3] if m[3] is not None else m[2]
    return out


def lire_ressource(path: Path) -> dict:
    """Sections d'un .tscn/.tres : ext (id -> path), sub (id -> {type, props}),
    nodes [{name, type, parent, instance, props}], resource (props)."""
    ext, sub, nodes, resource = {}, {}, [], {}
    cur = None
    pending_key, pending_val = None, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if pending_key is not None:
            pending_val += "\n" + raw
            if _balanced(pending_val):
                cur[pending_key] = pending_val
                pending_key = None
            continue
        m = _SECTION.match(raw)
        if m:
            kind, a = m[1], _attrs(m[2])
            if kind == "ext_resource":
                ext[a["id"]] = {"path": a.get("path", ""), "type": a.get("type", "")}
                cur = None
            elif kind == "sub_resource":
                sub[a["id"]] = {"type": a.get("type", ""), "props": {}}
                cur = sub[a["id"]]["props"]
            elif kind == "node":
                inst = None
                if "instance" in a:
                    im = re.search(r'ExtResource\("([^"]+)"\)', m[2])
                    inst = im[1] if im else None
                node = {"name": a.get("name", ""), "type": a.get("type"), "parent": a.get("parent"),
                        "instance": inst, "props": {}}
                nodes.append(node)
                cur = node["props"]
            elif kind == "resource":
                cur = resource
            else:
                cur = None
            continue
        if cur is None:
            continue
        pm = _PROP.match(raw)
        if pm:
            if _balanced(pm[2]):
                cur[pm[1]] = pm[2]
            else:
                pending_key, pending_val = pm[1], pm[2]
    return {"ext": ext, "sub": sub, "nodes": nodes, "resource": resource}


def _balanced(v: str) -> bool:
    return v.count("(") == v.count(")") and v.count("[") == v.count("]") and v.count("{") == v.count("}")


def _floats(s: str) -> list[float]:
    if "(" in s:  # Vector2(0, 6) : ne pas lire le 2 du nom du type
        s = s.split("(", 1)[1]
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", s)]


def v2(props: dict, key: str, default=(0.0, 0.0)):
    if key not in props:
        return default
    f = _floats(props[key])
    return (f[0], f[1])


def num(props: dict, key: str, default: float) -> float:
    if key not in props:
        return default
    return float(props[key])


def boolean(props: dict, key: str, default: bool) -> bool:
    if key not in props:
        return default
    return props[key].strip() == "true"


def pts(s: str) -> list[tuple[float, float]]:
    f = _floats(s)
    return list(zip(f[0::2], f[1::2]))


# =============================================================================
# Transformations 2D (a, b, c, d, tx, ty) : x' = a x + c y + tx ; y' = b x + d y + ty
# =============================================================================

IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def local_xform(props: dict):
    px, py = v2(props, "position")
    r = num(props, "rotation", 0.0)
    sx, sy = v2(props, "scale", (1.0, 1.0))
    sk = num(props, "skew", 0.0)
    return (math.cos(r) * sx, math.sin(r) * sx,
            -math.sin(r + sk) * sy, math.cos(r + sk) * sy, px, py)


def compose(p, l):
    a, b, c, d, tx, ty = p
    a2, b2, c2, d2, tx2, ty2 = l
    return (a * a2 + c * b2, b * a2 + d * b2,
            a * c2 + c * d2, b * c2 + d * d2,
            a * tx2 + c * ty2 + tx, b * tx2 + d * ty2 + ty)


def apply(t, p):
    a, b, c, d, tx, ty = t
    return (a * p[0] + c * p[1] + tx, b * p[0] + d * p[1] + ty)


def inverse(t):
    a, b, c, d, tx, ty = t
    det = a * d - b * c
    ia, ib, ic, id_ = d / det, -b / det, -c / det, a / det
    return (ia, ib, ic, id_, -(ia * tx + ic * ty), -(ib * tx + id_ * ty))


# =============================================================================
# Arbre de scene aplati (instances comprises)
# =============================================================================

class Projet:
    def __init__(self, racine: Path):
        self.racine = racine
        self._cache: dict[str, dict] = {}

    def fichier(self, res_path: str) -> Path:
        if not res_path.startswith("res://"):
            raise SystemExit(f"ERREUR : chemin non res:// : {res_path}")
        return self.racine / res_path[len("res://"):]

    def ressource(self, res_path: str) -> dict:
        if res_path not in self._cache:
            self._cache[res_path] = lire_ressource(self.fichier(res_path))
        return self._cache[res_path]

    def arbre(self, res_path: str) -> dict:
        """chemin relatif -> {type, props, ctx(res_path du fichier qui a defini les sous-ressources)}.
        Racine = '.'. Les instances sont depliees, les surcharges fusionnees."""
        doc = self.ressource(res_path)
        out: dict[str, dict] = {}
        for n in doc["nodes"]:
            par = n["parent"]
            if par is None:
                path = "."
            elif par == ".":
                path = n["name"]
            else:
                path = par + "/" + n["name"]
            if n["instance"]:
                sub_path = doc["ext"][n["instance"]]["path"]
                sub = self.arbre(sub_path)
                for sp, sn in sub.items():
                    full = path if sp == "." else path + "/" + sp
                    out[full] = {"type": sn["type"], "props": dict(sn["props"]), "ctx": sn["ctx"],
                                 "props_ctx": dict(sn.get("props_ctx", {}))}
                node = out[path]
                for k, v in n["props"].items():
                    node["props"][k] = v
                    node["props_ctx"][k] = res_path
            elif path in out and n["type"] is None:
                for k, v in n["props"].items():
                    out[path]["props"][k] = v
                    out[path]["props_ctx"][k] = res_path
            else:
                out[path] = {"type": n["type"], "props": dict(n["props"]), "ctx": res_path,
                             "props_ctx": {k: res_path for k in n["props"]}}
        return out


def parent_of(path: str) -> str | None:
    if path == ".":
        return None
    return path.rsplit("/", 1)[0] if "/" in path else "."


NON_2D = {"Node", "CanvasLayer", "Timer", "AudioStreamPlayer", "AnimationPlayer"}


def globals_xform(tree: dict) -> dict:
    cache: dict[str, tuple] = {}

    def g(path: str):
        if path in cache:
            return cache[path]
        n = tree[path]
        par = parent_of(path)
        base = IDENT if par is None or boolean(n["props"], "top_level", False) else g(par)
        t = base if n["type"] in NON_2D else compose(base, local_xform(n["props"]))
        cache[path] = t
        return t

    return {p: g(p) for p in tree}


# =============================================================================
# Formes bloquantes
# =============================================================================

def resoudre_sub(projet: Projet, ctx: str, ref: str):
    m = re.search(r'SubResource\("([^"]+)"\)', ref)
    if m:
        return projet.ressource(ctx)["sub"].get(m[1])
    m = re.search(r'ExtResource\("([^"]+)"\)', ref)
    if m:
        e = projet.ressource(ctx)["ext"][m[1]]
        doc = projet.ressource(e["path"])
        return {"type": e["type"], "props": doc["resource"], "doc_path": e["path"]}
    return None


def forme_polygones(shape: dict):
    """Polygones pleins et segments (en local) d'une Shape2D."""
    t, p = shape["type"], shape["props"]
    if t == "RectangleShape2D":
        w, h = v2(p, "size", (20.0, 20.0))
        return [[(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]], []
    if t == "CircleShape2D":
        r = num(p, "radius", 10.0)
        return [[(r * math.cos(i * math.pi / 12), r * math.sin(i * math.pi / 12)) for i in range(24)]], []
    if t == "CapsuleShape2D":
        r = num(p, "radius", 10.0)
        h = max(num(p, "height", 30.0), 2 * r)
        half = h / 2 - r
        poly = [(r * math.cos(i * math.pi / 12), -half + r * math.sin(i * math.pi / 12)) for i in range(12, 25)]
        poly += [(r * math.cos(i * math.pi / 12), half + r * math.sin(i * math.pi / 12)) for i in range(0, 13)]
        return [poly], []
    if t == "ConvexPolygonShape2D":
        return [pts(p.get("points", ""))], []
    if t == "ConcavePolygonShape2D":
        s = pts(p.get("segments", ""))
        return [], [(s[i], s[i + 1]) for i in range(0, len(s) - 1, 2)]
    if t == "SegmentShape2D":
        return [], [(v2(p, "a"), v2(p, "b", (0.0, 10.0)))]
    return None, None


BODY_TYPES = {"StaticBody2D", "AnimatableBody2D"}


def obstacles_corps(projet: Projet, tree: dict, gx: dict, mask: int, rapport: dict):
    polys, segs = [], []
    for path, n in tree.items():
        if n["type"] not in BODY_TYPES:
            continue
        layer = int(num(n["props"], "collision_layer", 1))
        if not layer & mask:
            continue
        if _desactive(tree, path):
            continue
        rapport["corps"] += 1
        for cp, cn in tree.items():
            if parent_of(cp) != path:
                continue
            if boolean(cn["props"], "disabled", False):
                continue
            t = gx[cp]
            if cn["type"] == "CollisionPolygon2D":
                poly = pts(cn["props"].get("polygon", ""))
                if len(poly) < 2:
                    continue
                w = [apply(t, q) for q in poly]
                if int(num(cn["props"], "build_mode", 0)) == 1:
                    segs += [(w[i], w[(i + 1) % len(w)]) for i in range(len(w))]
                    rapport["polygones_contour"] += 1
                else:
                    polys.append(w)
                    rapport["polygones"] += 1
            elif cn["type"] == "CollisionShape2D":
                ref = cn["props"].get("shape")
                if not ref:
                    continue
                ctx = cn["props_ctx"].get("shape", cn["ctx"])
                shape = resoudre_sub(projet, ctx, ref)
                if shape is None:
                    rapport["avertissements"].append(f"forme introuvable : {cp}")
                    continue
                pp, ss = forme_polygones(shape)
                if pp is None:
                    rapport["avertissements"].append(f"forme non geree {shape['type']} : {cp}")
                    continue
                polys += [[apply(t, q) for q in p] for p in pp]
                segs += [(apply(t, a), apply(t, b)) for a, b in ss]
                rapport["formes"] += 1
    return polys, segs


def _desactive(tree: dict, path: str) -> bool:
    p = path
    while p is not None:
        mode = tree[p]["props"].get("process_mode")
        if mode is not None:
            return mode.strip() == "4"
        p = parent_of(p)
    return False


# =============================================================================
# TileMapLayer : decodage, physique des tuiles, sol
# =============================================================================

FLIP_H, FLIP_V, TRANSPOSE = 1 << 12, 1 << 13, 1 << 14


def cases_calque(props: dict) -> list[tuple[int, int, int, int, int, int]]:
    raw = props.get("tile_map_data")
    if not raw:
        return []
    m = re.search(r'PackedByteArray\("([^"]*)"\)', raw)
    if m:
        b = base64.b64decode(m[1])
    else:
        b = bytes(int(x) for x in re.findall(r"\d+", raw.split("(", 1)[1]))
    out = []
    for i in range((len(b) - 2) // 12):
        out.append(struct.unpack_from("<hhHHHH", b, 2 + i * 12))
    return out


class TileSetInfo:
    def __init__(self, projet: Projet, doc_path: str, res: dict, sub_doc: dict, mask: int):
        p = res["props"] if "props" in res else res
        self.shape = int(num(p, "tile_shape", 0))
        self.layout = int(num(p, "tile_layout", 0))
        self.size = v2(p, "tile_size", (16.0, 16.0))
        layers = {}
        for k, v in p.items():
            m = re.match(r"physics_layer_(\d+)/collision_layer$", k)
            if m:
                layers[int(m[1])] = int(v)
        self.layer_bits = layers
        self.physique: dict[tuple, list] = {}
        for k, v in p.items():
            m = re.match(r"sources/(\d+)$", k)
            if not m:
                continue
            src_id = int(m[1])
            sm = re.search(r'SubResource\("([^"]+)"\)', v)
            if not sm:
                continue
            src = sub_doc["sub"][sm[1]]
            for tk, tv in src["props"].items():
                tm = re.match(r"(\d+):(\d+)/(\d+)/physics_layer_(\d+)/polygon_(\d+)/points$", tk)
                if not tm:
                    continue
                ax, ay, alt, pl = int(tm[1]), int(tm[2]), int(tm[3]), int(tm[4])
                if not self.layer_bits.get(pl, 1 if pl == 0 else 0) & mask:
                    continue
                self.physique.setdefault((src_id, ax, ay, alt), []).append(pts(tv))

    def map_to_local(self, cx: int, cy: int):
        w, h = self.size
        if self.shape == 1 and self.layout == 5:  # isometrique, DIAMOND_DOWN
            return ((cx - cy) * w / 2.0, (cx + cy) * h / 2.0)
        if self.shape == 0:  # carre
            return (cx * w + w / 2.0, cy * h + h / 2.0)
        raise SystemExit(f"ERREUR : tile_shape={self.shape} layout={self.layout} non gere")

    def local_to_map(self, x: float, y: float):
        w, h = self.size
        if self.shape == 1 and self.layout == 5:
            u, v = x / (w / 2.0), y / (h / 2.0)
            fx, fy = (u + v) / 2.0, (v - u) / 2.0
            return (math.floor(fx + 0.5), math.floor(fy + 0.5))
        if self.shape == 0:
            return (math.floor(x / w), math.floor(y / h))
        raise SystemExit("ERREUR : forme de tuile non geree")


def tileset_de(projet: Projet, ctx: str, ref: str, mask: int) -> TileSetInfo:
    m = re.search(r'ExtResource\("([^"]+)"\)', ref)
    if m:
        path = projet.ressource(ctx)["ext"][m[1]]["path"]
        doc = projet.ressource(path)
        return TileSetInfo(projet, path, doc["resource"], doc, mask)
    m = re.search(r'SubResource\("([^"]+)"\)', ref)
    doc = projet.ressource(ctx)
    return TileSetInfo(projet, ctx, doc["sub"][m[1]], doc, mask)


def _transforme_tuile(poly, alt):
    out = []
    for x, y in poly:
        if alt & TRANSPOSE:
            x, y = y, x
        if alt & FLIP_H:
            x = -x
        if alt & FLIP_V:
            y = -y
        out.append((x, y))
    return out


# =============================================================================
# Rasterisation
# =============================================================================

class Grille:
    def __init__(self, x0, y0, cell, cols, rows):
        self.x0, self.y0, self.cell, self.cols, self.rows = x0, y0, cell, cols, rows
        self.bloque = bytearray(cols * rows)  # 0 = marchable, sinon code raison
        self.raisons = {}

    def centre(self, c, r):
        return (self.x0 + (c + 0.5) * self.cell, self.y0 + (r + 0.5) * self.cell)

    def marque(self, c, r, code):
        if 0 <= c < self.cols and 0 <= r < self.rows:
            i = r * self.cols + c
            if not self.bloque[i]:
                self.bloque[i] = code

    def polygone(self, poly, code):
        """Cases dont le centre est dans le polygone (scanline, pair-impair) + cases
        traversees par le contour (une cloture fine bloque quand meme)."""
        ys = [p[1] for p in poly]
        r0 = max(0, int(math.floor((min(ys) - self.y0) / self.cell)))
        r1 = min(self.rows - 1, int(math.floor((max(ys) - self.y0) / self.cell)))
        n = len(poly)
        for r in range(r0, r1 + 1):
            yc = self.y0 + (r + 0.5) * self.cell
            xs = []
            for i in range(n):
                (xa, ya), (xb, yb) = poly[i], poly[(i + 1) % n]
                if (ya <= yc) != (yb <= yc):
                    xs.append(xa + (yc - ya) * (xb - xa) / (yb - ya))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                c0 = int(math.ceil((xs[k] - self.x0) / self.cell - 0.5))
                c1 = int(math.floor((xs[k + 1] - self.x0) / self.cell - 0.5))
                for c in range(max(c0, 0), min(c1, self.cols - 1) + 1):
                    self.marque(c, r, code)
        for i in range(n):
            self.segment(poly[i], poly[(i + 1) % n], code)

    def segment(self, a, b, code):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        steps = max(1, int(math.ceil(d / (self.cell / 4.0))))
        for s in range(steps + 1):
            x = a[0] + (b[0] - a[0]) * s / steps
            y = a[1] + (b[1] - a[1]) * s / steps
            self.marque(int(math.floor((x - self.x0) / self.cell)),
                        int(math.floor((y - self.y0) / self.cell)), code)


def dans(px, py, P):
    inside = False
    j = len(P) - 1
    for i in range(len(P)):
        xi, yi = P[i]
        xj, yj = P[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


CODE_OBSTACLE, CODE_TUILE, CODE_VIDE, CODE_HORS = 1, 2, 3, 4
NOMS_CODES = {CODE_OBSTACLE: "obstacle", CODE_TUILE: "tuile_collision", CODE_VIDE: "vide", CODE_HORS: "hors_area_limit"}


def encode_rle(g: Grille) -> list[str]:
    """Une chaine par ligne : longueurs de plages en base 36 separees par ',',
    alternees en commencant par une plage BLOQUEE (eventuellement 0)."""
    out = []
    for r in range(g.rows):
        row = g.bloque[r * g.cols:(r + 1) * g.cols]
        runs, cur, n = [], True, 0
        for v in row:
            b = v != 0
            if b == cur:
                n += 1
            else:
                runs.append(n)
                cur, n = b, 1
        runs.append(n)
        out.append(",".join(_b36(x) for x in runs))
    return out


def _b36(n: int) -> str:
    s = "0123456789abcdefghijklmnopqrstuvwxyz"
    if n == 0:
        return "0"
    o = ""
    while n:
        n, k = divmod(n, 36)
        o = s[k] + o
    return o


# =============================================================================
# Principal
# =============================================================================

def exporte_zone(projet: Projet, zone: dict, cfg: dict, png: Path | None):
    ext = cfg["extraction"]
    cell = float(ext["cell_size_px"])
    map_path = zone["map_path"]
    rapport = {"corps": 0, "polygones": 0, "polygones_contour": 0, "formes": 0,
               "tuiles_collision": 0, "avertissements": []}

    player = projet.arbre(ext["player_scene"])["."]
    mask = int(num(player["props"], "collision_mask", 1))

    tree = projet.arbre(map_path)
    gx = globals_xform(tree)

    # Calques de tuiles
    calques = []
    for path, n in tree.items():
        if n["type"] != "TileMapLayer" or not boolean(n["props"], "enabled", True):
            continue
        ref = n["props"].get("tile_set")
        if not ref:
            continue
        ts = tileset_de(projet, n["props_ctx"].get("tile_set", n["ctx"]), ref, mask)
        calques.append((path, n, ts, cases_calque(n["props"])))

    area = [tuple(p) for p in zone.get("area_limit") or []]
    if len(area) < 3:
        raise SystemExit(f"ERREUR : zone {zone['id']} sans area_limit")

    # Etendue : area_limit rognee sur l'etendue du sol peint (le reste est vide de toute facon).
    sol_names = set(ext["ground_layers"])
    xs, ys = [], []
    for path, n, ts, cs in calques:
        if path.split("/")[-1] not in sol_names or not cs:
            continue
        t = gx[path]
        for cx, cy, *_ in cs:
            x, y = apply(t, ts.map_to_local(cx, cy))
            xs.append(x)
            ys.append(y)
        pad = max(ts.size)
        xs += [min(xs) - pad, max(xs) + pad]
        ys += [min(ys) - pad, max(ys) + pad]
    ax = [p[0] for p in area]
    ay = [p[1] for p in area]
    x_min, x_max = max(min(ax), min(xs)), min(max(ax), max(xs))
    y_min, y_max = max(min(ay), min(ys)), min(max(ay), max(ys))
    x0 = math.floor(x_min / cell) * cell
    y0 = math.floor(y_min / cell) * cell
    cols = int(math.ceil((x_max - x0) / cell))
    rows = int(math.ceil((y_max - y0) / cell))
    g = Grille(x0, y0, cell, cols, rows)

    # 1. obstacles des corps statiques
    polys, segs = obstacles_corps(projet, tree, gx, mask, rapport)
    for p in polys:
        g.polygone(p, CODE_OBSTACLE)
    for a, b in segs:
        g.segment(a, b, CODE_OBSTACLE)

    # 2. tuiles a collision
    for path, n, ts, cs in calques:
        if not boolean(n["props"], "collision_enabled", True) or not ts.physique:
            continue
        t = gx[path]
        for cx, cy, src, axx, ayy, alt in cs:
            key = (src, axx, ayy, alt & 0x0FFF)
            polys_t = ts.physique.get(key)
            if not polys_t:
                continue
            ox, oy = ts.map_to_local(cx, cy)
            for poly in polys_t:
                w = [apply(t, (ox + x, oy + y)) for x, y in _transforme_tuile(poly, alt)]
                g.polygone(w, CODE_TUILE)
            rapport["tuiles_collision"] += 1

    # 3. vide (aucune tuile de sol) et 4. hors area_limit
    sols = []
    for path, n, ts, cs in calques:
        if path.split("/")[-1] in sol_names:
            sols.append((inverse(gx[path]), ts, {(c[0], c[1]) for c in cs}))
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            if g.bloque[i]:
                continue
            x, y = g.centre(c, r)
            if not dans(x, y, area):
                g.bloque[i] = CODE_HORS
                continue
            peint = False
            for inv, ts, cells in sols:
                lx, ly = apply(inv, (x, y))
                if ts.local_to_map(lx, ly) in cells:
                    peint = True
                    break
            if not peint:
                g.bloque[i] = CODE_VIDE

    compte = {nom: 0 for nom in NOMS_CODES.values()}
    marchable = 0
    for v in g.bloque:
        if v:
            compte[NOMS_CODES[v]] += 1
        else:
            marchable += 1

    doc = {
        "_doc": "GENERE par scripts/export_walkability.py depuis la carte Godot : ne pas editer a la main, relancer le script. "
                "Grille de marchabilite des monstres du monde (lue par presence). rle : une chaine par ligne (y croissant), "
                "longueurs de plages en base 36 separees par ',', alternees bloque/marchable en commencant par une plage BLOQUEE. "
                "Hors de la grille = non marchable.",
        "zone_id": zone["id"],
        "map_path": map_path,
        "cell_size_px": cell,
        "origin_x": x0,
        "origin_y": y0,
        "cols": cols,
        "rows": rows,
        "source": {"client_commit": _commit(projet.racine)},
        "stats": {"marchable": marchable, **compte},
        "rle": encode_rle(g),
    }
    if png:
        _png(g, png)
    return doc, rapport


def _commit(racine: Path) -> str:
    try:
        r = subprocess.run(["git", "-C", str(racine), "log", "-1", "--format=%h"],
                           capture_output=True, text=True, check=True)
        sha = r.stdout.strip()
        d = subprocess.run(["git", "-C", str(racine), "status", "--porcelain", "--", "scenes", "assets"],
                           capture_output=True, text=True).stdout.strip()
        return sha + ("+modifs-locales" if d else "")
    except Exception:
        return "inconnu"


def _png(g: Grille, out: Path):
    couleurs = {0: (120, 190, 90), CODE_OBSTACLE: (200, 60, 50), CODE_TUILE: (40, 90, 200),
                CODE_VIDE: (25, 25, 25), CODE_HORS: (70, 70, 70)}
    raw = bytearray()
    for r in range(g.rows):
        raw.append(0)
        for c in range(g.cols):
            raw += bytes(couleurs[g.bloque[r * g.cols + c]])

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", g.cols, g.rows, 8, 2, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    out.write_bytes(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projet", help="racine du projet Godot (kanarion_front)")
    ap.add_argument("--zone", action="append", help="zone a exporter (defaut : extraction.zones de la config)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--png", help="ecrit un apercu PNG (vert marchable, bleu tuile, rouge obstacle, noir vide)")
    a = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    zones = {z["id"]: z for z in json.loads(ZONES.read_text(encoding="utf-8"))["zones"]}
    projet = Projet(Path(a.projet).resolve())
    for zid in a.zone or cfg["extraction"]["zones"]:
        if zid not in zones or not zones[zid].get("map_path"):
            raise SystemExit(f"ERREUR : zone {zid} inconnue ou sans map_path")
        doc, rap = exporte_zone(projet, zones[zid], cfg, Path(a.png) if a.png else None)
        texte = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
        s = doc["stats"]
        total = doc["cols"] * doc["rows"]
        print(f"[{zid}] {doc['cols']}x{doc['rows']} cases de {doc['cell_size_px']:g} px, "
              f"origine ({doc['origin_x']:g},{doc['origin_y']:g}), carte {doc['source']['client_commit']}")
        print(f"  marchable {100 * s['marchable'] / total:.1f} %  " + "  ".join(
            f"{k} {100 * v / total:.1f} %" for k, v in s.items() if k != "marchable"))
        print(f"  corps {rap['corps']}, polygones {rap['polygones']} (+{rap['polygones_contour']} contours), "
              f"formes {rap['formes']}, tuiles a collision {rap['tuiles_collision']}")
        for w in rap["avertissements"]:
            print("  AVERTISSEMENT :", w)
        print(f"  fichier : {len(texte.encode('utf-8')) / 1024:.0f} Ko")
        if not a.dry_run:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            out = OUT_DIR / f"{zid}.json"
            out.write_text(texte, encoding="utf-8", newline="\n")
            print(f"  ecrit {out.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
