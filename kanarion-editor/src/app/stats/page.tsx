'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { SecondarySidebar } from '@/components/SecondarySidebar';
import { LoadingState } from '@/components/LoadingState';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface StatDefinition {
  name: string;
  name_en?: string;
  description: string;
  description_en?: string;
  bonus_type?: string;
  default?: number;
  cap?: number;
  formula?: string;
  point_value?: number;
  base_value?: number;
  derived?: boolean;
  clamp?: { min: number; max: number };
  effects?: Record<string, string>;
  aoe_effectiveness?: number;
}

interface StatsData {
  _meta: {
    version: string;
    last_updated: string;
    description: string;
    categories: string[];
    bonus_types: Record<string, string>;
  };
  stats: Record<string, Record<string, StatDefinition>>;
  effect_system: any;
  stacking_system: any;
  damage_pipeline: any;
}

const CATEGORY_COLORS: Record<string, string> = {
  resources: 'text-rose-400 border-rose-500/30',
  offensive: 'text-orange-400 border-orange-500/30',
  defensive: 'text-sky-400 border-sky-500/30',
  precision: 'text-violet-400 border-violet-500/30',
  support: 'text-emerald-400 border-emerald-500/30',
  special: 'text-amber-400 border-amber-500/30',
};

const CATEGORY_ICONS: Record<string, string> = {
  resources: '❤️',
  offensive: '⚔️',
  defensive: '🛡️',
  precision: '🎯',
  support: '💚',
  special: '✨',
};

export default function StatsReferencePage() {
  const [data, setData] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const { locale } = useLocale();

  useEffect(() => {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <LoadingState type="table" count={5} />;
  }

  if (!data) {
    return (
      <div className="p-8">
        <div className="text-red-400">Failed to load stats definitions</div>
      </div>
    );
  }

  // Flatten all stats for simple view
  const allStats: { key: string; stat: StatDefinition; category: string }[] = [];
  Object.entries(data.stats).forEach(([category, stats]) => {
    Object.entries(stats).forEach(([key, stat]) => {
      allStats.push({ key, stat, category });
    });
  });

  // Filter by search (search in both languages)
  const searchFilteredStats = searchTerm
    ? allStats.filter(
        ({ key, stat }) =>
          key.toLowerCase().includes(searchTerm.toLowerCase()) ||
          stat.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (stat.name_en?.toLowerCase().includes(searchTerm.toLowerCase())) ||
          stat.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (stat.description_en?.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : allStats;

  // Filter by category
  const filteredStats = activeCategory === 'all'
    ? searchFilteredStats
    : searchFilteredStats.filter(({ category }) => category === activeCategory);

  // Group by category for display
  const groupedStats: Record<string, typeof allStats> = {};
  filteredStats.forEach((item) => {
    if (!groupedStats[item.category]) {
      groupedStats[item.category] = [];
    }
    groupedStats[item.category].push(item);
  });

  // Category counts
  const categoryCounts: Record<string, number> = { all: allStats.length };
  Object.entries(data.stats).forEach(([category, stats]) => {
    categoryCounts[category] = Object.keys(stats).length;
  });

  // Build navigation items
  const navItems = [
    {
      id: 'all',
      icon: '📋',
      label: locale === 'fr' ? 'Toutes les Stats' : 'All Stats',
      count: categoryCounts.all,
      isActive: activeCategory === 'all',
      onClick: () => setActiveCategory('all'),
    },
    ...Object.keys(data.stats).map((category) => ({
      id: category,
      icon: CATEGORY_ICONS[category],
      label: category.charAt(0).toUpperCase() + category.slice(1),
      count: categoryCounts[category] || 0,
      isActive: activeCategory === category,
      onClick: () => setActiveCategory(category),
    })),
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      <SecondarySidebar
        title={locale === 'fr' ? 'Référence Stats' : 'Stats Reference'}
        subtitle={`${allStats.length} stats • v${data._meta.version}`}
        showSearch
        searchValue={searchTerm}
        onSearchChange={setSearchTerm}
        searchPlaceholder={locale === 'fr' ? 'Rechercher...' : 'Search stats...'}
        navItems={navItems}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {/* Stats List */}
          <div className="space-y-8">
            {Object.entries(groupedStats).map(([category, stats]) => (
              <div key={category}>
                {/* Category Header */}
                <h2 className={`text-lg font-semibold mb-3 flex items-center gap-2 ${CATEGORY_COLORS[category]?.split(' ')[0]}`}>
                  <span>{CATEGORY_ICONS[category]}</span>
                  <span className="capitalize">{category}</span>
                  <span className="text-zinc-600 text-sm font-normal">({stats.length})</span>
                </h2>

                {/* Stats Table */}
                <Card>
                  <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-36">Stat</TableHead>
                          <TableHead className="w-20">Bonus</TableHead>
                          <TableHead className="w-1/4">Description</TableHead>
                          <TableHead>{locale === 'fr' ? 'Calcul / Formule' : 'Formula'}</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {stats.map(({ key, stat }) => (
                          <TableRow key={key}>
                            <TableCell>
                              <div className={`font-medium ${CATEGORY_COLORS[category]?.split(' ')[0]}`}>
                                {locale === 'en' && stat.name_en ? stat.name_en : stat.name}
                              </div>
                              <code className="text-[10px] text-zinc-600">{key}</code>
                            </TableCell>
                            <TableCell>
                              {stat.bonus_type === 'both' && (
                                <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30">
                                  flat + %
                                </Badge>
                              )}
                              {stat.bonus_type === 'flat' && (
                                <Badge variant="secondary" className="bg-sky-500/20 text-sky-400 hover:bg-sky-500/30">
                                  flat
                                </Badge>
                              )}
                              {stat.bonus_type === 'percent' && (
                                <Badge variant="secondary" className="bg-violet-500/20 text-violet-400 hover:bg-violet-500/30">
                                  %
                                </Badge>
                              )}
                              {stat.bonus_type === 'none' && (
                                <Badge variant="secondary">—</Badge>
                              )}
                            </TableCell>
                            <TableCell className="text-sm text-zinc-300 whitespace-normal">
                              {locale === 'en' && stat.description_en ? stat.description_en : stat.description}
                              {stat.cap !== undefined && (
                                <Badge variant="destructive" className="ml-2">Cap: {stat.cap}</Badge>
                              )}
                              {stat.clamp && (
                                <Badge variant="outline" className="ml-2 text-amber-400 border-amber-400">
                                  Clamp: {stat.clamp.min}-{stat.clamp.max}%
                                </Badge>
                              )}
                            </TableCell>
                            <TableCell className="whitespace-normal">
                              {stat.formula ? (
                                <code className="text-xs text-emerald-400 bg-zinc-800 px-2 py-1 rounded break-all">
                                  {stat.formula}
                                </code>
                              ) : stat.default !== undefined ? (
                                <span className="text-xs text-zinc-500">
                                  Default: <span className="text-zinc-300">{stat.default}</span>
                                </span>
                              ) : stat.base_value !== undefined ? (
                                <span className="text-xs text-zinc-500">
                                  Base: <span className="text-zinc-300">{stat.base_value}</span>
                                </span>
                              ) : stat.derived ? (
                                <Badge variant="outline" className="text-violet-400 border-violet-400">Derived</Badge>
                              ) : (
                                <span className="text-xs text-zinc-600">—</span>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                  </Table>
                </Card>
              </div>
            ))}
          </div>

          {/* Quick Summary */}
          <Card className="mt-8">
            <CardContent className="p-4">
              <h3 className="font-semibold mb-3">{locale === 'fr' ? 'Résumé rapide' : 'Quick Summary'}</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 text-center text-sm">
                {Object.entries(data.stats).map(([category, stats]) => (
                  <Card key={category} className={`p-2 ${CATEGORY_COLORS[category]}`}>
                    <div className="text-lg">{CATEGORY_ICONS[category]}</div>
                    <div className="font-medium capitalize">{category}</div>
                    <div className="text-zinc-500 text-xs">{Object.keys(stats).length} stats</div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Effect System */}
          {data.effect_system && (
            <Card className="mt-8 border-violet-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-violet-400">
                  <span>🎯</span> {locale === 'fr' ? "Système d'Effets (CC/Debuffs)" : 'Effect System (CC/Debuffs)'}
                </CardTitle>
                <CardDescription>{data.effect_system.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="bg-zinc-800 p-4 rounded">
                    <h4 className="font-medium text-emerald-400 mb-2">Application (Chance)</h4>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-zinc-500">1.</span>
                        <code className="block text-xs text-emerald-400 mt-1">{data.effect_system.apply_formula?.step1}</code>
                      </div>
                      <div>
                        <span className="text-zinc-500">2.</span>
                        <code className="block text-xs text-amber-400 mt-1">{data.effect_system.apply_formula?.step2}</code>
                      </div>
                      <div>
                        <span className="text-zinc-500">3.</span>
                        <code className="block text-xs text-sky-400 mt-1">{data.effect_system.apply_formula?.step3}</code>
                      </div>
                    </div>
                    <p className="mt-3 text-xs text-zinc-500">
                      {data.effect_system.apply_formula?.explanation}
                    </p>
                  </div>
                  <div className="bg-zinc-800 p-4 rounded">
                    <h4 className="font-medium text-amber-400 mb-2">{locale === 'fr' ? 'Durée Debuffs' : 'Debuff Duration'}</h4>
                    <div className="space-y-2 text-sm">
                      <code className="block text-xs text-amber-400">{data.effect_system.duration_formula?.attacker_bonus}</code>
                      <code className="block text-xs text-sky-400">{data.effect_system.duration_formula?.defender_reduction}</code>
                    </div>
                    <p className="text-xs text-zinc-500 mt-2">
                      {locale === 'fr' ? 'Durée min' : 'Min duration'}: {data.effect_system.duration_formula?.minimum_duration}s
                    </p>
                    <p className="text-xs text-zinc-400 mt-2">
                      Ex: {data.effect_system.duration_formula?.example}
                    </p>
                  </div>
                  <div className="bg-zinc-800 p-4 rounded">
                    <h4 className="font-medium text-emerald-400 mb-2">{locale === 'fr' ? 'Durée Buffs' : 'Buff Duration'}</h4>
                    <code className="block text-xs text-emerald-400">{data.effect_system.buff_formula?.caster_bonus}</code>
                    <p className="text-xs text-zinc-400 mt-2">
                      Ex: {data.effect_system.buff_formula?.example}
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(data.effect_system.effect_categories).map(([key, cat]: [string, any]) => (
                    <Card key={key} className="bg-zinc-800/50">
                      <CardContent className="p-3">
                        <div className="font-medium text-sm">{cat.name}</div>
                        <div className="text-xs text-zinc-500 mt-1">
                          {cat.examples.join(', ')}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Damage Pipeline */}
          {data.damage_pipeline && (
            <Card className="mt-8 border-orange-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-400">
                  <span>⚔️</span> {locale === 'fr' ? 'Pipeline de Dégâts' : 'Damage Pipeline'}
                </CardTitle>
                <CardDescription>{data.damage_pipeline.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {data.damage_pipeline.steps.map((step: string, index: number) => (
                    <div key={index} className="flex items-start gap-3 p-2 bg-zinc-800/50 rounded">
                      <span className="text-orange-400 font-mono text-sm w-6">{index + 1}.</span>
                      <span className="text-sm text-zinc-300">{step.replace(/^\d+\.\s*/, '')}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Bonus Types Legend */}
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>{locale === 'fr' ? 'Types de bonus' : 'Bonus Types'}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400">flat + %</Badge>
                  <span className="text-zinc-400">{locale === 'fr' ? 'Supporte bonus flat ET pourcentage' : 'Supports flat AND percent bonuses'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="bg-sky-500/20 text-sky-400">flat</Badge>
                  <span className="text-zinc-400">{locale === 'fr' ? 'Bonus en points uniquement' : 'Flat points only'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="bg-violet-500/20 text-violet-400">%</Badge>
                  <span className="text-zinc-400">{locale === 'fr' ? 'Multiplicateur uniquement' : 'Multiplier only'}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
