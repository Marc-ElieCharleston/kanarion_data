// Skill constants and defaults

import type { TierScaling, DurationScaling } from '@/types/skill';

export const TIER_COLORS: Record<string, string> = {
  filler: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
  basic: 'bg-sky-500/20 text-sky-400 border-sky-500/30',
  standard: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  strong: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
  signature: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  ultimate: 'bg-red-500/20 text-red-400 border-red-500/30',
};

export const DEFAULT_TIER_SCALING: Record<string, TierScaling> = {
  filler: { power_per_level: 2, percent_per_level: 4, mana_per_level: 1 },
  basic: { power_per_level: 3, percent_per_level: 5, mana_per_level: 1 },
  standard: { power_per_level: 4, percent_per_level: 6, mana_per_level: 2 },
  strong: { power_per_level: 5, percent_per_level: 7, mana_per_level: 2 },
  signature: { power_per_level: 7, percent_per_level: 8, mana_per_level: 3 },
  ultimate: { power_per_level: 10, percent_per_level: 10, mana_per_level: 4 },
};

export const DEFAULT_DURATION_SCALING: Record<string, DurationScaling> = {
  hard_cc: { types: ['stun', 'freeze', 'petrify', 'sleep', 'knockdown'], duration_per_level: 0.1 },
  soft_cc: { types: ['slow', 'root', 'silence', 'blind', 'disarm'], duration_per_level: 0.15 },
  taunt: { types: ['taunt', 'fear', 'confusion'], duration_per_level: 0.2 },
  buff: { types: ['damage_reduction', 'atk_up', 'def_up', 'speed_up', 'frenzy'], duration_per_level: 0.3 },
  debuff: { types: ['armor_reduction', 'atk_down', 'def_down'], duration_per_level: 0.25 },
  shield: { types: ['shield'], duration_per_level: 0, value_per_level: 8 },
};
