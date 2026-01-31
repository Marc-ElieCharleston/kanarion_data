'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { LoadingState } from '@/components/LoadingState';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Zone {
  id: string;
  name: string;
  level_range: [number, number];
  description: string;
  mobs: { id: string; weight: number }[];
  elite_pool: string[];
  boss: { id: string; name_override: string };
  loot_table: string;
  dungeon_portal?: { id: string; min_level: number };
}

interface DungeonFloor {
  floor: number;
  name: string;
  name_fr?: string;
  description: string;
  description_fr?: string;
  mob_groups: {
    group_id: number;
    position: string;
    mobs: { id: string; count: number; level_offset: number; is_elite?: boolean }[];
  }[];
  boss?: {
    id: string;
    name: string;
    name_fr: string;
    level_offset: number;
    mechanics: string[];
  };
}

interface Dungeon {
  id: string;
  name: string;
  name_fr: string;
  description: string;
  description_fr: string;
  level_range: [number, number];
  min_level: number;
  recommended_party_size: [number, number];
  type: string;
  entry_location: string;
  duration_estimate_minutes: [number, number];
  floors: DungeonFloor[];
}

interface Quest {
  id: string;
  type: string;
  zone: string;
  title: string;
  summary: string;
  reset?: string;
  objectives: { template: string; mobs?: string[]; count?: number; boss?: string; min_star?: number }[];
  rewards: { xp_percent: number; gold: number; items?: { id: string; qty: number }[]; extra_loot_rolls?: number };
}

interface WorldData {
  zones: { _meta: unknown; zones: Zone[] };
  dungeons: { _meta: unknown; difficulty_modifiers: Record<string, unknown>; dungeons: Dungeon[] };
  quests: { _meta: unknown; quests: Quest[] };
}

const TABS = [
  { id: 'zones', name_fr: 'Zones', name_en: 'Zones', icon: '🗺️' },
  { id: 'dungeons', name_fr: 'Donjons', name_en: 'Dungeons', icon: '🏰' },
  { id: 'quests', name_fr: 'Quetes', name_en: 'Quests', icon: '📜' },
];

function ZonesTab({ data }: { data: WorldData['zones'] }) {
  const { locale } = useLocale();
  const zones = data.zones || [];

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-sm text-zinc-500">{zones.length} {locale === 'en' ? 'zones available' : 'zones disponibles'}</h3>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {zones.map((zone) => (
          <Card key={zone.id} className="p-4 hover:border-zinc-600 transition-colors">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-zinc-200">{zone.name}</h3>
              <Badge className="bg-blue-500/20 text-blue-400">
                Lv {zone.level_range[0]}-{zone.level_range[1]}
              </Badge>
            </div>
            <p className="text-sm text-zinc-400 mb-4">{zone.description}</p>

            {/* Mobs */}
            <div className="mb-3">
              <span className="text-xs text-zinc-500 block mb-1">{locale === 'en' ? 'Monsters' : 'Monstres'}:</span>
              <div className="flex flex-wrap gap-1">
                {zone.mobs.map((mob) => (
                  <span key={mob.id} className="text-xs bg-zinc-800 px-2 py-0.5 rounded text-zinc-300">
                    {mob.id.replace('mob_', '')} ({mob.weight}%)
                  </span>
                ))}
              </div>
            </div>

            {/* Elites */}
            <div className="mb-3">
              <span className="text-xs text-zinc-500 block mb-1">{locale === 'en' ? 'Elite Pool' : 'Pool Elite'}:</span>
              <div className="flex flex-wrap gap-1">
                {zone.elite_pool.map((elite) => (
                  <span key={elite} className="text-xs bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded">
                    {elite.replace('mob_', '')}
                  </span>
                ))}
              </div>
            </div>

            {/* Boss */}
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs text-zinc-500">{locale === 'en' ? 'Boss' : 'Boss'}:</span>
                <span className="text-sm text-orange-400 ml-2">{zone.boss.name_override}</span>
              </div>
              {zone.dungeon_portal && (
                <Badge className="bg-emerald-500/20 text-emerald-400">
                  {locale === 'en' ? 'Dungeon Lv' : 'Donjon Lv'} {zone.dungeon_portal.min_level}+
                </Badge>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function DungeonsTab({ data }: { data: WorldData['dungeons'] }) {
  const { locale } = useLocale();
  const dungeons = data.dungeons || [];
  const difficulties = data.difficulty_modifiers as Record<string, {
    hp_multiplier: number;
    damage_multiplier: number;
    xp_multiplier: number;
    gold_multiplier: number;
    loot_quality_bonus: number;
    description: string;
  }>;

  return (
    <div>
      {/* Difficulty Legend */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h3 className="text-sm font-medium mb-3">{locale === 'en' ? 'Difficulty Modifiers' : 'Modificateurs de Difficulte'}</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {Object.entries(difficulties).map(([key, diff]) => (
            <div key={key} className={`p-3 rounded-lg border ${
              key === 'normal' ? 'border-green-500/30 bg-green-500/10' :
              key === 'hard' ? 'border-yellow-500/30 bg-yellow-500/10' :
              'border-red-500/30 bg-red-500/10'
            }`}>
              <h4 className="font-medium capitalize mb-2">{key}</h4>
              <div className="text-xs space-y-1 text-zinc-400">
                <div>HP: x{diff.hp_multiplier}</div>
                <div>DMG: x{diff.damage_multiplier}</div>
                <div>XP/Gold: x{diff.xp_multiplier}</div>
                <div>Loot: +{diff.loot_quality_bonus}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dungeons */}
      <div className="space-y-6">
        {dungeons.map((dungeon) => (
          <Card key={dungeon.id} className="p-5 hover:border-zinc-600 transition-colors">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-xl font-semibold text-zinc-200">
                  {locale === 'en' ? dungeon.name : dungeon.name_fr}
                </h3>
                <p className="text-sm text-zinc-500">
                  {locale === 'en' ? dungeon.name_fr : dungeon.name}
                </p>
              </div>
              <div className="text-right">
                <Badge className="bg-blue-500/20 text-blue-400 mb-1">
                  Lv {dungeon.level_range[0]}-{dungeon.level_range[1]}
                </Badge>
                <div className="text-xs text-zinc-500">
                  {dungeon.recommended_party_size[0]}-{dungeon.recommended_party_size[1]} {locale === 'en' ? 'players' : 'joueurs'}
                </div>
              </div>
            </div>

            <p className="text-sm text-zinc-400 mb-4">
              {locale === 'en' ? dungeon.description : dungeon.description_fr}
            </p>

            <div className="flex flex-wrap gap-2 mb-4">
              <Badge variant="outline" className="text-xs">
                {dungeon.floors.length} {locale === 'en' ? 'floors' : 'etages'}
              </Badge>
              <Badge variant="outline" className="text-xs">
                {dungeon.duration_estimate_minutes[0]}-{dungeon.duration_estimate_minutes[1]} min
              </Badge>
              <Badge variant="outline" className="text-xs capitalize">
                {dungeon.type.replace(/_/g, ' ')}
              </Badge>
            </div>

            {/* Floors Summary */}
            <div className="space-y-2">
              <span className="text-xs text-zinc-500">{locale === 'en' ? 'Floors' : 'Etages'}:</span>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                {dungeon.floors.map((floor) => (
                  <div key={floor.floor} className="bg-zinc-800/50 p-2 rounded text-sm">
                    <div className="font-medium text-zinc-300">
                      {floor.floor}. {locale === 'en' ? floor.name : (floor.name_fr || floor.name)}
                    </div>
                    <div className="text-xs text-zinc-500">
                      {floor.mob_groups.length} {locale === 'en' ? 'groups' : 'groupes'}
                      {floor.boss && <span className="text-orange-400 ml-2">BOSS</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function QuestsTab({ data }: { data: WorldData['quests'] }) {
  const { locale } = useLocale();
  const [filter, setFilter] = useState<string>('all');
  const quests = data.quests || [];

  const filteredQuests = filter === 'all' ? quests : quests.filter((q) => q.type === filter);

  const typeColors: Record<string, string> = {
    main: 'bg-yellow-500/20 text-yellow-400',
    side: 'bg-blue-500/20 text-blue-400',
    repeatable: 'bg-green-500/20 text-green-400',
  };

  return (
    <div>
      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {['all', 'main', 'side', 'repeatable'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-4 py-2 rounded-lg transition-colors capitalize ${
              filter === type
                ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
            }`}
          >
            {type === 'all' ? (locale === 'en' ? 'All' : 'Tous') : type}
            {type !== 'all' && ` (${quests.filter((q) => q.type === type).length})`}
          </button>
        ))}
      </div>

      {/* Quests Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm bg-zinc-900 rounded-lg border border-zinc-800">
          <thead>
            <tr className="border-b border-zinc-700">
              <th className="text-left py-3 px-4 text-zinc-400">{locale === 'en' ? 'Quest' : 'Quete'}</th>
              <th className="text-center py-3 px-4 text-zinc-400">{locale === 'en' ? 'Type' : 'Type'}</th>
              <th className="text-center py-3 px-4 text-zinc-400">{locale === 'en' ? 'Zone' : 'Zone'}</th>
              <th className="text-left py-3 px-4 text-zinc-400">{locale === 'en' ? 'Objectives' : 'Objectifs'}</th>
              <th className="text-right py-3 px-4 text-zinc-400">{locale === 'en' ? 'Rewards' : 'Recompenses'}</th>
            </tr>
          </thead>
          <tbody>
            {filteredQuests.map((quest, i) => (
              <tr key={quest.id} className={`border-b border-zinc-800 ${i % 2 === 0 ? 'bg-zinc-800/20' : ''}`}>
                <td className="py-3 px-4">
                  <div className="font-medium text-zinc-200">{quest.title}</div>
                  <div className="text-xs text-zinc-500">{quest.summary}</div>
                </td>
                <td className="py-3 px-4 text-center">
                  <Badge className={`${typeColors[quest.type]} capitalize`}>
                    {quest.type}
                  </Badge>
                  {quest.reset && (
                    <div className="text-xs text-zinc-500 mt-1">{quest.reset}</div>
                  )}
                </td>
                <td className="py-3 px-4 text-center text-zinc-400">
                  {quest.zone.replace('zone_', 'Z')}
                </td>
                <td className="py-3 px-4">
                  {quest.objectives.map((obj, j) => (
                    <div key={j} className="text-xs text-zinc-400">
                      {obj.template === 'kill_mobs' && `Kill ${obj.count} ${obj.mobs?.join('/')}`}
                      {obj.template === 'defeat_boss' && `Defeat ${obj.boss}`}
                      {obj.template === 'defeat_elite' && `Defeat ${obj.count} elite`}
                      {obj.template === 'clear_star_packs' && `Clear ${obj.count}x ${obj.min_star}★ pack`}
                    </div>
                  ))}
                </td>
                <td className="py-3 px-4 text-right">
                  <div className="text-emerald-400 text-xs">+{quest.rewards.xp_percent}% XP</div>
                  <div className="text-yellow-400 text-xs">{quest.rewards.gold}g</div>
                  {quest.rewards.items && (
                    <div className="text-blue-400 text-xs">+{quest.rewards.items.length} items</div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function WorldPage() {
  const [activeTab, setActiveTab] = useState('zones');
  const [data, setData] = useState<WorldData | null>(null);
  const [loading, setLoading] = useState(true);
  const { locale } = useLocale();

  useEffect(() => {
    fetch('/api/world')
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <LoadingState />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-red-400">
        {locale === 'en' ? 'Failed to load world data' : 'Erreur de chargement'}
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Secondary Sidebar */}
      <aside className="w-64 border-r border-zinc-800 overflow-y-auto bg-zinc-900/50">
        <div className="p-4 border-b border-zinc-800">
          <h2 className="text-lg font-semibold">{locale === 'en' ? 'World' : 'Monde'}</h2>
          <p className="text-xs text-zinc-500">{locale === 'en' ? 'Zones, dungeons & quests' : 'Zones, donjons & quetes'}</p>
        </div>
        <nav className="p-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-left ${
                activeTab === tab.id
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                  : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
              }`}
            >
              <span className="text-xl">{tab.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{locale === 'en' ? tab.name_en : tab.name_fr}</div>
                <div className="text-xs text-zinc-500 truncate">{locale === 'en' ? tab.name_fr : tab.name_en}</div>
              </div>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {activeTab === 'zones' && <ZonesTab data={data.zones} />}
          {activeTab === 'dungeons' && <DungeonsTab data={data.dungeons} />}
          {activeTab === 'quests' && <QuestsTab data={data.quests} />}
        </div>
      </main>
    </div>
  );
}
