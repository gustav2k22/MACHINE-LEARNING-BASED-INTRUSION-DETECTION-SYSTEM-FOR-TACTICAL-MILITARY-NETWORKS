/**
 * @fileoverview Page 2 — Scenario Testing.
 * Allows users to select pre-built attack scenarios or enter custom features,
 * run a simulated ensemble prediction, and view:
 *  - Verdict with confidence arc
 *  - Per-model breakdown bars
 *  - SHAP-style feature importance chart
 *  - Scenario history table with re-run capability
 */

import { useState, useCallback } from 'react';
import {
  BarChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { Crosshair, Settings, Zap, AlertTriangle, CheckCircle, BarChart3, Clock, RotateCcw } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { COLORS, FEATURE_KEYS } from '../data/constants';
import { SCENARIOS } from '../data/metrics';
import { simulatePrediction } from '../data/generators';
import { Panel, PanelHeading } from '../components/Panel';

/**
 * Scenario Testing page — run simulated IDS predictions on preset or custom feature vectors.
 */
export function ScenarioTestPage() {
  const { colors } = useTheme();
  const [selected, setSelected] = useState(SCENARIOS[0]);
  const [customFeatures, setCustomFeatures] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  /** Execute the prediction simulation with a 1.2s delay for realism */
  const runPrediction = useCallback(() => {
    setLoading(true);
    setResult(null);
    setTimeout(() => {
      const prediction = simulatePrediction(selected);
      setResult(prediction);
      setHistory((prev) => [prediction, ...prev].slice(0, 10));
      setLoading(false);
    }, 1200);
  }, [selected]);

  const chartTooltipStyle = {
    background: colors.charcoal,
    border: `1px solid ${colors.border}`,
    fontFamily: 'Space Mono',
    fontSize: 11,
    color: colors.white,
  };

  return (
    <div className="space-y-4">
      {/* Scenario Selector */}
      <Panel>
        <PanelHeading icon={Crosshair}>SCENARIO SELECTOR</PanelHeading>
        <div className="flex gap-2 flex-wrap">
          {SCENARIOS.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => { setSelected(scenario); setResult(null); }}
              className={`px-4 py-2 text-[11px] font-display font-bold tracking-wider uppercase border transition-all ${
                selected.id === scenario.id
                  ? 'border-[#00D4FF] bg-[#00D4FF]/10 text-[#00D4FF]'
                  : 'border-[#1e293b] text-[#64748b] hover:border-[#334155]'
              }`}
              aria-pressed={selected.id === scenario.id}
              title={scenario.description}
            >
              {scenario.name}
            </button>
          ))}
        </div>
        {selected.description && (
          <p className="text-[11px] mt-3 italic" style={{ color: colors.muted }}>{selected.description}</p>
        )}
      </Panel>

      {/* Feature Input Grid */}
      <Panel>
        <PanelHeading icon={Settings}>
          FEATURE INPUT
          {selected.id !== 'custom' && (
            <span className="text-[9px] text-[#10B981] ml-2 normal-case tracking-normal">(Auto-populated)</span>
          )}
        </PanelHeading>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          {FEATURE_KEYS.map((key) => (
            <div key={key} className="border p-2" style={{ background: colors.navy, borderColor: colors.border }}>
              <label className="text-[9px] uppercase tracking-wider block mb-1 font-display" style={{ color: colors.muted }}>
                {key}
              </label>
              <input
                type="text"
                value={selected.id === 'custom' ? (customFeatures[key] || '') : (selected.features[key] ?? '')}
                onChange={(e) => setCustomFeatures((prev) => ({ ...prev, [key]: e.target.value }))}
                readOnly={selected.id !== 'custom'}
                className="w-full bg-transparent text-[11px] font-mono outline-none border-b focus:border-[#00D4FF] pb-0.5"
                style={{ color: colors.white, borderColor: colors.border }}
                placeholder="0"
                aria-label={key}
              />
            </div>
          ))}
        </div>
      </Panel>

      {/* Analyze Button */}
      <button
        onClick={runPrediction}
        disabled={loading}
        className="w-full py-3 bg-[#00D4FF]/10 border border-[#00D4FF] text-[#00D4FF] font-display font-bold text-sm tracking-[.3em] uppercase hover:bg-[#00D4FF]/20 transition-all disabled:opacity-50 flex items-center justify-center gap-3"
        aria-busy={loading}
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-[#00D4FF] border-t-transparent animate-spin" />
            ANALYZING TRAFFIC...
          </>
        ) : (
          <><Zap size={16} />ANALYZE TRAFFIC</>
        )}
      </button>

      {/* Prediction Results */}
      {result && (
        <div className="space-y-4 animate-fade-in">
          {/* Verdict Panel */}
          <Panel className={result.isAttack ? 'border-[#DC2626]' : 'border-[#10B981]'}>
            <div className="flex flex-col md:flex-row gap-6 items-center">
              {/* Verdict Icon */}
              <div className="text-center shrink-0">
                <div
                  className={`w-32 h-32 flex items-center justify-center border-2 ${
                    result.isAttack ? 'border-[#DC2626] text-[#DC2626]' : 'border-[#10B981] text-[#10B981]'
                  }`}
                  style={result.isAttack ? { animation: 'pulse-glow 2s ease-in-out infinite' } : {}}
                >
                  {result.isAttack ? <AlertTriangle size={48} /> : <CheckCircle size={48} />}
                </div>
                <p className={`mt-2 font-display font-bold text-lg tracking-wider ${
                  result.isAttack ? 'text-[#DC2626]' : 'text-[#10B981]'
                }`}>
                  {result.isAttack ? 'ATTACK DETECTED' : 'NORMAL TRAFFIC'}
                </p>
                {result.attackType && (
                  <p className="text-[11px] text-[#F59E0B] font-display mt-1">
                    {result.attackType} -- SEVERITY: HIGH
                  </p>
                )}
              </div>

              {/* Confidence Arc + Per-Model Breakdown */}
              <div className="flex-1 w-full">
                <p className="text-[10px] uppercase tracking-wider font-display mb-2" style={{ color: colors.muted }}>
                  Ensemble Confidence
                </p>
                <div className="flex items-center gap-4">
                  {/* Confidence Arc */}
                  <div className="relative w-24 h-24 shrink-0">
                    <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                      <circle cx={50} cy={50} r={40} fill="none" stroke={colors.border} strokeWidth={8} />
                      <circle
                        cx={50} cy={50} r={40} fill="none"
                        stroke={result.isAttack ? COLORS.crimson : COLORS.green}
                        strokeWidth={8}
                        strokeDasharray={`${result.confidence * 2.51} 251`}
                        strokeLinecap="butt"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-display font-bold" style={{ color: colors.white }}>
                        {result.confidence.toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  {/* Per-Model Bars */}
                  <div className="flex-1 space-y-2">
                    {Object.entries(result.perModel).map(([name, model]) => (
                      <div key={name} className="flex items-center gap-2">
                        <span className="text-[9px] w-24 font-mono" style={{ color: colors.muted }}>{name}</span>
                        <div className="flex-1 h-3 relative" style={{ background: colors.navy }}>
                          <div
                            className="h-full transition-all duration-700"
                            style={{
                              width: `${model.probability * 100}%`,
                              background: model.verdict ? COLORS.crimson : COLORS.green,
                            }}
                          />
                        </div>
                        <span className={`text-[9px] font-mono w-10 text-right ${model.verdict ? 'text-[#DC2626]' : 'text-[#10B981]'}`}>
                          {(model.probability * 100).toFixed(1)}%
                        </span>
                        <span className={`text-[8px] px-1 ${model.verdict ? 'bg-[#DC2626]/20 text-[#DC2626]' : 'bg-[#10B981]/20 text-[#10B981]'}`}>
                          {model.verdict ? 'ATK' : 'NRM'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                <p className="text-[10px] mt-3 border-t pt-2" style={{ color: colors.slate, borderColor: colors.border }}>
                  <span className="text-[#00D4FF] font-bold">META-LEARNER:</span> Logistic Regression aggregated base model predictions via 5-fold CV meta-features. Final decision:{' '}
                  <span className={result.isAttack ? 'text-[#DC2626]' : 'text-[#10B981]'}>
                    {result.isAttack ? 'ATTACK' : 'NORMAL'}
                  </span>{' '}
                  (threshold: 0.50)
                </p>
              </div>
            </div>
          </Panel>

          {/* Feature Importance Chart */}
          <Panel>
            <PanelHeading icon={BarChart3}>FEATURE IMPORTANCE (SHAP-STYLE)</PanelHeading>
            <div className="h-[280px]">
              <ResponsiveContainer>
                <BarChart data={result.featureImportance} layout="vertical" margin={{ left: 120 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                  <XAxis type="number" domain={[-1, 1]} stroke={colors.muted} tick={{ fontSize: 10 }} />
                  <YAxis type="category" dataKey="feature" stroke={colors.muted} tick={{ fontSize: 10, fontFamily: 'Space Mono' }} />
                  <Tooltip contentStyle={chartTooltipStyle} />
                  <Bar dataKey="impact" name="Impact">
                    {result.featureImportance.map((entry, i) => (
                      <Cell key={i} fill={entry.impact >= 0 ? COLORS.crimson : COLORS.green} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-[10px] mt-2" style={{ color: colors.muted }}>
              Red = pushes toward ATTACK. Green = pushes toward NORMAL.
            </p>
          </Panel>
        </div>
      )}

      {/* Scenario History */}
      {history.length > 0 && (
        <Panel>
          <PanelHeading icon={Clock}>SCENARIO HISTORY</PanelHeading>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr style={{ color: colors.muted }}>
                  {['#', 'SCENARIO', 'VERDICT', 'CONFIDENCE', 'TIME', ''].map((h) => (
                    <th key={h} className="px-3 py-2 text-left font-display text-[10px] uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {history.map((entry, i) => (
                  <tr key={i} className="border-t hover:bg-[#1e293b]/30" style={{ borderColor: colors.border + '80' }}>
                    <td className="px-3 py-1.5" style={{ color: colors.muted }}>{i + 1}</td>
                    <td className="px-3 py-1.5">{entry.scenarioName}</td>
                    <td className="px-3 py-1.5">
                      <span className={`px-1.5 py-0.5 text-[9px] font-bold ${
                        entry.isAttack ? 'bg-[#DC2626]/20 text-[#DC2626]' : 'bg-[#10B981]/20 text-[#10B981]'
                      }`}>
                        {entry.isAttack ? 'ATTACK' : 'NORMAL'}
                      </span>
                    </td>
                    <td className="px-3 py-1.5 font-mono">{entry.confidence.toFixed(1)}%</td>
                    <td className="px-3 py-1.5" style={{ color: colors.muted }}>{entry.timestamp}</td>
                    <td className="px-3 py-1.5">
                      <button className="text-[#00D4FF] hover:underline" aria-label="Re-run scenario">
                        <RotateCcw size={10} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}
    </div>
  );
}
