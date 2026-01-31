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

interface Effect {
  name_fr: string;
  name_en?: string;
  polarity: 'buff' | 'debuff';
  stacking?: string;
  impl: string;
  note?: string;
  formula?: string;
  description_fr?: string;
  description_en?: string;
  max_stacks?: number;
  damage_type?: string;
}

interface EffectsData {
  effects: {
    _meta: {
      version: string;
      stacking_system: {
        refresh: string;
        stackable: string;
        unique: string;
      };
    };
    categories: string[];
    effects: Record<string, Record<string, Effect>>;
    _summary: {
      total: number;
      categories: number;
      by_polarity: {
        buff: number;
        debuff: number;
      };
      breakdown: Record<string, number>;
    };
  };
  config: {
    stacking_system: {
      value_per_stack: number;
      max_stacks: number;
      formula: string;
      examples: Record<string, string>;
    };
    duration_balance: {
      buff_durations: Record<string, { min: number; max: number; typical_use: string }>;
      debuff_durations: Record<string, { min: number; max: number; typical_use: string }>;
    };
    dot_balance: {
      tick_interval: number;
      max_stacks: Record<string, number>;
      damage_formula: Record<string, string>;
    };
    control_effects: Record<string, any>;
    counter_effects: Record<string, any>;
  };
}

const CATEGORY_CONFIG: Record<string, { name: string; icon: string; color: string; description: string }> = {
  dot: { name: 'DoT', icon: '🔥', color: 'text-red-400 border-red-500/30', description: 'Damage over Time' },
  hot: { name: 'HoT', icon: '💚', color: 'text-green-400 border-green-500/30', description: 'Heal over Time' },
  stat_modifiers: { name: 'Stat Modifiers', icon: '📊', color: 'text-blue-400 border-blue-500/30', description: 'Buffs/Debuffs de stats' },
  tempo: { name: 'Tempo', icon: '⚡', color: 'text-yellow-400 border-yellow-500/30', description: 'Attack & Cast speed' },
  control: { name: 'Control (CC)', icon: '🔒', color: 'text-purple-400 border-purple-500/30', description: 'Crowd Control' },
  defensive: { name: 'Defensive', icon: '🛡️', color: 'text-sky-400 border-sky-500/30', description: 'Protection & Tank' },
  immunity: { name: 'Immunity', icon: '✨', color: 'text-emerald-400 border-emerald-500/30', description: 'Immunites (CC, degats, ciblage)' },
  aggro: { name: 'Aggro', icon: '😤', color: 'text-orange-400 border-orange-500/30', description: 'Systeme de menace' },
  special: { name: 'Special', icon: '🎯', color: 'text-amber-400 border-amber-500/30', description: 'Mecaniques uniques' },
};

const IMPL_COLORS: Record<string, string> = {
  done: 'bg-emerald-500/20 text-emerald-400',
  todo: 'bg-zinc-500/20 text-zinc-400',
  v2: 'bg-violet-500/20 text-violet-400',
};

const POLARITY_COLORS: Record<string, string> = {
  buff: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  debuff: 'bg-red-500/20 text-red-400 border-red-500/30',
};

const STACKING_COLORS: Record<string, string> = {
  stackable: 'bg-blue-500/20 text-blue-400',
  refresh: 'bg-amber-500/20 text-amber-400',
  unique: 'bg-zinc-500/20 text-zinc-400',
};

export default function EffectsReferencePage() {
  const [data, setData] = useState<EffectsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPolarity, setFilterPolarity] = useState<'all' | 'buff' | 'debuff'>('all');
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const { locale } = useLocale();

  useEffect(() => {
    fetch('/api/effects')
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
        <div className="text-red-400">Failed to load effects data</div>
      </div>
    );
  }

  const { effects, config } = data;

  // Flatten and filter effects
  const allEffects: { key: string; effect: Effect; category: string }[] = [];
  Object.entries(effects?.effects || {}).forEach(([category, categoryEffects]) => {
    if (category.startsWith('_')) return;
    Object.entries(categoryEffects).forEach(([key, effect]) => {
      if (key.startsWith('_')) return;
      allEffects.push({ key, effect: effect as Effect, category });
    });
  });

  const filteredEffects = allEffects.filter(({ key, effect, category }) => {
    const matchesSearch = searchTerm === '' ||
      key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      effect.name_fr.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (effect.name_en?.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesPolarity = filterPolarity === 'all' || effect.polarity === filterPolarity;
    const matchesCategory = activeCategory === 'all' || category === activeCategory;
    return matchesSearch && matchesPolarity && matchesCategory;
  });

  // Group by category
  const groupedEffects: Record<string, typeof allEffects> = {};
  filteredEffects.forEach((item) => {
    if (!groupedEffects[item.category]) {
      groupedEffects[item.category] = [];
    }
    groupedEffects[item.category].push(item);
  });

  // Category counts
  const categoryCounts: Record<string, number> = { all: allEffects.length };
  Object.entries(CATEGORY_CONFIG).forEach(([key]) => {
    categoryCounts[key] = allEffects.filter(e => e.category === key).length;
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
          <h2 className="text-lg font-semibold">Status Effects</h2>
          <p className="text-xs text-zinc-500 mt-1">
            {effects?._summary?.total || allEffects.length} effects
            {effects?._summary?.by_polarity && ` (${effects._summary.by_polarity.buff} buffs, ${effects._summary.by_polarity.debuff} debuffs)`}
          </p>
          <p className="text-xs text-zinc-600 mt-0.5">v{effects?._meta?.version || 'N/A'}</p>
        </div>

        {/* Search in sidebar */}
        <div className="p-4 border-b border-zinc-800">
          <SearchBar
            value={searchTerm}
            onChange={setSearchTerm}
            placeholder={locale === 'fr' ? 'Rechercher...' : 'Search effects...'}
          />
        </div>

        {/* Polarity Filter */}
        <div className="p-4 border-b border-zinc-800">
          <label className="text-xs text-zinc-500 uppercase tracking-wider mb-2 block">Type</label>
          <ButtonGroup
            options={[
              { value: 'all', label: 'All' },
              { value: 'buff', label: 'Buffs' },
              { value: 'debuff', label: 'Debuffs' },
            ]}
            value={filterPolarity}
            onChange={(value) => setFilterPolarity(value as 'all' | 'buff' | 'debuff')}
          />
        </div>

        {/* Category Navigation */}
        <nav className="p-2">
          <button
            onClick={() => {
              setActiveCategory('all');
              setIsMobileSidebarOpen(false);
            }}
            className={`w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg transition-colors text-left ${
              activeCategory === 'all'
                ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
            }`}
          >
            <span className="flex items-center gap-2">
              <span>📋</span>
              <span>All Categories</span>
            </span>
            <span className="text-xs text-zinc-500">({categoryCounts.all})</span>
          </button>

          {Object.entries(CATEGORY_CONFIG).map(([key, cat]) => (
            <button
              key={key}
              onClick={() => {
                setActiveCategory(key);
                setIsMobileSidebarOpen(false);
              }}
              className={`w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg transition-colors text-left mt-1 ${
                activeCategory === key
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                  : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
              }`}
            >
              <span className="flex items-center gap-2">
                <span>{cat.icon}</span>
                <span>{cat.name}</span>
              </span>
              <span className="text-xs text-zinc-500">({categoryCounts[key] || 0})</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {/* Effects List by Category */}
          <div className="space-y-8">
            {Object.entries(groupedEffects).map(([category, categoryEffects]) => {
          const catConfig = CATEGORY_CONFIG[category];
          if (!catConfig) return null;

          return (
            <div key={category}>
              <h2 className={`text-lg font-semibold mb-3 flex items-center gap-2 ${catConfig.color.split(' ')[0]}`}>
                <span>{catConfig.icon}</span>
                <span>{catConfig.name}</span>
                <span className="text-zinc-600 text-sm font-normal">({categoryEffects.length})</span>
              </h2>

              <Card className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-48">{locale === 'en' ? 'Effect' : 'Effet'}</TableHead>
                      <TableHead className="w-24">Type</TableHead>
                      <TableHead className="w-28">Stacking</TableHead>
                      <TableHead className="w-20">Status</TableHead>
                      <TableHead>{locale === 'en' ? 'Formula / Description' : 'Formule / Description'}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {categoryEffects.map(({ key, effect }) => (
                      <TableRow key={key}>
                        <TableCell>
                          <div className={`font-medium ${catConfig.color.split(' ')[0]}`}>
                            {locale === 'en' && effect.name_en ? effect.name_en : effect.name_fr}
                          </div>
                          {locale === 'en' ? (
                            effect.name_fr && <div className="text-xs text-zinc-500">{effect.name_fr}</div>
                          ) : (
                            effect.name_en && effect.name_en !== effect.name_fr && (
                              <div className="text-xs text-zinc-500">{effect.name_en}</div>
                            )
                          )}
                          <code className="text-[10px] text-zinc-600">{key}</code>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className={POLARITY_COLORS[effect.polarity]}>
                            {effect.polarity}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {effect.stacking ? (
                            <div>
                              <Badge className={STACKING_COLORS[effect.stacking] || STACKING_COLORS.unique}>
                                {effect.stacking}
                              </Badge>
                              {effect.max_stacks && effect.max_stacks > 1 && (
                                <span className="text-[10px] text-zinc-500 ml-1">({effect.max_stacks})</span>
                              )}
                            </div>
                          ) : (
                            <span className="text-xs text-zinc-600">—</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge className={IMPL_COLORS[effect.impl]}>
                            {effect.impl}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">
                          {effect.formula && (
                            <code className="text-xs text-amber-400 block mb-1">{effect.formula}</code>
                          )}
                          {(locale === 'en' ? effect.description_en : effect.description_fr) && (
                            <p className="text-zinc-400 text-xs">
                              {locale === 'en' && effect.description_en ? effect.description_en : effect.description_fr}
                            </p>
                          )}
                          {!effect.formula && !(locale === 'en' ? effect.description_en : effect.description_fr) && (
                            <span className="text-zinc-600">—</span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Card>
            </div>
          );
        })}
      </div>

      {/* Stacking System */}
      <Card className="mt-8 p-6 border-blue-500/30">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-blue-400">
          <span>📊</span> Systeme de Stacking
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-zinc-800 p-4 rounded">
            <h4 className="font-medium text-blue-400 mb-2">Stackable</h4>
            <p className="text-sm text-zinc-400">+{config.stacking_system.value_per_stack}% par stack</p>
            <p className="text-sm text-zinc-400">Max {config.stacking_system.max_stacks} stacks = +100%</p>
            <code className="block text-xs text-emerald-400 mt-2">{config.stacking_system.formula}</code>
          </div>
          <div className="bg-zinc-800 p-4 rounded">
            <h4 className="font-medium text-amber-400 mb-2">Refresh</h4>
            <p className="text-sm text-zinc-400">{effects._meta.stacking_system.refresh}</p>
            <p className="text-xs text-zinc-500 mt-2">CC, shields, etc.</p>
          </div>
          <div className="bg-zinc-800 p-4 rounded">
            <h4 className="font-medium text-zinc-400 mb-2">Unique</h4>
            <p className="text-sm text-zinc-400">{effects._meta.stacking_system.unique}</p>
            <p className="text-xs text-zinc-500 mt-2">Special effects</p>
          </div>
        </div>

        <div className="bg-zinc-800 p-4 rounded">
          <h4 className="font-medium text-emerald-400 mb-2">Exemples de Stacking</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
            {Object.entries(config.stacking_system.examples).map(([key, value]) => (
              <div key={key} className="text-zinc-400">
                <span className="text-zinc-500">{key.replace('_', ' ')}:</span> {value}
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* DoT Balance */}
      <Card className="mt-8 p-6 border-red-500/30">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-red-400">
          <span>🔥</span> DoT Balance
        </h3>

        <p className="text-sm text-zinc-400 mb-4">
          Tick interval: {config.dot_balance.tick_interval}s
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(config.dot_balance.damage_formula).map(([dot, formula]) => (
            <div key={dot} className="bg-zinc-800 p-4 rounded">
              <h4 className="font-medium text-red-400 mb-2 capitalize">{dot}</h4>
              <code className="text-xs text-amber-400">{formula}</code>
              <p className="text-xs text-zinc-500 mt-2">
                Max stacks: {config.dot_balance.max_stacks[dot]}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Control Effects */}
      <Card className="mt-8 p-6 border-purple-500/30">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-purple-400">
          <span>🔒</span> Control Effects (CC)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(config.control_effects).map(([cc, ccData]: [string, any]) => (
            <div key={cc} className="bg-zinc-800 p-4 rounded">
              <h4 className="font-medium text-purple-400 mb-2 capitalize">{cc}</h4>
              <p className="text-xs text-zinc-400">
                Max duration: {ccData.max_duration}s
              </p>
              {ccData.diminishing_returns && (
                <p className="text-xs text-amber-400 mt-1">
                  DR: {ccData.dr_formula}
                </p>
              )}
              {ccData.prevents && (
                <p className="text-xs text-red-400 mt-1">
                  Prevents: {ccData.prevents.join(', ')}
                </p>
              )}
              {ccData.allows && (
                <p className="text-xs text-emerald-400 mt-1">
                  Allows: {ccData.allows.join(', ')}
                </p>
              )}
              {ccData.effect && (
                <p className="text-xs text-zinc-500 mt-1">
                  {ccData.effect}
                </p>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Counter Effects */}
      <Card className="mt-8 p-6 border-amber-500/30">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-amber-400">
          <span>🎯</span> Counter Effects (Anti-Tank/Healer)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(config.counter_effects).filter(([k]) => !k.startsWith('_')).map(([key, effect]: [string, any]) => (
            <div key={key} className="bg-zinc-800 p-4 rounded">
              <h4 className="font-medium text-amber-400 mb-2">{key.replace(/_/g, ' ')}</h4>
              {effect.base_reduction_percent && (
                <p className="text-sm text-zinc-400">
                  -{effect.base_reduction_percent}% healing
                </p>
              )}
              {effect.reduction_percent && (
                <p className="text-sm text-red-400">
                  -{effect.reduction_percent}% (blocked)
                </p>
              )}
              {effect.effect && (
                <p className="text-sm text-zinc-400">{effect.effect}</p>
              )}
              <p className="text-xs text-zinc-500 mt-2">
                Stacking: {effect.stacking}
              </p>
              <p className="text-xs text-zinc-500">
                Duration: {effect.duration?.min}-{effect.duration?.max}s
              </p>
              {effect.counters && (
                <p className="text-xs text-emerald-400 mt-1">
                  Counters: {effect.counters.join(', ')}
                </p>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Duration Balance */}
      <Card className="mt-8 p-6">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-zinc-300">
          <span>⏱️</span> Duration Balance
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-emerald-400 mb-3">Buff Durations</h4>
            <div className="space-y-2">
              {Object.entries(config.duration_balance.buff_durations).map(([tier, data]) => (
                <div key={tier} className="flex items-center justify-between bg-zinc-800 p-2 rounded text-sm">
                  <span className="capitalize text-zinc-300">{tier}</span>
                  <span className="text-emerald-400">{data.min}-{data.max}s</span>
                  <span className="text-xs text-zinc-500">{data.typical_use}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <h4 className="font-medium text-red-400 mb-3">Debuff Durations</h4>
            <div className="space-y-2">
              {Object.entries(config.duration_balance.debuff_durations).map(([tier, data]) => (
                <div key={tier} className="flex items-center justify-between bg-zinc-800 p-2 rounded text-sm">
                  <span className="capitalize text-zinc-300">{tier}</span>
                  <span className="text-red-400">{data.min}-{data.max}s</span>
                  <span className="text-xs text-zinc-500">{data.typical_use}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>
        </div>
      </main>
    </div>
  );
}
