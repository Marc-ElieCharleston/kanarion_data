import { NextResponse } from 'next/server';
import { readJsonFile } from '@/lib/database';

export async function GET() {
  try {
    const data = await readJsonFile('systems/encounter_stars.json');
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error reading encounter stars:', error);
    return NextResponse.json({ error: 'Failed to load encounter stars' }, { status: 500 });
  }
}
