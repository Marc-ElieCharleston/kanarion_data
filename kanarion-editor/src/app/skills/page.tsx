'use client';

import { useEffect, useState } from 'react';
import SkillCard, {
  Skill,
  TierScaling,
  DurationScaling,
  DEFAULT_TIER_SCALING,
  DEFAULT_DURATION_SCALING
} from '@/components/SkillCard';

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

const CLASS_COLORS: Record<string, string> = {
  warrior: 'text-red-400 border-red-500/30',
  mage: 'text-violet-400 border-violet-500/30',
  healer: 'text-emerald-400 border-emerald-500/30',
  archer: 'text-amber-400 border-amber-500/30',
  rogue: 'text-zinc-300 border-zinc-500/30',
  artisan: 'text-orange-400 border-orange-500/30',
};

const CLASS_ICONS: Record<string, string> = {
  warrior: '!',
  mage: '*',
  healer: '+',
  archer: '>',
  rogue: '/',
  artisan: '#',
};

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
        <p className="text-zinc-600 text-xs mt-1">
          Double scaling: Base flat + % stat. Both increase with level.
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
          Base, %, Mana, et durees d&apos;effets scalent avec le niveau du skill
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

      {/* Scaling Reference */}
      <div className="mt-8 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h3 className="font-semibold mb-3">Scaling par Tier (par niveau)</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 text-sm">
          {Object.entries(scalingByTier)
            .filter(([key]) => !key.startsWith('_'))
            .map(([tier, config]) => (
              <div key={tier} className="p-2 bg-zinc-800 rounded">
                <div className="font-medium text-zinc-300 capitalize">{tier}</div>
                <div className="text-xs text-zinc-500">
                  +{config.power_per_level} base, +{config.percent_per_level || 4}%
                </div>
                <div className="text-xs text-zinc-600">
                  +{config.mana_per_level} mana
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Duration Scaling Reference */}
      <div className="mt-4 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
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
