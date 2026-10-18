# Données jamais lues : liste de candidats (2026-10-18)

Annexe de `rares_et_mecaniques_cases.md` §1. À traiter par l'agent maison : pour chaque clé, **vérifier**, puis brancher (si le design la veut) ou supprimer (règle « pas de données mortes, pas de doublon »).

## Méthode (heuristique, donc à vérifier une par une)

- Toutes les clés des JSON de `kanarion_database` (hors `_meta/`, `scripts/`, `out/`) ont été comparées aux identifiants présents dans le code C++ de `kanarion_back` et GDScript de `kanarion_client` (sans `build/`, `kanarion-meta/`, `addons/`).
- Une clé listée = son nom n'apparaît **nulle part** dans ce code.
- Retirés : les clés de documentation (`doc_*`, `note_*`, `lore_*`, `description*`, `name*`, `last_updated`, `formula*`, `design*`…) et les dictionnaires indexés par id (`<id>` dans les chemins = clé d'id parcourue en boucle).
- **Faux positifs possibles** : clés lues de façon générique (boucle sur tout un objet, jetons `[R]` des uniques, JSON pointers des keystones `runtime_scaling./triggers/...`), clés lues seulement par l'éditeur `kanarion-tool` ou les scripts Python de validation. Faux négatifs aussi : une clé au nom courant (`id`, `value`) peut être morte dans un fichier précis.
- Déjà confirmés morts à la main : `entities/monster_variants.json` `spawn_rules` (lu seulement par le client, qui tire un préfixe lui-même : `monster.gd:315`), `entities/boss_mechanics.json` entier côté serveur, `world/dungeons.json` `phases` (texte).
- Le script utilisé est en bas de ce fichier pour relancer l'analyse après corrections.

## Candidats par fichier (du plus chargé au moins chargé)

### `world/dungeons.json` (38)
`<id>.<id>.boss_wipe`, `<id>.<id>.difficulty_selection`, `<id>.<id>.hard.max_roll`, `<id>.<id>.hard.min_roll`, `<id>.<id>.heroic.max_roll`, `<id>.<id>.heroic.min_roll`, `<id>.<id>.individual_death`, `<id>.<id>.normal.max_roll`, `<id>.<id>.normal.min_roll`, `<id>.<id>.party_size_scaling`, `<id>.<id>.party_wipe`, `<id>[].boss.capture_profile`, `<id>[].difficulties.easy.guaranteed_substats`, `<id>[].difficulties.hard.guaranteed_substats`, `<id>[].difficulties.hard.key_source`, `<id>[].difficulties.heroic.guaranteed_substats`, `<id>[].difficulties.heroic.key_source`, `<id>[].difficulties.normal.guaranteed_substats`, `<id>[].duration_estimate_minutes`, `<id>[].entry_coordinates`, `<id>[].first_clear_bonus`, `<id>[].floors[].boss.base_monster`, `<id>[].floors[].environment_hazard`, `<id>[].floors[].floor_difficulty_modifier`, `<id>[].floors[].is_boss_room`, `<id>[].floors[][].mobs[].elite_type`, `<id>[].lockout_type`, `<id>[].loot_tables.key_drops`, `<id>[].loot_tables.lt_asher_tower_boss`, `<id>[].loot_tables.lt_asher_tower_elite` … +8

### `stats/definitions.json` (37)
`bonus_types`, `damage_pipeline`, `effect_system.effect_categories`, `stacking_system`, `stats.defensive.armor.bonus_type`, `stats.defensive.block_chance.bonus_type`, `stats.defensive.damage_reduction.bonus_type`, `stats.defensive.def.bonus_type`, `stats.defensive.effect_resist.bonus_type`, `stats.defensive.magic_resist.bonus_type`, `stats.defensive.parry_chance.bonus_type`, `stats.defensive.tenacity.bonus_type`, `stats.offensive.armor_pen.bonus_type`, `stats.offensive.atk.bonus_type`, `stats.offensive.attack_speed.bonus_type`, `stats.offensive.crit.bonus_type`, `stats.offensive.crit_dmg.bonus_type`, `stats.offensive.damage_percent.bonus_type`, `stats.offensive.debuff_duration.bonus_type`, `stats.offensive.double_hit_chance.bonus_type`, `stats.offensive.effect_chance.bonus_type`, `stats.offensive.mag.bonus_type`, `stats.offensive.magic_pen.bonus_type`, `stats.offensive.shield_break.bonus_type`, `stats.offensive.shield_pierce.bonus_type`, `stats.offensive.shield_pierce.implementation_status`, `stats.offensive.triple_hit_chance.bonus_type`, `stats.precision.flee.bonus_type`, `stats.precision.hit.bonus_type`, `stats.resources.hp.bonus_type` … +7

### `items/uniques.json` (36)
`drop_rule`, `droppable_uniques`, `naming_convention`, `total_uniques`, `uniques[].payoff_family`, `uniques[].rank_scaling.rang_1.bleed_bonus`, `uniques[].rank_scaling.rang_1.block_shield`, `uniques[].rank_scaling.rang_1.bond_charges`, `uniques[].rank_scaling.rang_1.bond_shown`, `uniques[].rank_scaling.rang_1.breach_charges`, `uniques[].rank_scaling.rang_1.breach_shown`, `uniques[].rank_scaling.rang_1.burn_bonus`, `uniques[].rank_scaling.rang_1.cast_charges`, `uniques[].rank_scaling.rang_1.cast_shown`, `uniques[].rank_scaling.rang_1.cd_cut`, `uniques[].rank_scaling.rang_1.crit_charges`, `uniques[].rank_scaling.rang_1.crit_dmg_charges`, `uniques[].rank_scaling.rang_1.crit_dmg_shown`, `uniques[].rank_scaling.rang_1.crit_shown`, `uniques[].rank_scaling.rang_1.dmg_charges`, `uniques[].rank_scaling.rang_1.dmg_shown`, `uniques[].rank_scaling.rang_1.double_hit`, `uniques[].rank_scaling.rang_1.dr_charges`, `uniques[].rank_scaling.rang_1.dr_shown`, `uniques[].rank_scaling.rang_1.first_skill_bonus`, `uniques[].rank_scaling.rang_1.frenzy_charges`, `uniques[].rank_scaling.rang_1.frenzy_shown`, `uniques[].rank_scaling.rang_1.fury_charges`, `uniques[].rank_scaling.rang_1.fury_shown`, `uniques[].rank_scaling.rang_1.heal_mag` … +6

### `config/monster_skills_scaling.json` (34)
`<id>.<id>.elite_to_boss`, `<id>.<id>.normal_to_elite`, `<id>.<id>.values.all_tiers`, `<id>.<id>.values.boss.aoe_range_bonus`, `<id>.<id>.values.boss.backline_damage_bonus`, `<id>.<id>.values.boss.def_increase`, `<id>.<id>.values.boss.duration_increase`, `<id>.<id>.values.elite.aoe_range_bonus`, `<id>.<id>.values.elite.atk_increase`, `<id>.<id>.values.elite.cooldown_reduction_on_cc`, `<id>.<id>.values.elite.def_increase`, `<id>.<id>.values.elite.duration_increase`, `<id>.<id>.values.elite.heal_percent`, `<id>.<id>.values.elite.mag_increase`, `<id>.<id>.values.normal.atk_increase`, `<id>.<id>.values.normal.def_increase`, `<id>.<id>.values.normal.duration_increase`, `<id>.<id>.values.normal.heal_percent`, `<id>.<id>.values.normal.mag_increase`, `<id>.artillery.alternative_row`, `<id>.artillery.never_position`, `<id>.assassin.alternative_row`, `<id>.assassin.never_position`, `<id>.berserker.alternative_row`, `<id>.berserker.never_position`, `<id>.boss.duration_mult`, `<id>.boss.effect_mult`, `<id>.brute.alternative_row`, `<id>.brute.never_position`, `<id>.controller.alternative_row` … +4

### `items/substat_crafting_system.json` (31)
`<id>.<id>.<id>.act_2`, `<id>.<id>.<id>.act_3`, `<id>.<id>.<id>.cost_estimate`, `<id>.<id>.<id>.rarity_increase`, `<id>.<id>.<id>[].drop_rate`, `<id>.<id>.<id>[].drop_source`, `<id>.<id>.rank_progression[].tier_required`, `<id>.<id>.replace_tokens.tiers[].craft_cost`, `<id>.<id>.replace_tokens[].act1_available`, `<id>.<id>.reroll_essences.tiers[].craft_cost`, `<id>.<id>.reroll_essences.tiers[].value_range`, `<id>.<id>.reroll_essences[].act1_available`, `<id>.<id>.select_crystals.tiers[].craft_cost`, `<id>.<id>.select_crystals[].act1_available`, `<id>.<id>.unlock_stones.tiers[].craft_cost`, `<id>.<id>.unlock_stones[].act1_available`, `<id>.<id>[].drop_rate`, `<id>.<id>[].drop_source`, `<id>.act_scope`, `<id>.selection_rules`, `<id>.tier_1.act1_available`, `<id>.tier_1.defensive[].value_range`, `<id>.tier_1.offensive[].value_range`, `<id>.tier_1.precision[].value_range`, `<id>.tier_1.resources[].value_range`, `<id>.tier_1.special[].value_range`, `<id>.tier_1.support[].value_range`, `<id>.tier_2.<id>[].value_range`, `<id>.tier_3.act1_available`, `<id>.tier_3.rare_defensive` … +1

### `systems/keystones.json` (29)
`common_keystones[].build_role`, `common_keystones[].variants[].runtime_scaling./triggers/0/cooldown`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/apply_shield_percent_max_hp`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/chance`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/drain_souffle_pct`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/duration`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/heal_percent_max_hp`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/restore_souffle_pct`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/revive_percent`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/revive_self_damage_percent`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/stacks_to_apply`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/0/value`, `common_keystones[].variants[].runtime_scaling./triggers/0/effects/1/heal_percent_max_hp`, `common_keystones[].variants[].runtime_scaling./triggers/0/skill_count`, `common_keystones[].variants[].runtime_scaling./triggers/0/threshold`, `common_keystones[].variants[].scaling.C.aggro_bonus`, `common_keystones[].variants[].scaling.C.combo_length`, `common_keystones[].variants[].scaling.C.every_n`, `common_keystones[].variants[].scaling.C.heal_on_expire`, `common_keystones[].variants[].scaling.C.souffle_gain`, `common_keystones[].variants[].scaling.C.souffle_regen_bonus`, `common_keystones[].variants[].scaling.SS.aggro_bonus`, `common_keystones[].variants[].scaling.SS.combo_length`, `common_keystones[].variants[].scaling.SS.every_n`, `common_keystones[].variants[].scaling.SS.heal_on_expire`, `common_keystones[].variants[].scaling.SS.souffle_gain`, `common_keystones[].variants[].scaling.SS.souffle_regen_bonus`, `rules.one_per_family`, `rules.rank_interpolation`

### `stats/status_effects.json` (26)
`<id>.enforcement.backend_load`, `<id>.exceptions_value_authorized`, `<id>.overflow_behavior`, `by_polarity`, `effects.control.slow.runtime.gcd_penalty_seconds_per_stack`, `effects.defensive.en_garde_stance.runtime.counter_attack_scaling`, `effects.defensive.riposte_active.runtime.consume_on_trigger`, `effects.defensive.riposte_active.runtime.on_hit_taken`, `effects.dot.curse_dot.duration_modifiable`, `effects.dot.curse_dot.runtime.damage_ignores_defense`, `effects.dot.curse_dot.runtime.scaling_behavior`, `effects.dot.holy_dot.duration_modifiable`, `effects.dot.holy_dot.runtime.damage_ignores_defense`, `effects.dot.holy_dot.runtime.ramp_per_tick`, `effects.dot.holy_dot.runtime.scaling_behavior`, `effects.dot.hp_dot.duration_modifiable`, `effects.dot.hp_dot.runtime.tick_percent`, `effects.dot.toxin.runtime.detonatable`, `effects.hot.heal_over_time.runtime.tick_percent`, `effects.hot.heal_over_time_mag.duration_modifiable`, `effects.hot.heal_over_time_max_hp.duration_modifiable`, `effects.immunity.cc_immune_zone.is_aura`, `effects.special.mana_drain.runtime.scaling_behavior`, `effects.special.mana_restore.runtime.scaling_modes`, `effects.special.mana_restore.runtime.value_per_level_supported`, `effects.stat_modifiers.crit_resistance_down.runtime.stat_mods.crit_resistance_percent`

### `items/panoplies.json` (22)
`min_level_by_size`, `piece_base_stats.<id>.magic_offensive`, `piece_base_stats.<id>.magic_support`, `piece_base_stats.<id>.melee_physical`, `piece_base_stats.<id>.melee_tank`, `set_signatures.adamah.effect.effects[].per_missing_pct`, `set_signatures.adamah.effect.effects[].value_per`, `set_signatures.orim.effect.triggers[].effects[].percent_of_heal`, `set_signatures.shomer.effect.triggers[].once_per_combat`, `sets.adamah.total_at_max`, `sets.adamah.weapon_template`, `sets.anan.total_at_max`, `sets.barzel.total_at_max`, `sets.barzel.weapon_template`, `sets.binah.total_at_max`, `sets.chayim.total_at_max`, `sets.davar.total_at_max`, `sets.eshal.total_at_max`, `sets.eshal.weapon_template`, `sets.even.total_at_max`, `sets.gevurah.total_at_max`, `sets.gevurah.weapon_template`

### `entities/monster_variants.json` (21)
`<id>.<id>.rarite_mult (normal/magic/rare/champion)`, `<id>.<id>.tier_mult (fodder..boss)`, `boss_variant.types.field_boss.respawn_time_minutes`, `boss_variant.types.field_boss.special_loot_table`, `boss_variant.types.special_loot_table`, `boss_variant.types.world_boss.contribution_loot`, `boss_variant.types.world_boss.respawn_time_minutes`, `elite_variant.guaranteed_rare_drop`, `elite_variant.special_abilities`, `prefix_variants.angry.loot_bonus`, `prefix_variants.armored.loot_bonus`, `prefix_variants.corrupted.loot_bonus`, `prefix_variants.giant.loot_bonus`, `prefix_variants.swift`, `rank_skills`, `spawn_rules.<id>.swift`, `species_families`, `stacking_rules`, `star_system.<id>.<id>.guaranteed_rarity`, `star_system.<id>.<id>.keystone_koro_boost`, `star_system.<id>.<id>.no_respawn`

### `systems/enhancement_system.json` (19)
`<id>.estimated_stones_for_max`, `<id>.level_requirements`, `<id>.on_failure`, `<id>.on_success`, `<id>.rank_1.craft_recipe`, `<id>.rank_1.drop_source_en`, `<id>.rank_1.drop_source_fr`, `<id>.rank_2.craft_recipe`, `<id>.rank_2.drop_source_en`, `<id>.rank_2.drop_source_fr`, `<id>.rank_3.craft_recipe`, `<id>.rank_3.drop_source_en`, `<id>.rank_3.drop_source_fr`, `<id>.rank_4.craft_recipe`, `<id>.rank_4.drop_source_en`, `<id>.rank_4.drop_source_fr`, `<id>.rank_5.craft_recipe`, `<id>.rank_5.drop_source_en`, `<id>.rank_5.drop_source_fr`

### `systems/tournament_role_kits.json` (19)
`subclasses.battle_cook`, `subclasses.bouncer`, `subclasses.choirmaster`, `subclasses.countermaster`, `subclasses.covenant`, `subclasses.deadeye`, `subclasses.dreadlord`, `subclasses.druidic_healer`, `subclasses.falcon_striker`, `subclasses.guitarist`, `subclasses.gunslasher`, `subclasses.hammer_lord`, `subclasses.nightstalker`, `subclasses.plague_brewer`, `subclasses.sanctifier`, `subclasses.sharpshooter`, `subclasses.skirmisher`, `subclasses.war_drummer`, `subclasses.wind_hunter`

### `entities/npcs.json` (17)
`class_master`, `class_masters[].dialogues.q_soren_voie_obj_1`, `service_npcs[].buy_config`, `service_npcs[].dialogues.farewell`, `service_npcs[].dialogues.q_colette_premier_compagnon_obj_0`, `service_npcs[].dialogues.q_havreden_arrivee_obj_0`, `service_npcs[].dialogues.q_havreden_tour_01_default`, `service_npcs[].dialogues.q_havreden_tour_01_obj_0`, `service_npcs[].dialogues.q_havreden_tour_02_obj_1`, `service_npcs[].dialogues.q_onb_forces_obj_2`, `service_npcs[].dialogues.q_tut_intro_01_default`, `service_npcs[].dialogues.q_tut_intro_08_obj_1`, `service_npcs[].shop_inventory.koro_basics`, `service_npcs[].shop_inventory.mercenary_potions`, `services_catalog`, `total_npcs`, `[].dialogues.farewell`

### `items/loot_tables.json` (17)
`anti_exploit`, `base_drops.enhancement_stones.drops_by_rank.rank_1.act_availability`, `base_drops.enhancement_stones.drops_by_rank.rank_2.act_availability`, `base_drops.enhancement_stones.drops_by_rank.rank_3.act_availability`, `base_drops.enhancement_stones.drops_by_rank.rank_3.act_multiplier`, `base_drops.enhancement_stones.drops_by_rank.rank_4.act_availability`, `base_drops.enhancement_stones.drops_by_rank.rank_4.act_multiplier`, `base_drops.enhancement_stones.drops_by_rank.rank_5.act_availability`, `base_drops.enhancement_stones.drops_by_rank.rank_5.act_multiplier`, `events.event_types.<id>.special_drops`, `final_calculation`, `multipliers.act_progression`, `multipliers.group_size.max_bonus_percent`, `multipliers.level_difference.min_drop_rate`, `rarity_system.tiers.<id>.base_weight`, `rarity_system.tiers.<id>.global_announce`, `rarity_system.tiers.<id>.special_sfx`

### `combat/targeting.json` (14)
`balance_guidelines`, `patterns.back_row.fixed_row`, `patterns.bounce_2.damage_reduction_per_bounce`, `patterns.bounce_2.initial_targets`, `patterns.bounce_2.max_bounces`, `patterns.bounce_all.damage_reduction_per_bounce`, `patterns.bounce_all.initial_targets`, `patterns.bounce_all.max_bounces`, `patterns.circle2`, `patterns.col_5`, `patterns.col_6`, `patterns.front_row.fixed_row`, `patterns.rect_3x2`, `patterns.x_diagonal`

### `config/game.json` (14)
`chat_channels`, `combat_grids.available.10x6`, `combat_grids.layout.board_cols`, `elite.elite_stat_mult`, `game_constants.max_raid_size`, `high_concept`, `implementation_status`, `minimap.hidden_during_combat`, `minimap.radius_pixels`, `minimap.update_rate_hz`, `party_behavior`, `slots_per_row`, `ui_sizes.bar_height_large`, `ui_sizes.font_size_normal`

### `config/monster_ai.json` (14)
`advanced_tactics`, `ai_roles.artillery.preferred_position`, `ai_roles.controller.priority_weights.debuff_enemy`, `ai_roles.healer.priority_weights.heal_critical_ally`, `ai_roles.support.heal_ally_threshold`, `ai_roles.support.priority_weights.debuff_enemy`, `ai_roles.tactician.analyzes_cooldowns`, `ai_roles.tactician.priority_weights.debuff_enemy`, `boss_phases.desperate.behavior_modifier`, `boss_phases.enraged.behavior_modifier`, `boss_phases.normal.behavior_modifier`, `intelligence_levels.<id>.has_phases`, `timing.reaction_randomness`, `timing.telegraph_duration`

### `entities/boss_mechanics.json` (14)
`<id>.<id>.add_mult`, `<id>.<id>.attack_speed_percent`, `<id>.<id>.dot_damage`, `<id>.<id>.ignore_block`, `<id>.ground_marker`, `<id>.screen_flash`, `<id>.target_marker`, `<id>[].base_monster`, `<id>[].mechanic.break_damage`, `<id>[].mechanic.spawn_rule`, `<id>[].phases[].hp_range`, `<id>[].phases[].mechanics[].break_condition`, `<id>[].phases[].mechanics[].spawn_rule`, `<id>[].respawn_minutes`

### `world/world_map.json` (14)
`<id>.campfire`, `<id>.gathering_node`, `<id>.max_monsters_per_area`, `<id>.rare_spawn`, `<id>.respawn_time_seconds`, `<id>.spawn_density`, `<id>.types[].rewards.elite_guaranteed`, `<id>.types[].rewards.equipment_on_completion`, `<id>.types[].rewards.guaranteed_equipment`, `<id>.types[].rewards.koro_chance`, `<id>.unlock_method`, `<id>[].post_boss_revelation`, `<id>[].rewards.equipment_level`, `<id>[].rewards.koro_pool`

### `classes/_classes_index.json` (13)
`classes[].passives_file`, `classes[].playstyle_tips`, `classes[].playstyle_tips_en`, `classes[].recommended_for`, `classes[].skills_file`, `classes[].subclasses[].fissure_relation`, `classes[].subclasses[].signature_skill`, `classes[].subclasses[].souffle_usage`, `classes[].subclasses[].tier3[].signature_fr`, `classes[].wiki_intro`, `classes[].wiki_intro_en`, `classes_by_role`, `subclasses_count`

### `systems/leaderboards.json` (13)
`config.entries_per_page`, `config.max_entries_displayed`, `config.refresh_interval_minutes`, `guild_leaderboards`, `leaderboards.achievements.seasonal`, `leaderboards.bosses_killed.seasonal`, `leaderboards.dungeons_cleared`, `leaderboards.level.seasonal`, `leaderboards.monsters_killed.seasonal`, `leaderboards.pvp_wins`, `seasons.duration_days`, `seasons.reset_seasonal_stats`, `seasons.rewards_top_100`

### `systems/encounter_stars.json` (12)
`<id>.already_dead_before_this_move`, `composition_rules.<id>.min_roles`, `encounter_templates`, `loot_integration`, `spawn_algorithm`, `star_tiers.<id>.boss_spawn_rules`, `star_tiers.<id>.boss_stats`, `star_tiers.<id>.elite_spawn_rules`, `star_tiers.<id>.elite_stats`, `star_tiers.<id>.loot_multiplier`, `star_tiers.<id>.max_diverse_types`, `star_tiers.<id>.unique_archetypes`

### `world/gather_nodes.json` (11)
`areas[].max_nodes`, `areas[].node_types`, `areas_schema`, `gather_duration`, `node_types`, `placement.areas_optional`, `placement.water_edges`, `profession_xp`, `rules.interact_range`, `rules.max_nodes_per_area_default`, `rules.rank_from_area`

### `systems/pvp.json` (10)
`arena.exhibition_only`, `arena.modes.arena_3v3.entity_count_includes_companions`, `arena.modes.arena_6v6.entity_count_includes_companions`, `arena.ranked_planned`, `arena.rewards_planned`, `duel.death_penalty`, `duel.hp_after_duel`, `duel.request_timeout_seconds`, `guild_wars`, `open_world_pvp`

### `systems/tower.json` (10)
`access.solo_allowed`, `difficulty.elites_from_floor_in_decade`, `difficulty.floor_pools`, `difficulty.guardian_extra_stars`, `difficulty.guardians_by_decade`, `difficulty.healer_from_floor_in_decade`, `difficulty.pools.abyss`, `difficulty.stars_by_decade`, `floor_overrides`, `keys.consumed_on_entry`

### `world/zones.json` (10)
`koro_pools`, `loot_tables[].equipment_chance`, `loot_tables[].koro_chance`, `loot_tables[].koro_pool`, `thematic_flow`, `zones[].allow_pvp`, `zones[].channel_capacity`, `zones[].is_expedition`, `zones[].is_safe_zone`, `zones[].loot_table`

### `config/skill_system.json` (9)
`duration_scaling.<id>.buff_debuff_stat`, `duration_scaling.<id>.hard_cc`, `duration_scaling.<id>.soft_cc_and_taunt`, `duration_scaling.hard_cc`, `duration_scaling.soft_cc`, `economy_analysis`, `points_per_skill_level`, `stat_scaling.available_stats`, `stat_scaling.default_by_damage_type`

### `items/profession_recipes.json` (9)
`<id>[].gather_level`, `<id>[].gathered_by`, `<id>[].input_qty`, `<id>[].input_rank`, `<id>[].node_type`, `<id>[].output_rank`, `<id>[].profession_level`, `<id>[].quality_cap`, `<id>[].world_buff`

### `classes/rogue/skills.json` (8)
`base_skills[].cooldown_per_level`, `subclass_skills.corsair.skills[].cooldown_per_level`, `subclass_skills.corsair.tier3.gunslasher`, `subclass_skills.duelist.skills[].cooldown_per_level`, `subclass_skills.duelist.tier3.countermaster`, `subclass_skills.shadowblade.skills[].cooldown_per_level`, `subclass_skills.shadowblade.tier3.nightstalker`, `subclass_skills.trickster.skills[].cooldown_per_level`

### `entities/monster_species.json` (8)
`stages.chief`, `stages.king`, `stages.larve`, `stages.lesser`, `stages.matron`, `stages.packleader`, `stages.queen`, `stages.warchief`

### `world/whispers.json` (8)
`display_system.pool_selection`, `display_system.triggers.<id>.cooldown_minutes`, `display_system.triggers.<id>.delay_seconds`, `display_system.triggers.<id>.frequency_minutes_max`, `display_system.triggers.<id>.frequency_minutes_min`, `sources.X.identifiable_par`, `sources.imitator`, `sources.self.identifiable_par`

### `classes/archer/skills.json` (7)
`<id>.counterplay`, `subclass_skills.ballmaster.tier3.bouncer`, `subclass_skills.falconer.tier3.falcon_striker`, `subclass_skills.falconer.tier3.wind_hunter`, `subclass_skills.gunslinger.tier3.deadeye`, `subclass_skills.ranger.tier3.sharpshooter`, `subclass_skills.ranger.tier3.skirmisher`

### `config/monster_scaling_model.json` (7)
`archetype_consolidation`, `archetypes_lv1_standard.range_max`, `archetypes_lv1_standard.range_min`, `level_curve.REQUIRES_BACK`, `level_curve.calibration.<id>.crit_pct`, `level_curve.calibration.<id>.dps_per_turn`, `per_mob_override`

### `systems/economy.json` (7)
`gold_sinks.teleportation.distance_multiplier`, `trade.restrictions.bound_items`, `trade.security.cooldown_after_modify_seconds`, `trade.security.double_confirmation`, `trade.security.modification_resets_confirm`, `vendor.buy_price_source`, `vendor.sell_price_ratio`

### `classes/healer/skills.json` (6)
`subclass_skills.cantor.tier3.choirmaster`, `subclass_skills.lifewarden.tier3.druidic_healer`, `subclass_skills.lifewarden.tier3.grove_warden.skills[].thorn_reflect_duration`, `subclass_skills.lightbringer.tier3.battle_healer.skills[].self_heal_percent`, `subclass_skills.lightbringer.tier3.sanctifier`, `subclass_skills.martyr.tier3.covenant`

### `entities/monster_archetype_assignments.json` (6)
`<id>.<id>.base_monster`, `<id>.<id>.custom_passives`, `<id>.<id>.custom_skills`, `<id>.<id>.signature_spell`, `<id>.archetype_distribution`, `<id>.total_monsters_assigned`

### `systems/guilds.json` (6)
`level_data.<id>.perk`, `level_data.<id>.xp_required`, `missions.monthly.duration_days`, `missions.player_xp_reward_percent`, `missions.weekly.duration_days`, `xp_rewards`

### `systems/professions.json` (6)
`achievements.sources_pending`, `achievements.xp_rule`, `professions`, `resource_rarity`, `rules.<id>.gold_costs`, `xp.gray_after_levels`

### `classes/artisan/skills.json` (5)
`subclass_skills.alchemist.tier3.plague_brewer`, `subclass_skills.blacksmith.tier3.breaker.skills[].boss_bonus_percent`, `subclass_skills.chef.tier3.battle_cook`, `subclass_skills.musician.tier3.guitarist`, `subclass_skills.musician.tier3.war_drummer`

### `config/rewards.json` (5)
`extension_procedure`, `inputs_declared_elsewhere`, `level_difference.min_drop_rate`, `migration_status`, `multiplier_families.act_progression`

### `world/quests.json` (5)
`reset_modes`, `templates.defeat_boss.recommended_count`, `templates.defeat_elite.recommended_count`, `templates.kill_mobs.counts_by_bracket`, `total_quests`

### `classes/mage/skills.json` (4)
`subclass_skills.elementalist.mechanics.burn.damage_per_stack`, `subclass_skills.occultist.mechanics.corruption.damage_per_stack`, `subclass_skills.spellblade.mechanics.arcane_momentum.damage_bonus_per_stack`, `subclass_skills.spellblade.mechanics.arcane_momentum.gain_from`

### `entities/x_companion.json` (3)
`<id>.core_rules`, `<id>.interaction_style`, `<id>.variations_by_zone`

### `classes/familiar/skills.json` (2)
`base_skills[].core_skill`, `base_skills[].filler_variant_group`

### `classes/rogue/passives.json` (2)
`innate_passive.conditions.count_trigger.armor_pen_per_stack`, `innate_passive.conditions.count_trigger.damage_per_stack`

### `classes/warrior/skills.json` (2)
`subclass_skills.warlord.tier3.dreadlord`, `subclass_skills.weaponmaster.tier3.hammer_lord`

### `config/familiar_balance.json` (2)
`capture_rate_by_rarity`, `role_profiles`

### `entities/familiars.json` (2)
`<id>.<id>.level_20`, `familiars[].visual_scale`

### `guild/missions.json` (2)
`member_reward.account_limit`, `missions_per_week`

### `items/affixes.json` (2)
`rules.max_same_stat_rolls`, `rules.no_duplicate_affix_id`

### `items/consumables.json` (2)
`star_modifiers[].drop_sources`, `star_modifiers[].effect.force_max`

### `items/equipment.json` (2)
`base_items.accessories.rings[].keystone_slot`, `loot_generation`

### `items/equipment_stats.json` (2)
`rarity_tiers`, `upgrade_system`

### `skills/monster_skills.json` (2)
`archetype_skills.boss_rongeur`, `archetype_skills.faune_identites`

### `systems/koro.json` (2)
`introduction.message_en`, `introduction.message_fr`

### `ui/emotes.json` (2)
`free_count`, `premium_price_diamonds`

### `classes/archer/passives.json` (1)
`innate_passive.conditions.count_trigger.damage_taken_increase_per_stack`

### `classes/artisan/passives.json` (1)
`innate_passive.conditions.count_trigger.heal_shield_power_per_stack`

### `classes/familiar/passives.json` (1)
`passives[].signature_species`

### `classes/mage/passives.json` (1)
`innate_passive.conditions.consume.consume_up_to`

### `entities/monsters.json` (1)
`<id>[].growth_tier`

### `entities/summons.json` (1)
`summons[].visual_kind`

### `guild/config.json` (1)
`<id>.zero_xp_from_level_delta`

### `items/currencies.json` (1)
`currencies[].is_soft_currency`

### `items/pet_books.json` (1)
`[].book_type`

### `items/recipes.json` (1)
`recipes[].level_band`

### `systems/encounter_formations.json` (1)
`band_definitions`

### `systems/equipment_upgrade.json` (1)
`cout_fixe`

### `systems/profession_xp.json` (1)
`<id>.scale_divisor`

### `systems/progression.json` (1)
`leveling.xp_source`

### `ui/cosmetics.json` (1)
`default_price_diamonds`

### `world/milestone_hints.json` (1)
`by_trigger`

### `world/tutorial_overlays.json` (1)
`indexed_by`

## Script (relancer depuis le dossier racine qui contient kanarion_back, kanarion_client, kanarion_database)

```python
import json, os, re, sys, collections
root = sys.argv[1]
db = os.path.join(root, 'kanarion_database')
src_text = []
for repo, exts in (('kanarion_back', ('.cpp','.hpp','.h','.cc')), ('kanarion_client', ('.gd',))):
    for d, dirs, files in os.walk(os.path.join(root, repo)):
        dirs[:] = [x for x in dirs if x not in ('build','.git','kanarion-meta','third_party','vendor','_deps','node_modules','.godot','addons')]
        for f in files:
            if f.endswith(exts):
                try: src_text.append(open(os.path.join(d,f),encoding='utf-8',errors='ignore').read())
                except: pass
blob = '\n'.join(src_text)
tokens = set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*', blob))
skip_dirs = ('_meta','scripts','out','.git','.github')
res = collections.defaultdict(list)
def walk(o, path, file):
    if isinstance(o, dict):
        missing=[k for k in o if k not in tokens]
        if len(o)>=4 and len(missing)>=0.5*len(o):
            for k,v in o.items(): walk(v, path+'.<id>', file)
            return
        for k, v in o.items():
            # skip id-like keys (dict keyed by ids) : contain digits or prefixes
            if re.match(r'^(mob_|skill_|item_|zone_|npc_|p_|wpn_|mat_|cons_|familiar_|quest_|ach_|dungeon_|merc_|pet_)', k) or k.startswith('_'):
                walk(v, path, file); continue
            if k not in tokens:
                res[file].append(path + '.' + k)
            walk(v, path + '.' + k, file)
    elif isinstance(o, list):
        for x in o[:50]: walk(x, path + '[]', file)
for d, dirs, files in os.walk(db):
    rel = os.path.relpath(d, db)
    if rel.split(os.sep)[0] in skip_dirs: dirs[:] = []; continue
    for f in files:
        if f.endswith('.json'):
            p = os.path.join(d, f)
            try: data = json.load(open(p, encoding='utf-8-sig'))
            except Exception as e: continue
            walk(data, '', os.path.relpath(p, db).replace(os.sep, '/'))
for f in sorted(res):
    uniq = sorted(set(res[f]))
    # collapse: keep only top-most dead paths
    top = [u for u in uniq if not any(u != o and u.startswith(o + '.') or u.startswith(o + '[]') and u != o for o in uniq)]
    print(f"## {f} ({len(top)})")
    for u in top[:40]: print('  ', u)
    if len(top) > 40: print('   ...', len(top)-40, 'more')
```
