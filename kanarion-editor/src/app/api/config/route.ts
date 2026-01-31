import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const basePath = path.join(process.cwd(), 'kanarion_database', 'config');

    const combatData = JSON.parse(fs.readFileSync(path.join(basePath, 'combat.json'), 'utf-8'));
    const monsterAiData = JSON.parse(fs.readFileSync(path.join(basePath, 'monster_ai.json'), 'utf-8'));
    const gameData = JSON.parse(fs.readFileSync(path.join(basePath, 'game.json'), 'utf-8'));

    return NextResponse.json({
      combat: combatData,
      monsterAi: monsterAiData,
      gameConfig: gameData,
    });
  } catch (error) {
    console.error('Error reading config files:', error);
    return NextResponse.json({ error: 'Failed to load config data' }, { status: 500 });
  }
}
