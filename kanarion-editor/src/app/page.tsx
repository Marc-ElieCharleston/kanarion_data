'use client';

import { useTranslations } from 'next-intl';
import { StatCard } from '@/components/StatCard';
import { FeatureCard } from '@/components/FeatureCard';
import { Card, CardContent } from '@/components/ui/card';

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
          <StatCard
            key={stat.labelKey || stat.label}
            label={stat.labelKey ? tNav(stat.labelKey) : (stat.label || '')}
            value={stat.value}
            href={stat.href}
            icon={stat.icon}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <FeatureCard
          title={tNav('classes')}
          description={t('classesDesc')}
          icon="⚔️"
          href="/classes"
          linkText={t('exploreClasses')}
        />

        <FeatureCard
          title={t('combatSystem')}
          description={t('combatDesc')}
          icon="⚔️"
          href="/patterns"
          linkText="Voir les patterns"
        />

        <FeatureCard
          title="Panoplies"
          description="Ensembles d'équipements avec bonus de set"
          icon="✨"
          href="/panoplies"
          linkText="Voir les panoplies"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <FeatureCard
          title={tNav('statusEffects')}
          description="Buffs, debuffs, DoTs, HoTs et effets de contrôle"
          icon="💫"
          href="/effects"
          linkText="Voir les effets"
        />

        <FeatureCard
          title={tNav('statsReference')}
          description="Système de stats et mécaniques de combat"
          icon="📊"
          href="/stats"
          linkText="Voir les stats"
        />

        <FeatureCard
          title={tNav('lootTables')}
          description="Système de loot, rareté et multiplicateurs"
          icon="🎁"
          href="/loot"
          linkText="Voir le loot"
        />
      </div>
    </div>
  );
}
