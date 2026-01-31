'use client';

import type { Skill } from '@/types/skill';

interface WarlordMechanicsProps {
  skill: Skill;
}

export default function WarlordMechanics({ skill }: WarlordMechanicsProps) {
  const hasWarlordMechanics = skill.armor_pen || skill.shield_break || skill.conditional;

  if (!hasWarlordMechanics) return null;

  return (
    <>
      {(skill.armor_pen || skill.shield_break) && (
        <div className="text-xs mb-1 flex flex-wrap gap-2">
          {skill.armor_pen && (
            <span>
              <span className="text-orange-400">Armor Pen:</span>{' '}
              <span className="text-zinc-300">{skill.armor_pen}%</span>
            </span>
          )}
          {skill.shield_break && (
            <span>
              <span className="text-sky-400">Shield Break:</span>{' '}
              <span className="text-zinc-300">{skill.shield_break}%</span>
            </span>
          )}
        </div>
      )}

      {skill.conditional && (
        <div className="text-xs mb-1 p-2 bg-violet-500/10 border border-violet-500/20 rounded">
          <span className="text-violet-400">Conditional:</span>{' '}
          {skill.conditional.requires_buff && (
            <span className="text-zinc-300">
              Under <span className="text-violet-300">{skill.conditional.requires_buff.replace('_', ' ')}</span>:
            </span>
          )}
          <span className="text-zinc-300">
            {skill.conditional.bonus_hit_count && ` +${skill.conditional.bonus_hit_count} hit`}
            {skill.conditional.bonus_double_hit_chance && `, +${skill.conditional.bonus_double_hit_chance}% double hit`}
          </span>
        </div>
      )}
    </>
  );
}
