import { NextResponse } from 'next/server';
import { readJsonFile } from '@/lib/database';

export async function GET() {
  try {
    // Read common passives
    const commonPassives = readJsonFile<{
      _meta: {
        version: string;
        last_updated: string;
        description: string;
      };
      common_passives: Array<{
        id: string;
        name_fr: string;
        name_en: string;
        max_level: number;
        description_fr: string;
        description_en: string;
        effects: Array<{
          stat: string;
          op: string;
          value_per_level: number;
        }>;
      }>;
    }>('classes/common_passives.json');

    // Read all class passives
    const classes = ['warrior', 'mage', 'healer', 'archer', 'rogue', 'artisan'];
    const classPassives: Record<string, any> = {};

    for (const className of classes) {
      try {
        const passives = readJsonFile<{
          _meta: {
            version: string;
            last_updated: string;
            class: string;
            description: string;
          };
          class_passives: Array<{
            id: string;
            name_fr: string;
            name_en: string;
            max_level: number;
            description_fr: string;
            description_en: string;
            effects: Array<{
              stat: string;
              op: string;
              value_per_level: number;
            }>;
          }>;
        }>(`classes/${className}/passives.json`);
        classPassives[className] = passives;
      } catch (error) {
        console.error(`Error reading passives for ${className}:`, error);
        classPassives[className] = null;
      }
    }

    // Read keystones
    const keystones = readJsonFile<{
      _meta: {
        version: string;
        last_updated: string;
        description: string;
      };
      rules: {
        max_active_keystones: number;
        max_rank: number;
        internal_cooldown_required: boolean;
        design_notes: string[];
      };
      archetypes: {
        striker: string[];
        bulwark: string[];
        conductor: string[];
      };
      class_keystones: Record<string, {
        mvp: string[];
        post_mvp: string[];
      }>;
      utility_keystones: string[];
    }>('systems/keystones.json');

    return NextResponse.json({
      common: commonPassives,
      classes: classPassives,
      keystones: keystones,
    });
  } catch (error) {
    console.error('Error in passives API:', error);
    return NextResponse.json(
      { error: 'Failed to fetch passives data' },
      { status: 500 }
    );
  }
}
