"""Add the 12 missing status effect definitions to status_effects.json."""
import json
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open("stats/status_effects.json", "r", encoding="utf-8") as f:
    data = json.load(f)

effects = data["effects"]

# 1. CHILL — DoT category (slow + light magical damage, Elementalist)
if "chill" not in effects.get("dot", {}):
    effects["dot"]["chill"] = {
        "name_fr": "Froid",
        "name_en": "Chill",
        "polarity": "debuff",
        "stacking": "stackable",
        "max_stacks": 3,
        "impl": "todo",
        "damage_type": "magical",
        "formula": "MAG * 0.1 per tick per stack + 10% slow",
        "tick_interval": 1.0,
        "tooltip_fr": "Ralentit et inflige de legers degats magiques.\nSe cumule.",
        "tooltip_en": "Slows and deals light magical damage.\nStacks.",
        "description_fr": "Ralentit la cible de 10% par charge et inflige de legers degats magiques par seconde. Max 3 charges.",
        "description_en": "Slows the target by 10% per stack and deals light magical damage per second. Max 3 stacks.",
        "sources": ["Mage (Elementalist)"],
        "runtime": {
            "tick_damage": "value",
            "tick_rate": 1.0,
            "stat_modifier": {"attack_speed": "-value/100"},
            "vfx_type": "frost_aura"
        }
    }
    print("Added: chill (DoT)")

# 2. CORRUPTION — DoT category (dark magic DoT, Occultist)
if "corruption" not in effects.get("dot", {}):
    effects["dot"]["corruption"] = {
        "name_fr": "Corruption",
        "name_en": "Corruption",
        "polarity": "debuff",
        "stacking": "stackable",
        "max_stacks": 5,
        "impl": "todo",
        "damage_type": "magical",
        "formula": "MAG * 0.15 per tick per stack",
        "tick_interval": 1.0,
        "tooltip_fr": "Corrompt la cible, infligeant des degats magiques croissants.\nSe cumule.",
        "tooltip_en": "Corrupts the target, dealing increasing magical damage.\nStacks.",
        "description_fr": "Inflige des degats magiques par seconde par charge. Max 5 charges. Plus de charges = plus de degats.",
        "description_en": "Deals magical damage per second per stack. Max 5 stacks. More stacks = more damage.",
        "sources": ["Mage (Occultist)"],
        "runtime": {
            "tick_damage": "value",
            "tick_rate": 1.0,
            "vfx_type": "dark_corruption"
        }
    }
    print("Added: corruption (DoT)")

# 3. TOXIN — DoT category (alchemist poison stacks, detonatable)
if "toxin" not in effects.get("dot", {}):
    effects["dot"]["toxin"] = {
        "name_fr": "Toxine",
        "name_en": "Toxin",
        "polarity": "debuff",
        "stacking": "stackable",
        "max_stacks": 10,
        "impl": "todo",
        "damage_type": "magical",
        "formula": "MAG * 0.1 per tick per stack",
        "tick_interval": 1.0,
        "tooltip_fr": "Empoisonne la cible. Les charges peuvent etre detonees.\nSe cumule.",
        "tooltip_en": "Poisons the target. Stacks can be detonated.\nStacks.",
        "description_fr": "Inflige de legers degats magiques par seconde par charge. Max 10 charges. Peut etre detone pour des degats massifs.",
        "description_en": "Deals light magical damage per second per stack. Max 10 stacks. Can be detonated for massive damage.",
        "sources": ["Artisan (Alchemist)"],
        "runtime": {
            "tick_damage": "value",
            "tick_rate": 1.0,
            "detonatable": True,
            "vfx_type": "poison_bubbles"
        }
    }
    print("Added: toxin (DoT)")

# 4. EXPOSED — stat_modifiers category (increased damage taken)
if "exposed" not in effects.get("stat_modifiers", {}):
    effects["stat_modifiers"]["exposed"] = {
        "name_fr": "Expose",
        "name_en": "Exposed",
        "polarity": "debuff",
        "stacking": "refresh",
        "impl": "todo",
        "formula": "+value% damage taken",
        "tooltip_fr": "Augmente les degats recus.",
        "tooltip_en": "Increases damage taken.",
        "description_fr": "La cible recoit value% de degats supplementaires de toutes les sources.",
        "description_en": "The target takes value% increased damage from all sources.",
        "sources": ["Rogue"],
        "runtime": {
            "stat_modifier": {"damage_taken": "value/100"},
            "vfx_type": "exposed_mark"
        }
    }
    print("Added: exposed (stat_modifier)")

# 5. CHALLENGED — special category (duelist forced 1v1)
if "challenged" not in effects.get("special", {}):
    effects["special"]["challenged"] = {
        "name_fr": "Defi",
        "name_en": "Challenged",
        "polarity": "debuff",
        "stacking": "unique",
        "impl": "todo",
        "formula": "Target can only attack the challenger",
        "tooltip_fr": "Force a attaquer le Duelliste.",
        "tooltip_en": "Forced to attack the Duelist.",
        "description_fr": "La cible ne peut attaquer que le Duelliste pendant la duree de l'effet.",
        "description_en": "The target can only attack the Duelist for the duration.",
        "sources": ["Rogue (Duelist)"],
        "runtime": {
            "forced_target": "caster",
            "vfx_type": "duel_mark"
        }
    }
    print("Added: challenged (special)")

# 6. EN_GARDE_STANCE — defensive category (counter stance)
if "en_garde_stance" not in effects.get("defensive", {}):
    effects["defensive"]["en_garde_stance"] = {
        "name_fr": "En Garde",
        "name_en": "En Garde Stance",
        "polarity": "buff",
        "stacking": "unique",
        "impl": "todo",
        "formula": "+value% parry chance, counter on parry",
        "tooltip_fr": "Posture defensive. Chance de parade augmentee et contre-attaque automatique.",
        "tooltip_en": "Defensive stance. Increased parry chance and automatic counter on parry.",
        "description_fr": "Augmente la chance de parade de value%. Chaque parade declenche une contre-attaque automatique.",
        "description_en": "Increases parry chance by value%. Each parry triggers an automatic counter-attack.",
        "sources": ["Rogue (Duelist)"],
        "runtime": {
            "stat_modifier": {"parry_chance": "value/100"},
            "on_parry": "counter_attack",
            "vfx_type": "stance_glow"
        }
    }
    print("Added: en_garde_stance (defensive)")

# 7. RIPOSTE_ACTIVE — defensive category (reflect next attack)
if "riposte_active" not in effects.get("defensive", {}):
    effects["defensive"]["riposte_active"] = {
        "name_fr": "Riposte",
        "name_en": "Riposte Active",
        "polarity": "buff",
        "stacking": "unique",
        "impl": "todo",
        "formula": "Reflects value% of next attack back to attacker",
        "tooltip_fr": "Renvoie une partie des degats de la prochaine attaque recue.",
        "tooltip_en": "Reflects part of the next attack received back to the attacker.",
        "description_fr": "Renvoie value% des degats de la prochaine attaque recue a l'attaquant.",
        "description_en": "Reflects value% of the next attack's damage back to the attacker.",
        "sources": ["Rogue (Duelist)"],
        "runtime": {
            "on_hit_taken": "reflect_damage",
            "reflect_percent": "value/100",
            "consume_on_trigger": True,
            "vfx_type": "riposte_flash"
        }
    }
    print("Added: riposte_active (defensive)")

# 8. TAUNT_REDIRECT — control category (redirect attacks)
if "taunt_redirect" not in effects.get("control", {}):
    effects["control"]["taunt_redirect"] = {
        "name_fr": "Redirection",
        "name_en": "Taunt Redirect",
        "polarity": "debuff",
        "stacking": "unique",
        "impl": "todo",
        "formula": "Target attacks are redirected to an ally",
        "tooltip_fr": "Les attaques de la cible sont redirigees.",
        "tooltip_en": "The target's attacks are redirected.",
        "description_fr": "Force la cible a attaquer un allie choisi par le Trickster au lieu de sa cible originale.",
        "description_en": "Forces the target to attack an ally chosen by the Trickster instead of their original target.",
        "sources": ["Rogue (Trickster)"],
        "runtime": {
            "forced_target": "redirect_to_ally",
            "vfx_type": "confusion_swirl"
        }
    }
    print("Added: taunt_redirect (control)")

# 9. STEAL_BUFF — special category (steal buffs from target)
if "steal_buff" not in effects.get("special", {}):
    effects["special"]["steal_buff"] = {
        "name_fr": "Vol de Buff",
        "name_en": "Buff Steal",
        "polarity": "debuff",
        "stacking": "unique",
        "impl": "todo",
        "formula": "Steals value random buffs from target",
        "tooltip_fr": "Vole des buffs a la cible.",
        "tooltip_en": "Steals buffs from the target.",
        "description_fr": "Vole value buff(s) aleatoire(s) de la cible et les applique au lanceur.",
        "description_en": "Steals value random buff(s) from the target and applies them to the caster.",
        "sources": ["Rogue (Trickster, Corsair)"],
        "runtime": {
            "action": "steal_random_buffs",
            "count": "value",
            "vfx_type": "steal_sparkle"
        }
    }
    print("Added: steal_buff (special)")

# 10. MANA_STEAL — special category (steal Breath)
if "mana_steal" not in effects.get("special", {}):
    effects["special"]["mana_steal"] = {
        "name_fr": "Vol de Souffle",
        "name_en": "Breath Steal",
        "polarity": "debuff",
        "stacking": "unique",
        "impl": "todo",
        "formula": "Steals value Breath from target",
        "tooltip_fr": "Vole du Souffle a la cible.",
        "tooltip_en": "Steals Breath from the target.",
        "description_fr": "Vole value points de Souffle a la cible et les transfère au lanceur.",
        "description_en": "Steals value Breath from the target and transfers it to the caster.",
        "sources": ["Mage", "Rogue (Corsair)"],
        "runtime": {
            "action": "transfer_mp",
            "amount": "value",
            "vfx_type": "mana_drain_swirl"
        }
    }
    print("Added: mana_steal (special)")

# 11. MANA_RESTORE — special category (restore Breath to allies)
if "mana_restore" not in effects.get("special", {}):
    effects["special"]["mana_restore"] = {
        "name_fr": "Restauration de Souffle",
        "name_en": "Breath Restore",
        "polarity": "buff",
        "stacking": "unique",
        "impl": "todo",
        "formula": "Restores value Breath to target",
        "tooltip_fr": "Restaure du Souffle.",
        "tooltip_en": "Restores Breath.",
        "description_fr": "Restaure value points de Souffle a la cible.",
        "description_en": "Restores value Breath to the target.",
        "sources": ["Artisan"],
        "runtime": {
            "action": "restore_mp",
            "amount": "value",
            "vfx_type": "breath_restore"
        }
    }
    print("Added: mana_restore (special)")

# 12. INTERRUPT — control category (cancel cast)
if "interrupt" not in effects.get("control", {}):
    effects["control"]["interrupt"] = {
        "name_fr": "Interruption",
        "name_en": "Interrupt",
        "polarity": "debuff",
        "stacking": "unique",
        "impl": "todo",
        "formula": "Cancels current cast",
        "tooltip_fr": "Interrompt l'incantation en cours.",
        "tooltip_en": "Interrupts the current cast.",
        "description_fr": "Annule l'incantation en cours de la cible. N'a pas d'effet si la cible ne lance rien.",
        "description_en": "Cancels the target's current cast. Has no effect if the target is not casting.",
        "sources": ["Archer (Gunslinger, Ballmaster)"],
        "runtime": {
            "action": "cancel_cast",
            "vfx_type": "interrupt_spark"
        }
    }
    print("Added: interrupt (control)")

with open("stats/status_effects.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("\nDone! 12 missing status effects added.")
