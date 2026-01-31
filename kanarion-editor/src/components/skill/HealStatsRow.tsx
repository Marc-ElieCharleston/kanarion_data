'use client';

import type { Skill } from '@/types/skill';

interface HealStatsRowProps {
  skill: Skill;
}

export default function HealStatsRow({ skill }: HealStatsRowProps) {
  if (!skill.base_heal) return null;

  return (
    <div className="flex flex-wrap gap-3 mb-2 text-sm">
      <div className="flex items-center gap-1">
        <span className="text-emerald-400">💚</span>
        <span className="text-zinc-400">Heal:</span>
        <span className="text-white">{skill.base_heal}</span>
      </div>
      {skill.heal_scaling_percent && skill.heal_scaling_stat && (
        <div className="flex items-center gap-1">
          <span className="text-emerald-400">📈</span>
          <span className="text-zinc-400">Scaling:</span>
          <span className="text-white">{skill.heal_scaling_percent}% {skill.heal_scaling_stat.toUpperCase()}</span>
        </div>
      )}
      {skill.hot_percent && skill.hot_duration && (
        <div className="flex items-center gap-1">
          <span className="text-green-400">🔄</span>
          <span className="text-zinc-400">HoT:</span>
          <span className="text-white">{skill.hot_percent}% HP/s</span>
          <span className="text-zinc-500">({skill.hot_duration}s)</span>
        </div>
      )}
    </div>
  );
}
