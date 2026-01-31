'use client';

import type { Skill } from '@/types/skill';

interface DuelistMechanicsProps {
  skill: Skill;
}

export default function DuelistMechanics({ skill }: DuelistMechanicsProps) {
  const hasDuelistMechanics = skill.applies_debuff === 'challenged' ||
    skill.counter_chance || skill.reflects_damage ||
    (skill.defense_reduction && skill.applies_debuff === 'exposed') ||
    skill.damage_mult_if_challenged || skill.damage_ramp_per_hit;

  if (!hasDuelistMechanics) return null;

  return (
    <>
      {/* Duelist - Challenged */}
      {skill.applies_debuff === 'challenged' && (
        <div className="text-xs mb-1 p-2 bg-rose-500/10 border border-rose-500/20 rounded">
          <span className="text-rose-400">⚔️ Challenged:</span>{' '}
          <span className="text-zinc-300">
            Marks target{skill.bonus_damage_vs_challenged && ` • +${skill.bonus_damage_vs_challenged}% dmg`}
          </span>
        </div>
      )}

      {/* Duelist - Counter stance */}
      {skill.counter_chance && (
        <div className="text-xs mb-1 p-2 bg-zinc-700/50 border border-zinc-600/30 rounded">
          <span className="text-zinc-400">🛡️ Counter:</span>{' '}
          <span className="text-zinc-300">
            {skill.counter_chance}%{skill.counter_chance_vs_challenged && ` / ${skill.counter_chance_vs_challenged}% vs Challenged`}
          </span>
        </div>
      )}

      {/* Duelist - Reflect */}
      {skill.reflects_damage && (
        <div className="text-xs mb-1 p-2 bg-cyan-500/10 border border-cyan-500/20 rounded">
          <span className="text-cyan-400">↩️ Reflect:</span>{' '}
          <span className="text-zinc-300">
            {skill.reflects_damage}%{skill.reflects_debuffs && ' + debuffs'}
            {skill.reflect_bonus_vs_challenged && ` • +${skill.reflect_bonus_vs_challenged}% vs Challenged`}
          </span>
        </div>
      )}

      {/* Duelist - Exposed */}
      {skill.defense_reduction && skill.applies_debuff === 'exposed' && (
        <div className="text-xs mb-1">
          <span className="text-orange-400">📉 Exposed:</span>{' '}
          <span className="text-zinc-300">-{skill.defense_reduction}% DEF</span>
        </div>
      )}

      {/* Duelist - Finisher multipliers */}
      {skill.damage_mult_if_challenged && (
        <div className="text-xs mb-1 p-2 bg-rose-500/10 border border-rose-500/20 rounded">
          <span className="text-rose-400">💥 Finisher:</span>{' '}
          <span className="text-zinc-300">
            x{skill.damage_mult_if_challenged} Challenged
            {skill.damage_mult_if_challenged_and_exposed && ` • x${skill.damage_mult_if_challenged_and_exposed} Both`}
          </span>
        </div>
      )}

      {/* Multi-hit ramping */}
      {skill.damage_ramp_per_hit && skill.hit_count && (
        <div className="text-xs mb-1 p-2 bg-orange-500/10 border border-orange-500/20 rounded">
          <span className="text-orange-400">📈 Ramping:</span>{' '}
          <span className="text-zinc-300">+{skill.damage_ramp_per_hit}%/hit (hit {skill.hit_count}: +{(skill.hit_count - 1) * skill.damage_ramp_per_hit}%)</span>
        </div>
      )}
    </>
  );
}
