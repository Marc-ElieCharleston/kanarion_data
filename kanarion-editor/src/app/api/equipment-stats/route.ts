import { NextResponse } from 'next/server';
import { readJsonFile } from '@/lib/database';

export async function GET() {
  try {
    const data = await readJsonFile('items/equipment_stats.json');
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error reading equipment stats:', error);
    return NextResponse.json({ error: 'Failed to load equipment stats' }, { status: 500 });
  }
}
