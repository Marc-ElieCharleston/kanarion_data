'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import StatsDisplay from '@/components/StatsDisplay';
import SkillCard, { TierScaling, DurationScaling, DEFAULT_TIER_SCALING, DEFAULT_DURATION_SCALING } from '@/components/SkillCard';
import { RangeSlider } from '@/components/RangeSlider';
import { TabsGroup } from '@/components/TabsGroup';
import { LoadingState } from '@/components/LoadingState';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ClassData {
  id: string;
  name: string;
  baseStats: Record<string, number | string>;
  growth: Record<string, number>;
  skills: {
    _meta: {
      pattern_presets: Record<string, string>;
    };
    base_skills: any[];
    subclass_skills: Record<string, {
      identity: string;
      signature: string;
      skills: any[];
    }>;
  };
}

const CLASS_ICONS: Record<string, string> = {
  warrior: '🗡️',
  mage: '🔮',
  healer: '💚',
  archer: '🏹',
  rogue: '🗡️',
  artisan: '🔧',
};

export default function ClassDetailPage() {
  const params = useParams();
  const classId = params.classId as string;

  const [classData, setClassData] = useState<ClassData | null>(null);
  const [level, setLevel] = useState(1);
  const [skillLevel, setSkillLevel] = useState(1);
  const [activeTab, setActiveTab] = useState<string>('stats');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/classes/${classId}`)
      .then(res => res.json())
      .then(data => {
        setClassData(data);
        setLoading(false);
      });
  }, [classId]);

  if (loading) {
    return <LoadingState />;
  }

  if (!classData) {
    return (
      <div className="p-8">
        <div className="text-red-400">Class not found</div>
      </div>
    );
  }

  const subclasses = classData.skills?.subclass_skills
    ? Object.keys(classData.skills.subclass_skills)
    : [];

  // Stats Tab Content
  const StatsTabContent = () => (
    <div className="space-y-6">
      <RangeSlider
        label="Character Level"
        value={level}
        onChange={setLevel}
        min={1}
        max={60}
      />
      <StatsDisplay
        baseStats={classData.baseStats}
        growth={classData.growth}
        level={level}
      />
    </div>
  );

  // Base Skills Tab Content
  const BaseSkillsTabContent = () => (
    <div className="space-y-4">
      <Card className="p-4">
        <RangeSlider
          label="Skill Level"
          value={skillLevel}
          onChange={setSkillLevel}
          min={1}
          max={10}
        />
      </Card>
      <h3 className="text-lg font-semibold text-zinc-300">Base Skills</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {classData.skills?.base_skills?.map((skill) => (
          <SkillCard
            key={skill.id}
            skill={skill}
            skillLevel={skillLevel}
            scalingByTier={DEFAULT_TIER_SCALING}
            durationScaling={DEFAULT_DURATION_SCALING}
          />
        ))}
      </div>
    </div>
  );

  // Subclass Tab Content Factory
  const SubclassTabContent = (subclassId: string) => {
    const subclass = classData.skills?.subclass_skills?.[subclassId];
    if (!subclass) return null;

    return (
      <div className="space-y-4">
        <Card className="p-4">
          <RangeSlider
            label="Skill Level"
            value={skillLevel}
            onChange={setSkillLevel}
            min={1}
            max={10}
          />
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-semibold text-zinc-300 capitalize">{subclassId}</h3>
          <p className="text-sm text-zinc-500">{subclass.identity}</p>
          <Badge variant="outline" className="mt-2">
            Signature: {subclass.signature}
          </Badge>
        </Card>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {subclass.skills?.map((skill) => (
            <SkillCard
              key={skill.id}
              skill={skill}
              skillLevel={skillLevel}
              scalingByTier={DEFAULT_TIER_SCALING}
              durationScaling={DEFAULT_DURATION_SCALING}
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
          <div className="flex items-center gap-3 mb-2">
            <span className="text-3xl">{CLASS_ICONS[classId] || '⚔️'}</span>
            <div>
              <h2 className="text-lg font-semibold capitalize">{classData.name}</h2>
              <p className="text-xs text-zinc-500">{classData.baseStats.identity}</p>
            </div>
          </div>
        </div>
        <nav className="p-2">
          <button
            onClick={() => setActiveTab('stats')}
            className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg transition-colors text-left ${
              activeTab === 'stats'
                ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
            }`}
          >
            <span>📊</span>
            <span>Stats</span>
          </button>
          <button
            onClick={() => setActiveTab('base')}
            className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg transition-colors text-left mt-1 ${
              activeTab === 'base'
                ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
            }`}
          >
            <span>⚡</span>
            <span>Base Skills</span>
          </button>
          {subclasses.length > 0 && (
            <div className="mt-3 pt-3 border-t border-zinc-800">
              <div className="px-2 py-1 text-xs text-zinc-500 uppercase tracking-wider">Subclasses</div>
              {subclasses.map(sc => (
                <button
                  key={sc}
                  onClick={() => setActiveTab(sc)}
                  className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg transition-colors text-left mt-1 ${
                    activeTab === sc
                      ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                      : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
                  }`}
                >
                  <span>🎭</span>
                  <span className="capitalize">{sc}</span>
                </button>
              ))}
            </div>
          )}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {activeTab === 'stats' && <StatsTabContent />}
          {activeTab === 'base' && <BaseSkillsTabContent />}
          {subclasses.includes(activeTab) && SubclassTabContent(activeTab)}

          {/* Pattern Legend */}
          {activeTab !== 'stats' && classData.skills?._meta?.pattern_presets && (
            <Card className="mt-8 p-4">
              <h4 className="text-sm font-semibold text-zinc-400 mb-3">Pattern Legend</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 text-xs">
                {Object.entries(classData.skills._meta.pattern_presets).map(([key, desc]) => (
                  <div key={key} className="flex items-center gap-2">
                    <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-violet-400">{key}</code>
                    <span className="text-zinc-500">{desc}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}
