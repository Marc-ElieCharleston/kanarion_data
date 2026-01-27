import { NextResponse } from 'next/server';
import { readJsonFile } from '@/lib/database';

interface SkillSystemConfig {
  _meta: {
    version: string;
    last_updated: string;
    description: string;
  };
  skill_points: {
    points_per_level: number;
    starting_points: number;
    max_player_level: number;
    total_points_available: number;
  };
  skill_levels: {
    min_level: number;
    max_level: number;
    points_per_skill_level: number;
  };
  skill_categories: Record<string, {
    count: number;
    unlock_at_player_level: number;
    description: string;
  }>;
  scaling: Record<string, {
    per_level_percent?: number;
    per_level_flat?: number;
    at_level_10: number;
    formula: string;
    description: string;
  }>;
  skill_tiers: Record<string, {
    power_range: [number, number];
    cooldown_range: [number, number];
    mana_range: [number, number];
    description: string;
  }>;
}

interface Skill {
  id: string;
  name: string;
  name_fr?: string;
  tier: string;
  target: string;
  pattern: string;
  damage_type: string;
  base_power: number;
  mana_cost: number;
  cooldown: number;
  vfx_type: string;
  description_fr?: string;
  description_en?: string;
  tags: string[];
  is_signature?: boolean;
  effect?: string;
  effect_chance?: number;
  effect_duration?: number;
  buff?: string;
  buff_value?: number;
  buff_duration?: number;
  debuff?: string;
  debuff_value?: number;
  debuff_duration?: number;
  shield_value?: number;
  shield_duration?: number;
  [key: string]: unknown;
}

interface SkillsFile {
  _meta: {
    version: string;
    last_updated: string;
    class: string;
    description: string;
    pattern_presets: Record<string, string>;
    vfx_available: string[];
  };
  base_skills: Skill[];
  subclass_skills: Record<string, {
    identity: string;
    signature: string;
    skills: Skill[];
  }>;
}

export async function GET() {
  try {
    const skillSystem = readJsonFile<SkillSystemConfig>('config/skill_system.json');

    const classes = ['warrior', 'mage', 'healer', 'archer', 'rogue', 'artisan'];
    const skillsByClass: Record<string, SkillsFile> = {};

    for (const className of classes) {
      try {
        skillsByClass[className] = readJsonFile<SkillsFile>(`classes/${className}/skills.json`);
      } catch {
        // Skip classes without skills file
      }
    }

    return NextResponse.json({
      system: skillSystem,
      classes: skillsByClass
    });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to load skills data' }, { status: 500 });
  }
}
