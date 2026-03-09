/**
 * @fileoverview Reusable panel and heading components for the SENTINEL-IDS dashboard.
 * Panel provides a themed container with border accents.
 * PanelHeading renders an uppercase, letter-spaced section title with an optional icon.
 */

import { useTheme } from '../context/ThemeContext';

/**
 * Themed container panel with border and background that responds to light/dark mode.
 * @param {object} props
 * @param {React.ReactNode} props.children
 * @param {string} [props.className] - Additional Tailwind classes
 * @param {boolean} [props.noPadding] - If true, removes default p-4 padding
 */
export function Panel({ children, className = '', noPadding = false }) {
  const { colors } = useTheme();
  return (
    <div
      className={`border transition-colors duration-200 ${noPadding ? '' : 'p-4'} ${className}`}
      style={{
        background: colors.charcoal,
        borderColor: colors.border,
        animation: 'fade-in .5s ease-out forwards',
      }}
    >
      {children}
    </div>
  );
}

/**
 * Section heading inside a panel — uppercase, letter-spaced, with optional Lucide icon.
 * @param {object} props
 * @param {React.ReactNode} props.children - Heading text
 * @param {React.ComponentType} [props.icon] - Lucide icon component
 */
export function PanelHeading({ children, icon: Icon }) {
  const { colors } = useTheme();
  return (
    <div
      className="flex items-center gap-2 mb-3 pb-2 border-b"
      style={{ borderColor: colors.border }}
    >
      {Icon && <Icon size={16} style={{ color: colors.cyan }} />}
      <h3
        className="font-display font-bold text-xs tracking-[.2em] uppercase"
        style={{ color: colors.slate }}
      >
        {children}
      </h3>
    </div>
  );
}
