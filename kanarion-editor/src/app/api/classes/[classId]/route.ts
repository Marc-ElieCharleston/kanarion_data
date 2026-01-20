import { NextResponse } from 'next/server';
import { getClassBaseStats, getClassGrowth, getClassSkills } from '@/lib/database';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ classId: string }> }
) {
  const { classId } = await params;

  const baseStats = getClassBaseStats(classId);
  const growth = getClassGrowth(classId);
  const skills = getClassSkills(classId);

  if (!baseStats) {
    return NextResponse.json({ error: 'Class not found' }, { status: 404 });
  }

  return NextResponse.json({
    id: classId,
    name: classId.charAt(0).toUpperCase() + classId.slice(1),
    baseStats,
    growth,
    skills,
  });
}
