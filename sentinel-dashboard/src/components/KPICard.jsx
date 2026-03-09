/**
 * @fileoverview Key Performance Indicator card component.
 * Displays a metric with label, value, trend arrow, and accent-colored icon.
 */

import { ArrowUp, ArrowDown } from 'lucide-react';
import { Panel } from './Panel';
import { useTheme } from '../context/ThemeContext';

/**
 * KPI metric card shown at the top of the Live Monitoring page.
 * @param {object} props
 * @param {string} props.label - Short uppercase label (e.g. "PACKETS ANALYZED")
 * @param {string|number} props.value - Formatted metric value
 * @param {React.ComponentType} props.icon - Lucide icon component
 * @param {string} props.color - Accent color hex for icon and value
 * @param {number} [props.trend] - Percent change vs. last hour (positive = up, negative = down)
 */
export function KPICard({ label, value, icon: Icon, color, trend }) {
  const { colors } = useTheme();

  return (
    <Panel className="flex-1 min-w-[200px]">
      <div className="flex items-start justify-between">
        <div>
          <p
            className="text-[10px] tracking-[.15em] uppercase font-display font-semibold mb-1"
            style={{ color: colors.muted }}
          >
            {label}
          </p>
          <p className="text-2xl font-display font-bold" style={{ color }}>
            {value}
          </p>
          {trend != null && (
            <p
              className={`text-[10px] mt-1 flex items-center gap-1 ${
                trend > 0 ? 'text-[#DC2626]' : 'text-[#10B981]'
              }`}
            >
              {trend > 0 ? <ArrowUp size={10} /> : <ArrowDown size={10} />}
              {Math.abs(trend)}% vs last hr
            </p>
          )}
        </div>
        <div
          className="p-2"
          style={{
            background: colors.navy,
            border: `1px solid ${color}33`,
          }}
        >
          <Icon size={20} style={{ color }} />
        </div>
      </div>
    </Panel>
  );
}
