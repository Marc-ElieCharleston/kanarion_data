'use client';

import AoeGrid from './AoeGrid';

export interface Skill {
  id: string;
  name: string;
  name_fr?: string;
  tier: string;
  target: string;
  pattern: string;
  damage_type: string;
  base_power: number;
  scaling_stat?: string;
  scaling_percent?: number;
  mana_cost: number;
  cooldown: number;
  vfx_type: string;
  description?: string;
  description_fr?: string;
  description_en?: string;
  tags: string[];
  is_signature?: boolean;
  ignore_los?: boolean;
  effect?: string;
  effect_duration?: number;
  buff?: string;
  buff_value?: number;
  buff_duration?: number;
  debuff?: string;
  debuff_value?: number;
  debuff_duration?: number;
  shield_value?: number;
  shield_duration?: number;
  hit_count?: number;
  lifesteal_percent?: number;
  execute_threshold?: number;
  [key: string]: unknown;
}

export interface TierScaling {
  power_per_level: number;
  percent_per_level?: number;
  mana_per_level: number;
  description?: string;
}

export interface DurationScaling {
  types: string[];
  duration_per_level: number;
  value_per_level?: number;
  description?: string;
}

interface SkillCardProps {
  skill: Skill;
  skillLevel?: number;
  scalingByTier?: Record<string, TierScaling>;
  durationScaling?: Record<string, DurationScaling>;
  showGrids?: boolean;
  onEdit?: (skill: Skill) => void;
  onDelete?: (skillId: string) => void;
}

const TIER_COLORS: Record<string, string> = {
  filler: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
  basic: 'bg-sky-500/20 text-sky-400 border-sky-500/30',
  standard: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  strong: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
  signature: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  ultimate: 'bg-red-500/20 text-red-400 border-red-500/30',
};

// Default scaling values
export const DEFAULT_TIER_SCALING: Record<string, TierScaling> = {
  filler: { power_per_level: 2, percent_per_level: 4, mana_per_level: 1 },
  basic: { power_per_level: 3, percent_per_level: 5, mana_per_level: 1 },
  standard: { power_per_level: 4, percent_per_level: 6, mana_per_level: 2 },
  strong: { power_per_level: 5, percent_per_level: 7, mana_per_level: 2 },
  signature: { power_per_level: 7, percent_per_level: 8, mana_per_level: 3 },
  ultimate: { power_per_level: 10, percent_per_level: 10, mana_per_level: 4 },
};

export const DEFAULT_DURATION_SCALING: Record<string, DurationScaling> = {
  hard_cc: { types: ['stun', 'freeze', 'petrify', 'sleep', 'knockdown'], duration_per_level: 0.1 },
  soft_cc: { types: ['slow', 'root', 'silence', 'blind', 'disarm'], duration_per_level: 0.15 },
  taunt: { types: ['taunt', 'fear', 'confusion'], duration_per_level: 0.2 },
  buff: { types: ['damage_reduction', 'atk_up', 'def_up', 'speed_up', 'frenzy'], duration_per_level: 0.3 },
  debuff: { types: ['armor_reduction', 'atk_down', 'def_down'], duration_per_level: 0.25 },
  shield: { types: ['shield'], duration_per_level: 0, value_per_level: 8 },
};

function getDurationScaling(effectType: string, durationScaling: Record<string, DurationScaling>): number {
  for (const [, config] of Object.entries(durationScaling)) {
    if (config.types && config.types.includes(effectType)) {
      return config.duration_per_level;
    }
  }
  return 0.1;
}

function getShieldScaling(durationScaling: Record<string, DurationScaling>): number {
  return durationScaling.shield?.value_per_level || 8;
}

export default function SkillCard({
  skill,
  skillLevel = 1,
  scalingByTier = DEFAULT_TIER_SCALING,
  durationScaling = DEFAULT_DURATION_SCALING,
  showGrids = true,
  onEdit,
  onDelete,
}: SkillCardProps) {
  const tierScaling = scalingByTier[skill.tier] || DEFAULT_TIER_SCALING[skill.tier] || { power_per_level: 2, percent_per_level: 4, mana_per_level: 1 };

  // Base power scaling (flat damage)
  const basePowerAtLevel = skill.base_power > 0
    ? skill.base_power + (skillLevel - 1) * tierScaling.power_per_level
    : 0;

  // Percent scaling (% of stat)
  const percentPerLevel = tierScaling.percent_per_level || 4;
  const scalingPercentAtLevel = skill.scaling_percent
    ? skill.scaling_percent + (skillLevel - 1) * percentPerLevel
    : 0;

  // Mana scaling
  const manaAtLevel = skill.mana_cost + (skillLevel - 1) * tierScaling.mana_per_level;

  // Duration scaling for effects
  const effectDurationScaling = skill.effect ? getDurationScaling(skill.effect, durationScaling) : 0;
  const effectDurationAtLevel = skill.effect_duration
    ? skill.effect_duration + (skillLevel - 1) * effectDurationScaling
    : 0;

  const buffDurationScaling = skill.buff ? getDurationScaling(skill.buff, durationScaling) : 0;
  const buffDurationAtLevel = skill.buff_duration
    ? skill.buff_duration + (skillLevel - 1) * buffDurationScaling
    : 0;

  const debuffDurationScaling = skill.debuff ? getDurationScaling(skill.debuff, durationScaling) : 0;
  const debuffDurationAtLevel = skill.debuff_duration
    ? skill.debuff_duration + (skillLevel - 1) * debuffDurationScaling
    : 0;

  // Shield value scaling
  const shieldScaling = getShieldScaling(durationScaling);
  const shieldValueAtLevel = skill.shield_value
    ? skill.shield_value + (skillLevel - 1) * shieldScaling
    : 0;

  const hasDamage = skill.base_power > 0 || skill.scaling_percent;

  return (
    <div className={`bg-zinc-900 rounded-lg border ${skill.is_signature ? 'border-amber-500/50' : 'border-zinc-800'} overflow-hidden`}>
      {/* Header */}
      <div className={`px-4 py-3 border-b ${skill.is_signature ? 'border-amber-500/30 bg-amber-500/5' : 'border-zinc-800'}`}>
        <div className="flex items-center justify-between">
          <div>
            <h4 className={`font-semibold ${skill.is_signature ? 'text-amber-400' : 'text-white'}`}>
              {skill.is_signature && '* '}{skill.name}
            </h4>
            {skill.name_fr && (
              <div className="text-xs text-zinc-500">{skill.name_fr}</div>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* LoS indicator */}
            {skill.ignore_los ? (
              <span className="text-[10px] px-1.5 py-0.5 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded">
                Ignore LoS
              </span>
            ) : skill.damage_type !== 'none' && (
              <span className="text-[10px] px-1.5 py-0.5 bg-zinc-700/50 text-zinc-500 border border-zinc-600/30 rounded">
                Req LoS
              </span>
            )}
            <span className={`text-xs px-2 py-1 rounded border ${TIER_COLORS[skill.tier]}`}>
              {skill.tier}
            </span>
            {/* Edit/Delete buttons */}
            {(onEdit || onDelete) && (
              <div className="flex gap-1 ml-2">
                {onEdit && (
                  <button
                    onClick={() => onEdit(skill)}
                    className="p-1 text-zinc-400 hover:text-white hover:bg-zinc-700 rounded"
                  >
                    E
                  </button>
                )}
                {onDelete && (
                  <button
                    onClick={() => onDelete(skill.id)}
                    className="p-1 text-zinc-400 hover:text-red-400 hover:bg-zinc-700 rounded"
                  >
                    X
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Damage stats row - NEW: base + % scaling */}
        {hasDamage && (
          <div className="flex flex-wrap gap-3 mb-2 text-sm">
            {skill.base_power > 0 && (
              <div className="flex items-center gap-1">
                <span className="text-orange-400">B:</span>
                <span className="text-white">{skill.base_power}</span>
                {skillLevel > 1 && (
                  <span className="text-emerald-400 text-xs">-&gt; {basePowerAtLevel}</span>
                )}
                <span className="text-zinc-500 text-xs">(+{tierScaling.power_per_level}/lvl)</span>
              </div>
            )}
            {skill.scaling_percent && skill.scaling_stat && (
              <div className="flex items-center gap-1">
                <span className="text-amber-400">%:</span>
                <span className="text-white">{skill.scaling_percent}% {skill.scaling_stat.toUpperCase()}</span>
                {skillLevel > 1 && (
                  <span className="text-emerald-400 text-xs">-&gt; {scalingPercentAtLevel}%</span>
                )}
                <span className="text-zinc-500 text-xs">(+{percentPerLevel}%/lvl)</span>
              </div>
            )}
          </div>
        )}

        {/* Mana/CD row */}
        <div className="flex flex-wrap gap-3 mb-3 text-sm">
          <div className="flex items-center gap-1">
            <span className="text-sky-400">MP:</span>
            <span className="text-white">{skill.mana_cost}</span>
            {skillLevel > 1 && (
              <span className="text-amber-400 text-xs">-&gt; {manaAtLevel}</span>
            )}
            <span className="text-zinc-500 text-xs">(+{tierScaling.mana_per_level}/lvl)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-violet-400">CD:</span>
            <span className="text-white">{skill.cooldown}s</span>
          </div>
          {skill.hit_count && skill.hit_count > 1 && (
            <div className="flex items-center gap-1">
              <span className="text-zinc-400">Hits:</span>
              <span className="text-white">{skill.hit_count}x</span>
            </div>
          )}
        </div>

        {/* Two grids: 4x4 and 5x3 */}
        {showGrids && (
          <div className="flex gap-4 mb-3">
            <AoeGrid
              pattern={skill.pattern}
              target={skill.target as 'enemy' | 'ally' | 'self' | 'allies' | 'enemies'}
              size="sm"
              gridFormat="4x4"
            />
            <AoeGrid
              pattern={skill.pattern}
              target={skill.target as 'enemy' | 'ally' | 'self' | 'allies' | 'enemies'}
              size="sm"
              gridFormat="5x3"
            />
          </div>
        )}

        {/* Description */}
        <p className="text-sm text-zinc-300 mb-2">
          {skill.description_fr || skill.description_en || skill.description || 'No description'}
        </p>

        {/* Effect details with duration scaling */}
        {skill.effect && (
          <div className="text-xs mb-1">
            <span className="text-violet-400">Effect:</span>{' '}
            <span className="text-zinc-300">{skill.effect}</span>
            {skill.effect_duration && (
              <>
                <span className="text-zinc-500"> {skill.effect_duration}s</span>
                {skillLevel > 1 && (
                  <span className="text-emerald-400"> -&gt; {effectDurationAtLevel.toFixed(1)}s</span>
                )}
              </>
            )}
          </div>
        )}

        {skill.buff && (
          <div className="text-xs mb-1">
            <span className="text-emerald-400">Buff:</span>{' '}
            <span className="text-zinc-300">{skill.buff}</span>
            {skill.buff_value && <span className="text-zinc-500"> ({skill.buff_value})</span>}
            {skill.buff_duration && (
              <>
                <span className="text-zinc-500"> {skill.buff_duration}s</span>
                {skillLevel > 1 && (
                  <span className="text-emerald-400"> -&gt; {buffDurationAtLevel.toFixed(1)}s</span>
                )}
              </>
            )}
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
                  <span className="text-emerald-400"> -&gt; {debuffDurationAtLevel.toFixed(1)}s</span>
                )}
              </>
            )}
          </div>
        )}

        {skill.shield_value && (
          <div className="text-xs mb-1">
            <span className="text-sky-400">Shield:</span>{' '}
            <span className="text-zinc-300">{skill.shield_value}</span>
            {skillLevel > 1 && (
              <span className="text-emerald-400"> -&gt; {shieldValueAtLevel}</span>
            )}
            {skill.shield_duration && <span className="text-zinc-500"> for {skill.shield_duration}s</span>}
          </div>
        )}

        {skill.lifesteal_percent && (
          <div className="text-xs mb-1">
            <span className="text-red-400">Lifesteal:</span>{' '}
            <span className="text-zinc-300">{skill.lifesteal_percent}%</span>
          </div>
        )}

        {skill.execute_threshold && (
          <div className="text-xs mb-1">
            <span className="text-red-400">Execute:</span>{' '}
            <span className="text-zinc-300">&lt;{skill.execute_threshold}% HP</span>
          </div>
        )}

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mt-2">
          {skill.tags.map((tag) => (
            <span key={tag} className="text-[10px] px-1.5 py-0.5 bg-zinc-800 text-zinc-500 rounded">
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
