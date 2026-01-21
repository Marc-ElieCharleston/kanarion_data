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
  effect?: string;
  effect_chance?: number;
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
  scaling: Record<string, {
    per_level_percent?: number;
    per_level_flat?: number;
    at_level_10: number;
    formula: string;
    description: string;
  }>;
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

function SkillCard({ skill, skillLevel }: { skill: Skill; skillLevel: number }) {
  const scaledPower = skill.base_power > 0
    ? Math.round(skill.base_power * (1 + skillLevel * 0.06))
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
          <span className={`text-xs px-2 py-1 rounded border ${TIER_COLORS[skill.tier]}`}>
            {skill.tier}
          </span>
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
              {skillLevel > 0 && (
                <span className="text-emerald-400 text-xs">→ {scaledPower}</span>
              )}
            </div>
          )}
          <div className="flex items-center gap-1">
            <span className="text-sky-400">💧</span>
            <span className="text-zinc-400">Mana:</span>
            <span className="text-white">{skill.mana_cost}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-violet-400">⏱️</span>
            <span className="text-zinc-400">CD:</span>
            <span className="text-white">{skill.cooldown}s</span>
          </div>
        </div>

        {/* Pattern + Description */}
        <div className="flex gap-4">
          <AoeGrid
            pattern={skill.pattern}
            target={skill.target as 'enemy' | 'ally' | 'self' | 'allies' | 'enemies'}
            size="sm"
          />
          <div className="flex-1">
            <p className="text-sm text-zinc-300">
              {skill.description_fr || skill.description_en || 'No description'}
            </p>

            {/* Effect details */}
            {skill.effect && (
              <div className="mt-2 text-xs">
                <span className="text-violet-400">Effect:</span>{' '}
                <span className="text-zinc-300">{skill.effect}</span>
                {skill.effect_chance && <span className="text-zinc-500"> ({skill.effect_chance}%)</span>}
                {skill.effect_duration && <span className="text-zinc-500"> for {skill.effect_duration}s</span>}
              </div>
            )}

            {skill.buff && (
              <div className="mt-1 text-xs">
                <span className="text-emerald-400">Buff:</span>{' '}
                <span className="text-zinc-300">{skill.buff}</span>
                {skill.buff_value && <span className="text-zinc-500"> ({skill.buff_value})</span>}
                {skill.buff_duration && <span className="text-zinc-500"> for {skill.buff_duration}s</span>}
              </div>
            )}

            {skill.debuff && (
              <div className="mt-1 text-xs">
                <span className="text-red-400">Debuff:</span>{' '}
                <span className="text-zinc-300">{skill.debuff}</span>
                {skill.debuff_value && <span className="text-zinc-500"> ({skill.debuff_value})</span>}
                {skill.debuff_duration && <span className="text-zinc-500"> for {skill.debuff_duration}s</span>}
              </div>
            )}

            {skill.shield_value && (
              <div className="mt-1 text-xs">
                <span className="text-sky-400">Shield:</span>{' '}
                <span className="text-zinc-300">{skill.shield_value}</span>
                {skill.shield_duration && <span className="text-zinc-500"> for {skill.shield_duration}s</span>}
              </div>
            )}
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mt-3">
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
  const [skillLevel, setSkillLevel] = useState(5);

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

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Skills System</h1>
        <p className="text-zinc-500 text-sm">
          {data.system.skill_points.total_points_available} skill points • Max skill level {data.system.skill_levels.max_level} • v{data.system._meta.version}
        </p>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
          <h3 className="font-semibold text-violet-400 mb-2">Skill Points</h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-zinc-500">Points per level</span>
              <span>{data.system.skill_points.points_per_level}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Max player level</span>
              <span>{data.system.skill_points.max_player_level}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Total points</span>
              <span className="text-emerald-400">{data.system.skill_points.total_points_available}</span>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
          <h3 className="font-semibold text-amber-400 mb-2">Skill Categories</h3>
          <div className="space-y-1 text-sm">
            {Object.entries(data.system.skill_categories).map(([key, cat]) => (
              <div key={key} className="flex justify-between">
                <span className="text-zinc-500 capitalize">{key}</span>
                <span>{cat.count} skills (lvl {cat.unlock_at_player_level}+)</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
          <h3 className="font-semibold text-emerald-400 mb-2">Scaling per Level</h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-zinc-500">Power</span>
              <span>+{data.system.scaling.power.per_level_percent}% / lvl</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Effect Chance</span>
              <span>+{data.system.scaling.effect_chance.per_level_flat}% / lvl</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">CD / Mana</span>
              <span className="text-zinc-600">Fixed (via gear)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Skill Level Slider */}
      <div className="mb-6 bg-zinc-900 rounded-lg border border-zinc-800 p-4">
        <div className="flex items-center gap-4">
          <span className="text-zinc-400">Preview skill at level:</span>
          <input
            type="range"
            min="0"
            max="10"
            value={skillLevel}
            onChange={(e) => setSkillLevel(parseInt(e.target.value))}
            className="flex-1 max-w-xs"
          />
          <span className="text-2xl font-bold text-violet-400 w-8">{skillLevel}</span>
        </div>
        {skillLevel > 0 && (
          <div className="mt-2 text-xs text-zinc-500">
            Power: +{Math.round(skillLevel * 6)}% • Effect Chance: +{skillLevel * 3}%
          </div>
        )}
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
                <SkillCard key={skill.id} skill={skill} skillLevel={skillLevel} />
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
                  <SkillCard key={skill.id} skill={skill} skillLevel={skillLevel} />
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Tier Legend */}
      <div className="mt-8 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h3 className="font-semibold mb-3">Skill Tiers</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {Object.entries(data.system.skill_tiers)
            .filter(([tier]) => !tier.startsWith('_'))
            .map(([tier, info]) => (
            <div key={tier} className={`p-3 rounded border ${TIER_COLORS[tier]}`}>
              <div className="font-medium capitalize">{tier}</div>
              <div className="text-xs opacity-70 mt-1">
                Power: {info.power_range[0]}-{info.power_range[1]}
              </div>
              <div className="text-xs opacity-70">
                CD: {info.cooldown_range[0]}-{info.cooldown_range[1]}s
              </div>
              <div className="text-xs opacity-70">
                Mana: {info.mana_range[0]}-{info.mana_range[1]}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
