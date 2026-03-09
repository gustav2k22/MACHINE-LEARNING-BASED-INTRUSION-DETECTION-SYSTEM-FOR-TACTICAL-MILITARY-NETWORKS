/**
 * @fileoverview Sidebar navigation component for the SENTINEL-IDS dashboard.
 * Contains the SENTINEL-IDS branding, navigation links with icons,
 * and a system status footer.
 */

import { Shield, Monitor, Crosshair, BarChart3, Layers, Bell } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

/** Navigation items — each maps to a page */
const NAV_ITEMS = [
  { id: 'dashboard', label: 'DASHBOARD',     icon: Monitor },
  { id: 'test',      label: 'SCENARIO TEST', icon: Crosshair },
  { id: 'model',     label: 'MODEL PERF',    icon: BarChart3 },
  { id: 'arch',      label: 'ARCHITECTURE',  icon: Layers },
  { id: 'alerts',    label: 'ALERTS',        icon: Bell },
];

/**
 * Left sidebar with branding, navigation, and system status.
 * @param {object} props
 * @param {string} props.activePage - Currently active page ID
 * @param {Function} props.onNavigate - Callback when a nav item is clicked
 */
export function Sidebar({ activePage, onNavigate }) {
  const { colors } = useTheme();

  return (
    <div
      className="w-[220px] shrink-0 border-r flex flex-col transition-colors duration-200"
      style={{ background: colors.darkPanel, borderColor: colors.border }}
    >
      {/* Branding */}
      <div className="p-4 border-b" style={{ borderColor: colors.border }}>
        <div className="flex items-center gap-2 mb-1">
          <Shield size={20} className="text-[#00D4FF]" />
          <span className="font-display font-bold text-lg tracking-[.15em] text-[#00D4FF]">SENTINEL-IDS</span>
        </div>
        <p className="text-[8px] text-[#DC2626] tracking-[.3em] font-display border border-[#DC2626]/30 px-2 py-0.5 inline-block mt-1">
          CLASSIFIED // FOUO
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4" aria-label="Main navigation">
        {NAV_ITEMS.map((item) => {
          const active = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              aria-current={active ? 'page' : undefined}
              className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-all border-l-2 ${
                active
                  ? 'bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]'
                  : 'text-[#64748b] hover:text-[#94a3b8] hover:bg-[#111827]/50 border-transparent'
              }`}
            >
              <item.icon size={18} />
              <span className="text-[11px] font-display font-bold tracking-[.15em]">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div className="p-4 border-t" style={{ borderColor: colors.border }}>
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 bg-[#10B981] animate-pulse-badge" />
          <span className="text-[9px] text-[#10B981]">SYSTEM ONLINE</span>
        </div>
        <p className="text-[8px]" style={{ color: colors.deepSlate }}>v2.1.0 // 8 datasets loaded</p>
        <p className="text-[8px]" style={{ color: colors.deepSlate }}>5 models operational</p>
      </div>
    </div>
  );
}
