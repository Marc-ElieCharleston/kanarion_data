'use client';

interface AoeGridProps {
  pattern: string;
  target?: 'enemy' | 'ally' | 'self' | 'allies' | 'enemies';
  size?: 'sm' | 'md' | 'lg';
  gridFormat?: '4x4' | '5x3';
}

// Format: [row][col] où 1 = touché, 2 = cible principale
// Orientation VERTICALE: row 0 = FRONT (haut), dernière row = BACK (bas)

// Grille 4x4: 4 rows x 4 cols
const PATTERNS_4x4: Record<string, number[][]> = {
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
  row_full: [
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
    [0, 0, 2, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 0],
  ],
  col_4: [
    [0, 0, 2, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 0],
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
  rect_3x2: [
    [0, 0, 2, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 1],
    [0, 0, 0, 0],
  ],
  rect_3x3: [
    [0, 1, 1, 1],
    [0, 1, 2, 1],
    [0, 1, 1, 1],
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
  all: [
    [1, 1, 1, 1],
    [1, 1, 2, 1],
    [1, 1, 1, 1],
    [1, 1, 1, 1],
  ],
};

// Grille 5x3: 3 rows x 5 cols (format alternatif)
const PATTERNS_5x3: Record<string, number[][]> = {
  single: [
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ],
  row_2: [
    [0, 0, 2, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ],
  row_3: [
    [0, 1, 2, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ],
  row_4: [
    [1, 1, 2, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ],
  row_full: [
    [1, 1, 2, 1, 1],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ],
  col_2: [
    [0, 0, 2, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
  ],
  col_3: [
    [0, 0, 2, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
  ],
  col_4: [
    [0, 0, 2, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
  ],
  rect_2x2: [
    [0, 0, 2, 1, 0],
    [0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0],
  ],
  rect_2x3: [
    [0, 1, 2, 1, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0],
  ],
  rect_3x2: [
    [0, 0, 2, 1, 0],
    [0, 0, 1, 1, 0],
    [0, 0, 1, 1, 0],
  ],
  cross: [
    [0, 0, 1, 0, 0],
    [0, 1, 2, 1, 0],
    [0, 0, 1, 0, 0],
  ],
  around_radius_1: [
    [0, 1, 1, 1, 0],
    [0, 1, 2, 1, 0],
    [0, 1, 1, 1, 0],
  ],
  single_plus_adjacent_1: [
    [0, 0, 2, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ],
  single_plus_adjacent_2: [
    [0, 1, 2, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ],
  front_row: [
    [1, 1, 2, 1, 1],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ],
  back_row: [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [1, 1, 2, 1, 1],
  ],
  all: [
    [1, 1, 1, 1, 1],
    [1, 1, 2, 1, 1],
    [1, 1, 1, 1, 1],
  ],
};

const sizeClasses = {
  sm: 'w-3 h-3 text-[6px]',
  md: 'w-5 h-5 text-[10px]',
  lg: 'w-7 h-7 text-xs',
};

export default function AoeGrid({ pattern, target = 'enemy', size = 'md', gridFormat = '4x4' }: AoeGridProps) {
  const patterns = gridFormat === '5x3' ? PATTERNS_5x3 : PATTERNS_4x4;
  const shape = patterns[pattern] || patterns.single || PATTERNS_4x4.single;
  const isAlly = target === 'ally' || target === 'allies' || target === 'self';

  const getCellColor = (value: number) => {
    if (value === 0) return 'bg-zinc-800 border-zinc-700';
    if (value === 2) return isAlly ? 'bg-emerald-500 border-emerald-400' : 'bg-red-500 border-red-400';
    return isAlly ? 'bg-emerald-400/60 border-emerald-500' : 'bg-red-400/60 border-red-500';
  };

  const rowLabels = gridFormat === '5x3'
    ? ['Front', 'Mid', 'Back']
    : ['Front', '', '', 'Back'];

  return (
    <div className="inline-flex gap-2 p-1 bg-zinc-900 rounded">
      {/* Row labels */}
      <div className="flex flex-col gap-0.5 justify-center">
        {rowLabels.map((label, i) => (
          <div key={i} className={`${sizeClasses[size]} flex items-center justify-end pr-1`}>
            <span className="text-[8px] text-zinc-500">{label}</span>
          </div>
        ))}
      </div>

      {/* Grid */}
      <div className="flex flex-col gap-0.5">
        <div className="text-[9px] text-zinc-500 text-center mb-0.5">{pattern}</div>
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
        <div className="text-[8px] text-zinc-600 text-center mt-0.5">{gridFormat}</div>
      </div>
    </div>
  );
}
