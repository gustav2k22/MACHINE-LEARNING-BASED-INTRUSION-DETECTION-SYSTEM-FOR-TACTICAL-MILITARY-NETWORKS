/**
 * @fileoverview Page 1 — Live Monitoring Dashboard.
 * Displays real-time network traffic analysis including:
 *  - KPI cards (packets analyzed, attacks detected, false positive rate, uptime)
 *  - Animated tactical threat map
 *  - 60-minute threat timeline (area chart)
 *  - Attack type distribution (donut chart)
 *  - Live scrolling traffic feed table
 *  - Active alerts sidebar
 */

import { useState, useRef, useMemo, useEffect } from 'react';
import {
  AreaChart, Area, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { Activity, AlertTriangle, Target, Gauge, Globe, TrendingUp, Crosshair, Radio, AlertCircle, Eye } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { COLORS } from '../data/constants';
import { Panel, PanelHeading } from '../components/Panel';
import { KPICard } from '../components/KPICard';
import { SeverityBadge } from '../components/SeverityBadge';
import { ThreatMap } from '../components/ThreatMap';

/**
 * Live Monitoring Dashboard page.
 * @param {object} props
 * @param {Array} props.packets - Live packet feed from useSimulation
 * @param {Array} props.timeline - 60-min timeline data
 * @param {number} props.attackCount - Running count of attacks detected
 * @param {number} props.totalPackets - Running count of packets analyzed
 */
export function DashboardPage({ packets, timeline, attackCount, totalPackets }) {
  const { colors } = useTheme();
  const feedRef = useRef(null);
  const [paused, setPaused] = useState(false);

  /** Show the 50 most recent packets in the traffic feed */
  const displayPackets = useMemo(() => packets.slice(0, 50), [packets]);

  /** Auto-scroll the traffic feed to the top when new packets arrive */
  useEffect(() => {
    if (!paused && feedRef.current) feedRef.current.scrollTop = 0;
  }, [packets, paused]);

  /** Aggregate attack type distribution from recent packets */
  const attackDistribution = useMemo(() => {
    const counts = { DoS: 0, Probe: 0, R2L: 0, U2R: 0, DDoS: 0 };
    packets
      .filter((p) => p.prediction === 'ATTACK')
      .forEach((p) => { if (p.attackType) counts[p.attackType]++; });
    return Object.entries(counts).map(([name, value]) => ({
      name,
      value: value || Math.floor(Math.random() * 20 + 5),
    }));
  }, [packets]);

  const pieColors = [COLORS.crimson, COLORS.amber, COLORS.purple, '#ec4899', '#f97316'];

  /** 5 most recent attack alerts for the sidebar */
  const recentAlerts = useMemo(
    () => packets.filter((p) => p.prediction === 'ATTACK').slice(0, 5),
    [packets],
  );

  const chartTooltipStyle = {
    background: colors.charcoal,
    border: `1px solid ${colors.border}`,
    fontFamily: 'Space Mono',
    fontSize: 11,
    color: colors.white,
  };

  return (
    <div className="space-y-4">
      {/* KPI Row */}
      <div className="flex gap-4 flex-wrap">
        <KPICard label="Packets Analyzed (Today)" value={totalPackets.toLocaleString()} icon={Activity} color={colors.cyan} trend={12} />
        <KPICard label="Attacks Detected" value={attackCount.toLocaleString()} icon={AlertTriangle} color={colors.crimson} trend={8} />
        <KPICard label="False Positive Rate" value="0.12%" icon={Target} color={colors.amber} trend={-3} />
        <KPICard label="System Uptime" value="99.97%" icon={Gauge} color={colors.green} />
      </div>

      {/* Tactical Threat Map */}
      <Panel>
        <PanelHeading icon={Globe}>TACTICAL THREAT MAP</PanelHeading>
        <div className="h-[200px]">
          <ThreatMap packets={packets} />
        </div>
      </Panel>

      {/* Timeline + Distribution Row */}
      <div className="flex gap-4 flex-wrap">
        <Panel className="flex-2 min-w-[400px]">
          <PanelHeading icon={TrendingUp}>THREAT TIMELINE (60 MIN)</PanelHeading>
          <div className="h-[220px]">
            <ResponsiveContainer>
              <AreaChart data={timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                <XAxis dataKey="time" stroke={colors.muted} tick={{ fontSize: 10 }} interval={9} />
                <YAxis stroke={colors.muted} tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={chartTooltipStyle} />
                <Area type="monotone" dataKey="normal" stroke={COLORS.green} fill={COLORS.green + '20'} strokeWidth={2} name="Normal" />
                <Area type="monotone" dataKey="attacks" stroke={COLORS.crimson} fill={COLORS.crimson + '20'} strokeWidth={2} name="Attacks" />
                <Legend wrapperStyle={{ fontSize: 10 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel className="flex-1 min-w-[250px]">
          <PanelHeading icon={Crosshair}>ATTACK DISTRIBUTION</PanelHeading>
          <div className="h-[220px]">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={attackDistribution} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3} dataKey="value" stroke="none">
                  {attackDistribution.map((_, i) => <Cell key={i} fill={pieColors[i]} />)}
                </Pie>
                <Tooltip contentStyle={chartTooltipStyle} />
                <Legend wrapperStyle={{ fontSize: 10 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      {/* Traffic Feed + Active Alerts Row */}
      <div className="flex gap-4 flex-wrap">
        {/* Live Traffic Feed */}
        <Panel className="flex-3 min-w-[500px]" noPadding>
          <div className="p-4 pb-2 flex justify-between items-center border-b" style={{ borderColor: colors.border }}>
            <PanelHeading icon={Radio}>LIVE TRAFFIC FEED</PanelHeading>
            <button
              onClick={() => setPaused(!paused)}
              aria-label={paused ? 'Resume live feed' : 'Pause live feed'}
              className="text-[10px] px-3 py-1 border transition-colors hover:text-[#00D4FF] hover:border-[#00D4FF]"
              style={{ borderColor: colors.border, color: colors.muted }}
            >
              {paused ? 'RESUME' : 'PAUSE'}
            </button>
          </div>
          <div
            ref={feedRef}
            className="overflow-auto max-h-[300px]"
            onMouseEnter={() => setPaused(true)}
            onMouseLeave={() => setPaused(false)}
          >
            <table className="w-full text-[11px]">
              <thead className="sticky top-0 z-10" style={{ background: colors.darkPanel }}>
                <tr style={{ color: colors.muted }}>
                  {['TIME', 'SRC IP', 'DST IP', 'PROTO', 'FEATURES', 'VERDICT', 'CONF%', 'MODEL'].map((h) => (
                    <th key={h} className="px-3 py-2 text-left font-display font-semibold text-[10px] uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {displayPackets.map((pkt) => (
                  <tr
                    key={pkt.id}
                    className={`border-t transition-colors ${
                      pkt.prediction === 'ATTACK' ? 'bg-[#DC2626]/5' : 'bg-[#10B981]/3'
                    } hover:bg-[#1e293b]/50`}
                    style={{ borderColor: colors.border + '80' }}
                  >
                    <td className="px-3 py-1.5" style={{ color: colors.muted }}>{pkt.timestamp.split(' ')[1]}</td>
                    <td className="px-3 py-1.5 font-mono">{pkt.sourceIP}</td>
                    <td className="px-3 py-1.5 font-mono">{pkt.destIP}</td>
                    <td className="px-3 py-1.5">{pkt.protocol}</td>
                    <td className="px-3 py-1.5 max-w-[150px] truncate" style={{ color: colors.muted }}>{pkt.featureSummary}</td>
                    <td className="px-3 py-1.5">
                      <span className={`px-1.5 py-0.5 text-[9px] font-bold ${
                        pkt.prediction === 'ATTACK' ? 'bg-[#DC2626]/20 text-[#DC2626]' : 'bg-[#10B981]/20 text-[#10B981]'
                      }`}>
                        {pkt.prediction}
                      </span>
                    </td>
                    <td className="px-3 py-1.5 font-mono" style={{ color: pkt.prediction === 'ATTACK' ? COLORS.crimson : COLORS.green }}>
                      {pkt.confidence.toFixed(1)}%
                    </td>
                    <td className="px-3 py-1.5" style={{ color: colors.muted }}>{pkt.model}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        {/* Active Alerts Sidebar */}
        <Panel className="flex-1 min-w-[280px]">
          <PanelHeading icon={AlertCircle}>ACTIVE ALERTS</PanelHeading>
          <div className="space-y-2">
            {recentAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-3 border ${
                  alert.severity === 'CRITICAL'
                    ? 'border-[#DC2626]/50 bg-[#DC2626]/5'
                    : 'border-[#F59E0B]/30 bg-[#F59E0B]/5'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <SeverityBadge severity={alert.severity} />
                  <span className="text-[9px]" style={{ color: colors.muted }}>{alert.timestamp.split(' ')[1]}</span>
                </div>
                <p className="text-[11px] font-mono">{alert.sourceIP}</p>
                <p className="text-[10px] mt-0.5" style={{ color: colors.slate }}>
                  {alert.attackType} -- Conf: {alert.confidence.toFixed(1)}%
                </p>
                <button
                  className="mt-2 text-[9px] px-2 py-0.5 border border-[#00D4FF]/30 text-[#00D4FF] hover:bg-[#00D4FF]/10 transition-colors flex items-center gap-1"
                  aria-label={`Investigate alert from ${alert.sourceIP}`}
                >
                  <Eye size={10} />INVESTIGATE
                </button>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
