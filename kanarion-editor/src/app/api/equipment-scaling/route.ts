import { NextResponse } from 'next/server';
import { readJsonFile } from '@/lib/database';

export async function GET() {
  try {
    const data = readJsonFile('items/equipment_scaling.json');
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error reading equipment scaling:', error);
    return NextResponse.json({ error: 'Failed to load equipment scaling' }, { status: 500 });
  }
}
