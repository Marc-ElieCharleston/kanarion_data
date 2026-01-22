'use client';

import { useState } from 'react';

// Grid configurations to compare
const GRID_CONFIGS = {
  '3x4': { rows: 3, cols: 4, slots: 12, name: '3x4' },
  '4x4': { rows: 4, cols: 4, slots: 16, name: '4x4 (Recommandé)' },
};

type GridConfig = keyof typeof GRID_CONFIGS;

// Pattern definitions - will adapt to grid size
const PATTERNS = {
  // Single target
  single: {
    name: 'Single',
    description: 'Cible unique',
    category: 'basic',
    getPattern: (rows: number, cols: number) => [[Math.floor(rows/2), Math.floor(cols/2)]],
  },

  // Row patterns
  row_2: {
    name: 'Row 2',
    description: '2 cases horizontales adjacentes',
    category: 'line',
    getPattern: (rows: number, cols: number) => {
      const r = Math.floor(rows/2);
      const c = Math.floor(cols/2);
      return [[r, c], [r, c+1]];
    },
  },
  row_3: {
    name: 'Row 3',
    description: '3 cases horizontales',
    category: 'line',
    getPattern: (rows: number, cols: number) => {
      const r = Math.floor(rows/2);
      const c = Math.floor(cols/2) - 1;
      return [[r, c], [r, c+1], [r, c+2]];
    },
  },
  row_4: {
    name: 'Row 4',
    description: 'Ligne complete (4 cases)',
    category: 'line',
    getPattern: (rows: number, cols: number) => {
      const r = Math.floor(rows/2);
      return Array.from({ length: cols }, (_, c) => [r, c]);
    },
  },

  // Column patterns
  col_2: {
    name: 'Column 2',
    description: '2 cases verticales',
    category: 'line',
    getPattern: (rows: number, cols: number) => {
      const c = Math.floor(cols/2);
      const r = Math.floor(rows/2);
      return [[r, c], [r+1 < rows ? r+1 : r-1, c]];
    },
  },
  col_3: {
    name: 'Column 3',
    description: '3 cases verticales',
    category: 'line',
    getPattern: (rows: number, cols: number) => {
      if (rows < 3) return [[0, Math.floor(cols/2)], [1, Math.floor(cols/2)]];
      const c = Math.floor(cols/2);
      return [[0, c], [1, c], [2, c]];
    },
  },
  col_4: {
    name: 'Column 4',
    description: 'Colonne complete (4 cases)',
    category: 'line',
    getPattern: (rows: number, cols: number) => {
      const c = Math.floor(cols/2);
      return Array.from({ length: rows }, (_, r) => [r, c]);
    },
  },

  // Rectangle patterns
  rect_2x2: {
    name: 'Rect 2x2',
    description: 'Carre 2x2 (4 cases)',
    category: 'area',
    getPattern: (rows: number, cols: number) => {
      const r = Math.floor(rows/2) - 1;
      const c = Math.floor(cols/2) - 1;
      return [[r, c], [r, c+1], [r+1, c], [r+1, c+1]].filter(([y, x]) => y >= 0 && x >= 0);
    },
  },
  rect_2x3: {
    name: 'Rect 2x3',
    description: 'Rectangle 2 rows x 3 cols (6 cases)',
    category: 'area',
    getPattern: (rows: number, cols: number) => {
      const r = Math.floor(rows/2) - 1;
      const c = Math.floor(cols/2) - 1;
      const tiles: number[][] = [];
      for (let dr = 0; dr < 2; dr++) {
        for (let dc = 0; dc < 3; dc++) {
          if (r + dr >= 0 && r + dr < rows && c + dc >= 0 && c + dc < cols) {
            tiles.push([r + dr, c + dc]);
          }
        }
      }
      return tiles;
    },
  },
  rect_3x3: {
    name: 'Rect 3x3',
    description: 'Carre 3x3 (9 cases)',
    category: 'area',
    getPattern: (rows: number, cols: number) => {
      const r = Math.floor(rows/2) - 1;
      const c = Math.floor(cols/2) - 1;
      const tiles: number[][] = [];
      for (let dr = 0; dr < 3; dr++) {
        for (let dc = 0; dc < 3; dc++) {
          if (r + dr >= 0 && r + dr < rows && c + dc >= 0 && c + dc < cols) {
            tiles.push([r + dr, c + dc]);
          }
        }
      }
      return tiles;
    },
  },

  // Cross/Plus patterns
  cross: {
    name: 'Cross',
    description: 'Croix (centre + 4 adjacents)',
    category: 'special',
    getPattern: (rows: number, cols: number) => {
      const r = Math.floor(rows/2);
      const c = Math.floor(cols/2);
      const tiles: number[][] = [[r, c]];
      if (r > 0) tiles.push([r-1, c]);
      if (r < rows-1) tiles.push([r+1, c]);
      if (c > 0) tiles.push([r, c-1]);
      if (c < cols-1) tiles.push([r, c+1]);
      return tiles;
    },
  },

  // Ring pattern (no center)
  ring: {
    name: 'Ring',
    description: 'Anneau (sans centre)',
    category: 'special',
    getPattern: (rows: number, cols: number) => {
      const r = Math.floor(rows/2);
      const c = Math.floor(cols/2);
      const tiles: number[][] = [];
      for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
          if (dr === 0 && dc === 0) continue; // skip center
          const nr = r + dr;
          const nc = c + dc;
          if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
            tiles.push([nr, nc]);
          }
        }
      }
      return tiles;
    },
  },

  // Diagonal patterns (only useful on 3+ rows)
  diagonal_down: {
    name: 'Diagonal \\',
    description: 'Diagonale descendante',
    category: 'special',
    getPattern: (rows: number, cols: number) => {
      const tiles: number[][] = [];
      const len = Math.min(rows, cols);
      for (let i = 0; i < len; i++) {
        tiles.push([i, i]);
      }
      return tiles;
    },
  },
  diagonal_up: {
    name: 'Diagonal /',
    description: 'Diagonale montante',
    category: 'special',
    getPattern: (rows: number, cols: number) => {
      const tiles: number[][] = [];
      const len = Math.min(rows, cols);
      for (let i = 0; i < len; i++) {
        tiles.push([rows - 1 - i, i]);
      }
      return tiles;
    },
  },

  // X pattern (checkerboard corners + center)
  x_pattern: {
    name: 'X Pattern',
    description: 'Coins + centre (damier)',
    category: 'special',
    getPattern: (rows: number, cols: number) => {
      // Pattern:
      // 1 0 1
      // 0 1 0
      // 1 0 1
      const midR = Math.floor(rows / 2);
      const midC = Math.floor(cols / 2);
      return [
        [midR - 1, midC - 1], [midR - 1, midC + 1],
        [midR, midC],
        [midR + 1, midC - 1], [midR + 1, midC + 1],
      ].filter(([r, c]) => r >= 0 && r < rows && c >= 0 && c < cols);
    },
  },

  // V pattern
  v_pattern: {
    name: 'V Pattern',
    description: 'Forme en V',
    category: 'special',
    getPattern: (rows: number, cols: number) => {
      // V shape: corners spread at top, converge at bottom
      const tiles: number[][] = [];
      const midCol = Math.floor(cols / 2);
      for (let r = 0; r < Math.min(rows, 3); r++) {
        const spread = 2 - r; // 2, 1, 0
        if (spread === 0) {
          tiles.push([r, midCol]);
        } else {
          tiles.push([r, midCol - spread]);
          tiles.push([r, midCol + spread]);
        }
      }
      return tiles.filter(([row, col]) => col >= 0 && col < cols);
    },
  },

  // A pattern (inverse V)
  a_pattern: {
    name: 'A Pattern',
    description: 'Forme en A (V inverse)',
    category: 'special',
    getPattern: (rows: number, cols: number) => {
      // A shape: converge at top, spread at bottom
      const tiles: number[][] = [];
      const midCol = Math.floor(cols / 2);
      for (let r = 0; r < Math.min(rows, 3); r++) {
        const spread = r; // 0, 1, 2
        if (spread === 0) {
          tiles.push([r, midCol]);
        } else {
          tiles.push([r, midCol - spread]);
          tiles.push([r, midCol + spread]);
        }
      }
      return tiles.filter(([row, col]) => col >= 0 && col < cols);
    },
  },

  // Double row (2x4)
  double_row: {
    name: 'Double Row',
    description: '2 lignes completes (2x4)',
    category: 'area',
    getPattern: (rows: number, cols: number) => {
      const tiles: number[][] = [];
      const startRow = Math.floor(rows / 2) - 1;
      for (let r = 0; r < 2; r++) {
        for (let c = 0; c < cols; c++) {
          if (startRow + r >= 0 && startRow + r < rows) {
            tiles.push([startRow + r, c]);
          }
        }
      }
      return tiles;
    },
  },

  // Double line (4x2) - 2 full columns
  double_line: {
    name: 'Double Line',
    description: '2 colonnes completes (4x2)',
    category: 'area',
    getPattern: (rows: number, cols: number) => {
      const tiles: number[][] = [];
      const startCol = Math.floor(cols / 2) - 1;
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < 2; c++) {
          if (startCol + c >= 0 && startCol + c < cols) {
            tiles.push([r, startCol + c]);
          }
        }
      }
      return tiles;
    },
  },

  // T patterns
  t_pattern: {
    name: 'T Pattern',
    description: 'Forme en T (souffle)',
    category: 'special',
    getPattern: (rows: number, cols: number) => {
      const midC = Math.floor(cols / 2);
      return [
        [0, midC - 1], [0, midC], [0, midC + 1],
        [1, midC],
        [2, midC],
      ].filter(([r, c]) => r < rows && c >= 0 && c < cols);
    },
  },
  t_inverted: {
    name: 'T Inverse',
    description: 'Forme en T inverse',
    category: 'special',
    getPattern: (rows: number, cols: number) => {
      const midC = Math.floor(cols / 2);
      return [
        [0, midC],
        [1, midC],
        [2, midC - 1], [2, midC], [2, midC + 1],
      ].filter(([r, c]) => r < rows && c >= 0 && c < cols);
    },
  },

  // Chain patterns - max 1 cell distance (adjacent, diagonal included)
  chain_2: {
    name: 'Chain 2',
    description: 'Rebondit sur 2 cibles (max 1 case, diag incluse)',
    category: 'chain',
    getPattern: (rows: number, cols: number) => {
      // Visual: shows adjacent bouncing including diagonal
      return [[1, 1], [2, 2], [3, 1]];
    },
  },
  chain_3: {
    name: 'Chain 3',
    description: 'Rebondit sur 3 cibles (max 1 case, diag incluse)',
    category: 'chain',
    getPattern: (rows: number, cols: number) => {
      return [[0, 1], [1, 2], [2, 1], [3, 2]];
    },
  },

  // Random patterns
  random_2: {
    name: 'Random 2',
    description: '2 cibles aleatoires',
    category: 'random',
    getPattern: (rows: number, cols: number) => [[0, 1], [rows-1, cols-2]],
  },
  random_3: {
    name: 'Random 3',
    description: '3 cibles aleatoires',
    category: 'random',
    getPattern: (rows: number, cols: number) => [[0, 0], [Math.floor(rows/2), Math.floor(cols/2)], [rows-1, cols-1]],
  },

  // Full patterns
  all: {
    name: 'All',
    description: 'Toute la grille',
    category: 'basic',
    getPattern: (rows: number, cols: number) => {
      const tiles: number[][] = [];
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          tiles.push([r, c]);
        }
      }
      return tiles;
    },
  },

  // Front row only
  front_row: {
    name: 'Front Row',
    description: 'Premiere ligne (front)',
    category: 'positional',
    getPattern: (rows: number, cols: number) => {
      return Array.from({ length: cols }, (_, c) => [0, c]);
    },
  },

  // Back row only
  back_row: {
    name: 'Back Row',
    description: 'Derniere ligne (back)',
    category: 'positional',
    getPattern: (rows: number, cols: number) => {
      return Array.from({ length: cols }, (_, c) => [rows - 1, c]);
    },
  },

  // Mid row (only for 3+ rows)
  mid_row: {
    name: 'Mid Row',
    description: 'Ligne du milieu',
    category: 'positional',
    getPattern: (rows: number, cols: number) => {
      if (rows < 3) return [];
      const midRow = Math.floor(rows / 2);
      return Array.from({ length: cols }, (_, c) => [midRow, c]);
    },
  },
};

const CATEGORIES = {
  basic: { name: 'Basique', color: 'text-zinc-400' },
  line: { name: 'Ligne', color: 'text-sky-400' },
  area: { name: 'Zone', color: 'text-orange-400' },
  special: { name: 'Special', color: 'text-violet-400' },
  chain: { name: 'Chain', color: 'text-emerald-400' },
  random: { name: 'Random', color: 'text-amber-400' },
  positional: { name: 'Positionnel', color: 'text-rose-400' },
};

function PatternGrid({
  rows,
  cols,
  pattern,
  size = 'normal'
}: {
  rows: number;
  cols: number;
  pattern: number[][];
  size?: 'small' | 'normal' | 'large';
}) {
  const cellSize = size === 'small' ? 'w-6 h-6' : size === 'large' ? 'w-12 h-12' : 'w-8 h-8';
  const patternSet = new Set(pattern.map(([r, c]) => `${r},${c}`));

  return (
    <div className="inline-flex flex-col gap-0.5">
      {Array.from({ length: rows }, (_, r) => (
        <div key={r} className="flex gap-0.5">
          {Array.from({ length: cols }, (_, c) => {
            const isActive = patternSet.has(`${r},${c}`);
            return (
              <div
                key={c}
                className={`${cellSize} rounded-sm border ${
                  isActive
                    ? 'bg-violet-500/80 border-violet-400'
                    : 'bg-zinc-800/50 border-zinc-700/50'
                }`}
              />
            );
          })}
        </div>
      ))}
    </div>
  );
}

export default function PatternsPage() {
  const [selectedGrid, setSelectedGrid] = useState<GridConfig>('4x4');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const config = GRID_CONFIGS[selectedGrid];

  const filteredPatterns = Object.entries(PATTERNS).filter(([_, p]) =>
    !selectedCategory || p.category === selectedCategory
  );

  return (
    <div className="p-4 md:p-6 lg:p-8">
      {/* Header */}
      <div className="mb-4 md:mb-6">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">Patterns de Combat</h1>
        <p className="text-zinc-500 text-sm">
          {Object.keys(PATTERNS).length} patterns - Compare les grilles
        </p>
      </div>

      {/* Grid Comparison */}
      <div className="mb-8 p-6 bg-zinc-900 rounded-lg border border-zinc-800">
        <h2 className="text-xl font-semibold mb-4">Comparaison des Grilles</h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {Object.entries(GRID_CONFIGS).map(([key, cfg]) => (
            <button
              key={key}
              onClick={() => setSelectedGrid(key as GridConfig)}
              className={`p-4 rounded-lg border transition-all ${
                selectedGrid === key
                  ? 'bg-violet-500/20 border-violet-500'
                  : 'bg-zinc-800/50 border-zinc-700 hover:border-zinc-600'
              }`}
            >
              <div className="font-semibold mb-2">{cfg.name}</div>
              <div className="text-xs text-zinc-500 mb-3">
                {cfg.rows} rows × {cfg.cols} cols = {cfg.slots} slots
              </div>
              <PatternGrid rows={cfg.rows} cols={cfg.cols} pattern={[]} size="small" />
            </button>
          ))}
        </div>

      </div>

      {/* Category Filter */}
      <div className="mb-6 flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedCategory(null)}
          className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
            !selectedCategory
              ? 'bg-violet-500 text-white'
              : 'bg-zinc-800 text-zinc-400 hover:text-white'
          }`}
        >
          Tous ({Object.keys(PATTERNS).length})
        </button>
        {Object.entries(CATEGORIES).map(([key, cat]) => {
          const count = Object.values(PATTERNS).filter(p => p.category === key).length;
          return (
            <button
              key={key}
              onClick={() => setSelectedCategory(key)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                selectedCategory === key
                  ? 'bg-violet-500 text-white'
                  : `bg-zinc-800 ${cat.color} hover:text-white`
              }`}
            >
              {cat.name} ({count})
            </button>
          );
        })}
      </div>

      {/* Patterns Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
        {filteredPatterns.map(([key, patternDef]) => {
          const pattern = patternDef.getPattern(config.rows, config.cols);
          const category = CATEGORIES[patternDef.category as keyof typeof CATEGORIES];

          return (
            <div
              key={key}
              className="bg-zinc-900 rounded-lg border border-zinc-800 p-4 hover:border-zinc-700 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="font-medium">{patternDef.name}</div>
                  <div className={`text-xs ${category.color}`}>{category.name}</div>
                </div>
                <div className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">
                  {pattern.length} tiles
                </div>
              </div>

              <div className="flex justify-center my-3">
                <PatternGrid
                  rows={config.rows}
                  cols={config.cols}
                  pattern={pattern}
                />
              </div>

              <div className="text-xs text-zinc-500 text-center">
                {patternDef.description}
              </div>
            </div>
          );
        })}
      </div>

      {/* Line of Sight System */}
      <div className="mt-8 p-6 bg-gradient-to-r from-violet-500/10 to-emerald-500/10 rounded-lg border border-violet-500/30">
        <h2 className="text-xl font-semibold mb-4 text-violet-400">Systeme Line of Sight (LoS)</h2>

        {/* Two grids visualization */}
        <div className="mb-6 p-4 bg-zinc-800 rounded">
          <h3 className="font-medium text-sky-400 mb-3 text-center">Combat: 2 grilles 4x4 face a face (style Canaan Online)</h3>
          <div className="flex justify-center items-center gap-8 text-xs font-mono">
            <div className="text-center">
              <div className="text-emerald-400 mb-2">ALLIES</div>
              <div className="space-y-1">
                <div className="flex gap-1">{['T1','T2','T3','T4'].map(t => <div key={t} className="w-8 h-6 bg-emerald-500/30 border border-emerald-500/50 rounded flex items-center justify-center text-[10px]">{t}</div>)}</div>
                <div className="flex gap-1">{['','','',''].map((t,i) => <div key={i} className="w-8 h-6 bg-zinc-700/30 border border-zinc-600/50 rounded"></div>)}</div>
                <div className="flex gap-1">{['D1','','D2',''].map((t,i) => <div key={i} className={`w-8 h-6 ${t ? 'bg-orange-500/30 border-orange-500/50' : 'bg-zinc-700/30 border-zinc-600/50'} border rounded flex items-center justify-center text-[10px]`}>{t}</div>)}</div>
                <div className="flex gap-1">{['H1','','H2',''].map((t,i) => <div key={i} className={`w-8 h-6 ${t ? 'bg-emerald-500/30 border-emerald-500/50' : 'bg-zinc-700/30 border-zinc-600/50'} border rounded flex items-center justify-center text-[10px]`}>{t}</div>)}</div>
              </div>
            </div>
            <div className="text-2xl text-zinc-500">VS</div>
            <div className="text-center">
              <div className="text-rose-400 mb-2">ENNEMIS</div>
              <div className="space-y-1">
                <div className="flex gap-1">{['E1','','E2',''].map((t,i) => <div key={i} className={`w-8 h-6 ${t ? 'bg-rose-500/30 border-rose-500/50' : 'bg-zinc-700/30 border-zinc-600/50'} border rounded flex items-center justify-center text-[10px]`}>{t}</div>)}</div>
                <div className="flex gap-1">{['','','',''].map((t,i) => <div key={i} className="w-8 h-6 bg-zinc-700/30 border border-zinc-600/50 rounded"></div>)}</div>
                <div className="flex gap-1">{['E5','','',''].map((t,i) => <div key={i} className={`w-8 h-6 ${t ? 'bg-rose-500/30 border-rose-500/50' : 'bg-zinc-700/30 border-zinc-600/50'} border rounded flex items-center justify-center text-[10px]`}>{t}</div>)}</div>
                <div className="flex gap-1">{['E9','','',''].map((t,i) => <div key={i} className={`w-8 h-6 ${t ? 'bg-rose-500/30 border-rose-500/50' : 'bg-zinc-700/30 border-zinc-600/50'} border rounded flex items-center justify-center text-[10px]`}>{t}</div>)}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-emerald-400 mb-2">Regles LoS</h3>
            <ul className="text-sm text-zinc-300 space-y-2">
              <li><span className="text-amber-400">Core rule:</span> Cible bloquee si elle a quelqu'un DEVANT ELLE (sa grille)</li>
              <li><span className="text-amber-400">Auto-attacks:</span> Check LoS - cibles bloquees non cliquables</li>
              <li><span className="text-amber-400">Spells:</span> Par defaut ignorent LoS (configurable par spell)</li>
              <li><span className="text-amber-400">Invocations:</span> Bloquent LoS comme les joueurs</li>
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-sky-400 mb-2">Exemple</h3>
            <div className="text-sm text-zinc-400 bg-zinc-800 p-3 rounded space-y-2">
              <p><span className="text-rose-400">E9</span> (healer back) a <span className="text-rose-400">E5</span> et <span className="text-rose-400">E1</span> devant lui</p>
              <p>→ <span className="text-red-400">E9 non cliquable</span> pour auto-attack</p>
              <p><span className="text-rose-400">E2</span> (front) n'a personne devant</p>
              <p>→ <span className="text-emerald-400">E2 cliquable</span></p>
              <p className="text-violet-400 mt-2">Spell AOE = toutes cibles selectionnables</p>
            </div>
          </div>
        </div>
        <div className="mt-4 p-3 bg-zinc-800 rounded">
          <h4 className="font-medium text-amber-400 mb-2">Pourquoi 4x4 + LoS?</h4>
          <ul className="text-sm text-zinc-400 space-y-1">
            <li>• Mort du tank = backline exposee (healer devient cliquable)</li>
            <li>• Teleport/Dash deviennent essentiels (repositionnement)</li>
            <li>• Invocations tank = bodyblock strategique</li>
            <li>• 16 slots avec 10 joueurs = place pour summons + mouvement</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
