import { NextResponse } from 'next/server';
import { readJsonFile } from '@/lib/database';

export async function GET() {
  try {
    const data = readJsonFile('systems/enhancement_system.json');
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error reading enhancement system:', error);
    return NextResponse.json({ error: 'Failed to load enhancement system' }, { status: 500 });
  }
}
