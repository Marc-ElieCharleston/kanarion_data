// Skill interfaces and types

export interface Skill {
  id: string;
  name: string;
  name_fr?: string;
  tier: string;
  target: string;
  pattern: string;
  damage_type: string;
  base_power: number;
  scaling_stat?: string;
  scaling_percent?: number;
  mana_cost: number;
  cooldown: number;
  vfx_type: string;
  description?: string;
  description_fr?: string;
  description_en?: string;
  tags: string[];
  is_signature?: boolean;
  ignore_los?: boolean;
  effect?: string;
  effect_duration?: number;
  buff?: string;
  buff_value?: number;
  buff_duration?: number;
  debuff?: string;
  debuff_value?: number;
  debuff_duration?: number;
  shield_value?: number;
  shield_duration?: number;
  // Shield scaling fields (MAG-based)
  shield_base?: number;
  shield_scaling_stat?: string;
  shield_scaling_percent?: number;
  self_shield_base?: number;
  self_shield_scaling_percent?: number;
  hit_count?: number;
  lifesteal_percent?: number;
  execute_threshold?: number;
  // Guardian-specific fields
  buff_scaling?: string;
  secondary_buff?: string;
  secondary_buff_value?: number;
  // Warlord-specific fields
  armor_pen?: number;
  shield_break?: number;
  // Weaponmaster-specific fields
  conditional?: {
    requires_buff?: string;
    bonus_hit_count?: number;
    bonus_double_hit_chance?: number;
  };
  // Healer-specific fields
  base_heal?: number;
  heal_scaling_stat?: string;
  heal_scaling_percent?: number;
  hot_percent?: number;
  hot_duration?: number;
  cleanse_count?: number;
  self_shield?: boolean;
  self_shield_value?: number;
  shield_scaling?: string;
  // Lifewarden/Soulreaper conditional bonus fields
  conditional_bonus?: {
    condition?: string;
    hp_threshold?: number;
    heal_bonus_percent?: number;
    lifesteal_bonus_percent?: number;
    shield_bonus_percent?: number;
  };
  thorn_reflect_percent?: number;
  hot_amplify_percent?: number;
  // Mage-specific fields
  cast_time?: number;
  channel_time?: number;
  generates_charges?: number;
  consumes_charges?: boolean;
  max_charges_consumed?: number;
  bonus_per_charge?: number;
  mana_regen_percent?: number;
  mana_regen_ticks?: number;
  // Cantor-specific fields
  mana_regen_duration?: number;
  resurrect?: boolean;
  resurrect_hp_percent?: number;
  cast_interruptible?: boolean;
  // Soulreaper-specific fields
  lifesteal_target?: string;
  sacrifice_hp_percent?: number;
  dot_type?: string;
  dot_percent?: number;
  dot_duration?: number;
  dot_heals_lowest_ally?: boolean;
  damage_per_missing_hp_percent?: number;
  max_missing_hp_bonus?: number;
  drain_to_all_allies?: boolean;
  drain_heal_percent?: number;
  // Archer-specific fields
  marked_bonus_percent?: number;
  applies_bleed?: boolean;
  bleed_stacks?: number;
  bleed_duration?: number;
  mark_refresh_on_hit?: boolean;
  mark_spread_on_kill?: boolean;
  // Ranger-specific fields
  crit_damage_bonus?: number;
  ignore_shields?: boolean;
  execute_bonus_percent?: number;
  guaranteed_crit?: boolean;
  cd_reset_on_kill?: boolean;
  // Falconer-specific fields
  damage_per_bleed_stack?: number;
  // Ballmaster-specific fields
  bounce_count?: number;
  can_bounce_same_target?: boolean;
  damage_per_bounce?: number;
  bounce_if_adjacent?: boolean;
  bounce_returns?: boolean;
  few_targets_bonus?: number;
  few_targets_threshold?: number;
  // Gunslinger-specific fields
  interrupts_cast?: boolean;
  each_hit_can_crit?: boolean;
  tertiary_buff?: string;
  tertiary_buff_value?: number;
  secondary_effect?: string;
  secondary_effect_duration?: number;
  // Artisan-specific fields
  damage_per_adjacent_ally?: number;
  max_adjacent_bonus?: number;
  shield_on_cross?: boolean;
  team_damage_amp?: number;
  mana_restore_base?: number;
  mana_restore_scaling_stat?: string;
  mana_restore_scaling_percent?: number;
  // Blacksmith-specific fields
  bonus_if_armor_broken?: number;
  debuff_stacks?: number;
  double_damage_if_armor_broken?: boolean;
  // Alchemist-specific fields
  applies_toxin?: boolean;
  toxin_stacks?: number;
  toxin_duration?: number;
  toxin_refresh?: boolean;
  detonates_toxin?: boolean;
  detonate_damage_base?: number;
  detonate_damage_per_stack?: number;
  detonate_consumes_stacks?: boolean;
  // Chef-specific fields
  applies_burn?: boolean;
  burn_stacks?: number;
  burn_duration?: number;
  hot_base?: number;
  hot_scaling_stat?: string;
  hot_scaling_percent?: number;
  allies_hot_base?: number;
  allies_hot_scaling_percent?: number;
  allies_hot_duration?: number;
  allies_buff?: string;
  allies_buff_value?: number;
  allies_buff_duration?: number;
  dual_effect?: boolean;
  // Musician-specific fields
  secondary_debuff?: string;
  secondary_debuff_value?: number;
  secondary_debuff_duration?: number;
  enemies_debuff?: string;
  enemies_debuff_value?: number;
  enemies_debuff_duration?: number;
  // Rogue-specific fields
  applies_bleed_stacks?: number;
  bonus_damage_per_debuff?: number;
  max_debuff_bonus?: number;
  debuff_damage_taken?: number;
  mark_ignore_los?: boolean;
  stealth_bonus_damage?: number;
  execute_bonus_damage?: number;
  armor_penetration?: number;
  disarm_blocks_auto?: boolean;
  disarm_blocks_spells?: boolean;
  buff_steal_count?: number;
  buff_steal_per_level?: number;
  stun_chance?: number;
  stun_chance_per_level?: number;
  stun_duration?: number;
  disarm_chance?: number;
  disarm_chance_per_level?: number;
  disarm_duration?: number;
  steals_mana?: number;
  steals_mana_per_level?: number;
  steals_buff_chance?: number;
  steals_mana_percent?: number;
  steals_all_buffs?: boolean;
  applies_blind?: boolean;
  blind_duration?: number;
  // Duelist-specific fields
  applies_debuff?: string;
  bonus_damage_vs_challenged?: number;
  counter_chance?: number;
  counter_chance_vs_challenged?: number;
  counter_type?: string;
  reflects_damage?: number;
  reflects_debuffs?: boolean;
  reflect_bonus_vs_challenged?: number;
  defense_reduction?: number;
  defense_reduction_per_level?: number;
  damage_mult_if_challenged?: number;
  damage_mult_if_challenged_and_exposed?: number;
  damage_ramp_per_hit?: number;
  [key: string]: unknown;
}

export interface TierScaling {
  power_per_level: number;
  percent_per_level?: number;
  mana_per_level: number;
  description?: string;
}

export interface DurationScaling {
  types: string[];
  duration_per_level: number;
  value_per_level?: number;
  description?: string;
}

export interface SkillCardProps {
  skill: Skill;
  skillLevel?: number;
  scalingByTier?: Record<string, TierScaling>;
  durationScaling?: Record<string, DurationScaling>;
  showGrids?: boolean;
  onEdit?: (skill: Skill) => void;
  onDelete?: (skillId: string) => void;
}
