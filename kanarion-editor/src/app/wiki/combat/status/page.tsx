'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { SecondarySidebar } from '@/components/SecondarySidebar';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  getStatusEffectsForPlayer,
  PlayerStatusCategory,
  PlayerStatusEffect,
  CATEGORY_COLORS,
} from '@/lib/playerData';

// Composant pour afficher un status effect
function StatusEffectCard({ effect, locale }: { effect: PlayerStatusEffect; locale: 'fr' | 'en' }) {
  return (
    <Card className="p-4 hover:border-zinc-600 transition-colors">
      <div className="flex items-start gap-3">
        <span className="text-2xl">{effect.icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold">{effect.name}</h3>
            <Badge
              variant="outline"
              className={effect.type === 'buff'
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-red-500/10 text-red-400 border-red-500/30'
              }
            >
              {effect.typeLabel}
            </Badge>
          </div>

          <p className="text-sm text-zinc-400 mb-3">{effect.description}</p>

          {/* Stacking Info */}
          <div className="bg-zinc-800/50 rounded p-2 mb-2">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-zinc-500">{locale === 'fr' ? 'Stacking:' : 'Stacking:'}</span>
              <Badge variant="secondary" className="text-xs">
                {effect.stacking.type}
                {effect.stacking.maxStacks && ` (max ${effect.stacking.maxStacks})`}
              </Badge>
            </div>
            <p className="text-xs text-zinc-500 mt-1">{effect.stacking.explanation}</p>
          </div>

          {/* Counters */}
          {effect.counters && effect.counters.length > 0 && (
            <div className="mt-2">
              <span className="text-xs text-zinc-500">
                {locale === 'fr' ? 'Contré par:' : 'Countered by:'}
              </span>
              <div className="flex flex-wrap gap-1 mt-1">
                {effect.counters.map((counter, idx) => (
                  <Badge key={idx} variant="outline" className="text-xs text-sky-400 border-sky-500/30">
                    {counter}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Sources */}
          {effect.sources && effect.sources.length > 0 && (
            <div className="mt-2">
              <span className="text-xs text-zinc-500">
                {locale === 'fr' ? 'Sources:' : 'Sources:'}
              </span>
              <span className="text-xs text-zinc-400 ml-1">
                {effect.sources.join(', ')}
              </span>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

export default function WikiStatusEffectsPage() {
  const { locale } = useLocale();
  const [categories, setCategories] = useState<PlayerStatusCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    Promise.all([
      fetch('/api/effects').then(r => r.json()),
    ]).then(([effectsData]) => {
      const statusEffectsData = effectsData.effects;
      const configData = effectsData.config;

      const playerCategories = getStatusEffectsForPlayer(
        statusEffectsData,
        configData,
        null,
        locale as 'fr' | 'en'
      );

      setCategories(playerCategories);
      setLoading(false);
    });
  }, [locale]);

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="text-zinc-500">
          {locale === 'fr' ? 'Chargement...' : 'Loading...'}
        </div>
      </div>
    );
  }

  // Filter effects
  const filteredCategories = categories.map(cat => ({
    ...cat,
    effects: cat.effects.filter(effect => {
      const matchesSearch = searchTerm === '' ||
        effect.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        effect.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = activeCategory === 'all' || cat.id === activeCategory;
      return matchesSearch && matchesCategory;
    })
  })).filter(cat => cat.effects.length > 0);

  const totalEffects = categories.reduce((sum, cat) => sum + cat.effects.length, 0);

  // Build navigation items
  const navItems = [
    {
      id: 'all',
      icon: '📋',
      label: locale === 'fr' ? 'Tous les effets' : 'All Effects',
      count: totalEffects,
      isActive: activeCategory === 'all',
      onClick: () => setActiveCategory('all'),
    },
    ...categories.map(cat => ({
      id: cat.id,
      icon: cat.icon,
      label: cat.name,
      count: cat.effects.length,
      isActive: activeCategory === cat.id,
      onClick: () => setActiveCategory(cat.id),
    })),
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      <SecondarySidebar
        title={locale === 'fr' ? 'Status Effects' : 'Status Effects'}
        subtitle={`${totalEffects} ${locale === 'fr' ? 'effets' : 'effects'}`}
        showSearch
        searchValue={searchTerm}
        onSearchChange={setSearchTerm}
        searchPlaceholder={locale === 'fr' ? 'Rechercher...' : 'Search...'}
        navItems={navItems}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {/* Quick Info Box */}
          <Card className="p-4 mb-6 border-blue-500/30 bg-blue-500/5">
            <h3 className="font-semibold text-blue-400 mb-2 flex items-center gap-2">
              <span>💡</span>
              {locale === 'fr' ? 'Comment ça marche ?' : 'How does it work?'}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-zinc-400">
              <div>
                <span className="text-emerald-400 font-medium">Buffs</span>
                <p>{locale === 'fr' ? 'Effets positifs qui améliorent vos stats' : 'Positive effects that improve your stats'}</p>
              </div>
              <div>
                <span className="text-red-400 font-medium">Debuffs</span>
                <p>{locale === 'fr' ? 'Effets négatifs infligés aux ennemis' : 'Negative effects inflicted on enemies'}</p>
              </div>
              <div>
                <span className="text-purple-400 font-medium">Stacking</span>
                <p>{locale === 'fr' ? '+10% par stack, max 10 stacks = +100%' : '+10% per stack, max 10 stacks = +100%'}</p>
              </div>
            </div>
          </Card>

          {/* Resistance Info */}
          <Card className="p-4 mb-6 border-amber-500/30 bg-amber-500/5">
            <h3 className="font-semibold text-amber-400 mb-2 flex items-center gap-2">
              <span>🛡️</span>
              {locale === 'fr' ? 'Comment résister ?' : 'How to resist?'}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-zinc-400">
              <div>
                <span className="text-sky-400 font-medium">
                  {locale === 'fr' ? 'Résistance aux Effets' : 'Effect Resistance'}
                </span>
                <p>{locale === 'fr' ? 'Chance de résister complètement à un debuff/CC' : 'Chance to completely resist a debuff/CC'}</p>
              </div>
              <div>
                <span className="text-sky-400 font-medium">
                  {locale === 'fr' ? 'Ténacité' : 'Tenacity'}
                </span>
                <p>{locale === 'fr' ? 'Réduit la durée des debuffs/CC reçus' : 'Reduces duration of debuffs/CC received'}</p>
              </div>
            </div>
          </Card>

          {/* Effects by Category */}
          <div className="space-y-8">
            {filteredCategories.map(category => (
              <div key={category.id}>
                <h2 className={`text-lg font-semibold mb-4 flex items-center gap-2 ${CATEGORY_COLORS[category.id]?.split(' ')[0]}`}>
                  <span>{category.icon}</span>
                  <span>{category.name}</span>
                  <span className="text-zinc-600 text-sm font-normal">({category.effects.length})</span>
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {category.effects.map(effect => (
                    <StatusEffectCard
                      key={effect.id}
                      effect={effect}
                      locale={locale as 'fr' | 'en'}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* No results */}
          {filteredCategories.length === 0 && (
            <div className="text-center text-zinc-500 py-12">
              {locale === 'fr' ? 'Aucun effet trouvé' : 'No effects found'}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
