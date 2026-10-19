#!/usr/bin/env python3
"""Exporte les aires de monstres d'Havreden de la carte (havreden_map.tscn) vers
world/zones.json, zone `village`.

POURQUOI CE SCRIPT EXISTE
-------------------------
La carte est l'outil de DESSIN : Charleston trace les aires (`map_areas/mz_*`),
la limite jouable (`Ground/Area_limit`) et les villes (`*_area`) dans Godot.
La DONNEE que lisent le serveur (presence : spawn, coffres, Fissures, failles,
recolte, aggro) et le client (libelle de la mini-carte, bornes) est zones.json.
Recopier a la main faisait deriver les deux (rectangles englobants, villes
oubliees, monstres poses dans le vide). Ce script fait la transcription, de
facon repetable.

CE QU'IL ECRIT (zone `village` seulement, le reste du fichier n'est pas reecrit)
  area_limit     <- Ground/Area_limit (position/scale appliquees)
  safe_polygons  <- chaque Polygon2D `*_area` hors map_areas (villes) ; l'ancien
                    `safe_polygon` du village est garde tel quel
  spawn_areas    <- chaque `map_areas/mz_<nom>_<min>_<max>[_elite]` :
                    id, name_fr/name_en (carnet _meta/carnet/noms_zones.md),
                    level_range (tranche du nom), polygon (rogne sur area_limit),
                    bounds (boite englobante du polygone), count (regle de densite)

CE QU'IL NE TOUCHE JAMAIS
  mobs, elite_pool, boss, max_stars, elite_pack_chance et toute autre cle d'un id
  qui existe deja. Un id renomme reprend le roster de son ancien id (table
  REPRISE). Une aire sans roster est ecrite avec `mobs: []` et `count: 0`.

SOL PAS ENCORE PEINT
  Le calque `Ground` est decode a chaque execution : une aire dont plus de
  --empty-ground (20 %) de la surface tombe sur des cases vides est ecrite avec
  `count: 0` (dormante : le serveur n'y pose ni monstre, ni coffre, ni Fissure,
  ni faille, ni point de recolte). Le roster n'est pas touche : quand le sol est
  peint, relancer le script suffit pour qu'elle redevienne spawnable.
  Les cases d'eau (calque `Water`) sont mesurees et signalees, mais le serveur ne
  connait que des polygones : il ne peut pas les eviter au tirage.

USAGE
    python -X utf8 scripts/export_havreden_areas.py <havreden_map.tscn> --dry-run
    python -X utf8 scripts/export_havreden_areas.py <havreden_map.tscn>
    git add world/zones.json && python -X utf8 scripts/hash_content.py && git add _meta/version.json

Idempotent : une seconde execution sur la meme carte ne change rien.
"""
from __future__ import annotations

import argparse
import base64
import copy
import difflib
import json
import math
import re
import struct
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONES = ROOT / "world" / "zones.json"
CARNET = ROOT / "_meta" / "carnet" / "noms_zones.md"
ZONE_ID = "village"

# Renommages de la carte v7 : nouvel id <- ancien id dont on reprend le roster
# (mobs, elite_pool, boss, max_stars...). Decide par Charleston le 2026-10-19.
REPRISE = {
    "mz_abords_d_havreden_1_8": "mz_rats_1_8",
    "mz_lisiere_d_havreden_3_8": "mz_scarabees_3_8",
    "mz_fourres_des_sangliers_8_15": "mz_sanglier_8_15",
    "mz_bocage_9_20": "mz_hyene_9_20",
    "mz_bois_des_loups_13_32": "mz_loup_13_23",
    "mz_foret_nord_12_26": "mz_foret_12_26",
    "mz_combe_aux_ours_20_28": "mz_ours_20_28",
    "mz_route_de_rochebourg_40_50": "mz_brigand_35-45",
    "mz_abords_de_rochebourg_45_50": "mz_rats_corrompu_40-50",
    "mz_chemin_des_pelerins_45_60": "mz_fanatique_45_60_elite",
    "mz_mines_basses_50_60": "mz_gobelins_50_60",
    "mz_to_do_16-25_elite": "mz_taureaux_16-25_elite",
}

# Aires dessinees mais pas encore a exporter (Charleston les remplira).
NON_EXPORTEES = {"mz_to_do_6_15"}

# Bois des Loups (13-32, entree au nord) : pas de degrade continu, trois sous-aires
# du nord au sud, chacune une spawn_area a part entiere. Rosters ecrits a la
# PREMIERE creation seulement ; ensuite la data fait foi (jamais reecrits).
DECOUPES = {
    "mz_bois_des_loups_13_32": [
        {"suffix": "a", "level_range": [13, 19], "max_stars": 3,
         "mobs": [{"id": "mob_wolf", "weight": 3}, {"id": "mob_frothing_wolf", "weight": 2}]},
        {"suffix": "b", "level_range": [20, 26], "max_stars": 3,
         "mobs": [{"id": "mob_loup_noir", "weight": 3}, {"id": "mob_wolf_packleader", "weight": 1}]},
        {"suffix": "c", "level_range": [27, 32], "max_stars": 4,
         "mobs": [{"id": "mob_loup_blanc", "weight": 3}, {"id": "mob_vieux_loup", "weight": 2}]},
    ],
}

NOM_AIRE = re.compile(r"^mz_(?P<slug>.+?)_(?P<min>\d+)[_-](?P<max>\d+)(?P<elite>_elite)?$")
CLES_GEOMETRIE = ("id", "name_fr", "name_en", "level_range", "count", "bounds", "polygon")


# =============================================================================
# Lecture de la scene
# =============================================================================

def lire_scene(path: Path):
    """Noeuds de la scene : chemin -> {name, type, parent, pos, scale, rot, poly, tiles}."""
    nodes, order, cur = {}, [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r'\[node name="([^"]+)" type="([^"]+)"(?: parent="([^"]*)")?', line)
        if m:
            name, typ, par = m.groups()
            if par is None:
                p = "."
            elif par == ".":
                p = name
            else:
                p = par + "/" + name
            cur = {"name": name, "type": typ, "parent": par, "path": p, "pos": (0.0, 0.0),
                   "scale": (1.0, 1.0), "rot": 0.0, "poly": None, "tiles": None}
            nodes[p] = cur
            order.append(p)
            continue
        if line.startswith("["):
            cur = None
            continue
        if cur is None:
            continue
        if m := re.match(r"position = Vector2\(([-\d.e]+), ([-\d.e]+)\)", line):
            cur["pos"] = (float(m[1]), float(m[2]))
        elif m := re.match(r"scale = Vector2\(([-\d.e]+), ([-\d.e]+)\)", line):
            cur["scale"] = (float(m[1]), float(m[2]))
        elif m := re.match(r"rotation = ([-\d.e]+)", line):
            cur["rot"] = float(m[1])
        elif m := re.match(r"polygon = PackedVector2Array\((.*)\)", line):
            v = [float(x) for x in m[1].split(",") if x.strip()]
            cur["poly"] = list(zip(v[0::2], v[1::2]))
        elif m := re.match(r'tile_map_data = PackedByteArray\("([^"]*)"\)', line):
            cur["tiles"] = m[1]
    return nodes, order


def vers_monde(nodes, chemin, pt):
    """Applique scale puis position de chaque ancetre. Une rotation est refusee."""
    x, y = pt
    p = chemin
    while p and p != ".":
        n = nodes[p]
        if abs(n["rot"]) > 1e-9:
            raise SystemExit(f"ERREUR : '{p}' est tourne (rotation={n['rot']}), non gere")
        x = x * n["scale"][0] + n["pos"][0]
        y = y * n["scale"][1] + n["pos"][1]
        p = n["parent"] if n["parent"] not in (None, ".") else None
    return (x, y)


def polygone_monde(nodes, chemin):
    n = nodes[chemin]
    return [vers_monde(nodes, chemin, pt) for pt in (n["poly"] or [])]


def cellules(nodes, chemin):
    """Cases peintes d'un TileMapLayer (format Godot 4 : 2 octets d'en-tete, 12 par case)."""
    n = nodes.get(chemin)
    if not n or not n["tiles"]:
        return set(), (0.0, 0.0)
    b = base64.b64decode(n["tiles"])
    out = set()
    for i in range((len(b) - 2) // 12):
        x, y = struct.unpack_from("<hh", b, 2 + i * 12)
        out.add((x, y))
    return out, n["pos"]


def case_du_point(x, y, origine):
    """Inverse de la projection iso 64x30 (diamond down) : monde -> case."""
    u = (x - origine[0]) / 32.0
    v = (y - origine[1]) / 15.0
    return (round((u + v) / 2.0), round((v - u) / 2.0))


# =============================================================================
# Geometrie
# =============================================================================

def surface(P):
    s = 0.0
    for i in range(len(P)):
        x1, y1 = P[i]
        x2, y2 = P[(i + 1) % len(P)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


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


def oriente(P):
    s = 0.0
    for i in range(len(P)):
        x1, y1 = P[i]
        x2, y2 = P[(i + 1) % len(P)]
        s += x1 * y2 - x2 * y1
    return s


def convexe(P):
    signe = 0
    for i in range(len(P)):
        a, b, c = P[i], P[(i + 1) % len(P)], P[(i + 2) % len(P)]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cr) < 1e-9:
            continue
        s = 1 if cr > 0 else -1
        if signe and s != signe:
            return False
        signe = s
    return True


def rogner(sujet, coupe):
    """Sutherland-Hodgman : `sujet` (quelconque) rogne par `coupe` (CONVEXE)."""
    if not convexe(coupe):
        raise SystemExit("ERREUR : polygone de coupe non convexe (area_limit ?)")
    if oriente(coupe) < 0:
        coupe = list(reversed(coupe))

    def a_gauche(p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0

    def croise(p, q, a, b):
        x1, y1 = p
        x2, y2 = q
        x3, y3 = a
        x4, y4 = b
        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    out = list(sujet)
    for i in range(len(coupe)):
        a, b = coupe[i], coupe[(i + 1) % len(coupe)]
        entree, out = out, []
        if not entree:
            break
        s = entree[-1]
        for e in entree:
            if a_gauche(e, a, b):
                if not a_gauche(s, a, b):
                    out.append(croise(s, e, a, b))
                out.append(e)
            elif a_gauche(s, a, b):
                out.append(croise(s, e, a, b))
            s = e
    return out


def entiers(P):
    """Arrondi a l'entier, sans doublons consecutifs ni sommet colineaire."""
    Q = []
    for x, y in P:
        p = [int(round(x)), int(round(y))]
        if not Q or Q[-1] != p:
            Q.append(p)
    if len(Q) > 1 and Q[0] == Q[-1]:
        Q.pop()
    R = []
    for i in range(len(Q)):
        a, b, c = Q[i - 1], Q[i], Q[(i + 1) % len(Q)]
        if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) != 0:
            R.append(b)
    return R


def boite(P):
    xs = [p[0] for p in P]
    ys = [p[1] for p in P]
    return {"x_min": min(xs), "x_max": max(xs), "y_min": min(ys), "y_max": max(ys)}


def mesure_sol(P, sol, origine_sol, eau, origine_eau, pas):
    """Part de la surface du polygone sur des cases sans sol, et sur de l'eau."""
    b = boite(P)
    total = vide = mouille = 0
    y = b["y_min"] + pas / 2.0
    while y < b["y_max"]:
        x = b["x_min"] + pas / 2.0
        while x < b["x_max"]:
            if dans(x, y, P):
                total += 1
                if case_du_point(x, y, origine_sol) not in sol:
                    if case_du_point(x, y, origine_eau) in eau:
                        mouille += 1
                    else:
                        vide += 1
            x += pas
        y += pas
    if total == 0:
        return 1.0, 0.0
    return vide / total, mouille / total


# =============================================================================
# Noms (carnet)
# =============================================================================

def slug(texte):
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def nettoie(nom):
    return re.split(r"[,(]", nom)[0].strip()


def lire_carnet(path: Path):
    noms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) != 3 or cols[1] in ("Français", "") or set(cols[0]) <= set("-"):
            continue
        fr, en = nettoie(cols[1]), nettoie(cols[2])
        if fr:
            noms.append((slug(fr), fr, en))
    return noms


def trouve_nom(nom_slug, carnet):
    exacts = [n for n in carnet if n[0] == nom_slug]
    if exacts:
        return exacts[0]
    sans_article = [n for n in carnet if re.sub(r"^(le|la|les|l)_", "", n[0]) == nom_slug]
    if sans_article:
        return sans_article[0]
    prefixes = [n for n in carnet if n[0].startswith(nom_slug + "_")]
    if len(prefixes) == 1:
        return prefixes[0]
    return None


# =============================================================================
# Ecriture sans reformater le reste du fichier
# =============================================================================

class Lecteur:
    """Analyseur JSON minimal qui garde les positions de chaque valeur."""

    def __init__(self, t):
        self.t = t

    def blanc(self, i):
        while i < len(self.t) and self.t[i] in " \t\r\n":
            i += 1
        return i

    def valeur(self, i):
        """-> (fin, structure). structure : dict cle -> (debut, fin, sous) ou liste."""
        i = self.blanc(i)
        c = self.t[i]
        if c == "{":
            membres = {}
            i = self.blanc(i + 1)
            if self.t[i] == "}":
                return i + 1, membres
            while True:
                i = self.blanc(i)
                fin_cle = self.chaine(i)
                cle = json.loads(self.t[i:fin_cle])
                i = self.blanc(fin_cle)
                assert self.t[i] == ":"
                debut = self.blanc(i + 1)
                fin, sous = self.valeur(debut)
                membres[cle] = (debut, fin, sous)
                i = self.blanc(fin)
                if self.t[i] == ",":
                    i += 1
                    continue
                assert self.t[i] == "}"
                return i + 1, membres
        if c == "[":
            elems = []
            i = self.blanc(i + 1)
            if self.t[i] == "]":
                return i + 1, elems
            while True:
                debut = self.blanc(i)
                fin, sous = self.valeur(debut)
                elems.append((debut, fin, sous))
                i = self.blanc(fin)
                if self.t[i] == ",":
                    i += 1
                    continue
                assert self.t[i] == "]"
                return i + 1, elems
        if c == '"':
            return self.chaine(i), None
        j = i
        while j < len(self.t) and self.t[j] not in ",]} \t\r\n":
            j += 1
        return j, None

    def chaine(self, i):
        assert self.t[i] == '"'
        j = i + 1
        while self.t[j] != '"':
            j += 2 if self.t[j] == "\\" else 1
        return j + 1


def rend(v, indent, nl):
    """json.dumps(indent=2) sauf : un tableau de nombres tient sur une ligne ([x, y])."""
    pad = " " * indent
    if isinstance(v, dict):
        if not v:
            return "{}"
        items = [f'{pad}  {json.dumps(k, ensure_ascii=False)}: {rend(x, indent + 2, nl)}' for k, x in v.items()]
        return "{" + nl + ("," + nl).join(items) + nl + pad + "}"
    if isinstance(v, list):
        if not v:
            return "[]"
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
            return "[" + ", ".join(json.dumps(x) for x in v) + "]"
        items = [pad + "  " + rend(x, indent + 2, nl) for x in v]
        return "[" + nl + ("," + nl).join(items) + nl + pad + "]"
    return json.dumps(v, ensure_ascii=False)


def colonne(t, pos):
    return pos - (t.rfind("\n", 0, pos) + 1)


# =============================================================================
# Export
# =============================================================================

def compte(surface_px2, elite, a):
    n = a.density * surface_px2 / 1e6
    n = max(a.count_min, min(a.count_max, round(n)))
    if elite:
        n = max(1, round(n * a.elite_factor))
    return int(n)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tscn", type=Path, help="havreden_map.tscn (lu, jamais modifie)")
    ap.add_argument("--zones", type=Path, default=ZONES)
    ap.add_argument("--carnet", type=Path, default=CARNET)
    ap.add_argument("--dry-run", action="store_true", help="imprime le diff, n'ecrit rien")
    ap.add_argument("--density", type=float, default=10.0,
                    help="monstres par million de px2 de POLYGONE (defaut 10, regle des aires de 08/2026)")
    ap.add_argument("--count-min", type=int, default=30)
    ap.add_argument("--count-max", type=int, default=55)
    ap.add_argument("--elite-factor", type=float, default=0.5,
                    help="facteur applique aux aires *_elite apres le bornage (defaut 0.5)")
    ap.add_argument("--empty-ground", type=float, default=0.20,
                    help="part maximale de cases sans sol avant de rendre l'aire dormante")
    ap.add_argument("--ground-step", type=float, default=32.0, help="pas de mesure du sol, px")
    ap.add_argument("--report", type=Path, help="ecrit aussi le rapport en JSON")
    a = ap.parse_args()

    nodes, order = lire_scene(a.tscn)
    if "Ground/Area_limit" not in nodes:
        raise SystemExit("ERREUR : pas de Ground/Area_limit dans la scene")
    limite = polygone_monde(nodes, "Ground/Area_limit")
    sol, origine_sol = cellules(nodes, "Ground")
    eau, origine_eau = cellules(nodes, "Water")
    if not sol:
        raise SystemExit("ERREUR : calque Ground vide ou introuvable")
    carnet = lire_carnet(a.carnet)

    brut = a.zones.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in brut else "\n"
    data = json.loads(brut)
    zones = data["zones"]
    iz = next(i for i, z in enumerate(zones) if z.get("id") == ZONE_ID)
    village = zones[iz]
    anciennes = {sa["id"]: sa for sa in village.get("spawn_areas", [])}
    rapport = {"aires": [], "retirees": [], "signalements": []}

    # ---- zones sures (villes) -------------------------------------------------
    ancienne_sure = village.get("safe_polygon") or []
    sures = []
    for p in order:
        n = nodes[p]
        if n["type"] != "Polygon2D" or not n["name"].endswith("_area") or p.startswith("map_areas/"):
            continue
        P = entiers(polygone_monde(nodes, p))
        if len(P) < 3:
            rapport["signalements"].append(f"ville {p} : moins de 3 sommets, ignoree")
            continue
        if ancienne_sure and len(P) == len(ancienne_sure) and all(
                abs(P[i][0] - ancienne_sure[i][0]) <= 1 and abs(P[i][1] - ancienne_sure[i][1]) <= 1
                for i in range(len(P))):
            rapport["signalements"].append(f"ville {p} : identique a safe_polygon (gardee la)")
            continue
        sid = n["name"][: -len("_area")]
        if any(s_["id"] == sid for s_ in sures):
            sid = p.replace("/", "__")[: -len("_area")]
        sures.append({"id": sid, "polygon": P})
    toutes_sures = ([ancienne_sure] if ancienne_sure else []) + [s["polygon"] for s in sures]

    # ---- aires ----------------------------------------------------------------
    nouvelles = []
    sources_utilisees = set()  # anciens ids dont le roster (ou la place) a ete repris
    for p in order:
        n = nodes[p]
        if not p.startswith("map_areas/") or not n["name"].startswith("mz_") or n["type"] != "Polygon2D":
            continue
        nid = n["name"]
        if nid in NON_EXPORTEES:
            rapport["signalements"].append(f"{nid} : non exportee (a remplir plus tard)")
            continue
        m = NOM_AIRE.match(nid)
        if not m:
            raise SystemExit(f"ERREUR : nom d'aire illisible '{nid}' (attendu mz_<nom>_<min>_<max>[_elite])")
        lo, hi, elite = int(m["min"]), int(m["max"]), bool(m["elite"])
        poly = rogner(polygone_monde(nodes, p), limite)
        if len(poly) < 3 or surface(poly) < 1.0:
            rapport["signalements"].append(f"{nid} : entierement hors de area_limit, ignoree")
            continue

        nom = trouve_nom(m["slug"], carnet)
        source = nid if nid in anciennes else REPRISE.get(nid)
        if source in anciennes:
            sources_utilisees.add(source)
        if nid in DECOUPES and REPRISE.get(nid) in anciennes and not any(
                f"{nid}_{bd['suffix']}" in anciennes for bd in DECOUPES[nid]):
            rapport["signalements"].append(
                f"{nid} : decoupe en {len(DECOUPES[nid])} sous-aires ; le roster de {REPRISE[nid]} "
                f"({', '.join(m_['id'] for m_ in anciennes[REPRISE[nid]].get('mobs', []))}) est remplace "
                f"par les rosters du script")
        if nom:
            name_fr, name_en = nom[1], nom[2]
        elif source in anciennes and anciennes[source].get("name_fr"):
            name_fr, name_en = anciennes[source]["name_fr"], anciennes[source].get("name_en", "")
            rapport["signalements"].append(f"{nid} : absent du carnet, nom repris de {source} « {name_fr} »")
        else:
            name_fr = name_en = m["slug"].replace("_", " ").title()
            rapport["signalements"].append(f"{nid} : absent du carnet, nom derive « {name_fr} »")

        # Sous-aires (bandes nord -> sud d'egale hauteur), sinon l'aire entiere.
        morceaux = []
        if nid in DECOUPES:
            ys = [q[1] for q in poly]
            y0, y1 = min(ys), max(ys)
            bandes = DECOUPES[nid]
            h = (y1 - y0) / len(bandes)
            xs = [q[0] for q in poly]
            for k, bd in enumerate(bandes):
                rect = [(min(xs) - 1, y0 + k * h), (max(xs) + 1, y0 + k * h),
                        (max(xs) + 1, y0 + (k + 1) * h), (min(xs) - 1, y0 + (k + 1) * h)]
                morceaux.append((f"{nid}_{bd['suffix']}", rogner(poly, rect), bd))
        else:
            morceaux.append((nid, poly, None))

        total_parent = sum(surface(q) for _, q, _ in morceaux)
        compte_parent = compte(total_parent, elite, a)
        for mid, mpoly, bd in morceaux:
            P = entiers(mpoly)
            entree = {}
            if mid in anciennes:
                entree = copy.deepcopy(anciennes[mid])
                origine = "existante"
            elif bd is None and source in anciennes:
                entree = copy.deepcopy(anciennes[source])
                origine = f"reprise de {source}"
            elif bd is not None:
                entree = {"max_stars": bd["max_stars"], "mobs": copy.deepcopy(bd["mobs"])}
                origine = f"decoupe de {nid} (roster du script)"
            else:
                entree = {"mobs": []}
                origine = "nouvelle"
            for k in CLES_GEOMETRIE:
                entree.pop(k, None)
            vide, mouille = mesure_sol(P, sol, origine_sol, eau, origine_eau, a.ground_step)
            a_roster = bool(entree.get("mobs"))
            sans_sol = vide > a.empty_ground
            if not a_roster or sans_sol:
                n_monstres = 0
                etat = "count 0 " + " + ".join(
                    x for x, ok in (("sans roster", not a_roster), ("sol absent", sans_sol)) if ok)
            elif bd is not None:
                n_monstres = max(1, round(compte_parent * surface(mpoly) / total_parent))
                etat = "spawnable"
            else:
                n_monstres, etat = compte(surface(mpoly), elite, a), "spawnable"
            lr = bd["level_range"] if bd else [lo, hi]
            sortie = {"id": mid, "name_fr": name_fr, "name_en": name_en, "level_range": lr,
                      "count": n_monstres}
            if bd is not None:
                sortie["parent_area"] = nid
            sortie.update({k: v for k, v in entree.items() if k in ("max_stars",)})
            sortie["bounds"] = boite(P)
            sortie["polygon"] = P
            sortie.update({k: v for k, v in entree.items() if k not in sortie})
            nouvelles.append(sortie)
            rapport["aires"].append({
                "id": mid, "level_range": lr, "count": n_monstres, "etat": etat, "origine": origine,
                "surface_mpx2": round(surface(mpoly) / 1e6, 2), "sol_vide": round(vide, 3),
                "eau": round(mouille, 3), "nom": name_fr})
            if mouille > 0.05:
                rapport["signalements"].append(
                    f"{mid} : {mouille:.0%} de sa surface est de l'eau (le serveur ne peut pas l'eviter)")

    gardes = {x["id"] for x in nouvelles}
    for old in anciennes:
        if old in gardes:
            continue
        if old in sources_utilisees:
            continue
        rapport["retirees"].append(old)

    # ---- ecriture -------------------------------------------------------------
    t = brut
    lec = Lecteur(t)
    _, racine = lec.valeur(0)
    zdeb, zfin, _ = racine["zones"]
    zd, zf, zs = racine["zones"][2][iz]
    membres = zs

    remplacements = []

    def remplace(cle, valeur):
        d, f, _ = membres[cle]
        remplacements.append((d, f, rend(valeur, colonne(t, d) - len(json.dumps(cle)) - 2, nl)))

    limite_json = entiers(limite)
    remplace("area_limit", limite_json)
    remplace("spawn_areas", nouvelles)
    pad = " " * (colonne(t, membres["id"][0]) - len('"id": '))
    if "safe_polygons" in membres:
        remplace("safe_polygons", sures)
    else:
        apres = membres.get("_safe_polygon_note") or membres.get("safe_polygon")
        if not apres:
            raise SystemExit("ERREUR : pas de safe_polygon dans la zone village, ou inserer safe_polygons ?")
        note = ("Zones sures en plus de safe_polygon (villes de la carte : Polygon2D *_area de "
                "havreden_map.tscn, exportes par scripts/export_havreden_areas.py). Le serveur n'y pose "
                "aucun monstre, coffre, Fissure, porte de faille ni point de recolte, et aucun groupe n'y "
                "engage un joueur.")
        bloc = (f",{nl}{pad}\"safe_polygons\": {rend(sures, len(pad), nl)}"
                f",{nl}{pad}\"_safe_polygons_note\": {json.dumps(note, ensure_ascii=False)}")
        remplacements.append((apres[1], apres[1], bloc))
    if "_spawn_areas_export_note" not in membres:
        note = ("spawn_areas, area_limit et safe_polygons sont EXPORTES de havreden_map.tscn par "
                "scripts/export_havreden_areas.py (polygon = contour map_areas/mz_*, rogne sur area_limit ; "
                "bounds = sa boite englobante ; count = regle de densite du script, 0 si pas de roster ou si "
                "le sol n'est pas peint). Relancer le script apres toute retouche de la carte. Seuls les "
                "rosters (mobs, elite_pool, boss, max_stars...) s'editent a la main ici.")
        d, f, _ = membres["spawn_areas"]
        remplacements.append((f, f, f",{nl}{pad}\"_spawn_areas_export_note\": {json.dumps(note, ensure_ascii=False)}"))

    for d, f, txt in sorted(remplacements, key=lambda r: r[0], reverse=True):
        t = t[:d] + txt + t[f:]

    json.loads(t)  # le resultat doit rester du JSON valide

    # ---- rapport --------------------------------------------------------------
    print(f"{'id':42} {'tranche':8} {'count':>5}  {'etat':33} sol vide  eau   origine")
    for r in rapport["aires"]:
        print(f"{r['id']:42} {r['level_range'][0]:>3}-{r['level_range'][1]:<4} {r['count']:>5}  "
              f"{r['etat']:33} {r['sol_vide']:>7.0%} {r['eau']:>5.0%}   {r['origine']}")
    total = sum(r["count"] for r in rapport["aires"])
    print(f"total monstres (count) : {total} ; villes en safe_polygons : {[s['id'] for s in sures]}")
    for s in rapport["signalements"]:
        print("signalement :", s)
    if rapport["retirees"]:
        print("anciennes aires retirees (absentes de la carte, roster perdu ici, garde dans git) :",
              ", ".join(rapport["retirees"]))
    if a.report:
        a.report.write_text(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if t == brut:
        print("zones.json : deja a jour, rien a ecrire")
        return 0
    if a.dry_run:
        sys.stdout.writelines(difflib.unified_diff(
            brut.splitlines(keepends=True), t.splitlines(keepends=True),
            fromfile="world/zones.json", tofile="world/zones.json (export)", n=1))
        print("\n--dry-run : rien n'est ecrit")
        return 0
    a.zones.write_bytes(t.encode("utf-8"))
    print(f"zones.json ecrit ({len(nouvelles)} aires)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
