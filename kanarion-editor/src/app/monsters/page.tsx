'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { SearchBar } from '@/components/SearchBar';
import { ButtonGroup } from '@/components/ButtonGroup';
import { LoadingState } from '@/components/LoadingState';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface Monster {
  id: string;
  name: string;
  category: string;
  base_level: number;
  danger_level: number;
  tags: string[];
  ai_role: string;
  base_stats: {
    hp: number;
    atk: number;
    def: number;
    speed: number;
  };
  drops: string[];
}

interface NPC {
  id: string;
  name: string;
  services: string[];
  location: string;
  lore: string;
}

interface NPCsData {
  _meta: {
    version: string;
    last_updated: string;
    description: string;
  };
  types: string[];
  priorities: string[];
  service_npcs: NPC[];
  quest_npcs?: NPC[];
  class_masters?: NPC[];
}

interface MonstersData {
  monsters: {
    _meta: {
      version: string;
      last_updated: string;
      description: string;
    };
    tags_catalog: string[];
    ai_roles_catalog: Record<string, string>;
    monsters: Monster[];
  };
  npcs: NPCsData;
}

const CATEGORY_CONFIG: Record<string, { name: string; icon: string; color: string }> = {
  beast: { name: 'Beast', icon: '🐺', color: 'text-amber-400 border-amber-500/30' },
  humanoid: { name: 'Humanoid', icon: '🧌', color: 'text-orange-400 border-orange-500/30' },
  undead: { name: 'Undead', icon: '💀', color: 'text-purple-400 border-purple-500/30' },
  elemental: { name: 'Elemental', icon: '🔥', color: 'text-blue-400 border-blue-500/30' },
  demon: { name: 'Demon', icon: '👿', color: 'text-red-400 border-red-500/30' },
  corrupted: { name: 'Corrupted', icon: '🌑', color: 'text-violet-400 border-violet-500/30' },
};

const AI_ROLE_ICONS: Record<string, string> = {
  brute: '⚔️',
  assassin: '🗡️',
  tank: '🛡️',
  healer: '💚',
  support: '✨',
  artillery: '🏹',
  tactician: '🧠',
};

export default function MonstersPage() {
  const [data, setData] = useState<MonstersData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'monsters' | 'npcs'>('monsters');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterDanger, setFilterDanger] = useState<string>('all');
  const [filterNPCType, setFilterNPCType] = useState<string>('service');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const { locale } = useLocale();

  useEffect(() => {
    fetch('/api/monsters')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  if (!data || !data.monsters?.monsters) {
    return (
      <div className="p-8">
        <div className="text-red-400">Failed to load monsters data</div>
      </div>
    );
  }

  const monstersData = data.monsters;
  const npcsData = data.npcs;

  // Filter monsters
  const filteredMonsters = monstersData.monsters.filter(monster => {
    const matchesSearch = searchTerm === '' ||
      monster.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      monster.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || monster.category === filterCategory;
    const matchesDanger = filterDanger === 'all' || monster.danger_level === parseInt(filterDanger);
    return matchesSearch && matchesCategory && matchesDanger;
  });

  // Filter NPCs
  const allNPCs = [
    ...(npcsData.service_npcs || []),
    ...(npcsData.quest_npcs || []),
    ...(npcsData.class_masters || []),
  ];
  const filteredNPCs = allNPCs.filter(npc => {
    const matchesSearch = searchTerm === '' ||
      npc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      npc.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      npc.lore.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  // Category counts
  const categories = [...new Set(monstersData.monsters.map(m => m.category))];
  const categoryCounts: Record<string, number> = { all: monstersData.monsters.length };
  categories.forEach(cat => {
    categoryCounts[cat] = monstersData.monsters.filter(m => m.category === cat).length;
  });

  // Danger level counts
  const dangerLevels = [...new Set(monstersData.monsters.map(m => m.danger_level))].sort((a, b) => a - b);
  const dangerCounts: Record<string, number> = { all: monstersData.monsters.length };
  dangerLevels.forEach(level => {
    dangerCounts[level.toString()] = monstersData.monsters.filter(m => m.danger_level === level).length;
  });

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Mobile hamburger button */}
      <button
        onClick={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
        className="lg:hidden fixed top-20 left-4 z-50 p-2 bg-zinc-800 rounded-lg border border-zinc-700 hover:bg-zinc-700 transition-colors"
        aria-label="Toggle filters"
      >
        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {isMobileSidebarOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Mobile overlay */}
      {isMobileSidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsMobileSidebarOpen(false)}
        />
      )}

      {/* Secondary Sidebar */}
      <aside className={`
        w-64 bg-zinc-900/50 border-r border-zinc-800 overflow-y-auto
        lg:block
        ${isMobileSidebarOpen ? 'fixed inset-y-0 left-0 z-40' : 'hidden'}
      `}>
        <div className="p-4 border-b border-zinc-800">
          <h2 className="text-lg font-semibold">{locale === 'en' ? 'Bestiary' : 'Bestiaire'}</h2>
          <p className="text-xs text-zinc-500 mt-1">
            {locale === 'en' ? 'Monsters & NPCs' : 'Monstres & NPCs'} • v{monstersData._meta.version}
          </p>
        </div>

        {/* Tab Selection */}
        <div className="p-2 border-b border-zinc-800">
          <div className="flex gap-1">
            <button
              onClick={() => {
                setActiveTab('monsters');
                setSearchTerm('');
              }}
              className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'monsters'
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                  : 'text-zinc-400 hover:bg-zinc-800/50'
              }`}
            >
              👹 Monsters
            </button>
            <button
              onClick={() => {
                setActiveTab('npcs');
                setSearchTerm('');
              }}
              className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'npcs'
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                  : 'text-zinc-400 hover:bg-zinc-800/50'
              }`}
            >
              🧑 NPCs
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-zinc-800">
          <SearchBar
            value={searchTerm}
            onChange={setSearchTerm}
            placeholder={locale === 'en' ? 'Search...' : 'Rechercher...'}
          />
        </div>

        {/* Filters - Monsters only */}
        {activeTab === 'monsters' && (
          <>
            <div className="p-4 border-b border-zinc-800">
              <label className="text-xs text-zinc-500 uppercase tracking-wider mb-2 block">{locale === 'en' ? 'Danger Level' : 'Niveau de Danger'}</label>
              <ButtonGroup
                options={[
                  { value: 'all', label: 'All' },
                  ...dangerLevels.map(level => ({
                    value: level.toString(),
                    label: `⭐${level}`,
                    count: dangerCounts[level.toString()] || 0,
                  })),
                ]}
                value={filterDanger}
                onChange={setFilterDanger}
              />
            </div>

            <nav className="p-2">
              <div className="text-xs text-zinc-500 uppercase tracking-wider px-2 py-1 mb-1">{locale === 'en' ? 'Category' : 'Catégorie'}</div>

              <button
                onClick={() => {
                  setFilterCategory('all');
                  setIsMobileSidebarOpen(false);
                }}
                className={`w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg transition-colors text-left ${
                  filterCategory === 'all'
                    ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                    : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
                }`}
              >
                <span className="flex items-center gap-2">
                  <span>📋</span>
                  <span>{locale === 'en' ? 'All Categories' : 'Toutes'}</span>
                </span>
                <span className="text-xs text-zinc-500">({categoryCounts.all})</span>
              </button>

              {categories.map(cat => {
                const config = CATEGORY_CONFIG[cat] || { name: cat, icon: '❓', color: 'text-zinc-400' };
                return (
                  <button
                    key={cat}
                    onClick={() => {
                      setFilterCategory(cat);
                      setIsMobileSidebarOpen(false);
                    }}
                    className={`w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg transition-colors text-left mt-1 ${
                      filterCategory === cat
                        ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                        : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <span>{config.icon}</span>
                      <span className="capitalize">{config.name}</span>
                    </span>
                    <span className="text-xs text-zinc-500">({categoryCounts[cat] || 0})</span>
                  </button>
                );
              })}
            </nav>
          </>
        )}

        {/* NPCs info */}
        {activeTab === 'npcs' && (
          <div className="p-4">
            <p className="text-sm text-zinc-400">
              {allNPCs.length} {locale === 'en' ? 'NPCs available' : 'NPCs disponibles'}
            </p>
            <p className="text-xs text-zinc-500 mt-2">
              Services: shops, crafting, quests, teleport, etc.
            </p>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          <div className="mb-4">
            <h1 className="text-2xl font-bold mb-2">
              {activeTab === 'monsters' ? (locale === 'en' ? 'Bestiary' : 'Bestiaire') : 'NPCs'}
            </h1>
            <p className="text-sm text-zinc-500">
              {activeTab === 'monsters'
                ? `${filteredMonsters.length} / ${monstersData.monsters.length} ${locale === 'en' ? 'monsters shown' : 'monstres affichés'}`
                : `${filteredNPCs.length} / ${allNPCs.length} ${locale === 'en' ? 'NPCs shown' : 'NPCs affichés'}`
              }
            </p>
          </div>

          {/* Monsters Table */}
          {activeTab === 'monsters' && (
            <>
          <Card className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-48">{locale === 'en' ? 'Monster' : 'Monstre'}</TableHead>
                  <TableHead className="w-32">{locale === 'en' ? 'Category' : 'Catégorie'}</TableHead>
                  <TableHead className="w-24">{locale === 'en' ? 'Level' : 'Niveau'}</TableHead>
                  <TableHead className="w-24">{locale === 'en' ? 'Danger' : 'Danger'}</TableHead>
                  <TableHead className="w-32">{locale === 'en' ? 'AI Role' : 'Rôle IA'}</TableHead>
                  <TableHead>Stats</TableHead>
                  <TableHead>Tags</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMonsters.map(monster => {
                  const catConfig = CATEGORY_CONFIG[monster.category] || { name: monster.category, icon: '❓', color: 'text-zinc-400' };
                  return (
                    <TableRow key={monster.id}>
                      <TableCell>
                        <div className="font-medium">{monster.name}</div>
                        <code className="text-[10px] text-zinc-600">{monster.id}</code>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={catConfig.color}>
                          {catConfig.icon} {catConfig.name}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="font-mono text-zinc-300">Lv. {monster.base_level}</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-amber-400">{'⭐'.repeat(monster.danger_level)}</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {AI_ROLE_ICONS[monster.ai_role] || '❓'} {monster.ai_role}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1 text-xs">
                          <span className="bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded">HP: {monster.base_stats.hp}</span>
                          <span className="bg-orange-500/20 text-orange-400 px-1.5 py-0.5 rounded">ATK: {monster.base_stats.atk}</span>
                          <span className="bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded">DEF: {monster.base_stats.def}</span>
                          <span className="bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded">SPD: {monster.base_stats.speed}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {monster.tags.slice(0, 3).map(tag => (
                            <Badge key={tag} variant="outline" className="text-[10px]">
                              {tag}
                            </Badge>
                          ))}
                          {monster.tags.length > 3 && (
                            <Badge variant="outline" className="text-[10px]">
                              +{monster.tags.length - 3}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </Card>

            {filteredMonsters.length === 0 && (
              <div className="text-center text-zinc-500 py-8">
                {locale === 'en' ? 'No monsters match the filters.' : 'Aucun monstre ne correspond aux filtres.'}
              </div>
            )}
            </>
          )}

          {/* NPCs Table */}
          {activeTab === 'npcs' && (
            <>
              <Card className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-48">NPC</TableHead>
                      <TableHead className="w-32">Location</TableHead>
                      <TableHead>Services</TableHead>
                      <TableHead>Lore</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredNPCs.map(npc => (
                      <TableRow key={npc.id}>
                        <TableCell>
                          <div className="font-medium">{npc.name}</div>
                          <code className="text-[10px] text-zinc-600">{npc.id}</code>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-sky-400 border-sky-500/30">
                            📍 {npc.location}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {npc.services?.map(service => (
                              <Badge key={service} variant="secondary" className="text-xs">
                                {service.replace(/_/g, ' ')}
                              </Badge>
                            )) || <span className="text-zinc-500">—</span>}
                          </div>
                        </TableCell>
                        <TableCell>
                          <p className="text-sm text-zinc-400 italic">{npc.lore}</p>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Card>

              {filteredNPCs.length === 0 && (
                <div className="text-center text-zinc-500 py-8">
                  {locale === 'en' ? 'No NPCs match the search.' : 'Aucun NPC ne correspond à la recherche.'}
                </div>
              )}
            </>
          )}

          {/* AI Roles Reference - Monsters only */}
          {activeTab === 'monsters' && (
            <Card className="mt-8 p-6">
              <h3 className="text-lg font-semibold mb-4">AI Roles Reference</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(monstersData.ai_roles_catalog).filter(([key]) => !key.startsWith('_')).map(([role, description]) => (
                  <div key={role} className="bg-zinc-800/50 p-3 rounded">
                    <div className="font-medium text-sm flex items-center gap-2">
                      <span>{AI_ROLE_ICONS[role] || '❓'}</span>
                      <span className="capitalize">{role}</span>
                    </div>
                    <p className="text-xs text-zinc-500 mt-1">{description}</p>
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
