'use client';

import Link from 'next/link';
import { useLocale } from '@/i18n/provider';
import { Card } from '@/components/ui/card';

const WIKI_SECTIONS = [
  {
    id: 'classes',
    icon: '⚔️',
    titleFr: 'Classes',
    titleEn: 'Classes',
    descFr: 'Découvrez les 6 classes et leurs spécialisations',
    descEn: 'Discover the 6 classes and their specializations',
    href: '/wiki/classes',
    color: 'border-violet-500/30 hover:border-violet-500/50',
    disabled: false,
  },
  {
    id: 'combat',
    icon: '💫',
    titleFr: 'Combat',
    titleEn: 'Combat',
    descFr: 'Status effects, types de dégâts, mécaniques',
    descEn: 'Status effects, damage types, mechanics',
    href: '/wiki/combat/status',
    color: 'border-purple-500/30 hover:border-purple-500/50',
    disabled: false,
  },
  {
    id: 'items',
    icon: '🎒',
    titleFr: 'Équipements',
    titleEn: 'Equipment',
    descFr: 'Armes, armures, sets et affixes',
    descEn: 'Weapons, armor, sets and affixes',
    href: '/wiki/items',
    color: 'border-amber-500/30 hover:border-amber-500/50',
    disabled: true,
  },
  {
    id: 'world',
    icon: '🗺️',
    titleFr: 'Monde',
    titleEn: 'World',
    descFr: 'Zones, monstres et donjons',
    descEn: 'Zones, monsters and dungeons',
    href: '/wiki/world',
    color: 'border-emerald-500/30 hover:border-emerald-500/50',
    disabled: true,
  },
];

export default function WikiHomePage() {
  const { locale } = useLocale();

  return (
    <div className="min-h-screen p-8">
      {/* Hero */}
      <div className="max-w-4xl mx-auto text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          {locale === 'fr' ? 'Guide de Kanarion Online' : 'Kanarion Online Guide'}
        </h1>
        <p className="text-zinc-400 text-lg">
          {locale === 'fr'
            ? 'Tout ce que vous devez savoir pour maîtriser le jeu'
            : 'Everything you need to know to master the game'}
        </p>
      </div>

      {/* Sections Grid */}
      <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
        {WIKI_SECTIONS.map((section) => (
          section.disabled ? (
            <Card
              key={section.id}
              className={`p-6 ${section.color} opacity-50 cursor-not-allowed`}
            >
              <div className="flex items-start gap-4">
                <span className="text-4xl">{section.icon}</span>
                <div>
                  <h2 className="text-xl font-semibold mb-2">
                    {locale === 'fr' ? section.titleFr : section.titleEn}
                  </h2>
                  <p className="text-zinc-400 text-sm">
                    {locale === 'fr' ? section.descFr : section.descEn}
                  </p>
                  <span className="inline-block mt-3 text-xs bg-zinc-800 text-zinc-500 px-2 py-1 rounded">
                    {locale === 'fr' ? 'Bientôt' : 'Coming soon'}
                  </span>
                </div>
              </div>
            </Card>
          ) : (
            <Link key={section.id} href={section.href}>
              <Card
                className={`p-6 ${section.color} transition-colors cursor-pointer h-full`}
              >
                <div className="flex items-start gap-4">
                  <span className="text-4xl">{section.icon}</span>
                  <div>
                    <h2 className="text-xl font-semibold mb-2">
                      {locale === 'fr' ? section.titleFr : section.titleEn}
                    </h2>
                    <p className="text-zinc-400 text-sm">
                      {locale === 'fr' ? section.descFr : section.descEn}
                    </p>
                  </div>
                </div>
              </Card>
            </Link>
          )
        ))}
      </div>

      {/* Quick Info */}
      <div className="max-w-4xl mx-auto mt-12 text-center">
        <p className="text-zinc-500 text-sm">
          {locale === 'fr'
            ? '🎮 Ce guide est en cours de construction. Plus de contenu arrive bientôt !'
            : '🎮 This guide is under construction. More content coming soon!'}
        </p>
      </div>
    </div>
  );
}
