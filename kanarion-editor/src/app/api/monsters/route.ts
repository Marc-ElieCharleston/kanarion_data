import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const monstersPath = path.join(process.cwd(), 'kanarion_database', 'entities', 'monsters.json');
    const npcsPath = path.join(process.cwd(), 'kanarion_database', 'entities', 'npcs.json');

    const monstersData = JSON.parse(fs.readFileSync(monstersPath, 'utf-8'));
    const npcsData = JSON.parse(fs.readFileSync(npcsPath, 'utf-8'));

    return NextResponse.json({
      monsters: monstersData,
      npcs: npcsData,
    });
  } catch (error) {
    console.error('Error reading monsters/npcs files:', error);
    return NextResponse.json({ error: 'Failed to load monsters' }, { status: 500 });
  }
}
