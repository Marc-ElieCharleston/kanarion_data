import { NextResponse } from 'next/server';
import { readJsonFile } from '@/lib/database';

export async function GET() {
  const definitions = readJsonFile<any>('stats/definitions.json');
  return NextResponse.json(definitions);
}
