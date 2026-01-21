'use client';

import { useEffect, useState } from 'react';
import AoeGrid from '@/components/AoeGrid';

interface Skill {
  id: string;
  name: string;
  name_fr?: string;
  tier: string;
  target: string;
  pattern: string;
  damage_type: string;
  base_power: number;
  mana_cost: number;
  cooldown: number;
  vfx_type: string;
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

interface SkillsFile {
  _meta: {
    version: string;
    last_updated: string;
    class: string;
    description: string;
    pattern_presets: Record<string, string>;
    vfx_available: string[];
  };
  base_skills: Skill[];
  subclass_skills: Record<string, {
    identity: string;
    signature: string;
    skills: Skill[];
  }>;
}

interface TierScaling {
  power_per_level: number;
  mana_per_level: number;
  description: string;
}

interface DurationScaling {
  types: string[];
  duration_per_level: number;
  value_per_level?: number;
  description: string;
}

interface SkillSystemConfig {
  _meta: { version: string; last_updated: string };
  skill_points: {
    points_per_level: number;
    max_player_level: number;
    total_points_available: number;
  };
  skill_levels: {
    min_level: number;
    max_level: number;
  };
  skill_categories: Record<string, {
    count: number;
    unlock_at_player_level: number;
    description: string;
  }>;
  scaling: {
    type: string;
    [key: string]: unknown;
  };
  scaling_by_tier: Record<string, TierScaling>;
  duration_scaling: Record<string, DurationScaling>;
  skill_tiers: Record<string, {
    power_range: [number, number];
    cooldown_range: [number, number];
    mana_range: [number, number];
    description: string;
  }>;
}

interface SkillsData {
  system: SkillSystemConfig;
  classes: Record<string, SkillsFile>;
}

const TIER_COLORS: Record<string, string> = {
  filler: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
  basic: 'bg-sky-500/20 text-sky-400 border-sky-500/30',
  standard: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  strong: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
  signature: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  ultimate: 'bg-red-500/20 text-red-400 border-red-500/30',
};

const CLASS_COLORS: Record<string, string> = {
  warrior: 'text-red-400 border-red-500/30',
  mage: 'text-violet-400 border-violet-500/30',
  healer: 'text-emerald-400 border-emerald-500/30',
  archer: 'text-amber-400 border-amber-500/30',
  rogue: 'text-zinc-300 border-zinc-500/30',
  artisan: 'text-orange-400 border-orange-500/30',
};

const CLASS_ICONS: Record<string, string> = {
  warrior: '⚔️',
  mage: '🔮',
  healer: '💚',
  archer: '🏹',
  rogue: '🗡️',
  artisan: '🔧',
};

// Default scaling values
const DEFAULT_TIER_SCALING: Record<string, TierScaling> = {
  filler: { power_per_level: 2, mana_per_level: 1, description: '' },
  basic: { power_per_level: 3, mana_per_level: 1, description: '' },
  standard: { power_per_level: 4, mana_per_level: 2, description: '' },
  strong: { power_per_level: 5, mana_per_level: 2, description: '' },
  signature: { power_per_level: 7, mana_per_level: 3, description: '' },
  ultimate: { power_per_level: 10, mana_per_level: 4, description: '' },
};

const DEFAULT_DURATION_SCALING: Record<string, DurationScaling> = {
  hard_cc: { types: ['stun', 'freeze', 'petrify', 'sleep', 'knockdown'], duration_per_level: 0.1, description: '' },
  soft_cc: { types: ['slow', 'root', 'silence', 'blind', 'disarm'], duration_per_level: 0.15, description: '' },
  taunt: { types: ['taunt', 'fear', 'confusion'], duration_per_level: 0.2, description: '' },
  buff: { types: ['damage_reduction', 'atk_up', 'def_up', 'speed_up', 'frenzy'], duration_per_level: 0.3, description: '' },
  debuff: { types: ['armor_reduction', 'atk_down', 'def_down'], duration_per_level: 0.25, description: '' },
  shield: { types: ['shield'], duration_per_level: 0, value_per_level: 8, description: '' },
};

function getDurationScaling(effectType: string, durationScaling: Record<string, DurationScaling>): number {
  for (const [, config] of Object.entries(durationScaling)) {
    if (config.types && config.types.includes(effectType)) {
      return config.duration_per_level;
    }
  }
  return 0.1; // default
}

function getShieldScaling(durationScaling: Record<string, DurationScaling>): number {
  return durationScaling.shield?.value_per_level || 8;
}

function SkillCard({
  skill,
  skillLevel,
  scalingByTier,
  durationScaling
}: {
  skill: Skill;
  skillLevel: number;
  scalingByTier: Record<string, TierScaling>;
  durationScaling: Record<string, DurationScaling>;
}) {
  const tierScaling = scalingByTier[skill.tier] || DEFAULT_TIER_SCALING[skill.tier] || { power_per_level: 2, mana_per_level: 1 };

  // Power/Mana scaling
  const powerAtLevel = skill.base_power > 0
    ? skill.base_power + (skillLevel - 1) * tierScaling.power_per_level
    : 0;
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

  return (
    <div className={`bg-zinc-900 rounded-lg border ${skill.is_signature ? 'border-amber-500/50' : 'border-zinc-800'} overflow-hidden`}>
      {/* Header */}
      <div className={`px-4 py-3 border-b ${skill.is_signature ? 'border-amber-500/30 bg-amber-500/5' : 'border-zinc-800'}`}>
        <div className="flex items-center justify-between">
          <div>
            <h4 className={`font-semibold ${skill.is_signature ? 'text-amber-400' : 'text-white'}`}>
              {skill.is_signature && '⭐ '}{skill.name}
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
            ) : (
              <span className="text-[10px] px-1.5 py-0.5 bg-zinc-700/50 text-zinc-500 border border-zinc-600/30 rounded">
                Req LoS
              </span>
            )}
            <span className={`text-xs px-2 py-1 rounded border ${TIER_COLORS[skill.tier]}`}>
              {skill.tier}
            </span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Stats row */}
        <div className="flex flex-wrap gap-3 mb-3 text-sm">
          {skill.base_power > 0 && (
            <div className="flex items-center gap-1">
              <span className="text-orange-400">⚔️</span>
              <span className="text-zinc-400">Power:</span>
              <span className="text-white">{skill.base_power}</span>
              {skillLevel > 1 && (
                <span className="text-emerald-400 text-xs">→ {powerAtLevel}</span>
              )}
            </div>
          )}
          <div className="flex items-center gap-1">
            <span className="text-sky-400">💧</span>
            <span className="text-zinc-400">Mana:</span>
            <span className="text-white">{skill.mana_cost}</span>
            {skillLevel > 1 && (
              <span className="text-amber-400 text-xs">→ {manaAtLevel}</span>
            )}
          </div>
          <div className="flex items-center gap-1">
            <span className="text-violet-400">⏱️</span>
            <span className="text-zinc-400">CD:</span>
            <span className="text-white">{skill.cooldown}s</span>
          </div>
        </div>

        {/* Two grids: 4x4 and 5x3 */}
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

        {/* Description */}
        <p className="text-sm text-zinc-300 mb-2">
          {skill.description_fr || skill.description_en || 'No description'}
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
            {skill.buff_value && <span className="text-zinc-500"> ({skill.buff_value})</span>}
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

        {skill.shield_value && (
          <div className="text-xs mb-1">
            <span className="text-sky-400">Shield:</span>{' '}
            <span className="text-zinc-300">{skill.shield_value}</span>
            {skillLevel > 1 && (
              <span className="text-emerald-400"> → {shieldValueAtLevel}</span>
            )}
            {skill.shield_duration && <span className="text-zinc-500"> for {skill.shield_duration}s</span>}
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

export default function SkillsPage() {
  const [data, setData] = useState<SkillsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedClass, setSelectedClass] = useState<string>('warrior');
  const [selectedSubclass, setSelectedSubclass] = useState<string | null>(null);
  const [skillLevel, setSkillLevel] = useState(1);

  useEffect(() => {
    fetch('/api/skills')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-zinc-400">Loading skills...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8">
        <div className="text-red-400">Failed to load skills data</div>
      </div>
    );
  }

  const classData = data.classes[selectedClass];
  const subclasses = classData ? Object.keys(classData.subclass_skills) : [];
  const scalingByTier = data.system.scaling_by_tier || DEFAULT_TIER_SCALING;
  const durationScaling = data.system.duration_scaling || DEFAULT_DURATION_SCALING;

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Skills System</h1>
        <p className="text-zinc-500 text-sm">
          {data.system.skill_points.total_points_available} skill points | Max level {data.system.skill_levels.max_level} | v{data.system._meta.version}
        </p>
      </div>

      {/* Skill Level Slider */}
      <div className="mb-6 bg-zinc-900 rounded-lg border border-zinc-800 p-4">
        <div className="flex items-center gap-4">
          <span className="text-zinc-400">Skill Level:</span>
          <input
            type="range"
            min="1"
            max="10"
            value={skillLevel}
            onChange={(e) => setSkillLevel(parseInt(e.target.value))}
            className="flex-1 max-w-xs"
          />
          <span className="text-2xl font-bold text-violet-400 w-8">{skillLevel}</span>
        </div>
        <div className="mt-2 text-xs text-zinc-600">
          Power/Mana + durees d&apos;effets scalent avec le niveau du skill
        </div>
      </div>

      {/* Class Selection */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-3">Select Class</h2>
        <div className="flex flex-wrap gap-2">
          {Object.keys(data.classes).map((className) => (
            <button
              key={className}
              onClick={() => {
                setSelectedClass(className);
                setSelectedSubclass(null);
              }}
              className={`px-4 py-2 rounded-lg border transition-all ${
                selectedClass === className
                  ? `${CLASS_COLORS[className]} bg-zinc-800`
                  : 'border-zinc-700 text-zinc-400 hover:border-zinc-600'
              }`}
            >
              {CLASS_ICONS[className]} {className.charAt(0).toUpperCase() + className.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {classData && (
        <>
          {/* Base Skills */}
          <div className="mb-8">
            <h2 className={`text-xl font-semibold mb-4 ${CLASS_COLORS[selectedClass]?.split(' ')[0]}`}>
              {CLASS_ICONS[selectedClass]} Base Skills ({classData.base_skills.length})
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
              {classData.base_skills.map((skill) => (
                <SkillCard
                  key={skill.id}
                  skill={skill}
                  skillLevel={skillLevel}
                  scalingByTier={scalingByTier}
                  durationScaling={durationScaling}
                />
              ))}
            </div>
          </div>

          {/* Subclass Selection */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-3">Subclasses</h2>
            <div className="flex flex-wrap gap-2">
              {subclasses.map((subclass) => (
                <button
                  key={subclass}
                  onClick={() => setSelectedSubclass(selectedSubclass === subclass ? null : subclass)}
                  className={`px-4 py-2 rounded-lg border transition-all ${
                    selectedSubclass === subclass
                      ? 'border-violet-500/50 bg-violet-500/10 text-violet-400'
                      : 'border-zinc-700 text-zinc-400 hover:border-zinc-600'
                  }`}
                >
                  {subclass.charAt(0).toUpperCase() + subclass.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Subclass Skills */}
          {selectedSubclass && classData.subclass_skills[selectedSubclass] && (
            <div className="mb-8">
              <div className="mb-4">
                <h2 className="text-xl font-semibold text-violet-400">
                  {selectedSubclass.charAt(0).toUpperCase() + selectedSubclass.slice(1)} Skills
                </h2>
                <p className="text-sm text-zinc-500">
                  {classData.subclass_skills[selectedSubclass].identity}
                </p>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                {classData.subclass_skills[selectedSubclass].skills.map((skill) => (
                  <SkillCard
                    key={skill.id}
                    skill={skill}
                    skillLevel={skillLevel}
                    scalingByTier={scalingByTier}
                    durationScaling={durationScaling}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Duration Scaling Reference */}
      <div className="mt-8 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h3 className="font-semibold mb-3">Duration Scaling par Type</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 text-sm">
          {Object.entries(durationScaling)
            .filter(([key]) => !key.startsWith('_'))
            .map(([type, config]) => (
              <div key={type} className="p-2 bg-zinc-800 rounded">
                <div className="font-medium text-zinc-300 capitalize">{type.replace('_', ' ')}</div>
                <div className="text-xs text-zinc-500">
                  {config.duration_per_level > 0
                    ? `+${config.duration_per_level}s/lvl`
                    : config.value_per_level
                      ? `+${config.value_per_level} value/lvl`
                      : 'fixed'
                  }
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
