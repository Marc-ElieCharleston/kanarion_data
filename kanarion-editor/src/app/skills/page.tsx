'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import SkillCard, {
  Skill,
  TierScaling,
  DurationScaling,
  DEFAULT_TIER_SCALING,
  DEFAULT_DURATION_SCALING
} from '@/components/SkillCard';
import { RangeSlider } from '@/components/RangeSlider';
import { LoadingState } from '@/components/LoadingState';
import { Card } from '@/components/ui/card';

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
  const [activeView, setActiveView] = useState<string>('warrior-base');
  const [skillLevel, setSkillLevel] = useState(1);
  const { locale } = useLocale();

  useEffect(() => {
    fetch('/api/skills')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  if (!data) {
    return (
      <div className="p-8">
        <div className="text-red-400">Failed to load skills data</div>
      </div>
    );
  }

  const scalingByTier = data.system.scaling_by_tier || DEFAULT_TIER_SCALING;
  const durationScaling = data.system.duration_scaling || DEFAULT_DURATION_SCALING;

  // Parse activeView to get class and subclass
  const [selectedClass, viewType] = activeView.split('-');
  const classData = data.classes[selectedClass];
  const isBaseView = viewType === 'base';
  const selectedSubclass = isBaseView ? null : viewType;

  // Content Components
  const BaseSkillsContent = ({ className }: { className: string }) => {
    const classInfo = data.classes[className];
    if (!classInfo) return null;

    return (
      <div>
        <h2 className={`text-xl font-semibold mb-4 ${CLASS_COLORS[className]?.split(' ')[0]}`}>
          {CLASS_ICONS[className]} Base Skills ({classInfo.base_skills.length})
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {classInfo.base_skills.map((skill) => (
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
    );
  };

  const SubclassSkillsContent = ({ className, subclass }: { className: string; subclass: string }) => {
    const classInfo = data.classes[className];
    if (!classInfo || !classInfo.subclass_skills[subclass]) return null;

    const subclassData = classInfo.subclass_skills[subclass];

    return (
      <div>
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-violet-400 capitalize">
            {subclass} Skills
          </h2>
          <p className="text-sm text-zinc-500">{subclassData.identity}</p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {subclassData.skills.map((skill) => (
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
    );
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Secondary Sidebar */}
      <aside className="w-64 border-r border-zinc-800 overflow-y-auto bg-zinc-900/50">
        <div className="p-4 border-b border-zinc-800">
          <h2 className="text-lg font-semibold">{locale === 'en' ? 'Skills System' : 'Système de Skills'}</h2>
          <p className="text-xs text-zinc-500 mt-1">
            {data.system.skill_points.total_points_available} points | v{data.system._meta.version}
          </p>
        </div>

        <nav className="p-2">
          {Object.keys(data.classes).map((className) => {
            const classInfo = data.classes[className];
            const subclasses = Object.keys(classInfo.subclass_skills);

            return (
              <div key={className} className="mb-2">
                {/* Base Skills Button */}
                <button
                  onClick={() => setActiveView(`${className}-base`)}
                  className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg transition-colors text-left ${
                    activeView === `${className}-base`
                      ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                      : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
                  }`}
                >
                  <span>{CLASS_ICONS[className]}</span>
                  <span className="capitalize">{className}</span>
                </button>

                {/* Subclasses */}
                <div className="ml-4 mt-1 space-y-0.5">
                  {subclasses.map((subclass) => (
                    <button
                      key={subclass}
                      onClick={() => setActiveView(`${className}-${subclass}`)}
                      className={`w-full flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors text-left text-sm ${
                        activeView === `${className}-${subclass}`
                          ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                          : 'text-zinc-500 hover:bg-zinc-800/30 hover:text-zinc-400'
                      }`}
                    >
                      <span className="capitalize">{subclass}</span>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {/* Skill Level Slider */}
          <Card className="mb-6 p-4">
            <RangeSlider
              label={locale === 'en' ? 'Skill Level' : 'Niveau du Skill'}
              value={skillLevel}
              onChange={setSkillLevel}
              min={1}
              max={10}
            />
            <div className="mt-2 text-xs text-zinc-600">
              {locale === 'en'
                ? 'Base, %, Mana, and effect durations scale with skill level'
                : 'Base, %, Mana, et durées d\'effets scalent avec le niveau du skill'}
            </div>
          </Card>

          {/* Skills Display */}
          {isBaseView ? (
            <BaseSkillsContent className={selectedClass} />
          ) : selectedSubclass ? (
            <SubclassSkillsContent className={selectedClass} subclass={selectedSubclass} />
          ) : null}

          {/* Scaling Reference */}
          <Card className="mt-8 p-4">
            <h3 className="font-semibold mb-3">{locale === 'en' ? 'Scaling by Tier (per level)' : 'Scaling par Tier (par niveau)'}</h3>
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
          </Card>

          {/* Duration Scaling Reference */}
          <Card className="mt-4 p-4">
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
          </Card>
        </div>
      </main>
    </div>
  );
}
