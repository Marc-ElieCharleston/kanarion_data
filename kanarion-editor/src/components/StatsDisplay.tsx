'use client';

interface StatsDisplayProps {
  baseStats: Record<string, number | string>;
  growth?: Record<string, number>;
  level?: number;
}

const STAT_CATEGORIES = {
  resources: ['hp', 'mp', 'hp_regen', 'mp_regen', 'hp_regen_combat', 'mp_regen_combat'],
  offensive: ['atk', 'mag', 'crit', 'crit_dmg', 'armor_pen', 'magic_pen', 'damage_percent', 'debuff_duration'],
  defensive: ['def', 'armor', 'magic_resist', 'damage_reduction', 'block_chance', 'parry_chance', 'effect_resist', 'tenacity'],
  precision: ['hit', 'flee', 'attack_speed', 'double_hit_chance'],
  support: ['heal_power', 'shield_power', 'healing_received', 'effect_chance', 'buff_duration'],
  special: ['lifesteal', 'spell_vamp', 'cast_speed', 'cooldown_reduction', 'luck'],
};

const STAT_LABELS: Record<string, string> = {
  hp: 'HP',
  mp: 'MP',
  hp_regen: 'HP Regen',
  mp_regen: 'MP Regen',
  hp_regen_combat: 'HP Regen (Combat)',
  mp_regen_combat: 'MP Regen (Combat)',
  atk: 'ATK',
  def: 'DEF',
  mag: 'MAG',
  armor: 'Armor',
  magic_resist: 'M.Resist',
  crit: 'Crit%',
  crit_dmg: 'Crit DMG',
  hit: 'Hit',
  flee: 'Flee',
  armor_pen: 'Armor Pen',
  magic_pen: 'Magic Pen',
  effect_chance: 'Effect%',
  effect_resist: 'Effect Res',
  debuff_duration: 'Debuff Dur',
  tenacity: 'Tenacity',
  buff_duration: 'Buff Dur',
  damage_percent: 'DMG%',
  damage_reduction: 'DMG Red',
  double_hit_chance: 'Double Hit',
  attack_speed: 'ATK Speed',
  heal_power: 'Heal Power',
  shield_power: 'Shield Power',
  healing_received: 'Heal Received',
  block_chance: 'Block%',
  parry_chance: 'Parry%',
  lifesteal: 'Lifesteal',
  spell_vamp: 'Spell Vamp',
  cast_speed: 'Cast Speed',
  cooldown_reduction: 'CDR',
  luck: 'Luck',
};

const STAT_COLORS: Record<string, string> = {
  resources: 'text-rose-400',
  offensive: 'text-orange-400',
  defensive: 'text-sky-400',
  precision: 'text-violet-400',
  support: 'text-emerald-400',
  special: 'text-amber-400',
};

const CATEGORY_LABELS: Record<string, string> = {
  resources: 'Resources',
  offensive: 'Offensive',
  defensive: 'Defensive',
  precision: 'Precision',
  support: 'Support',
  special: 'Special',
};

export default function StatsDisplay({ baseStats, growth, level = 1 }: StatsDisplayProps) {
  const calculateStat = (stat: string, base: number): number => {
    if (!growth || level === 1) return base;
    const growthValue = growth[stat] || 0;
    return Math.round((base + growthValue * (level - 1)) * 100) / 100;
  };

  const renderStatRow = (stat: string, category: string) => {
    const base = baseStats[stat];
    if (base === undefined || typeof base === 'string') return null;

    const current = calculateStat(stat, base);
    const growthValue = growth?.[stat];

    return (
      <div key={stat} className="flex justify-between items-center py-1 px-2 hover:bg-zinc-800/50 rounded">
        <span className={`text-sm ${STAT_COLORS[category]}`}>
          {STAT_LABELS[stat] || stat}
        </span>
        <div className="flex items-center gap-2">
          <span className="font-mono text-white">{current}</span>
          {growthValue !== undefined && growthValue !== 0 && (
            <span className="text-xs text-emerald-500 font-mono">
              +{growthValue}/lvl
            </span>
          )}
        </div>
      </div>
    );
  };

  const renderCategory = (category: string, stats: string[]) => {
    const renderedStats = stats.map(stat => renderStatRow(stat, category)).filter(Boolean);
    if (renderedStats.length === 0) return null;

    return (
      <div key={category} className="space-y-1">
        <h4 className={`text-xs uppercase tracking-wider ${STAT_COLORS[category]} opacity-70 mb-2 flex items-center gap-2`}>
          <span>{CATEGORY_LABELS[category]}</span>
          <span className="text-zinc-600">({renderedStats.length})</span>
        </h4>
        {renderedStats}
      </div>
    );
  };

  return (
    <div className="bg-zinc-900 rounded-lg p-4">
      {baseStats.identity && (
        <div className="text-sm text-zinc-400 italic mb-4 pb-2 border-b border-zinc-700">
          {baseStats.identity}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(STAT_CATEGORIES).map(([category, stats]) =>
          renderCategory(category, stats)
        )}
      </div>

      {/* Légende */}
      <div className="mt-6 pt-4 border-t border-zinc-800 text-xs text-zinc-500">
        <div className="flex flex-wrap gap-4">
          <span>
            <span className="text-emerald-500">+X/lvl</span> = Growth par niveau
          </span>
          <span>
            Stats techniques (crit, flee, block...) = équipement/passifs seulement
          </span>
        </div>
      </div>
    </div>
  );
}
