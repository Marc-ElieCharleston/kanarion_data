# Skills "level-trap" — liste à reviewer avec le designer

**Total** : 129 skills flaggés par `scripts/lint_useless_level.py`

## Question à poser pour CHAQUE skill

1. Est-ce intentionnel que ce skill ne scale rien quand on le monte ?
   - **Oui (utilitaire pur, durée fixe, etc.)** → mettre `mana_cost_per_level: 0` pour cohérence (sinon le joueur paye plus cher sans gain)
   - **Non, devrait scaler** → choisir la mécanique à scaler et lui donner un `*_per_level` positif :
     - Damage : `power_per_level` (base flat) ou `percent_per_level` (scaling %)
     - Heal : `power_per_level` (base flat sur heal_base)
     - Effet buff/debuff : `effect_power_per_level`
     - Durée statut : `duration_per_level`
     - Shield : `shield_value_per_level`
     - HoT durée : `hot_duration_per_level`

## Skills par classe

### ARCHER (12 skills)

| Skill ID | Tier | Cat | Mana/lvl | Mécanique actuelle | Action proposée |
|----------|------|-----|----------|---------------------|------------------|
| `eagle_eye` | basic | none | 2 | effects=2 | _à décider_ |
| `hunter_mark` | basic | none | 1 | effects=2 | _à décider_ |
| `ranger_steady_aim` | strong | none | (def +4) | effects=1 | _à décider_ |
| `sharpshooter_focus` | advanced | none | 2 | effects=3 | _à décider_ |
| `skirmisher_tactical_evade` | advanced | none | 2 | effects=2 | _à décider_ |
| `falconer_wing_guard` | strong | none | (def +4) | effects=1 | _à décider_ |
| `wind_hunter_aerial_guard` | advanced | none | 2 | effects=3 | _à décider_ |
| `bouncer_precise_calculation` | advanced | none | 2 | effects=2 | _à décider_ |
| `striker_frantic_cadence` | advanced | none | 2 | effects=3 | _à décider_ |
| `gunslinger_rapid_fire` | strong | none | (def +4) | effects=3 | _à décider_ |
| `quickshot_frenzy` | advanced | none | 2 | effects=3 | _à décider_ |
| `deadeye_dead_eye` | advanced | none | 2 | effects=3 | _à décider_ |

### ARTISAN (18 skills)

| Skill ID | Tier | Cat | Mana/lvl | Mécanique actuelle | Action proposée |
|----------|------|-----|----------|---------------------|------------------|
| `work_rhythm` | standard | none | 2 | effects=1 | _à décider_ |
| `expose_flaw` | standard | none | 2 | effects=1 | _à décider_ |
| `blacksmith_metalguard` | strong | none | (def +4) | effects=3 | _à décider_ |
| `forgemaster_reinforced_plate` | advanced | none | 1 | effects=1 | _à décider_ |
| `forgemaster_iron_wall` | advanced | none | 2 | effects=2 | _à décider_ |
| `forgemaster_living_forge` | advanced | none | 3 | effects=2 | _à décider_ |
| `forgemaster_stoicism` | advanced | none | 3 | effects=3 | _à décider_ |
| `forgemaster_living_fortress` | signature | none | 4 | effects=3 | _à décider_ |
| `chef_energy_snack` | strong | none | (def +4) | effects=2 | _à décider_ |
| `chef_warming_broth` | strong | none | (def +4) | effects=2 | _à décider_ |
| `battle_cook_power_dish` | advanced | none | 1 | effects=2 | _à décider_ |
| `battle_cook_steady_course` | advanced | none | 2 | effects=1 | _à décider_ |
| `musician_rallying_melody` | standard | none | (def +4) | effects=2 | _à décider_ |
| `musician_tempo_shift` | strong | none | (def +4) | effects=2 | _à décider_ |
| `musician_grand_performance` | signature | none | (def +4) | effects=2 | _à décider_ |
| `guitarist_heroic_anthem` | advanced | none | 1 | effects=2 | _à décider_ |
| `guitarist_clear_chorus` | advanced | none | 2 | effects=1 | _à décider_ |
| `guitarist_gentle_cadence` | advanced | none | 2 | effects=1 | _à décider_ |

### FAMILIAR (7 skills)

| Skill ID | Tier | Cat | Mana/lvl | Mécanique actuelle | Action proposée |
|----------|------|-----|----------|---------------------|------------------|
| `shrill_cry` | basic | none | 1 | effects=1 | _à décider_ |
| `bristled_fur` | advanced | none | 1 | effects=1 | _à décider_ |
| `restorative_lick` | filler | none | 1 | heal_scale=100% | _à décider_ |
| `soothing_aura` | basic | none | 1 | effects=1 | _à décider_ |
| `rescue_instinct` | advanced | none | 2 | heal_scale=200% / effects=1 | _à décider_ |
| `breath_screen` | filler | none | 1 | effects=1 | _à décider_ |
| `invigorating_presence` | basic | none | 1 | effects=1 | _à décider_ |

### HEALER (26 skills)

| Skill ID | Tier | Cat | Mana/lvl | Mécanique actuelle | Action proposée |
|----------|------|-----|----------|---------------------|------------------|
| `holy_shield` | strong | none | 2 | effects=2 | _à décider_ |
| `lifewarden_regrowth` | standard | none | (def +4) | effects=2 | _à décider_ |
| `lifewarden_vine_shield` | standard | none | (def +4) | effects=1 | _à décider_ |
| `lifewarden_regeneration` | strong | none | (def +4) | effects=2 | _à décider_ |
| `druidic_healer_bloom` | advanced | none | 2 | effects=1 | _à décider_ |
| `grove_warden_vine_shield` | advanced | none | 2 | effects=1 | _à décider_ |
| `grove_warden_thorn_wall` | advanced | none | 3 | effects=1 | _à décider_ |
| `grove_warden_sylvan_aura` | advanced | none | 3 | effects=2 | _à décider_ |
| `grove_warden_sylvan_fortress` | signature | none | 4 | effects=2 | _à décider_ |
| `lightbringer_sanctuary` | strong | none | (def +4) | effects=2 | _à décider_ |
| `lightbringer_bless` | standard | none | (def +4) | effects=1 | _à décider_ |
| `cantor_hymn_of_vigor` | basic | none | (def +4) | effects=1 | _à décider_ |
| `cantor_war_anthem` | strong | none | (def +4) | effects=1 | _à décider_ |
| `cantor_hymn_of_haste` | standard | none | (def +4) | effects=1 | _à décider_ |
| `cantor_sacred_ward` | strong | none | (def +4) | effects=3 | _à décider_ |
| `cantor_requiem` | signature | none | (def +4) | _aucune valeur mécanique_ | _à décider_ |
| `choirmaster_minor_hymn` | advanced | none | 1 | effects=2 | _à décider_ |
| `choirmaster_song_of_protection` | advanced | none | 2 | effects=2 | _à décider_ |
| `choirmaster_sacred_canticle` | advanced | none | 3 | effects=2 | _à décider_ |
| `martyr_intercession` | standard | none | (def +4) | dot=3%/s (6.0s) | _à décider_ |
| `martyr_intercession` | standard | none | (def +4) | dot=3%/s (6.0s) | _à décider_ |
| `martyr_sacred_pact` | standard | none | (def +4) | effects=1 | _à décider_ |
| `intercessor_stigma` | advanced | none | 3 | effects=2 | _à décider_ |
| `intercessor_martyrs_path` | advanced | none | 3 | effects=3 | _à décider_ |
| `covenant_breath_link` | advanced | none | 2 | effects=2 | _à décider_ |
| `covenant_communion` | advanced | none | 3 | effects=2 | _à décider_ |

### MAGE (9 skills)

| Skill ID | Tier | Cat | Mana/lvl | Mécanique actuelle | Action proposée |
|----------|------|-----|----------|---------------------|------------------|
| `mana_shield` | basic | none | 1 | effects=1 | _à décider_ |
| `elem_elemental_focus` | basic | none | (def +4) | effects=1 | _à décider_ |
| `card_lucky_draw` | basic | none | (def +4) | _aucune valeur mécanique_ | _à décider_ |
| `fate_gambler_double_or_nothing` | advanced | none | 2 | _aucune valeur mécanique_ | _à décider_ |
| `sb_enchanted_blade` | standard | none | (def +4) | effects=1 | _à décider_ |
| `sb_spell_guard` | standard | none | (def +4) | effects=1 | _à décider_ |
| `runeknight_warding_rune` | advanced | none | 2 | effects=2 | _à décider_ |
| `runeknight_runic_aura` | advanced | none | 3 | effects=2 | _à décider_ |
| `runeknight_runic_wall` | advanced | none | 3 | effects=2 | _à décider_ |

### PET_SKILLS (12 skills)

| Skill ID | Tier | Cat | Mana/lvl | Mécanique actuelle | Action proposée |
|----------|------|-----|----------|---------------------|------------------|
| `skill_pet_tank_shrill_cry` | basic | none | 3 | effects=1 | _à décider_ |
| `skill_pet_tank_bristle` | basic | none | 2 | effects=2 | _à décider_ |
| `skill_pet_tank_stubborn_stance` | filler | none | 1 | effects=2 | _à décider_ |
| `skill_pet_heal_lick` | filler | none | 2 | _aucune valeur mécanique_ | _à décider_ |
| `skill_pet_heal_aura` | basic | none | 3 | effects=1 | _à décider_ |
| `skill_pet_heal_vital_breath` | filler | none | 2 | effects=1 | _à décider_ |
| `skill_pet_heal_regen_wave` | advanced | none | 5 | effects=1 | _à décider_ |
| `skill_pet_heal_calming_embrace` | basic | none | 4 | effects=1 | _à décider_ |
| `skill_pet_utility_invigorate` | basic | none | 4 | effects=1 | _à décider_ |
| `skill_pet_utility_alert_cry` | filler | none | 2 | effects=1 | _à décider_ |
| `skill_pet_utility_light_step` | filler | none | 2 | effects=1 | _à décider_ |
| `skill_pet_utility_tactical_sniff` | basic | none | 3 | effects=1 | _à décider_ |

### ROGUE (12 skills)

| Skill ID | Tier | Cat | Mana/lvl | Mécanique actuelle | Action proposée |
|----------|------|-----|----------|---------------------|------------------|
| `mark_target` | standard | none | 2 | effects=2 | _à décider_ |
| `shadowblade_vanish` | strong | none | (def +4) | effects=1 | _à décider_ |
| `nightstalker_shadow_veil` | advanced | none | 2 | effects=1 | _à décider_ |
| `assassin_premeditation` | advanced | none | 2 | effects=2 | _à décider_ |
| `trickster_misdirection` | strong | none | (def +4) | effects=1 | _à décider_ |
| `trickster_grand_swindle` | signature | none | (def +4) | effects=1 | _à décider_ |
| `blinker_phase_step` | advanced | none | 2 | effects=2 | _à décider_ |
| `duelist_en_garde` | standard | none | (def +4) | effects=1 | _à décider_ |
| `duelist_riposte` | strong | none | (def +4) | effects=1 | _à décider_ |
| `blade_dancer_cadence` | advanced | none | 2 | effects=2 | _à décider_ |
| `countermaster_master_guard` | advanced | none | 2 | effects=2 | _à décider_ |
| `countermaster_perfect_counter` | signature | none | 3 | effects=3 | _à décider_ |

### WARRIOR (33 skills)

| Skill ID | Tier | Cat | Mana/lvl | Mécanique actuelle | Action proposée |
|----------|------|-----|----------|---------------------|------------------|
| `defensive_stance` | basic | none | 5 | effects=1 | _à décider_ |
| `taunting_shout` | standard | none | 6 | effects=1 | _à décider_ |
| `guardian_protect_ally` | standard | none | (def +4) | effects=4 | _à décider_ |
| `guardian_iron_stance` | strong | none | (def +4) | scaling=15% / effects=3 | _à décider_ |
| `guardian_barrier` | standard | none | (def +4) | scaling=10% / effects=1 | _à décider_ |
| `guardian_aegis_of_the_realm` | signature | none | (def +4) | effects=1 | _à décider_ |
| `bulwark_massive_presence` | advanced | none | 2 | effects=3 | _à décider_ |
| `bulwark_stone_form` | advanced | none | 2 | effects=4 | _à décider_ |
| `bulwark_last_bastion` | signature | none | 4 | effects=5 | _à décider_ |
| `sentinel_watch` | advanced | none | 1 | effects=1 | _à décider_ |
| `sentinel_protective_wing` | advanced | none | 2 | effects=2 | _à décider_ |
| `sentinel_wardship` | advanced | none | 3 | effects=4 | _à décider_ |
| `sentinel_selfless_vow` | advanced | none | 3 | effects=1 | _à décider_ |
| `sentinel_phalanx` | signature | none | 4 | effects=3 | _à décider_ |
| `berserker_bloodlust` | standard | none | (def +4) | effects=3 | _à décider_ |
| `berserker_frenzy` | strong | none | (def +4) | effects=3 | _à décider_ |
| `bloodrage_defiant_blood` | advanced | none | 2 | effects=3 | _à décider_ |
| `frenzied_warrior_trance` | advanced | none | 2 | effects=3 | _à décider_ |
| `weaponmaster_blade_stance` | standard | none | (def +4) | effects=1 | _à décider_ |
| `hammer_lord_forge_stance` | advanced | none | 2 | effects=3 | _à décider_ |
| `dual_axe_reaver_bloodthirst` | advanced | none | 2 | effects=3 | _à décider_ |
| `warlord_command_shout` | standard | none | (def +4) | effects=2 | _à décider_ |
| `warlord_weakening_roar` | basic | none | (def +4) | effects=2 | _à décider_ |
| `warlord_rally` | standard | none | (def +4) | effects=1 | _à décider_ |
| `warlord_war_banner` | signature | none | (def +4) | effects=3 | _à décider_ |
| `commander_battle_order` | advanced | none | 1 | effects=2 | _à décider_ |
| `commander_maneuver` | advanced | none | 2 | effects=2 | _à décider_ |
| `commander_chosen` | advanced | none | 3 | effects=4 | _à décider_ |
| `commander_coordination` | advanced | none | 3 | effects=2 | _à décider_ |
| `commander_call_to_glory` | signature | none | 4 | effects=5 | _à décider_ |
| `dreadlord_terror_cry` | advanced | none | 2 | effects=2 | _à décider_ |
| `dreadlord_suffocating_presence` | advanced | none | 3 | effects=3 | _à décider_ |
| `dreadlord_reign_of_terror` | signature | none | 4 | effects=4 | _à décider_ |

## Cas spécial : `dot-static` (1 skill)

| Skill ID | Détail | Action |
|----------|--------|--------|
| `skill_healer_martyr_intercession` | dot_percent=3, dot_duration=6, dot_heals_lowest_ally=true | Le schéma Skill n'a pas `dot_percent_per_level` ni `dot_duration_per_level`. Soit (a) ajouter ces champs côté `kanarion_front/scripts/skills/skill.gd` + loader, soit (b) ajouter `power_per_level` ou autre champ existant qui ferait scaler la mécanique par stats du caster. Décision design. |