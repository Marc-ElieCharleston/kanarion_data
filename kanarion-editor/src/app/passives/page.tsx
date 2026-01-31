'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingState } from '@/components/LoadingState';
import { Separator } from '@/components/ui/separator';

interface Passive {
  id: string;
  name_fr: string;
  name_en: string;
  max_level: number;
  description_fr: string;
  description_en: string;
  effects: Array<{
    stat: string;
    op: string;
    value_per_level: number;
  }>;
}

interface PassivesData {
  common: {
    _meta: {
      version: string;
      last_updated: string;
      description: string;
    };
    common_passives: Passive[];
  };
  classes: Record<string, {
    _meta: {
      version: string;
      last_updated: string;
      class: string;
      description: string;
    };
    class_passives: Passive[];
  }>;
}

const CLASS_COLORS: Record<string, string> = {
  warrior: 'bg-gradient-to-br from-red-600/20 to-red-900/20 border-red-500/30',
  mage: 'bg-gradient-to-br from-violet-600/20 to-violet-900/20 border-violet-500/30',
  healer: 'bg-gradient-to-br from-emerald-600/20 to-emerald-900/20 border-emerald-500/30',
  archer: 'bg-gradient-to-br from-amber-600/20 to-amber-900/20 border-amber-500/30',
  rogue: 'bg-gradient-to-br from-zinc-600/20 to-zinc-900/20 border-zinc-500/30',
  artisan: 'bg-gradient-to-br from-orange-600/20 to-orange-900/20 border-orange-500/30',
};

const CLASS_TEXT_COLORS: Record<string, string> = {
  warrior: 'text-red-400',
  mage: 'text-violet-400',
  healer: 'text-emerald-400',
  archer: 'text-amber-400',
  rogue: 'text-zinc-300',
  artisan: 'text-orange-400',
};

const CLASS_NAMES: Record<string, string> = {
  warrior: 'Warrior',
  mage: 'Mage',
  healer: 'Healer',
  archer: 'Archer',
  rogue: 'Rogue',
  artisan: 'Artisan',
};

export default function PassivesPage() {
  const [data, setData] = useState<PassivesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedView, setSelectedView] = useState<string>('common');
  const { locale } = useLocale();

  useEffect(() => {
    fetch('/api/passives')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  if (!data) {
    return <div className="p-8 text-center text-red-400">Erreur de chargement des passifs</div>;
  }

  const classes = ['warrior', 'mage', 'healer', 'archer', 'rogue', 'artisan'];

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-zinc-800 bg-zinc-900/50 overflow-y-auto p-4 space-y-4">
        <div className="space-y-2">
          <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider px-2">
            {locale === 'fr' ? 'Passifs' : 'Passives'}
          </div>

          {/* Common Passives Button */}
          <button
            onClick={() => setSelectedView('common')}
            className={`w-full text-left px-3 py-2 rounded transition-colors ${
              selectedView === 'common'
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'bg-zinc-800/30 text-zinc-400 hover:bg-zinc-800/50'
            }`}
          >
            <span className={selectedView === 'common' ? 'text-blue-400' : ''}>
              {locale === 'fr' ? 'Commun' : 'Common'}
            </span>
            <div className="text-xs text-zinc-500 mt-0.5">
              {data.common.common_passives.length} passifs
            </div>
          </button>

          <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider px-2 mt-4">
            {locale === 'fr' ? 'Classes' : 'Classes'}
          </div>

          {classes.map((className) => (
            <button
              key={className}
              onClick={() => setSelectedView(className)}
              className={`w-full text-left px-3 py-2 rounded transition-colors ${
                selectedView === className
                  ? `${CLASS_COLORS[className]} border`
                  : 'bg-zinc-800/30 text-zinc-400 hover:bg-zinc-800/50'
              }`}
            >
              <span className={selectedView === className ? CLASS_TEXT_COLORS[className] : ''}>
                {CLASS_NAMES[className]}
              </span>
              <div className="text-xs text-zinc-500 mt-0.5">
                {data.classes[className]?.class_passives?.length || 0} passifs
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold mb-2">
              {selectedView === 'common'
                ? (locale === 'fr' ? 'Passifs Communs' : 'Common Passives')
                : `${locale === 'fr' ? 'Passifs' : 'Passives'} - ${CLASS_NAMES[selectedView]}`
              }
            </h1>
            <p className="text-zinc-400">
              {selectedView === 'common'
                ? (locale === 'fr'
                    ? '10 passifs disponibles pour toutes les classes'
                    : '10 passives available for all classes')
                : (locale === 'fr'
                    ? `10 passifs spécifiques à la classe ${CLASS_NAMES[selectedView]}`
                    : `10 class-specific passives for ${CLASS_NAMES[selectedView]}`)
              }
            </p>
          </div>

          {/* Common Passives */}
          {selectedView === 'common' && (
          <div>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-2xl font-bold">
                {locale === 'fr' ? 'Passifs Communs' : 'Common Passives'}
              </h2>
              <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
                {data.common.common_passives.length} passifs
              </Badge>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.common.common_passives.map((passive) => (
                <Card key={passive.id} className="bg-zinc-900/50 border-zinc-800">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="text-blue-400">
                        {locale === 'fr' ? passive.name_fr : passive.name_en}
                      </span>
                      <Badge variant="secondary" className="bg-zinc-800">
                        Max: {passive.max_level}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm text-zinc-300">
                      {locale === 'fr' ? passive.description_fr : passive.description_en}
                    </p>
                    <div className="space-y-1">
                      {passive.effects.map((effect, idx) => (
                        <div key={idx} className="text-xs text-zinc-400 font-mono">
                          <span className="text-emerald-400">{effect.stat}</span>
                          {' '}
                          <span className="text-zinc-500">{effect.op}</span>
                          {' '}
                          <span className="text-amber-400">
                            {effect.value_per_level > 0 ? '+' : ''}
                            {effect.value_per_level}
                            {effect.op.includes('percent') ? '%' : ''}
                          </span>
                          <span className="text-zinc-500"> /niveau</span>
                        </div>
                      ))}
                    </div>
                    <div className="pt-2 border-t border-zinc-800 text-xs text-zinc-500">
                      Au niveau max: {' '}
                      {passive.effects.map((effect, idx) => (
                        <span key={idx} className="text-violet-400">
                          {idx > 0 && ', '}
                          {effect.value_per_level > 0 ? '+' : ''}
                          {(effect.value_per_level * passive.max_level).toFixed(1)}
                          {effect.op.includes('percent') ? '%' : ''} {effect.stat}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
          )}

          {/* Class-Specific Passives */}
          {selectedView !== 'common' && data.classes[selectedView] && (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.classes[selectedView].class_passives.map((passive) => (
                  <Card
                    key={passive.id}
                    className={`${CLASS_COLORS[selectedView]} border`}
                  >
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className={CLASS_TEXT_COLORS[selectedView]}>
                          {locale === 'fr' ? passive.name_fr : passive.name_en}
                        </span>
                        <Badge variant="secondary" className="bg-zinc-800">
                          Max: {passive.max_level}
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm text-zinc-300">
                        {locale === 'fr' ? passive.description_fr : passive.description_en}
                      </p>
                      <div className="space-y-1">
                        {passive.effects.map((effect, idx) => (
                          <div key={idx} className="text-xs text-zinc-400 font-mono">
                            <span className="text-emerald-400">{effect.stat}</span>
                            {' '}
                            <span className="text-zinc-500">{effect.op}</span>
                            {' '}
                            <span className="text-amber-400">
                              {effect.value_per_level > 0 ? '+' : ''}
                              {effect.value_per_level}
                              {effect.op.includes('percent') ? '%' : ''}
                            </span>
                            <span className="text-zinc-500"> /niveau</span>
                          </div>
                        ))}
                      </div>
                      <div className="pt-2 border-t border-zinc-800 text-xs text-zinc-500">
                        {locale === 'fr' ? 'Au niveau max:' : 'At max level:'} {' '}
                        {passive.effects.map((effect, idx) => (
                          <span key={idx} className={CLASS_TEXT_COLORS[selectedView]}>
                            {idx > 0 && ', '}
                            {effect.value_per_level > 0 ? '+' : ''}
                            {(effect.value_per_level * passive.max_level).toFixed(1)}
                            {effect.op.includes('percent') ? '%' : ''} {effect.stat}
                          </span>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
