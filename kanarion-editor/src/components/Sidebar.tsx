'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useLocale } from '@/i18n/provider';

const NAV_ITEMS = [
  { nameKey: 'dashboard', href: '/', icon: '🏠' },
  { nameKey: 'classes', href: '/classes', icon: '⚔️' },
  { nameKey: 'skills', href: '/skills', icon: '✨' },
  { nameKey: 'statsReference', href: '/stats', icon: '📊' },
  { nameKey: 'statusEffects', href: '/effects', icon: '💫' },
  { nameKey: 'patterns', href: '/patterns', icon: '🎯' },
  { nameKey: 'panoplies', href: '/panoplies', icon: '👕' },
  { nameKey: 'equipmentStats', href: '/equipment-stats', icon: '⚔️' },
  { nameKey: 'lootTables', href: '/loot', icon: '🎁' },
  { nameKey: 'monsters', href: '/monsters', icon: '👹', disabled: true },
  { nameKey: 'items', href: '/items', icon: '🎒', disabled: true },
  { nameKey: 'world', href: '/world', icon: '🗺️', disabled: true },
  { nameKey: 'systems', href: '/systems', icon: '⚙️' },
  { nameKey: 'ideas', href: '/ideas', icon: '💡' },
];

const CLASSES = [
  { id: 'warrior', name: 'Warrior', icon: '🗡️' },
  { id: 'mage', name: 'Mage', icon: '🔮' },
  { id: 'healer', name: 'Healer', icon: '💚' },
  { id: 'archer', name: 'Archer', icon: '🏹' },
  { id: 'rogue', name: 'Rogue', icon: '🗡️' },
  { id: 'artisan', name: 'Artisan', icon: '🔧' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const t = useTranslations('nav');
  const tCommon = useTranslations('common');
  const { locale, setLocale } = useLocale();

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
          flex flex-col
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="p-4 border-b border-zinc-800">
          <h1 className="text-xl font-bold text-white">KanarionDB</h1>
          <p className="text-xs text-zinc-500">Database Editor v0.9</p>
        </div>

        <nav className="p-2 flex-1">
          {NAV_ITEMS.map((item) => (
            <div key={item.href}>
              {item.disabled ? (
                <div className="flex items-center gap-3 px-3 py-2 text-zinc-600 cursor-not-allowed">
                  <span>{item.icon}</span>
                  <span>{t(item.nameKey)}</span>
                  <span className="text-[10px] bg-zinc-800 px-1.5 py-0.5 rounded ml-auto">{tCommon('soon')}</span>
                </div>
              ) : (
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    pathname === item.href
                      ? 'bg-zinc-800 text-white'
                      : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{t(item.nameKey)}</span>
                </Link>
              )}

              {item.href === '/classes' && pathname.startsWith('/classes') && (
                <div className="ml-4 mt-1 space-y-1">
                  {CLASSES.map((cls) => (
                    <Link
                      key={cls.id}
                      href={`/classes/${cls.id}`}
                      className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg transition-colors ${
                        pathname === `/classes/${cls.id}`
                          ? 'bg-zinc-700 text-white'
                          : 'text-zinc-500 hover:bg-zinc-800/50 hover:text-zinc-300'
                      }`}
                    >
                      <span>{cls.icon}</span>
                      <span>{cls.name}</span>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>

        {/* Language Toggle */}
        <div className="p-3 border-t border-zinc-800">
          <button
            onClick={toggleLocale}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors text-sm"
          >
            <span className="text-lg">{locale === 'fr' ? '🇫🇷' : '🇬🇧'}</span>
            <span className="text-zinc-300">{locale === 'fr' ? 'Francais' : 'English'}</span>
            <span className="text-zinc-500 text-xs ml-auto">→ {locale === 'fr' ? 'EN' : 'FR'}</span>
          </button>
        </div>
      </aside>
    </>
  );
}
