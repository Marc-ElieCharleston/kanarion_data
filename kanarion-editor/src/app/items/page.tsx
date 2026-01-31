'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { LoadingState } from '@/components/LoadingState';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface BaseItem {
  id: string;
  name: string;
  level_req?: number;
  class_tags?: string[];
  base_stats?: Record<string, number>;
  weight?: string;
}

interface Equipment {
  _meta: { version: string; last_updated: string; description: string };
  equipment_system: {
    slots: string[];
    slots_display: Record<string, string>;
    rarities: { id: string; base_mult: number; affix_min: number; affix_max: number; color: string }[];
    level_brackets: { id: string; min: number; max: number }[];
  };
  base_items: {
    weapons: Record<string, BaseItem[]>;
    armor: Record<string, BaseItem[]>;
    accessories?: Record<string, BaseItem[]>;
  };
}

interface Consumable {
  id: string;
  name: string;
  description: string;
  rarity: string;
  stack_max: number;
  buy_price?: number;
  sell_price: number;
  effect: Record<string, unknown>;
}

interface Material {
  id: string;
  name: string;
  sell_price: number;
  sources: string[];
  rarity?: string;
  buy_price?: number;
}

interface Affix {
  id: string;
  name: string;
  weight: number;
  level_range: [number, number];
  allowed_slots: string[];
  rolls: { stat: string; min: number; max: number }[];
}

interface Currency {
  id: string;
  name: string;
  is_soft_currency: boolean;
  enabled?: boolean;
  icon: string;
  sources: string[];
  uses: string[];
}

interface ItemsData {
  equipment: Equipment;
  consumables: { _meta: unknown; potions: Consumable[]; food: Consumable[] };
  materials: { _meta: unknown; common: Material[]; uncommon: Material[]; rare: Material[]; gems: Material[] };
  affixes: { _meta: unknown; prefixes: Affix[]; suffixes: Affix[] };
  currencies: { _meta: unknown; currencies: Currency[]; rarity_colors: Record<string, { hex: string; name: string }> };
}

const TABS = [
  { id: 'equipment', name_fr: 'Equipements', name_en: 'Equipment', icon: '⚔️' },
  { id: 'consumables', name_fr: 'Consommables', name_en: 'Consumables', icon: '🧪' },
  { id: 'materials', name_fr: 'Materiaux', name_en: 'Materials', icon: '📦' },
  { id: 'affixes', name_fr: 'Affixes', name_en: 'Affixes', icon: '✨' },
  { id: 'currencies', name_fr: 'Monnaies', name_en: 'Currencies', icon: '💰' },
];

function EquipmentTab({ data }: { data: Equipment }) {
  const [selectedCategory, setSelectedCategory] = useState<'weapons' | 'armor'>('weapons');
  const { locale } = useLocale();

  const categories = [
    { id: 'weapons', name_fr: 'Armes', name_en: 'Weapons' },
    { id: 'armor', name_fr: 'Armures', name_en: 'Armor' },
  ];

  const items = data.base_items[selectedCategory];
  const rarities = data.equipment_system.rarities;

  return (
    <div>
      {/* Rarity Legend */}
      <div className="mb-6 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
        <h3 className="text-sm font-medium mb-3">{locale === 'en' ? 'Rarity System' : 'Systeme de Rarete'}</h3>
        <div className="flex flex-wrap gap-2">
          {rarities.map((r) => (
            <Badge key={r.id} style={{ backgroundColor: r.color + '20', color: r.color, borderColor: r.color }}>
              {r.id} ({r.affix_min}-{r.affix_max} affixes, x{r.base_mult})
            </Badge>
          ))}
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 mb-4">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id as 'weapons' | 'armor')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedCategory === cat.id
                ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
            }`}
          >
            {locale === 'en' ? cat.name_en : cat.name_fr}
          </button>
        ))}
      </div>

      {/* Items Grid */}
      <div className="space-y-6">
        {Object.entries(items).map(([type, itemList]) => (
          <div key={type}>
            <h3 className="text-lg font-semibold capitalize mb-3 text-zinc-200">{type}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {itemList.map((item) => (
                <Card key={item.id} className="p-3 hover:border-zinc-600 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-zinc-200">{item.name}</span>
                    <Badge variant="outline" className="text-xs">Lv {item.level_req}</Badge>
                  </div>
                  {item.class_tags && (
                    <div className="flex gap-1 mb-2">
                      {item.class_tags.map((tag) => (
                        <span key={tag} className="text-xs bg-zinc-800 px-1.5 py-0.5 rounded text-zinc-400 capitalize">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  {item.weight && (
                    <span className="text-xs text-zinc-500 capitalize">{item.weight}</span>
                  )}
                  {item.base_stats && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {Object.entries(item.base_stats).map(([stat, value]) => (
                        <span key={stat} className="text-xs text-emerald-400">
                          +{value} {stat.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ConsumablesTab({ data }: { data: ItemsData['consumables'] }) {
  const { locale } = useLocale();
  const allConsumables = [...(data.potions || []), ...(data.food || [])];

  const rarityColors: Record<string, string> = {
    common: '#FFFFFF',
    uncommon: '#00FF00',
    rare: '#0088FF',
    epic: '#AA00FF',
    legendary: '#FF8800',
  };

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-sm text-zinc-500">{allConsumables.length} {locale === 'en' ? 'consumables' : 'consommables'}</h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {allConsumables.map((item) => (
          <Card key={item.id} className="p-4 hover:border-zinc-600 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium" style={{ color: rarityColors[item.rarity] || '#FFFFFF' }}>
                {item.name}
              </span>
              <Badge variant="outline" className="text-xs capitalize">{item.rarity}</Badge>
            </div>
            <p className="text-sm text-zinc-400 mb-3">{item.description}</p>
            <div className="flex justify-between text-xs text-zinc-500">
              <span>{locale === 'en' ? 'Stack' : 'Pile'}: {item.stack_max}</span>
              <span className="text-yellow-400">{item.buy_price ? `${item.buy_price}g` : ''}</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function MaterialsTab({ data }: { data: ItemsData['materials'] }) {
  const { locale } = useLocale();
  const categories = [
    { id: 'common', name_fr: 'Commun', name_en: 'Common', items: data.common || [], color: '#FFFFFF' },
    { id: 'uncommon', name_fr: 'Peu commun', name_en: 'Uncommon', items: data.uncommon || [], color: '#00FF00' },
    { id: 'rare', name_fr: 'Rare', name_en: 'Rare', items: data.rare || [], color: '#0088FF' },
    { id: 'gems', name_fr: 'Gemmes', name_en: 'Gems', items: data.gems || [], color: '#AA00FF' },
  ];

  return (
    <div className="space-y-8">
      {categories.map((cat) => (
        <div key={cat.id}>
          <div className="flex items-center gap-2 mb-4">
            <h3 className="text-lg font-semibold" style={{ color: cat.color }}>
              {locale === 'en' ? cat.name_en : cat.name_fr}
            </h3>
            <span className="text-sm text-zinc-500">({cat.items.length})</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {cat.items.map((mat) => (
              <Card key={mat.id} className="p-3 hover:border-zinc-600 transition-colors">
                <div className="font-medium text-zinc-200 mb-1">{mat.name}</div>
                <div className="flex justify-between text-xs">
                  <span className="text-zinc-500">{mat.sources?.join(', ')}</span>
                  <span className="text-yellow-400">{mat.sell_price}g</span>
                </div>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function AffixesTab({ data }: { data: ItemsData['affixes'] }) {
  const { locale } = useLocale();
  const [selectedType, setSelectedType] = useState<'prefixes' | 'suffixes'>('prefixes');

  const affixes = data[selectedType] || [];

  return (
    <div>
      {/* Type Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setSelectedType('prefixes')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            selectedType === 'prefixes'
              ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
              : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
          }`}
        >
          {locale === 'en' ? 'Prefixes' : 'Prefixes'} ({data.prefixes?.length || 0})
        </button>
        <button
          onClick={() => setSelectedType('suffixes')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            selectedType === 'suffixes'
              ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
              : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
          }`}
        >
          {locale === 'en' ? 'Suffixes' : 'Suffixes'} ({data.suffixes?.length || 0})
        </button>
      </div>

      {/* Affixes Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm bg-zinc-900 rounded-lg border border-zinc-800">
          <thead>
            <tr className="border-b border-zinc-700">
              <th className="text-left py-3 px-4 text-zinc-400">{locale === 'en' ? 'Name' : 'Nom'}</th>
              <th className="text-center py-3 px-4 text-zinc-400">{locale === 'en' ? 'Level Range' : 'Niveaux'}</th>
              <th className="text-center py-3 px-4 text-zinc-400">{locale === 'en' ? 'Weight' : 'Poids'}</th>
              <th className="text-left py-3 px-4 text-zinc-400">{locale === 'en' ? 'Slots' : 'Emplacements'}</th>
              <th className="text-left py-3 px-4 text-zinc-400">{locale === 'en' ? 'Stats' : 'Stats'}</th>
            </tr>
          </thead>
          <tbody>
            {affixes.map((affix, i) => (
              <tr key={affix.id} className={`border-b border-zinc-800 ${i % 2 === 0 ? 'bg-zinc-800/20' : ''}`}>
                <td className="py-3 px-4 font-medium text-zinc-200">{affix.name}</td>
                <td className="py-3 px-4 text-center text-zinc-400">
                  Lv {affix.level_range[0]}-{affix.level_range[1]}
                </td>
                <td className="py-3 px-4 text-center text-zinc-400">{affix.weight}</td>
                <td className="py-3 px-4">
                  <div className="flex flex-wrap gap-1">
                    {affix.allowed_slots.map((slot) => (
                      <span key={slot} className="text-xs bg-zinc-800 px-1.5 py-0.5 rounded text-zinc-400 capitalize">
                        {slot}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="py-3 px-4">
                  {affix.rolls.map((roll, j) => (
                    <span key={j} className="text-emerald-400 text-xs mr-2">
                      +{roll.min}-{roll.max} {roll.stat.toUpperCase()}
                    </span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CurrenciesTab({ data }: { data: ItemsData['currencies'] }) {
  const { locale } = useLocale();

  return (
    <div>
      {/* Currencies */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">{locale === 'en' ? 'Currencies' : 'Monnaies'}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.currencies.map((currency) => (
            <Card key={currency.id} className={`p-4 ${currency.enabled === false ? 'opacity-50' : ''}`}>
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">{currency.id === 'gold' ? '🪙' : '💎'}</span>
                <div>
                  <h4 className="font-semibold text-zinc-200">{currency.name}</h4>
                  <Badge variant="outline" className="text-xs">
                    {currency.is_soft_currency ? 'Soft' : 'Premium'}
                  </Badge>
                  {currency.enabled === false && (
                    <Badge variant="outline" className="text-xs ml-1 text-red-400 border-red-400">Disabled</Badge>
                  )}
                </div>
              </div>
              <div className="space-y-2">
                <div>
                  <span className="text-xs text-zinc-500">{locale === 'en' ? 'Sources' : 'Sources'}:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {currency.sources.map((src) => (
                      <span key={src} className="text-xs bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded">
                        {src.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-xs text-zinc-500">{locale === 'en' ? 'Uses' : 'Usages'}:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {currency.uses.map((use) => (
                      <span key={use} className="text-xs bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded">
                        {use.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Rarity Colors */}
      <div>
        <h3 className="text-lg font-semibold mb-4">{locale === 'en' ? 'Rarity Colors' : 'Couleurs de Rarete'}</h3>
        <div className="flex flex-wrap gap-3">
          {Object.entries(data.rarity_colors).map(([rarity, info]) => (
            <div key={rarity} className="flex items-center gap-2 bg-zinc-800 px-3 py-2 rounded-lg">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: info.hex }} />
              <span className="text-sm capitalize" style={{ color: info.hex }}>{rarity}</span>
              <span className="text-xs text-zinc-500">({info.name})</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ItemsPage() {
  const [activeTab, setActiveTab] = useState('equipment');
  const [data, setData] = useState<ItemsData | null>(null);
  const [loading, setLoading] = useState(true);
  const { locale } = useLocale();

  useEffect(() => {
    fetch('/api/items')
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <LoadingState />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-red-400">
        {locale === 'en' ? 'Failed to load items' : 'Erreur de chargement'}
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Secondary Sidebar */}
      <aside className="w-64 border-r border-zinc-800 overflow-y-auto bg-zinc-900/50">
        <div className="p-4 border-b border-zinc-800">
          <h2 className="text-lg font-semibold">{locale === 'en' ? 'Items' : 'Items'}</h2>
          <p className="text-xs text-zinc-500">{locale === 'en' ? 'Game items database' : 'Base de donnees items'}</p>
        </div>
        <nav className="p-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-left ${
                activeTab === tab.id
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                  : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
              }`}
            >
              <span className="text-xl">{tab.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{locale === 'en' ? tab.name_en : tab.name_fr}</div>
                <div className="text-xs text-zinc-500 truncate">{locale === 'en' ? tab.name_fr : tab.name_en}</div>
              </div>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {activeTab === 'equipment' && <EquipmentTab data={data.equipment} />}
          {activeTab === 'consumables' && <ConsumablesTab data={data.consumables} />}
          {activeTab === 'materials' && <MaterialsTab data={data.materials} />}
          {activeTab === 'affixes' && <AffixesTab data={data.affixes} />}
          {activeTab === 'currencies' && <CurrenciesTab data={data.currencies} />}
        </div>
      </main>
    </div>
  );
}
