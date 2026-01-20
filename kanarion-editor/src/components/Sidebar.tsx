'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  { name: 'Dashboard', href: '/', icon: '🏠' },
  { name: 'Classes', href: '/classes', icon: '⚔️' },
  { name: 'Stats Reference', href: '/stats', icon: '📊' },
  { name: 'Status Effects', href: '/effects', icon: '💫' },
  { name: 'Patterns', href: '/patterns', icon: '🎯' },
  { name: 'Monsters', href: '/monsters', icon: '👹', disabled: true },
  { name: 'Items', href: '/items', icon: '🎒', disabled: true },
  { name: 'World', href: '/world', icon: '🗺️', disabled: true },
  { name: 'Systems', href: '/systems', icon: '⚙️', disabled: true },
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

  return (
    <aside className="w-64 bg-zinc-900 border-r border-zinc-800 h-screen sticky top-0 overflow-y-auto">
      <div className="p-4 border-b border-zinc-800">
        <h1 className="text-xl font-bold text-white">KanarionDB</h1>
        <p className="text-xs text-zinc-500">Database Editor v0.9</p>
      </div>

      <nav className="p-2">
        {NAV_ITEMS.map((item) => (
          <div key={item.href}>
            {item.disabled ? (
              <div className="flex items-center gap-3 px-3 py-2 text-zinc-600 cursor-not-allowed">
                <span>{item.icon}</span>
                <span>{item.name}</span>
                <span className="text-[10px] bg-zinc-800 px-1.5 py-0.5 rounded ml-auto">Soon</span>
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
                <span>{item.name}</span>
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
    </aside>
  );
}
