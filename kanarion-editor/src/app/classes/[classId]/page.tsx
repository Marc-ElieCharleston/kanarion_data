'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import StatsDisplay from '@/components/StatsDisplay';
import SkillCard from '@/components/SkillCard';
import LevelSlider from '@/components/LevelSlider';

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
  const [activeTab, setActiveTab] = useState<'stats' | 'base' | string>('stats');
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
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-zinc-400">Loading...</div>
      </div>
    );
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

  const tabs = [
    { id: 'stats', label: 'Stats', icon: '📊' },
    { id: 'base', label: 'Base Skills', icon: '⚡' },
    ...subclasses.map(sc => ({
      id: sc,
      label: sc.charAt(0).toUpperCase() + sc.slice(1),
      icon: '🎭',
    })),
  ];

  const renderContent = () => {
    if (activeTab === 'stats') {
      return (
        <div className="space-y-6">
          <LevelSlider level={level} onChange={setLevel} maxLevel={60} />
          <StatsDisplay
            baseStats={classData.baseStats}
            growth={classData.growth}
            level={level}
          />
        </div>
      );
    }

    if (activeTab === 'base') {
      return (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-zinc-300">Base Skills</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {classData.skills?.base_skills?.map((skill) => (
              <SkillCard key={skill.id} skill={skill} />
            ))}
          </div>
        </div>
      );
    }

    // Subclass skills
    const subclass = classData.skills?.subclass_skills?.[activeTab];
    if (!subclass) return null;

    return (
      <div className="space-y-4">
        <div className="bg-zinc-900 p-4 rounded-lg border border-zinc-700">
          <h3 className="text-lg font-semibold text-zinc-300 capitalize">{activeTab}</h3>
          <p className="text-sm text-zinc-500">{subclass.identity}</p>
          <p className="text-xs text-amber-400 mt-1">
            Signature: {subclass.signature}
          </p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {subclass.skills?.map((skill) => (
            <SkillCard key={skill.id} skill={skill} />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <span className="text-5xl">{CLASS_ICONS[classId] || '⚔️'}</span>
        <div>
          <h1 className="text-3xl font-bold capitalize">{classData.name}</h1>
          <p className="text-zinc-400">{classData.baseStats.identity}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-6 border-b border-zinc-800 pb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === tab.id
                ? 'bg-violet-600 text-white'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-white'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      {renderContent()}

      {/* Pattern Legend */}
      {activeTab !== 'stats' && classData.skills?._meta?.pattern_presets && (
        <div className="mt-8 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
          <h4 className="text-sm font-semibold text-zinc-400 mb-3">Pattern Legend</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 text-xs">
            {Object.entries(classData.skills._meta.pattern_presets).map(([key, desc]) => (
              <div key={key} className="flex items-center gap-2">
                <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-violet-400">{key}</code>
                <span className="text-zinc-500">{desc}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
