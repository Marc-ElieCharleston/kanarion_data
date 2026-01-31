import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Read both status effects files
    const effectsPath = path.join(process.cwd(), 'kanarion_database', 'stats', 'status_effects.json');
    const configPath = path.join(process.cwd(), 'kanarion_database', 'config', 'status_effects.json');

    const effectsData = JSON.parse(fs.readFileSync(effectsPath, 'utf-8'));
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

    return NextResponse.json({
      effects: effectsData,
      config: configData,
    });
  } catch (error) {
    console.error('Error reading effects files:', error);
    return NextResponse.json({ error: 'Failed to load effects' }, { status: 500 });
  }
}
