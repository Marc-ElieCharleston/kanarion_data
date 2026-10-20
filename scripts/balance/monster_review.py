"""Review table for the monster roster refactor (species x stage x archetype).

For every monster: species, stage prefix, role variant, current ai_role /
stat_archetype, PROPOSED archetype among the 11, target skill count by tier,
current skills, and flags to check by hand. Heuristic first pass, meant to be
reviewed and corrected in the CSV, then applied by a separate script.

Output: out/monster_review.csv. Read-only on the game data.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"

ARCHETYPES = ["tank", "gardien", "brute", "berserker", "assassin", "archer", "mage",
              "controleur", "soigneur", "invocateur", "enchanteur"]
# Skill count target (product 2026-10-02): tough is a stat tier, not a mechanic tier.
# Below lv40 (still near the village): normal 2, elite 3, boss 4. From lv40: normal 3
# (the 3rd = the archetype's identity effect, long cooldown, visible cast), elite 4,
# boss 4 + a phase mechanic.
SKILLS_BY_TIER = {"fodder": 2, "standard": 2, "tough": 2, "elite": 3, "boss": 4}
SKILLS_DEEP_LEVEL = 40
SKILLS_DEEP_BONUS = {"fodder": 1, "standard": 1, "tough": 1, "elite": 1, "boss": 0}
# Manual calls after looking at the client portraits (assets/icons/monsters, 2026-10-02).
OVERRIDES = {
    "mob_dark_priest": "controleur",       # hooded caster, red magic in hand: no healer look
    "mob_zealot_acolyte": "brute",         # no portrait; keep its current melee role
    "mob_goblin_witch": "controleur",      # no portrait; keep its current role
    "mob_converted_hunter": "archer",      # bow and quiver
    "mob_zealot_guard": "gardien",         # tower shield
    "mob_bell_guardian": "gardien",        # stone construct guarding the bell
}
# Stage prefixes: same role, stronger or weaker version of the species.
STAGES = {"jeune": 0.55, "larve": 0.55, "tutorial": 0.6, "small": 0.7, "alpha": 1.0, "geant": 1.5,
          "giant": 1.5, "ancient": 1.4, "lesser": 0.8, "corrupted": 1.2, "packleader": 1.3,
          "chief": 1.3, "warchief": 1.4, "warlord": 1.5, "king": 1.5, "queen": 1.5, "matron": 1.4}
# Role variants: name tokens that switch the archetype.
ROLE_TOKENS = {
    "soigneur": "soigneur", "soigneuse": "soigneur", "healer": "soigneur", "herbalist": "soigneur",
    "witch_doctor": "soigneur", "priest": "soigneur", "stitcher": "soigneur",
    "mage": "mage", "warlock": "mage", "witch": "mage", "scholar": "mage", "shaman": "enchanteur",
    "assassin": "assassin", "stalker": "assassin", "cutpurse": "assassin",
    "cuirasse": "tank", "juggernaut": "tank",
    "guard": "gardien", "sentinel": "gardien", "warden": "gardien", "banner_bearer": "enchanteur",
    "archer": "archer", "hunter": "archer", "crossbowman": "archer", "bomber": "archer",
    "caller": "invocateur", "summoner": "invocateur",
    "ritualist": "controleur", "acolyte": "enchanteur", "elder": "enchanteur",
    "berserker": "berserker", "frothing": "berserker", "enraged": "berserker", "wrathful": "berserker",
}
AI_ROLE_TO_ARCH = {"tank": "tank", "brute": "brute", "bruiser": "brute", "berserker": "berserker",
                   "assassin": "assassin", "caster": "mage", "controller": "controleur",
                   "tactician": "controleur", "healer": "soigneur", "support": "enchanteur"}
STOP = {"mob", "boss"}


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def skill_damage_types():
    """skill id -> damage_type, to split artillery into archer / mage."""
    out = {}
    s = load("skills/monster_skills.json")

    def walk(o):
        if isinstance(o, dict):
            if str(o.get("id", "")).startswith("skill_"):
                out[o["id"]] = o.get("damage_type", "")
                return
            for k, v in o.items():
                if not k.startswith("_"):
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(s)
    return out


def main():
    mons = load("entities/monsters.json")["monsters"]
    dtypes = skill_damage_types()
    usage = {}
    for rel in ["world/dungeons.json", "world/zones.json", "world/tower_floors.json", "systems/tower.json"]:
        txt = (ROOT / rel).read_text(encoding="utf-8")
        for m in mons:
            if f'"{m["id"]}"' in txt:
                usage.setdefault(m["id"], []).append(Path(rel).stem)

    rows = []
    for m in mons:
        mid = m["id"]
        tokens = [t for t in mid.split("_") if t not in STOP]
        joined = "_".join(tokens)
        species = tokens[0] if tokens else mid
        stage = next((t for t in tokens if t in STAGES), "")
        role_tok = next((k for k in sorted(ROLE_TOKENS, key=len, reverse=True) if k in joined), "")
        ai = m.get("ai_role", "")
        cur = m.get("stat_archetype", "")
        flags = []
        if role_tok:
            prop = ROLE_TOKENS[role_tok]
        elif ai == "artillery":
            phys = sum(dtypes.get(s) == "physical" for s in m.get("skills", []))
            mag = sum(dtypes.get(s) == "magical" for s in m.get("skills", []))
            prop = "archer" if phys > mag else "mage"
        else:
            prop = AI_ROLE_TO_ARCH.get(ai, cur or "brute")
        if mid in OVERRIDES:
            prop = OVERRIDES[mid]
            flags.append("manual")
        elif prop != AI_ROLE_TO_ARCH.get(ai, prop) and ai != "artillery":
            flags.append(f"role_from_name({role_tok})")
        if prop in ("gardien", "invocateur", "enchanteur", "soigneur", "berserker"):
            flags.append("archetype_new_or_split")
        tier = m.get("threat_tier", "standard")
        want = SKILLS_BY_TIER.get(tier, 2)
        if m.get("base_level", 1) >= SKILLS_DEEP_LEVEL:
            want += SKILLS_DEEP_BONUS.get(tier, 0)
        have = len(m.get("skills", []))
        if have != want:
            flags.append(f"skills {have}->{want}")
        generic = [s for s in m.get("skills", []) if s in ("skill_mob_bite", "skill_mob_slam", "skill_mob_slash",
                                                           "skill_mob_claw", "skill_mob_shoot")]
        if len(generic) == have and have:
            flags.append("only_generic_skills")
        if m.get("roster_status") == "active" and mid not in usage:
            flags.append("not_placed_anywhere")
        rows.append({
            "id": mid, "name_fr": m.get("name_fr", ""), "status": m.get("roster_status", ""),
            "category": m.get("category", ""), "species": species, "stage": stage,
            "stage_mult": STAGES.get(stage, 1.0), "role_variant": role_tok,
            "ai_role": ai, "stat_archetype_now": cur, "archetype_proposed": prop,
            "tier": tier, "base_level": m.get("base_level", 1),
            "skills_now": " ".join(m.get("skills", [])), "skills_target": want,
            "used_in": " ".join(usage.get(mid, [])), "flags": " ".join(flags),
        })
    OUT.mkdir(exist_ok=True)
    path = OUT / "monster_review.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} monsters -> {path}")


if __name__ == "__main__":
    main()
