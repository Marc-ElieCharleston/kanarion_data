'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export type ViewMode = 'dev' | 'player';

type ViewModeContextType = {
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
  isDev: boolean;
  isPlayer: boolean;
};

const ViewModeContext = createContext<ViewModeContextType | null>(null);

export function useViewMode() {
  const context = useContext(ViewModeContext);
  if (!context) {
    throw new Error('useViewMode must be used within a ViewModeProvider');
  }
  return context;
}

export function ViewModeProvider({ children }: { children: ReactNode }) {
  // Use lazy initialization to read from localStorage only once
  const [viewMode, setViewModeState] = useState<ViewMode>(() => {
    if (typeof window === 'undefined') return 'dev';
    const saved = localStorage.getItem('viewMode');
    if (saved === 'dev' || saved === 'player') return saved;
    return 'dev';
  });

  const setViewMode = useCallback((newMode: ViewMode) => {
    setViewModeState(newMode);
    if (typeof window !== 'undefined') {
      localStorage.setItem('viewMode', newMode);
    }
  }, []);

  return (
    <ViewModeContext.Provider
      value={{
        viewMode,
        setViewMode,
        isDev: viewMode === 'dev',
        isPlayer: viewMode === 'player',
      }}
    >
      {children}
    </ViewModeContext.Provider>
  );
}
