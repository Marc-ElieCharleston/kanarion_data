'use client';

import { useEffect, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { SecondarySidebar } from '@/components/SecondarySidebar';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  getClassesForPlayer,
  PlayerClass,
  DIFFICULTY_COLORS,
  CLASS_ICONS,
} from '@/lib/playerData';

// Composant pour afficher une subclass
function SubclassCard({ subclass, locale }: { subclass: PlayerClass['subclasses'][0]; locale: 'fr' | 'en' }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-zinc-800/50 rounded-lg p-3 hover:bg-zinc-800 transition-colors">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left"
      >
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-white">{subclass.name}</h4>
            <p className="text-xs text-zinc-400 italic">{subclass.tagline}</p>
          </div>
          <svg
            className={`w-4 h-4 text-zinc-500 transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-zinc-700 space-y-3">
          <p className="text-sm text-zinc-300">{subclass.description}</p>

          {subclass.lore && (
            <p className="text-xs text-zinc-500 italic border-l-2 border-zinc-700 pl-3">
              {subclass.lore}
            </p>
          )}

          {subclass.tier3 && subclass.tier3.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-zinc-500 mb-1">
                {locale === 'fr' ? 'Spécialisations Tier 3:' : 'Tier 3 Specializations:'}
              </p>
              <div className="flex flex-wrap gap-2">
                {subclass.tier3.map(t3 => (
                  <Badge key={t3.id} variant="outline" className="text-xs">
                    {t3.id.replace(/_/g, ' ')}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Composant pour afficher une classe complete
function ClassDetail({ cls, locale }: { cls: PlayerClass; locale: 'fr' | 'en' }) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="overflow-hidden">
        <div className="p-6 border-b border-zinc-800 bg-gradient-to-r from-zinc-900 to-zinc-800">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-4">
              <span className="text-5xl">{cls.icon}</span>
              <div>
                <h2 className="text-2xl font-bold text-white">{cls.name}</h2>
                <p className="text-zinc-400 italic">{cls.tagline}</p>
              </div>
            </div>
            <div className="flex flex-col gap-2 items-end">
              <Badge variant="secondary" className="text-xs">
                {cls.roleLabel}
              </Badge>
              <Badge variant="outline" className={`text-xs ${DIFFICULTY_COLORS[cls.difficulty]}`}>
                {cls.difficultyLabel}
              </Badge>
            </div>
          </div>

          <p className="text-zinc-300">{cls.description}</p>
        </div>

        {/* Wiki Intro */}
        <div className="p-6 border-b border-zinc-800">
          <p className="text-sm text-zinc-400 leading-relaxed">{cls.wikiIntro}</p>
        </div>

        {/* Lore */}
        {cls.lore && (
          <div className="px-6 py-4 bg-zinc-900/50 border-b border-zinc-800">
            <p className="text-xs text-zinc-500 italic border-l-2 border-violet-500/50 pl-3">
              &ldquo;{cls.lore}&rdquo;
            </p>
          </div>
        )}

        {/* Playstyle Tips */}
        {cls.playstyleTips && cls.playstyleTips.length > 0 && (
          <div className="p-6">
            <h3 className="text-sm font-semibold text-amber-400 mb-3 flex items-center gap-2">
              <span>💡</span>
              {locale === 'fr' ? 'Conseils de jeu' : 'Playstyle Tips'}
            </h3>
            <ul className="space-y-2">
              {cls.playstyleTips.map((tip, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-zinc-400">
                  <span className="text-emerald-400 mt-0.5">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </Card>

      {/* Subclasses */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-violet-400 mb-4 flex items-center gap-2">
          <span>⚔️</span>
          {locale === 'fr' ? 'Spécialisations' : 'Specializations'}
          <span className="text-zinc-500 font-normal text-sm">({cls.subclasses.length})</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {cls.subclasses.map(sub => (
            <SubclassCard key={sub.id} subclass={sub} locale={locale} />
          ))}
        </div>
      </Card>
    </div>
  );
}

// Composant aperçu de toutes les classes
function AllClassesOverview({ classes, locale, onSelectClass }: {
  classes: PlayerClass[];
  locale: 'fr' | 'en';
  onSelectClass: (id: string) => void;
}) {
  return (
    <div className="space-y-6">
      {/* Quick Role Overview */}
      <Card className="p-6 border-blue-500/30 bg-blue-500/5">
        <h3 className="font-semibold text-blue-400 mb-4 flex items-center gap-2">
          <span>📋</span>
          {locale === 'fr' ? 'Rôles en équipe' : 'Team Roles'}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <span className="text-sky-400 font-medium">🛡️ Tank</span>
            <p className="text-sm text-zinc-400">{locale === 'fr' ? 'Warrior - Protège l\'équipe' : 'Warrior - Protects the team'}</p>
          </div>
          <div>
            <span className="text-red-400 font-medium">⚔️ DPS Mêlée</span>
            <p className="text-sm text-zinc-400">{locale === 'fr' ? 'Rogue - Élimine les cibles' : 'Rogue - Eliminates targets'}</p>
          </div>
          <div>
            <span className="text-orange-400 font-medium">🏹 DPS Distance</span>
            <p className="text-sm text-zinc-400">{locale === 'fr' ? 'Archer - Pression constante' : 'Archer - Constant pressure'}</p>
          </div>
          <div>
            <span className="text-violet-400 font-medium">🔮 DPS Magique</span>
            <p className="text-sm text-zinc-400">{locale === 'fr' ? 'Mage - Dégâts massifs' : 'Mage - Massive damage'}</p>
          </div>
          <div>
            <span className="text-emerald-400 font-medium">💚 Healer</span>
            <p className="text-sm text-zinc-400">{locale === 'fr' ? 'Healer - Maintient en vie' : 'Healer - Keeps alive'}</p>
          </div>
          <div>
            <span className="text-amber-400 font-medium">🔧 Support</span>
            <p className="text-sm text-zinc-400">{locale === 'fr' ? 'Artisan - Prépare le terrain' : 'Artisan - Sets up plays'}</p>
          </div>
        </div>
      </Card>

      {/* Classes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {classes.map(cls => (
          <Card
            key={cls.id}
            className="p-4 hover:border-zinc-600 transition-colors cursor-pointer"
            onClick={() => onSelectClass(cls.id)}
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="text-3xl">{cls.icon}</span>
              <div>
                <h3 className="font-semibold text-white">{cls.name}</h3>
                <p className="text-xs text-zinc-400">{cls.roleLabel}</p>
              </div>
            </div>
            <p className="text-sm text-zinc-400 mb-3 line-clamp-2">{cls.description}</p>
            <div className="flex items-center justify-between">
              <Badge variant="outline" className={`text-xs ${DIFFICULTY_COLORS[cls.difficulty]}`}>
                {cls.difficultyLabel}
              </Badge>
              <span className="text-xs text-zinc-500">{cls.subclasses.length} specs</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default function WikiClassesPage() {
  const { locale } = useLocale();
  const [classes, setClasses] = useState<PlayerClass[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedClass, setSelectedClass] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/classes')
      .then(r => r.json())
      .then(data => {
        const playerClasses = getClassesForPlayer(data, locale as 'fr' | 'en');
        setClasses(playerClasses);
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

  // Build navigation items for SecondarySidebar
  const navItems = [
    {
      id: 'all',
      icon: '📋',
      label: locale === 'fr' ? 'Aperçu' : 'Overview',
      isActive: selectedClass === null,
      onClick: () => setSelectedClass(null),
    },
    ...classes.map(cls => ({
      id: cls.id,
      icon: cls.icon,
      label: cls.name,
      subtitle: cls.roleLabel,
      isActive: selectedClass === cls.id,
      onClick: () => setSelectedClass(cls.id),
    })),
  ];

  const selectedClassData = selectedClass
    ? classes.find(c => c.id === selectedClass)
    : null;

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      <SecondarySidebar
        title={locale === 'fr' ? 'Classes' : 'Classes'}
        subtitle={`6 classes • 24 specs`}
        navItems={navItems}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 lg:p-8">
          {selectedClassData ? (
            <ClassDetail cls={selectedClassData} locale={locale as 'fr' | 'en'} />
          ) : (
            <AllClassesOverview
              classes={classes}
              locale={locale as 'fr' | 'en'}
              onSelectClass={setSelectedClass}
            />
          )}
        </div>
      </main>
    </div>
  );
}
