'use client';

import { useEffect, useState } from 'react';
import { TabsGroup } from '@/components/TabsGroup';
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

interface StatMultiplier {
  hp_multiplier: number;
  atk_multiplier: number;
  mag_multiplier: number;
  def_multiplier: number;
  note: string;
}

interface StoneType {
  id: string;
  name_hebrew: string;
  hebrew_script: string;
  name_fr: string;
  name_en: string;
  target: string;
  target_slots: string[];
  icon: string;
  color: string;
}

interface StoneRank {
  name_fr: string;
  name_en: string;
  enhancement_range: [number, number];
  success_rate: number;
  drop_source_fr: string;
  drop_source_en: string;
  craft_recipe: { input: { rank: string; quantity: number }; output: { rank: string; quantity: number } } | null;
}

interface EnhancementData {
  _meta: {
    version: string;
    last_updated: string;
    description_fr: string;
    description_en: string;
  };
  enhancement_overview: {
    description_fr: string;
    description_en: string;
    max_level: number;
    stat_bonus_per_level: number;
    stat_bonus_formula: string;
    milestones: Record<string, { total_bonus: string }>;
  };
  stone_types: Record<string, StoneType>;
  stone_ranks: Record<string, StoneRank>;
  visual_effects: {
    description_fr: string;
    description_en: string;
    effects: Record<string, { glow: string; particles: string; color?: string }>;
  };
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
  star_tiers: Record<string, StarTier & {
    elite_stats?: StatMultiplier;
    boss_stats?: StatMultiplier;
  }>;
  loot_integration: {
    rarity_boost: Record<string, number>;
  };
}

const TABS = [
  { id: 'encounter-stars', name_fr: 'Systeme d\'Etoiles', name_en: 'Star System', icon: '⭐' },
  { id: 'enhancement', name_fr: 'Amelioration', name_en: 'Enhancement', icon: '💎' },
  { id: 'koro', name_fr: 'Système Koro', name_en: 'Koro System', icon: '🃏', disabled: true },
  { id: 'crafting', name_fr: 'Crafting Substats', name_en: 'Substat Crafting', icon: '⚗️', disabled: true },
  { id: 'economy', name_fr: 'Economie', name_en: 'Economy', icon: '💰', disabled: true },
  { id: 'pvp', name_fr: 'PvP', name_en: 'PvP', icon: '⚔️', disabled: true },
  { id: 'guilds', name_fr: 'Guildes', name_en: 'Guilds', icon: '🏰', disabled: true },
];

function StarTierCard({ tier, data }: { tier: string; data: StarTier }) {
  const rarityBoost = tier === '3' ? 1 : tier === '4' ? 1 : tier === '5' ? 2 : 0;

  return (
    <Card
      className="p-4 hover:border-zinc-700 transition-colors"
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
          <Badge className="bg-yellow-500/20 text-yellow-400">
            Loot Garanti
          </Badge>
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
        <Badge className="bg-green-500/20 text-green-400">
          Loot ×{data.loot_multiplier}
        </Badge>
        <Badge className="bg-blue-500/20 text-blue-400">
          XP ×{data.xp_multiplier}
        </Badge>
        <Badge className="bg-yellow-500/20 text-yellow-400">
          Gold ×{data.gold_multiplier}
        </Badge>
        {rarityBoost > 0 && (
          <Badge className="bg-purple-500/20 text-purple-400">
            Rareté +{rarityBoost}
          </Badge>
        )}
      </div>
    </Card>
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
    return <LoadingState />;
  }

  if (!data) {
    return <div className="text-red-400">Erreur de chargement</div>;
  }

  return (
    <div>
      {/* Overview */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-lg font-semibold mb-2">Vue d&apos;ensemble / Overview</h2>
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
        <h2 className="text-sm font-medium mb-3">Echelle de Difficulte / Difficulty Scale</h2>
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
        <h2 className="text-lg font-semibold mb-3">Exemple: Spawn 5★ / Example: 5★ Spawn</h2>
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

      {/* Elite & Boss Stats */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Elite Stats */}
        <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800 border-l-4 border-l-purple-500">
          <h2 className="text-lg font-semibold mb-3 text-purple-400">Stats des Elites / Elite Stats</h2>
          <p className="text-xs text-zinc-500 mb-4">Multiplicateurs vs monstre normal / Multipliers vs normal monster (+ ★ bonus)</p>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-zinc-800/50 rounded p-3 text-center">
              <div className="text-2xl font-bold text-red-400">×3</div>
              <div className="text-xs text-zinc-500">HP</div>
            </div>
            <div className="bg-zinc-800/50 rounded p-3 text-center">
              <div className="text-2xl font-bold text-orange-400">×1.8</div>
              <div className="text-xs text-zinc-500">ATK / MAG</div>
            </div>
            <div className="bg-zinc-800/50 rounded p-3 text-center">
              <div className="text-2xl font-bold text-blue-400">×2</div>
              <div className="text-xs text-zinc-500">DEF</div>
            </div>
            <div className="bg-zinc-800/50 rounded p-3 text-center">
              <div className="text-lg font-bold text-purple-400">+1 Passif</div>
              <div className="text-xs text-zinc-500">+1 Skill</div>
            </div>
          </div>
          <div className="mt-3 text-xs text-zinc-500">
            6 archétypes: Warrior, Tank, Assassin, Caster, Healer, Summoner
          </div>
        </div>

        {/* Boss Stats */}
        <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800 border-l-4 border-l-orange-500">
          <h2 className="text-lg font-semibold mb-3 text-orange-400">Stats des Boss / Boss Stats</h2>
          <p className="text-xs text-zinc-500 mb-4">Stats FIXES / FIXED stats (no ★ bonus applied)</p>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-zinc-800/50 rounded p-3 text-center">
              <div className="text-2xl font-bold text-red-400">×8</div>
              <div className="text-xs text-zinc-500">HP</div>
            </div>
            <div className="bg-zinc-800/50 rounded p-3 text-center">
              <div className="text-2xl font-bold text-orange-400">×2.5</div>
              <div className="text-xs text-zinc-500">ATK / MAG</div>
            </div>
            <div className="bg-zinc-800/50 rounded p-3 text-center">
              <div className="text-2xl font-bold text-blue-400">×2</div>
              <div className="text-xs text-zinc-500">DEF</div>
            </div>
            <div className="bg-zinc-800/50 rounded p-3 text-center">
              <div className="text-lg font-bold text-orange-400">2-3 Passifs</div>
              <div className="text-xs text-zinc-500">2-4 Skills</div>
            </div>
          </div>
          <div className="mt-3 text-xs text-zinc-500">
            Immune CC hard, Tenacité -70%, Enrage Timer
          </div>
        </div>
      </div>

      {/* Combat Example */}
      <div className="mt-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-lg font-semibold mb-3">Exemple Combat 5★ / Combat Example (Zone T1 lvl 10)</h2>
        <p className="text-xs text-zinc-500 mb-4">Monstre normal de base / Base normal monster: 100 HP, 20 ATK, 10 DEF</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-700">
                <th className="text-left py-2 px-3 text-zinc-400">Type</th>
                <th className="text-center py-2 px-3 text-zinc-400">Calcul HP</th>
                <th className="text-center py-2 px-3 text-zinc-400">HP Final</th>
                <th className="text-center py-2 px-3 text-zinc-400">ATK Final</th>
                <th className="text-center py-2 px-3 text-zinc-400">DEF Final</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-zinc-800">
                <td className="py-2 px-3 text-zinc-300">Normal (5★)</td>
                <td className="py-2 px-3 text-center text-zinc-500">100 × 1.30</td>
                <td className="py-2 px-3 text-center text-red-400">130</td>
                <td className="py-2 px-3 text-center text-orange-400">26</td>
                <td className="py-2 px-3 text-center text-blue-400">13</td>
              </tr>
              <tr className="border-b border-zinc-800 bg-purple-500/5">
                <td className="py-2 px-3 text-purple-400">Élite (5★)</td>
                <td className="py-2 px-3 text-center text-zinc-500">100 × 3 × 1.30</td>
                <td className="py-2 px-3 text-center text-red-400">390</td>
                <td className="py-2 px-3 text-center text-orange-400">47</td>
                <td className="py-2 px-3 text-center text-blue-400">26</td>
              </tr>
              <tr className="bg-orange-500/5">
                <td className="py-2 px-3 text-orange-400">Boss</td>
                <td className="py-2 px-3 text-center text-zinc-500">100 × 8 (fixe)</td>
                <td className="py-2 px-3 text-center text-red-400">800</td>
                <td className="py-2 px-3 text-center text-orange-400">50</td>
                <td className="py-2 px-3 text-center text-blue-400">20</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="mt-3 p-2 bg-zinc-800/50 rounded text-xs text-zinc-400">
          <strong>Total groupe 5★:</strong> 5 normaux (650 HP) + 3 élites (1170 HP) + 1 boss (800 HP) = <span className="text-amber-400">2620 HP total</span>
        </div>
      </div>
    </div>
  );
}

function EnhancementTab() {
  const [data, setData] = useState<EnhancementData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/systems/enhancement')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  if (!data) {
    return <div className="text-red-400">Erreur de chargement</div>;
  }

  return (
    <div>
      {/* Overview */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-lg font-semibold mb-2">Vue d&apos;ensemble / Overview</h2>
        <p className="text-sm text-zinc-400 mb-3">{data.enhancement_overview.description_fr}</p>
        <p className="text-xs text-zinc-500">{data.enhancement_overview.description_en}</p>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-zinc-800/50 rounded p-3 text-center">
            <div className="text-2xl font-bold text-emerald-400">+{data.enhancement_overview.max_level}</div>
            <div className="text-xs text-zinc-500">Max Level</div>
          </div>
          <div className="bg-zinc-800/50 rounded p-3 text-center">
            <div className="text-2xl font-bold text-blue-400">+{data.enhancement_overview.stat_bonus_per_level}%</div>
            <div className="text-xs text-zinc-500">Par niveau / Per level</div>
          </div>
          <div className="bg-zinc-800/50 rounded p-3 text-center">
            <div className="text-2xl font-bold text-amber-400">+60%</div>
            <div className="text-xs text-zinc-500">Bonus Max (+20)</div>
          </div>
          <div className="bg-zinc-800/50 rounded p-3 text-center">
            <div className="text-lg font-bold text-zinc-300">{data.enhancement_overview.stat_bonus_formula}</div>
            <div className="text-xs text-zinc-500">Formule</div>
          </div>
        </div>
      </div>

      {/* Stone Types */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-4">Types de Pierres / Stone Types</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(data.stone_types).map(([key, stone]) => (
            <div
              key={key}
              className="bg-zinc-900 rounded-lg border border-zinc-800 p-4"
              style={{ borderLeftColor: stone.color, borderLeftWidth: '4px' }}
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-3xl">{stone.icon}</span>
                <div>
                  <h3 className="font-semibold" style={{ color: stone.color }}>{stone.name_hebrew}</h3>
                  <p className="text-xs text-zinc-500">{stone.hebrew_script}</p>
                </div>
              </div>
              <p className="text-sm text-zinc-400 mb-2">{stone.name_fr} / {stone.name_en}</p>
              <div className="mt-3 pt-3 border-t border-zinc-800">
                <div className="text-xs text-zinc-500 mb-1">Cible / Target:</div>
                <div className="flex flex-wrap gap-1">
                  {stone.target_slots.map(slot => (
                    <span key={slot} className="bg-zinc-800 text-zinc-300 text-xs px-2 py-0.5 rounded capitalize">
                      {slot.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stone Ranks & Success Rates */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-4">Rangs des Pierres / Stone Ranks</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm bg-zinc-900 rounded-lg border border-zinc-800">
            <thead>
              <tr className="border-b border-zinc-700">
                <th className="text-left py-3 px-4 text-zinc-400">Rang / Rank</th>
                <th className="text-center py-3 px-4 text-zinc-400">Niveaux / Levels</th>
                <th className="text-center py-3 px-4 text-zinc-400">Taux / Rate</th>
                <th className="text-left py-3 px-4 text-zinc-400">Source</th>
                <th className="text-left py-3 px-4 text-zinc-400">Craft</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(data.stone_ranks).map(([key, rank], index) => (
                <tr key={key} className={`border-b border-zinc-800 ${index % 2 === 0 ? 'bg-zinc-800/20' : ''}`}>
                  <td className="py-3 px-4">
                    <span className="font-medium text-zinc-200">{rank.name_fr}</span>
                    <span className="text-zinc-500 text-xs ml-2">/ {rank.name_en}</span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="font-mono text-emerald-400">+{rank.enhancement_range[0]} → +{rank.enhancement_range[1]}</span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`font-mono ${rank.success_rate === 100 ? 'text-green-400' : rank.success_rate >= 80 ? 'text-yellow-400' : 'text-orange-400'}`}>
                      {rank.success_rate}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-zinc-400 text-xs">{rank.drop_source_fr}</td>
                  <td className="py-3 px-4 text-zinc-400 text-xs">
                    {rank.craft_recipe ? (
                      <span className="text-violet-400">
                        {rank.craft_recipe.input.quantity}× {data.stone_ranks[rank.craft_recipe.input.rank]?.name_fr || rank.craft_recipe.input.rank}
                      </span>
                    ) : (
                      <span className="text-zinc-600">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Rules */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 border-l-4 border-l-green-500 p-4">
          <h3 className="font-semibold text-green-400 mb-2">Succes / Success</h3>
          <p className="text-sm text-zinc-400">L&apos;equipement gagne +1 niveau</p>
          <p className="text-xs text-zinc-500 mt-1">Equipment gains +1 level</p>
          <p className="text-sm text-zinc-400 mt-2">La pierre est consommee</p>
          <p className="text-xs text-zinc-500">Stone is consumed</p>
        </div>
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 border-l-4 border-l-red-500 p-4">
          <h3 className="font-semibold text-red-400 mb-2">Echec / Failure</h3>
          <p className="text-sm text-zinc-400">La pierre est detruite</p>
          <p className="text-xs text-zinc-500 mt-1">Stone is destroyed</p>
          <p className="text-sm text-emerald-400 mt-2">L&apos;equipement reste intact!</p>
          <p className="text-xs text-zinc-500">Equipment remains intact!</p>
        </div>
      </div>

      {/* Visual Effects */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-lg font-semibold mb-4">Effets Visuels / Visual Effects</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Object.entries(data.visual_effects.effects).map(([range, effect]) => (
            <div
              key={range}
              className="bg-zinc-800/50 rounded p-3 text-center"
              style={{ borderColor: effect.color || '#71717a', borderWidth: '1px' }}
            >
              <div className="text-sm font-mono text-zinc-300">{range.replace(/_/g, ' ')}</div>
              <div className="text-xs text-zinc-500 mt-1">{effect.glow}</div>
              {effect.particles !== 'none' && (
                <div className="text-xs mt-1" style={{ color: effect.color }}>
                  {effect.particles}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Example Calculation */}
      <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-lg font-semibold mb-3">Exemple / Example</h2>
        <p className="text-sm text-zinc-400 mb-4">Epee avec 100 ATK de base amelioree a +15:</p>
        <div className="flex items-center gap-4 flex-wrap">
          <div className="bg-zinc-800/50 rounded p-3 text-center">
            <div className="text-sm text-zinc-500">Base ATK</div>
            <div className="text-xl font-mono text-zinc-300">100</div>
          </div>
          <span className="text-zinc-500">×</span>
          <div className="bg-zinc-800/50 rounded p-3 text-center">
            <div className="text-sm text-zinc-500">Bonus +15</div>
            <div className="text-xl font-mono text-blue-400">1.45</div>
          </div>
          <span className="text-zinc-500">=</span>
          <div className="bg-emerald-500/20 border border-emerald-500/50 rounded p-3 text-center">
            <div className="text-sm text-emerald-400">ATK Final</div>
            <div className="text-xl font-mono text-emerald-300">145</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SystemsPage() {
  const [activeSystem, setActiveSystem] = useState('encounter-stars');
  const enabledTabs = TABS.filter(tab => !tab.disabled);

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Secondary Sidebar */}
      <aside className="w-64 border-r border-zinc-800 overflow-y-auto bg-zinc-900/50">
        <div className="p-4 border-b border-zinc-800">
          <h2 className="text-lg font-semibold">Systèmes</h2>
          <p className="text-xs text-zinc-500">Game Systems</p>
        </div>
        <nav className="p-2">
          {enabledTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSystem(tab.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-left ${
                activeSystem === tab.id
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                  : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
              }`}
            >
              <span className="text-xl">{tab.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{tab.name_fr}</div>
                <div className="text-xs text-zinc-500 truncate">{tab.name_en}</div>
              </div>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {activeSystem === 'encounter-stars' && <EncounterStarsTab />}
          {activeSystem === 'enhancement' && <EnhancementTab />}
        </div>
      </main>
    </div>
  );
}
