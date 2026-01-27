import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function GET() {
  try {
    const ideasPath = path.join(process.cwd(), '..', 'kanarion_database', '_meta', 'ideas_to_integrate.json');
    const ideasContent = await fs.readFile(ideasPath, 'utf-8');
    const ideas = JSON.parse(ideasContent);

    return NextResponse.json(ideas);
  } catch (error) {
    console.error('Error loading ideas:', error);
    return NextResponse.json({ error: 'Failed to load ideas' }, { status: 500 });
  }
}
