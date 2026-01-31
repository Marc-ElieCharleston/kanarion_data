'use client';

import type { Skill } from '@/types/skill';

interface ArcherMechanicsProps {
  skill: Skill;
}

export default function ArcherMechanics({ skill }: ArcherMechanicsProps) {
  const hasArcherMechanics = skill.marked_bonus_percent || skill.applies_bleed || 
    skill.mark_refresh_on_hit || skill.mark_spread_on_kill ||
    skill.crit_damage_bonus || skill.guaranteed_crit || skill.ignore_shields ||
    (skill.execute_bonus_percent && skill.execute_threshold) || skill.cd_reset_on_kill ||
    skill.damage_per_bleed_stack;

  if (!hasArcherMechanics) return null;

  return (
    <>
      {/* Archer - Mark bonus */}
      {skill.marked_bonus_percent && (
        <div className="text-xs mb-1 p-2 bg-amber-500/10 border border-amber-500/20 rounded">
          <span className="text-amber-400">🎯 Mark Synergy:</span>{' '}
          <span className="text-zinc-300">+{skill.marked_bonus_percent}% damage if target is Marked</span>
        </div>
      )}

      {/* Archer - Bleed application */}
      {skill.applies_bleed && (
        <div className="text-xs mb-1">
          <span className="text-red-400">🩸 Bleed:</span>{' '}
          <span className="text-zinc-300">
            Applies {skill.bleed_stacks || 1} stack{(skill.bleed_stacks || 1) > 1 ? 's' : ''} ({skill.bleed_duration}s)
          </span>
        </div>
      )}

      {/* Falconer - Damage per bleed stack */}
      {skill.damage_per_bleed_stack && (
        <div className="text-xs mb-1 p-2 bg-red-500/10 border border-red-500/20 rounded">
          <span className="text-red-400">🩸 Bleed Synergy:</span>{' '}
          <span className="text-zinc-300">+{skill.damage_per_bleed_stack}% damage per bleed stack on target</span>
        </div>
      )}

      {/* Archer - Mark mechanics */}
      {(skill.mark_refresh_on_hit || skill.mark_spread_on_kill) && (
        <div className="text-xs mb-1">
          <span className="text-amber-400">🎯 Mark:</span>{' '}
          <span className="text-zinc-300">
            {skill.mark_refresh_on_hit && 'Refreshes on hit'}
            {skill.mark_refresh_on_hit && skill.mark_spread_on_kill && ' • '}
            {skill.mark_spread_on_kill && 'Spreads on kill'}
          </span>
        </div>
      )}

      {/* Ranger - Crit damage bonus */}
      {skill.crit_damage_bonus && (
        <div className="text-xs mb-1">
          <span className="text-orange-400">💥 Crit Bonus:</span>{' '}
          <span className="text-zinc-300">+{skill.crit_damage_bonus}% crit damage</span>
        </div>
      )}

      {/* Ranger - Guaranteed crit */}
      {skill.guaranteed_crit && (
        <div className="text-xs mb-1">
          <span className="text-yellow-400">⚡ Guaranteed Crit</span>
        </div>
      )}

      {/* Ranger - Ignore shields */}
      {skill.ignore_shields && (
        <div className="text-xs mb-1">
          <span className="text-sky-400">🛡️ Ignores Shields</span>
        </div>
      )}

      {/* Ranger - Execute bonus */}
      {skill.execute_bonus_percent && skill.execute_threshold && (
        <div className="text-xs mb-1 p-2 bg-red-500/10 border border-red-500/20 rounded">
          <span className="text-red-400">💀 Execute:</span>{' '}
          <span className="text-zinc-300">+{skill.execute_bonus_percent}% damage if target &lt;{skill.execute_threshold}% HP</span>
        </div>
      )}

      {/* Ranger - CD reset on kill */}
      {skill.cd_reset_on_kill && (
        <div className="text-xs mb-1">
          <span className="text-emerald-400">🔄 CD resets on kill</span>
        </div>
      )}
    </>
  );
}
