import Link from 'next/link';
import { getClassList, getAllBaseStats } from '@/lib/database';

const CLASS_ICONS: Record<string, string> = {
  warrior: '🗡️',
  mage: '🔮',
  healer: '💚',
  archer: '🏹',
  rogue: '🗡️',
  artisan: '🔧',
};

const CLASS_COLORS: Record<string, string> = {
  warrior: 'from-red-500/20 to-red-900/20 border-red-500/30',
  mage: 'from-violet-500/20 to-violet-900/20 border-violet-500/30',
  healer: 'from-emerald-500/20 to-emerald-900/20 border-emerald-500/30',
  archer: 'from-amber-500/20 to-amber-900/20 border-amber-500/30',
  rogue: 'from-slate-500/20 to-slate-900/20 border-slate-500/30',
  artisan: 'from-orange-500/20 to-orange-900/20 border-orange-500/30',
};

export default function ClassesPage() {
  const classes = getClassList();
  const baseStats = getAllBaseStats();

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Classes</h1>
        <p className="text-zinc-400">
          6 classes jouables avec leurs stats de base et compétences
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map((classId) => {
          const stats = baseStats[classId];
          if (!stats) return null;

          return (
            <Link
              key={classId}
              href={`/classes/${classId}`}
              className={`bg-gradient-to-br ${CLASS_COLORS[classId]} p-6 rounded-lg border hover:scale-[1.02] transition-transform`}
            >
              <div className="flex items-center gap-3 mb-4">
                <span className="text-4xl">{CLASS_ICONS[classId]}</span>
                <div>
                  <h2 className="text-xl font-bold capitalize">{classId}</h2>
                  <p className="text-xs text-zinc-400">{stats.identity}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-zinc-900/50 rounded p-2">
                  <div className="text-lg font-bold text-rose-400">{stats.hp}</div>
                  <div className="text-[10px] text-zinc-500">HP</div>
                </div>
                <div className="bg-zinc-900/50 rounded p-2">
                  <div className="text-lg font-bold text-orange-400">{stats.atk}</div>
                  <div className="text-[10px] text-zinc-500">ATK</div>
                </div>
                <div className="bg-zinc-900/50 rounded p-2">
                  <div className="text-lg font-bold text-violet-400">{stats.mag}</div>
                  <div className="text-[10px] text-zinc-500">MAG</div>
                </div>
                <div className="bg-zinc-900/50 rounded p-2">
                  <div className="text-lg font-bold text-sky-400">{stats.def}</div>
                  <div className="text-[10px] text-zinc-500">DEF</div>
                </div>
                <div className="bg-zinc-900/50 rounded p-2">
                  <div className="text-lg font-bold text-amber-400">{stats.crit}%</div>
                  <div className="text-[10px] text-zinc-500">CRIT</div>
                </div>
                <div className="bg-zinc-900/50 rounded p-2">
                  <div className="text-lg font-bold text-emerald-400">{stats.flee}</div>
                  <div className="text-[10px] text-zinc-500">FLEE</div>
                </div>
              </div>

              <div className="mt-4 text-sm text-zinc-400 text-center">
                Click to view skills & details →
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
