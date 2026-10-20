"""Arbre des passifs V2 : genere classes/passive_tree.json (l'arbre que lisent le serveur et le client).

Source unique : ce script. Pour retoucher un noeud, modifier son contenu ici puis relancer :
    python -I _meta/conception_passifs/gen_arbre_v2.py          (depuis la racine de la base)
    python -I _meta/conception_passifs/sim_arbre_v2.py classes/passive_tree.json
    python scripts/validate_passive_tree.py

Gabarit : le bras Attaque ecrit par le proprietaire (arbre_v2_attaque.json). Chaque bras reprend
exactement ses emplacements (rangs, couts, aretes), donc chaque notable tombe a la meme distance du
centre (15 / 30 / 50 / 75).

Integration 2026-10-20 (retour de test 0.20 : « il manque la 6e branche, et aucune branche ne donne de
MAG ou un peu d'ATK au debut ») :
  - 6e bras : Arcanes (MAG, penetration magique, Souffle, incantation), place entre Soin et Soutien ;
    les deux ponts d'Attaque ecrits par le proprietaire restent en place. A VALIDER.
  - chaque bras qui ne commence pas deja par ATK ou MAG recoit une « graine » : un petit noeud de
    3 rangs relie au centre seul (feuille, hors du chemin, donc les distances ne bougent pas). A VALIDER.
  - UNIQUEMENT des stats et des mecaniques deja branchees cote combat (passive_tree_mechanics.hpp) :
    les noeuds dont la mecanique V2 n'existe pas encore sont remplaces par des stats, gardent leur id
    (et leur icone), et portent `to_validate` + `v2_planned` (la mecanique prevue, pour plus tard).
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "classes", "passive_tree.json")
src = json.load(open(os.path.join(HERE, "arbre_v2_attaque.json"), encoding="utf-8"))

SCALE = 46  # unites du gabarit -> unites de dessin (le client dessine pos tel quel)

# Emplacement du gabarit -> cle du noeud d'Attaque qui l'occupe.
SLOTS = {
    "e1": "force", "e2": "eye", "e3": "edge", "e4": "aim",
    "n15a": "execution", "n15b": "first_blood", "side15": "reach",
    "ra1": "grip", "ra2": "lynx", "rb1": "vigor", "rb2": "ferocity",
    "n30a": "killer_instinct", "n30b": "breach", "n30c": "momentum",
    "rc1": "lethality", "rc2": "weak_point", "rc3": "steady",
    "rd1": "carnage", "rd2": "raw_power", "rd3": "perforation",
    "n50a": "relentless", "n50b": "guardbreaker", "side50": "bloodlust",
    "m1": "m_carnage", "m2": "m_lethal", "m3": "m_power",
    "megaa": "mega_fatal", "megab": "mega_unleashed",
}
GROUPS = {"n15": ("n15a", "n15b"), "n30": ("n30a", "n30b", "n30c"), "n50": ("n50a", "n50b"),
          "mega": ("megaa", "megab")}
ATK = {n["id"]: n for n in src["nodes"]}
SLOT_OF = {f"pt2_atk_{v}": k for k, v in SLOTS.items()}


# ---------------------------------------------------------------------------------------------
# Effets
# ---------------------------------------------------------------------------------------------
def flat(stat, v):
    return {"stat": stat, "op": "add_flat", "value_per_rank": v}


def pct(stat, v):
    return {"stat": stat, "op": "add_percent", "value_per_rank": v}


def once(stat, v, op="add_flat"):
    return {"stat": stat, "op": op, "value": v}


def mech(name, **params):
    return {"mechanic": name, "params": params}


# Libelles des stats : (FR forme « +X <...> », FR forme « +X % de <...> », EN, unite)
# unite "pct" : la stat est deja un pourcentage (+X % de ...) ; "flat" : nombre (+X ...).
STAT_TEXT = {
    "atk": ("attaque", "d'attaque", "attack", "flat"),
    "mag": ("magie", "de magie", "magic", "flat"),
    "crit": (None, "de chance critique", "critical chance", "pct"),
    "crit_dmg": ("dégâts critiques", "de dégâts critiques", "critical damage", "flat"),
    "hit": ("précision", "de précision", "accuracy", "flat"),
    "damage_percent": (None, "de dégâts infligés", "damage dealt", "pct"),
    "armor_pen": ("pénétration d'armure", "de pénétration d'armure", "armor penetration", "flat"),
    "magic_pen": ("pénétration magique", "de pénétration magique", "magic penetration", "flat"),
    "armor": ("armure", "d'armure", "armor", "flat"),
    "magic_resist": ("résistance magique", "de résistance magique", "magic resistance", "flat"),
    "hp": ("PV max", "de PV max", "max HP", "flat"),
    "mp": ("Souffle max", "de Souffle max", "max Breath", "flat"),
    "flee": ("esquive", "d'esquive", "evasion", "flat"),
    "parry_chance": (None, "de chance de parade", "parry chance", "pct"),
    "block_chance": (None, "de chance de blocage", "block chance", "pct"),
    "lifesteal": (None, "de vol de vie", "lifesteal", "pct"),
    "spell_vamp": (None, "de vol de sort", "spell vamp", "pct"),
    "damage_reduction": (None, "de réduction des dégâts subis", "damage reduction", "pct"),
    "effect_resist": ("résistance aux effets", "de résistance aux effets", "effect resistance", "flat"),
    "tenacity": ("ténacité", "de ténacité", "tenacity", "flat"),
    "hp_regen": ("régénération de PV", "de régénération de PV", "HP regeneration", "flat"),
    "mp_regen": ("Souffle par seconde", "de régénération de Souffle", "Breath per second", "flat"),
    "heal_power": (None, "de puissance de soin", "healing power", "pct"),
    "healing_received": (None, "de soins reçus", "healing received", "pct"),
    "shield_power": (None, "de puissance de bouclier", "shield power", "pct"),
    "cast_speed": (None, "de vitesse d'incantation", "cast speed", "pct"),
    "cooldown_reduction": (None, "de réduction de recharge", "cooldown reduction", "pct"),
    "buff_duration": (None, "de durée des améliorations", "buff duration", "pct"),
    "debuff_duration": (None, "de durée des affaiblissements", "debuff duration", "pct"),
    "effect_chance": (None, "de chance d'effet", "effect chance", "pct"),
}


def num_fr(v):
    s = f"{abs(v):g}"
    return s.replace(".", ",")


def num_en(v):
    return f"{abs(v):g}"


def stat_phrase(e):
    """(fr, en) d'un effet de stat, signe compris."""
    stat, op = e["stat"], e["op"]
    v = e.get("value_per_rank", e.get("value"))
    fr_flat, fr_pct, en, unit = STAT_TEXT[stat]
    sign = "+" if v >= 0 else "-"
    if stat == "thorns":
        return (f"renvoie {num_fr(v)} % des dégâts subis à l'attaquant",
                f"reflects {num_en(v)}% of the damage taken to the attacker")
    if stat == "damage_reduction" and v < 0:
        return f"+{num_fr(v)} % de dégâts subis", f"+{num_en(v)}% damage taken"
    if op == "add_percent" or unit == "pct":
        return f"{sign}{num_fr(v)} % {fr_pct}", f"{sign}{num_en(v)}% {en}"
    return f"{sign}{num_fr(v)} {fr_flat}", f"{sign}{num_en(v)} {en}"


STAT_TEXT["thorns"] = (None, None, None, "pct")


def join(parts, word):
    if len(parts) <= 1:
        return "".join(parts)
    return ", ".join(parts[:-1]) + f" {word} " + parts[-1]


def cap_first(s):
    return s[:1].upper() + s[1:]


def describe(effects, per_rank, mech_text=None, malus=()):
    """Description FR/EN generee depuis les effets (texte honnete par construction).
    mech_text : (fr, en) des effets de mecanique, places en tete. malus : indices des effets
    de stat qui forment la contrepartie."""
    stat_effects = [e for e in effects if "stat" in e]
    good = [stat_phrase(e) for i, e in enumerate(stat_effects) if i not in malus]
    bad = [stat_phrase(e) for i, e in enumerate(stat_effects) if i in malus]
    fr_parts, en_parts = [], []
    if mech_text:
        fr_parts.append(mech_text[0].rstrip("."))
        en_parts.append(mech_text[1].rstrip("."))
    if good:
        fr_parts.append(cap_first(join([p[0] for p in good], "et")) + (" par rang" if per_rank else ""))
        en_parts.append(cap_first(join([p[1] for p in good], "and")) + (" per rank" if per_rank else ""))
    fr = ". ".join(fr_parts) + "."
    en = ". ".join(en_parts) + "."
    if bad:
        fr += " Contrepartie : " + join([p[0] for p in bad], "et") + "."
        en += " Trade-off: " + join([p[1] for p in bad], "and") + "."
    return fr, en


# ---------------------------------------------------------------------------------------------
# Contenu. Chaque emplacement -> dict(key, fr, en, effects, [mech=(fr, en)], [malus=(i,..)],
#                                     [to_validate=str], [v2_planned=str]).
# Regles : fixe a l'entree, % en profondeur ; jamais de % sur une stat dont la base vaut 0.
# Mecaniques : SEULEMENT celles du catalogue MECHANICS (branchees en combat).
# ---------------------------------------------------------------------------------------------
def N(key, fr, en, effects, **kw):
    return dict(key=key, fr=fr, en=en, effects=effects, **kw)


SUB = "mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider)"

# Bras Attaque : contenu du proprietaire (arbre_v2_attaque.json) ; seuls les noeuds dont la mecanique
# n'existe pas en combat sont remplaces, et les textes sont regeneres (accents, anglais).
ATTACK = {
    "e1": N("force", "Force", "Might", None),
    "e2": N("eye", "Œil vif", "Keen Eye", None),
    "e3": N("edge", "Tranchant", "Edge", None),
    "e4": N("aim", "Visée", "Aim", None),
    "n15a": N("execution", "Exécution", "Execution", None,
              mech=("+15 % de dégâts contre une cible sous 30 % de ses PV.",
                    "+15% damage against a target below 30% HP.")),
    "n15b": N("first_blood", "Premier sang", "First Blood", [once("crit", 6), once("crit_dmg", 10)],
              to_validate=SUB, v2_planned="damage_vs_target_hp_above : +20 % de degats contre une cible au-dessus de 90 % de ses PV"),
    "side15": N("reach", "Allonge", "Reach", None,
                mech=("+1 portée à tes sorts offensifs dont la portée de base est d'au moins 3.",
                      "+1 range to your offensive spells whose base range is at least 3.")),
    "ra1": N("grip", "Poigne", "Firm Grip", None),
    "ra2": N("lynx", "Œil de lynx", "Lynx Eye", None),
    "rb1": N("vigor", "Vigueur", "Vigor", None),
    "rb2": N("ferocity", "Férocité", "Ferocity", None),
    "n30a": N("killer_instinct", "Lame : instinct du tueur", "Blade: Killer Instinct", None,
              mech=("Après un coup critique : +10 % de chance critique pendant 3 s.",
                    "After a critical hit: +10% critical chance for 3 s.")),
    "n30b": N("breach", "Brute : percée", "Brute: Breach", None),
    "n30c": N("momentum", "Cadence : élan", "Cadence: Momentum", [once("cast_speed", 8), once("damage_percent", 4)],
              to_validate=SUB, v2_planned="stacking_stat_on_event : chaque sort lance donne +2 % de degats pendant 6 s, cumulable 5 fois"),
    "rc1": N("lethality", "Létalité", "Lethality", None),
    "rc2": N("weak_point", "Point faible", "Weak Point", None),
    "rc3": N("steady", "Main sûre", "Steady Hand", None),
    "rd1": N("carnage", "Carnage", "Carnage", None),
    "rd2": N("raw_power", "Puissance brute", "Raw Power", None),
    "rd3": N("perforation", "Perforation", "Perforation", None),
    "n50a": N("relentless", "Acharnement", "Relentless", [once("damage_percent", 10)],
              to_validate=SUB, v2_planned="consecutive_hit_stacks : +4 % par coup sur la meme cible, 5 cumuls"),
    "n50b": N("guardbreaker", "Brise-garde", "Guardbreaker", [once("armor_pen", 12), once("magic_pen", 12)],
              to_validate=SUB, v2_planned="crit_ignores_defense : les crits ignorent 30 % de l'armure et de la resistance magique"),
    "side50": N("bloodlust", "Soif de sang", "Bloodlust", [once("lifesteal", 6), once("spell_vamp", 6)],
                to_validate=SUB, v2_planned="stat_window_after_event kill : +15 % de degats pendant 5 s apres un ennemi tue"),
    "m1": N("m_carnage", "Maîtrise : carnage", "Mastery: Carnage", None),
    "m2": N("m_lethal", "Maîtrise : coup mortel", "Mastery: Deadly Blow", None),
    "m3": N("m_power", "Maîtrise : puissance", "Mastery: Power", None),
    "megaa": N("mega_fatal", "Coup Fatal", "Fatal Strike",
               [once("crit_dmg", 50),
                mech("cooldown_reduction_on_event", event="crit", seconds=1, scope="cast_skill", internal_cooldown_s=0),
                once("damage_percent", -10)],
               mech=("Tes coups critiques réduisent de 1 s la recharge du sort lancé.",
                     "Your critical hits reduce the cooldown of the cast spell by 1 s."),
               malus=(1,), to_validate="contrepartie : -10 % de degats infliges au lieu de -15 % sur les coups non critiques (non_crit_damage_modifier pas branche)",
               v2_planned="non_crit_damage_modifier : -15 % de degats sur les coups non critiques"),
    "megab": N("mega_unleashed", "Déchaînement", "Unleashed", None, malus=(1, 2)),
}

ARMS = {}
ARMS["defense"] = ("def", {
    "e1": N("hide", "Peau dure", "Thick Hide", [flat("armor", 2)]),
    "e2": N("constitution", "Constitution", "Constitution", [flat("hp", 12)]),
    "e3": N("calm", "Esprit calme", "Calm Mind", [flat("magic_resist", 2)]),
    "e4": N("light_step", "Pas léger", "Light Step", [flat("flee", 1)]),
    "n15a": N("iron_skin", "Peau de fer", "Iron Skin",
              [mech("damage_taken_reduction_conditional", condition="area_attack", reduction_pct=15)],
              mech=("-15 % de dégâts reçus des attaques de zone.", "-15% damage taken from area attacks.")),
    "n15b": N("hold_position", "Position tenue", "Hold Position",
              [mech("damage_taken_reduction_conditional", condition="stationary_3s", reduction_pct=10)],
              mech=("Si tu ne t'es pas déplacé depuis 3 s : -10 % de dégâts reçus.",
                    "If you have not moved for 3 s: -10% damage taken.")),
    "side15": N("composure", "Sang-froid", "Composure",
                [mech("damage_taken_reduction_conditional", condition="attacker_beyond_3_tiles", reduction_pct=12)],
                mech=("-12 % de dégâts reçus des ennemis à plus de 3 cases.",
                      "-12% damage taken from enemies more than 3 tiles away.")),
    "ra1": N("rampart", "Rempart", "Rampart", [flat("armor", 3), flat("magic_resist", 3)]),
    "ra2": N("robust", "Robustesse", "Robustness", [flat("hp", 15)]),
    "rb1": N("bastion", "Bastion", "Bastion", [pct("hp", 2)]),
    "rb2": N("plating", "Carapace", "Plating", [pct("armor", 2), pct("magic_resist", 2)]),
    "n30a": N("guard", "Garde : parade", "Guard: Parry", [once("parry_chance", 8), once("block_chance", 8)]),
    "n30b": N("retaliation", "Représailles : épines", "Retaliation: Thorns", [once("thorns", 15)]),
    "n30c": N("vampire", "Endurance : vampirisme", "Endurance: Vampirism", [once("lifesteal", 6), once("spell_vamp", 6)]),
    "rc1": N("endurance", "Endurance", "Endurance", [flat("damage_reduction", 1)]),
    "rc2": N("resilience", "Résilience", "Resilience", [flat("effect_resist", 2)]),
    "rc3": N("anchor", "Ancrage", "Anchor", [flat("tenacity", 2)]),
    "rd1": N("scales", "Écailles", "Scales", [pct("armor", 2), pct("magic_resist", 2)]),
    "rd2": N("colossus", "Colosse", "Colossus", [pct("hp", 2)]),
    "rd3": N("regrowth", "Régénération", "Regrowth", [pct("hp_regen", 5)]),
    "n50a": N("unshakable", "Inébranlable", "Unshakable",
              [mech("shield_on_low_hp", hp_pct=30, shield_pct_max_hp=20, internal_cooldown_s=45)],
              mech=("Sous 30 % de PV : bouclier égal à 20 % de tes PV max. Une fois toutes les 45 s.",
                    "Below 30% HP: a shield equal to 20% of your max HP. Once every 45 s.")),
    "n50b": N("last_stand", "Dernier rempart", "Last Stand", [once("damage_reduction", 6)],
              to_validate=SUB, v2_planned="damage_taken_reduction_conditional hp_below : sous 30 % de PV, -20 % de degats subis"),
    "side50": N("living_wall", "Mur vivant", "Living Wall", [once("block_chance", 6), once("parry_chance", 4)],
                to_validate=SUB, v2_planned="stat_window_after_event block_or_parry : -20 % de degats subis pendant 3 s"),
    "m1": N("m_bastion", "Maîtrise : bastion", "Mastery: Bastion", [pct("hp", 2)]),
    "m2": N("m_armor", "Maîtrise : cuirasse", "Mastery: Cuirass", [pct("armor", 2), pct("magic_resist", 2)]),
    "m3": N("m_endurance", "Maîtrise : endurance", "Mastery: Endurance", [flat("damage_reduction", 1)]),
    "megaa": N("mega_fortress", "Forteresse", "Fortress",
               [once("hp", 30, "add_percent"), once("damage_reduction", 15), once("damage_percent", -25)], malus=(2,)),
    "megab": N("mega_titan", "Colère du titan", "Titan's Wrath",
               [once("thorns", 30), once("lifesteal", 10), once("damage_reduction", -15), once("healing_received", -25)],
               malus=(2, 3)),
})

ARMS["healing"] = ("heal", {
    "e1": N("warm_hands", "Mains chaudes", "Warm Hands", [flat("heal_power", 2)]),
    "e2": N("sap", "Sève", "Sap", [flat("mp", 10)]),
    "e3": N("grace", "Grâce", "Grace", [flat("healing_received", 2)]),
    "e4": N("focus", "Concentration", "Focus", [flat("mag", 2)]),
    "n15a": N("helping_hand", "Main secourable", "Helping Hand",
              [mech("heal_bonus_target_hp_below", hp_pct=40, heal_pct=20)],
              mech=("+20 % de soin sur un allié sous 40 % de ses PV.", "+20% healing on an ally below 40% HP.")),
    "n15b": N("prevention", "Soins préventifs", "Preventive Care", [once("heal_power", 6), once("shield_power", 6)],
              to_validate=SUB, v2_planned="heal_bonus_target_hp_above : +15 % de soins sur une cible au-dessus de 70 % de ses PV"),
    "side15": N("extended_heal", "Soin étendu", "Extended Heal",
                [mech("heal_splash_nearest_ally", ratio_pct=30, skill_filter="single_target_heal")],
                mech=("Tes soins mono-cible soignent aussi l'allié le plus proche de la cible, à 30 %.",
                      "Your single-target heals also heal the ally closest to the target, at 30%.")),
    "ra1": N("fervor", "Ferveur", "Fervor", [flat("heal_power", 3)]),
    "ra2": N("reserve", "Réserve", "Reserve", [flat("mp", 12)]),
    "rb1": N("wisdom", "Sagesse", "Wisdom", [pct("mag", 2)]),
    "rb2": N("aegis_craft", "Art du bouclier", "Shieldcraft", [flat("shield_power", 2)]),
    "n30a": N("transfusion", "Transfusion", "Transfusion", [mech("heal_return_to_caster", ratio_pct=10)],
              mech=("10 % des soins que tu donnes te reviennent.", "10% of the healing you give comes back to you.")),
    "n30b": N("spell_vamp", "Vol de sort", "Spell Vamp", [once("spell_vamp", 8)]),
    "n30c": N("holy_shield", "Égide sacrée", "Holy Aegis", [once("shield_power", 15), once("healing_received", 10)]),
    "rc1": N("quick_prayer", "Prière rapide", "Quick Prayer", [flat("cast_speed", 2)]),
    "rc2": N("perseverance", "Persévérance", "Perseverance", [flat("cooldown_reduction", 1)]),
    "rc3": N("devotion", "Recueillement", "Devotion", [flat("healing_received", 2)]),
    "rd1": N("divine_grace", "Grâce divine", "Divine Grace", [pct("mag", 2)]),
    "rd2": N("fountain", "Fontaine", "Fountain", [pct("mp", 3)]),
    "rd3": N("radiance", "Rayonnement", "Radiance", [flat("shield_power", 3)]),
    "n50a": N("last_breath", "Dernier souffle", "Last Breath", [mech("prevent_ally_death", heal_pct=25, per_combat=1)],
              mech=("Une fois par combat, un allié qui devrait mourir reste à 1 PV puis reçoit un soin de 25 % de ses PV max.",
                    "Once per combat, an ally who should die stays at 1 HP then is healed for 25% of their max HP.")),
    "n50b": N("downpour", "Ondée", "Downpour",
              [mech("heal_splash_nearest_ally", ratio_pct=45, skill_filter="single_target_heal")],
              mech=("Tes soins mono-cible soignent aussi l'allié le plus proche de la cible, à 45 % (ne s'ajoute pas à Soin étendu : le plus fort compte).",
                    "Your single-target heals also heal the ally closest to the target, at 45% (does not add to Extended Heal: the stronger one applies)."),
              to_validate="un seul allie (la V2 en prevoyait 2 a 25 % : parametre count pas branche)",
              v2_planned="heal_splash_nearest_ally count=2 ratio 25"),
    "side50": N("prayer", "Prière de combat", "Battle Prayer", [once("cast_speed", 4), once("heal_power", 6)],
                to_validate=SUB, v2_planned="stacking_stat_on_event heal_cast : +3 % de puissance de soin par soin, 5 cumuls, 6 s"),
    "m1": N("m_heal", "Maîtrise : soins", "Mastery: Healing", [flat("heal_power", 2)]),
    "m2": N("m_wisdom", "Maîtrise : sagesse", "Mastery: Wisdom", [pct("mag", 2)]),
    "m3": N("m_source", "Maîtrise : source", "Mastery: Source", [pct("mp", 3)]),
    "megaa": N("mega_sanctuary", "Sanctuaire", "Sanctuary",
               [once("heal_power", 30), once("buff_duration", 25), once("damage_percent", -30)], malus=(2,)),
    "megab": N("mega_martyr", "Martyr", "Martyr",
               [once("heal_power", 40), once("healing_received", 20), once("hp", -20, "add_percent")], malus=(2,)),
})

# 6e bras (2026-10-20, A VALIDER en entier) : la magie pure. Valeurs calquees sur Attaque.
ARMS["arcane"] = ("arc", {
    "e1": N("lore", "Savoir", "Lore", [flat("mag", 3)]),
    "e2": N("flow", "Flux", "Flow", [flat("mp", 10)]),
    "e3": N("arcane_pierce", "Perce-arcane", "Arcane Pierce", [flat("magic_pen", 1.5)]),
    "e4": N("focusing", "Focalisation", "Focusing", [flat("crit", 1)]),
    "n15a": N("arcane_power", "Puissance arcanique", "Arcane Power", [once("mag", 8, "add_percent")]),
    "n15b": N("quick_casting", "Incantation vive", "Quick Casting", [once("cast_speed", 8)]),
    "side15": N("piercing_mind", "Esprit perçant", "Piercing Mind", [once("magic_pen", 6)]),
    "ra1": N("erudition", "Érudition", "Erudition", [flat("mag", 3)]),
    "ra2": N("wellspring", "Source", "Wellspring", [flat("mp", 12)]),
    "rb1": N("intellect", "Intellect", "Intellect", [pct("mag", 2)]),
    "rb2": N("arcane_fervor", "Ferveur arcanique", "Arcane Fervor", [flat("damage_percent", 1)]),
    "n30a": N("siphon", "Siphon", "Siphon", [once("spell_vamp", 8)]),
    "n30b": N("torrent", "Torrent", "Torrent", [once("magic_pen", 8), once("damage_percent", 6)]),
    "n30c": N("time_mastery", "Maîtrise du temps", "Time Mastery", [once("cooldown_reduction", 8)]),
    "rc1": N("flare", "Éclat", "Flare", [flat("crit_dmg", 4)]),
    "rc2": N("lucidity", "Lucidité", "Lucidity", [flat("crit", 1)]),
    "rc3": N("velocity", "Vélocité", "Velocity", [flat("cast_speed", 2)]),
    "rd1": N("amplification", "Amplification", "Amplification", [pct("mag", 2)]),
    "rd2": N("overflow", "Débordement", "Overflow", [pct("mp", 3)]),
    "rd3": N("arcane_perforation", "Perforation arcanique", "Arcane Perforation", [flat("magic_pen", 1.5)]),
    "n50a": N("archmage", "Archimage", "Archmage", [once("mag", 12, "add_percent"), once("crit_dmg", 10)]),
    "n50b": N("overload", "Surcharge", "Overload", [once("damage_percent", 10)]),
    "side50": N("meditation", "Méditation", "Meditation", [once("mp_regen", 2)]),
    "m1": N("m_arcana", "Maîtrise : arcanes", "Mastery: Arcana", [pct("mag", 2)]),
    "m2": N("m_flow", "Maîtrise : flux", "Mastery: Flow", [flat("cooldown_reduction", 1)]),
    "m3": N("m_overload", "Maîtrise : surcharge", "Mastery: Overload", [flat("damage_percent", 1.5)]),
    "megaa": N("mega_archon", "Archonte", "Archon",
               [once("mag", 30, "add_percent"), once("magic_pen", 15), once("hp", -20, "add_percent")], malus=(2,)),
    "megab": N("mega_storm", "Tempête arcanique", "Arcane Storm",
               [once("damage_percent", 25), once("cast_speed", 15), once("mp", -30, "add_percent")], malus=(2,)),
})

ARMS["support"] = ("sup", {
    "e1": N("persistence", "Persistance", "Persistence", [flat("buff_duration", 2)]),
    "e2": N("liveliness", "Vivacité", "Liveliness", [flat("cast_speed", 2)]),
    "e3": N("long_breath", "Souffle long", "Long Breath", [flat("mp", 10)]),
    "e4": N("will", "Volonté", "Will", [flat("effect_resist", 2)]),
    "n15a": N("inspiration", "Inspiration", "Inspiration", [mech("buff_grants_stat", stat="damage_percent", value=8)],
              mech=("Tes améliorations sur un allié lui donnent aussi +8 % de dégâts pendant leur durée.",
                    "Your buffs on an ally also grant them +8% damage for their duration.")),
    "n15b": N("protection", "Protection", "Protection", [once("shield_power", 12), once("buff_duration", 4)],
              to_validate=SUB, v2_planned="buff_grants_stat damage_reduction : un allie que tu buffes subit -8 % de degats"),
    "side15": N("extended_aura", "Aura étendue", "Extended Aura",
                [mech("buff_splash_adjacent_ally", skill_filter="single_target_buff")],
                mech=("Tes améliorations mono-cible touchent aussi un allié adjacent.",
                      "Your single-target buffs also reach an adjacent ally.")),
    "ra1": N("swift_mind", "Esprit vif", "Swift Mind", [flat("cooldown_reduction", 1)]),
    "ra2": N("tenacity", "Ténacité", "Tenacity", [flat("tenacity", 2)]),
    "rb1": N("clarity", "Clarté", "Clarity", [pct("mp", 3)]),
    "rb2": N("harmony", "Harmonie", "Harmony", [pct("mag", 2)]),
    "n30a": N("rhythm", "Rythme", "Rhythm", [mech("free_cast_every_n", n=4)],
              mech=("Un sort sur 4 ne coûte pas de Souffle.", "One spell in 4 costs no Breath.")),
    "n30b": N("conductor", "Chef d'orchestre", "Conductor",
              [mech("cooldown_reduction_on_event", event="buff_applied_to_ally", seconds=1, scope="buffed_ally", internal_cooldown_s=5)],
              mech=("Quand tu améliores un allié, ses recharges diminuent de 1 s. Une fois toutes les 5 s par allié.",
                    "When you buff an ally, their cooldowns drop by 1 s. Once every 5 s per ally.")),
    "n30c": N("foresight", "Clairvoyance", "Foresight", [once("buff_duration", 15), once("debuff_duration", 10)]),
    "rc1": N("serenity", "Sérénité", "Serenity", [flat("buff_duration", 2)]),
    "rc2": N("discipline", "Discipline", "Discipline", [flat("cooldown_reduction", 1)]),
    "rc3": N("firmness", "Fermeté", "Firmness", [flat("effect_resist", 2)]),
    "rd1": N("eloquence", "Éloquence", "Eloquence", [flat("cast_speed", 2)]),
    "rd2": N("breadth", "Ampleur", "Breadth", [pct("mp", 3)]),
    "rd3": N("presence", "Présence", "Presence", [pct("hp", 2)]),
    "n50a": N("vanguard", "Chef de file", "Vanguard",
              [mech("buff_grants_stat", stat="damage_percent", value=6), once("shield_power", 10)],
              mech=("Tes améliorations sur un allié lui donnent aussi +6 % de dégâts pendant leur durée (s'ajoute à Inspiration).",
                    "Your buffs on an ally also grant them +6% damage for their duration (adds to Inspiration)."),
              to_validate="partie defensive (-6 % de degats subis pour l'allie) remplacee par +10 % de puissance de bouclier",
              v2_planned="buff_grants_stat damage_reduction 6"),
    "n50b": N("acceleration", "Accélération", "Acceleration", [once("cast_speed", 10), once("cooldown_reduction", 5)],
              to_validate=SUB, v2_planned="buff_grants_stat cast_speed : un allie que tu buffes a +15 % de vitesse d'incantation"),
    "side50": N("shared_drive", "Élan partagé", "Shared Drive", [once("damage_percent", 5), once("buff_duration", 5)],
                to_validate=SUB, v2_planned="stacking_stat_on_event buff_applied_to_ally : +3 % de degats par buff donne, 5 cumuls, 6 s"),
    "m1": N("m_duration", "Maîtrise : durée", "Mastery: Duration", [flat("buff_duration", 3)]),
    "m2": N("m_tempo", "Maîtrise : tempo", "Mastery: Tempo", [flat("cooldown_reduction", 1)]),
    "m3": N("m_clarity", "Maîtrise : clarté", "Mastery: Clarity", [pct("mp", 3)]),
    "megaa": N("mega_warmaster", "Maître de guerre", "Warmaster",
               [once("buff_duration", 50), mech("buff_grants_stat", stat="damage_percent", value=10), once("damage_percent", -25)],
               mech=("Tes améliorations sur un allié lui donnent aussi +10 % de dégâts pendant leur durée.",
                     "Your buffs on an ally also grant them +10% damage for their duration."),
               malus=(1,)),
    "megab": N("mega_haste", "Hâte suprême", "Supreme Haste",
               [once("cooldown_reduction", 15), once("cast_speed", 15), once("hp", -20, "add_percent")], malus=(2,),
               to_validate=SUB + " ; l'effet porte sur toi, plus sur les allies (d'ou le nouveau nom)",
               v2_planned="Hate collective, buff_grants_stat cooldown_reduction : un allie que tu buffes a -20 % de recharge"),
})

ARMS["debuff"] = ("deb", {
    "e1": N("sure_hand", "Coup d'œil", "Sharp Glance", [flat("hit", 3)]),
    "e2": N("venom", "Venin", "Venom", [flat("effect_chance", 2)]),
    "e3": N("lingering", "Prolongation", "Lingering", [flat("debuff_duration", 2)]),
    "e4": N("mind_piercer", "Perce-esprit", "Mind Piercer", [flat("magic_pen", 1.5)]),
    "n15a": N("grip", "Emprise", "Grip", [mech("damage_vs_target_with_status", status_category="control", damage_pct=10)],
              mech=("+10 % de dégâts contre une cible sous contrôle (étourdie, ralentie, réduite au silence...).",
                    "+10% damage against a controlled target (stunned, slowed, silenced...).")),
    "n15b": N("plague_touch", "Fléau", "Scourge", [once("effect_chance", 6), once("debuff_duration", 6)],
              to_validate=SUB, v2_planned="damage_vs_target_debuff_count : +12 % de degats contre une cible a 2 affaiblissements ou plus"),
    "side15": N("contagion", "Contagion", "Contagion", [mech("debuff_spread_on_death", max_spread=1)],
                mech=("Quand une cible affaiblie meurt, ses affaiblissements passent à l'ennemi le plus proche.",
                      "When a weakened target dies, its debuffs spread to the nearest enemy.")),
    "ra1": N("shadows", "Ténèbres", "Shadows", [flat("effect_chance", 2)]),
    "ra2": N("haste", "Hâte", "Haste", [flat("cooldown_reduction", 1)]),
    "rb1": N("malice", "Malice", "Malice", [pct("atk", 2), pct("mag", 2)]),
    "rb2": N("corruption", "Corruption", "Corruption", [flat("debuff_duration", 2)]),
    "n30a": N("control_zone", "Zone de contrôle", "Control Zone",
              [mech("control_splash_adjacent", skill_filter="single_target_control")],
              mech=("Tes sorts de contrôle mono-cible touchent aussi une case adjacente.",
                    "Your single-target control spells also hit an adjacent tile.")),
    "n30b": N("tempo_master", "Maître du tempo", "Tempo Master",
              [mech("cooldown_reduction_on_event", event="control_applied", seconds=1, scope="other_skills", internal_cooldown_s=3)],
              mech=("Quand tu contrôles une cible : -1 s de recharge sur tes autres sorts. Une fois toutes les 3 s.",
                    "When you control a target: -1 s cooldown on your other spells. Once every 3 s.")),
    "n30c": N("deep_venom", "Venin profond", "Deep Venom", [once("effect_chance", 15), once("debuff_duration", 10)]),
    "rc1": N("fatality", "Fatalité", "Fatality", [flat("effect_chance", 2)]),
    "rc2": N("dark_persistence", "Persistance noire", "Dark Persistence", [flat("debuff_duration", 2)]),
    "rc3": N("armor_breaker", "Brise-armure", "Armor Breaker", [flat("armor_pen", 1.5), flat("magic_pen", 1.5)]),
    "rd1": N("curse", "Malédiction", "Curse", [pct("atk", 2), pct("mag", 2)]),
    "rd2": N("affliction", "Affliction", "Affliction", [flat("damage_percent", 1)]),
    "rd3": N("hex", "Maléfice", "Hex", [flat("debuff_duration", 3)]),
    "n50a": N("torment", "Supplice", "Torment", [once("damage_percent", 8), once("effect_chance", 8)],
              to_validate=SUB, v2_planned="damage_vs_target_debuff_count per_debuff : +4 % par affaiblissement de la cible, jusqu'a 5"),
    "n50b": N("vise", "Étau", "Vise",
              [mech("damage_vs_target_with_status", status_category="control", damage_pct=15),
               mech("stat_vs_target_with_status", status_category="control", stat="crit", value=10)],
              mech=("+15 % de dégâts et +10 % de chance critique contre une cible sous contrôle (s'ajoute à Emprise).",
                    "+15% damage and +10% critical chance against a controlled target (adds to Grip).")),
    "side50": N("will_breaker", "Brise-volonté", "Will Breaker", [once("effect_chance", 10)],
                to_validate=SUB, v2_planned="stat_window_after_event control_applied : +15 % de chance d'effet pendant 4 s"),
    "m1": N("m_grip", "Maîtrise : emprise", "Mastery: Grip", [flat("effect_chance", 2)]),
    "m2": N("m_duration", "Maîtrise : persistance", "Mastery: Persistence", [flat("debuff_duration", 3)]),
    "m3": N("m_malice", "Maîtrise : malice", "Mastery: Malice", [pct("atk", 2), pct("mag", 2)]),
    "megaa": N("mega_plague", "Peste", "Plague",
               [once("damage_percent", 20), once("effect_chance", 15), once("hp", -15, "add_percent")], malus=(2,),
               to_validate=SUB, v2_planned="control_splash_adjacent harmful : un affaiblissement d'un sort cible touche aussi un ennemi adjacent ; contrepartie -25 % de duree des affaiblissements"),
    "megab": N("mega_chains", "Seigneur des chaînes", "Lord of Chains",
               [once("debuff_duration", 40), once("effect_chance", 20), once("damage_percent", -25)], malus=(2,)),
})

# Graines (2026-10-20, A VALIDER) : petit noeud de debut, relie au centre seul, pour que chaque bras
# donne tot de la MAG ou un peu d'ATK. Attaque (Force) et Arcanes (Savoir) commencent deja ainsi.
# Retour de Charleston (2026-10-20, 2e passe) : des premiers noeuds GENERIQUES (PV, DEF, MAG) selon le
# theme du bras, qui n'orientent pas un build des le debut. Attaque garde Force (ATK + MAG), Arcanes Savoir.
SEEDS = {
    "defense": N("seed_build", "Carrure", "Sturdy Build", [flat("hp", 12)]),
    "healing": N("seed_prayer", "Prière ardente", "Ardent Prayer", [flat("mag", 2)]),
    "support": N("seed_poise", "Aplomb", "Poise", [flat("hp", 8), flat("armor", 1)]),
    "debuff": N("seed_dark_lore", "Sombre savoir", "Dark Lore", [flat("mag", 2)]),
}
SEED_NOTE = ("premier noeud generique du bras (retour de Charleston 2026-10-20 : PV, DEF ou MAG selon le theme, "
             "sans orienter un build) : stat et valeur par rang a valider")

# Ponts (bras A, bras B, prefixe, passage, hybride sur le chemin, hybride a cote). L'anneau est
# Attaque, Defense, Soin, Arcanes, Soutien, Affaiblissement. Attaque <-> Defense et Attaque <->
# Affaiblissement viennent du proprietaire (noeuds d'arbre_v2_attaque.json, contenu ci-dessous).
BRIDGES = [
    ("defense", "healing", "def_heal",
     N("p", "Passage", "Passage", [flat("hp", 12), flat("healing_received", 2)]),
     N("h", "Rempart vivant", "Living Rampart", [mech("shield_from_healing_received", ratio_pct=10)],
       mech=("10 % des soins que tu reçois deviennent du bouclier.", "10% of the healing you receive becomes a shield.")),
     N("s", "Second élan", "Second Wind", [once("healing_received", 12), once("damage_reduction", 3)],
       to_validate=SUB + " (un 2e bouclier sous les PV bas ecraserait Inebranlable : le composant n'en tient qu'un)",
       v2_planned="shield_on_low_hp : sous 25 % de PV, bouclier de 15 % des PV max, une fois toutes les 60 s")),
    ("healing", "arcane", "heal_arc",
     N("p", "Passage", "Passage", [flat("mag", 2), flat("heal_power", 2)]),
     N("h", "Lumière arcanique", "Arcane Light", [once("mag", 8, "add_percent"), once("heal_power", 8)],
       to_validate="pont du 6e bras, ajoute le 2026-10-20"),
     N("s", "Siphon vital", "Vital Siphon", [once("spell_vamp", 6), once("healing_received", 6)],
       to_validate="pont du 6e bras, ajoute le 2026-10-20")),
    ("arcane", "support", "arc_sup",
     N("p", "Passage", "Passage", [flat("mp", 10), flat("cast_speed", 2)]),
     N("h", "Chant de guerre", "War Chant", [mech("buff_cleanses_debuff", count=1)],
       mech=("Tes améliorations sur un allié retirent un de ses affaiblissements.",
             "Your buffs on an ally remove one of their debuffs.")),
     N("s", "Résonance", "Resonance", [once("buff_duration", 8), once("cooldown_reduction", 4)],
       to_validate="pont du 6e bras, ajoute le 2026-10-20 (Chant de guerre vient de l'ancien pont Soin <-> Soutien)")),
    ("support", "debuff", "sup_deb",
     N("p", "Passage", "Passage", [flat("effect_chance", 2), flat("effect_resist", 2)]),
     N("h", "Coordination", "Coordination", [mech("ally_buffed_bonus_vs_debuffed", damage_pct=8)],
       mech=("Un allié que tu as amélioré inflige +8 % de dégâts aux cibles que tu as affaiblies.",
             "An ally you buffed deals +8% damage to targets you weakened.")),
     N("s", "Marque du chef", "Leader's Mark", [once("crit", 6), once("effect_chance", 6)],
       to_validate=SUB, v2_planned="ally_buffed_bonus_vs_debuffed crit : +10 % de chance critique pour un allie buffe contre tes cibles affaiblies")),
]
ATK_BRIDGES = {  # contenu des 4 hybrides et des passages ecrits par le proprietaire
    "pt2_brg_atk_def_a": N("p", "Passage", "Passage", None),
    "pt2_brg_atk_def_b": N("p", "Passage", "Passage", None),
    "pt2_brg_atk_deb_a": N("p", "Passage", "Passage", None),
    "pt2_brg_atk_deb_b": N("p", "Passage", "Passage", None),
    "pt2_hyb_atk_def": N("h", "Riposte", "Riposte", [mech("next_hit_bonus_after_event", events=["block", "parry"], damage_pct=40)],
                         mech=("Après un blocage ou une parade, ta prochaine attaque inflige +40 % de dégâts.",
                               "After a block or a parry, your next attack deals +40% damage.")),
    "pt2_hyb_atk_def_side": N("s", "Garde de fer", "Iron Guard", [once("damage_percent", 6), once("damage_reduction", 4)],
                              to_validate=SUB, v2_planned="stats_while_hp_above : au-dessus de 70 % de PV, +12 % de degats et -8 % de degats recus"),
    "pt2_hyb_atk_deb": N("h", "Opportuniste", "Opportunist",
                         [mech("stat_vs_target_with_status", status_category="control", stat="crit", value=20)],
                         mech=("+20 % de chance critique contre une cible sous contrôle.",
                               "+20% critical chance against a controlled target.")),
    "pt2_hyb_atk_deb_side": N("s", "Curée", "Quarry", [once("damage_percent", 6), once("effect_chance", 6)],
                              to_validate=SUB, v2_planned="damage_vs_target_debuff_count : +20 % de degats contre une cible a 3 affaiblissements ou plus"),
}

# ---------------------------------------------------------------------------------------------
# Catalogue des mecaniques = ce que le combat sait faire (server-combat passive_tree_mechanics.hpp).
# variants : valeurs exigees des parametres discriminants. stacking : single (un seul noeud de
# l'arbre peut la porter), additive (les valeurs s'ajoutent), max (la plus forte compte).
# ---------------------------------------------------------------------------------------------
MECHANICS = {
    "damage_vs_target_hp_below": {"params": {"hp_pct": "number", "damage_pct": "number"}, "stacking": "single",
                                  "doc_fr": "Bonus de degats contre une cible sous un seuil de PV."},
    "damage_vs_target_with_status": {"params": {"status_category": "status_category", "damage_pct": "number"},
                                     "variants": {"status_category": ["control"]}, "stacking": "additive",
                                     "doc_fr": "Bonus de degats contre une cible sous controle."},
    "stat_vs_target_with_status": {"params": {"status_category": "status_category", "stat": "stat", "value": "number"},
                                   "variants": {"status_category": ["control"], "stat": ["crit"]}, "stacking": "additive",
                                   "doc_fr": "Bonus de chance critique contre une cible sous controle."},
    "stat_window_after_event": {"params": {"event": "string", "stat": "stat", "value": "number", "duration_s": "number"},
                                "variants": {"event": ["crit"], "stat": ["crit"]}, "stacking": "single",
                                "doc_fr": "Apres un coup critique : bonus de chance critique temporaire."},
    "cooldown_reduction_on_event": {"params": {"event": "string", "seconds": "number", "scope": "string", "internal_cooldown_s": "number"},
                                    "variants": {"event": ["crit", "control_applied", "buff_applied_to_ally"],
                                                 "scope": ["cast_skill", "other_skills", "buffed_ally"]},
                                    "pairs": [["crit", "cast_skill"], ["control_applied", "other_skills"], ["buff_applied_to_ally", "buffed_ally"]],
                                    "stacking": "single", "doc_fr": "Reduit des recharges quand l'evenement survient."},
    "next_hit_bonus_after_event": {"params": {"events": "list", "damage_pct": "number"},
                                   "variants": {"events": [["block", "parry"]]}, "stacking": "single",
                                   "doc_fr": "Apres un blocage ou une parade, la prochaine attaque inflige plus de degats."},
    "damage_taken_reduction_conditional": {"params": {"condition": "string", "reduction_pct": "number"},
                                           "variants": {"condition": ["area_attack", "attacker_beyond_3_tiles", "stationary_3s"]},
                                           "stacking": "single", "doc_fr": "Reduit les degats recus quand la condition est vraie."},
    "shield_on_low_hp": {"params": {"hp_pct": "number", "shield_pct_max_hp": "number", "internal_cooldown_s": "number"},
                         "stacking": "single", "doc_fr": "Bouclier quand les PV passent sous le seuil."},
    "heal_bonus_target_hp_below": {"params": {"hp_pct": "number", "heal_pct": "number"}, "stacking": "single",
                                   "doc_fr": "Bonus de soin sur un allie sous un seuil de PV."},
    "heal_splash_nearest_ally": {"params": {"ratio_pct": "number", "skill_filter": "string"},
                                 "variants": {"skill_filter": ["single_target_heal"]}, "stacking": "max",
                                 "doc_fr": "Un soin mono-cible soigne aussi l'allie le plus proche de la cible."},
    "heal_return_to_caster": {"params": {"ratio_pct": "number"}, "stacking": "single",
                              "doc_fr": "Une part des soins donnes revient au lanceur."},
    "prevent_ally_death": {"params": {"heal_pct": "number", "per_combat": "int"}, "stacking": "single",
                           "doc_fr": "Un allie qui devrait mourir reste a 1 PV puis recoit un soin."},
    "buff_grants_stat": {"params": {"stat": "stat", "value": "number"}, "variants": {"stat": ["damage_percent"]},
                         "stacking": "additive", "doc_fr": "Tes ameliorations sur un allie lui donnent des degats en plus."},
    "buff_splash_adjacent_ally": {"params": {"skill_filter": "string"}, "variants": {"skill_filter": ["single_target_buff"]},
                                  "stacking": "single", "doc_fr": "Une amelioration mono-cible touche aussi un allie adjacent."},
    "free_cast_every_n": {"params": {"n": "int"}, "stacking": "single", "doc_fr": "Un sort sur N ne coute pas de Souffle."},
    "skill_range_bonus": {"params": {"bonus": "int", "min_base_range": "int", "skill_filter": "string"},
                          "variants": {"skill_filter": ["offensive"]}, "stacking": "single",
                          "doc_fr": "Portee augmentee pour les sorts offensifs."},
    "control_splash_adjacent": {"params": {"skill_filter": "string"}, "variants": {"skill_filter": ["single_target_control"]},
                                "stacking": "single", "doc_fr": "Un sort de controle mono-cible touche aussi une case adjacente."},
    "debuff_spread_on_death": {"params": {"max_spread": "int"}, "stacking": "single",
                               "doc_fr": "A la mort d'une cible affaiblie, ses affaiblissements passent a l'ennemi le plus proche."},
    "shield_from_healing_received": {"params": {"ratio_pct": "number"}, "stacking": "single",
                                     "doc_fr": "Une part des soins recus devient du bouclier."},
    "buff_cleanses_debuff": {"params": {"count": "int"}, "stacking": "single",
                             "doc_fr": "Tes ameliorations sur un allie retirent des affaiblissements."},
    "ally_buffed_bonus_vs_debuffed": {"params": {"damage_pct": "number"}, "stacking": "single",
                                      "doc_fr": "Un allie ameliore inflige plus de degats a une cible que tu as affaiblie."},
}

# ---------------------------------------------------------------------------------------------
# Geometrie
# ---------------------------------------------------------------------------------------------
RING = ["attack", "defense", "healing", "arcane", "support", "debuff"]
ANGLES = {a: -90 + 60 * i for i, a in enumerate(RING)}
COLORS = {"attack": "#e66b52", "defense": "#5c99e6", "healing": "#5cc78f", "arcane": "#4fd1c5",
          "support": "#f2b84d", "debuff": "#a875e6"}
NAMES = {"attack": ("Attaque", "Attack"), "defense": ("Défense", "Defense"), "healing": ("Soin", "Healing"),
         "arcane": ("Arcanes", "Arcana"), "support": ("Soutien", "Support"), "debuff": ("Affaiblissement", "Weakening")}
PREFIX = {"attack": "atk", "defense": "def", "healing": "heal", "arcane": "arc", "support": "sup", "debuff": "deb"}


def to_world(arm, along, lateral):
    t = math.radians(ANGLES[arm])
    x = along * math.cos(t) - lateral * math.sin(t)
    y = along * math.sin(t) + lateral * math.cos(t)
    return [x, y]


def local_of(atk_node):
    x, y = atk_node["pos"]
    return -y, x  # along, lateral (Attaque pointe vers -y)


def scaled(p):
    return [round(p[0] * SCALE, 1), round(p[1] * SCALE, 1)]


# ---------------------------------------------------------------------------------------------
# Icones : celles qui existent dans le client (assets/icons/passives/), y compris les 40 icones V2
# livrees le 2026-10-17 (tree/v2_*). Les noeuds nouveaux du 2026-10-20 recoivent une icone EXISTANTE
# proche en attendant la leur (icon_planned = fichier a commander, liste ICONES_A_COMMANDER).
# ---------------------------------------------------------------------------------------------
V1_ICON = {"execution": "tree/execution", "reach": "tree/reach", "killer_instinct": "tree/killer_instinct",
           "mega_fatal": "tree/fatal_strike", "iron_skin": "tree/iron_skin", "hold_position": "tree/hold_position",
           "composure": "tree/composure", "unshakable": "tree/unshakable", "helping_hand": "tree/helping_hand",
           "extended_heal": "tree/extended_heal", "transfusion": "tree/transfusion", "last_breath": "tree/last_breath",
           "inspiration": "tree/inspiration", "extended_aura": "tree/extended_aura", "rhythm": "tree/rhythm",
           "conductor": "tree/conductor", "grip": "tree/grip", "contagion": "tree/contagion",
           "control_zone": "tree/control_zone", "tempo_master": "tree/tempo_master", "atk_def": "tree/riposte",
           "def_heal": "tree/living_rampart", "arc_sup": "tree/war_chant", "sup_deb": "tree/coordination",
           "atk_deb": "tree/opportunist"}
# Icones V2 livrees, par id de noeud (sans pt2_) : le nom de fichier suit l'id.
V2_DELIVERED = {"atk_first_blood", "atk_breach", "atk_momentum", "atk_relentless", "atk_guardbreaker", "atk_bloodlust",
                "atk_mega_unleashed", "def_guard", "def_retaliation", "def_vampire", "def_last_stand", "def_living_wall",
                "def_mega_fortress", "def_mega_titan", "heal_prevention", "heal_spell_vamp", "heal_holy_shield",
                "heal_downpour", "heal_prayer", "heal_mega_sanctuary", "heal_mega_martyr", "sup_protection",
                "sup_foresight", "sup_vanguard", "sup_acceleration", "sup_shared_drive", "sup_mega_warmaster",
                "sup_mega_haste", "deb_plague_touch", "deb_deep_venom", "deb_torment", "deb_vise", "deb_will_breaker",
                "deb_mega_plague", "deb_mega_chains", "hyb_atk_def_side", "hyb_atk_deb_side", "hyb_def_heal_side"}
# Hybrides V2 livres sur un pont qui n'existe plus (Soin <-> Soutien, Soutien <-> Affaiblissement) :
REUSED_HYB = {"pt2_hyb_sup_deb_side": "tree/v2_hyb_sup_deb_side"}
STAT_ICON = {"crit": "common/critical_instinct", "crit_dmg": "tree/crit_damage", "hit": "common/precision",
             "atk": "common/strength", "mag": "common/intellect", "armor": "common/resistance",
             "magic_resist": "tree/magic_resist", "hp": "common/vitality", "flee": "common/agility",
             "damage_percent": "common/breakthrough", "armor_pen": "tree/penetration", "magic_pen": "common/arcane_piercing",
             "cast_speed": "tree/cast_speed", "damage_reduction": "tree/damage_reduction", "lifesteal": "common/vampirism",
             "parry_chance": "tree/parry", "block_chance": "tree/parry", "thorns": "tree/thorns",
             "healing_received": "tree/healing_received", "heal_power": "tree/heal_power", "spell_vamp": "tree/spell_vamp",
             "shield_power": "tree/shield_power", "mp": "common/deep_breath", "mp_regen": "tree/mp_regen",
             "buff_duration": "tree/buff_duration", "cooldown_reduction": "tree/cooldown_reduction",
             "tenacity": "common/tenacity", "effect_resist": "common/warding", "effect_chance": "tree/effect_chance",
             "debuff_duration": "tree/debuff_duration", "hp_regen": "common/restoration"}
# Remplacement en attendant l'icone commandee : (icone existante, sujet propose pour la commande).
PLACEHOLDER = {
    "arc_arcane_power": ("common/intellect", "un livre ouvert d'ou jaillit une flamme bleu-vert"),
    "arc_quick_casting": ("tree/cast_speed", "une main qui trace un sceau en un eclair, trainees cyan"),
    "arc_piercing_mind": ("common/arcane_piercing", "une aiguille de lumiere cyan qui traverse un bouclier runique"),
    "arc_siphon": ("tree/spell_vamp", "un tourbillon cyan aspire par une paume ouverte"),
    "arc_torrent": ("common/breakthrough", "un torrent d'energie cyan qui brise une rune"),
    "arc_time_mastery": ("tree/cooldown_reduction", "un sablier entoure d'anneaux runiques cyan"),
    "arc_archmage": ("common/focus", "un baton couronne d'un cristal cyan, robe etoilee"),
    "arc_overload": ("common/breakthrough", "un cristal fissure qui deborde d'energie cyan"),
    "arc_meditation": ("tree/mp_regen", "une silhouette en tailleur, souffle cyan qui monte"),
    "arc_mega_archon": ("common/intellect", "un mage immense flottant, couronne de runes, le corps translucide (PV sacrifies)"),
    "arc_mega_storm": ("tree/cast_speed", "une tempete d'eclairs cyan, la fiole de Souffle vide a la ceinture"),
    "hyb_heal_arc": ("tree/heal_power", "une main qui soigne, lumiere verte melee de runes cyan"),
    "hyb_heal_arc_side": ("tree/spell_vamp", "un filet de vie verte aspire par un sort cyan"),
    "hyb_arc_sup_side": ("tree/buff_duration", "une onde doree et cyan qui se propage en cercles"),
}
TO_ORDER = []


def icon_for(node, effects):
    nid = node["id"]
    short = nid[len("pt2_"):]
    if node["kind"] == "center":
        return "tree/tree_center"
    if node["kind"] in ("small", "bridge_small"):
        return STAT_ICON[next(e["stat"] for e in effects if "stat" in e)]
    if nid in REUSED_HYB:
        return REUSED_HYB[nid]
    key = short.split("_", 1)[1] if not short.startswith("hyb_") else short[len("hyb_"):]
    if key in V1_ICON:
        return V1_ICON[key]
    if short in V2_DELIVERED:
        return f"tree/v2_{short}"
    if short in PLACEHOLDER:
        icon, subject = PLACEHOLDER[short]
        node["icon_planned"] = f"tree/v2_{short}"
        TO_ORDER.append({"arm": node.get("arm") or "+".join(node.get("arms", [])), "kind": node["kind"],
                         "name_fr": node["name_fr"], "file": f"tree/v2_{short}.png", "placeholder": icon,
                         "subject": subject, "description_fr": node["description_fr"]})
        return icon
    raise SystemExit(f"pas d'icone pour {nid}")


# ---------------------------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------------------------
COSTS = src["rules"]["costs"]


def make_node(nid, kind, arm, max_rank, pos, spec, effects, choice=None, arms=None):
    node = {"id": nid, "kind": kind, "arm": arm}
    if arms:
        node["arms"] = arms
    node["max_rank"] = max_rank
    if kind not in ("small", "bridge_small", "center"):
        node["cost"] = COSTS[kind]
    node["pos"] = scaled(pos)
    if choice:
        node["choice"] = choice
    per_rank = kind in ("small", "bridge_small")
    fr, en = describe(effects, per_rank and max_rank > 1, spec.get("mech"), spec.get("malus", ()))
    node["name_fr"], node["name_en"] = spec["fr"], spec["en"]
    node["description_fr"], node["description_en"] = fr, en
    node["effects"] = effects
    for k in ("to_validate", "v2_planned"):
        if spec.get(k):
            node[k] = spec[k]
    node["icon"] = icon_for(node, effects)
    return node


nodes = [{"id": "pt_center", "kind": "center", "arm": None, "max_rank": 1, "pos": [0, 0], "icon": "tree/tree_center",
          "name_fr": "Centre", "name_en": "Center", "description_fr": "Point de départ de l'arbre. Toujours acquis.",
          "description_en": "Starting point of the tree. Always acquired.", "effects": []}]
edges = []
notable30 = {}
ids_by_arm = {}

for arm in RING:
    pfx = PREFIX[arm]
    content = ATTACK if arm == "attack" else ARMS[arm][1]
    assert set(content) == set(SLOTS), (arm, set(SLOTS) ^ set(content))
    ids = {}
    for slot, spec in content.items():
        tpl = ATK[f"pt2_atk_{SLOTS[slot]}"]
        nid = f"pt2_{pfx}_{spec['key']}"
        ids[slot] = nid
        effects = spec["effects"] if spec["effects"] is not None else tpl["effects"]
        choice = None
        if "choice" in tpl:
            group = next(g for g, members in GROUPS.items() if slot in members)
            choice = {"group": f"{pfx}_{group}", "option": spec["key"]}
        nodes.append(make_node(nid, tpl["kind"], arm, tpl.get("max_rank", 1),
                               to_world(arm, *local_of(tpl)), spec, effects, choice))
    for a, b in src["edges"]:
        if a == "pt_center" and b in SLOT_OF:
            edges.append(["pt_center", ids[SLOT_OF[b]]])
        elif a in SLOT_OF and b in SLOT_OF:
            edges.append([ids[SLOT_OF[a]], ids[SLOT_OF[b]]])
    notable30[arm] = [ids["n30a"], ids["n30b"], ids["n30c"]]
    ids_by_arm[arm] = ids
    if arm in SEEDS:
        spec = SEEDS[arm]
        spec = dict(spec, to_validate=SEED_NOTE)
        nid = f"pt2_{pfx}_{spec['key']}"
        nodes.append(make_node(nid, "small", arm, 3, to_world(arm, 3.2, 1.3), spec, spec["effects"]))
        edges.append(["pt_center", nid])


def bridge_layout(arm_a, arm_b):
    pa, pb = to_world(arm_a, 11, 0), to_world(arm_b, 11, 0)
    lerp = lambda t: [pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t]
    mid = lerp(0.5)
    norm = math.hypot(*mid) or 1
    side = [mid[0] + mid[0] / norm * 1.5, mid[1] + mid[1] / norm * 1.5]
    return lerp(0.3), mid, lerp(0.7), side


# Ponts d'Attaque (proprietaire) : memes noeuds et memes regles, rebranches sur les vrais notables 30.
for other, key in (("defense", "atk_def"), ("debuff", "atk_deb")):
    layout = bridge_layout("attack", other)
    a_arm, b_arm = ("attack", other)
    for nid, pos in zip((f"pt2_brg_{key}_a", f"pt2_hyb_{key}", f"pt2_brg_{key}_b", f"pt2_hyb_{key}_side"), layout):
        tpl = ATK[nid]
        spec = ATK_BRIDGES[nid]
        effects = spec["effects"] if spec["effects"] is not None else tpl["effects"]
        nodes.append(make_node(nid, tpl["kind"], None, tpl.get("max_rank", 1), pos, spec, effects, arms=[a_arm, b_arm]))
CLONE_TO_REAL = {}
for arm, pfx in (("defense", "def"), ("debuff", "deb")):
    for clone, real in zip(("killer_instinct", "breach", "momentum"), notable30[arm]):
        CLONE_TO_REAL[f"pt2_{pfx}_{clone}"] = real
for a, b in src["edges"]:
    if a.startswith("pt2_brg_") or b.startswith("pt2_brg_") or a.startswith("pt2_hyb_") or b.startswith("pt2_hyb_"):
        edges.append([CLONE_TO_REAL.get(a, a), CLONE_TO_REAL.get(b, b)])

for arm_a, arm_b, key, passage, hyb, hyb_side in BRIDGES:
    pos = bridge_layout(arm_a, arm_b)
    ba, h, bb, hs = (f"pt2_brg_{key}_a", f"pt2_hyb_{key}", f"pt2_brg_{key}_b", f"pt2_hyb_{key}_side")
    for nid, kind, p, spec in ((ba, "bridge_small", pos[0], passage), (h, "hybrid", pos[1], hyb),
                               (bb, "bridge_small", pos[2], passage), (hs, "hybrid", pos[3], hyb_side)):
        nodes.append(make_node(nid, kind, None, 1, p, spec, spec["effects"], arms=[arm_a, arm_b]))
    for n30 in notable30[arm_a]:
        edges.append([n30, ba])
    edges += [[ba, h], [h, bb], [h, hs]]
    for n30 in notable30[arm_b]:
        edges.append([bb, n30])

ids = {n["id"] for n in nodes}
missing = [e for e in edges if e[0] not in ids or e[1] not in ids]
assert not missing, missing
assert len(ids) == len(nodes), "id en double"

rules = json.loads(json.dumps(src["rules"]))
rules["points"] = {
    "max_points": 99, "starting_points": 0, "points_per_level": 1,
    "_note": "Regle actuelle du serveur (level_calc) : 1 point par niveau gagne, niveaux 2 a 100 = 99. La V2 en "
             "prevoit 100 (1 au niveau 1, starting_passive_points dans systems/progression.json) : a valider, non applique.",
}
rules["small_passes_at_max_rank"] = True
rules["mega_max"] = 1
rules["bridges"] = {"excluded_by_mega": True, "kinds": ["bridge_small", "hybrid"],
                    "_note": "Avoir un mega ferme les ponts (passages et hybrides) : un all-in ne peut pas devenir hybride."}
rules["respec"] = dict(rules.get("respec", {}), status="proposition, NON appliquee : le reset suit toujours la regle actuelle du serveur")

out = {
    "_meta": {
        "version": "2.3",
        "last_updated": "2026-10-20",
        "description": "Arbre des passifs communs (onglet Passif), V2 a distance : un centre, 6 bras (Attaque, Defense, "
                       "Soin, Arcanes, Soutien, Affaiblissement), un pont entre chaque paire de bras voisins. Les notables "
                       "tombent a 15 / 30 / 50 / 75 points du centre. Lu par economy (achat, retrait, reset), combat "
                       "(stats + mecaniques) et le client (ecran). Les passifs de classe ne sont pas concernes.",
        "generator": "GENERE par _meta/conception_passifs/gen_arbre_v2.py : ne pas editer a la main.",
        "doc": "_meta/conception_passifs/ARBRE_PASSIFS_V2.md",
        "simulation": "python -I _meta/conception_passifs/sim_arbre_v2.py classes/passive_tree.json",
        "coordinates": f"pos en unites de dessin (gabarit x {SCALE}), centre en [0,0], x vers la droite, y vers le bas.",
        "icons": "chemin relatif a kanarion_front/assets/icons/passives/ sans extension. icon_planned = icone commandee, "
                 "icon = remplacement en attendant.",
        "to_validate": "les noeuds qui portent to_validate sont des choix d'integration a faire valider par le proprietaire "
                       "(v2_planned = la mecanique prevue par la V2, pas encore branchee en combat).",
    },
    "rules": rules,
    "layout": {"scale": SCALE,
               "rings": [{"points": p, "radius": round(r * SCALE, 1)} for p, r in ((15, 6.5), (30, 11), (50, 17), (75, 23.5))],
               "arm_label_radius": round(26.5 * SCALE, 1)},
    "arms": [{"id": a, "name_fr": NAMES[a][0], "name_en": NAMES[a][1], "color": COLORS[a], "angle_deg": ANGLES[a],
              "neighbors": [RING[(i - 1) % len(RING)], RING[(i + 1) % len(RING)]]} for i, a in enumerate(RING)],
    "mechanics": MECHANICS,
    "nodes": nodes,
    "edges": edges,
}
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
    f.write("\n")
with open(os.path.join(HERE, "icones_v2_a_creer.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(TO_ORDER, f, ensure_ascii=False, indent=1)
    f.write("\n")
tv = sum(1 for n in nodes if n.get("to_validate"))
print(f"classes/passive_tree.json : {len(nodes)} noeuds, {len(edges)} aretes, {len(RING)} bras, "
      f"{tv} noeuds a valider, {len(TO_ORDER)} icones a commander")
