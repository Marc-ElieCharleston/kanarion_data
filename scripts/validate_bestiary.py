#!/usr/bin/env python3
"""
Validateur du BESTIAIRE (monstres, especes, familiers, empreintes) -- cree le 2026-10-14.

Lot L0 de l'audit de scalabilite familiers/monstres (2026-10-13). Le serveur et le
client ont des replis SILENCIEUX : espece inconnue -> x1.0, role IA inconnu ->
brute, archetype inconnu -> rat, portrait absent -> tete du rat, monstre sans table
-> aucune ressource. Une faute dans la data donne donc un monstre plausible mais
faux, et personne ne le voit. Ce script relie tous les fichiers du bestiaire et
echoue FORT quand un lien est casse, avant le commit et en CI.

Contrôles (code, gravite par defaut) :
  B01 ERROR  schema de monsters.json : ids uniques, champs obligatoires, vocabulaires
             fermes (stat_archetype, ai_role, species, stage, threat_tier, rarity,
             roster_status) -- plus aucun x1.0 ni « brute » par defaut
  B02 ERROR  butin : tout monstre actif a une table (loot_table_id, sinon id sans
             mob_/boss_ : meme regle que loot_roller.cpp resolve_table_key)
  B03 ERROR  capture : famille connue, un archetype par role autorise, espece de
             monstre capturable, signature identique, growth_tier connu
  B04 WARN   capture : drop_chance == capture_rate_by_rarity[growth_tier], sauf
             surcharge assumee (`_override_reason` dans familiar_capture)
  B05 ERROR  archetypes de familier : id == familiar_<famille>_<role>, role,
             monster_species, signature skill_familiar_sig_<template>, loadout,
             balance_profile, icone declaree
  B06 ERROR  empreintes : une par (famille capturee, role) x rarete ; id, famille,
             role et rarete coherents ; toute empreinte mene a un archetype existant
             (sinon le service retombe sur le rat). Orphelines = WARN.
  B07 ERROR  raretes : memes ids (et memes poids) dans familiar_balance,
             familiar_incubation, gen_familiar_traces.RARITIES, les empreintes et
             capture_rate_by_rarity
  B08 ERROR  tables des generateurs coherentes avec entities/monster_species.json :
             apply_familiar_species.py (FAMILIAR_TO_MONSTER, SPECIES_PASSIVE),
             apply_monster_v2.py (EXTRA_SPECIES, HUMANS, UNDECIDED_CAPTURE,
             SPECIES_FIX), scripts/balance/species_table.py (SPECIES,
             SPECIES_IDENTITY, STAGE). Lues par `ast`, jamais executees.
  B09 WARN   especes dont la capturabilite n'est pas decidee (capturable: null)
  B10 ERROR  tutoriel et dons : monster_id des scenarios, archetypes des
             gift_offers, mercenaires
  B11 ERROR  affinites (familiar_balance.affinities, SI present) : especes,
             familles et statuts references existent
  B12 WARN   assets des monstres actifs : sprite resolu (client) ou art_pending
  B13 WARN   assets des familiers : icone « rat » bouche-trou, portrait et sprite
             (client)
  B14 WARN   _meta/sprite_resolution.json : alias et echelles sur des familles
             qui existent

ASSETS. Les sprites et portraits vivent dans le depot CLIENT. Sans lui, B12/B13 se
limitent a ce que dit la data (art_pending, icones rat_*.png). Avec lui
(--client-root, ou la variable KANARION_CLIENT_ROOT, ou un dossier voisin
../kanarion_client detecte automatiquement), les fichiers sont verifies avec les
memes regles que le client (sprite_resolver.gd, familiar_portrait.gd).

DETTE CONNUE -> WARNING. Les categories B04, B06 (orphelines), B09, B12, B13, B14
sont de la dette connue au 2026-10-14 : elles s'affichent avec leur compte et leur
liste, mais ne bloquent pas. Pour en faire une erreur bloquante une fois la dette
soldee : passer sa gravite a ERROR dans SEVERITY ci-dessous (une ligne), ou lancer
avec --strict pour tout durcir d'un coup (utile pour mesurer avant de basculer).

Usage :
  python scripts/validate_bestiary.py                 # exit 1 si une ERROR
  python scripts/validate_bestiary.py --warn-only     # rapporte, exit 0 toujours
  python scripts/validate_bestiary.py --strict        # les WARNING deviennent ERROR
  python scripts/validate_bestiary.py --client-root ../kanarion_client
  python scripts/validate_bestiary.py --no-client     # ignore un client detecte
  python scripts/validate_bestiary.py --max-items 0   # listes completes (defaut 0)

Exit 0 = tout va bien (ou --warn-only), exit 1 = au moins une ERROR.
"""

import argparse
import ast
import json
import os
import sys
from collections import defaultdict

DB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ERROR = "ERROR"
WARNING = "WARNING"

# Gravite de chaque categorie. Une dette soldee se verrouille en passant sa ligne a ERROR.
SEVERITY = {
    "B01": ERROR,
    "B02": ERROR,     # 0 monstre actif sans table depuis a7f4013 (2026-10-13)
    "B03": ERROR,
    "B04": WARNING,   # 4 drop_chance divergents : corriger, ou ajouter `_override_reason`
    "B05": ERROR,
    "B06": ERROR,
    "B06o": WARNING,  # empreintes orphelines conservees (inventaires joueurs)
    "B07": ERROR,
    "B08": ERROR,
    "B09": WARNING,   # `tribal` : capture a decider par le proprietaire
    "B10": ERROR,
    "B11": ERROR,
    "B12": WARNING,   # monstres sans sprite (faune des vacances, boss_*, humains)
    "B13": WARNING,   # familles en icone rat / sans portrait / sans sprite
    "B14": WARNING,
}

TITLES = {
    "B01": "schema et vocabulaires de monsters.json",
    "B02": "table de butin pour chaque monstre actif",
    "B03": "capture -> famille, archetypes, espece capturable, signature",
    "B04": "drop_chance de capture == capture_rate_by_rarity[growth_tier]",
    "B05": "archetypes de familier (id, role, espece, signature, loadout, icone)",
    "B06": "empreintes : une par (famille capturee, role, rarete)",
    "B06o": "empreintes orphelines (aucun monstre ne les donne)",
    "B07": "raretes identiques partout",
    "B08": "tables des generateurs Python == monster_species.json",
    "B09": "especes a capturabilite non decidee",
    "B10": "tutoriel et offres de familiers",
    "B11": "bloc affinities",
    "B12": "assets des monstres actifs",
    "B13": "assets des familiers (icone, portrait, sprite)",
    "B14": "_meta/sprite_resolution.json",
}

ROLES_FALLBACK = ("attaque", "tank", "heal", "utilitaire")
MONSTER_REQUIRED = ("id", "name_fr", "name_en", "category", "base_level", "level_range", "tags",
                    "ai_role", "base_stats", "base_xp", "skills", "threat_tier", "stat_archetype",
                    "rarity", "roster_status", "aggro_type")
ROSTER_STATUS = {"active", "shelved"}
# Exceptions ASSUMEES (mannequin d'entrainement : aucune identite de stats, aucun skill).
# Toute autre exception doit etre ajoutee ici, explicitement, avec sa raison.
SPECIESLESS_OK = {"mob_training_dummy"}
SKILLLESS_OK = {"mob_training_dummy"}


def load(rel):
    with open(os.path.join(DB, rel), encoding="utf-8") as f:
        return json.load(f)


def load_opt(rel):
    p = os.path.join(DB, rel)
    return load(rel) if os.path.exists(p) else None


def py_tables(rel, names):
    """Lit des constantes litterales d'un script SANS l'executer (ast.literal_eval)."""
    p = os.path.join(DB, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=rel)
    out = {}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return out


def public(d):
    return {k: v for k, v in (d or {}).items() if not str(k).startswith("_")}


class Report:
    def __init__(self):
        self.items = defaultdict(list)
        self.info = defaultdict(list)

    def add(self, code, msg):
        self.items[code].append(msg)

    def note(self, code, msg):
        self.info[code].append(msg)


# =============================================================================
# CONTROLES
# =============================================================================

def check_monsters(r, ctx):
    monsters = ctx["monsters"]
    seen = set()
    for m in monsters:
        mid = m.get("id", "?")
        if mid in seen:
            r.add("B01", f"{mid} : id en double")
        seen.add(mid)
        for k in MONSTER_REQUIRED:
            if k == "skills" and mid in SKILLLESS_OK and isinstance(m.get(k), list):
                continue
            if k not in m or m[k] in (None, "", []):
                r.add("B01", f"{mid} : champ obligatoire absent ou vide '{k}'")
        if not (mid.startswith("mob_") or mid.startswith("boss_")):
            r.add("B01", f"{mid} : id sans prefixe mob_/boss_ (convention du butin et du sprite)")
        checks = (
            ("stat_archetype", ctx["stat_archetypes"], "config/monster_scaling_model.json archetypes_lv1_standard"),
            ("ai_role", ctx["ai_roles"], "config/monster_ai.json ai_roles"),
            ("threat_tier", ctx["threat_tiers"], "config/monster_scaling_model.json tier_multipliers"),
            ("rarity", ctx["monster_rarities"], "config/monster_scaling_model.json rarity_multipliers"),
            ("roster_status", ROSTER_STATUS, "active|shelved"),
        )
        for field, vocab, src in checks:
            v = m.get(field)
            if v is not None and v not in vocab:
                r.add("B01", f"{mid} : {field} '{v}' inconnu ({src})")
        sp = m.get("species")
        if sp is None:
            if mid not in SPECIESLESS_OK:
                r.add("B01", f"{mid} : pas de species (le scaling C++ la prendrait a x1.0 sans rien dire)")
        elif sp not in ctx["species"]:
            r.add("B01", f"{mid} : species '{sp}' absente de entities/monster_species.json (x1.0 silencieux)")
        st = m.get("stage")
        if st is not None and st not in ctx["stages"]:
            r.add("B01", f"{mid} : stage '{st}' absent de monster_species.json stages (x1.0 silencieux)")
        lr = m.get("level_range")
        if isinstance(lr, list):
            if len(lr) != 2 or not all(isinstance(x, int) for x in lr) or lr[0] > lr[1]:
                r.add("B01", f"{mid} : level_range invalide {lr}")
        if "base_level" in m and not isinstance(m["base_level"], int):
            r.add("B01", f"{mid} : base_level non entier")


def check_loot(r, ctx):
    tables = ctx["loot_tables"]
    used = set()
    for m in ctx["monsters"]:
        mid = m.get("id", "?")
        ltid = m.get("loot_table_id")
        if ltid and ltid not in tables:
            r.add("B02", f"{mid} : loot_table_id '{ltid}' absent de monster_loot_tables")
        key = ltid if ltid in tables else None
        if key is None:
            stripped = mid[4:] if mid.startswith("mob_") else mid[5:] if mid.startswith("boss_") else mid
            key = stripped if stripped in tables else None
        if key:
            used.add(key)
        elif m.get("roster_status") == "active":
            r.add("B02", f"{mid} : aucune table de butin (ajouter '{mid.split('_', 1)[-1]}' dans "
                         "items/loot_tables.json monster_loot_tables, une liste vide est permise)")
    for k, v in tables.items():
        if not isinstance(v, list):
            r.add("B02", f"monster_loot_tables['{k}'] n'est pas une liste")
    unused = sorted(k for k in tables if k not in used)
    if unused:
        r.note("B02", f"{len(unused)} table(s) sans monstre : {', '.join(unused)}")


def check_capture(r, ctx):
    fam_roles = ctx["family_roles"]
    arch = ctx["archetypes"]
    rates = ctx["capture_rates"]
    for m in ctx["monsters"]:
        cap = m.get("familiar_capture")
        if not cap or not cap.get("enabled"):
            continue
        mid = m["id"]
        if m.get("roster_status") != "active":
            r.note("B03", f"{mid} : capture active sur un monstre {m.get('roster_status')}")
        fam = cap.get("family")
        if not fam:
            r.add("B03", f"{mid} : familiar_capture.enabled sans 'family'")
            continue
        if fam not in fam_roles:
            r.add("B03", f"{mid} : famille '{fam}' sans aucun archetype dans entities/familiars.json")
            continue
        roles = cap.get("allowed_roles") or []
        if not roles:
            r.add("B03", f"{mid} : allowed_roles vide")
        for role in roles:
            if role not in ctx["roles"]:
                r.add("B03", f"{mid} : role '{role}' inconnu (familiar_balance.json role_profiles)")
            elif f"familiar_{fam}_{role}" not in arch:
                r.add("B03", f"{mid} : pas d'archetype familiar_{fam}_{role} pour le role autorise '{role}'")
        sp = m.get("species")
        spd = ctx["species"].get(sp)
        if spd is not None and spd.get("capturable") is not True and not m.get("capturable"):
            r.add("B03", f"{mid} : capture active mais l'espece '{sp}' a capturable={spd.get('capturable')}")
        sig = cap.get("signature_template")
        fam_sigs = {a["signature_template"] for a in arch.values() if a.get("species") == fam}
        if sig and fam_sigs and sig not in fam_sigs:
            r.add("B03", f"{mid} : signature_template '{sig}' != celle des archetypes {sorted(fam_sigs)}")
        tier = cap.get("growth_tier")
        if tier not in rates:
            r.add("B03", f"{mid} : growth_tier '{tier}' absent de capture_rate_by_rarity")
            continue
        dc = cap.get("drop_chance")
        if dc is not None and dc != rates[tier] and not cap.get("_override_reason"):
            r.add("B04", f"{mid} : drop_chance {dc} != capture_rate_by_rarity['{tier}'] = {rates[tier]} "
                         "(corriger, ou justifier par `_override_reason`)")


def check_archetypes(r, ctx):
    seen = set()
    for a in ctx["familiar_list"]:
        aid = a.get("archetype_id") or a.get("id") or "?"
        if aid in seen:
            r.add("B05", f"{aid} : archetype en double")
        seen.add(aid)
        if a.get("id") != a.get("archetype_id"):
            r.add("B05", f"{aid} : id '{a.get('id')}' != archetype_id")
        fam, role = a.get("species"), a.get("role")
        if not fam:
            r.add("B05", f"{aid} : pas de famille (champ species) -> le service en ferait un rat")
        if role not in ctx["roles"]:
            r.add("B05", f"{aid} : role '{role}' inconnu (familiar_balance.json role_profiles)")
        if fam and role and aid != f"familiar_{fam}_{role}":
            r.add("B05", f"{aid} : id != familiar_<famille>_<role> (familiar_{fam}_{role})")
        msp = a.get("monster_species")
        if msp not in ctx["species"]:
            r.add("B05", f"{aid} : monster_species '{msp}' absente de monster_species.json")
        sig = a.get("signature_template")
        if not sig:
            r.add("B05", f"{aid} : pas de signature_template")
        elif f"skill_familiar_sig_{sig}" not in ctx["familiar_skills"]:
            r.add("B05", f"{aid} : skill_familiar_sig_{sig} absent de classes/familiar/skills.json")
        for s in a.get("skill_loadout", []) or []:
            if s not in ctx["familiar_skills"]:
                r.add("B05", f"{aid} : skill_loadout '{s}' absent de classes/familiar/skills.json")
        bp = a.get("balance_profile")
        if bp not in ctx["balance_profiles"]:
            r.add("B05", f"{aid} : balance_profile '{bp}' absent de familiar_balance.json profiles")
        if a.get("ai_profile") and a["ai_profile"] not in ctx["ai_roles"]:
            r.add("B05", f"{aid} : ai_profile '{a['ai_profile']}' absent de monster_ai.json ai_roles")
        icon = a.get("icon")
        if not icon or not str(icon).endswith(".png"):
            r.add("B05", f"{aid} : icone non declaree ({icon!r})")


def check_traces(r, ctx):
    rar = ctx["rarities"]
    traces = ctx["traces"]
    by_id = {}
    for t in traces:
        tid = t.get("id", "?")
        if tid in by_id:
            r.add("B06", f"{tid} : empreinte en double")
        by_id[tid] = t
        fam, role, tr = t.get("family"), t.get("role"), t.get("trace_rarity")
        if tid != f"empreinte_souffle_{fam}_{role}_{tr}":
            r.add("B06", f"{tid} : id != empreinte_souffle_<family>_<role>_<trace_rarity> ({fam}, {role}, {tr})")
        if tr not in rar:
            r.add("B06", f"{tid} : trace_rarity '{tr}' inconnue")
        if f"familiar_{fam}_{role}" not in ctx["archetypes"]:
            r.add("B06", f"{tid} : aucun archetype familiar_{fam}_{role} (le service retomberait sur le rat)")
    wanted = set()
    for m in ctx["monsters"]:
        cap = m.get("familiar_capture") or {}
        if not cap.get("enabled") or not cap.get("family"):
            continue
        for role in cap.get("allowed_roles") or []:
            for rr in rar:
                wanted.add(f"empreinte_souffle_{cap['family']}_{role}_{rr}")
    for tid in sorted(wanted - set(by_id)):
        r.add("B06", f"{tid} : empreinte manquante (python scripts/gen_familiar_traces.py)")
    orphans = sorted(set(by_id) - wanted)
    fams = sorted({by_id[t].get("family") for t in orphans})
    if orphans:
        r.add("B06o", f"{len(orphans)} empreintes sans monstre capturable, familles : {', '.join(fams)}")
    captured = {(m["familiar_capture"]["family"], role) for m in ctx["monsters"]
                if (m.get("familiar_capture") or {}).get("enabled") and m["familiar_capture"].get("family")
                for role in m["familiar_capture"].get("allowed_roles") or []}
    gifts = {aid for offer in public(ctx["balance"].get("gift_offers")).values() for aid in offer}
    unreachable = sorted(aid for aid, a in ctx["archetypes"].items()
                         if (a.get("species"), a.get("role")) not in captured and aid not in gifts)
    if unreachable:
        r.note("B06", f"{len(unreachable)} archetype(s) ni capturables ni offerts (Aldric, orphelines) : "
                      + ", ".join(unreachable))


def check_rarities(r, ctx):
    ref = ctx["rarities"]
    sets = {"familiar_balance.json rarity_multipliers": ref}
    inc = ctx["incubation"] or {}
    if "durations_seconds" in inc:
        sets["familiar_incubation.json durations_seconds"] = list(public(inc["durations_seconds"]))
    if "rarity_drop_weights" in inc:
        sets["familiar_incubation.json rarity_drop_weights"] = list(public(inc["rarity_drop_weights"]))
        for k, w in public(inc["rarity_drop_weights"]).items():
            bw = public(ctx["balance"].get("rarity_multipliers")).get(k, {}).get("drop_weight")
            if bw is not None and bw != w:
                r.add("B07", f"poids de drop '{k}' : familiar_balance {bw} != familiar_incubation {w}")
    gen = py_tables("scripts/gen_familiar_traces.py", {"RARITIES"})
    if gen and "RARITIES" in gen:
        sets["gen_familiar_traces.py RARITIES"] = [x[0] for x in gen["RARITIES"]]
    else:
        r.add("B07", "scripts/gen_familiar_traces.py : RARITIES introuvable")
    sets["items/consumables.json familiar_traces.trace_rarity"] = sorted({t.get("trace_rarity") for t in ctx["traces"]})
    tiers = set(ctx["capture_rates"]) - {"starter"}
    sets["capture_rate_by_rarity (hors starter)"] = sorted(tiers)
    for name, vals in sets.items():
        if set(vals) != set(ref):
            r.add("B07", f"{name} = {sorted(vals)} != {sorted(ref)}")
    for k, v in public(ctx["balance"].get("rarity_multipliers")).items():
        if not isinstance(v, dict) or not (0 < float(v.get("stat_multiplier", 0)) <= 5):
            r.add("B07", f"rarity_multipliers['{k}'].stat_multiplier hors de ]0, 5] (le service le remettrait a 1.0)")
        if not isinstance(v, dict) or not float(v.get("drop_weight", 0)) > 0:
            r.add("B07", f"rarity_multipliers['{k}'].drop_weight <= 0 : cette rarete ne tomberait jamais")


def check_generators(r, ctx):
    species = ctx["species"]
    stages = ctx["stages"]
    fam_species = {a.get("species") for a in ctx["archetypes"].values()}
    fas = py_tables("scripts/apply_familiar_species.py", {"FAMILIAR_TO_MONSTER", "SPECIES_PASSIVE"})
    if not fas or "FAMILIAR_TO_MONSTER" not in fas or "SPECIES_PASSIVE" not in fas:
        r.add("B08", "apply_familiar_species.py : FAMILIAR_TO_MONSTER / SPECIES_PASSIVE illisibles")
    else:
        f2m, spp = fas["FAMILIAR_TO_MONSTER"], fas["SPECIES_PASSIVE"]
        for fam in sorted(fam_species - set(f2m)):
            r.add("B08", f"FAMILIAR_TO_MONSTER : famille '{fam}' absente (le script echouera)")
        for fam, msp in sorted(f2m.items()):
            if msp not in species:
                r.add("B08", f"FAMILIAR_TO_MONSTER['{fam}'] = '{msp}' absente de monster_species.json")
        for a in ctx["archetypes"].values():
            want = f2m.get(a.get("species"))
            if want and a.get("monster_species") != want:
                r.add("B08", f"{a['archetype_id']} : monster_species '{a.get('monster_species')}' != "
                             f"FAMILIAR_TO_MONSTER '{want}' (relancer apply_familiar_species.py)")
        for msp in sorted({f2m[f] for f in fam_species if f in f2m} - set(spp)):
            r.add("B08", f"SPECIES_PASSIVE : espece '{msp}' utilisee par un familier, sans passif")
        for msp in sorted(set(spp) - set(species)):
            r.add("B08", f"SPECIES_PASSIVE : espece '{msp}' absente de monster_species.json")
        for msp in sorted(set(spp)):
            if species.get(msp, {}).get("capturable") is False:
                r.add("B08", f"SPECIES_PASSIVE : espece '{msp}' a un passif mais capturable=false")
    v2 = py_tables("scripts/apply_monster_v2.py",
                   {"EXTRA_SPECIES", "HUMANS", "UNDECIDED_CAPTURE", "SPECIES_FIX"}) or {}
    st = py_tables("scripts/balance/species_table.py", {"SPECIES", "SPECIES_IDENTITY", "STAGE"}) or {}
    if not all(k in v2 for k in ("EXTRA_SPECIES", "HUMANS", "UNDECIDED_CAPTURE", "SPECIES_FIX")):
        r.add("B08", "apply_monster_v2.py : EXTRA_SPECIES / HUMANS / UNDECIDED_CAPTURE / SPECIES_FIX illisibles")
        return
    if not all(k in st for k in ("SPECIES", "SPECIES_IDENTITY", "STAGE")):
        r.add("B08", "balance/species_table.py : SPECIES / SPECIES_IDENTITY / STAGE illisibles")
        return
    # apply_monster_v2.species_file() REECRIT monster_species.json depuis ces tables :
    # toute difference serait perdue (ou reintroduite) au prochain `apply`.
    ident = dict(st["SPECIES_IDENTITY"])
    ident.pop("elementaire", None)
    ident.update(v2["EXTRA_SPECIES"])
    for sp in sorted(set(species) - set(ident)):
        r.add("B08", f"espece '{sp}' dans monster_species.json mais ni dans SPECIES_IDENTITY ni dans "
                     "EXTRA_SPECIES (apply_monster_v2.py l'effacerait)")
    for sp in sorted(set(ident) - set(species)):
        r.add("B08", f"espece '{sp}' dans les tables Python mais absente de monster_species.json")
    for sp, (core, bonus, note) in sorted(ident.items()):
        e = species.get(sp)
        if e is None:
            continue
        want = dict(zip(["hp", "atk", "armor", "magic_resist"], core))
        if e.get("identity") != want:
            r.add("B08", f"espece '{sp}' : identity {e.get('identity')} != tables Python {want}")
        if e.get("rate_bonus") != bonus:
            r.add("B08", f"espece '{sp}' : rate_bonus {e.get('rate_bonus')} != tables Python {bonus}")
        if e.get("note_fr") != note:
            r.add("B08", f"espece '{sp}' : note_fr differe des tables Python")
        want_cap = None if sp in v2["UNDECIDED_CAPTURE"] else sp not in v2["HUMANS"]
        if e.get("capturable") != want_cap:
            r.add("B08", f"espece '{sp}' : capturable {e.get('capturable')} != HUMANS/UNDECIDED_CAPTURE ({want_cap})")
    if stages != st["STAGE"]:
        diff = sorted(set(stages.items()) ^ set(st["STAGE"].items()))
        r.add("B08", f"stages de monster_species.json != species_table.STAGE : {diff}")
    by_id = {m["id"]: m for m in ctx["monsters"]}
    for sp, ids in st["SPECIES"].items():
        for mid in ids:
            want = v2["SPECIES_FIX"].get(mid, sp)
            if want == "elementaire":
                continue
            m = by_id.get(mid)
            if m is None:
                r.note("B08", f"species_table.SPECIES['{sp}'] cite {mid}, absent de monsters.json")
            elif m.get("species") != want:
                r.add("B08", f"{mid} : species '{m.get('species')}' != species_table/SPECIES_FIX '{want}'")


def check_species(r, ctx):
    for sp, e in sorted(ctx["species"].items()):
        if e.get("capturable") is None:
            r.add("B09", f"espece '{sp}' : capturable=null (a decider)")
        for k in ("identity", "rate_bonus", "capturable"):
            if k not in e:
                r.add("B01", f"monster_species.json '{sp}' : champ '{k}' absent")
    used = {m.get("species") for m in ctx["monsters"]}
    unused = sorted(set(ctx["species"]) - used)
    if unused:
        r.note("B09", f"{len(unused)} espece(s) sans monstre : {', '.join(unused)}")


def check_tutorial_gifts(r, ctx):
    mids = {m["id"] for m in ctx["monsters"]}
    tut = ctx["tutorial"]
    mercs = ctx["mercenary_ids"]
    if tut is not None:
        for sid, sc in public(tut.get("scenarios")).items():
            for side in ("allies", "enemies"):
                for e in sc.get(side, []) or []:
                    kind = e.get("kind")
                    if kind == "monster":
                        if e.get("monster_id") not in mids:
                            r.add("B10", f"tutorial_encounters '{sid}' : monster_id '{e.get('monster_id')}' "
                                         "inconnu (le serveur le remplacerait par mob_rat)")
                    elif kind == "mercenary":
                        if mercs is not None and e.get("archetype_id") not in mercs:
                            r.add("B10", f"tutorial_encounters '{sid}' : mercenaire '{e.get('archetype_id')}' inconnu")
                    else:
                        r.add("B10", f"tutorial_encounters '{sid}' : kind '{kind}' inconnu")
    for offer, aids in public(ctx["balance"].get("gift_offers")).items():
        for aid in aids:
            if aid not in ctx["archetypes"]:
                r.add("B10", f"gift_offers['{offer}'] : archetype '{aid}' inconnu")


def check_affinities(r, ctx):
    aff = ctx["balance"].get("affinities")
    if aff is None:
        r.note("B11", "pas de bloc affinities dans familiar_balance.json : rien a verifier")
        return
    for sp in public(aff.get("species_to_affinity")):
        if sp not in ctx["species"]:
            r.add("B11", f"affinities.species_to_affinity : espece '{sp}' inconnue")
    for fam in public(aff.get("family_overrides")):
        if fam not in ctx["family_roles"]:
            r.add("B11", f"affinities.family_overrides : famille '{fam}' inconnue")
    for k in public(aff.get("chance_by_rarity")):
        if k not in ctx["rarities"]:
            r.add("B11", f"affinities.chance_by_rarity : rarete '{k}' inconnue")
    status = ctx["status_ids"]

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("status", "status_id", "effect_id", "statuses") and v:
                    for sid in (v if isinstance(v, list) else [v]):
                        if isinstance(sid, str) and sid not in status:
                            r.add("B11", f"affinities{path}.{k} : statut '{sid}' absent de stats/status_effects.json")
                elif not str(k).startswith("_"):
                    walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(aff, "")


# ----------------------------------------------------------------------------- assets

def find_client(arg, disabled):
    if disabled:
        return None
    for cand in (arg, os.environ.get("KANARION_CLIENT_ROOT"),
                 os.path.join(os.path.dirname(DB), "kanarion_client")):
        if cand and os.path.isfile(os.path.join(cand, "project.godot")):
            return os.path.abspath(cand)
        if cand and cand == arg:
            print(f"ATTENTION : --client-root '{arg}' n'est pas un projet Godot (project.godot absent)")
    return None


def check_assets(r, ctx, client):
    sr = ctx["sprite_resolution"] or {}
    alias = public(sr.get("familiar_species_sprite"))
    scale = public(sr.get("familiar_species_scale"))
    fams = set(ctx["family_roles"])
    for k in sorted(set(alias) - fams):
        r.add("B14", f"familiar_species_sprite : '{k}' n'est pas une famille de familier")
    for k in sorted(set(scale) - fams):
        r.add("B14", f"familiar_species_scale : '{k}' n'est pas une famille de familier")

    active = [m for m in ctx["monsters"] if m.get("roster_status") == "active"]
    # Une famille est « art_pending declare » si un monstre qui la donne porte art_pending.
    fam_pending = {m["familiar_capture"]["family"] for m in ctx["monsters"]
                   if m.get("art_pending") and (m.get("familiar_capture") or {}).get("family")}

    # Icones « rat » bouche-trou dans la data elle-meme (audit D7).
    rat_icon = defaultdict(list)
    for a in ctx["archetypes"].values():
        base = os.path.basename(str(a.get("icon", "")))
        if a.get("species") != "rat" and base.startswith("rat_"):
            rat_icon[a["species"]].append(a["role"])
    und = sorted(f for f in rat_icon if f not in fam_pending)
    dec = sorted(f for f in rat_icon if f in fam_pending)
    if und:
        r.add("B13", f"{len(und)} famille(s) avec icone rat_*.png SANS art_pending declare : {', '.join(und)}")
    if dec:
        r.add("B13", f"{len(dec)} famille(s) avec icone rat_*.png, art_pending declare : {', '.join(dec)}")

    if client is None:
        pend = sorted(m["id"] for m in active if m.get("art_pending"))
        if pend:
            r.add("B12", f"{len(pend)} monstre(s) actif(s) art_pending (sprite non verifie, client absent) : "
                         + ", ".join(pend))
        r.note("B12", "client absent : sprites et portraits non verifies "
                      "(--client-root CHEMIN ou KANARION_CLIENT_ROOT pour les verifier)")
        return

    mon_dir = os.path.join(client, "assets", "animations", "monsters")
    have = {f[:-len("_frames.tres")] for f in os.listdir(mon_dir) if f.endswith("_frames.tres")} \
        if os.path.isdir(mon_dir) else set()
    exact, family, none_pend, none_undecl = [], [], [], []
    for m in active:
        mid = m["id"]
        # room.cpp n'enleve que « mob_ » (audit B15) : boss_x cherche boss_x_frames.tres.
        key = mid[4:] if mid.startswith("mob_") else mid
        if key in have:
            exact.append(mid)
            continue
        parts = key.split("_")
        base = None
        while len(parts) > 1:
            parts.pop()
            if "_".join(parts) in have:
                base = "_".join(parts)
                break
        if base:
            family.append(f"{mid}->{base}")
        elif m.get("art_pending"):
            none_pend.append(mid)
        else:
            none_undecl.append(mid)
    r.note("B12", f"{len(active)} monstres actifs : {len(exact)} sprite exact, {len(family)} repli famille, "
                  f"{len(none_pend) + len(none_undecl)} sans sprite")
    if none_undecl:
        r.add("B12", f"{len(none_undecl)} monstre(s) actif(s) SANS sprite et SANS art_pending : "
                     + ", ".join(none_undecl))
    if none_pend:
        r.add("B12", f"{len(none_pend)} monstre(s) actif(s) sans sprite, art_pending declare : "
                     + ", ".join(none_pend))
    if family:
        r.add("B12", f"{len(family)} monstre(s) actif(s) sur le repli par famille (sprite d'un autre monstre) : "
                     + ", ".join(family))

    ui = os.path.join(client, "assets", "ui", "familiars")
    no_portrait, no_sprite, no_icon = [], [], 0
    for fam in sorted(fams):
        if not (os.path.isfile(os.path.join(ui, "portraits_v2", fam + ".png"))
                or os.path.isfile(os.path.join(ui, fam + ".png"))):
            no_portrait.append(fam)
        names = [fam] + ([alias[fam]] if fam in alias else [])
        if not any(n in have for n in names):
            no_sprite.append(fam)
    for a in ctx["archetypes"].values():
        icon = str(a.get("icon", ""))
        if icon and not os.path.isfile(os.path.join(client, "assets", icon)):
            no_icon += 1
    if no_portrait:
        r.add("B13", f"{len(no_portrait)}/{len(fams)} famille(s) sans portrait (le client affiche le rat) : "
                     + ", ".join(no_portrait))
    if no_sprite:
        r.add("B13", f"{len(no_sprite)}/{len(fams)} famille(s) sans sprite de compagnon : " + ", ".join(no_sprite))
    if no_icon:
        # Le client ne lit pas `icon` (familiar_portrait.gd resout par famille) : champ mort,
        # a supprimer au lot L4 (audit D7). Signale sans bloquer ni lister.
        r.note("B13", f"champ `icon` des archetypes : {no_icon}/{len(ctx['archetypes'])} fichiers absents "
                      "du client, qui ne le lit pas (portrait resolu par famille)")


# =============================================================================
# MAIN
# =============================================================================

def build_context():
    monsters = load("entities/monsters.json")["monsters"]
    sp = load("entities/monster_species.json")
    fams = load("entities/familiars.json")["familiars"]
    balance = load("config/familiar_balance.json")
    model = load("config/monster_scaling_model.json")
    ai = load("config/monster_ai.json")
    loot = load("items/loot_tables.json")
    cons = load("items/consumables.json")
    fskills = load("classes/familiar/skills.json")
    mercs = load_opt("entities/mercenaries.json")
    status = load_opt("stats/status_effects.json") or {}
    family_roles = defaultdict(set)
    for a in fams:
        family_roles[a.get("species")].add(a.get("role"))
    merc_ids = None
    if mercs is not None:
        merc_ids = set()

        def walk(o):
            if isinstance(o, dict):
                for k in ("id", "archetype_id"):
                    if isinstance(o.get(k), str):
                        merc_ids.add(o[k])
                for k, v in o.items():
                    if isinstance(v, (dict, list)):
                        if isinstance(v, dict) and not str(k).startswith("_"):
                            merc_ids.add(k)
                        walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(mercs)
    status_ids = set()
    for cat in (status.get("effects") or {}).values():
        if isinstance(cat, dict):
            status_ids.update(cat.keys())
    return {
        "monsters": monsters,
        "species": public(sp.get("species")),
        "stages": public(sp.get("stages")),
        "familiar_list": fams,
        "archetypes": {a.get("archetype_id"): a for a in fams},
        "family_roles": dict(family_roles),
        "balance": balance,
        "roles": set(public(balance.get("role_profiles"))) or set(ROLES_FALLBACK),
        "balance_profiles": set(public(balance.get("profiles"))),
        "rarities": list(public(balance.get("rarity_multipliers"))),
        "capture_rates": public(balance.get("capture_rate_by_rarity")),
        "incubation": load_opt("config/familiar_incubation.json"),
        "stat_archetypes": {k for k, v in public(model.get("archetypes_lv1_standard")).items() if isinstance(v, dict)},
        "threat_tiers": set(public(model.get("tier_multipliers"))),
        "monster_rarities": set(public(model.get("rarity_multipliers"))),
        "ai_roles": set(public(ai.get("ai_roles"))),
        "loot_tables": public(loot.get("monster_loot_tables")),
        "traces": cons.get("familiar_traces", []),
        "familiar_skills": {s.get("id") for s in fskills.get("base_skills", []) if isinstance(s, dict)},
        "tutorial": load_opt("config/tutorial_encounters.json"),
        "mercenary_ids": merc_ids,
        "status_ids": status_ids,
        "sprite_resolution": load_opt("_meta/sprite_resolution.json"),
    }


def main():
    ap = argparse.ArgumentParser(description="Validateur du bestiaire (lot L0 de l'audit de scalabilite).")
    ap.add_argument("--warn-only", action="store_true", help="rapporte tout mais sort toujours en 0")
    ap.add_argument("--strict", action="store_true", help="les categories WARNING deviennent ERROR")
    ap.add_argument("--client-root", help="checkout de kanarion_client pour verifier sprites et portraits")
    ap.add_argument("--no-client", action="store_true", help="ne pas chercher de client, meme voisin")
    ap.add_argument("--max-items", type=int, default=0, help="lignes listees par categorie (0 = toutes)")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    ctx = build_context()
    client = find_client(args.client_root, args.no_client)
    r = Report()
    check_monsters(r, ctx)
    check_loot(r, ctx)
    check_capture(r, ctx)
    check_archetypes(r, ctx)
    check_traces(r, ctx)
    check_rarities(r, ctx)
    check_generators(r, ctx)
    check_species(r, ctx)
    check_tutorial_gifts(r, ctx)
    check_affinities(r, ctx)
    check_assets(r, ctx, client)

    print("=" * 72)
    print("VALIDATION DU BESTIAIRE")
    print(f"  {len(ctx['monsters'])} monstres ({sum(1 for m in ctx['monsters'] if m.get('roster_status') == 'active')} actifs), "
          f"{len(ctx['species'])} especes, {len(ctx['family_roles'])} familles, "
          f"{len(ctx['archetypes'])} archetypes, {len(ctx['traces'])} empreintes")
    print(f"  client : {client or 'non fourni (assets verifies depuis la data seulement)'}")
    print("=" * 72)
    n_err = n_warn = 0
    for code in SEVERITY:
        sev = SEVERITY[code]
        if args.strict and sev == WARNING:
            sev = ERROR
        items = r.items.get(code, [])
        if not items:
            status = "PASS"
        elif sev == ERROR:
            status, n_err = "FAIL", n_err + len(items)
        else:
            status, n_warn = "WARN", n_warn + len(items)
        label = f"[{status}] {code} ({sev}) {TITLES[code]}"
        print(label + (f" : {len(items)}" if items else ""))
        shown = items if args.max_items <= 0 else items[:args.max_items]
        for it in shown:
            print(f"    - {it}")
        if len(shown) < len(items):
            print(f"    ... et {len(items) - len(shown)} autre(s) (--max-items 0 pour tout voir)")
        for it in r.info.get(code, []):
            print(f"    info : {it}")
    print("=" * 72)
    if n_err:
        print(f"VALIDATION FAILED - {n_err} erreur(s), {n_warn} avertissement(s)")
        if args.warn_only:
            print("(--warn-only : sortie 0 malgre les erreurs)")
            return 0
        return 1
    print(f"VALIDATION PASSED - 0 erreur, {n_warn} avertissement(s) (dette connue)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
