/**
 * @fileoverview Animated SVG tactical threat map component.
 * Renders a grid of 12 military network nodes with animated connection lines
 * that visualize real-time packet flow between network segments.
 * Attack connections are shown as pulsing red dashed lines.
 */

import { useMemo } from 'react';
import { NETWORK_NODES } from '../data/constants';
import { useTheme } from '../context/ThemeContext';

/**
 * Tactical network threat map displaying nodes and animated traffic connections.
 * @param {object} props
 * @param {Array<object>} props.packets - Recent packet data used to draw connection lines
 */
export function ThreatMap({ packets }) {
  const { colors } = useTheme();

  /** Static node positions computed once — 12 nodes in a 4x3 grid with jitter */
  const nodes = useMemo(() => {
    return NETWORK_NODES.map((label, i) => ({
      id: i,
      x: 40 + (i % 4) * 150 + Math.random() * 30,
      y: 25 + Math.floor(i / 4) * 60 + Math.random() * 15,
      label,
      isCritical: i < 3,
    }));
  }, []);

  /** Derive connection lines from recent packets, mapping to source/dest nodes */
  const connections = useMemo(() => {
    return (packets || []).slice(0, 8).map((packet, i) => {
      const src = nodes[i % 12];
      const dst = nodes[(i + 3 + Math.floor(Math.random() * 4)) % 12];
      return { ...packet, x1: src.x, y1: src.y, x2: dst.x, y2: dst.y };
    });
  }, [packets, nodes]);

  return (
    <svg
      viewBox="0 0 640 210"
      className="w-full h-full"
      role="img"
      aria-label="Tactical network threat map showing connections between military network nodes"
      style={{ background: `radial-gradient(ellipse at center, #0d1b2a, ${colors.navy})` }}
    >
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Grid lines */}
      {Array.from({ length: 22 }, (_, i) => (
        <line key={`vg${i}`} x1={i * 30} y1={0} x2={i * 30} y2={210} stroke={colors.border} strokeWidth={0.3} />
      ))}
      {Array.from({ length: 11 }, (_, i) => (
        <line key={`hg${i}`} x1={0} y1={i * 20} x2={640} y2={i * 20} stroke={colors.border} strokeWidth={0.3} />
      ))}

      {/* Connection lines between nodes */}
      {connections.map((conn, i) => (
        <g key={`conn-${i}`}>
          <line
            x1={conn.x1} y1={conn.y1} x2={conn.x2} y2={conn.y2}
            stroke={conn.prediction === 'ATTACK' ? colors.crimson : colors.cyan}
            strokeWidth={conn.prediction === 'ATTACK' ? 1.5 : 0.7}
            opacity={0.6}
            filter="url(#glow)"
            strokeDasharray={conn.prediction === 'ATTACK' ? '4,4' : 'none'}
          >
            <animate attributeName="opacity" values=".3;.8;.3" dur={`${2 + i * 0.3}s`} repeatCount="indefinite" />
          </line>
          {conn.prediction === 'ATTACK' && (
            <circle cx={(conn.x1 + conn.x2) / 2} cy={(conn.y1 + conn.y2) / 2} r={3} fill={colors.crimson} opacity={0.8}>
              <animate attributeName="r" values="2;5;2" dur="1.5s" repeatCount="indefinite" />
            </circle>
          )}
        </g>
      ))}

      {/* Network nodes */}
      {nodes.map((node) => (
        <g key={node.id}>
          <rect
            x={node.x - 8} y={node.y - 8} width={16} height={16}
            fill={node.isCritical ? colors.cyan + '33' : colors.border}
            stroke={node.isCritical ? colors.cyan : '#334155'}
            strokeWidth={1}
          />
          <rect x={node.x - 3} y={node.y - 3} width={6} height={6} fill={node.isCritical ? colors.cyan : colors.green} />
          <text x={node.x} y={node.y + 20} textAnchor="middle" fill={colors.muted} fontSize={6} fontFamily="Space Mono">
            {node.label}
          </text>
        </g>
      ))}
    </svg>
  );
}
