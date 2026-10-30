#!/usr/bin/env python3
"""Generateur deterministe des parchemins d'emote (items/emote_scrolls.json).

Decision Charleston du 2026-10-23 : les emotes payantes ne se vendent plus en
diamants. Chaque emote premium de ui/emotes.json devient un OBJET, le parchemin
d'emote, qui tombe dans les coffres, aux evenements et rarement en combat. On
l'utilise (l'emote est apprise pour tout le compte) ou on le revend / l'echange
(hotel des ventes, echange direct).

SOURCE DE VERITE
----------------
Ce script est la source de verite de items/emote_scrolls.json. Le fichier JSON
est un PRODUIT : un texte, un prix ou un champ se corrige ICI, puis on regenere.

Entrees :
  - ui/emotes.json : les emotes (id, nom FR/EN, pack, tier, icone). Une emote
    `tier: premium` = un parchemin. Les emotes offertes n'en ont pas.
  - items/loot_tables.json `emote_scroll_drops` : rarete par pack et prix de
    revente au PNJ par rarete. Les chances de drop vivent dans ce meme bloc et ne
    sont PAS recopiees ici (le serveur les lit la-bas).

Schema d'un parchemin :
  id           = scroll_emote_<emote_id>
  item_type    = "emote_scroll"
  emote_id     = l'emote apprise (aussi dans effect.emote_id, que lit le serveur)
  effect       = {"type": "unlock_emote", "emote_id": <id>}
  icon         = l'icone de l'emote (assets/icons/ui/emotes/<icon>.png cote client)
  global_pool  = false si l'emote a une source PRECISE (ui/emotes.json source.kind autre
                 que "global") : le parchemin sort du tirage global (coffres, evenements,
                 combats) et ne tombe que de sa source, sinon "Se trouve : X" serait faux.
                 Lu par shared/gameplay/emote_scrolls.hpp. Absent = true.

Lot 2 (2026-10-30) :
  - `rarity` sur l'emote remplace la rarete de son pack ;
  - `scroll: false` = emote liee au compte (hauts faits) : aucun parchemin.

Usage :
  python scripts/gen_emote_scrolls.py            # regenere items/emote_scrolls.json
  python scripts/gen_emote_scrolls.py --check    # sort 1 si le fichier n'est pas a jour
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EMOTES = ROOT / "ui" / "emotes.json"
LOOT = ROOT / "items" / "loot_tables.json"
OUT = ROOT / "items" / "emote_scrolls.json"

PREFIX = "scroll_emote_"
STACK_MAX = 99


def load(path: pathlib.Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build() -> dict:
    emotes = load(EMOTES).get("emotes", [])
    block = load(LOOT)["emote_scroll_drops"]
    rarity_by_pack = block["rarity_by_pack"]
    prices = block["sell_price_by_rarity"]

    scrolls = []
    for e in emotes:
        if e.get("tier") != "premium" or e.get("scroll") is False:
            continue
        eid = e["id"]
        pack = e.get("pack", "")
        rarity = e.get("rarity") or rarity_by_pack.get(pack)
        if rarity is None:
            raise SystemExit(f"emote '{eid}' : ni rarity, ni pack '{pack}' dans emote_scroll_drops.rarity_by_pack")
        if rarity not in prices:
            raise SystemExit(f"emote '{eid}' : rarete '{rarity}' sans prix dans sell_price_by_rarity")
        source_kind = (e.get("source") or {}).get("kind", "global")
        name_fr, name_en = e["name_fr"], e["name_en"]
        scroll = {
            "id": PREFIX + eid,
            "name_fr": f"Parchemin d'emote : {name_fr}",
            "name_en": f"Emote Scroll: {name_en}",
            "description_fr": f"Apprend l'emote « {name_fr} » à tout ton compte. "
                              f"Se revend et s'échange entre joueurs.",
            "description_en": f"Teaches the \"{name_en}\" emote to your whole account. "
                              f"Can be sold and traded between players.",
            "item_type": "emote_scroll",
            "emote_id": eid,
            "pack": pack,
            "rarity": rarity,
            "icon": e.get("icon") or f"emote_{eid}",
            "effect": {"type": "unlock_emote", "emote_id": eid},
            "tradeable": True,
            "hdv_listable": True,
            "stack_max": STACK_MAX,
            "sell_price": prices[rarity],
        }
        if source_kind != "global":
            scroll["global_pool"] = False
        scrolls.append(scroll)

    return {
        "_meta": {
            "version": "1.0",
            "last_updated": "2026-10-30",
            "description": "Parchemins d'emote (decision Charleston 2026-10-23). Un parchemin par emote "
                           "premium de ui/emotes.json. L'utiliser apprend l'emote a tout le compte "
                           "(serveur : economy USE_ITEM effet unlock_emote, refuse sans rien consommer "
                           "si l'emote est deja possedee). Echangeable, vendable a l'hotel des ventes et "
                           "au PNJ. Chances de drop : items/loot_tables.json emote_scroll_drops. global_pool:false = "
                           "parchemin a source precise (lot 2), hors du tirage global.",
            "generated_by": "scripts/gen_emote_scrolls.py",
            "count": len(scrolls),
        },
        "emote_scrolls": scrolls,
    }


def dump(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    doc = build()
    if "--check" in sys.argv:
        if not OUT.exists() or load(OUT) != doc:
            print(f"{OUT.relative_to(ROOT)} n'est pas a jour : lancer python scripts/gen_emote_scrolls.py")
            return 1
        print(f"{OUT.relative_to(ROOT)} a jour ({doc['_meta']['count']} parchemins)")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(doc))
    print(f"{OUT.relative_to(ROOT)} : {doc['_meta']['count']} parchemins ecrits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
