import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const basePath = path.join(process.cwd(), 'kanarion_database', 'world');

    const zonesData = JSON.parse(fs.readFileSync(path.join(basePath, 'zones.json'), 'utf-8'));
    const dungeonsData = JSON.parse(fs.readFileSync(path.join(basePath, 'dungeons.json'), 'utf-8'));
    const questsData = JSON.parse(fs.readFileSync(path.join(basePath, 'quests.json'), 'utf-8'));

    return NextResponse.json({
      zones: zonesData,
      dungeons: dungeonsData,
      quests: questsData,
    });
  } catch (error) {
    console.error('Error reading world files:', error);
    return NextResponse.json({ error: 'Failed to load world data' }, { status: 500 });
  }
}
