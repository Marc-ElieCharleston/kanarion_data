'use client';

import { useEffect, useState } from 'react';

interface SetBonus {
  [key: string]: number;
}

interface PanoplieSet {
  id: string;
  name_fr: string;
  name_en: string;
  identity: string;
  description_fr: string;
  level_range: [number, number];
  pieces_count: number;
  pieces: Record<string, string>;
  bonuses: Record<string, SetBonus>;
  total_at_max: SetBonus;
}

interface PanopliesData {
  _meta: {
    version: string;
    total_sets: number;
    equipment_slots: string[];
  };
  sets: Record<string, PanoplieSet>;
  _summary: {
    by_pieces: Record<string, string[]>;
    by_identity: Record<string, string[]>;
  };
}

const IDENTITY_CONFIG: Record<string, { name: string; color: string; icon: string }> = {
  sustain_regen: { name: 'Sustain / Regen', color: 'text-green-400 border-green-500/30', icon: '💚' },
  tank_def: { name: 'Tank / DEF', color: 'text-sky-400 border-sky-500/30', icon: '🛡️' },
  balanced_utility: { name: 'Balanced / Utility', color: 'text-zinc-400 border-zinc-500/30', icon: '⚖️' },
  physical_dps_crit: { name: 'Physical DPS / Crit', color: 'text-red-400 border-red-500/30', icon: '⚔️' },
  healer: { name: 'Healer', color: 'text-emerald-400 border-emerald-500/30', icon: '✨' },
  support_buff: { name: 'Support / Buff', color: 'text-amber-400 border-amber-500/30', icon: '🎯' },
  shield_tank: { name: 'Shield Tank', color: 'text-blue-400 border-blue-500/30', icon: '🔰' },
  rogue_evasion: { name: 'Rogue / Evasion', color: 'text-purple-400 border-purple-500/30', icon: '🗡️' },
  fire_mage_dot: { name: 'Fire Mage / DoT', color: 'text-orange-400 border-orange-500/30', icon: '🔥' },
  ice_mage_control: { name: 'Ice Mage / Control', color: 'text-cyan-400 border-cyan-500/30', icon: '❄️' },
  bruiser_hp_atk: { name: 'Bruiser / HP+ATK', color: 'text-yellow-400 border-yellow-500/30', icon: '💪' },
  speed_evasion: { name: 'Speed / Evasion', color: 'text-teal-400 border-teal-500/30', icon: '💨' },
  anti_burst_mitigation: { name: 'Anti-Burst / Mitigation', color: 'text-slate-400 border-slate-500/30', icon: '🏠' },
  lifesteal_sustain_dps: { name: 'Lifesteal / Sustain DPS', color: 'text-rose-400 border-rose-500/30', icon: '🩸' },
};

const STAT_LABELS: Record<string, string> = {
  hp_regen_percent: 'HP Regen/s',
  mp_regen_percent: 'MP Regen/s',
  hp_max: 'HP Max',
  mp_max: 'MP Max',
  heal_received_percent: 'Heal Received',
  def_percent: 'DEF',
  armor: 'Armor',
  damage_reduction_percent: 'Damage Reduction',
  aggro_generation_percent: 'Aggro Generation',
  atk_percent: 'ATK',
  mag_percent: 'MAG',
  all_stats_percent: 'All Stats',
  xp_gain_percent: 'XP Gain',
  gold_drop_percent: 'Gold Drop',
  crit_chance_percent: 'Crit Chance',
  crit_damage_percent: 'Crit Damage',
  armor_penetration_percent: 'Armor Pen',
  heal_power_percent: 'Heal Power',
  mana_cost_reduction_percent: 'Mana Cost Reduction',
  hot_effectiveness_percent: 'HoT Effectiveness',
  shield_power_percent: 'Shield Power',
  buff_duration_percent: 'Buff Duration',
  buff_potency_percent: 'Buff Potency',
  block_chance_percent: 'Block Chance',
  shield_received_percent: 'Shield Received',
  flee_percent: 'Flee (Evasion)',
  attack_speed_percent: 'Attack Speed',
  burn_damage_percent: 'Burn Damage',
  dot_duration_bonus: 'DoT Duration',
  dot_damage_percent: 'DoT Damage',
  magic_penetration_percent: 'Magic Pen',
  slow_potency_percent: 'Slow Potency',
  cc_duration_bonus: 'CC Duration',
  magic_resist_debuff_percent: 'MR Debuff',
  lifesteal_percent: 'Lifesteal',
  spell_vamp_percent: 'Spell Vamp',
  crit_damage_received_reduction_percent: 'Crit Damage Received Reduction',
};

function formatBonus(stat: string, value: number): string {
  const label = STAT_LABELS[stat] || stat;
  const isFlat = stat.includes('_max') || stat === 'armor' || stat.includes('_bonus');
  const prefix = value > 0 ? '+' : '';
  const suffix = isFlat ? '' : '%';
  return `${prefix}${value}${suffix} ${label}`;
}

function SetCard({ set }: { set: PanoplieSet }) {
  const identity = IDENTITY_CONFIG[set.identity] || { name: set.identity, color: 'text-zinc-400 border-zinc-500/30', icon: '?' };
  const bonusLevels = Object.keys(set.bonuses).sort((a, b) => parseInt(a) - parseInt(b));

  return (
    <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4 hover:border-zinc-700 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-lg">{set.name_fr}</h3>
          <p className="text-xs text-zinc-500">{set.name_en}</p>
        </div>
        <div className={`px-2 py-1 rounded border text-xs ${identity.color}`}>
          {identity.icon} {identity.name}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-zinc-400 mb-3 italic">{set.description_fr}</p>

      {/* Meta info */}
      <div className="flex gap-3 mb-4 text-xs">
        <span className="bg-zinc-800 px-2 py-1 rounded">
          Lvl {set.level_range[0]}-{set.level_range[1]}
        </span>
        <span className="bg-zinc-800 px-2 py-1 rounded">
          {set.pieces_count} pièces
        </span>
      </div>

      {/* Bonus levels */}
      <div className="space-y-2 mb-4">
        {bonusLevels.map((level) => (
          <div key={level} className="bg-zinc-800/50 rounded p-2">
            <div className="text-xs font-medium text-violet-400 mb-1">{level} pièces:</div>
            <div className="flex flex-wrap gap-1">
              {Object.entries(set.bonuses[level]).map(([stat, value]) => (
                <span key={stat} className="text-xs bg-zinc-700/50 px-1.5 py-0.5 rounded text-zinc-300">
                  {formatBonus(stat, value)}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Total at max */}
      <div className="border-t border-zinc-700 pt-3">
        <div className="text-xs font-medium text-emerald-400 mb-2">
          TOTAL ({set.pieces_count}p):
        </div>
        <div className="flex flex-wrap gap-1">
          {Object.entries(set.total_at_max).map(([stat, value]) => (
            <span key={stat} className="text-xs bg-emerald-500/10 border border-emerald-500/30 px-1.5 py-0.5 rounded text-emerald-300">
              {formatBonus(stat, value)}
            </span>
          ))}
        </div>
      </div>

      {/* Pieces list */}
      <details className="mt-3">
        <summary className="text-xs text-zinc-500 cursor-pointer hover:text-zinc-400">
          Voir les {set.pieces_count} pièces
        </summary>
        <div className="mt-2 grid grid-cols-2 gap-1 text-xs text-zinc-500">
          {Object.entries(set.pieces).map(([slot, itemId]) => (
            <div key={slot} className="bg-zinc-800/30 px-2 py-1 rounded">
              <span className="text-zinc-400">{slot}:</span> {itemId.replace('item_', '')}
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}

export default function PanopliesPage() {
  const [data, setData] = useState<PanopliesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterIdentity, setFilterIdentity] = useState<string>('all');
  const [filterPieces, setFilterPieces] = useState<string>('all');

  useEffect(() => {
    fetch('/api/panoplies')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse text-zinc-500">Chargement des panoplies...</div>
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

  const sets = Object.values(data.sets);
  const identities = [...new Set(sets.map(s => s.identity))];

  const filteredSets = sets.filter(set => {
    if (filterIdentity !== 'all' && set.identity !== filterIdentity) return false;
    if (filterPieces !== 'all' && set.pieces_count !== parseInt(filterPieces)) return false;
    return true;
  });

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Panoplies</h1>
        <p className="text-zinc-500 text-sm">
          {data._meta.total_sets} sets - Âge de l&apos;Harmonie (lvl 1-20)
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-4">
        <div>
          <label className="text-xs text-zinc-500 block mb-1">Identité</label>
          <select
            value={filterIdentity}
            onChange={(e) => setFilterIdentity(e.target.value)}
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
          >
            <option value="all">Toutes ({sets.length})</option>
            {identities.map(id => {
              const config = IDENTITY_CONFIG[id] || { name: id, icon: '' };
              const count = sets.filter(s => s.identity === id).length;
              return (
                <option key={id} value={id}>
                  {config.icon} {config.name} ({count})
                </option>
              );
            })}
          </select>
        </div>

        <div>
          <label className="text-xs text-zinc-500 block mb-1">Nombre de pièces</label>
          <select
            value={filterPieces}
            onChange={(e) => setFilterPieces(e.target.value)}
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
          >
            <option value="all">Toutes</option>
            <option value="6">6 pièces ({sets.filter(s => s.pieces_count === 6).length})</option>
            <option value="8">8 pièces ({sets.filter(s => s.pieces_count === 8).length})</option>
          </select>
        </div>
      </div>

      {/* Summary by identity */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-sm font-medium mb-3">Par type de build</h2>
        <div className="flex flex-wrap gap-2">
          {Object.entries(data._summary.by_identity).map(([identity, setIds]) => {
            const config = IDENTITY_CONFIG[identity] || { name: identity, icon: '?', color: 'text-zinc-400' };
            return (
              <button
                key={identity}
                onClick={() => setFilterIdentity(filterIdentity === identity ? 'all' : identity)}
                className={`px-3 py-1.5 rounded text-xs transition-colors border ${
                  filterIdentity === identity
                    ? 'bg-violet-500/20 border-violet-500 text-violet-300'
                    : `bg-zinc-800/50 ${config.color}`
                }`}
              >
                {config.icon} {config.name} ({setIds.length})
              </button>
            );
          })}
        </div>
      </div>

      {/* Sets grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredSets.map(set => (
          <SetCard key={set.id} set={set} />
        ))}
      </div>

      {filteredSets.length === 0 && (
        <div className="text-center text-zinc-500 py-8">
          Aucune panoplie ne correspond aux filtres.
        </div>
      )}
    </div>
  );
}
