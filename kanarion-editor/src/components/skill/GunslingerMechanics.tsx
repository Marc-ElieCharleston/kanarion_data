'use client';

import type { Skill } from '@/types/skill';

interface GunslingerMechanicsProps {
  skill: Skill;
}

export default function GunslingerMechanics({ skill }: GunslingerMechanicsProps) {
  const hasGunslingerMechanics = skill.interrupts_cast || 
    (skill.each_hit_can_crit && skill.hit_count && skill.hit_count > 1) ||
    skill.tertiary_buff || skill.secondary_effect;

  if (!hasGunslingerMechanics) return null;

  return (
    <>
      {/* Gunslinger - Interrupt */}
      {skill.interrupts_cast && (
        <div className="text-xs mb-1">
          <span className="text-rose-400">⚡ Interrupts enemy casts</span>
        </div>
      )}

      {/* Gunslinger - Each hit can crit */}
      {skill.each_hit_can_crit && skill.hit_count && skill.hit_count > 1 && (
        <div className="text-xs mb-1">
          <span className="text-orange-400">💥 Each hit can crit separately</span>
        </div>
      )}

      {/* Gunslinger - Tertiary buff */}
      {skill.tertiary_buff && (
        <div className="text-xs mb-1">
          <span className="text-teal-400">+ Buff:</span>{' '}
          <span className="text-zinc-300">{skill.tertiary_buff.replace('_', ' ')} +{skill.tertiary_buff_value}%</span>
        </div>
      )}

      {/* Gunslinger - Secondary effect (CC) */}
      {skill.secondary_effect && (
        <div className="text-xs mb-1">
          <span className="text-violet-400">+ Effect:</span>{' '}
          <span className="text-zinc-300">{skill.secondary_effect} ({skill.secondary_effect_duration}s)</span>
        </div>
      )}
    </>
  );
}
