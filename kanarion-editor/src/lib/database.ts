import fs from 'fs';
import path from 'path';

// Check local copy first (Vercel build), then parent directory (local dev)
const LOCAL_DB = path.join(process.cwd(), 'kanarion_database');
const PARENT_DB = path.join(process.cwd(), '..', 'kanarion_database');
const DB_PATH = fs.existsSync(LOCAL_DB) ? LOCAL_DB : PARENT_DB;

export function readJsonFile<T>(relativePath: string): T {
  const filePath = path.join(DB_PATH, relativePath);
  const content = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(content) as T;
}

export function writeJsonFile<T>(relativePath: string, data: T): void {
  const filePath = path.join(DB_PATH, relativePath);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

export function getClassList(): string[] {
  return ['warrior', 'mage', 'healer', 'archer', 'rogue', 'artisan'];
}

export interface ClassStats {
  identity: string;
  // Resources
  hp: number;
  mp: number;
  hp_regen: number;
  mp_regen: number;
  hp_regen_combat: number;
  mp_regen_combat: number;
  // Offensive
  atk: number;
  def: number;
  mag: number;
  armor: number;
  magic_resist: number;
  crit: number;
  crit_dmg: number;
  // Precision
  hit: number;
  flee: number;
  armor_pen: number;
  magic_pen: number;
  // Defensive
  block_chance: number;
  parry_chance: number;
  effect_chance: number;
  effect_resist: number;
  debuff_duration: number;
  tenacity: number;
  buff_duration: number;
  damage_percent: number;
  damage_reduction: number;
  // Support
  double_hit_chance: number;
  attack_speed: number;
  heal_power: number;
  shield_power: number;
  healing_received: number;
  lifesteal: number;
  spell_vamp: number;
  cast_speed: number;
  cooldown_reduction: number;
  // Special
  luck: number;
}

export interface ClassGrowth {
  // Resources
  hp: number;
  mp: number;
  hp_regen: number;
  mp_regen: number;
  hp_regen_combat: number;
  mp_regen_combat: number;
  // Offensive
  atk: number;
  def: number;
  mag: number;
  armor: number;
  magic_resist: number;
  crit: number;
  crit_dmg: number;
  // Precision
  hit: number;
  flee: number;
  armor_pen: number;
  magic_pen: number;
  // Defensive
  block_chance: number;
  parry_chance: number;
  effect_chance: number;
  effect_resist: number;
  debuff_duration: number;
  tenacity: number;
  buff_duration: number;
  damage_percent: number;
  damage_reduction: number;
  // Support
  double_hit_chance: number;
  attack_speed: number;
  heal_power: number;
  shield_power: number;
  healing_received: number;
  lifesteal: number;
  spell_vamp: number;
  cast_speed: number;
  cooldown_reduction: number;
  // Special
  luck: number;
}

export interface Skill {
  id: string;
  name: string;
  target: string;
  pattern: string;
  vfx_type: string;
  tres: string;
  description: string;
  tags: string[];
  is_signature?: boolean;
}

export interface SkillsFile {
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

export function getClassBaseStats(className: string): ClassStats | null {
  const data = readJsonFile<Record<string, ClassStats>>('stats/class_base_stats.json');
  return data[className] || null;
}

export function getClassGrowth(className: string): ClassGrowth | null {
  const data = readJsonFile<Record<string, ClassGrowth>>('stats/class_growth.json');
  return data[className] || null;
}

export function getClassSkills(className: string): SkillsFile | null {
  try {
    return readJsonFile<SkillsFile>(`classes/${className}/skills.json`);
  } catch {
    return null;
  }
}

export function getAllBaseStats(): Record<string, ClassStats> {
  const data = readJsonFile<Record<string, ClassStats>>('stats/class_base_stats.json');
  const { _meta, ...classes } = data as Record<string, ClassStats>;
  return classes;
}

export function getAllGrowthStats(): Record<string, ClassGrowth> {
  const data = readJsonFile<Record<string, ClassGrowth>>('stats/class_growth.json');
  const { _meta, ...classes } = data as Record<string, ClassGrowth>;
  return classes;
}
