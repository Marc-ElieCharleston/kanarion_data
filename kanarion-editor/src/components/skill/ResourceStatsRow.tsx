'use client';

import type { Skill, TierScaling } from '@/types/skill';

interface ResourceStatsRowProps {
  skill: Skill;
  skillLevel: number;
  manaAtLevel: number;
  tierScaling: TierScaling;
}

export default function ResourceStatsRow({
  skill,
  skillLevel,
  manaAtLevel,
  tierScaling,
}: ResourceStatsRowProps) {
  return (
    <div className="flex flex-wrap gap-3 mb-3 text-sm">
      <div className="flex items-center gap-1">
        <span className="text-sky-400">💧</span>
        <span className="text-zinc-400">Mana:</span>
        <span className="text-white">{skill.mana_cost}</span>
        {skillLevel > 1 && (
          <span className="text-amber-400 text-xs">→ {manaAtLevel}</span>
        )}
        <span className="text-zinc-500 text-xs">(+{tierScaling.mana_per_level}/lvl)</span>
      </div>
      <div className="flex items-center gap-1">
        <span className="text-violet-400">⏱️</span>
        <span className="text-zinc-400">CD:</span>
        <span className="text-white">{skill.cooldown}s</span>
      </div>
      {skill.cast_time && (
        <div className="flex items-center gap-1">
          <span className="text-amber-400">🔮</span>
          <span className="text-zinc-400">Cast:</span>
          <span className="text-amber-300">{skill.cast_time}s</span>
        </div>
      )}
      {skill.channel_time && (
        <div className="flex items-center gap-1">
          <span className="text-cyan-400">🔄</span>
          <span className="text-zinc-400">Channel:</span>
          <span className="text-cyan-300">{skill.channel_time}s</span>
        </div>
      )}
      {skill.hit_count && skill.hit_count > 1 && (
        <div className="flex items-center gap-1">
          <span className="text-zinc-400">Hits:</span>
          <span className="text-white">{skill.hit_count}x</span>
        </div>
      )}
    </div>
  );
}
