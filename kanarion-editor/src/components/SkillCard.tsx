'use client';

import AoeGrid from './AoeGrid';

interface Skill {
  id: string;
  name: string;
  target: string;
  pattern: string;
  vfx_type: string;
  description: string;
  tags: string[];
  is_signature?: boolean;
}

interface SkillCardProps {
  skill: Skill;
  onEdit?: (skill: Skill) => void;
  onDelete?: (skillId: string) => void;
}

const VFX_ICONS: Record<string, string> = {
  melee_slash: '⚔️',
  shield: '🛡️',
  buff_aura: '✨',
  debuff_aura: '💀',
  whirlwind: '🌀',
  dash_trail: '💨',
  falling: '☄️',
  life_steal: '🩸',
};

const TARGET_COLORS: Record<string, string> = {
  self: 'bg-blue-500/20 text-blue-400',
  ally: 'bg-emerald-500/20 text-emerald-400',
  allies: 'bg-emerald-500/20 text-emerald-400',
  enemy: 'bg-red-500/20 text-red-400',
  enemies: 'bg-red-500/20 text-red-400',
};

export default function SkillCard({ skill, onEdit, onDelete }: SkillCardProps) {
  return (
    <div
      className={`bg-zinc-900 rounded-lg p-4 border ${
        skill.is_signature
          ? 'border-amber-500/50 bg-gradient-to-br from-zinc-900 to-amber-950/20'
          : 'border-zinc-700'
      } hover:border-zinc-500 transition-colors`}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xl">{VFX_ICONS[skill.vfx_type] || '⚡'}</span>
            <h3 className="font-semibold text-white">
              {skill.name}
              {skill.is_signature && (
                <span className="ml-2 text-xs bg-amber-500/30 text-amber-400 px-2 py-0.5 rounded">
                  SIGNATURE
                </span>
              )}
            </h3>
          </div>
          <p className="text-xs text-zinc-500 font-mono mt-1">{skill.id}</p>
        </div>

        <div className="flex gap-1">
          {onEdit && (
            <button
              onClick={() => onEdit(skill)}
              className="p-1.5 text-zinc-400 hover:text-white hover:bg-zinc-700 rounded"
            >
              ✏️
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(skill.id)}
              className="p-1.5 text-zinc-400 hover:text-red-400 hover:bg-zinc-700 rounded"
            >
              🗑️
            </button>
          )}
        </div>
      </div>

      <p className="text-sm text-zinc-300 mb-4">{skill.description}</p>

      <div className="flex flex-wrap gap-4 items-start">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs text-zinc-500">Target:</span>
            <span className={`text-xs px-2 py-0.5 rounded ${TARGET_COLORS[skill.target] || 'bg-zinc-700 text-zinc-300'}`}>
              {skill.target}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-zinc-500">VFX:</span>
            <span className="text-xs bg-zinc-700 px-2 py-0.5 rounded text-zinc-300">
              {skill.vfx_type}
            </span>
          </div>
        </div>

        <AoeGrid pattern={skill.pattern} target={skill.target as any} size="md" />
      </div>

      <div className="flex flex-wrap gap-1 mt-4">
        {skill.tags.map((tag, index) => (
          <span
            key={index}
            className="text-xs bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded"
          >
            #{tag}
          </span>
        ))}
      </div>
    </div>
  );
}
