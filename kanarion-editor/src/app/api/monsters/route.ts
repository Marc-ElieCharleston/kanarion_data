import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const monstersPath = path.join(process.cwd(), '..', 'kanarion_database', 'entities', 'monsters.json');
    const monstersData = JSON.parse(fs.readFileSync(monstersPath, 'utf-8'));

    return NextResponse.json(monstersData);
  } catch (error) {
    console.error('Error reading monsters file:', error);
    return NextResponse.json({ error: 'Failed to load monsters' }, { status: 500 });
  }
}
