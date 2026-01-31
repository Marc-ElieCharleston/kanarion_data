import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const basePath = path.join(process.cwd(), 'kanarion_database', 'items');

    const equipmentData = JSON.parse(fs.readFileSync(path.join(basePath, 'equipment.json'), 'utf-8'));
    const consumablesData = JSON.parse(fs.readFileSync(path.join(basePath, 'consumables.json'), 'utf-8'));
    const materialsData = JSON.parse(fs.readFileSync(path.join(basePath, 'materials.json'), 'utf-8'));
    const affixesData = JSON.parse(fs.readFileSync(path.join(basePath, 'affixes.json'), 'utf-8'));
    const currenciesData = JSON.parse(fs.readFileSync(path.join(basePath, 'currencies.json'), 'utf-8'));

    return NextResponse.json({
      equipment: equipmentData,
      consumables: consumablesData,
      materials: materialsData,
      affixes: affixesData,
      currencies: currenciesData,
    });
  } catch (error) {
    console.error('Error reading items files:', error);
    return NextResponse.json({ error: 'Failed to load items' }, { status: 500 });
  }
}
