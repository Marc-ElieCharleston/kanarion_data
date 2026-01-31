'use client';

import type { Skill } from '@/types/skill';

interface ClassMechanicsProps {
  skill: Skill;
}

export default function ClassMechanics({ skill }: ClassMechanicsProps) {
  return (
    <>
      {/* Thorn reflect */}
      {skill.thorn_reflect_percent && (
        <div className="text-xs mb-1">
          <span className="text-rose-400">Thorns:</span>{' '}
          <span className="text-zinc-300">Reflects {skill.thorn_reflect_percent}% melee damage</span>
        </div>
      )}

      {/* Conditional bonus */}
      {skill.conditional_bonus && (
        <div className="text-xs mb-1 p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
          <span className="text-emerald-400">Bonus:</span>{' '}
          <span className="text-zinc-300">
            {skill.conditional_bonus.condition === 'target_has_hot' && 'If target has HoT: '}
            {skill.conditional_bonus.condition === 'caster_below_hp' && `If caster <${skill.conditional_bonus.hp_threshold}% HP: `}
            {skill.conditional_bonus.condition === 'caster_below_hp_after' && `If caster <${skill.conditional_bonus.hp_threshold}% HP after: `}
            {skill.conditional_bonus.heal_bonus_percent && `+${skill.conditional_bonus.heal_bonus_percent}% heal`}
            {skill.conditional_bonus.lifesteal_bonus_percent && `+${skill.conditional_bonus.lifesteal_bonus_percent}% lifesteal`}
            {skill.conditional_bonus.shield_bonus_percent && `+${skill.conditional_bonus.shield_bonus_percent}% shield`}
          </span>
        </div>
      )}

      {skill.hot_amplify_percent && (
        <div className="text-xs mb-1">
          <span className="text-green-400">HoT Amplify:</span>{' '}
          <span className="text-zinc-300">+{skill.hot_amplify_percent}% to all active HoTs</span>
        </div>
      )}

      {skill.lifesteal_percent && (
        <div className="text-xs mb-1">
          <span className="text-red-400">Lifesteal:</span>{' '}
          <span className="text-zinc-300">
            {skill.lifesteal_percent}%{skill.lifesteal_target && ` → ${skill.lifesteal_target}`}
          </span>
        </div>
      )}

      {/* Sacrifice HP */}
      {skill.sacrifice_hp_percent && (
        <div className="text-xs mb-1">
          <span className="text-rose-500">💔 Sacrifice:</span>{' '}
          <span className="text-zinc-300">{skill.sacrifice_hp_percent}% of your HP</span>
        </div>
      )}

      {/* DoT that heals */}
      {skill.dot_percent && (
        <div className="text-xs mb-1">
          <span className="text-purple-400">DoT:</span>{' '}
          <span className="text-zinc-300">
            {skill.dot_percent}% HP/s for {skill.dot_duration}s
            {skill.dot_heals_lowest_ally && <span className="text-emerald-400"> → heals lowest ally</span>}
          </span>
        </div>
      )}

      {/* Damage scaling with missing HP */}
      {skill.damage_per_missing_hp_percent && (
        <div className="text-xs mb-1 p-2 bg-rose-500/10 border border-rose-500/20 rounded">
          <span className="text-rose-400">🩸 Missing HP Bonus:</span>{' '}
          <span className="text-zinc-300">
            +{skill.damage_per_missing_hp_percent}% damage per 1% missing HP
            {skill.max_missing_hp_bonus && ` (max +${skill.max_missing_hp_bonus}%)`}
          </span>
        </div>
      )}

      {/* Drain to all allies */}
      {skill.drain_to_all_allies && (
        <div className="text-xs mb-1">
          <span className="text-rose-400">🩸 Drain:</span>{' '}
          <span className="text-zinc-300">
            {skill.drain_heal_percent}% of damage heals all allies
          </span>
        </div>
      )}

      {/* Arcane Charges system */}
      {skill.generates_charges && (
        <div className="text-xs mb-1">
          <span className="text-indigo-400">⚡ Generates:</span>{' '}
          <span className="text-indigo-300">{skill.generates_charges} Arcane Charge{skill.generates_charges > 1 ? 's' : ''}</span>
        </div>
      )}

      {skill.consumes_charges && (
        <div className="text-xs mb-1 p-2 bg-indigo-500/10 border border-indigo-500/20 rounded">
          <span className="text-indigo-400">⚡ Consumes Charges:</span>{' '}
          <span className="text-zinc-300">
            Up to {skill.max_charges_consumed || '?'} charges
            {skill.bonus_per_charge && ` (+${skill.bonus_per_charge}% damage/charge)`}
          </span>
        </div>
      )}

      {/* Mana regen */}
      {skill.mana_regen_percent && (
        <div className="text-xs mb-1">
          <span className="text-sky-400">💧 Mana Regen:</span>{' '}
          <span className="text-sky-300">
            {skill.mana_regen_percent}% max MP/s
            {skill.mana_regen_ticks && ` (${skill.mana_regen_percent * skill.mana_regen_ticks}% total)`}
            {skill.mana_regen_duration && ` for ${skill.mana_regen_duration}s`}
          </span>
        </div>
      )}

      {/* Resurrect */}
      {skill.resurrect && (
        <div className="text-xs mb-1 p-2 bg-amber-500/10 border border-amber-500/20 rounded">
          <span className="text-amber-400">✝️ Resurrect:</span>{' '}
          <span className="text-zinc-300">
            Revives at {skill.resurrect_hp_percent || 50}% HP
            {skill.cast_interruptible && ' (interruptible)'}
          </span>
        </div>
      )}

      {skill.execute_threshold && !skill.execute_bonus_percent && !skill.execute_bonus_damage && (
        <div className="text-xs mb-1">
          <span className="text-red-400">Execute:</span>{' '}
          <span className="text-zinc-300">&lt;{skill.execute_threshold}% HP</span>
        </div>
      )}
    </>
  );
}
