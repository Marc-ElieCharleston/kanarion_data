'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useLocale } from '@/i18n/provider';
import { useViewMode } from '@/contexts/ViewModeContext';

// Navigation Dev (structure groupée par catégorie)
const DEV_NAV_GROUPS = [
  {
    id: 'main',
    items: [
      { nameKey: 'dashboard', href: '/', icon: '🏠' },
    ]
  },
  {
    id: 'skills',
    labelKey: 'skillsAbilities',
    items: [
      { nameKey: 'classes', href: '/classes', icon: '⚔️' },
      { nameKey: 'skills', href: '/skills', icon: '✨' },
      { nameKey: 'passives', href: '/passives', icon: '🌟' },
    ]
  },
  {
    id: 'stats',
    labelKey: 'statsEffects',
    items: [
      { nameKey: 'statsReference', href: '/stats', icon: '📊' },
      { nameKey: 'statusEffects', href: '/effects', icon: '💫' },
    ]
  },
  {
    id: 'combat',
    labelKey: 'combat',
    items: [
      { nameKey: 'patterns', href: '/patterns', icon: '🎯' },
    ]
  },
  {
    id: 'entities',
    labelKey: 'entities',
    items: [
      { nameKey: 'monsters', href: '/monsters', icon: '👹' },
    ]
  },
  {
    id: 'items',
    labelKey: 'items',
    items: [
      { nameKey: 'items', href: '/items', icon: '🎒' },
      { nameKey: 'panoplies', href: '/panoplies', icon: '👕' },
      { nameKey: 'equipmentStats', href: '/equipment-stats', icon: '🛡️' },
      { nameKey: 'lootTables', href: '/loot', icon: '🎁' },
    ]
  },
  {
    id: 'world',
    labelKey: 'world',
    items: [
      { nameKey: 'world', href: '/world', icon: '🗺️' },
      { nameKey: 'npcs', href: '/npcs', icon: '🧑‍🤝‍🧑' },
    ]
  },
  {
    id: 'systems',
    labelKey: 'systems',
    items: [
      { nameKey: 'systems', href: '/systems', icon: '⚙️' },
      { nameKey: 'config', href: '/config', icon: '📖' },
    ]
  },
  {
    id: 'meta',
    labelKey: 'ideasMeta',
    items: [
      { nameKey: 'ideas', href: '/ideas', icon: '💡' },
    ]
  },
];

// Navigation Player (wiki simplifié - pages composées)
const PLAYER_NAV_GROUPS = [
  {
    id: 'main',
    items: [
      { name: 'Accueil', nameKey: 'home', href: '/wiki', icon: '🏠' },
    ]
  },
  {
    id: 'classes',
    label: 'Classes',
    items: [
      { name: 'Toutes les Classes', nameKey: 'allClasses', href: '/wiki/classes', icon: '⚔️' },
    ]
  },
  {
    id: 'combat',
    label: 'Combat',
    items: [
      { name: 'Status Effects', nameKey: 'statusEffects', href: '/wiki/combat/status', icon: '💫' },
      { name: 'Types de Dégâts', nameKey: 'damageTypes', href: '/wiki/combat/damage', icon: '⚔️', disabled: true },
      { name: 'Patterns & Zones', nameKey: 'patterns', href: '/wiki/combat/patterns', icon: '🎯', disabled: true },
    ]
  },
  {
    id: 'items',
    label: 'Équipements',
    items: [
      { name: 'Équipements', nameKey: 'equipment', href: '/wiki/items/equipment', icon: '🎒', disabled: true },
      { name: 'Sets (Panoplies)', nameKey: 'sets', href: '/wiki/items/sets', icon: '👕', disabled: true },
    ]
  },
  {
    id: 'world',
    label: 'Monde',
    items: [
      { name: 'Monstres & Boss', nameKey: 'monsters', href: '/wiki/world/monsters', icon: '👹', disabled: true },
      { name: 'Zones', nameKey: 'zones', href: '/wiki/world/zones', icon: '🗺️', disabled: true },
    ]
  },
];

const CLASSES = [
  {
    id: 'warrior',
    name: 'Warrior',
    icon: '🗡️',
    subclasses: [
      { id: 'berserker', name: 'Berserker' },
      { id: 'guardian', name: 'Guardian' },
      { id: 'duelist', name: 'Duelist' },
      { id: 'knight', name: 'Knight' }
    ]
  },
  {
    id: 'mage',
    name: 'Mage',
    icon: '🔮',
    subclasses: [
      { id: 'elementalist', name: 'Elementalist' },
      { id: 'occultist', name: 'Occultist' },
      { id: 'chronomancer', name: 'Chronomancer' },
      { id: 'arcanist', name: 'Arcanist' }
    ]
  },
  {
    id: 'healer',
    name: 'Healer',
    icon: '💚',
    subclasses: [
      { id: 'priest', name: 'Priest' },
      { id: 'druid', name: 'Druid' },
      { id: 'shaman', name: 'Shaman' },
      { id: 'monk', name: 'Monk' }
    ]
  },
  {
    id: 'archer',
    name: 'Archer',
    icon: '🏹',
    subclasses: [
      { id: 'ranger', name: 'Ranger' },
      { id: 'sniper', name: 'Sniper' },
      { id: 'trapper', name: 'Trapper' },
      { id: 'beastmaster', name: 'Beastmaster' }
    ]
  },
  {
    id: 'rogue',
    name: 'Rogue',
    icon: '🗡️',
    subclasses: [
      { id: 'assassin', name: 'Assassin' },
      { id: 'shadowblade', name: 'Shadowblade' },
      { id: 'trickster', name: 'Trickster' },
      { id: 'bounty_hunter', name: 'Bounty Hunter' }
    ]
  },
  {
    id: 'artisan',
    name: 'Artisan',
    icon: '🔧',
    subclasses: [
      { id: 'alchemist', name: 'Alchemist' },
      { id: 'engineer', name: 'Engineer' },
      { id: 'runesmith', name: 'Runesmith' },
      { id: 'enchanter', name: 'Enchanter' }
    ]
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [expandedClasses, setExpandedClasses] = useState<string[]>([]);
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['main', 'classes', 'combat', 'items', 'world']);
  const t = useTranslations('nav');
  const tCommon = useTranslations('common');
  const { locale, setLocale } = useLocale();
  const { viewMode, setViewMode, isDev, isPlayer } = useViewMode();

  const toggleClass = (classId: string) => {
    setExpandedClasses(prev =>
      prev.includes(classId)
        ? prev.filter(id => id !== classId)
        : [...prev, classId]
    );
  };

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  // Close sidebar on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  // Prevent body scroll when sidebar is open on mobile
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const toggleLocale = () => {
    setLocale(locale === 'fr' ? 'en' : 'fr');
  };

  return (
    <>
      {/* Mobile hamburger button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-zinc-800 rounded-lg border border-zinc-700 hover:bg-zinc-700 transition-colors"
        aria-label="Toggle menu"
      >
        <svg
          className="w-6 h-6 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          {isOpen ? (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          ) : (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          )}
        </svg>
      </button>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:sticky top-0 left-0 z-40 h-screen
          w-64 bg-zinc-900 border-r border-zinc-800 overflow-y-auto
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="p-4 border-b border-zinc-800">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-xl font-bold text-white">KanarionDB</h1>
            <button
              onClick={toggleLocale}
              className="flex items-center gap-1.5 px-2.5 py-1.5 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 hover:border-zinc-600 rounded-lg transition-colors"
              title={locale === 'fr' ? 'Switch to English' : 'Passer en Français'}
            >
              <span className="text-lg">{locale === 'fr' ? '🇫🇷' : '🇬🇧'}</span>
              <span className="text-zinc-300 text-sm font-medium">{locale.toUpperCase()}</span>
            </button>
          </div>

          {/* View Mode Toggle */}
          <div className="flex gap-1 p-1 bg-zinc-800 rounded-lg mb-2">
            <button
              onClick={() => setViewMode('dev')}
              className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                isDev
                  ? 'bg-violet-600 text-white'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-700'
              }`}
            >
              <span>🔧</span>
              <span>Dev</span>
            </button>
            <button
              onClick={() => setViewMode('player')}
              className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                isPlayer
                  ? 'bg-emerald-600 text-white'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-700'
              }`}
            >
              <span>🎮</span>
              <span>Player</span>
            </button>
          </div>

          <p className="text-xs text-zinc-500">
            {isDev ? 'Database Editor v0.9' : 'Wiki / Guide'}
          </p>
        </div>

        <nav className="p-2 flex-1 overflow-y-auto">
          {/* DEV MODE NAVIGATION */}
          {isDev && DEV_NAV_GROUPS.map((group) => (
            <div key={group.id} className="mb-2">
              {group.labelKey && (
                <div className="px-3 py-2 text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                  {t(group.labelKey)}
                </div>
              )}
              {group.items.map((item) => (
                <div key={item.href}>
                  {'disabled' in item && item.disabled ? (
                    <div className="flex items-center gap-3 px-3 py-2 text-zinc-600 cursor-not-allowed">
                      <span>{item.icon}</span>
                      <span>{t(item.nameKey)}</span>
                      <span className="text-[10px] bg-zinc-800 px-1.5 py-0.5 rounded ml-auto">{tCommon('soon')}</span>
                    </div>
                  ) : (
                    <Link
                      href={item.href}
                      className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                        pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href + '/'))
                          ? 'bg-violet-600/20 text-violet-400 border border-violet-500/30'
                          : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
                      }`}
                    >
                      <span>{item.icon}</span>
                      <span>{t(item.nameKey)}</span>
                    </Link>
                  )}

                  {item.href === '/classes' && pathname.startsWith('/classes') && (
                    <div className="ml-2 mt-1 space-y-0.5">
                      {CLASSES.map((cls) => (
                        <div key={cls.id}>
                          <div className="flex items-center">
                            <button
                              onClick={() => toggleClass(cls.id)}
                              className="p-1 hover:bg-zinc-800 rounded transition-colors"
                            >
                              <svg
                                className={`w-3 h-3 text-zinc-500 transition-transform ${
                                  expandedClasses.includes(cls.id) ? 'rotate-90' : ''
                                }`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                              </svg>
                            </button>
                            <Link
                              href={`/classes/${cls.id}`}
                              className={`flex-1 flex items-center gap-2 px-2 py-1.5 text-sm rounded-lg transition-colors ${
                                pathname === `/classes/${cls.id}`
                                  ? 'bg-zinc-700 text-white'
                                  : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-300'
                              }`}
                            >
                              <span>{cls.icon}</span>
                              <span>{cls.name}</span>
                            </Link>
                          </div>
                          {expandedClasses.includes(cls.id) && (
                            <div className="ml-8 space-y-0.5 mt-0.5">
                              {cls.subclasses.map((subclass) => (
                                <Link
                                  key={subclass.id}
                                  href={`/classes/${cls.id}#${subclass.id}`}
                                  className={`block px-3 py-1 text-xs rounded-lg transition-colors ${
                                    pathname.includes(subclass.id)
                                      ? 'bg-zinc-700/50 text-violet-300'
                                      : 'text-zinc-500 hover:bg-zinc-800/30 hover:text-zinc-400'
                                  }`}
                                >
                                  {subclass.name}
                                </Link>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))}

          {/* PLAYER MODE NAVIGATION */}
          {isPlayer && PLAYER_NAV_GROUPS.map((group) => (
            <div key={group.id} className="mb-2">
              {group.label && (
                <div className="px-3 py-2 text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                  {group.label}
                </div>
              )}
              {group.items.map((item) => (
                'disabled' in item && item.disabled ? (
                  <div
                    key={item.href}
                    className="flex items-center gap-3 px-3 py-2 text-zinc-600 cursor-not-allowed"
                  >
                    <span>{item.icon}</span>
                    <span>{item.name}</span>
                    <span className="text-[10px] bg-zinc-800 px-1.5 py-0.5 rounded ml-auto">{tCommon('soon')}</span>
                  </div>
                ) : (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                      pathname === item.href || pathname.startsWith(item.href + '/')
                        ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                        : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
                    }`}
                  >
                    <span>{item.icon}</span>
                    <span>{item.name}</span>
                  </Link>
                )
              ))}
            </div>
          ))}
        </nav>

      </aside>
    </>
  );
}
