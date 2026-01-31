'use client';

import { useEffect, useState } from 'react';
import { TabsGroup } from '@/components/TabsGroup';
import { LoadingState } from '@/components/LoadingState';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface RarityTier {
  name_fr: string;
  name_en: string;
  color: string;
  substat_count: number;
  substat_upgrade_chance: number;
}

interface StatPool {
  stat: string;
  weight: number;
}

interface SoulEssenceType {
  name_fr: string;
  name_en: string;
  main_stat: string;
  description_fr: string;
  color: string;
  stat_split?: { atk: number; mag: number };
}

interface EquipmentStatsData {
  _meta: { version: string; last_updated: string };
  rarity_tiers: Record<string, RarityTier>;
  equipment_categories: {
    armor: {
      description: string;
      slots: string[];
      main_stat_by_armor_type: Record<string, { options: string[]; weights: number[] }>;
      substat_pool: StatPool[];
    };
    accessory: {
      description: string;
      slots: string[];
      main_stat_options: Record<string, { options: string[]; weights: number[] }>;
      substat_pool: StatPool[];
    };
    soul_essence: {
      description: string;
      lore: { fr: string; en: string };
      main_stat_types: Record<string, SoulEssenceType>;
      substat_pool: StatPool[];
    };
  };
  stat_ranges_by_rarity: {
    main_stats: Record<string, Record<string, number[]>>;
  };
  examples: Record<string, object>;
}

interface ScalingTier {
  name_fr: string;
  name_en: string;
  level_range: [number, number];
  stat_multiplier: number;
}

interface ScalingRarity {
  name_fr: string;
  name_en: string;
  color: string;
  substat_count: { min: number; max: number };
  roll_range_percent: { min: number; max: number };
  description_fr: string;
  description_en: string;
}

interface EquipmentScalingData {
  _meta: { version: string; last_updated: string };
  tier_system: {
    description_fr: string;
    description_en: string;
    tiers: Record<string, ScalingTier>;
  };
  rarity_system: {
    description_fr: string;
    description_en: string;
    rarities: Record<string, ScalingRarity>;
  };
  base_stat_values: {
    main_stats: Record<string, { base: number; per_level: number }>;
    substats: Record<string, number>;
  };
}

const STAT_LABELS: Record<string, { fr: string; en: string }> = {
  hp_max: { fr: 'HP Max', en: 'Max HP' },
  mp_max: { fr: 'MP Max', en: 'Max MP' },
  atk: { fr: 'ATK', en: 'ATK' },
  mag: { fr: 'MAG', en: 'MAG' },
  armor: { fr: 'Armure', en: 'Armor' },
  magic_resist: { fr: 'Res. Magique', en: 'Magic Resist' },
  hp_regen: { fr: 'Regen HP', en: 'HP Regen' },
  mp_regen: { fr: 'Regen MP', en: 'MP Regen' },
  def_percent: { fr: 'DEF %', en: 'DEF %' },
  damage_reduction: { fr: 'Reduction Degats', en: 'Damage Reduction' },
  atk_percent: { fr: 'ATK %', en: 'ATK %' },
  mag_percent: { fr: 'MAG %', en: 'MAG %' },
  crit: { fr: 'Critique', en: 'Critical' },
  crit_dmg: { fr: 'Degats Crit', en: 'Crit Damage' },
  attack_speed: { fr: 'Vitesse ATK', en: 'Attack Speed' },
  cooldown_reduction: { fr: 'Reduction CD', en: 'Cooldown Reduction' },
  effect_chance: { fr: 'Chance Effet', en: 'Effect Chance' },
  buff_duration: { fr: 'Duree Buffs', en: 'Buff Duration' },
  armor_pen: { fr: 'Pen. Armure', en: 'Armor Pen' },
  magic_pen: { fr: 'Pen. Magique', en: 'Magic Pen' },
  damage_percent: { fr: 'Degats %', en: 'Damage %' },
  lifesteal: { fr: 'Vol de Vie', en: 'Lifesteal' },
};

const SLOT_LABELS: Record<string, { fr: string; en: string }> = {
  helmet: { fr: 'Casque', en: 'Helmet' },
  armor: { fr: 'Armure', en: 'Armor' },
  gloves: { fr: 'Gants', en: 'Gloves' },
  boots: { fr: 'Bottes', en: 'Boots' },
  belt: { fr: 'Ceinture', en: 'Belt' },
  cape: { fr: 'Cape', en: 'Cape' },
  amulet: { fr: 'Amulette', en: 'Amulet' },
  ring_1: { fr: 'Anneau 1', en: 'Ring 1' },
  ring_2: { fr: 'Anneau 2', en: 'Ring 2' },
  weapon: { fr: 'Arme', en: 'Weapon' },
};

const ARMOR_TYPE_CONFIG: Record<string, { icon: string; color: string }> = {
  cloth: { icon: '🧵', color: '#9b59b6' },
  leather: { icon: '🦊', color: '#8b4513' },
  plate: { icon: '🛡️', color: '#7f8c8d' },
  mixed: { icon: '⚖️', color: '#f39c12' },
};

function RarityBadge({ rarity, data }: { rarity: string; data: RarityTier }) {
  return (
    <div
      className="flex items-center gap-2 px-3 py-2 rounded-lg border"
      style={{ borderColor: data.color, backgroundColor: data.color + '15' }}
    >
      <span style={{ color: data.color }} className="font-bold">
        {rarity.replace('_star', '★')}
      </span>
      <span className="text-zinc-300">{data.name_fr}</span>
      <span className="text-xs text-zinc-500">({data.substat_count} substats)</span>
    </div>
  );
}

function StatPoolDisplay({ pool, titleFr, titleEn }: { pool: StatPool[]; titleFr: string; titleEn: string }) {
  const totalWeight = pool.reduce((sum, s) => sum + s.weight, 0);

  return (
    <div className="bg-zinc-800/50 rounded-lg p-4">
      <h4 className="text-sm font-medium mb-1 text-zinc-300">{titleFr}</h4>
      <h5 className="text-xs text-zinc-500 mb-3">{titleEn}</h5>
      <div className="flex flex-wrap gap-2">
        {pool.map((s) => {
          const percent = Math.round((s.weight / totalWeight) * 100);
          const label = STAT_LABELS[s.stat];
          return (
            <span
              key={s.stat}
              className="bg-zinc-700/50 text-zinc-300 text-xs px-2 py-1 rounded"
              title={`${percent}% chance`}
            >
              {label ? `${label.fr} / ${label.en}` : s.stat}
              <span className="text-zinc-500 ml-1">({percent}%)</span>
            </span>
          );
        })}
      </div>
    </div>
  );
}

function SoulEssenceCard({ type, data }: { type: string; data: SoulEssenceType }) {
  return (
    <div
      className="bg-zinc-900 rounded-lg border border-zinc-800 p-4"
      style={{ borderLeftColor: data.color, borderLeftWidth: '4px' }}
    >
      <div className="flex items-center gap-3 mb-2">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-xl"
          style={{ backgroundColor: data.color + '30' }}
        >
          {type === 'essence_force' ? '⚔️' : type === 'essence_arcane' ? '✨' : '⚖️'}
        </div>
        <div>
          <h4 className="font-semibold" style={{ color: data.color }}>{data.name_fr}</h4>
          <p className="text-xs text-zinc-500">{data.name_en}</p>
        </div>
      </div>
      <p className="text-sm text-zinc-400 mb-2">{data.description_fr}</p>
      <div className="bg-zinc-800/50 rounded px-3 py-2">
        <span className="text-xs text-zinc-500">Main Stat: </span>
        {data.stat_split ? (
          <span className="text-amber-400">
            {data.stat_split.atk * 100}% ATK + {data.stat_split.mag * 100}% MAG
          </span>
        ) : (
          <span style={{ color: data.color }}>
            {data.main_stat === 'atk' ? 'ATK' : 'MAG'}
          </span>
        )}
      </div>
    </div>
  );
}

export default function EquipmentStatsPage() {
  const [data, setData] = useState<EquipmentStatsData | null>(null);
  const [scalingData, setScalingData] = useState<EquipmentScalingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'scaling' | 'armor' | 'accessory' | 'soul'>('scaling');

  useEffect(() => {
    Promise.all([
      fetch('/api/equipment-stats').then(res => res.json()),
      fetch('/api/equipment-scaling').then(res => res.json())
    ])
      .then(([equipData, scaleData]) => {
        setData(equipData);
        setScalingData(scaleData);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  if (!data) {
    return (
      <div className="p-8">
        <div className="text-red-400">Erreur de chargement</div>
      </div>
    );
  }

  const { armor, accessory, soul_essence } = data.equipment_categories;

  return (
    <div className="p-4 md:p-6 lg:p-8">
      {/* Header */}
      <div className="mb-4 md:mb-6">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">Systeme de Stats Equipement / Equipment Stats System</h1>
        <p className="text-zinc-500 text-sm">
          Tiers, rarete, main stats, substats et Essences d&apos;Ame / Tiers, rarity, main stats, substats and Soul Essences
        </p>
      </div>

      {/* Rarity Tiers */}
      <Card className="mb-6 p-4">
        <h2 className="text-lg font-semibold mb-3">Rarete et Substats</h2>
        <div className="flex flex-wrap gap-3">
          {Object.entries(data.rarity_tiers).map(([rarity, tierData]) => (
            <RarityBadge key={rarity} rarity={rarity} data={tierData} />
          ))}
        </div>
      </Card>

      {/* Tabs */}
      <div className="mb-4 md:mb-6 flex flex-wrap gap-2">
        <button
          onClick={() => setActiveTab('scaling')}
          className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm transition-colors flex items-center gap-1 sm:gap-2 ${
            activeTab === 'scaling'
              ? 'bg-emerald-500/20 border border-emerald-500 text-emerald-300'
              : 'bg-zinc-800/50 border border-zinc-700 text-zinc-400 hover:text-white'
          }`}
        >
          <span>📈</span>
          <span className="hidden sm:inline">Scaling / Tiers</span>
          <span className="sm:hidden">Scaling</span>
        </button>
        <button
          onClick={() => setActiveTab('armor')}
          className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm transition-colors flex items-center gap-1 sm:gap-2 ${
            activeTab === 'armor'
              ? 'bg-blue-500/20 border border-blue-500 text-blue-300'
              : 'bg-zinc-800/50 border border-zinc-700 text-zinc-400 hover:text-white'
          }`}
        >
          <span>🛡️</span>
          <span className="hidden sm:inline">Armure (6 slots)</span>
          <span className="sm:hidden">Armure</span>
        </button>
        <button
          onClick={() => setActiveTab('accessory')}
          className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm transition-colors flex items-center gap-1 sm:gap-2 ${
            activeTab === 'accessory'
              ? 'bg-purple-500/20 border border-purple-500 text-purple-300'
              : 'bg-zinc-800/50 border border-zinc-700 text-zinc-400 hover:text-white'
          }`}
        >
          <span>💍</span>
          <span className="hidden sm:inline">Accessoires (3 slots)</span>
          <span className="sm:hidden">Accessoires</span>
        </button>
        <button
          onClick={() => setActiveTab('soul')}
          className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm transition-colors flex items-center gap-1 sm:gap-2 ${
            activeTab === 'soul'
              ? 'bg-amber-500/20 border border-amber-500 text-amber-300'
              : 'bg-zinc-800/50 border border-zinc-700 text-zinc-400 hover:text-white'
          }`}
        >
          <span>✨</span>
          <span className="hidden sm:inline">Essence d&apos;Ame</span>
          <span className="sm:hidden">Essence</span>
        </button>
      </div>

      {/* Scaling Tab */}
      {activeTab === 'scaling' && scalingData && (
        <div className="space-y-6">
          {/* Tier System */}
          <Card className="p-4">
            <h3 className="text-lg font-semibold mb-2">Systeme de Tiers / Tier System</h3>
            <p className="text-sm text-zinc-400 mb-4">{scalingData.tier_system.description_fr}</p>
            <p className="text-xs text-zinc-500 mb-4">{scalingData.tier_system.description_en}</p>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-zinc-700">
                    <th className="text-left py-3 px-4 text-zinc-400">Tier</th>
                    <th className="text-center py-3 px-4 text-zinc-400">Niveaux / Levels</th>
                    <th className="text-center py-3 px-4 text-zinc-400">Multiplicateur / Multiplier</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(scalingData.tier_system.tiers).map(([key, tier], index) => (
                    <tr key={key} className={`border-b border-zinc-800 ${index % 2 === 0 ? 'bg-zinc-800/20' : ''}`}>
                      <td className="py-3 px-4">
                        <span className="font-bold text-emerald-400">{key}</span>
                        <span className="text-zinc-500 text-xs ml-2">{tier.name_fr}</span>
                      </td>
                      <td className="py-3 px-4 text-center font-mono text-zinc-300">
                        {tier.level_range[0]} - {tier.level_range[1]}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className="font-mono text-amber-400">×{tier.stat_multiplier}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Rarity Roll Ranges */}
          <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-semibold mb-2">Rarete et Fourchettes de Roll / Rarity & Roll Ranges</h3>
            <p className="text-sm text-zinc-400 mb-4">{scalingData.rarity_system.description_fr}</p>
            <p className="text-xs text-zinc-500 mb-4">{scalingData.rarity_system.description_en}</p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(scalingData.rarity_system.rarities).map(([key, rarity]) => (
                <div
                  key={key}
                  className="bg-zinc-800/50 rounded-lg p-4 border-l-4"
                  style={{ borderLeftColor: rarity.color }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold" style={{ color: rarity.color }}>
                      {key.replace('_star', '★')} {rarity.name_fr}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-500 mb-3">{rarity.name_en}</p>

                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="bg-zinc-700/30 rounded p-2">
                      <div className="text-xs text-zinc-500">Substats</div>
                      <div className="font-mono text-zinc-200">
                        {rarity.substat_count.min === rarity.substat_count.max
                          ? rarity.substat_count.min
                          : `${rarity.substat_count.min}-${rarity.substat_count.max}`}
                      </div>
                    </div>
                    <div className="bg-zinc-700/30 rounded p-2">
                      <div className="text-xs text-zinc-500">Roll Range</div>
                      <div className="font-mono text-blue-400">
                        {rarity.roll_range_percent.min}-{rarity.roll_range_percent.max}%
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Roll Formula */}
          <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-semibold mb-3">Formule de Calcul / Roll Formula</h3>
            <div className="bg-zinc-800/50 rounded-lg p-4">
              <code className="text-emerald-400 text-sm">
                valeur_finale = base_value × tier_multiplier × random(roll_min%, roll_max%)
              </code>
            </div>

            <div className="mt-4">
              <h4 className="text-sm font-medium text-zinc-400 mb-2">Exemple / Example:</h4>
              <div className="flex items-center gap-3 flex-wrap text-sm">
                <div className="bg-zinc-800/50 rounded p-2 text-center">
                  <div className="text-xs text-zinc-500">Crit (base)</div>
                  <div className="font-mono text-zinc-300">3%</div>
                </div>
                <span className="text-zinc-500">×</span>
                <div className="bg-zinc-800/50 rounded p-2 text-center">
                  <div className="text-xs text-zinc-500">T3 mult</div>
                  <div className="font-mono text-amber-400">2.0</div>
                </div>
                <span className="text-zinc-500">×</span>
                <div className="bg-zinc-800/50 rounded p-2 text-center">
                  <div className="text-xs text-zinc-500">4★ roll (70-95%)</div>
                  <div className="font-mono text-purple-400">85%</div>
                </div>
                <span className="text-zinc-500">=</span>
                <div className="bg-emerald-500/20 border border-emerald-500/50 rounded p-2 text-center">
                  <div className="text-xs text-emerald-400">Final</div>
                  <div className="font-mono text-emerald-300">5.1% Crit</div>
                </div>
              </div>
            </div>
          </div>

          {/* Base Values Reference */}
          <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-semibold mb-3">Valeurs de Base T1 / Base T1 Values</h3>
            <p className="text-xs text-zinc-500 mb-4">Valeurs multipliees par le multiplicateur du Tier</p>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
              {Object.entries(scalingData.base_stat_values.substats).map(([stat, value]) => {
                const label = STAT_LABELS[stat];
                return (
                  <div key={stat} className="bg-zinc-800/50 rounded p-2 text-center">
                    <div className="text-xs text-zinc-500 truncate">
                      {label ? label.fr : stat}
                    </div>
                    <div className="font-mono text-zinc-300">{value}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Armor Tab */}
      {activeTab === 'armor' && (
        <div className="space-y-6">
          <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-semibold mb-2">Pieces d&apos;Armure</h3>
            <p className="text-sm text-zinc-400 mb-4">{armor.description}</p>

            {/* Slots */}
            <div className="flex flex-wrap gap-2 mb-4">
              {armor.slots.map((slot) => {
                const label = SLOT_LABELS[slot];
                return (
                  <span key={slot} className="bg-zinc-800 text-zinc-300 text-sm px-3 py-1 rounded">
                    {label ? `${label.fr} / ${label.en}` : slot}
                  </span>
                );
              })}
            </div>

            {/* Main Stats by Armor Type */}
            <h4 className="text-sm font-medium mb-3 text-zinc-400">Main Stat selon le type d&apos;armure</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
              {Object.entries(armor.main_stat_by_armor_type).map(([type, config]) => (
                <div
                  key={type}
                  className="bg-zinc-800/50 rounded-lg p-3 border-l-4"
                  style={{ borderLeftColor: ARMOR_TYPE_CONFIG[type]?.color || '#666' }}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span>{ARMOR_TYPE_CONFIG[type]?.icon}</span>
                    <span className="font-medium capitalize">{type}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {config.options.map((stat, i) => (
                      <span
                        key={stat}
                        className="text-xs bg-zinc-700/50 px-2 py-0.5 rounded text-zinc-300"
                      >
                        {STAT_LABELS[stat]?.fr || stat}
                        <span className="text-zinc-500 ml-1">({config.weights[i]}%)</span>
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <StatPoolDisplay pool={armor.substat_pool} titleFr="Pool de Substats (Defensif)" titleEn="Substat Pool (Defensive)" />
          </div>
        </div>
      )}

      {/* Accessory Tab */}
      {activeTab === 'accessory' && (
        <div className="space-y-6">
          <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-semibold mb-2">Accessoires</h3>
            <p className="text-sm text-zinc-400 mb-4">{accessory.description}</p>

            {/* Main Stats by Slot */}
            <h4 className="text-sm font-medium mb-3 text-zinc-400">Main Stat selon le slot</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
              {Object.entries(accessory.main_stat_options).map(([slot, config]) => (
                <div
                  key={slot}
                  className="bg-zinc-800/50 rounded-lg p-3 border-l-4 border-l-purple-500"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span>{slot === 'amulet' ? '📿' : '💍'}</span>
                    <span className="font-medium">{slot === 'amulet' ? 'Amulette' : 'Anneau'}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {config.options.map((stat, i) => (
                      <span
                        key={stat}
                        className="text-xs bg-zinc-700/50 px-2 py-0.5 rounded text-zinc-300"
                      >
                        {STAT_LABELS[stat]?.fr || stat}
                        <span className="text-zinc-500 ml-1">({config.weights[i]}%)</span>
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <StatPoolDisplay pool={accessory.substat_pool} titleFr="Pool de Substats (Offensif/Utilitaire)" titleEn="Substat Pool (Offensive/Utility)" />
          </div>
        </div>
      )}

      {/* Soul Essence Tab */}
      {activeTab === 'soul' && (
        <div className="space-y-6">
          {/* Lore */}
          <div className="p-4 bg-gradient-to-r from-amber-500/10 to-purple-500/10 rounded-lg border border-amber-500/30">
            <h3 className="text-lg font-semibold mb-2 text-amber-400">Essence d&apos;Ame</h3>
            <p className="text-sm text-zinc-300 italic">&quot;{soul_essence.lore.fr}&quot;</p>
          </div>

          {/* Essence Types */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(soul_essence.main_stat_types).map(([type, typeData]) => (
              <SoulEssenceCard key={type} type={type} data={typeData} />
            ))}
          </div>

          {/* Substat Pool */}
          <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
            <StatPoolDisplay pool={soul_essence.substat_pool} titleFr="Pool de Substats (Pur Offensif)" titleEn="Substat Pool (Pure Offensive)" />
          </div>

          {/* Build Examples */}
          <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
            <h4 className="text-sm font-medium mb-3 text-zinc-400">Exemples de Builds</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="bg-zinc-800/50 rounded p-3">
                <div className="text-red-400 font-medium mb-1">Archer MAG</div>
                <p className="text-xs text-zinc-500">Essence Arcanique pour booster les sorts a scaling magique</p>
              </div>
              <div className="bg-zinc-800/50 rounded p-3">
                <div className="text-purple-400 font-medium mb-1">Spellblade</div>
                <p className="text-xs text-zinc-500">Warrior + Essence Equilibre pour hybrid melee/magic</p>
              </div>
              <div className="bg-zinc-800/50 rounded p-3">
                <div className="text-amber-400 font-medium mb-1">Battlemage</div>
                <p className="text-xs text-zinc-500">Mage + Essence Force pour auto-attacks renforces</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="mt-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h3 className="text-lg font-semibold mb-3">Resume</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-blue-500/10 rounded p-3 border border-blue-500/30">
            <div className="text-blue-400 font-medium mb-1">Armure (6 slots)</div>
            <p className="text-zinc-400">Focus defensif: HP, MP, Armor, MR, Regen</p>
          </div>
          <div className="bg-purple-500/10 rounded p-3 border border-purple-500/30">
            <div className="text-purple-400 font-medium mb-1">Accessoires (3 slots)</div>
            <p className="text-zinc-400">Focus offensif/utilitaire: ATK%, MAG%, Crit, CDR</p>
          </div>
          <div className="bg-amber-500/10 rounded p-3 border border-amber-500/30">
            <div className="text-amber-400 font-medium mb-1">Essence d&apos;Ame (1 slot)</div>
            <p className="text-zinc-400">Pur offensif: ATK/MAG, Crit, Pen, Speed</p>
          </div>
        </div>
      </div>
    </div>
  );
}
