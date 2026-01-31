'use client';

import type { Skill } from '@/types/skill';

interface EffectsDisplayProps {
  skill: Skill;
  skillLevel: number;
  effectDurationAtLevel: number;
  buffDurationAtLevel: number;
  debuffDurationAtLevel: number;
  shieldValueAtLevel: number;
}

export default function EffectsDisplay({
  skill,
  skillLevel,
  effectDurationAtLevel,
  buffDurationAtLevel,
  debuffDurationAtLevel,
  shieldValueAtLevel,
}: EffectsDisplayProps) {
  return (
    <>
      {/* Effect details with duration scaling */}
      {skill.effect && (
        <div className="text-xs mb-1">
          <span className="text-violet-400">Effect:</span>{' '}
          <span className="text-zinc-300">{skill.effect}</span>
          {skill.effect_duration && (
            <>
              <span className="text-zinc-500"> {skill.effect_duration}s</span>
              {skillLevel > 1 && (
                <span className="text-emerald-400"> → {effectDurationAtLevel.toFixed(1)}s</span>
              )}
            </>
          )}
        </div>
      )}

      {skill.buff && (
        <div className="text-xs mb-1">
          <span className="text-emerald-400">Buff:</span>{' '}
          <span className="text-zinc-300">{skill.buff}</span>
          {skill.buff_value && (
            <span className="text-zinc-500">
              {' '}({skill.buff_value}{skill.buff_scaling ? `% ${skill.buff_scaling.replace('_', ' ')}` : ''})
            </span>
          )}
          {skill.buff_duration && (
            <>
              <span className="text-zinc-500"> {skill.buff_duration}s</span>
              {skillLevel > 1 && (
                <span className="text-emerald-400"> → {buffDurationAtLevel.toFixed(1)}s</span>
              )}
            </>
          )}
        </div>
      )}

      {skill.secondary_buff && (
        <div className="text-xs mb-1">
          <span className="text-teal-400">+ Buff:</span>{' '}
          <span className="text-zinc-300">{skill.secondary_buff.replace('_', ' ')}</span>
          {skill.secondary_buff_value && <span className="text-zinc-500"> ({skill.secondary_buff_value}%)</span>}
        </div>
      )}

      {skill.debuff && (
        <div className="text-xs mb-1">
          <span className="text-red-400">Debuff:</span>{' '}
          <span className="text-zinc-300">{skill.debuff}</span>
          {skill.debuff_value && <span className="text-zinc-500"> ({skill.debuff_value})</span>}
          {skill.debuff_duration && (
            <>
              <span className="text-zinc-500"> {skill.debuff_duration}s</span>
              {skillLevel > 1 && (
                <span className="text-emerald-400"> → {debuffDurationAtLevel.toFixed(1)}s</span>
              )}
            </>
          )}
        </div>
      )}

      {/* Shield - MAG scaling format */}
      {skill.shield_base && (
        <div className="text-xs mb-1">
          <span className="text-sky-400">🛡️ Shield:</span>{' '}
          <span className="text-zinc-300">
            {skill.shield_base} + {skill.shield_scaling_percent}% {skill.shield_scaling_stat?.toUpperCase()}
          </span>
          {skill.shield_duration && <span className="text-zinc-500"> for {skill.shield_duration}s</span>}
          {skill.self_shield && skill.self_shield_base && (
            <span className="text-teal-400"> + ({skill.self_shield_base} + {skill.self_shield_scaling_percent}% {skill.shield_scaling_stat?.toUpperCase()}) on self</span>
          )}
        </div>
      )}

      {/* Shield - HP% format (legacy/Blood Pact) */}
      {skill.shield_value && !skill.shield_base && (
        <div className="text-xs mb-1">
          <span className="text-sky-400">🛡️ Shield:</span>{' '}
          <span className="text-zinc-300">
            {skill.shield_value}{skill.shield_scaling ? `% ${skill.shield_scaling.replace('_', ' ')}` : ''}
          </span>
          {!skill.shield_scaling && skillLevel > 1 && (
            <span className="text-emerald-400"> → {shieldValueAtLevel}</span>
          )}
          {skill.shield_duration && <span className="text-zinc-500"> for {skill.shield_duration}s</span>}
          {skill.self_shield && skill.self_shield_value && (
            <span className="text-teal-400"> + {skill.self_shield_value}% on self</span>
          )}
        </div>
      )}

      {skill.cleanse_count && (
        <div className="text-xs mb-1">
          <span className="text-purple-400">Cleanse:</span>{' '}
          <span className="text-zinc-300">{skill.cleanse_count} debuff{skill.cleanse_count > 1 ? 's' : ''}</span>
        </div>
      )}
    </>
  );
}
