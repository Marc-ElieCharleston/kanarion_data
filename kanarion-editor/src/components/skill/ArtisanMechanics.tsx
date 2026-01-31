'use client';

import type { Skill } from '@/types/skill';

interface ArtisanMechanicsProps {
  skill: Skill;
}

export default function ArtisanMechanics({ skill }: ArtisanMechanicsProps) {
  const hasArtisanMechanics = skill.damage_per_adjacent_ally || skill.shield_on_cross ||
    skill.team_damage_amp || skill.mana_restore_base ||
    skill.bonus_if_armor_broken || skill.debuff_stacks || skill.double_damage_if_armor_broken ||
    skill.applies_toxin || skill.detonates_toxin ||
    skill.applies_burn || skill.hot_base ||
    (skill.dual_effect && (skill.allies_hot_base || skill.allies_buff || skill.enemies_debuff)) ||
    skill.secondary_debuff;

  if (!hasArtisanMechanics) return null;

  return (
    <>
      {/* Artisan - Adjacent ally bonus */}
      {skill.damage_per_adjacent_ally && (
        <div className="text-xs mb-1 p-2 bg-amber-500/10 border border-amber-500/20 rounded">
          <span className="text-amber-400">👥 Teamwork:</span>{' '}
          <span className="text-zinc-300">
            +{skill.damage_per_adjacent_ally}% damage per adjacent ally
            {skill.max_adjacent_bonus && ` (max +${skill.max_adjacent_bonus}%)`}
          </span>
        </div>
      )}

      {/* Artisan - Shield on cross */}
      {skill.shield_on_cross && (
        <div className="text-xs mb-1">
          <span className="text-sky-400">🛡️ Cross Shield:</span>{' '}
          <span className="text-zinc-300">Shields allies in cross pattern</span>
        </div>
      )}

      {/* Artisan - Team damage amp */}
      {skill.team_damage_amp && (
        <div className="text-xs mb-1">
          <span className="text-orange-400">⚔️ Team Amp:</span>{' '}
          <span className="text-zinc-300">Team deals +{skill.team_damage_amp}% damage to target</span>
        </div>
      )}

      {/* Artisan - Mana restore */}
      {skill.mana_restore_base && (
        <div className="text-xs mb-1">
          <span className="text-sky-400">💧 Mana Restore:</span>{' '}
          <span className="text-zinc-300">
            {skill.mana_restore_base} + {skill.mana_restore_scaling_percent}% {skill.mana_restore_scaling_stat?.toUpperCase()}
          </span>
        </div>
      )}

      {/* Blacksmith - Armor break synergy */}
      {skill.bonus_if_armor_broken && (
        <div className="text-xs mb-1 p-2 bg-orange-500/10 border border-orange-500/20 rounded">
          <span className="text-orange-400">🔨 Armor Synergy:</span>{' '}
          <span className="text-zinc-300">+{skill.bonus_if_armor_broken}% damage if target has -armor debuff</span>
        </div>
      )}

      {/* Blacksmith - Debuff stacks */}
      {skill.debuff_stacks && (
        <div className="text-xs mb-1">
          <span className="text-violet-400">📚 Stackable:</span>{' '}
          <span className="text-zinc-300">Can stack up to {skill.debuff_stacks}x</span>
        </div>
      )}

      {/* Blacksmith - Double damage if armor broken */}
      {skill.double_damage_if_armor_broken && (
        <div className="text-xs mb-1 p-2 bg-red-500/10 border border-red-500/20 rounded">
          <span className="text-red-400">💥 Shatter:</span>{' '}
          <span className="text-zinc-300">Double damage if targets have -armor debuff</span>
        </div>
      )}

      {/* Alchemist - Toxin application */}
      {skill.applies_toxin && (
        <div className="text-xs mb-1">
          <span className="text-lime-400">🧪 Toxin:</span>{' '}
          <span className="text-zinc-300">
            {skill.toxin_stacks} stack{(skill.toxin_stacks || 0) > 1 ? 's' : ''} ({skill.toxin_duration}s)
            {skill.toxin_refresh && <span className="text-lime-300"> • refreshes</span>}
          </span>
        </div>
      )}

      {/* Alchemist - Detonate toxin */}
      {skill.detonates_toxin && (
        <div className="text-xs mb-1 p-2 bg-lime-500/10 border border-lime-500/20 rounded">
          <span className="text-lime-400">💥 Detonate Toxin:</span>{' '}
          <span className="text-zinc-300">
            {skill.detonate_damage_base} + {skill.detonate_damage_per_stack}% MAG per stack
            {skill.detonate_consumes_stacks && <span className="text-amber-300"> • consumes stacks</span>}
          </span>
        </div>
      )}

      {/* Chef - Burn application */}
      {skill.applies_burn && (
        <div className="text-xs mb-1">
          <span className="text-orange-400">🔥 Burn:</span>{' '}
          <span className="text-zinc-300">
            {skill.burn_stacks} stack{(skill.burn_stacks || 0) > 1 ? 's' : ''} ({skill.burn_duration}s)
          </span>
        </div>
      )}

      {/* Chef - Flat HoT */}
      {skill.hot_base && (
        <div className="text-xs mb-1">
          <span className="text-green-400">💚 HoT:</span>{' '}
          <span className="text-zinc-300">
            {skill.hot_base} + {skill.hot_scaling_percent}% {skill.hot_scaling_stat?.toUpperCase()}/s ({skill.hot_duration}s)
          </span>
        </div>
      )}

      {/* Chef - Dual effect (enemies + allies) */}
      {skill.dual_effect && skill.allies_hot_base && (
        <div className="text-xs mb-1 p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
          <span className="text-emerald-400">👥 Allies:</span>{' '}
          <span className="text-zinc-300">
            HoT {skill.allies_hot_base} + {skill.allies_hot_scaling_percent}% MAG/s ({skill.allies_hot_duration}s)
            {skill.allies_buff && ` + ${skill.allies_buff_value}% ${skill.allies_buff.replace('_', ' ')} (${skill.allies_buff_duration}s)`}
          </span>
        </div>
      )}

      {/* Musician - Secondary debuff */}
      {skill.secondary_debuff && (
        <div className="text-xs mb-1">
          <span className="text-red-400">+ Debuff:</span>{' '}
          <span className="text-zinc-300">
            -{skill.secondary_debuff_value}% {skill.secondary_debuff.replace('_', ' ')} ({skill.secondary_debuff_duration}s)
          </span>
        </div>
      )}

      {/* Musician - Grand Performance dual effect */}
      {skill.dual_effect && skill.allies_buff && !skill.allies_hot_base && (
        <div className="text-xs mb-1 p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
          <span className="text-emerald-400">👥 Allies:</span>{' '}
          <span className="text-zinc-300">
            +{skill.allies_buff_value}% {skill.allies_buff.replace('_', ' ')} ({skill.allies_buff_duration}s)
          </span>
        </div>
      )}

      {skill.dual_effect && skill.enemies_debuff && (
        <div className="text-xs mb-1 p-2 bg-red-500/10 border border-red-500/20 rounded">
          <span className="text-red-400">👹 Enemies:</span>{' '}
          <span className="text-zinc-300">
            -{skill.enemies_debuff_value}% {skill.enemies_debuff.replace('_', ' ')} ({skill.enemies_debuff_duration}s)
          </span>
        </div>
      )}
    </>
  );
}
