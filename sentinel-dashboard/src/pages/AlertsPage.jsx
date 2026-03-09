/**
 * @fileoverview Page 5 — Alerts & Reports.
 * Provides a filterable, paginated alert feed with:
 *  - Search by IP address
 *  - Severity and attack type filters
 *  - CSV export capability
 *  - Alert detail modal with packet features and recommended actions
 */

import { useState, useMemo } from 'react';
import { Search, Filter, Download, Eye, AlertTriangle, X } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { COLORS, ATTACK_TYPES } from '../data/constants';
import { generateAlerts } from '../data/generators';
import { Panel } from '../components/Panel';
import { SeverityBadge } from '../components/SeverityBadge';

const PAGE_SIZE = 15;

/**
 * Alerts & Reports page — browse, filter, and inspect security alerts.
 */
export function AlertsPage() {
  const { colors } = useTheme();
  const [alerts] = useState(() => generateAlerts(80));
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedAlert, setSelectedAlert] = useState(null);

  /** Apply all active filters to the alert list */
  const filteredAlerts = useMemo(() => {
    return alerts.filter((alert) => {
      if (severityFilter !== 'ALL' && alert.severity !== severityFilter) return false;
      if (typeFilter !== 'ALL' && alert.attackType !== typeFilter) return false;
      if (searchQuery && !alert.sourceIP.includes(searchQuery) && !alert.destIP.includes(searchQuery)) return false;
      return true;
    });
  }, [alerts, severityFilter, typeFilter, searchQuery]);

  /** Current page slice */
  const pagedAlerts = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredAlerts.slice(start, start + PAGE_SIZE);
  }, [filteredAlerts, currentPage]);

  const totalPages = Math.ceil(filteredAlerts.length / PAGE_SIZE);

  /** Export filtered alerts as CSV download */
  const exportCSV = () => {
    const headers = ['ID', 'Timestamp', 'Source IP', 'Dest IP', 'Type', 'Severity', 'Confidence', 'Dataset', 'Status'];
    const rows = filteredAlerts.map((a) =>
      [a.id, a.timestamp, a.sourceIP, a.destIP, a.attackType, a.severity, a.confidence, a.dataset, a.status].join(',')
    );
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sentinel-alerts-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      {/* Filter Bar */}
      <Panel>
        <div className="flex gap-3 flex-wrap items-center">
          {/* Search */}
          <div className="flex items-center gap-2 border px-3 py-1.5" style={{ background: colors.navy, borderColor: colors.border }}>
            <Search size={14} style={{ color: colors.muted }} />
            <input
              type="text"
              placeholder="Search IP..."
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
              className="bg-transparent text-[11px] font-mono outline-none w-32"
              style={{ color: colors.white }}
              aria-label="Search by IP address"
            />
          </div>

          {/* Severity Filters */}
          <div className="flex items-center gap-2">
            <Filter size={14} style={{ color: colors.muted }} />
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => (
              <button
                key={sev}
                onClick={() => { setSeverityFilter(sev); setCurrentPage(1); }}
                className={`text-[9px] px-2 py-1 border transition-all ${
                  severityFilter === sev
                    ? 'border-[#00D4FF] text-[#00D4FF] bg-[#00D4FF]/10'
                    : 'border-[#1e293b] text-[#64748b]'
                }`}
                aria-pressed={severityFilter === sev}
              >
                {sev}
              </button>
            ))}
          </div>

          {/* Attack Type Filters */}
          <div className="flex items-center gap-2">
            {['ALL', ...ATTACK_TYPES].map((type) => (
              <button
                key={type}
                onClick={() => { setTypeFilter(type); setCurrentPage(1); }}
                className={`text-[9px] px-2 py-1 border transition-all ${
                  typeFilter === type
                    ? 'border-[#F59E0B] text-[#F59E0B] bg-[#F59E0B]/10'
                    : 'border-[#1e293b] text-[#64748b]'
                }`}
                aria-pressed={typeFilter === type}
              >
                {type}
              </button>
            ))}
          </div>

          {/* Export Button */}
          <div className="ml-auto">
            <button
              onClick={exportCSV}
              className="flex items-center gap-1 text-[10px] px-3 py-1.5 border border-[#00D4FF]/30 text-[#00D4FF] hover:bg-[#00D4FF]/10 transition-colors"
              aria-label="Export alerts as CSV"
            >
              <Download size={12} />EXPORT REPORT (CSV)
            </button>
          </div>
        </div>
      </Panel>

      {/* Alerts Table */}
      <Panel noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-[11px]">
            <thead style={{ background: colors.darkPanel }}>
              <tr style={{ color: colors.muted }}>
                {['ID', 'TIMESTAMP', 'SRC IP', 'DST IP', 'TYPE', 'SEVERITY', 'CONF%', 'DATASET', 'STATUS', ''].map((h) => (
                  <th key={h} className="px-3 py-2.5 text-left font-display text-[10px] uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {pagedAlerts.map((alert) => (
                <tr
                  key={alert.id}
                  className="border-t hover:bg-[#1e293b]/30 cursor-pointer transition-colors"
                  style={{ borderColor: colors.border + '80' }}
                  onClick={() => setSelectedAlert(alert)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && setSelectedAlert(alert)}
                  aria-label={`View alert ${alert.id} details`}
                >
                  <td className="px-3 py-2 font-mono" style={{ color: colors.muted }}>#{String(alert.id).padStart(4, '0')}</td>
                  <td className="px-3 py-2 font-mono" style={{ color: colors.slate }}>{alert.timestamp}</td>
                  <td className="px-3 py-2 font-mono">{alert.sourceIP}</td>
                  <td className="px-3 py-2 font-mono">{alert.destIP}</td>
                  <td className="px-3 py-2">{alert.attackType}</td>
                  <td className="px-3 py-2"><SeverityBadge severity={alert.severity} /></td>
                  <td className="px-3 py-2 font-mono" style={{ color: parseFloat(alert.confidence) > 95 ? COLORS.crimson : COLORS.amber }}>
                    {alert.confidence}%
                  </td>
                  <td className="px-3 py-2" style={{ color: colors.muted }}>{alert.dataset}</td>
                  <td className="px-3 py-2">
                    <span className={`px-1.5 py-0.5 text-[8px] ${
                      alert.status === 'OPEN' ? 'bg-[#DC2626]/20 text-[#DC2626]' : 'bg-[#10B981]/20 text-[#10B981]'
                    }`}>
                      {alert.status}
                    </span>
                  </td>
                  <td className="px-3 py-2"><Eye size={12} className="text-[#00D4FF]" /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex justify-between items-center px-4 py-3 border-t" style={{ borderColor: colors.border }}>
          <span className="text-[10px]" style={{ color: colors.muted }}>{filteredAlerts.length} alerts</span>
          <div className="flex gap-1">
            {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                onClick={() => setCurrentPage(p)}
                className={`w-7 h-7 text-[10px] border transition-all ${
                  currentPage === p
                    ? 'border-[#00D4FF] text-[#00D4FF] bg-[#00D4FF]/10'
                    : 'border-[#1e293b] text-[#64748b]'
                }`}
                aria-label={`Page ${p}`}
                aria-current={currentPage === p ? 'page' : undefined}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </Panel>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div
          className="fixed inset-0 z-60 flex items-center justify-center bg-black/70"
          onClick={() => setSelectedAlert(null)}
          role="dialog"
          aria-modal="true"
          aria-label={`Alert ${selectedAlert.id} details`}
        >
          <div
            className="border w-full max-w-xl mx-4"
            style={{ background: colors.charcoal, borderColor: colors.border }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex justify-between items-center px-4 py-3 border-b" style={{ borderColor: colors.border }}>
              <div className="flex items-center gap-2">
                <AlertTriangle size={16} className="text-[#DC2626]" />
                <h3 className="font-display font-bold text-sm tracking-wider" style={{ color: colors.white }}>
                  ALERT #{String(selectedAlert.id).padStart(4, '0')}
                </h3>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="hover:opacity-80 transition-opacity"
                style={{ color: colors.muted }}
                aria-label="Close alert details"
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-4 space-y-4">
              <div className="flex gap-3 items-center">
                <SeverityBadge severity={selectedAlert.severity} />
                <span className="text-[10px]" style={{ color: colors.slate }}>{selectedAlert.timestamp}</span>
              </div>

              {/* Key Details Grid */}
              <div className="grid grid-cols-2 gap-3">
                {[
                  ['Source IP', selectedAlert.sourceIP],
                  ['Dest IP', selectedAlert.destIP],
                  ['Attack Type', selectedAlert.attackType],
                  ['Confidence', selectedAlert.confidence + '%'],
                  ['Model', 'StackingEnsemble'],
                  ['Dataset', selectedAlert.dataset],
                ].map(([label, value]) => (
                  <div key={label} className="p-2 border" style={{ background: colors.navy, borderColor: colors.border }}>
                    <p className="text-[8px] tracking-wider" style={{ color: colors.muted }}>{label}</p>
                    <p className="text-[11px] font-mono" style={{ color: colors.white }}>{value}</p>
                  </div>
                ))}
              </div>

              {/* Packet Features */}
              <div>
                <p className="text-[10px] font-display tracking-wider uppercase mb-2" style={{ color: colors.muted }}>
                  Packet Features
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(selectedAlert.features).map(([key, value]) => (
                    <div key={key} className="p-2 border" style={{ background: colors.navy, borderColor: colors.border }}>
                      <p className="text-[8px]" style={{ color: colors.muted }}>{key}</p>
                      <p className="text-[11px] font-mono" style={{ color: colors.white }}>{value}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommended Actions */}
              <div>
                <p className="text-[10px] font-display tracking-wider uppercase mb-2" style={{ color: colors.muted }}>
                  Recommended Action
                </p>
                <div className="flex gap-2">
                  {[
                    { label: 'BLOCK IP',  color: COLORS.crimson },
                    { label: 'MONITOR',   color: COLORS.cyan },
                    { label: 'ESCALATE',  color: COLORS.amber },
                  ].map((action) => (
                    <button
                      key={action.label}
                      className="flex-1 py-2 text-[10px] font-display font-bold tracking-wider border transition-all hover:opacity-80"
                      style={{
                        borderColor: action.color,
                        color: action.color,
                        background: action.color + '10',
                      }}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
