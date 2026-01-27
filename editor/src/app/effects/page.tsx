'use client';

import { useEffect, useState } from 'react';

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
      done: number;
      todo: number;
      v2: number;
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

  useEffect(() => {
    fetch('/api/effects')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-zinc-400">Loading...</div>
      </div>
    );
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
  Object.entries(effects.effects).forEach(([category, categoryEffects]) => {
    if (category.startsWith('_')) return;
    Object.entries(categoryEffects).forEach(([key, effect]) => {
      if (key.startsWith('_')) return;
      allEffects.push({ key, effect: effect as Effect, category });
    });
  });

  const filteredEffects = allEffects.filter(({ key, effect }) => {
    const matchesSearch = searchTerm === '' ||
      key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      effect.name_fr.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPolarity = filterPolarity === 'all' || effect.polarity === filterPolarity;
    return matchesSearch && matchesPolarity;
  });

  // Group by category
  const groupedEffects: Record<string, typeof allEffects> = {};
  filteredEffects.forEach((item) => {
    if (!groupedEffects[item.category]) {
      groupedEffects[item.category] = [];
    }
    groupedEffects[item.category].push(item);
  });

  return (
    <div className="p-4 md:p-6 lg:p-8">
      {/* Header */}
      <div className="mb-4 md:mb-6">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">Status Effects Reference</h1>
        <p className="text-zinc-500 text-sm">
          {effects._summary.total} effects ({effects._summary.done} done, {effects._summary.todo} todo, {effects._summary.v2} v2)
          • v{effects._meta.version}
        </p>
      </div>

      {/* Search & Filter */}
      <div className="mb-6 flex flex-wrap gap-4">
        <input
          type="text"
          placeholder="Rechercher..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2 text-white placeholder-zinc-500 focus:outline-none focus:border-violet-500 w-full max-w-md"
        />
        <div className="flex gap-2">
          <button
            onClick={() => setFilterPolarity('all')}
            className={`px-3 py-2 rounded-lg text-sm ${filterPolarity === 'all' ? 'bg-zinc-700 text-white' : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'}`}
          >
            Tous
          </button>
          <button
            onClick={() => setFilterPolarity('buff')}
            className={`px-3 py-2 rounded-lg text-sm ${filterPolarity === 'buff' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'}`}
          >
            Buffs
          </button>
          <button
            onClick={() => setFilterPolarity('debuff')}
            className={`px-3 py-2 rounded-lg text-sm ${filterPolarity === 'debuff' ? 'bg-red-500/20 text-red-400' : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'}`}
          >
            Debuffs
          </button>
        </div>
      </div>

      {/* Quick Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
        {Object.entries(CATEGORY_CONFIG).map(([key, cat]) => {
          const count = groupedEffects[key]?.length || 0;
          return (
            <div key={key} className={`p-3 rounded-lg border bg-zinc-900 ${cat.color}`}>
              <div className="text-2xl mb-1">{cat.icon}</div>
              <div className="font-medium">{cat.name}</div>
              <div className="text-zinc-500 text-xs">{count} effects</div>
            </div>
          );
        })}
      </div>

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

              <div className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-x-auto">
                <table className="w-full min-w-[600px]">
                  <thead>
                    <tr className="border-b border-zinc-800 text-left text-xs text-zinc-500 uppercase">
                      <th className="px-4 py-3 w-48">Effet</th>
                      <th className="px-4 py-3 w-24">Type</th>
                      <th className="px-4 py-3 w-28">Stacking</th>
                      <th className="px-4 py-3 w-20">Status</th>
                      <th className="px-4 py-3">Formula / Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categoryEffects.map(({ key, effect }) => (
                      <tr key={key} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                        <td className="px-4 py-3">
                          <div className={`font-medium ${catConfig.color.split(' ')[0]}`}>
                            {effect.name_fr}
                          </div>
                          {effect.name_en && effect.name_en !== effect.name_fr && (
                            <div className="text-xs text-zinc-500">{effect.name_en}</div>
                          )}
                          <code className="text-[10px] text-zinc-600">{key}</code>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded border ${POLARITY_COLORS[effect.polarity]}`}>
                            {effect.polarity}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {effect.stacking ? (
                            <div>
                              <span className={`text-xs px-2 py-0.5 rounded ${STACKING_COLORS[effect.stacking] || STACKING_COLORS.unique}`}>
                                {effect.stacking}
                              </span>
                              {effect.max_stacks && effect.max_stacks > 1 && (
                                <span className="text-[10px] text-zinc-500 ml-1">({effect.max_stacks})</span>
                              )}
                            </div>
                          ) : (
                            <span className="text-xs text-zinc-600">—</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded ${IMPL_COLORS[effect.impl]}`}>
                            {effect.impl}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {effect.formula && (
                            <code className="text-xs text-amber-400 block mb-1">{effect.formula}</code>
                          )}
                          {effect.description_fr && (
                            <p className="text-zinc-400 text-xs">{effect.description_fr}</p>
                          )}
                          {!effect.formula && !effect.description_fr && (
                            <span className="text-zinc-600">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          );
        })}
      </div>

      {/* Stacking System */}
      <div className="mt-8 p-6 bg-zinc-900 rounded-lg border border-blue-500/30">
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
      </div>

      {/* DoT Balance */}
      <div className="mt-8 p-6 bg-zinc-900 rounded-lg border border-red-500/30">
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
      </div>

      {/* Control Effects */}
      <div className="mt-8 p-6 bg-zinc-900 rounded-lg border border-purple-500/30">
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
      </div>

      {/* Counter Effects */}
      <div className="mt-8 p-6 bg-zinc-900 rounded-lg border border-amber-500/30">
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
      </div>

      {/* Duration Balance */}
      <div className="mt-8 p-6 bg-zinc-900 rounded-lg border border-zinc-700">
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
      </div>
    </div>
  );
}
