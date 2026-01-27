'use client';

import Link from 'next/link';
import { useTranslations } from 'next-intl';

export default function Home() {
  const t = useTranslations('home');
  const tNav = useTranslations('nav');

  const stats = [
    { labelKey: 'classes', value: '6', href: '/classes', icon: '⚔️' },
    { label: 'Subclasses', value: '24', href: '/classes', icon: '🎭' },
    { label: 'Skills', value: '100+', href: '/classes', icon: '✨' },
    { labelKey: 'monsters', value: '50+', href: '/monsters', icon: '👹' },
    { label: 'Zones', value: '10', href: '/world', icon: '🗺️' },
    { labelKey: 'items', value: '200+', href: '/items', icon: '🎒' },
  ];

  return (
    <div className="p-4 md:p-6 lg:p-8">
      <div className="mb-6 md:mb-8">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">{t('title')}</h1>
        <p className="text-zinc-400">
          {t('subtitle')}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {stats.map((stat) => (
          <Link
            key={stat.labelKey || stat.label}
            href={stat.href}
            className="bg-zinc-900 p-4 rounded-lg border border-zinc-800 hover:border-zinc-600 transition-colors"
          >
            <div className="text-2xl mb-2">{stat.icon}</div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
            <div className="text-sm text-zinc-500">
              {stat.labelKey ? tNav(stat.labelKey) : stat.label}
            </div>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>⚔️</span> {tNav('classes')}
          </h2>
          <p className="text-zinc-400 text-sm mb-4">
            {t('classesDesc')}
          </p>
          <Link
            href="/classes"
            className="inline-flex items-center gap-2 text-violet-400 hover:text-violet-300"
          >
            {t('exploreClasses')} →
          </Link>
        </div>

        <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>📊</span> {t('combatSystem')}
          </h2>
          <p className="text-zinc-400 text-sm mb-4">
            {t('combatDesc')}
          </p>
          <div className="text-zinc-500 text-sm">{t('comingSoon')}</div>
        </div>
      </div>

      <div className="mt-8 p-4 bg-zinc-900/50 rounded-lg border border-zinc-800">
        <div className="flex items-center gap-2 text-sm text-zinc-500">
          <span>📁</span>
          <span>{t('databasePath')}:</span>
          <code className="bg-zinc-800 px-2 py-0.5 rounded text-zinc-400">
            ../kanarion_database/
          </code>
        </div>
      </div>
    </div>
  );
}
