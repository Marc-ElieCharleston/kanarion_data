'use client';

import { useEffect, useState } from 'react';

interface SetBonus {
  [key: string]: number;
}

interface PieceInfo {
  id: string;
  name_fr: string;
  name_en: string;
}

interface PanoplieSet {
  id: string;
  name_fr: string;
  name_en: string;
  meaning: string;
  identity: string;
  armor_type: string;
  description_fr: string;
  description_en: string;
  pieces_count: number;
  pieces: Record<string, PieceInfo>;
  bonuses: Record<string, SetBonus>;
  total_at_max: SetBonus;
}

interface EquipmentSlot {
  id: string;
  name_fr: string;
  name_en: string;
}

interface PanopliesData {
  _meta: {
    version: string;
    last_updated: string;
    description: string;
    total_sets: number;
    tier_system: Record<string, { level_range: [number, number]; stat_multiplier: number }>;
    equipment_slots: EquipmentSlot[];
    notes: Record<string, string>;
  };
  sets: Record<string, PanoplieSet>;
  _summary: {
    total_sets: number;
    by_size: Record<string, string[]>;
    by_armor_type: Record<string, string[]>;
    by_identity: Record<string, string[]>;
  };
}

const IDENTITY_CONFIG: Record<string, { name: string; color: string; icon: string }> = {
  // Mini-sets (2p)
  lifesteal_link: { name: 'Lifesteal Link', color: 'text-rose-400 border-rose-500/30', icon: '🩸' },
  crit_marker: { name: 'Crit / Marker', color: 'text-red-400 border-red-500/30', icon: '🎯' },
  hp_regen: { name: 'HP Regen', color: 'text-green-400 border-green-500/30', icon: '💚' },
  mana_wisdom: { name: 'Mana / Wisdom', color: 'text-blue-400 border-blue-500/30', icon: '🔮' },
  mana_sustain: { name: 'Mana Sustain', color: 'text-blue-400 border-blue-500/30', icon: '💙' },
  raw_power: { name: 'Raw Power', color: 'text-orange-400 border-orange-500/30', icon: '💪' },
  defense_anchor: { name: 'Defense Anchor', color: 'text-sky-400 border-sky-500/30', icon: '🛡️' },
  // Medium sets (4p)
  speed_evasion: { name: 'Speed / Evasion', color: 'text-teal-400 border-teal-500/30', icon: '💨' },
  buff_support: { name: 'Buff / Support', color: 'text-amber-400 border-amber-500/30', icon: '✨' },
  control_slow: { name: 'Control / Slow', color: 'text-cyan-400 border-cyan-500/30', icon: '❄️' },
  armor_break: { name: 'Armor Break', color: 'text-yellow-500 border-yellow-500/30', icon: '⚔️' },
  hot_healer: { name: 'HoT Healer', color: 'text-emerald-400 border-emerald-500/30', icon: '🌿' },
  hp_tank: { name: 'HP Tank', color: 'text-slate-400 border-slate-500/30', icon: '🪨' },
  mage_dps: { name: 'Mage DPS', color: 'text-violet-400 border-violet-500/30', icon: '🔮' },
  physical_dps: { name: 'Physical DPS', color: 'text-red-500 border-red-500/30', icon: '⚔️' },
  // Large sets (6p)
  rogue_assassin: { name: 'Rogue / Assassin', color: 'text-purple-400 border-purple-500/30', icon: '🗡️' },
  healer_holy: { name: 'Holy Healer', color: 'text-yellow-300 border-yellow-400/30', icon: '☀️' },
  fire_mage_dot: { name: 'Fire Mage / DoT', color: 'text-orange-500 border-orange-500/30', icon: '🔥' },
  ice_mage_control: { name: 'Ice Mage / Control', color: 'text-cyan-300 border-cyan-400/30', icon: '❄️' },
  shield_tank: { name: 'Shield Tank', color: 'text-blue-500 border-blue-500/30', icon: '🔰' },
  balanced_utility: { name: 'Balanced / Utility', color: 'text-zinc-400 border-zinc-500/30', icon: '⚖️' },
  // Complete sets (8p)
  main_tank: { name: 'Main Tank', color: 'text-sky-400 border-sky-500/30', icon: '🛡️' },
  physical_dps_crit: { name: 'Physical DPS / Crit', color: 'text-red-500 border-red-500/30', icon: '🏹' },
  sustain_regen: { name: 'Sustain / Regen', color: 'text-green-400 border-green-500/30', icon: '💚' },
  bruiser_hp_atk: { name: 'Bruiser / HP+ATK', color: 'text-yellow-400 border-yellow-500/30', icon: '💪' },
};

const ARMOR_TYPE_CONFIG: Record<string, { name_fr: string; name_en: string; color: string; icon: string }> = {
  cloth: { name_fr: 'Tissu', name_en: 'Cloth', color: 'text-violet-400 border-violet-500/30', icon: '👘' },
  leather: { name_fr: 'Cuir', name_en: 'Leather', color: 'text-amber-500 border-amber-500/30', icon: '🦊' },
  plate: { name_fr: 'Plaque', name_en: 'Plate', color: 'text-slate-300 border-slate-400/30', icon: '⚙️' },
  mixed: { name_fr: 'Mixte', name_en: 'Mixed', color: 'text-zinc-400 border-zinc-500/30', icon: '⚖️' },
};

const STAT_LABELS: Record<string, { fr: string; en: string }> = {
  // Resources
  hp_max: { fr: 'HP Max', en: 'Max HP' },
  mp_max: { fr: 'MP Max', en: 'Max MP' },
  hp_regen: { fr: 'Regen HP', en: 'HP Regen' },
  mp_regen: { fr: 'Regen MP', en: 'MP Regen' },
  // Offensive
  atk: { fr: 'ATK', en: 'ATK' },
  atk_percent: { fr: 'ATK %', en: 'ATK %' },
  mag: { fr: 'MAG', en: 'MAG' },
  mag_percent: { fr: 'MAG %', en: 'MAG %' },
  crit: { fr: 'Critique', en: 'Crit Chance' },
  crit_dmg: { fr: 'Degats Crit', en: 'Crit Damage' },
  damage_percent: { fr: 'Degats %', en: 'Damage %' },
  attack_speed: { fr: 'Vitesse ATK', en: 'Attack Speed' },
  armor_pen: { fr: 'Pen. Armure', en: 'Armor Pen' },
  magic_pen: { fr: 'Pen. Magique', en: 'Magic Pen' },
  effect_chance: { fr: 'Chance Effet', en: 'Effect Chance' },
  debuff_duration: { fr: 'Duree Debuff', en: 'Debuff Duration' },
  // Defensive
  def_percent: { fr: 'DEF %', en: 'DEF %' },
  armor: { fr: 'Armure', en: 'Armor' },
  damage_reduction: { fr: 'Reduction Degats', en: 'Damage Reduction' },
  block_chance: { fr: 'Chance Blocage', en: 'Block Chance' },
  flee: { fr: 'Esquive', en: 'Flee (Evasion)' },
  hit: { fr: 'Precision', en: 'Hit Rate' },
  // Support
  heal_power: { fr: 'Puissance Soin', en: 'Heal Power' },
  shield_power: { fr: 'Puissance Bouclier', en: 'Shield Power' },
  healing_received: { fr: 'Soins Recus', en: 'Heal Received' },
  buff_duration: { fr: 'Duree Buffs', en: 'Buff Duration' },
  cooldown_reduction: { fr: 'Reduction CD', en: 'CDR' },
  // Special
  lifesteal: { fr: 'Vol de Vie', en: 'Lifesteal' },
  spell_vamp: { fr: 'Vol Magique', en: 'Spell Vamp' },
  thorns: { fr: 'Epines', en: 'Thorns' },
  luck: { fr: 'Chance', en: 'Luck' },
  cast_speed: { fr: 'Vitesse Incant.', en: 'Cast Speed' },
};

function formatBonus(stat: string, value: number): string {
  const label = STAT_LABELS[stat];
  const labelText = label ? `${label.fr}` : stat;
  const isFlat = stat.includes('_max') || stat === 'armor' || stat.includes('_bonus');
  const prefix = value > 0 ? '+' : '';
  const suffix = isFlat ? '' : '%';
  return `${prefix}${value}${suffix} ${labelText}`;
}

function SetCard({ set }: { set: PanoplieSet }) {
  const identity = IDENTITY_CONFIG[set.identity] || { name: set.identity, color: 'text-zinc-400 border-zinc-500/30', icon: '?' };
  const armorType = ARMOR_TYPE_CONFIG[set.armor_type] || { name_fr: set.armor_type, name_en: set.armor_type, color: 'text-zinc-400 border-zinc-500/30', icon: '?' };
  const bonusLevels = Object.keys(set.bonuses).sort((a, b) => parseInt(a) - parseInt(b));

  return (
    <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4 hover:border-zinc-700 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-lg">{set.name_fr}</h3>
          <p className="text-xs text-zinc-500">{set.name_en} • <span className="text-zinc-400 italic">&quot;{set.meaning}&quot;</span></p>
        </div>
        <div className="flex flex-col gap-1 items-end">
          <div className={`px-2 py-1 rounded border text-xs ${identity.color}`}>
            {identity.icon} {identity.name}
          </div>
          <div className={`px-2 py-0.5 rounded border text-[10px] ${armorType.color}`}>
            {armorType.icon} {armorType.name_fr} / {armorType.name_en}
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-zinc-400 mb-3 italic">{set.description_fr}</p>

      {/* Meta info */}
      <div className="flex gap-3 mb-4 text-xs">
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
          {Object.entries(set.pieces).map(([slot, piece]) => (
            <div key={slot} className="bg-zinc-800/30 px-2 py-1 rounded">
              <span className="text-zinc-400 capitalize">{slot.replace('_', ' ')}:</span>{' '}
              <span className="text-zinc-300">{piece.name_fr}</span>
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
  const [filterArmorType, setFilterArmorType] = useState<string>('all');

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

  // Filter out comment entries (they start with _)
  const sets = Object.entries(data.sets)
    .filter(([key]) => !key.startsWith('_'))
    .map(([, value]) => value);
  const identities = [...new Set(sets.map(s => s.identity))];
  const armorTypes = [...new Set(sets.map(s => s.armor_type))];

  const filteredSets = sets.filter(set => {
    if (filterIdentity !== 'all' && set.identity !== filterIdentity) return false;
    if (filterPieces !== 'all' && set.pieces_count !== parseInt(filterPieces)) return false;
    if (filterArmorType !== 'all' && set.armor_type !== filterArmorType) return false;
    return true;
  });

  return (
    <div className="p-4 md:p-6 lg:p-8">
      {/* Header */}
      <div className="mb-4 md:mb-6">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">Panoplies</h1>
        <p className="text-zinc-500 text-sm">
          {data._meta.total_sets} sets - {data._meta.description}
        </p>
        <p className="text-zinc-600 text-xs mt-1">
          v{data._meta.version} • Dernière mise à jour: {data._meta.last_updated}
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
            <option value="2">2 pièces ({sets.filter(s => s.pieces_count === 2).length})</option>
            <option value="4">4 pièces ({sets.filter(s => s.pieces_count === 4).length})</option>
            <option value="6">6 pièces ({sets.filter(s => s.pieces_count === 6).length})</option>
            <option value="8">8 pièces ({sets.filter(s => s.pieces_count === 8).length})</option>
          </select>
        </div>

        <div>
          <label className="text-xs text-zinc-500 block mb-1">Type d&apos;armure</label>
          <select
            value={filterArmorType}
            onChange={(e) => setFilterArmorType(e.target.value)}
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
          >
            <option value="all">Tous</option>
            {armorTypes.map(type => {
              const config = ARMOR_TYPE_CONFIG[type] || { name_fr: type, name_en: type, color: 'text-zinc-400', icon: '' };
              const count = sets.filter(s => s.armor_type === type).length;
              return (
                <option key={type} value={type}>
                  {config.icon} {config.name_fr} / {config.name_en} ({count})
                </option>
              );
            })}
          </select>
        </div>
      </div>

      {/* Summary by size */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-sm font-medium mb-3">Par taille de set</h2>
        <div className="flex flex-wrap gap-2">
          {Object.entries(data._summary.by_size).map(([size, setIds]) => {
            const sizeNum = size.replace('_pieces', '');
            return (
              <button
                key={size}
                onClick={() => setFilterPieces(filterPieces === sizeNum ? 'all' : sizeNum)}
                className={`px-3 py-1.5 rounded text-xs transition-colors border ${
                  filterPieces === sizeNum
                    ? 'bg-violet-500/20 border-violet-500 text-violet-300'
                    : 'bg-zinc-800/50 border-zinc-700 text-zinc-400'
                }`}
              >
                {sizeNum} pièces ({setIds.length})
              </button>
            );
          })}
        </div>
      </div>

      {/* Summary by armor type */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-sm font-medium mb-3">Par type d&apos;armure</h2>
        <div className="flex flex-wrap gap-2">
          {Object.entries(data._summary.by_armor_type).map(([type, setIds]) => {
            const config = ARMOR_TYPE_CONFIG[type] || { name_fr: type, name_en: type, icon: '?', color: 'text-zinc-400' };
            return (
              <button
                key={type}
                onClick={() => setFilterArmorType(filterArmorType === type ? 'all' : type)}
                className={`px-3 py-1.5 rounded text-xs transition-colors border ${
                  filterArmorType === type
                    ? 'bg-violet-500/20 border-violet-500 text-violet-300'
                    : `bg-zinc-800/50 ${config.color}`
                }`}
              >
                {config.icon} {config.name_fr} ({setIds.length})
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
