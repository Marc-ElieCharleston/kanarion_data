"""Arbre des passifs V2 complet (brouillon) : les 4 bras manquants + les 3 ponts manquants.

Le bras Attaque (arbre_v2_attaque.json, ecrit par le proprietaire) sert de GABARIT : chaque bras
reprend exactement ses emplacements (rangs, couts, aretes), donc chaque notable tombe a la meme
distance du centre (15 / 30 / 50 / 75). Seul le contenu change, et il est decrit plus bas, bras par
bras, emplacement par emplacement. Les noeuds d'Attaque sont recopies tels quels ; seuls ses ponts
sont rebranches sur les vrais notables 30 de Defense et d'Affaiblissement.

Usage : python -I gen_arbre_v2.py      (ecrit arbre_v2.json a cote)
Puis :  python -I sim_arbre_v2.py arbre_v2.json
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(HERE, "arbre_v2_attaque.json"), encoding="utf-8"))

# Emplacement du gabarit -> id du noeud d'Attaque qui l'occupe.
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


def flat(stat, v):
    return {"stat": stat, "op": "add_flat", "value_per_rank": v}


def pct(stat, v):
    return {"stat": stat, "op": "add_percent", "value_per_rank": v}


def once(stat, v, op="add_flat"):
    return {"stat": stat, "op": op, "value": v}


def mech(name, **params):
    return {"mechanic": name, "params": params}


# ---------------------------------------------------------------------------------------------
# Contenu des bras. Chaque entree : emplacement -> (cle, nom, description, effets).
# Regles suivies (celles du bras Attaque) : fixe a l'entree, % en profondeur ; jamais de % sur une
# stat dont la base de classe vaut 0 (validate_passives regle 8) ; mecaniques V1 reprises quand
# elles existent, nouvelles mecaniques listees dans NEW_MECHANICS.
# ---------------------------------------------------------------------------------------------
ARMS = {}

ARMS["defense"] = ("def", {
    "e1": ("hide", "Peau dure", "+2 armure par rang.", [flat("armor", 2)]),
    "e2": ("constitution", "Constitution", "+12 PV max par rang.", [flat("hp", 12)]),
    "e3": ("calm", "Esprit calme", "+2 resistance magique par rang.", [flat("magic_resist", 2)]),
    "e4": ("light_step", "Pas leger", "+1 esquive par rang.", [flat("flee", 1)]),
    "n15a": ("iron_skin", "Peau de fer", "-15 % de degats subis des attaques de zone.",
             [mech("damage_taken_reduction_conditional", condition="area_attack", reduction_pct=15)]),
    "n15b": ("hold_position", "Position tenue", "Immobile depuis 3 s : -10 % de degats subis.",
             [mech("damage_taken_reduction_conditional", condition="stationary_3s", reduction_pct=10)]),
    "side15": ("composure", "Sang-froid", "-12 % de degats subis d'un attaquant a plus de 3 cases.",
               [mech("damage_taken_reduction_conditional", condition="attacker_beyond_3_tiles", reduction_pct=12)]),
    "ra1": ("rampart", "Rempart", "+3 armure et +3 resistance magique par rang.",
            [flat("armor", 3), flat("magic_resist", 3)]),
    "ra2": ("robust", "Robustesse", "+15 PV max par rang.", [flat("hp", 15)]),
    "rb1": ("bastion", "Bastion", "+2 % de PV max par rang.", [pct("hp", 2)]),
    "rb2": ("plating", "Carapace", "+2 % d'armure et +2 % de resistance magique par rang.",
            [pct("armor", 2), pct("magic_resist", 2)]),
    "n30a": ("guard", "Garde : parade", "+8 % de chance de parade et +8 % de chance de blocage.",
             [once("parry_chance", 8), once("block_chance", 8)]),
    "n30b": ("retaliation", "Represailles : epines", "Renvoie 15 % des degats subis a l'attaquant.",
             [once("thorns", 15)]),
    "n30c": ("vampire", "Endurance : vampirisme", "+6 % de vol de vie et +6 % de vol de sort.",
             [once("lifesteal", 6), once("spell_vamp", 6)]),
    "rc1": ("endurance", "Endurance", "+1 % de reduction des degats subis par rang.", [flat("damage_reduction", 1)]),
    "rc2": ("resilience", "Resilience", "+2 resistance aux effets par rang.", [flat("effect_resist", 2)]),
    "rc3": ("anchor", "Ancrage", "+2 tenacite par rang (les controles subis durent moins).", [flat("tenacity", 2)]),
    "rd1": ("scales", "Ecailles", "+2 % d'armure et +2 % de resistance magique par rang.",
            [pct("armor", 2), pct("magic_resist", 2)]),
    "rd2": ("colossus", "Colosse", "+2 % de PV max par rang.", [pct("hp", 2)]),
    "rd3": ("regrowth", "Regeneration", "+5 % de regeneration de PV par rang.", [pct("hp_regen", 5)]),
    "n50a": ("unshakable", "Inebranlable", "Sous 30 % de PV : bouclier egal a 20 % de tes PV max. Une fois toutes les 45 s.",
             [mech("shield_on_low_hp", hp_pct=30, shield_pct_max_hp=20, internal_cooldown_s=45)]),
    "n50b": ("last_stand", "Dernier rempart", "Sous 30 % de PV : -20 % de degats subis.",
             [mech("damage_taken_reduction_conditional", condition="hp_below", hp_pct=30, reduction_pct=20)]),
    "side50": ("living_wall", "Mur vivant", "Apres un blocage ou une parade : -20 % de degats subis pendant 3 s.",
               [mech("stat_window_after_event", event="block_or_parry", stat="damage_reduction", value=20, duration_s=3)]),
    "m1": ("m_bastion", "Maitrise : bastion", "+2 % de PV max par rang.", [pct("hp", 2)]),
    "m2": ("m_armor", "Maitrise : cuirasse", "+2 % d'armure et +2 % de resistance magique par rang.",
           [pct("armor", 2), pct("magic_resist", 2)]),
    "m3": ("m_endurance", "Maitrise : endurance", "+1 % de reduction des degats subis par rang.",
           [flat("damage_reduction", 1)]),
    "megaa": ("mega_fortress", "Forteresse",
              "+30 % de PV max et +15 % de reduction des degats subis. Contrepartie : -25 % de degats infliges.",
              [once("hp", 30, "add_percent"), once("damage_reduction", 15), once("damage_percent", -25)]),
    "megab": ("mega_titan", "Colere du titan",
              "Renvoie 30 % des degats subis et +10 % de vol de vie. Contrepartie : -25 % de soins recus.",
              [once("thorns", 30), once("lifesteal", 10), once("healing_received", -25)]),
})

ARMS["healing"] = ("heal", {
    "e1": ("warm_hands", "Mains chaudes", "+2 % de puissance de soin par rang.", [flat("heal_power", 2)]),
    "e2": ("sap", "Seve", "+10 Souffle max par rang.", [flat("mp", 10)]),
    "e3": ("grace", "Grace", "+2 % de soins recus par rang.", [flat("healing_received", 2)]),
    "e4": ("focus", "Concentration", "+2 magie par rang.", [flat("mag", 2)]),
    "n15a": ("helping_hand", "Aide salvatrice", "+20 % de soins sur une cible sous 40 % de ses PV.",
             [mech("heal_bonus_target_hp_below", hp_pct=40, heal_pct=20)]),
    "n15b": ("prevention", "Soins preventifs", "+15 % de soins sur une cible au-dessus de 70 % de ses PV.",
             [mech("heal_bonus_target_hp_above", hp_pct=70, heal_pct=15)]),
    "side15": ("extended_heal", "Soin etendu", "Un soin cible soigne aussi l'allie blesse le plus proche de 30 % du soin.",
               [mech("heal_splash_nearest_ally", ratio_pct=30, skill_filter="single_target_heal")]),
    "ra1": ("fervor", "Ferveur", "+3 % de puissance de soin par rang.", [flat("heal_power", 3)]),
    "ra2": ("reserve", "Reserve", "+12 Souffle max par rang.", [flat("mp", 12)]),
    "rb1": ("wisdom", "Sagesse", "+2 % de magie par rang.", [pct("mag", 2)]),
    "rb2": ("aegis_craft", "Art du bouclier", "+2 % de puissance de bouclier par rang.", [flat("shield_power", 2)]),
    "n30a": ("transfusion", "Transfusion", "10 % des soins donnes a un allie te reviennent.",
             [mech("heal_return_to_caster", ratio_pct=10)]),
    "n30b": ("spell_vamp", "Vol de sort", "+8 % de vol de sort.", [once("spell_vamp", 8)]),
    "n30c": ("holy_shield", "Egide sacree", "+15 % de puissance de bouclier et +10 % de soins recus.",
             [once("shield_power", 15), once("healing_received", 10)]),
    "rc1": ("quick_prayer", "Priere rapide", "+2 % de vitesse d'incantation par rang.", [flat("cast_speed", 2)]),
    "rc2": ("perseverance", "Perseverance", "+1 % de reduction de recharge par rang.", [flat("cooldown_reduction", 1)]),
    "rc3": ("devotion", "Recueillement", "+2 % de soins recus par rang.", [flat("healing_received", 2)]),
    "rd1": ("divine_grace", "Grace divine", "+2 % de magie par rang.", [pct("mag", 2)]),
    "rd2": ("fountain", "Fontaine", "+3 % de Souffle max par rang.", [pct("mp", 3)]),
    "rd3": ("radiance", "Rayonnement", "+3 % de puissance de bouclier par rang.", [flat("shield_power", 3)]),
    "n50a": ("last_breath", "Dernier souffle", "Une fois par combat, un allie qui devait mourir reste a 1 PV et recoit 25 % de ses PV max.",
             [mech("prevent_ally_death", heal_pct=25, per_combat=1)]),
    "n50b": ("downpour", "Ondee", "Un soin cible soigne aussi les 2 allies blesses les plus proches de 25 % du soin.",
             [mech("heal_splash_nearest_ally", ratio_pct=25, count=2, skill_filter="single_target_heal")]),
    "side50": ("prayer", "Priere de combat", "Chaque soin lance donne +3 % de puissance de soin pendant 6 s, cumulable 5 fois.",
               [mech("stacking_stat_on_event", event="heal_cast", stat="heal_power", value_per_stack=3, max_stacks=5, duration_s=6)]),
    "m1": ("m_heal", "Maitrise : soins", "+2 % de puissance de soin par rang.", [flat("heal_power", 2)]),
    "m2": ("m_wisdom", "Maitrise : sagesse", "+2 % de magie par rang.", [pct("mag", 2)]),
    "m3": ("m_source", "Maitrise : source", "+3 % de Souffle max par rang.", [pct("mp", 3)]),
    "megaa": ("mega_sanctuary", "Sanctuaire",
              "+30 % de puissance de soin et +25 % de duree des buffs (soins sur la duree compris). Contrepartie : -30 % de degats infliges.",
              [once("heal_power", 30), once("buff_duration", 25), once("damage_percent", -30)]),
    "megab": ("mega_martyr", "Martyr",
              "+40 % de puissance de soin et +20 % de soins recus. Contrepartie : -20 % de PV max.",
              [once("heal_power", 40), once("healing_received", 20), once("hp", -20, "add_percent")]),
})

ARMS["support"] = ("sup", {
    "e1": ("persistence", "Persistance", "+2 % de duree des buffs par rang.", [flat("buff_duration", 2)]),
    "e2": ("liveliness", "Vivacite", "+2 % de vitesse d'incantation par rang.", [flat("cast_speed", 2)]),
    "e3": ("long_breath", "Souffle long", "+10 Souffle max par rang.", [flat("mp", 10)]),
    "e4": ("will", "Volonte", "+2 resistance aux effets par rang.", [flat("effect_resist", 2)]),
    "n15a": ("inspiration", "Inspiration", "Un allie que tu buffes inflige +8 % de degats pendant le buff.",
             [mech("buff_grants_stat", stat="damage_percent", value=8)]),
    "n15b": ("protection", "Protection", "Un allie que tu buffes subit -8 % de degats pendant le buff.",
             [mech("buff_grants_stat", stat="damage_reduction", value=8)]),
    "side15": ("extended_aura", "Aura etendue", "Un buff cible touche aussi un allie adjacent.",
               [mech("buff_splash_adjacent_ally", skill_filter="single_target_buff")]),
    "ra1": ("swift_mind", "Esprit vif", "+1 % de reduction de recharge par rang.", [flat("cooldown_reduction", 1)]),
    "ra2": ("tenacity", "Tenacite", "+2 tenacite par rang.", [flat("tenacity", 2)]),
    "rb1": ("clarity", "Clarte", "+3 % de Souffle max par rang.", [pct("mp", 3)]),
    "rb2": ("harmony", "Harmonie", "+2 % de magie par rang.", [pct("mag", 2)]),
    "n30a": ("rhythm", "Rythme", "Un sort sur 4 qui coute du Souffle est gratuit.",
             [mech("free_cast_every_n", n=4)]),
    "n30b": ("conductor", "Chef d'orchestre", "Buffer un allie reduit ses recharges de 1 s (une fois toutes les 5 s par allie).",
             [mech("cooldown_reduction_on_event", event="buff_applied_to_ally", seconds=1, scope="buffed_ally", internal_cooldown_s=5)]),
    "n30c": ("foresight", "Clairvoyance", "+15 % de duree des buffs et +10 % de duree des affaiblissements.",
             [once("buff_duration", 15), once("debuff_duration", 10)]),
    "rc1": ("serenity", "Serenite", "+2 % de duree des buffs par rang.", [flat("buff_duration", 2)]),
    "rc2": ("discipline", "Discipline", "+1 % de reduction de recharge par rang.", [flat("cooldown_reduction", 1)]),
    "rc3": ("firmness", "Fermete", "+2 resistance aux effets par rang.", [flat("effect_resist", 2)]),
    "rd1": ("eloquence", "Eloquence", "+2 % de vitesse d'incantation par rang.", [flat("cast_speed", 2)]),
    "rd2": ("breadth", "Ampleur", "+3 % de Souffle max par rang.", [pct("mp", 3)]),
    "rd3": ("presence", "Presence", "+2 % de PV max par rang.", [pct("hp", 2)]),
    "n50a": ("vanguard", "Chef de file", "Un allie que tu buffes inflige +6 % de degats et subit -6 % de degats pendant le buff.",
             [mech("buff_grants_stat", stat="damage_percent", value=6), mech("buff_grants_stat", stat="damage_reduction", value=6)]),
    "n50b": ("acceleration", "Acceleration", "Un allie que tu buffes a +15 % de vitesse d'incantation pendant le buff.",
             [mech("buff_grants_stat", stat="cast_speed", value=15)]),
    "side50": ("shared_drive", "Elan partage", "Chaque buff donne a un allie te donne +3 % de degats pendant 6 s, cumulable 5 fois.",
               [mech("stacking_stat_on_event", event="buff_applied_to_ally", stat="damage_percent", value_per_stack=3, max_stacks=5, duration_s=6)]),
    "m1": ("m_duration", "Maitrise : duree", "+3 % de duree des buffs par rang.", [flat("buff_duration", 3)]),
    "m2": ("m_tempo", "Maitrise : tempo", "+1 % de reduction de recharge par rang.", [flat("cooldown_reduction", 1)]),
    "m3": ("m_clarity", "Maitrise : clarte", "+3 % de Souffle max par rang.", [pct("mp", 3)]),
    "megaa": ("mega_warmaster", "Maitre de guerre",
              "Tes buffs sur les allies durent 50 % plus longtemps et donnent +10 % de degats. Contrepartie : -25 % de tes propres degats.",
              [once("buff_duration", 50), mech("buff_grants_stat", stat="damage_percent", value=10), once("damage_percent", -25)]),
    "megab": ("mega_haste", "Hate collective",
              "Un allie que tu buffes a -20 % de recharge pendant le buff. Contrepartie : -20 % de tes PV max.",
              [mech("buff_grants_stat", stat="cooldown_reduction", value=20), once("hp", -20, "add_percent")]),
})

ARMS["debuff"] = ("deb", {
    "e1": ("sure_hand", "Main sure", "+3 precision par rang.", [flat("hit", 3)]),
    "e2": ("venom", "Venin", "+2 % de chance d'effet par rang.", [flat("effect_chance", 2)]),
    "e3": ("lingering", "Prolongation", "+2 % de duree des affaiblissements par rang.", [flat("debuff_duration", 2)]),
    "e4": ("mind_piercer", "Perce-esprit", "+1,5 penetration magique par rang.", [flat("magic_pen", 1.5)]),
    "n15a": ("grip", "Emprise", "+10 % de degats contre une cible sous controle.",
             [mech("damage_vs_target_with_status", status_category="control", damage_pct=10)]),
    "n15b": ("plague_touch", "Fleau", "+12 % de degats contre une cible qui porte au moins 2 affaiblissements.",
             [mech("damage_vs_target_debuff_count", min_debuffs=2, damage_pct=12)]),
    "side15": ("contagion", "Contagion", "Quand une cible meurt, tes affaiblissements passent sur l'ennemi le plus proche.",
               [mech("debuff_spread_on_death", max_spread=1)]),
    "ra1": ("shadows", "Tenebres", "+2 % de chance d'effet par rang.", [flat("effect_chance", 2)]),
    "ra2": ("haste", "Hate", "+1 % de reduction de recharge par rang.", [flat("cooldown_reduction", 1)]),
    "rb1": ("malice", "Malice", "+2 % d'attaque et +2 % de magie par rang.", [pct("atk", 2), pct("mag", 2)]),
    "rb2": ("corruption", "Corruption", "+2 % de duree des affaiblissements par rang.", [flat("debuff_duration", 2)]),
    "n30a": ("control_zone", "Zone de controle", "Un controle cible touche aussi un ennemi adjacent.",
             [mech("control_splash_adjacent", skill_filter="single_target_control")]),
    "n30b": ("tempo_master", "Maitre du tempo", "Controler un ennemi reduit tes autres recharges de 1 s (une fois toutes les 3 s).",
             [mech("cooldown_reduction_on_event", event="control_applied", seconds=1, scope="other_skills", internal_cooldown_s=3)]),
    "n30c": ("deep_venom", "Venin profond", "+15 % de chance d'effet et +10 % de duree des affaiblissements.",
             [once("effect_chance", 15), once("debuff_duration", 10)]),
    "rc1": ("fatality", "Fatalite", "+2 % de chance d'effet par rang.", [flat("effect_chance", 2)]),
    "rc2": ("dark_persistence", "Persistance noire", "+2 % de duree des affaiblissements par rang.", [flat("debuff_duration", 2)]),
    "rc3": ("armor_breaker", "Brise-armure", "+1,5 penetration d'armure et +1,5 penetration magique par rang.",
            [flat("armor_pen", 1.5), flat("magic_pen", 1.5)]),
    "rd1": ("curse", "Malediction", "+2 % d'attaque et +2 % de magie par rang.", [pct("atk", 2), pct("mag", 2)]),
    "rd2": ("affliction", "Affliction", "+1 % de degats infliges par rang.", [flat("damage_percent", 1)]),
    "rd3": ("hex", "Malefice", "+3 % de duree des affaiblissements par rang.", [flat("debuff_duration", 3)]),
    "n50a": ("torment", "Supplice", "+4 % de degats par affaiblissement que porte la cible, jusqu'a 5.",
             [mech("damage_vs_target_debuff_count", per_debuff=True, damage_pct=4, max_debuffs=5)]),
    "n50b": ("vise", "Etau", "+15 % de degats et +10 % de chance critique contre une cible sous controle.",
             [mech("damage_vs_target_with_status", status_category="control", damage_pct=15),
              mech("stat_vs_target_with_status", status_category="control", stat="crit", value=10)]),
    "side50": ("will_breaker", "Brise-volonte", "Apres avoir controle un ennemi : +15 % de chance d'effet pendant 4 s.",
               [mech("stat_window_after_event", event="control_applied", stat="effect_chance", value=15, duration_s=4)]),
    "m1": ("m_grip", "Maitrise : emprise", "+2 % de chance d'effet par rang.", [flat("effect_chance", 2)]),
    "m2": ("m_duration", "Maitrise : duree", "+3 % de duree des affaiblissements par rang.", [flat("debuff_duration", 3)]),
    "m3": ("m_malice", "Maitrise : malice", "+2 % d'attaque et +2 % de magie par rang.", [pct("atk", 2), pct("mag", 2)]),
    "megaa": ("mega_plague", "Peste",
              "Un affaiblissement pose par un sort cible touche aussi un ennemi adjacent (sans relance en chaine). Contrepartie : tes affaiblissements durent 25 % de moins.",
              [mech("control_splash_adjacent", skill_filter="single_target_debuff", status_category="harmful"), once("debuff_duration", -25)]),
    "megab": ("mega_chains", "Seigneur des chaines",
              "+40 % de duree des affaiblissements et +20 % de chance d'effet. Contrepartie : -25 % de degats infliges.",
              [once("debuff_duration", 40), once("effect_chance", 20), once("damage_percent", -25)]),
})

# Ponts manquants (Attaque <-> Defense et Attaque <-> Affaiblissement existent deja).
# (bras A, bras B, prefixe, passage, hybride principal, hybride a cote)
BRIDGES = [
    ("defense", "healing", "def_heal",
     ("Passage", "+12 PV max et +2 % de soins recus.", [flat("hp", 12), flat("healing_received", 2)]),
     ("Rempart vivant", "10 % des soins que tu recois deviennent un bouclier (5 s).",
      [mech("shield_from_healing_received", ratio_pct=10)]),
     ("Second elan", "Sous 25 % de PV : bouclier egal a 15 % de tes PV max. Une fois toutes les 60 s.",
      [mech("shield_on_low_hp", hp_pct=25, shield_pct_max_hp=15, internal_cooldown_s=60)])),
    ("healing", "support", "heal_sup",
     ("Passage", "+10 Souffle max et +2 % de duree des buffs.", [flat("mp", 10), flat("buff_duration", 2)]),
     ("Chant de guerre", "Un buff donne a un allie lui retire un affaiblissement.",
      [mech("buff_cleanses_debuff", count=1)]),
     ("Benediction", "Un allie que tu buffes recoit +10 % de soins pendant le buff.",
      [mech("buff_grants_stat", stat="healing_received", value=10)])),
    ("support", "debuff", "sup_deb",
     ("Passage", "+2 % de chance d'effet et +2 resistance aux effets.", [flat("effect_chance", 2), flat("effect_resist", 2)]),
     ("Coordination", "Un allie que tu buffes inflige +8 % de degats aux cibles que tu as affaiblies.",
      [mech("ally_buffed_bonus_vs_debuffed", damage_pct=8)]),
     ("Marque du chef", "Un allie que tu buffes a +10 % de chance critique contre les cibles que tu as affaiblies.",
      [mech("ally_buffed_bonus_vs_debuffed", crit=10)])),
]

# Mecaniques qui n'existent pas encore cote combat (a ajouter a la liste du document).
# Plus aucune mecanique entierement nouvelle dans les 4 bras proposes : seulement des EXTENSIONS d'une
# mecanique deja codee (un parametre, un evenement ou une stat de plus). Celles du bras Attaque (ecrit par
# le proprietaire) sont listees a part dans le document.
NEW_MECHANICS = [
    "damage_taken_reduction_conditional: condition hp_below (Dernier rempart)",
    "stat_window_after_event: evenements block_or_parry, control_applied (Mur vivant, Brise-volonte) ; stats damage_reduction, effect_chance",
    "heal_bonus_target_hp_above: miroir de heal_bonus_target_hp_below (Soins preventifs)",
    "heal_splash_nearest_ally: parametre count (Ondee)",
    "stacking_stat_on_event: evenement heal_cast, stat heal_power (Priere de combat) ; evenement buff_applied_to_ally (Elan partage)",
    "buff_grants_stat: stats damage_reduction, cast_speed, cooldown_reduction, healing_received (Protection, Chef de file, Acceleration, Hate collective, Benediction)",
    "damage_vs_target_debuff_count: mode per_debuff (Supplice)",
    "control_splash_adjacent: status_category harmful (Peste)",
    "ally_buffed_bonus_vs_debuffed: parametre crit (Marque du chef)",
]

ARM_META = {a["id"]: a for a in src["arms"]}
V1_ANGLES = {"attack": -90, "defense": -18, "healing": 54, "support": 126, "debuff": 198}
V1_COLORS = {"attack": "#e66b52", "defense": "#5c99e6", "healing": "#5cc78f", "support": "#f2b84d", "debuff": "#a875e6"}
NAMES = {"attack": ("Attaque", "Attack"), "defense": ("Defense", "Defense"), "healing": ("Soin", "Healing"),
         "support": ("Soutien", "Support"), "debuff": ("Affaiblissement", "Weakening")}
RING = ["attack", "defense", "healing", "support", "debuff"]


def to_world(arm, along, lateral):
    t = math.radians(V1_ANGLES[arm])
    x = along * math.cos(t) - lateral * math.sin(t)
    y = along * math.sin(t) + lateral * math.cos(t)
    return [round(x, 2), round(y, 2)]


def local_of(atk_node):
    x, y = atk_node["pos"]
    return -y, x  # along, lateral (Attaque pointe vers -y)


nodes = [n for n in src["nodes"]]  # Attaque recopiee telle quelle
edges = []
notable30 = {"attack": ["pt2_atk_killer_instinct", "pt2_atk_breach", "pt2_atk_momentum"]}

for arm, (pfx, content) in ARMS.items():
    assert set(content) == set(SLOTS), (arm, set(SLOTS) ^ set(content))
    ids = {}
    for slot, (key, name, desc, effects) in content.items():
        tpl = ATK[f"pt2_atk_{SLOTS[slot]}"]
        nid = f"pt2_{pfx}_{key}"
        ids[slot] = nid
        node = {"id": nid, "kind": tpl["kind"], "arm": arm}
        if "max_rank" in tpl:
            node["max_rank"] = tpl["max_rank"]
        node["pos"] = to_world(arm, *local_of(tpl))
        if "choice" in tpl:
            group = next(g for g, members in GROUPS.items() if slot in members)
            node["choice"] = {"group": f"{pfx}_{group}", "option": key}
        node["name_fr"] = name
        node["description_fr"] = desc
        node["effects"] = effects
        nodes.append(node)
    # Aretes : celles du gabarit Attaque, traduites emplacement par emplacement.
    for a, b in src["edges"]:
        if a == "pt_center" and b in SLOT_OF:
            edges.append(["pt_center", ids[SLOT_OF[b]]])
        elif a in SLOT_OF and b in SLOT_OF:
            edges.append([ids[SLOT_OF[a]], ids[SLOT_OF[b]]])
    notable30[arm] = [ids["n30a"], ids["n30b"], ids["n30c"]]

# Aretes d'Attaque, ponts rebranches sur les vrais notables 30 des voisins.
CLONE_TO_REAL = {}
for arm, pfx in (("defense", "def"), ("debuff", "deb")):
    for clone, real in zip(("killer_instinct", "breach", "momentum"), notable30[arm]):
        CLONE_TO_REAL[f"pt2_{pfx}_{clone}"] = real
for a, b in src["edges"]:
    edges.append([CLONE_TO_REAL.get(a, a), CLONE_TO_REAL.get(b, b)])

# Ponts d'Attaque : memes regles et memes noeuds, seules les POSITIONS de dessin sont recalculees comme
# celles des autres ponts (la ligne horizontale du brouillon croisait le dessin des bras voisins).
def bridge_layout(arm_a, arm_b):
    pa, pb = to_world(arm_a, 11, 0), to_world(arm_b, 11, 0)
    lerp = lambda t: [round(pa[0] + (pb[0] - pa[0]) * t, 2), round(pa[1] + (pb[1] - pa[1]) * t, 2)]
    mid = lerp(0.5)
    norm = math.hypot(*mid) or 1
    side = [round(mid[0] + mid[0] / norm * 1.5, 2), round(mid[1] + mid[1] / norm * 1.5, 2)]
    return lerp(0.3), mid, lerp(0.7), side


for other, key in (("defense", "atk_def"), ("debuff", "atk_deb")):
    pos = bridge_layout("attack", other)
    for nid, pp in zip((f"pt2_brg_{key}_a", f"pt2_hyb_{key}", f"pt2_brg_{key}_b", f"pt2_hyb_{key}_side"), pos):
        node = next(n for n in nodes if n["id"] == nid)
        nodes[nodes.index(node)] = dict(node, pos=pp)

# Ponts manquants : passage, hybride, passage entre les notables 30 des deux bras.
for arm_a, arm_b, key, passage, hyb, hyb_side in BRIDGES:
    pa = to_world(arm_a, 11, 0)
    pb = to_world(arm_b, 11, 0)
    lerp = lambda t: [round(pa[0] + (pb[0] - pa[0]) * t, 2), round(pa[1] + (pb[1] - pa[1]) * t, 2)]
    mid = lerp(0.5)
    norm = math.hypot(*mid) or 1
    side_pos = [round(mid[0] + mid[0] / norm * 1.5, 2), round(mid[1] + mid[1] / norm * 1.5, 2)]
    ba, h, bb, hs = (f"pt2_brg_{key}_a", f"pt2_hyb_{key}", f"pt2_brg_{key}_b", f"pt2_hyb_{key}_side")
    for nid, kind, pos, (name, desc, eff) in (
        (ba, "bridge_small", lerp(0.3), passage), (h, "hybrid", mid, hyb),
        (bb, "bridge_small", lerp(0.7), passage), (hs, "hybrid", side_pos, hyb_side)):
        n = {"id": nid, "kind": kind, "arm": None, "arms": [arm_a, arm_b]}
        if kind == "bridge_small":
            n["max_rank"] = 1
        n.update({"pos": pos, "name_fr": name, "description_fr": desc, "effects": eff})
        nodes.append(n)
    for n30 in notable30[arm_a]:
        edges.append([n30, ba])
    edges += [[ba, h], [h, bb], [h, hs]]
    for n30 in notable30[arm_b]:
        edges.append([bb, n30])

out = dict(src)
out["_meta"] = dict(src["_meta"], version="2.2-brouillon", last_updated="2026-10-16",
                    description=src["_meta"]["description"].replace("Regles + bras Attaque seul", "Regles + les 5 bras + les 5 ponts"),
                    generator="gen_arbre_v2.py : bras Attaque recopie de arbre_v2_attaque.json (proprietaire), "
                              "4 autres bras et 3 ponts generes sur son gabarit (memes rangs, couts et aretes).",
                    simulation="python -I _meta/conception_passifs/sim_arbre_v2.py _meta/conception_passifs/arbre_v2.json",
                    new_mechanics=NEW_MECHANICS)
out["arms"] = [{"id": a, "name_fr": NAMES[a][0], "name_en": NAMES[a][1], "color": V1_COLORS[a],
                "angle_deg": V1_ANGLES[a], "neighbors": [RING[(i - 1) % 5], RING[(i + 1) % 5]]}
               for i, a in enumerate(RING)]
out["nodes"] = nodes
out["edges"] = edges

ids = {n["id"] for n in nodes}
missing = [e for e in edges if e[0] not in ids or e[1] not in ids]
assert not missing, missing
assert len(ids) == len(nodes), "id en double"
json.dump(out, open(os.path.join(HERE, "arbre_v2.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
print(f"arbre_v2.json : {len(nodes)} noeuds, {len(edges)} aretes, {len(NEW_MECHANICS)} mecaniques nouvelles")
