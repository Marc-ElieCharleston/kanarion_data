import { NextResponse } from 'next/server';
import { getClassSkills, readJsonFile, writeJsonFile, SkillsFile } from '@/lib/database';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ classId: string }> }
) {
  const { classId } = await params;
  const skills = getClassSkills(classId);

  if (!skills) {
    return NextResponse.json({ error: 'Skills not found' }, { status: 404 });
  }

  return NextResponse.json(skills);
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ classId: string }> }
) {
  const { classId } = await params;
  const body = await request.json();

  try {
    writeJsonFile(`classes/${classId}/skills.json`, body);
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to save' }, { status: 500 });
  }
}
