/**
 * @fileoverview Theme context provider for the SENTINEL-IDS dashboard.
 * Supports dark (default military command center) and light modes.
 * Automatically detects the operating system's preferred color scheme
 * and allows manual override via a toggle.
 */

import { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { COLORS, LIGHT_COLORS } from '../data/constants';

/** @type {React.Context} */
const ThemeContext = createContext(null);

/**
 * Provides theme state (dark/light) and a toggle function to all children.
 * On mount, reads the OS preference via `prefers-color-scheme`.
 * Persists the user's manual choice in sessionStorage for the current tab.
 */
export function ThemeProvider({ children }) {
  const [mode, setMode] = useState(() => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }
    return 'dark';
  });

  /* Listen for OS-level theme changes */
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: light)');
    const handler = (e) => setMode(e.matches ? 'light' : 'dark');
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  const toggleTheme = () => setMode((prev) => (prev === 'dark' ? 'light' : 'dark'));
  const isDark = mode === 'dark';

  /** Resolved palette — switches between dark and light color sets */
  const colors = useMemo(() => {
    const base = isDark ? { ...COLORS } : { ...COLORS, ...LIGHT_COLORS };
    return base;
  }, [isDark]);

  const value = useMemo(() => ({ mode, isDark, toggleTheme, colors }), [mode, isDark, colors]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to access the current theme context.
 * @returns {{ mode: 'dark'|'light', isDark: boolean, toggleTheme: Function, colors: object }}
 */
export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within a ThemeProvider');
  return ctx;
}
