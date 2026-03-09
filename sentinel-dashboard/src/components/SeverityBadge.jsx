/**
 * @fileoverview Severity badge component for alert severity levels.
 * Renders a color-coded inline badge (CRITICAL, HIGH, MEDIUM, LOW).
 */

/**
 * Inline severity indicator with color coding and optional pulse animation.
 * @param {object} props
 * @param {'CRITICAL'|'HIGH'|'MEDIUM'|'LOW'} props.severity - Alert severity level
 */
export function SeverityBadge({ severity }) {
  const styles = {
    CRITICAL: 'bg-[#DC2626]/20 text-[#DC2626] border-[#DC2626] animate-pulse-badge',
    HIGH:     'bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]',
    MEDIUM:   'bg-[#00D4FF]/20 text-[#00D4FF] border-[#00D4FF]',
    LOW:      'bg-[#10B981]/20 text-[#10B981] border-[#10B981]',
  };

  return (
    <span
      className={`px-2 py-0.5 text-[10px] font-bold tracking-wider border ${styles[severity] || styles.LOW}`}
      role="status"
      aria-label={`Severity: ${severity}`}
    >
      {severity}
    </span>
  );
}
