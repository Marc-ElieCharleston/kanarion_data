'use client';

import type { Skill, TierScaling } from '@/types/skill';

interface DamageStatsRowProps {
  skill: Skill;
  skillLevel: number;
  basePowerAtLevel: number;
  scalingPercentAtLevel: number;
  tierScaling: TierScaling;
  percentPerLevel: number;
}

export default function DamageStatsRow({
  skill,
  skillLevel,
  basePowerAtLevel,
  scalingPercentAtLevel,
  tierScaling,
  percentPerLevel,
}: DamageStatsRowProps) {
  const hasDamage = skill.base_power > 0 || skill.scaling_percent;
  
  if (!hasDamage) return null;

  return (
    <div className="flex flex-wrap gap-3 mb-2 text-sm">
      {skill.base_power > 0 && (
        <div className="flex items-center gap-1">
          <span className="text-orange-400">⚔️</span>
          <span className="text-zinc-400">Power:</span>
          <span className="text-white">{skill.base_power}</span>
          {skillLevel > 1 && (
            <span className="text-emerald-400 text-xs">→ {basePowerAtLevel}</span>
          )}
          <span className="text-zinc-500 text-xs">(+{tierScaling.power_per_level}/lvl)</span>
        </div>
      )}
      {skill.scaling_percent && skill.scaling_stat && (
        <div className="flex items-center gap-1">
          <span className="text-amber-400">📈</span>
          <span className="text-zinc-400">Scaling:</span>
          <span className={`text-white ${skill.scaling_stat === 'current_shield' ? 'text-sky-300' : ''}`}>
            {skill.scaling_percent}% {skill.scaling_stat === 'current_shield' ? 'Current Shield' : skill.scaling_stat.toUpperCase()}
          </span>
          {skillLevel > 1 && (
            <span className="text-emerald-400 text-xs">→ {scalingPercentAtLevel}%</span>
          )}
          <span className="text-zinc-500 text-xs">(+{percentPerLevel}%/lvl)</span>
        </div>
      )}
    </div>
  );
}
