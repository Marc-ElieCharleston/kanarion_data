'use client';

import { useEffect, useState } from 'react';

interface StarTier {
  name_fr: string;
  name_en: string;
  icon: string;
  color: string;
  monster_count: { min: number; max: number };
  stat_bonus_percent: number;
  elite_chance: number;
  elite_count: { min: number; max: number };
  boss_chance: number;
  boss_count?: number;
  loot_multiplier: number;
  xp_multiplier: number;
  gold_multiplier: number;
  guaranteed_loot?: boolean;
  description_fr: string;
  description_en: string;
}

interface EncounterStarsData {
  _meta: {
    version: string;
    last_updated: string;
    description: string;
  };
  overview: {
    description: string;
    affects: string[];
  };
  star_tiers: Record<string, StarTier>;
  loot_integration: {
    rarity_boost: Record<string, number>;
  };
}

const TABS = [
  { id: 'encounter-stars', name: 'Système d\'Étoiles', icon: '⭐' },
  { id: 'economy', name: 'Économie', icon: '💰', disabled: true },
  { id: 'pvp', name: 'PvP', icon: '⚔️', disabled: true },
  { id: 'guilds', name: 'Guildes', icon: '🏰', disabled: true },
];

function StarTierCard({ tier, data }: { tier: string; data: StarTier }) {
  const rarityBoost = tier === '3' ? 1 : tier === '4' ? 1 : tier === '5' ? 2 : 0;

  return (
    <div
      className="bg-zinc-900 rounded-lg border border-zinc-800 p-4 hover:border-zinc-700 transition-colors"
      style={{ borderLeftColor: data.color, borderLeftWidth: '4px' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl" style={{ color: data.color }}>{data.icon}</span>
          <div>
            <h3 className="font-semibold" style={{ color: data.color }}>{data.name_fr}</h3>
            <p className="text-xs text-zinc-500">{data.name_en}</p>
          </div>
        </div>
        {data.guaranteed_loot && (
          <span className="bg-yellow-500/20 text-yellow-400 text-xs px-2 py-1 rounded">
            Loot Garanti
          </span>
        )}
      </div>

      {/* Description */}
      <p className="text-sm text-zinc-400 mb-4">{data.description_fr}</p>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
        <div className="bg-zinc-800/50 rounded p-2 text-center">
          <div className="text-xs text-zinc-500">Monstres</div>
          <div className="font-mono text-zinc-200">{data.monster_count.min}-{data.monster_count.max}</div>
        </div>
        <div className="bg-zinc-800/50 rounded p-2 text-center">
          <div className="text-xs text-zinc-500">Stats Bonus</div>
          <div className="font-mono text-red-400">+{data.stat_bonus_percent}%</div>
        </div>
        <div className="bg-zinc-800/50 rounded p-2 text-center">
          <div className="text-xs text-zinc-500">Élites</div>
          <div className="font-mono text-purple-400">
            {data.elite_chance > 0 ? `${data.elite_count.min}-${data.elite_count.max}` : '-'}
            {data.elite_chance > 0 && data.elite_chance < 100 && (
              <span className="text-xs text-zinc-500"> ({data.elite_chance}%)</span>
            )}
          </div>
        </div>
        <div className="bg-zinc-800/50 rounded p-2 text-center">
          <div className="text-xs text-zinc-500">Boss</div>
          <div className="font-mono text-orange-400">
            {data.boss_chance > 0 ? data.boss_count || 1 : '-'}
          </div>
        </div>
      </div>

      {/* Multipliers */}
      <div className="flex flex-wrap gap-2">
        <span className="bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded">
          Loot ×{data.loot_multiplier}
        </span>
        <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded">
          XP ×{data.xp_multiplier}
        </span>
        <span className="bg-yellow-500/20 text-yellow-400 text-xs px-2 py-1 rounded">
          Gold ×{data.gold_multiplier}
        </span>
        {rarityBoost > 0 && (
          <span className="bg-purple-500/20 text-purple-400 text-xs px-2 py-1 rounded">
            Rareté +{rarityBoost}
          </span>
        )}
      </div>
    </div>
  );
}

function EncounterStarsTab() {
  const [data, setData] = useState<EncounterStarsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/systems/encounter-stars')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="animate-pulse text-zinc-500">Chargement...</div>;
  }

  if (!data) {
    return <div className="text-red-400">Erreur de chargement</div>;
  }

  return (
    <div>
      {/* Overview */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-lg font-semibold mb-2">Vue d&apos;ensemble</h2>
        <p className="text-sm text-zinc-400 mb-3">{data.overview.description}</p>
        <div className="flex flex-wrap gap-2">
          {data.overview.affects.map((affect, i) => (
            <span key={i} className="bg-zinc-800 text-zinc-300 text-xs px-2 py-1 rounded">
              {affect}
            </span>
          ))}
        </div>
      </div>

      {/* Visual Scale */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-sm font-medium mb-3">Échelle de Difficulté</h2>
        <div className="flex items-center gap-1">
          {Object.entries(data.star_tiers).map(([tier, tierData]) => (
            <div
              key={tier}
              className="flex-1 h-8 rounded flex items-center justify-center text-sm font-medium"
              style={{ backgroundColor: tierData.color + '30', color: tierData.color }}
            >
              {tierData.icon}
            </div>
          ))}
        </div>
        <div className="flex items-center gap-1 mt-1">
          {Object.entries(data.star_tiers).map(([tier, tierData]) => (
            <div key={tier} className="flex-1 text-center text-xs text-zinc-500">
              {tierData.monster_count.min}-{tierData.monster_count.max}
            </div>
          ))}
        </div>
      </div>

      {/* Star Tiers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {Object.entries(data.star_tiers).map(([tier, tierData]) => (
          <StarTierCard key={tier} tier={tier} data={tierData} />
        ))}
      </div>

      {/* Spawn Example */}
      <div className="mt-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-lg font-semibold mb-3">Exemple: Spawn 5★</h2>
        <div className="space-y-2 text-sm">
          <div className="flex items-start gap-2">
            <span className="w-6 h-6 rounded-full bg-zinc-800 flex items-center justify-center text-xs">1</span>
            <span className="text-zinc-300">5★ sélectionné pour cette zone</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="w-6 h-6 rounded-full bg-zinc-800 flex items-center justify-center text-xs">2</span>
            <span className="text-zinc-300">Roll nombre: <span className="text-amber-400">9 monstres</span></span>
          </div>
          <div className="flex items-start gap-2">
            <span className="w-6 h-6 rounded-full bg-zinc-800 flex items-center justify-center text-xs">3</span>
            <span className="text-zinc-300">Stats appliquées: <span className="text-red-400">+30% HP/ATK/DEF/MAG</span></span>
          </div>
          <div className="flex items-start gap-2">
            <span className="w-6 h-6 rounded-full bg-zinc-800 flex items-center justify-center text-xs">4</span>
            <span className="text-zinc-300">Boss: <span className="text-orange-400">1 garanti</span></span>
          </div>
          <div className="flex items-start gap-2">
            <span className="w-6 h-6 rounded-full bg-zinc-800 flex items-center justify-center text-xs">5</span>
            <span className="text-zinc-300">Élites: <span className="text-purple-400">2 garantis</span> + roll 2× (20% chacun) = <span className="text-purple-400">1 extra</span></span>
          </div>
          <div className="flex items-start gap-2">
            <span className="w-6 h-6 rounded-full bg-emerald-800 flex items-center justify-center text-xs">✓</span>
            <span className="text-emerald-400">Résultat: 1 boss, 3 élites, 5 normaux (tous +30%)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SystemsPage() {
  const [activeTab, setActiveTab] = useState('encounter-stars');

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Systèmes</h1>
        <p className="text-zinc-500 text-sm">
          Mécaniques de jeu et systèmes globaux
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex flex-wrap gap-2">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => !tab.disabled && setActiveTab(tab.id)}
            disabled={tab.disabled}
            className={`px-4 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
              activeTab === tab.id
                ? 'bg-violet-500/20 border border-violet-500 text-violet-300'
                : tab.disabled
                ? 'bg-zinc-800/30 text-zinc-600 cursor-not-allowed'
                : 'bg-zinc-800/50 border border-zinc-700 text-zinc-400 hover:text-white hover:border-zinc-600'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.name}</span>
            {tab.disabled && <span className="text-[10px] bg-zinc-700 px-1.5 py-0.5 rounded">Soon</span>}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'encounter-stars' && <EncounterStarsTab />}
    </div>
  );
}
