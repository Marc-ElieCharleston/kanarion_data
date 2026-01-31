'use client';

import type { Skill } from '@/types/skill';
import { TIER_COLORS } from '@/constants/skill';

interface SkillCardHeaderProps {
  skill: Skill;
  onEdit?: (skill: Skill) => void;
  onDelete?: (skillId: string) => void;
}

export default function SkillCardHeader({ skill, onEdit, onDelete }: SkillCardHeaderProps) {
  return (
    <div className={`px-3 sm:px-4 py-2 sm:py-3 border-b ${skill.is_signature ? 'border-amber-500/30 bg-amber-500/5' : 'border-zinc-800'}`}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div className="min-w-0">
          <h4 className={`font-semibold text-sm sm:text-base truncate ${skill.is_signature ? 'text-amber-400' : 'text-white'}`}>
            {skill.is_signature && '★ '}{skill.name}
          </h4>
          {skill.name_fr && (
            <div className="text-xs text-zinc-500 truncate">{skill.name_fr}</div>
          )}
        </div>
        <div className="flex items-center gap-1 sm:gap-2 flex-wrap">
          {/* LoS indicator */}
          {skill.ignore_los ? (
            <span className="text-[10px] px-1.5 py-0.5 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded">
              Ignore LoS
            </span>
          ) : skill.damage_type !== 'none' && (
            <span className="text-[10px] px-1.5 py-0.5 bg-zinc-700/50 text-zinc-500 border border-zinc-600/30 rounded">
              Req LoS
            </span>
          )}
          <span className={`text-xs px-2 py-1 rounded border ${TIER_COLORS[skill.tier]}`}>
            {skill.tier}
          </span>
          {/* Edit/Delete buttons */}
          {(onEdit || onDelete) && (
            <div className="flex gap-1 ml-2">
              {onEdit && (
                <button
                  onClick={() => onEdit(skill)}
                  className="p-1 text-zinc-400 hover:text-white hover:bg-zinc-700 rounded"
                >
                  E
                </button>
              )}
              {onDelete && (
                <button
                  onClick={() => onDelete(skill.id)}
                  className="p-1 text-zinc-400 hover:text-red-400 hover:bg-zinc-700 rounded"
                >
                  X
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
