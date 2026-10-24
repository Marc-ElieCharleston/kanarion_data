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

Exception a la regle 3 : le PRIX D'ACHAT (`buy_price`). Il ne vient que de
SHOP_BUY_PRICES (le rayon de Colette) : le script le pose sur les empreintes du
rayon et le retire des autres, y compris sur une entree deja presente. Changer
le rayon = changer SHOP_BUY_PRICES puis relancer le script.

Usage
-----
    python scripts/gen_familiar_traces.py            # ajoute ce qui manque
    python scripts/gen_familiar_traces.py --check    # ne touche rien, sort 1 si une
                                                     # empreinte manque ou si le contenu
                                                     # d'une empreinte presente differe
    python scripts/gen_familiar_traces.py --prune    # retire aussi les orphelines
"""
import json
import os
import sys
import unicodedata

# rarete -> (libelle FR, libelle EN). Le prix de revente vient de
# systems/npc_resale.json (familiar_traces), lu dans main().
RARITIES = [
    ("common", "Commun", "Common"),
    ("uncommon", "Peu Commun", "Uncommon"),
    ("rare", "Rare", "Rare"),
    ("epic", "Épique", "Epic"),
    ("legendary", "Légendaire", "Legendary"),
]

# role de familier -> (libelle FR, libelle EN)
ROLES = {
    "attaque": ("Attaque", "Attack"),
    "tank": ("Tank", "Tank"),
    "heal": ("Soin", "Healer"),
    "utilitaire": ("Utilitaire", "Utility"),
}

# Empreintes vendues par Colette (entities/npcs.json npc_familiar_breeder_colette,
# shop_inventory.empreintes) : seules a porter un prix d'achat. Le reste s'obtient
# uniquement par capture. Le meme rayon est le choix du familier de depart du
# tutoriel (config/familiar_balance.json tutorial_gift.from_shop).
# 2026-10-23 (decision Charleston, option C) : loup attaque, sanglier tank,
# scarabee soin, rat utilitaire.
SHOP_BUY_PRICES = {
    "empreinte_souffle_loup_attaque_common": 200,
    "empreinte_souffle_sanglier_tank_common": 200,
    "empreinte_souffle_scarabee_heal_common": 200,
    "empreinte_souffle_rat_utilitaire_common": 200,
}

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONSTERS = os.path.join(REPO, "entities", "monsters.json")
CONSUMABLES = os.path.join(REPO, "items", "consumables.json")
RESALE = os.path.join(REPO, "systems", "npc_resale.json")


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
    tid = f"empreinte_souffle_{fam}_{role}_{rar_id}"
    t = {
        "id": tid,
        "name_fr": f"Empreinte de Souffle - {ffr} {rfr} ({rar_fr})",
        "name_en": f"Breath Imprint - {fen} {ren} ({rar_en})",
        "description_fr": (f"Une empreinte de Souffle (voie {rfr}) capturée sur une créature "
                           f"de type {ffr}."),
        "description_en": (f"A Breath imprint ({ren} path) captured from a {fen} creature."),
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
    if tid in SHOP_BUY_PRICES:
        t["buy_price"] = SHOP_BUY_PRICES[tid]
    return t


def main():
    check = "--check" in sys.argv
    prune = "--prune" in sys.argv

    with open(CONSUMABLES, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    with open(RESALE, "r", encoding="utf-8") as fh:
        prix_par_rarete = json.load(fh)["familiar_traces"]
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
            for rar_id, rar_fr, rar_en in RARITIES:
                t = empreinte(fam, ffr, fen, role, rar_id, rar_fr, rar_en, prix_par_rarete[rar_id])
                voulues[t["id"]] = t

    a_ajouter = [t for i, t in voulues.items() if i not in par_id]
    # Exception a la regle 3 : buy_price suit SHOP_BUY_PRICES, meme sur une entree
    # presente (un objet qui sort du rayon perd son prix d'achat, un qui y entre le
    # recoit). Les libelles, eux, ne bougent jamais.
    prix_a_aligner = []
    for i, t in par_id.items():
        voulu = SHOP_BUY_PRICES.get(i)
        if t.get("buy_price") != voulu:
            prix_a_aligner.append((i, t.get("buy_price"), voulu))
    inconnus = sorted(set(SHOP_BUY_PRICES) - set(par_id) - set(voulues))
    if inconnus:
        print("ERREUR : SHOP_BUY_PRICES nomme des empreintes qui n'existent pas :", ", ".join(inconnus))
        return 1
    # Entrees presentes dont le contenu differe de ce que le script produirait.
    # Signalees seulement (regle 3 : le script ne reecrit pas une entree vivante),
    # mais elles font echouer --check : un ecart = la data ou le script a derive.
    def sans_prix(t):
        return {k: v for k, v in t.items() if k != "buy_price"}
    derivees = [i for i, t in voulues.items() if i in par_id and sans_prix(par_id[i]) != sans_prix(t)]
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

    if derivees:
        print(f"  {len(derivees)} empreinte(s) dont le contenu differe du script :")
        for i in derivees[:20]:
            cles = sorted(k for k in set(par_id[i]) | set(voulues[i])
                          if par_id[i].get(k) != voulues[i].get(k))
            print(f"    {i} : {', '.join(cles)}")

    if prix_a_aligner:
        print(f"  {len(prix_a_aligner)} prix d'achat a aligner sur SHOP_BUY_PRICES :")
        for i, avant, apres in prix_a_aligner:
            print(f"    {i} : {avant} -> {apres}")

    if check:
        ecart = (len(a_ajouter) + len(derivees) + len(prix_a_aligner)
                 + (len(orphelines) if prune else 0))
        if ecart:
            print("--check : le fichier n'est pas a jour")
            return 1
        print("--check : a jour")
        return 0

    if not a_ajouter and not prix_a_aligner and not (prune and orphelines):
        print("Rien a faire.")
        return 0

    for t in actuelles:
        i = t.get("id")
        if i in SHOP_BUY_PRICES:
            t["buy_price"] = SHOP_BUY_PRICES[i]
        else:
            t.pop("buy_price", None)

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
