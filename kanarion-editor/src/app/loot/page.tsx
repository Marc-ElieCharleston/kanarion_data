'use client';

import { useEffect, useState } from 'react';

interface RarityTier {
  name: string;
  name_en: string;
  color: string;
  base_weight: number;
}

interface MultiplierValue {
  gold: number;
  xp: number;
  drop_chance: number;
  rarity_boost?: number;
}

interface GroupValue {
  mult: number;
  bonus: string;
}

interface LootTablesData {
  _meta: {
    version: string;
    last_updated: string;
    description: string;
    formula_overview: string;
  };
  rarity_system: {
    description: string;
    tiers: Record<string, RarityTier>;
  };
  multipliers: {
    monster_state: Record<string, MultiplierValue>;
    dungeon_difficulty: Record<string, MultiplierValue>;
    group_size: {
      description: string;
      max_bonus_percent: number;
      values: Record<string, GroupValue>;
    };
    level_difference: {
      no_penalty_range: number;
      penalty_per_level: number;
      max_penalty: number;
    };
  };
  events: {
    event_types: Record<string, {
      name_fr: string;
      name_en: string;
      bonuses: { gold: number; xp: number; drop_chance: number };
    }>;
  };
}

function RarityBadge({ tier, data }: { tier: string; data: RarityTier }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-zinc-800/50 rounded-lg">
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center text-lg font-bold"
        style={{ backgroundColor: data.color + '30', color: data.color }}
      >
        {tier.replace('_star', '')}
      </div>
      <div className="flex-1">
        <div className="font-medium" style={{ color: data.color }}>{data.name}</div>
        <div className="text-xs text-zinc-500">{data.name_en}</div>
      </div>
      <div className="text-right">
        <div className="text-sm text-zinc-400">Weight</div>
        <div className="font-mono text-zinc-300">{data.base_weight}</div>
      </div>
    </div>
  );
}

function MultiplierTable({ title, data }: { title: string; data: Record<string, MultiplierValue> }) {
  return (
    <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
      <h3 className="font-semibold mb-3">{title}</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-zinc-500 border-b border-zinc-800">
              <th className="text-left py-2 px-2">Type</th>
              <th className="text-center py-2 px-2">Gold</th>
              <th className="text-center py-2 px-2">XP</th>
              <th className="text-center py-2 px-2">Drop</th>
              <th className="text-center py-2 px-2">Rarity+</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(data).map(([key, val]) => (
              <tr key={key} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                <td className="py-2 px-2 capitalize">{key.replace(/_/g, ' ')}</td>
                <td className="text-center py-2 px-2 font-mono text-yellow-400">×{val.gold}</td>
                <td className="text-center py-2 px-2 font-mono text-blue-400">×{val.xp}</td>
                <td className="text-center py-2 px-2 font-mono text-green-400">×{val.drop_chance}</td>
                <td className="text-center py-2 px-2 font-mono text-purple-400">+{val.rarity_boost || 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Calculator({ data }: { data: LootTablesData }) {
  const [baseChance, setBaseChance] = useState(0.05);
  const [monsterState, setMonsterState] = useState('normal');
  const [dungeonDiff, setDungeonDiff] = useState('open_world');
  const [groupSize, setGroupSize] = useState('1');
  const [luck, setLuck] = useState(0);
  const [event, setEvent] = useState('none');

  const stateMult = data.multipliers.monster_state[monsterState]?.drop_chance || 1;
  const dungeonMult = data.multipliers.dungeon_difficulty[dungeonDiff]?.drop_chance || 1;
  const groupMult = data.multipliers.group_size.values[groupSize]?.mult || 1;
  const luckMult = 1 + (luck * 0.002);
  const eventMult = event !== 'none' ? data.events.event_types[event]?.bonuses.drop_chance || 1 : 1;

  const finalChance = Math.min(0.95, baseChance * stateMult * dungeonMult * groupMult * luckMult * eventMult);

  return (
    <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
      <h3 className="font-semibold mb-4">Calculateur de Drop</h3>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="text-xs text-zinc-500 block mb-1">Base Chance</label>
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={baseChance}
            onChange={(e) => setBaseChance(parseFloat(e.target.value) || 0)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
          />
        </div>

        <div>
          <label className="text-xs text-zinc-500 block mb-1">Monster State</label>
          <select
            value={monsterState}
            onChange={(e) => setMonsterState(e.target.value)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
          >
            {Object.keys(data.multipliers.monster_state).map(key => (
              <option key={key} value={key}>{key.replace(/_/g, ' ')}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs text-zinc-500 block mb-1">Dungeon</label>
          <select
            value={dungeonDiff}
            onChange={(e) => setDungeonDiff(e.target.value)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
          >
            {Object.keys(data.multipliers.dungeon_difficulty).map(key => (
              <option key={key} value={key}>{key.replace(/_/g, ' ')}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs text-zinc-500 block mb-1">Group Size</label>
          <select
            value={groupSize}
            onChange={(e) => setGroupSize(e.target.value)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
          >
            {Object.keys(data.multipliers.group_size.values).map(key => (
              <option key={key} value={key}>{key} joueur(s)</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs text-zinc-500 block mb-1">Luck Stat</label>
          <input
            type="number"
            min="0"
            max="500"
            value={luck}
            onChange={(e) => setLuck(parseInt(e.target.value) || 0)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
          />
        </div>

        <div>
          <label className="text-xs text-zinc-500 block mb-1">Event</label>
          <select
            value={event}
            onChange={(e) => setEvent(e.target.value)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
          >
            <option value="none">Aucun</option>
            {Object.entries(data.events.event_types).map(([key, val]) => (
              <option key={key} value={key}>{val.name_fr}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="bg-zinc-800 rounded-lg p-4">
        <div className="text-xs text-zinc-500 mb-2">Formule:</div>
        <div className="font-mono text-xs text-zinc-400 mb-3 overflow-x-auto">
          {baseChance} × {stateMult} × {dungeonMult} × {groupMult.toFixed(2)} × {luckMult.toFixed(2)} × {eventMult} =
        </div>
        <div className="text-center">
          <span className="text-3xl font-bold text-green-400">{(finalChance * 100).toFixed(1)}%</span>
          <span className="text-zinc-500 ml-2">chance de drop</span>
        </div>
      </div>
    </div>
  );
}

function LootFlowDiagram() {
  return (
    <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
      <h3 className="font-semibold mb-4">Flow du Loot (Équipement)</h3>
      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center text-xs">1</span>
          <span>Tuer monstre → Roll drop (oui/non selon chance finale)</span>
        </div>
        <div className="ml-4 border-l-2 border-zinc-700 pl-4 py-1">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-orange-500/20 text-orange-400 flex items-center justify-center text-xs">2</span>
            <span>Roll catégorie (équipement, matériau, consommable)</span>
          </div>
        </div>
        <div className="ml-8 border-l-2 border-zinc-700 pl-4 py-1">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-yellow-500/20 text-yellow-400 flex items-center justify-center text-xs">3</span>
            <span>Roll rareté (1-5★ selon weights + rarity_boost)</span>
          </div>
        </div>
        <div className="ml-12 border-l-2 border-zinc-700 pl-4 py-1">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center text-xs">4</span>
            <span>Roll quel set (weighted par zone/monstre)</span>
          </div>
        </div>
        <div className="ml-16 border-l-2 border-zinc-700 pl-4 py-1">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs">5</span>
            <span>Roll quelle pièce du set</span>
          </div>
        </div>
        <div className="ml-20 border-l-2 border-zinc-700 pl-4 py-1">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs">6</span>
            <span>Roll main stat + substats + valeurs</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LootPage() {
  const [data, setData] = useState<LootTablesData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/loot')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse text-zinc-500">Chargement des tables de loot...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8">
        <div className="text-red-400">Erreur de chargement</div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Tables de Loot</h1>
        <p className="text-zinc-500 text-sm">{data._meta.description}</p>
        <p className="text-zinc-600 text-xs mt-1">
          v{data._meta.version} • {data._meta.last_updated}
        </p>
      </div>

      {/* Formula Overview */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-sm font-medium mb-2">Formule Globale</h2>
        <code className="text-xs text-emerald-400 bg-zinc-800 px-2 py-1 rounded">
          {data._meta.formula_overview}
        </code>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Calculator */}
        <Calculator data={data} />

        {/* Loot Flow */}
        <LootFlowDiagram />

        {/* Rarity System */}
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
          <h3 className="font-semibold mb-3">Système de Rareté</h3>
          <div className="space-y-2">
            {Object.entries(data.rarity_system.tiers).map(([tier, tierData]) => (
              <RarityBadge key={tier} tier={tier} data={tierData} />
            ))}
          </div>
        </div>

        {/* Group Size */}
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
          <h3 className="font-semibold mb-3">Bonus de Groupe</h3>
          <p className="text-xs text-zinc-500 mb-3">Max: +{data.multipliers.group_size.max_bonus_percent}%</p>
          <div className="grid grid-cols-5 gap-2">
            {Object.entries(data.multipliers.group_size.values).map(([size, val]) => (
              <div key={size} className="bg-zinc-800/50 rounded p-2 text-center">
                <div className="text-lg font-bold text-zinc-300">{size}</div>
                <div className="text-xs text-green-400">{val.bonus}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Monster State Multipliers */}
        <MultiplierTable
          title="Multiplicateurs - État du Monstre"
          data={data.multipliers.monster_state}
        />

        {/* Dungeon Difficulty Multipliers */}
        <MultiplierTable
          title="Multiplicateurs - Difficulté Donjon"
          data={data.multipliers.dungeon_difficulty}
        />

        {/* Events */}
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4 xl:col-span-2">
          <h3 className="font-semibold mb-3">Événements Spéciaux</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(data.events.event_types).map(([key, event]) => (
              <div key={key} className="bg-zinc-800/50 rounded-lg p-3">
                <div className="font-medium text-amber-400">{event.name_fr}</div>
                <div className="text-xs text-zinc-500 mb-2">{event.name_en}</div>
                <div className="flex gap-2 text-xs">
                  <span className="bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded">
                    Gold ×{event.bonuses.gold}
                  </span>
                  <span className="bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
                    XP ×{event.bonuses.xp}
                  </span>
                  <span className="bg-green-500/20 text-green-400 px-2 py-0.5 rounded">
                    Drop ×{event.bonuses.drop_chance}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
