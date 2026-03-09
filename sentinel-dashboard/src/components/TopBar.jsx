/**
 * @fileoverview Top status bar component for the SENTINEL-IDS dashboard.
 * Displays the SENTINEL-IDS label, live UTC clock, network status indicator,
 * threat level badge with pulse animation, and a dark/light theme toggle.
 */

import { Shield, Clock, AlertTriangle, Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { COLORS } from '../data/constants';

/**
 * Resolves threat level to its accent color.
 * @param {string} level - CRITICAL | HIGH | MODERATE | LOW
 * @returns {string} Hex color code
 */
function threatColor(level) {
  if (level === 'CRITICAL') return COLORS.crimson;
  if (level === 'HIGH') return COLORS.amber;
  if (level === 'MODERATE') return COLORS.amber;
  return COLORS.green;
}

/**
 * Top bar with system metadata and theme toggle.
 * @param {object} props
 * @param {Date} props.clock - Current time
 * @param {string} props.threatLevel - Current threat level string
 */
export function TopBar({ clock, threatLevel }) {
  const { colors, isDark, toggleTheme } = useTheme();
  const color = threatColor(threatLevel);
  const shouldPulse = threatLevel === 'CRITICAL' || threatLevel === 'HIGH';

  return (
    <div
      className="h-12 border-b flex items-center px-4 gap-4 shrink-0 transition-colors duration-200"
      style={{ background: colors.darkPanel, borderColor: colors.border }}
      role="banner"
    >
      {/* Brand */}
      <div className="flex items-center gap-2">
        <Shield size={14} className="text-[#00D4FF]" />
        <span className="font-display font-bold text-xs tracking-[.15em]" style={{ color: colors.slate }}>
          SENTINEL-IDS
        </span>
      </div>

      <div className="flex-1" />

      {/* Live Clock */}
      <div className="flex items-center gap-2">
        <Clock size={12} style={{ color: colors.muted }} />
        <span className="text-[11px] font-mono" style={{ color: colors.slate }}>
          {clock.toISOString().replace('T', ' ').slice(0, 19)} UTC
        </span>
      </div>

      <div className="h-6 w-px" style={{ background: colors.border }} />

      {/* Network Status */}
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 bg-[#10B981]" />
        <span className="text-[10px] text-[#10B981] font-display tracking-wider">NETWORK OK</span>
      </div>

      <div className="h-6 w-px" style={{ background: colors.border }} />

      {/* Threat Level */}
      <div
        className={`flex items-center gap-2 px-3 py-1 border ${shouldPulse ? 'animate-pulse-badge' : ''}`}
        style={{ borderColor: color, background: color + '15' }}
        role="status"
        aria-label={`Threat level: ${threatLevel}`}
      >
        <AlertTriangle size={12} style={{ color }} />
        <span className="text-[10px] font-display font-bold tracking-wider" style={{ color }}>
          THREAT: {threatLevel}
        </span>
      </div>

      <div className="h-6 w-px" style={{ background: colors.border }} />

      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className="flex items-center gap-2 px-2 py-1 border transition-all hover:border-[#00D4FF]"
        style={{ borderColor: colors.border, color: colors.muted }}
        aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
        title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      >
        {isDark ? <Sun size={14} /> : <Moon size={14} />}
        <span className="text-[9px] font-display tracking-wider">{isDark ? 'LIGHT' : 'DARK'}</span>
      </button>
    </div>
  );
}
