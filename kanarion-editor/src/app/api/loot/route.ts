import { NextResponse } from 'next/server';
import { readJsonFile } from '@/lib/database';

export async function GET() {
  try {
    const lootTables = await readJsonFile('items/loot_tables.json');
    return NextResponse.json(lootTables);
  } catch (error) {
    console.error('Error reading loot tables:', error);
    return NextResponse.json({ error: 'Failed to load loot tables' }, { status: 500 });
  }
}
