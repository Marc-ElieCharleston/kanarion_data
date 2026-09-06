#!/usr/bin/env python3
"""Genere les empreintes de Souffle (familiar traces) dans items/consumables.json.

Modele courant : UNE empreinte par (famille, role, rarete).
    empreinte_souffle_<famille>_<role>_<rarete>

Ce que fait ce script
---------------------
Il LIT les familles et leurs roles dans `entities/monsters.json`
(`familiar_capture.family` + `familiar_capture.allowed_roles`, sur les monstres
dont `enabled` est vrai), et s'assure que chaque combinaison a ses 5 raretes.

Pourquoi il a ete reecrit (2026-09-05)
--------------------------------------
La version precedente portait sa propre liste `FAMILIES` en dur -- une COPIE de
ce que `monsters.json` declare deja -- et faisait `data["familiar_traces"] = traces`,
donc un remplacement total du tableau.

Les deux defauts se sont combines le 2026-09-05 : la data etait passee au modele
par role (420 empreintes) pendant que le script produisait encore l'ancien modele
par famille. Un simple `python scripts/gen_familiar_traces.py` a remplace les 420
entrees vivantes par 220 entrees mortes. Seule une reference cassee dans le loot du
rat tutoriel a fait remonter le probleme par la CI ; sans elle, la perte passait.

Trois regles en decoulent, et elles sont le coeur de ce fichier :

  1. AUCUNE liste de familles en dur. La source est `monsters.json`. Une liste
     recopiee finit toujours par deriver de son original.
  2. LE SCRIPT NE SUPPRIME RIEN par defaut. Une entree presente dans le fichier et
     absente de ce qu'il calcule est CONSERVEE et signalee. Il faut `--prune`, un
     geste explicite, pour la retirer.
  3. LES LIBELLES EXISTANTS NE BOUGENT PAS. Le nom d'une famille deja presente est
     relu depuis ses empreintes, jamais recalcule -- sinon une regeneration
     renommerait des objets deja dans les inventaires des joueurs.

Usage
-----
    python scripts/gen_familiar_traces.py            # ajoute ce qui manque
    python scripts/gen_familiar_traces.py --check    # ne touche rien, sort 1 si ecart
    python scripts/gen_familiar_traces.py --prune    # retire aussi les orphelines
"""
import json
import os
import sys
import unicodedata

# rarete -> (libelle FR, libelle EN, prix de vente)
RARITIES = [
    ("common", "Commun", "Common", 40),
    ("uncommon", "Peu Commun", "Uncommon", 70),
    ("rare", "Rare", "Rare", 120),
    ("epic", "Epique", "Epic", 400),
    ("legendary", "Legendaire", "Legendary", 1200),
]

# role de familier -> (libelle FR, libelle EN)
ROLES = {
    "attaque": ("Attaque", "Attack"),
    "tank": ("Tank", "Tank"),
    "heal": ("Soin", "Healer"),
    "utilitaire": ("Utilitaire", "Utility"),
}

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONSTERS = os.path.join(REPO, "entities", "monsters.json")
CONSUMABLES = os.path.join(REPO, "items", "consumables.json")


def sans_accents(s):
    """Les libelles d'empreinte sont sans accents (convention du fichier)."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def familles_depuis_les_monstres():
    """{famille: {"roles": [...], "fr": str, "en": str}} lu dans monsters.json.

    Le libelle vient du monstre qui porte la famille. Quand plusieurs la portent
    (mob_hyene et mob_alpha_hyena partagent `hyene`), on prend `mob_<famille>`
    s'il existe, sinon le moins haut niveau -- la forme de base de l'espece.
    """
    with open(MONSTERS, "r", encoding="utf-8") as fh:
        monstres = json.load(fh)["monsters"]

    porteurs = {}
    for m in monstres:
        cap = m.get("familiar_capture") or {}
        if not cap.get("enabled"):
            continue
        fam = cap.get("family", "")
        roles = [r for r in cap.get("allowed_roles", []) if r in ROLES]
        if not fam or not roles:
            continue
        porteurs.setdefault(fam, {"roles": set(), "mobs": []})
        porteurs[fam]["roles"].update(roles)
        porteurs[fam]["mobs"].append(m)

    out = {}
    for fam, info in porteurs.items():
        mobs = info["mobs"]
        exact = [m for m in mobs if m["id"] == "mob_" + fam]
        ref = exact[0] if exact else min(mobs, key=lambda m: m.get("base_level", 0))
        out[fam] = {
            "roles": sorted(info["roles"]),
            "fr": sans_accents(ref.get("name_fr", fam)),
            "en": ref.get("name_en", fam),
        }
    return out


def libelles_existants(traces):
    """{famille: (fr, en)} relu depuis les empreintes deja ecrites.

    Regle 3 : on ne renomme jamais une famille deja presente. Le libelle se
    retrouve en retirant le prefixe "Empreinte de Souffle - ", le role et la
    rarete du nom affiche.
    """
    out = {}
    for t in traces:
        fam, role = t.get("family"), t.get("role")
        if not fam or role not in ROLES or fam in out:
            continue
        rfr, ren = ROLES[role]
        try:
            fr = t["name_fr"].split(" - ", 1)[1].rsplit(" (", 1)[0]
            en = t["name_en"].split(" - ", 1)[1].rsplit(" (", 1)[0]
        except (KeyError, IndexError):
            continue
        if fr.endswith(" " + rfr) and en.endswith(" " + ren):
            out[fam] = (fr[: -len(rfr) - 1], en[: -len(ren) - 1])
    return out


def empreinte(fam, ffr, fen, role, rar_id, rar_fr, rar_en, prix):
    rfr, ren = ROLES[role]
    return {
        "id": f"empreinte_souffle_{fam}_{role}_{rar_id}",
        "name_fr": f"Empreinte de Souffle - {ffr} {rfr} ({rar_fr})",
        "name_en": f"Breath Imprint - {fen} {ren} ({rar_en})",
        "description_fr": (f"Une empreinte de Souffle (voie {rfr}) capturee sur une creature "
                           f"de type {ffr}. Apportez-la a Colette pour la faire incuber en familier."),
        "description_en": (f"A Breath imprint ({ren} path) captured from a {fen} creature. "
                           f"Bring it to Colette to incubate it into a familiar."),
        "rarity": rar_id,
        "item_type": "familiar_trace",
        "family": fam,
        "role": role,
        "trace_rarity": rar_id,
        # L'icone est partagee par voie et rarete (20 icones pour des centaines
        # d'ids) : le contrat "icone = id de l'item" est rompu ici a dessein.
        "icon": f"empreinte_{role}_{rar_id}",
        "effect": {"type": "familiar_trace_deposit", "value": 0},
        "tradeable": True,
        "hdv_listable": True,
        "stack_max": 99,
        "sell_price": prix,
    }


def main():
    check = "--check" in sys.argv
    prune = "--prune" in sys.argv

    with open(CONSUMABLES, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    actuelles = data.get("familiar_traces", [])
    par_id = {t["id"]: t for t in actuelles if "id" in t}

    familles = familles_depuis_les_monstres()
    connus = libelles_existants(actuelles)

    voulues = {}
    nouvelles_familles = []
    for fam, info in sorted(familles.items()):
        if fam in connus:
            ffr, fen = connus[fam]            # regle 3 : jamais de renommage
        else:
            ffr, fen = info["fr"], info["en"]
            nouvelles_familles.append((fam, ffr, fen))
        for role in info["roles"]:
            for rar_id, rar_fr, rar_en, prix in RARITIES:
                t = empreinte(fam, ffr, fen, role, rar_id, rar_fr, rar_en, prix)
                voulues[t["id"]] = t

    a_ajouter = [t for i, t in voulues.items() if i not in par_id]
    orphelines = [t for i, t in par_id.items() if i not in voulues]

    if nouvelles_familles:
        print("Nouvelles familles (libelle derive du monstre, verifiez-le) :")
        for fam, ffr, fen in nouvelles_familles:
            print(f"  {fam:26} -> {ffr} / {fen}")

    print(f"{len(familles)} familles capturables dans monsters.json")
    print(f"empreintes : {len(par_id)} presentes, {len(a_ajouter)} a ajouter, "
          f"{len(orphelines)} orpheline(s)")

    if orphelines:
        # Regle 2 : une orpheline n'est pas forcement morte. Trois familles
        # (chien_sauvage, scarabee_sables, serpent) ont des empreintes sans
        # monstre capturable, et les inventaires des joueurs peuvent en contenir.
        fams = sorted({t.get("family", "?") for t in orphelines})
        print("  orphelines (CONSERVEES, --prune pour les retirer) :", ", ".join(fams))

    if check:
        ecart = len(a_ajouter) + (len(orphelines) if prune else 0)
        if ecart:
            print("--check : le fichier n'est pas a jour")
            return 1
        print("--check : a jour")
        return 0

    if not a_ajouter and not (prune and orphelines):
        print("Rien a faire.")
        return 0

    finales = [t for t in actuelles
               if not (prune and t.get("id") in {o["id"] for o in orphelines})]
    finales.extend(a_ajouter)
    finales.sort(key=lambda t: (t.get("family", ""), t.get("role", ""),
                                [r[0] for r in RARITIES].index(t.get("trace_rarity", "common"))
                                if t.get("trace_rarity") in [r[0] for r in RARITIES] else 99))
    data["familiar_traces"] = finales

    # Mode texte : sous Windows, \n devient \r\n, ce qui preserve les fins de
    # ligne CRLF du depot. Ne pas passer en mode binaire ici.
    with open(CONSUMABLES, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    if prune and orphelines:
        print(f"Retire {len(orphelines)} orpheline(s).")
    print(f"Ecrit {len(finales)} empreintes dans {CONSUMABLES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
