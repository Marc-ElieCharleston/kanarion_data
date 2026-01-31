'use client';

import type { Skill } from '@/types/skill';

interface BallmasterMechanicsProps {
  skill: Skill;
}

export default function BallmasterMechanics({ skill }: BallmasterMechanicsProps) {
  const hasBallmasterMechanics = skill.bounce_count || skill.bounce_if_adjacent || skill.few_targets_bonus;

  if (!hasBallmasterMechanics) return null;

  return (
    <>
      {/* Ballmaster - Bounce mechanics */}
      {skill.bounce_count && (
        <div className="text-xs mb-1 p-2 bg-cyan-500/10 border border-cyan-500/20 rounded">
          <span className="text-cyan-400">🔄 Bounce:</span>{' '}
          <span className="text-zinc-300">
            {skill.bounce_count} bounces
            {skill.can_bounce_same_target && ' (can rehit)'}
            {skill.damage_per_bounce && ` • +${skill.damage_per_bounce}% dmg/bounce`}
          </span>
        </div>
      )}

      {/* Ballmaster - Conditional bounce */}
      {skill.bounce_if_adjacent && (
        <div className="text-xs mb-1">
          <span className="text-cyan-400">↩️ Ricochet:</span>{' '}
          <span className="text-zinc-300">
            Bounces if adjacent enemy{skill.bounce_returns && ' (returns = 2 hits)'}
          </span>
        </div>
      )}

      {/* Ballmaster - Few targets bonus */}
      {skill.few_targets_bonus && (
        <div className="text-xs mb-1">
          <span className="text-amber-400">🎯 Concentrated:</span>{' '}
          <span className="text-zinc-300">+{skill.few_targets_bonus}% damage if ≤{skill.few_targets_threshold} targets</span>
        </div>
      )}
    </>
  );
}
