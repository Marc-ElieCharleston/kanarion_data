'use client';

import AoeGrid from './AoeGrid';
import {
  SkillCardHeader,
  DamageStatsRow,
  HealStatsRow,
  ResourceStatsRow,
  EffectsDisplay,
  ClassMechanics,
  ArcherMechanics,
  BallmasterMechanics,
  GunslingerMechanics,
  ArtisanMechanics,
  RogueMechanics,
  DuelistMechanics,
  WarlordMechanics,
  TagsList,
} from './skill';

import type { Skill, TierScaling, DurationScaling, SkillCardProps } from '@/types/skill';
import { DEFAULT_TIER_SCALING, DEFAULT_DURATION_SCALING } from '@/constants/skill';
import { calculateSkillStats } from '@/utils/skillScaling';

// Re-export types for backwards compatibility
export type { Skill, TierScaling, DurationScaling } from '@/types/skill';
export { DEFAULT_TIER_SCALING, DEFAULT_DURATION_SCALING } from '@/constants/skill';

export default function SkillCard({
  skill,
  skillLevel = 1,
  scalingByTier = DEFAULT_TIER_SCALING,
  durationScaling = DEFAULT_DURATION_SCALING,
  showGrids = true,
  onEdit,
  onDelete,
}: SkillCardProps) {
  const stats = calculateSkillStats(skill, skillLevel, scalingByTier, durationScaling);

  return (
    <div className={`bg-zinc-900 rounded-lg border ${skill.is_signature ? 'border-amber-500/50' : 'border-zinc-800'} overflow-hidden`}>
      {/* Header */}
      <SkillCardHeader skill={skill} onEdit={onEdit} onDelete={onDelete} />

      {/* Content */}
      <div className="p-4">
        {/* Damage stats row */}
        <DamageStatsRow
          skill={skill}
          skillLevel={skillLevel}
          basePowerAtLevel={stats.basePowerAtLevel}
          scalingPercentAtLevel={stats.scalingPercentAtLevel}
          tierScaling={stats.tierScaling}
          percentPerLevel={stats.percentPerLevel}
        />

        {/* Heal stats row */}
        <HealStatsRow skill={skill} />

        {/* Mana/CD row */}
        <ResourceStatsRow
          skill={skill}
          skillLevel={skillLevel}
          manaAtLevel={stats.manaAtLevel}
          tierScaling={stats.tierScaling}
        />

        {/* AoE Grids */}
        {showGrids && (
          <div className="flex justify-center space-x-8 mb-3 -mx-2">
            <AoeGrid
              pattern={skill.pattern}
              target={skill.target as 'enemy' | 'ally' | 'self' | 'allies' | 'enemies'}
              size="sm"
              gridFormat="4x4"
            />
            <AoeGrid
              pattern={skill.pattern}
              target={skill.target as 'enemy' | 'ally' | 'self' | 'allies' | 'enemies'}
              size="sm"
              gridFormat="5x3"
            />
          </div>
        )}

        {/* Description */}
        <p className="text-sm text-zinc-300 mb-2">
          {skill.description_fr || skill.description_en || skill.description || 'No description'}
        </p>

        {/* Effects (buffs, debuffs, shields) */}
        <EffectsDisplay
          skill={skill}
          skillLevel={skillLevel}
          effectDurationAtLevel={stats.effectDurationAtLevel}
          buffDurationAtLevel={stats.buffDurationAtLevel}
          debuffDurationAtLevel={stats.debuffDurationAtLevel}
          shieldValueAtLevel={stats.shieldValueAtLevel}
        />

        {/* Class-specific mechanics */}
        <ClassMechanics skill={skill} />
        <ArcherMechanics skill={skill} />
        <BallmasterMechanics skill={skill} />
        <GunslingerMechanics skill={skill} />
        <ArtisanMechanics skill={skill} />
        <RogueMechanics skill={skill} />
        <DuelistMechanics skill={skill} />
        <WarlordMechanics skill={skill} />

        {/* Tags */}
        <TagsList tags={skill.tags} />
      </div>
    </div>
  );
}
