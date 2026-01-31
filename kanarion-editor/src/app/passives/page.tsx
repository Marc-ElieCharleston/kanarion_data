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

interface Keystone {
  id: string;
  name_fr: string;
  name_en: string;
  type: 'dps' | 'tank' | 'support' | 'control';
  description_fr: string;
  description_en: string;
  effects: Record<string, any>;
}

interface KeystonesData {
  _meta: {
    version: string;
    last_updated: string;
    description: string;
  };
  rules: {
    max_active_keystones: number;
    has_levels: boolean;
    design_notes: string[];
  };
  common_keystones: Keystone[];
  class_keystones: Record<string, Keystone[]>;
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
  keystones: KeystonesData;
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
  const [activeTab, setActiveTab] = useState<'passives' | 'keystones'>('passives');
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
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-zinc-800 bg-zinc-900/50 overflow-y-auto p-4 space-y-4">
        {/* Tab Selection */}
        <div className="space-y-2">
          <button
            onClick={() => { setActiveTab('passives'); setSelectedView('common'); }}
            className={`w-full px-3 py-2 rounded transition-colors ${
              activeTab === 'passives'
                ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30'
                : 'bg-zinc-800/30 text-zinc-400 hover:bg-zinc-800/50'
            }`}
          >
            {locale === 'fr' ? '📚 Passifs' : '📚 Passives'}
          </button>
          <button
            onClick={() => { setActiveTab('keystones'); setSelectedView('warrior'); }}
            className={`w-full px-3 py-2 rounded transition-colors ${
              activeTab === 'keystones'
                ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30'
                : 'bg-zinc-800/30 text-zinc-400 hover:bg-zinc-800/50'
            }`}
          >
            {locale === 'fr' ? '💎 Keystones' : '💎 Keystones'}
          </button>
        </div>

        <Separator />

        {/* Passives Tab Content */}
        {activeTab === 'passives' && (
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
        )}

        {/* Keystones Tab Content */}
        {activeTab === 'keystones' && (
          <div className="space-y-2">
            <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider px-2">
              Keystones
            </div>

            {/* Common Keystones Button */}
            <button
              onClick={() => setSelectedView('common')}
              className={`w-full text-left px-3 py-2 rounded transition-colors ${
                selectedView === 'common'
                  ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                  : 'bg-zinc-800/30 text-zinc-400 hover:bg-zinc-800/50'
              }`}
            >
              <span className={selectedView === 'common' ? 'text-purple-400' : ''}>
                {locale === 'fr' ? 'Commun' : 'Common'}
              </span>
              <div className="text-xs text-zinc-500 mt-0.5">
                {data.keystones.common_keystones.length} keystones
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
                  {data.keystones.class_keystones[className]?.length || 0} keystones
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header for Passives */}
          {activeTab === 'passives' && (
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
          )}

          {/* Header for Keystones */}
          {activeTab === 'keystones' && (
            <div>
              <h1 className="text-3xl font-bold mb-2">
                {selectedView === 'common'
                  ? `Keystones ${locale === 'fr' ? 'Communs' : 'Common'}`
                  : `Keystones - ${CLASS_NAMES[selectedView]}`
                }
              </h1>
              <div className="space-y-2">
                <p className="text-zinc-400">
                  {locale === 'fr'
                    ? 'Choix unique parmi plusieurs options qui changent radicalement votre gameplay'
                    : 'Unique choice among multiple options that radically change your gameplay'}
                </p>
                <div className="flex gap-4 text-sm">
                  <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-amber-500/30">
                    {locale === 'fr' ? '1 seul actif' : 'Only 1 active'}
                  </Badge>
                  <Badge variant="outline" className="bg-purple-500/10 text-purple-400 border-purple-500/30">
                    {locale === 'fr' ? 'Pas de niveaux' : 'No levels'}
                  </Badge>
                  <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
                    {locale === 'fr' ? 'Effets radicaux' : 'Radical effects'}
                  </Badge>
                </div>
              </div>
            </div>
          )}

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

          {/* Common Keystones Display */}
          {activeTab === 'keystones' && selectedView === 'common' && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <h2 className="text-2xl font-bold text-purple-400">
                  {locale === 'fr' ? 'Keystones Communs' : 'Common Keystones'}
                </h2>
                <Badge variant="outline" className="bg-purple-500/10 text-purple-400 border-purple-500/30">
                  {data.keystones.common_keystones.length} keystones
                </Badge>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.keystones.common_keystones.map((keystone) => {
                  const typeColors = {
                    dps: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
                    tank: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30' },
                    support: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' },
                    control: { bg: 'bg-violet-500/10', text: 'text-violet-400', border: 'border-violet-500/30' }
                  };
                  const color = typeColors[keystone.type];

                  return (
                    <Card key={keystone.id} className={`${color.bg} border ${color.border}`}>
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          <span className={color.text}>
                            {locale === 'fr' ? keystone.name_fr : keystone.name_en}
                          </span>
                          <Badge variant="outline" className={`${color.bg} ${color.text} ${color.border}`}>
                            {keystone.type.toUpperCase()}
                          </Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-zinc-300">
                          {locale === 'fr' ? keystone.description_fr : keystone.description_en}
                        </p>
                        <div className="pt-2 border-t border-zinc-700">
                          <div className="text-xs text-zinc-500 font-mono">
                            ID: {keystone.id}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}

          {/* Class Keystones Display */}
          {activeTab === 'keystones' && selectedView !== 'common' && (
            <div>
              {data.keystones.class_keystones[selectedView]?.length > 0 ? (
                <>
                  <div className="flex items-center gap-3 mb-4">
                    <h2 className="text-2xl font-bold">
                      Keystones - <span className={CLASS_TEXT_COLORS[selectedView]}>{CLASS_NAMES[selectedView]}</span>
                    </h2>
                    <Badge variant="outline" className={`${CLASS_COLORS[selectedView]} border`}>
                      {data.keystones.class_keystones[selectedView].length} keystones
                    </Badge>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {data.keystones.class_keystones[selectedView].map((keystone) => {
                      const typeColors = {
                        dps: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
                        tank: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30' },
                        support: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' },
                        control: { bg: 'bg-violet-500/10', text: 'text-violet-400', border: 'border-violet-500/30' }
                      };
                      const color = typeColors[keystone.type];

                      return (
                        <Card key={keystone.id} className={`${CLASS_COLORS[selectedView]} border`}>
                          <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                              <span className={CLASS_TEXT_COLORS[selectedView]}>
                                {locale === 'fr' ? keystone.name_fr : keystone.name_en}
                              </span>
                              <Badge variant="outline" className={`${color.bg} ${color.text} ${color.border}`}>
                                {keystone.type.toUpperCase()}
                              </Badge>
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-3">
                            <p className="text-sm text-zinc-300">
                              {locale === 'fr' ? keystone.description_fr : keystone.description_en}
                            </p>
                            <div className="pt-2 border-t border-zinc-700">
                              <div className="text-xs text-zinc-500 font-mono">
                                ID: {keystone.id}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </>
              ) : (
                <Card className="bg-zinc-900/50 border-zinc-800">
                  <CardContent className="p-8 text-center">
                    <p className="text-zinc-400">
                      {locale === 'fr'
                        ? `Aucun keystone spécifique à la classe ${CLASS_NAMES[selectedView]} pour le moment.`
                        : `No class-specific keystones for ${CLASS_NAMES[selectedView]} yet.`}
                    </p>
                    <p className="text-zinc-500 text-sm mt-2">
                      {locale === 'fr'
                        ? 'Les keystones de classe seront ajoutés prochainement.'
                        : 'Class keystones will be added soon.'}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
