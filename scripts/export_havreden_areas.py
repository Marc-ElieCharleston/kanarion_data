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
                    id, name_fr/name_en (NOM DU NOEUD, voir NOMS ci-dessous),
                    level_range (tranche du nom), polygon (rogne sur area_limit),
                    bounds (boite englobante du polygone), count (regle de densite,
                    ou COUNT_IMPOSE)

NOMS (decision Charleston du 2026-10-20)
  La scene fait foi : le nom affiche et la tranche viennent du nom du noeud
  `mz_<nom>_<min>_<max>`. Le carnet (_meta/carnet/noms_zones.md) ne sert qu'a
  l'orthographe (accents, articles) et a l'anglais quand il a EXACTEMENT ce nom.
  S'il n'a qu'un nom approchant (ex. carnet « Clairiere Disputee », scene
  « clairiere ») ou une autre tranche, le script garde la scene et SIGNALE
  l'ecart : c'est le carnet qu'il faut mettre a jour, pas la carte. Un nom de
  noeud provisoire (`to_do`) donne un nom provisoire, signale aussi.

CE QU'IL NE TOUCHE JAMAIS
  mobs, elite_pool, boss, elite_pack_chance et toute autre cle d'un id qui existe
  deja et a deja des monstres. Un id renomme reprend le roster de son ancien id
  (table REPRISE). Une aire SANS monstre recoit son roster de la table ROSTERS
  si elle y figure, sinon elle est ecrite avec `mobs: []` et `count: 0`.
  Exception : max_stars est ecrit a MAX_STARS (5) sur toutes les aires
  (decision du 2026-10-23).

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

# Nombre de monstres impose a la place de la regle de densite (2026-10-20, Charleston :
# les Abords d'Havreden passent de 32 a 45, la zone de depart doit etre plus peuplee).
# Une aire sans roster ou sans sol reste a 0 quand meme.
COUNT_IMPOSE = {"mz_abords_d_havreden_1_8": 45}

# Noms de noeud provisoires : pas un nom de lieu, le script en donne un provisoire.
NOMS_PROVISOIRES = {
    "to_do": {False: ("Zone à nommer", "Unnamed Zone"), True: ("Zone élite", "Elite Zone")},
}

# Anglais des noms de la scene que le carnet n'a pas (a valider, comme le carnet).
NOMS_EN_SCENE = {"clairiere": "The Clearing"}

# Mots qui restent en minuscule dans un nom (sauf en tete).
MOTS_MINUSCULES = {"de", "des", "du", "la", "le", "les", "aux", "au", "en", "et", "sur", "sous"}

# Decoupes d'une aire en sous-aires, chacune une spawn_area a part entiere (id
# <aire>_<suffix>, parent_area = l'aire). Rosters ecrits a la PREMIERE creation
# seulement ; ensuite la data fait foi (jamais reecrits).
#   mode "bandes" : bandes nord -> sud d'egale hauteur, dans l'ordre de la liste.
#   mode "coins"  : quadrants autour du centre de la boite englobante ; chaque
#                   sous-aire nomme son coin (no, ne, se, so).
# Bois des Loups (13-32, entree au nord) : pas de degrade continu, trois bandes.
# La Louve Matriarche (mob_wolf_soigneur, sortie du roster par le decoupage du
# 2026-10-19) revient au FOND du bois, en elite (Charleston, 2026-10-20).
# Anse des Naufrages (1-100, l'ile de capture) : « les niveaux 1-100 se font par
# coins de l'ile » (plan de la carte des monstres, zone de capture). Proposition A
# VALIDER : quatre coins de 25 niveaux, du nord (cote continent) vers le sud, dans
# le sens des aiguilles d'une montre ; meme roster partout (les betes saines du
# plan), la Hyene Alpha (rare) en elite.
_ANSE_MOBS = [{"id": "mob_belier", "weight": 10}, {"id": "mob_hyene", "weight": 10},
              {"id": "mob_taureau", "weight": 6}, {"id": "mob_cheval_sauvage", "weight": 6},
              {"id": "mob_armadillo", "weight": 4}]
DECOUPES = {
    "mz_bois_des_loups_13_32": {"mode": "bandes", "morceaux": [
        {"suffix": "a", "level_range": [13, 19], "max_stars": 3,
         "mobs": [{"id": "mob_wolf", "weight": 3}, {"id": "mob_frothing_wolf", "weight": 2}]},
        {"suffix": "b", "level_range": [20, 26], "max_stars": 3,
         "mobs": [{"id": "mob_loup_noir", "weight": 3}]},
        {"suffix": "c", "level_range": [27, 32], "max_stars": 4,
         "elite_pool": ["mob_vieux_loup"], "elite_pack_chance": 0.25,
         "mobs": [{"id": "mob_loup_blanc", "weight": 3}, {"id": "mob_vieux_loup", "weight": 2}]},
    ]},
    "mz_anse_des_naufrages_1_100": {"mode": "coins", "morceaux": [
        {"suffix": "no", "coin": "no", "level_range": [1, 25], "max_stars": 2,
         "elite_pool": ["mob_alpha_hyena"], "elite_pack_chance": 0.25, "mobs": _ANSE_MOBS},
        {"suffix": "ne", "coin": "ne", "level_range": [26, 50], "max_stars": 3,
         "elite_pool": ["mob_alpha_hyena"], "elite_pack_chance": 0.25, "mobs": _ANSE_MOBS},
        {"suffix": "se", "coin": "se", "level_range": [51, 75], "max_stars": 4,
         "elite_pool": ["mob_alpha_hyena"], "elite_pack_chance": 0.25, "mobs": _ANSE_MOBS},
        {"suffix": "so", "coin": "so", "level_range": [76, 100], "max_stars": 5,
         "elite_pool": ["mob_alpha_hyena"], "elite_pack_chance": 0.25, "mobs": _ANSE_MOBS},
    ]},
}
CLES_ROSTER_DECOUPE = ("max_stars", "elite_pool", "elite_pack_chance", "mobs")

# Etoiles : toutes les aires montent a 5 etoiles (Charleston, 2026-10-23 : « chaque
# zone peut avoir 5 etoiles »). Ecrit sur CHAQUE aire a chaque export, y compris les
# aires deja peuplees et les sous-aires des DECOUPES : c'est une regle de carte, pas
# un reglage d'aire.
MAX_STARS = 5

# Rosters des aires du niveau 20 au niveau 100 restees sans monstre (carte complete,
# Charleston 2026-10-23 : « on a toute la data jusqu'au niveau 100, place les
# monstres »). Source : la carte des monstres du 11/10 (artifact « Carte des monstres
# de Kanarion », noms FR -> ids de entities/monsters.json). Le niveau d'un monstre
# vient de l'AIRE (presence roll_area_level), pas de son level_range.
# Regles : poids 10 ; un elite nomme par la carte -> elite_pool + elite_pack_chance
# 0.3 (valeur des aires 60+ de 0.19) ; un boss du monde nomme par la carte -> boss
# pack_chance 0.5 (idem). Un monstre SANS sprite client dedie (monde ET combat) n'est
# pas pose : voir la liste ABSENTS_SANS_SPRITE.
# Ecrit seulement quand l'aire n'a pas encore de monstre (mobs vide ou absent) :
# ensuite la data fait foi, comme pour toute aire existante.
def _r(*ids):
    return [{"id": i, "weight": 10} for i in ids]


ROSTERS = {
    # Clairiere Disputee (carte : 15-25 ; scene 30-40, la scene fait foi).
    "mz_clairiere_30_40": {"mobs": _r("mob_wolf", "mob_loup_noir", "mob_boar", "mob_laie", "mob_marcassin")},
    "mz_combe_aux_ours_20_28": {"mobs": _r("mob_ourson", "mob_ours_brun", "mob_ourse", "mob_ours_noir",
                                           "mob_ours_cavernes")},
    "mz_foret_sud_25_35": {"mobs": _r("mob_ours_fissure", "mob_boar_wolf", "mob_frothing_wolf"),
                           "elite_pool": ["mob_grande_ourse"], "elite_pack_chance": 0.3},
    "mz_bois_fletri_25_35": {"mobs": _r("mob_cerf_obscur", "mob_misty_fox", "mob_biche_fletrie",
                                        "mob_cerf_fletri", "mob_blaireau_fletri")},
    "mz_ruines_de_guetteval_35_45": {"mobs": _r("mob_rat_mage", "mob_rat_soigneur"),
                                     "boss": {"id": "mob_rat_rongeur", "pack_chance": 0.5}},
    "mz_terres_de_givre_60_66": {"mobs": _r("mob_crystal_wolf", "mob_spectral_wolf", "mob_golem",
                                            "mob_ours_givre", "mob_cerf_givre")},
    # Col d'Asher : « on melange les voisins » (Givre a l'ouest, Braise a l'est,
    # patrouilles de zelotes venues de la Tour).
    "mz_col_d_asher_63_70": {"mobs": _r("mob_crystal_wolf", "mob_cerf_givre", "mob_ember_hound",
                                        "mob_sanglier_braise", "mob_zealot_guard", "mob_zealot_ritualist")},
    "mz_lac_gele_64_70": {"mobs": _r("mob_crystal_wolf", "mob_spectral_wolf", "mob_golem",
                                     "mob_ours_givre", "mob_cerf_givre")},
    "mz_terres_de_braise_63_70": {"mobs": _r("mob_ember_hound", "mob_nightmare_horse", "mob_nightmare_stag",
                                             "mob_sanglier_braise")},
    "mz_chemin_des_cendres_66_72": {"mobs": _r("mob_ember_hound", "mob_nightmare_horse", "mob_sanglier_braise"),
                                    "elite_pool": ["mob_taureau_braise"], "elite_pack_chance": 0.3},
    "mz_marais_de_la_faille_65_72": {"mobs": _r("mob_lizardman", "mob_lizardman_shaman", "mob_rift_stalker",
                                                "mob_rift_stitcher", "mob_rift_warden"),
                                     "elite_pool": ["mob_rift_maw"], "elite_pack_chance": 0.3},
    "mz_champ_des_ossuaires_70_78": {"mobs": _r("mob_archer_squelette", "mob_guerrier_skull",
                                                "mob_skeleton_necromancer", "mob_soul_harvester",
                                                "mob_bone_colossus")},
    "mz_plaine_fendue_72_80": {"mobs": _r("mob_abyss_swarmling", "mob_void_revenant", "mob_void_hound",
                                          "mob_void_executioner", "mob_lesser_void_titan"),
                               "elite_pool": ["mob_dread_horror", "mob_dread_matron"], "elite_pack_chance": 0.3},
    "mz_chaussee_brisee_78_88": {"mobs": _r("mob_void_spawn", "mob_nether_caller", "mob_void_priest",
                                            "mob_dread_stalker", "mob_lesser_demon"),
                                 "elite_pool": ["mob_abyssal_warlock"], "elite_pack_chance": 0.3},
    "mz_terres_dechirees_85_95": {"mobs": _r("mob_abyssal_charger", "mob_abyssal_reaver", "mob_abyssal_juggernaut",
                                             "mob_abyssal_seraph", "mob_abyssal_scholar"),
                                  "elite_pool": ["mob_soul_devourer", "mob_maw_of_the_abyss"],
                                  "elite_pack_chance": 0.3},
    # L'Abime : la carte n'y a qu'UN monstre avec sprite (Archonte Abyssal) ; les trois
    # archontes dechus n'ont pas d'art. Completee, A VALIDER, par les demons « qui
    # pensent » de Caer Isthrel (80-100, meme bande de la carte) : Erudit et Seraphin.
    "mz_l_abime_90_100": {"mobs": _r("mob_abyssal_archon", "mob_abyssal_scholar", "mob_abyssal_seraph"),
                          "boss": {"id": "mob_abyssal_sovereign", "pack_chance": 0.5}},
}

# Monstres de la carte des monstres NON poses faute de sprite client (monde + combat),
# a ajouter aux rosters quand leur art arrive. Informatif (rapport du script).
ABSENTS_SANS_SPRITE = {
    "mz_foret_sud_25_35": ["Sanglier Cuirasse (pas de fiche)", "Loup Fissure (pas de fiche)"],
    "mz_bois_fletri_25_35": ["Faon Fletri (pas de fiche)",
                             "boss_gardien_bois_fletri (sprite gardien_bois_fletri : le client ne retire pas boss_)"],
    "mz_ruines_de_guetteval_35_45": ["mob_wolf_packleader, mob_wolf_corrupted (loups humanoides : sprites sur "
                                     "feat/dungeon-open-run, pas sur main ; repli sur le loup gris)",
                                     "Louve Chamane (pas de fiche)",
                                     "mob_rat_assassin, mob_rat_cuirasse (repli sur le rat, art a generer)"],
    "mz_champ_des_ossuaires_70_78": ["boss_cursed_champion (pas de sprite)", "Liche (pas de fiche)"],
    "mz_l_abime_90_100": ["mob_grieving_sentinel, mob_wrathful_archon, mob_throne_sentinel (pas de sprite)"],
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
    """-> [(slug, fr, en, tranche)] ; tranche = (min, max), ou None (ville, 60+, —)."""
    noms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) != 3 or cols[1] in ("Français", "") or set(cols[0]) <= set("-"):
            continue
        fr, en = nettoie(cols[1]), nettoie(cols[2])
        m = re.fullmatch(r"(\d+)-(\d+)", cols[0])
        if fr:
            noms.append((slug(fr), fr, en, (int(m[1]), int(m[2])) if m else None))
    return noms


def trouve_nom(nom_slug, carnet):
    """Le MEME nom dans le carnet (a l'article pres), sinon None."""
    exacts = [n for n in carnet if n[0] == nom_slug]
    if exacts:
        return exacts[0]
    sans_article = [n for n in carnet if re.sub(r"^(le|la|les|l)_", "", n[0]) == nom_slug]
    if sans_article:
        return sans_article[0]
    return None


def nom_approchant(nom_slug, carnet):
    """Un nom du carnet qui COMMENCE par celui de la scene (ex. « Clairiere Disputee »)."""
    prefixes = [n for n in carnet if n[0].startswith(nom_slug + "_")]
    return prefixes[0] if len(prefixes) == 1 else None


def derive_nom(nom_slug, carnet):
    """Nom francais tire du nom du noeud, avec l'orthographe des mots du carnet."""
    vocab = {}
    for _, fr, _, _ in carnet:
        for mot in re.split(r"[\s']+", fr):
            if mot:
                vocab.setdefault(slug(mot), mot)
    jetons = nom_slug.split("_")
    out, i = [], 0
    while i < len(jetons):
        j = jetons[i]
        mot = vocab.get(j, j)
        if j in ("d", "l") and i + 1 < len(jetons):
            suivant = vocab.get(jetons[i + 1], jetons[i + 1])
            mot = j + "'" + suivant[:1].upper() + suivant[1:]
            i += 1
        elif out and j in MOTS_MINUSCULES:
            mot = mot.lower()
        else:
            mot = mot[:1].upper() + mot[1:]
        out.append(mot)
        i += 1
    texte = " ".join(out)
    return texte[:1].upper() + texte[1:]


def nom_de_scene(nom_slug, lo, hi, elite, carnet, signale):
    """(name_fr, name_en) d'une aire, la scene faisant foi (voir NOMS en tete)."""
    if nom_slug in NOMS_PROVISOIRES:
        fr, en = NOMS_PROVISOIRES[nom_slug][elite]
        signale(f"noeud au nom provisoire '{nom_slug}' : nom affiche provisoire « {fr} » / « {en} », a nommer")
        return fr, en
    exact = trouve_nom(nom_slug, carnet)
    if exact:
        if exact[3] and exact[3] != (lo, hi):
            signale(f"« {exact[1]} » : tranche du carnet {exact[3][0]}-{exact[3][1]}, scene {lo}-{hi} "
                    f"(la scene fait foi, carnet a mettre a jour)")
        return exact[1], exact[2]
    fr = derive_nom(nom_slug, carnet)
    en = NOMS_EN_SCENE.get(nom_slug)
    approche = nom_approchant(nom_slug, carnet)
    if approche:
        tr = f" ({approche[3][0]}-{approche[3][1]})" if approche[3] else ""
        signale(f"le carnet dit « {approche[1]} »{tr}, la scene dit « {fr} » ({lo}-{hi}) : nom de la scene "
                f"retenu, carnet a mettre a jour")
    else:
        signale(f"« {fr} » absent du carnet : nom tire de la scene")
    if not en:
        en = fr
        signale(f"« {fr} » : pas d'anglais connu, le francais est repris (a traduire)")
    else:
        signale(f"« {fr} » : anglais « {en} » propose par le script (NOMS_EN_SCENE), a valider")
    return fr, en


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

        source = nid if nid in anciennes else REPRISE.get(nid)
        if source in anciennes:
            sources_utilisees.add(source)
        decoupe = DECOUPES.get(nid, {}).get("morceaux", [])
        if decoupe and source in anciennes and not any(
                f"{nid}_{bd['suffix']}" in anciennes for bd in decoupe):
            rapport["signalements"].append(
                f"{nid} : decoupe en {len(decoupe)} sous-aires ; le roster de {source} "
                f"({', '.join(m_['id'] for m_ in anciennes[source].get('mobs', [])) or 'vide'}) est remplace "
                f"par les rosters du script")
        name_fr, name_en = nom_de_scene(m["slug"], lo, hi, elite, carnet,
                                        lambda t: rapport["signalements"].append(f"{nid} : {t}"))

        # Sous-aires (DECOUPES : bandes nord -> sud, ou coins), sinon l'aire entiere.
        morceaux = []
        if decoupe:
            xs = [q[0] for q in poly]
            ys = [q[1] for q in poly]
            x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys), max(ys)
            mode = DECOUPES[nid]["mode"]
            for k, bd in enumerate(decoupe):
                if mode == "bandes":
                    h = (y1 - y0) / len(decoupe)
                    rect = [(x0, y0 + k * h), (x1, y0 + k * h), (x1, y0 + (k + 1) * h), (x0, y0 + (k + 1) * h)]
                elif mode == "coins":
                    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
                    gx = (x0, cx) if bd["coin"][1] == "o" else (cx, x1)
                    gy = (y0 - 1, cy) if bd["coin"][0] == "n" else (cy, y1 + 1)
                    rect = [(gx[0], gy[0]), (gx[1], gy[0]), (gx[1], gy[1]), (gx[0], gy[1])]
                else:
                    raise SystemExit(f"ERREUR : mode de decoupe inconnu '{mode}' pour {nid}")
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
                entree = {k: copy.deepcopy(bd[k]) for k in CLES_ROSTER_DECOUPE if k in bd}
                origine = f"decoupe de {nid} (roster du script)"
            else:
                entree = {"mobs": []}
                origine = "nouvelle"
            for k in CLES_GEOMETRIE:
                entree.pop(k, None)
            if not entree.get("mobs") and mid in ROSTERS:
                entree.update(copy.deepcopy(ROSTERS[mid]))
                origine += " + roster ROSTERS"
            entree["max_stars"] = MAX_STARS
            vide, mouille = mesure_sol(P, sol, origine_sol, eau, origine_eau, a.ground_step)
            a_roster = bool(entree.get("mobs"))
            sans_sol = vide > a.empty_ground
            if not a_roster or sans_sol:
                n_monstres = 0
                etat = "count 0 " + " + ".join(
                    x for x, ok in (("sans roster", not a_roster), ("sol absent", sans_sol)) if ok)
            elif mid in COUNT_IMPOSE:
                n_monstres, etat = COUNT_IMPOSE[mid], "spawnable (count impose)"
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
    for aid, absents in ABSENTS_SANS_SPRITE.items():
        rapport["signalements"].append(f"{aid} : pas pose faute de sprite : {'; '.join(absents)}")
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
