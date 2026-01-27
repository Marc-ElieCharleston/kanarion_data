import { NextResponse } from 'next/server';
import { getClassList, getAllBaseStats, getAllGrowthStats } from '@/lib/database';

export async function GET() {
  const classes = getClassList();
  const baseStats = getAllBaseStats();
  const growthStats = getAllGrowthStats();

  const classesData = classes.map(className => ({
    id: className,
    name: className.charAt(0).toUpperCase() + className.slice(1),
    baseStats: baseStats[className],
    growth: growthStats[className],
  }));

  return NextResponse.json(classesData);
}
