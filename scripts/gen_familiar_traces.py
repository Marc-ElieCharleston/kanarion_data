#!/usr/bin/env python3
"""Deterministic generator for familiar trace items (Capture MVP).

Produces 29 families x 5 rarities = 145 trace items and merges them into
items/consumables.json under the top-level array key "familiar_traces"
(idempotent: the array is fully replaced if it already exists).

Trace item schema (per CAPTURE_MVP_SPEC.md):
  id            = empreinte_souffle_<family>_<rarity>
  effect        = {"type": "familiar_trace_deposit", "value": 0}
  item_type     = "familiar_trace"
  family        = <family>
  trace_rarity  = <rarity>
  rarity        = <rarity>
  tradeable     = true, hdv_listable = true, stack_max = 99
  sell_price    = common 40 / rare 120 / epic 400 / legendary 1200
  (no buy_price -- traces are looted / HDV only, never vendor-bought)

Run from anywhere:
  python scripts/gen_familiar_traces.py
"""
import json
import os

# 29 MVP families -> (FR label, EN label). The 3 sprite-less families
# (chien_sauvage, scarabee_sables, serpent) are intentionally EXCLUDED.
FAMILIES = [
    ("belier", "Belier", "Ram"),
    ("cerf_cauchemar", "Cerf Cauchemar", "Nightmare Stag"),
    ("cerf_obscur", "Cerf Obscur", "Dark Stag"),
    ("chargeur_abyssal", "Chargeur Abyssal", "Abyssal Charger"),
    ("cheval_cauchemar", "Cheval Cauchemar", "Nightmare Horse"),
    ("cheval_sauvage", "Cheval Sauvage", "Wild Horse"),
    ("chien_braise", "Chien de Braise", "Ember Hound"),
    ("chien_vide", "Chien du Vide", "Void Hound"),
    ("corbeau", "Corbeau", "Crow"),
    ("demon_mineur", "Demon Mineur", "Lesser Demon"),
    ("gardien_cloche", "Gardien Cloche", "Bell Guardian"),
    ("golem", "Golem", "Golem"),
    ("golem_runique", "Golem Runique", "Runic Golem"),
    ("hybride_sanglier_loup", "Hybride Sanglier-Loup", "Boar-Wolf Hybrid"),
    ("hyene", "Hyene", "Hyena"),
    ("loup", "Loup", "Wolf"),
    ("loup_cristal", "Loup de Cristal", "Crystal Wolf"),
    ("loup_spectral", "Loup Spectral", "Spectral Wolf"),
    ("rat", "Rat", "Rat"),
    ("renard_brumeux", "Renard Brumeux", "Misty Fox"),
    ("sanglier", "Sanglier", "Boar"),
    ("scarabee", "Scarabee", "Beetle"),
    ("scorpion", "Scorpion", "Scorpion"),
    ("squelette", "Squelette", "Skeleton"),
    ("squelette_necromancien", "Squelette Necromancien", "Skeleton Necromancer"),
    ("tatou", "Tatou", "Armadillo"),
    ("taureau", "Taureau", "Bull"),
    ("tortue_pierre", "Tortue de Pierre", "Stone Turtle"),
    ("traqueur_faille", "Traqueur de Faille", "Rift Stalker"),
]

# rarity_id -> (FR label, EN label, sell_price)
RARITIES = [
    ("common", "Commun", "Common", 40),
    ("uncommon", "Peu commun", "Uncommon", 70),
    ("rare", "Rare", "Rare", 120),
    ("epic", "Epique", "Epic", 400),
    ("legendary", "Legendaire", "Legendary", 1200),
]


def build_traces():
    traces = []
    for fam_id, fam_fr, fam_en in FAMILIES:
        for rar_id, rar_fr, rar_en, sell in RARITIES:
            traces.append({
                "id": f"empreinte_souffle_{fam_id}_{rar_id}",
                "name_fr": f"Empreinte de Souffle - {fam_fr} ({rar_fr})",
                "name_en": f"Breath Imprint - {fam_en} ({rar_en})",
                "description_fr": (
                    f"Une empreinte vivante capturee sur une creature de type "
                    f"{fam_fr}. Apportez-la a Colette pour la faire incuber en familier."
                ),
                "description_en": (
                    f"A living imprint captured from a {fam_en} creature. "
                    f"Bring it to Colette to incubate it into a familiar."
                ),
                "rarity": rar_id,
                "item_type": "familiar_trace",
                "family": fam_id,
                "trace_rarity": rar_id,
                "effect": {"type": "familiar_trace_deposit", "value": 0},
                "tradeable": True,
                "hdv_listable": True,
                "stack_max": 99,
                "sell_price": sell,
            })
    return traces


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo_root, "items", "consumables.json")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    traces = build_traces()
    assert len(traces) == len(FAMILIES) * len(RARITIES) == 145, len(traces)

    # Idempotent: replace the array if present, else append as last key.
    data["familiar_traces"] = traces

    # Text mode on Windows translates \n -> \r\n, preserving CRLF endings.
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"Wrote {len(traces)} familiar_traces to {path}")
    by_rar = {}
    for t in traces:
        by_rar[t["trace_rarity"]] = by_rar.get(t["trace_rarity"], 0) + 1
    print("By rarity:", by_rar)


if __name__ == "__main__":
    main()
