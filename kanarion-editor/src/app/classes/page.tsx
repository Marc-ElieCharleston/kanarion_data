import Link from 'next/link';
import { getClassList, getAllBaseStats } from '@/lib/database';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ClassStatBox } from '@/components/ClassStatBox';

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
    <div className="p-4 md:p-6 lg:p-8">
      <div className="mb-6 md:mb-8">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">Classes</h1>
        <p className="text-zinc-400">
          6 classes jouables avec leurs stats de base et compétences
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map((classId) => {
          const stats = baseStats[classId];
          if (!stats) return null;

          return (
            <Link key={classId} href={`/classes/${classId}`}>
              <Card className={`bg-gradient-to-br ${CLASS_COLORS[classId]} p-6 border hover:scale-[1.02] transition-transform`}>
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-4xl">{CLASS_ICONS[classId]}</span>
                  <div>
                    <h2 className="text-xl font-bold capitalize">{classId}</h2>
                    <Badge variant="outline" className="text-xs mt-1">
                      {stats.identity}
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-1.5 sm:gap-2">
                  <ClassStatBox label="MP" value={stats.mp} color="text-blue-400" />
                  <ClassStatBox label="HP" value={stats.hp} color="text-rose-400" />
                  <ClassStatBox label="ATK" value={stats.atk} color="text-orange-400" />
                  <ClassStatBox label="MAG" value={stats.mag} color="text-violet-400" />
                  <ClassStatBox label="ARMOR" value={stats.armor} color="text-slate-400" />
                  <ClassStatBox label="M.RES" value={stats.magic_resist} color="text-cyan-400" />
                </div>

                <div className="mt-4 text-sm text-zinc-400 text-center">
                  Click to view skills & details →
                </div>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
