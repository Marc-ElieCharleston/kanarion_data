'use client';

interface LevelSliderProps {
  level: number;
  maxLevel?: number;
  onChange: (level: number) => void;
}

export default function LevelSlider({ level, maxLevel = 60, onChange }: LevelSliderProps) {
  return (
    <div className="flex items-center gap-4 bg-zinc-900 px-4 py-3 rounded-lg">
      <span className="text-sm text-zinc-400">Level:</span>
      <input
        type="range"
        min="1"
        max={maxLevel}
        value={level}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="flex-1 h-2 bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-violet-500"
      />
      <span className="text-lg font-bold text-white w-12 text-center">{level}</span>
    </div>
  );
}
