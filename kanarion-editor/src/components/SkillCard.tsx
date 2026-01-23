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
  // Guardian-specific fields
  buff_scaling?: string;
  secondary_buff?: string;
  secondary_buff_value?: number;
  // Warlord-specific fields
  armor_pen?: number;
  shield_break?: number;
  // Weaponmaster-specific fields
  conditional?: {
    requires_buff?: string;
    bonus_hit_count?: number;
    bonus_double_hit_chance?: number;
  };
  // Healer-specific fields
  base_heal?: number;
  heal_scaling_stat?: string;
  heal_scaling_percent?: number;
  hot_percent?: number;
  hot_duration?: number;
  cleanse_count?: number;
  self_shield?: boolean;
  self_shield_value?: number;
  shield_scaling?: string;
  // Lifewarden-specific fields
  conditional_bonus?: {
    condition?: string;
    heal_bonus_percent?: number;
  };
  thorn_reflect_percent?: number;
  hot_amplify_percent?: number;
  // Mage-specific fields
  cast_time?: number;
  channel_time?: number;
  generates_charges?: number;
  consumes_charges?: boolean;
  max_charges_consumed?: number;
  bonus_per_charge?: number;
  mana_regen_percent?: number;
  mana_regen_ticks?: number;
  // Cantor-specific fields
  mana_regen_duration?: number;
  resurrect?: boolean;
  resurrect_hp_percent?: number;
  cast_interruptible?: boolean;
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
      <div className={`px-3 sm:px-4 py-2 sm:py-3 border-b ${skill.is_signature ? 'border-amber-500/30 bg-amber-500/5' : 'border-zinc-800'}`}>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div className="min-w-0">
            <h4 className={`font-semibold text-sm sm:text-base truncate ${skill.is_signature ? 'text-amber-400' : 'text-white'}`}>
              {skill.is_signature && '* '}{skill.name}
            </h4>
            {skill.name_fr && (
              <div className="text-xs text-zinc-500 truncate">{skill.name_fr}</div>
            )}
          </div>
          <div className="flex items-center gap-1 sm:gap-2 flex-wrap">
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
        {/* Damage stats row - base + % scaling */}
        {hasDamage && (
          <div className="flex flex-wrap gap-3 mb-2 text-sm">
            {skill.base_power > 0 && (
              <div className="flex items-center gap-1">
                <span className="text-orange-400">⚔️</span>
                <span className="text-zinc-400">Power:</span>
                <span className="text-white">{skill.base_power}</span>
                {skillLevel > 1 && (
                  <span className="text-emerald-400 text-xs">→ {basePowerAtLevel}</span>
                )}
                <span className="text-zinc-500 text-xs">(+{tierScaling.power_per_level}/lvl)</span>
              </div>
            )}
            {skill.scaling_percent && skill.scaling_stat && (
              <div className="flex items-center gap-1">
                <span className="text-amber-400">📈</span>
                <span className="text-zinc-400">Scaling:</span>
                <span className={`text-white ${skill.scaling_stat === 'current_shield' ? 'text-sky-300' : ''}`}>
                  {skill.scaling_percent}% {skill.scaling_stat === 'current_shield' ? 'Current Shield' : skill.scaling_stat.toUpperCase()}
                </span>
                {skillLevel > 1 && (
                  <span className="text-emerald-400 text-xs">→ {scalingPercentAtLevel}%</span>
                )}
                <span className="text-zinc-500 text-xs">(+{percentPerLevel}%/lvl)</span>
              </div>
            )}
          </div>
        )}

        {/* Heal stats row */}
        {skill.base_heal && (
          <div className="flex flex-wrap gap-3 mb-2 text-sm">
            <div className="flex items-center gap-1">
              <span className="text-emerald-400">💚</span>
              <span className="text-zinc-400">Heal:</span>
              <span className="text-white">{skill.base_heal}</span>
            </div>
            {skill.heal_scaling_percent && skill.heal_scaling_stat && (
              <div className="flex items-center gap-1">
                <span className="text-emerald-400">📈</span>
                <span className="text-zinc-400">Scaling:</span>
                <span className="text-white">{skill.heal_scaling_percent}% {skill.heal_scaling_stat.toUpperCase()}</span>
              </div>
            )}
            {skill.hot_percent && skill.hot_duration && (
              <div className="flex items-center gap-1">
                <span className="text-green-400">🔄</span>
                <span className="text-zinc-400">HoT:</span>
                <span className="text-white">{skill.hot_percent}% HP/s</span>
                <span className="text-zinc-500">({skill.hot_duration}s)</span>
              </div>
            )}
          </div>
        )}

        {/* Mana/CD row */}
        <div className="flex flex-wrap gap-3 mb-3 text-sm">
          <div className="flex items-center gap-1">
            <span className="text-sky-400">💧</span>
            <span className="text-zinc-400">Mana:</span>
            <span className="text-white">{skill.mana_cost}</span>
            {skillLevel > 1 && (
              <span className="text-amber-400 text-xs">→ {manaAtLevel}</span>
            )}
            <span className="text-zinc-500 text-xs">(+{tierScaling.mana_per_level}/lvl)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-violet-400">⏱️</span>
            <span className="text-zinc-400">CD:</span>
            <span className="text-white">{skill.cooldown}s</span>
          </div>
          {skill.cast_time && (
            <div className="flex items-center gap-1">
              <span className="text-amber-400">🔮</span>
              <span className="text-zinc-400">Cast:</span>
              <span className="text-amber-300">{skill.cast_time}s</span>
            </div>
          )}
          {skill.channel_time && (
            <div className="flex items-center gap-1">
              <span className="text-cyan-400">🔄</span>
              <span className="text-zinc-400">Channel:</span>
              <span className="text-cyan-300">{skill.channel_time}s</span>
            </div>
          )}
          {skill.hit_count && skill.hit_count > 1 && (
            <div className="flex items-center gap-1">
              <span className="text-zinc-400">Hits:</span>
              <span className="text-white">{skill.hit_count}x</span>
            </div>
          )}
        </div>

        {/* Two grids: 4x4 and 5x3 */}
        {showGrids && (
          <div className="flex justify-center space-x-8 mb-3 -mx-2">
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
            {skill.buff_value && (
              <span className="text-zinc-500">
                {' '}({skill.buff_value}{skill.buff_scaling ? `% ${skill.buff_scaling.replace('_', ' ')}` : ''})
              </span>
            )}
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
                  <span className="text-emerald-400"> -&gt; {debuffDurationAtLevel.toFixed(1)}s</span>
                )}
              </>
            )}
          </div>
        )}

        {skill.shield_value && (
          <div className="text-xs mb-1">
            <span className="text-sky-400">Shield:</span>{' '}
            <span className="text-zinc-300">
              {skill.shield_value}{skill.shield_scaling ? `% ${skill.shield_scaling.replace('_', ' ')}` : ''}
            </span>
            {!skill.shield_scaling && skillLevel > 1 && (
              <span className="text-emerald-400"> -&gt; {shieldValueAtLevel}</span>
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

        {skill.thorn_reflect_percent && (
          <div className="text-xs mb-1">
            <span className="text-rose-400">Thorns:</span>{' '}
            <span className="text-zinc-300">Reflects {skill.thorn_reflect_percent}% melee damage</span>
          </div>
        )}

        {skill.conditional_bonus && (
          <div className="text-xs mb-1 p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
            <span className="text-emerald-400">Bonus:</span>{' '}
            <span className="text-zinc-300">
              {skill.conditional_bonus.condition === 'target_has_hot' && 'If target has HoT: '}
              {skill.conditional_bonus.heal_bonus_percent && `+${skill.conditional_bonus.heal_bonus_percent}% heal`}
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
            <span className="text-zinc-300">{skill.lifesteal_percent}%</span>
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

        {skill.execute_threshold && (
          <div className="text-xs mb-1">
            <span className="text-red-400">Execute:</span>{' '}
            <span className="text-zinc-300">&lt;{skill.execute_threshold}% HP</span>
          </div>
        )}

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
