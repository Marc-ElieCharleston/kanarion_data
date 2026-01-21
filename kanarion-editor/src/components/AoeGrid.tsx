'use client';

interface AoeGridProps {
  pattern: string;
  target?: 'enemy' | 'ally' | 'self' | 'allies' | 'enemies';
  size?: 'sm' | 'md' | 'lg';
}

// Format: [row][col] où 1 = touché, 2 = cible principale
// Grille 4x4: row 0 = front, row 1 = mid_front, row 2 = mid_back, row 3 = back
const PATTERN_SHAPES: Record<string, number[][]> = {
  single: [
    [0, 0, 2, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  row_2: [
    [0, 0, 2, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  row_3: [
    [0, 1, 2, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  row_4: [
    [1, 1, 2, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  col_2: [
    [0, 0, 2, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  col_3: [
    [0, 0, 1, 0],
    [0, 0, 2, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 0],
  ],
  col_4: [
    [0, 0, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 2, 0],
    [0, 0, 1, 0],
  ],
  rect_2x2: [
    [0, 0, 2, 1],
    [0, 0, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  rect_2x3: [
    [0, 1, 2, 1],
    [0, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  rect_3x3: [
    [1, 1, 1, 0],
    [1, 2, 1, 0],
    [1, 1, 1, 0],
    [0, 0, 0, 0],
  ],
  cross: [
    [0, 0, 1, 0],
    [0, 1, 2, 1],
    [0, 0, 1, 0],
    [0, 0, 0, 0],
  ],
  ring: [
    [0, 1, 1, 1],
    [0, 1, 0, 1],
    [0, 1, 1, 1],
    [0, 0, 0, 0],
  ],
  around_radius_1: [
    [0, 1, 1, 1],
    [0, 1, 2, 1],
    [0, 1, 1, 1],
    [0, 0, 0, 0],
  ],
  single_plus_adjacent_1: [
    [0, 0, 2, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  single_plus_adjacent_2: [
    [0, 1, 2, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  rect_3x2: [
    [0, 1, 2, 1],
    [0, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  diagonal_down: [
    [2, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
  ],
  diagonal_up: [
    [0, 0, 0, 1],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [2, 0, 0, 0],
  ],
  x_pattern: [
    [1, 0, 1, 0],
    [0, 2, 0, 0],
    [1, 0, 1, 0],
    [0, 0, 0, 0],
  ],
  v_pattern: [
    [1, 0, 0, 1],
    [0, 1, 1, 0],
    [0, 0, 2, 0],
    [0, 0, 0, 0],
  ],
  a_pattern: [
    [0, 0, 2, 0],
    [0, 1, 0, 1],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  t_pattern: [
    [0, 1, 2, 1],
    [0, 0, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 0],
  ],
  t_inverted: [
    [0, 0, 2, 0],
    [0, 0, 1, 0],
    [0, 1, 1, 1],
    [0, 0, 0, 0],
  ],
  double_row: [
    [1, 1, 2, 1],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  double_line: [
    [0, 0, 1, 1],
    [0, 0, 2, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 1],
  ],
  chain_2: [
    [0, 0, 2, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  chain_3: [
    [0, 0, 2, 1],
    [0, 0, 0, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  random_2: [
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  random_3: [
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  front_row: [
    [1, 1, 2, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  back_row: [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [1, 1, 2, 1],
  ],
  mid_rows: [
    [0, 0, 0, 0],
    [1, 1, 2, 1],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
  ],
  all: [
    [1, 1, 1, 1],
    [1, 1, 2, 1],
    [1, 1, 1, 1],
    [1, 1, 1, 1],
  ],
};

const sizeClasses = {
  sm: 'w-4 h-4 text-[8px]',
  md: 'w-6 h-6 text-xs',
  lg: 'w-8 h-8 text-sm',
};

export default function AoeGrid({ pattern, target = 'enemy', size = 'md' }: AoeGridProps) {
  const shape = PATTERN_SHAPES[pattern] || PATTERN_SHAPES.single;
  const isAlly = target === 'ally' || target === 'allies' || target === 'self';

  const getCellColor = (value: number) => {
    if (value === 0) return 'bg-zinc-800 border-zinc-700';
    if (value === 2) return isAlly ? 'bg-emerald-500 border-emerald-400' : 'bg-red-500 border-red-400';
    return isAlly ? 'bg-emerald-400/60 border-emerald-500' : 'bg-red-400/60 border-red-500';
  };

  return (
    <div className="inline-flex flex-col gap-0.5 p-1 bg-zinc-900 rounded">
      <div className="text-[10px] text-zinc-500 text-center mb-1">{pattern}</div>
      {shape.map((row, rowIndex) => (
        <div key={rowIndex} className="flex gap-0.5">
          {row.map((cell, colIndex) => (
            <div
              key={colIndex}
              className={`${sizeClasses[size]} ${getCellColor(cell)} border rounded-sm flex items-center justify-center`}
            >
              {cell === 2 && <span className="font-bold">X</span>}
              {cell === 1 && <span className="opacity-70">•</span>}
            </div>
          ))}
        </div>
      ))}
      <div className="flex gap-2 mt-1 text-[9px] text-zinc-500 justify-center">
        <span>Front</span>
        <span>→</span>
        <span>Back</span>
      </div>
    </div>
  );
}
