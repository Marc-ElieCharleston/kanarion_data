import Link from 'next/link';

export default function Home() {
  const stats = [
    { label: 'Classes', value: '6', href: '/classes', icon: '⚔️' },
    { label: 'Subclasses', value: '24', href: '/classes', icon: '🎭' },
    { label: 'Skills', value: '100+', href: '/classes', icon: '✨' },
    { label: 'Monsters', value: '50+', href: '/monsters', icon: '👹' },
    { label: 'Zones', value: '10', href: '/world', icon: '🗺️' },
    { label: 'Items', value: '200+', href: '/items', icon: '🎒' },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">KanarionDB Editor</h1>
        <p className="text-zinc-400">
          Visual database editor for Kanarion Online MMORPG
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {stats.map((stat) => (
          <Link
            key={stat.label}
            href={stat.href}
            className="bg-zinc-900 p-4 rounded-lg border border-zinc-800 hover:border-zinc-600 transition-colors"
          >
            <div className="text-2xl mb-2">{stat.icon}</div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
            <div className="text-sm text-zinc-500">{stat.label}</div>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>⚔️</span> Classes
          </h2>
          <p className="text-zinc-400 text-sm mb-4">
            6 classes de base avec 4 sous-classes chacune. Visualisez les stats,
            la progression et tous les skills avec leurs patterns AOE.
          </p>
          <Link
            href="/classes"
            className="inline-flex items-center gap-2 text-violet-400 hover:text-violet-300"
          >
            Explorer les classes →
          </Link>
        </div>

        <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>📊</span> Combat System
          </h2>
          <p className="text-zinc-400 text-sm mb-4">
            Grille de combat 2×5 (10 slots). Patterns d'AOE visualisables,
            système de ciblage dual (allié + ennemi).
          </p>
          <div className="text-zinc-500 text-sm">Coming soon...</div>
        </div>
      </div>

      <div className="mt-8 p-4 bg-zinc-900/50 rounded-lg border border-zinc-800">
        <div className="flex items-center gap-2 text-sm text-zinc-500">
          <span>📁</span>
          <span>Database path:</span>
          <code className="bg-zinc-800 px-2 py-0.5 rounded text-zinc-400">
            ../kanarion_database/
          </code>
        </div>
      </div>
    </div>
  );
}
