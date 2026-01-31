// Skill scaling utility functions

import type { Skill, TierScaling, DurationScaling } from '@/types/skill';
import { DEFAULT_TIER_SCALING, DEFAULT_DURATION_SCALING } from '@/constants/skill';

export function getDurationScaling(effectType: string, durationScaling: Record<string, DurationScaling>): number {
  for (const [, config] of Object.entries(durationScaling)) {
    if (config.types && config.types.includes(effectType)) {
      return config.duration_per_level;
    }
  }
  return 0.1;
}

export function getShieldScaling(durationScaling: Record<string, DurationScaling>): number {
  return durationScaling.shield?.value_per_level || 8;
}

export interface CalculatedSkillStats {
  basePowerAtLevel: number;
  scalingPercentAtLevel: number;
  manaAtLevel: number;
  effectDurationAtLevel: number;
  buffDurationAtLevel: number;
  debuffDurationAtLevel: number;
  shieldValueAtLevel: number;
  tierScaling: TierScaling;
  percentPerLevel: number;
  effectDurationScaling: number;
  buffDurationScaling: number;
  debuffDurationScaling: number;
  shieldScaling: number;
  hasDamage: boolean;
}

export function calculateSkillStats(
  skill: Skill,
  skillLevel: number,
  scalingByTier: Record<string, TierScaling> = DEFAULT_TIER_SCALING,
  durationScaling: Record<string, DurationScaling> = DEFAULT_DURATION_SCALING
): CalculatedSkillStats {
  const tierScaling = scalingByTier[skill.tier] || DEFAULT_TIER_SCALING[skill.tier] || { power_per_level: 2, percent_per_level: 4, mana_per_level: 1 };

  // Base power scaling (flat damage)
  const basePowerAtLevel = skill.base_power > 0
    ? skill.base_power + (skillLevel - 1) * tierScaling.power_per_level
    : 0;

  // Percent scaling (% of stat)
  const percentPerLevel = tierScaling.percent_per_level || 4;
  const scalingPercentAtLevel = skill.scaling_percent
    ? skill.scaling_percent + (skillLevel - 1) * percentPerLevel
    : 0;

  // Mana scaling
  const manaAtLevel = skill.mana_cost + (skillLevel - 1) * tierScaling.mana_per_level;

  // Duration scaling for effects
  const effectDurationScaling = skill.effect ? getDurationScaling(skill.effect, durationScaling) : 0;
  const effectDurationAtLevel = skill.effect_duration
    ? skill.effect_duration + (skillLevel - 1) * effectDurationScaling
    : 0;

  const buffDurationScaling = skill.buff ? getDurationScaling(skill.buff, durationScaling) : 0;
  const buffDurationAtLevel = skill.buff_duration
    ? skill.buff_duration + (skillLevel - 1) * buffDurationScaling
    : 0;

  const debuffDurationScaling = skill.debuff ? getDurationScaling(skill.debuff, durationScaling) : 0;
  const debuffDurationAtLevel = skill.debuff_duration
    ? skill.debuff_duration + (skillLevel - 1) * debuffDurationScaling
    : 0;

  // Shield value scaling
  const shieldScaling = getShieldScaling(durationScaling);
  const shieldValueAtLevel = skill.shield_value
    ? skill.shield_value + (skillLevel - 1) * shieldScaling
    : 0;

  const hasDamage = skill.base_power > 0 || !!skill.scaling_percent;

  return {
    basePowerAtLevel,
    scalingPercentAtLevel,
    manaAtLevel,
    effectDurationAtLevel,
    buffDurationAtLevel,
    debuffDurationAtLevel,
    shieldValueAtLevel,
    tierScaling,
    percentPerLevel,
    effectDurationScaling,
    buffDurationScaling,
    debuffDurationScaling,
    shieldScaling,
    hasDamage,
  };
}
