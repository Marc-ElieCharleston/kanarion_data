'use client';

import type { Skill } from '@/types/skill';

interface RogueMechanicsProps {
  skill: Skill;
}

export default function RogueMechanics({ skill }: RogueMechanicsProps) {
  const hasRogueMechanics = skill.applies_bleed_stacks || skill.bonus_damage_per_debuff ||
    skill.mark_ignore_los || skill.stealth_bonus_damage || skill.execute_bonus_damage ||
    skill.armor_penetration || skill.disarm_blocks_auto || skill.disarm_blocks_spells ||
    skill.buff_steal_count || skill.stun_chance || skill.disarm_chance ||
    skill.steals_mana || skill.steals_all_buffs;

  if (!hasRogueMechanics) return null;

  return (
    <>
      {/* Rogue - Bleed stacks */}
      {skill.applies_bleed_stacks && (
        <div className="text-xs mb-1">
          <span className="text-red-400">🩸 Bleed:</span>{' '}
          <span className="text-zinc-300">{skill.applies_bleed_stacks} stack{skill.applies_bleed_stacks > 1 ? 's' : ''}</span>
        </div>
      )}

      {/* Rogue - Exploit Weakness */}
      {skill.bonus_damage_per_debuff && (
        <div className="text-xs mb-1 p-2 bg-purple-500/10 border border-purple-500/20 rounded">
          <span className="text-purple-400">🎯 Exploit Weakness:</span>{' '}
          <span className="text-zinc-300">
            +{skill.bonus_damage_per_debuff}% damage per debuff
            {skill.max_debuff_bonus && ` (max +${skill.max_debuff_bonus}%)`}
          </span>
        </div>
      )}

      {/* Rogue - Mark mechanics */}
      {skill.mark_ignore_los && (
        <div className="text-xs mb-1">
          <span className="text-amber-400">🎯 Mark:</span>{' '}
          <span className="text-zinc-300">Team ignores LoS</span>
          {skill.debuff_damage_taken && <span className="text-red-300"> • +{skill.debuff_damage_taken}% dmg taken</span>}
        </div>
      )}

      {/* Rogue - Stealth bonus */}
      {skill.stealth_bonus_damage && (
        <div className="text-xs mb-1 p-2 bg-zinc-700/50 border border-zinc-600/30 rounded">
          <span className="text-zinc-400">🌑 Stealth:</span>{' '}
          <span className="text-zinc-300">+{skill.stealth_bonus_damage}% from stealth</span>
        </div>
      )}

      {/* Rogue - Execute bonus */}
      {skill.execute_bonus_damage && skill.execute_threshold && (
        <div className="text-xs mb-1 p-2 bg-red-500/10 border border-red-500/20 rounded">
          <span className="text-red-400">💀 Execute:</span>{' '}
          <span className="text-zinc-300">+{skill.execute_bonus_damage}% if &lt;{skill.execute_threshold}% HP</span>
        </div>
      )}

      {/* Rogue - Armor penetration */}
      {skill.armor_penetration && (
        <div className="text-xs mb-1">
          <span className="text-orange-400">🗡️ Armor Pen:</span>{' '}
          <span className="text-zinc-300">Ignores {skill.armor_penetration}%</span>
        </div>
      )}

      {/* Trickster - Disarm blocks */}
      {(skill.disarm_blocks_auto || skill.disarm_blocks_spells) && (
        <div className="text-xs mb-1 p-2 bg-violet-500/10 border border-violet-500/20 rounded">
          <span className="text-violet-400">🚫 Disarm:</span>{' '}
          <span className="text-zinc-300">
            Blocks {skill.disarm_blocks_auto && 'autos'}{skill.disarm_blocks_auto && skill.disarm_blocks_spells && ' + '}{skill.disarm_blocks_spells && 'spells'}
          </span>
        </div>
      )}

      {/* Trickster - Buff steal */}
      {skill.buff_steal_count && (
        <div className="text-xs mb-1">
          <span className="text-teal-400">🎭 Steal:</span>{' '}
          <span className="text-zinc-300">{skill.buff_steal_count} buff{skill.buff_steal_count > 1 ? 's' : ''}</span>
        </div>
      )}

      {/* Corsair - Stun chance */}
      {skill.stun_chance && (
        <div className="text-xs mb-1">
          <span className="text-yellow-400">⚡ Stun:</span>{' '}
          <span className="text-zinc-300">{skill.stun_chance}% for {skill.stun_duration}s</span>
        </div>
      )}

      {/* Corsair - Disarm chance */}
      {skill.disarm_chance && (
        <div className="text-xs mb-1">
          <span className="text-violet-400">🚫 Disarm:</span>{' '}
          <span className="text-zinc-300">{skill.disarm_chance}% for {skill.disarm_duration}s</span>
        </div>
      )}

      {/* Corsair - Mana steal */}
      {skill.steals_mana && (
        <div className="text-xs mb-1">
          <span className="text-sky-400">💧 Mana Steal:</span>{' '}
          <span className="text-zinc-300">
            {skill.steals_mana} mana{skill.steals_buff_chance && ` • ${skill.steals_buff_chance}% steal buff`}
          </span>
        </div>
      )}

      {/* Corsair - Raid */}
      {skill.steals_all_buffs && (
        <div className="text-xs mb-1 p-2 bg-amber-500/10 border border-amber-500/20 rounded">
          <span className="text-amber-400">🏴‍☠️ Raid:</span>{' '}
          <span className="text-zinc-300">
            {skill.steals_mana_percent && `${skill.steals_mana_percent}% mana + `}ALL buffs
            {skill.applies_blind && ` + Blind ${skill.blind_duration}s`}
          </span>
        </div>
      )}
    </>
  );
}
