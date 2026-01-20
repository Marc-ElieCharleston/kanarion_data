import { NextResponse } from 'next/server';
import { readJsonFile } from '@/lib/database';

export async function GET() {
  try {
    const panoplies = await readJsonFile('items/panoplies.json');
    return NextResponse.json(panoplies);
  } catch (error) {
    console.error('Error reading panoplies:', error);
    return NextResponse.json({ error: 'Failed to load panoplies' }, { status: 500 });
  }
}
