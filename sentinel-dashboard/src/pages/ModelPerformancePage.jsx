/**
 * @fileoverview Page 3 — Model Performance.
 * Comprehensive view of ML model evaluation metrics including:
 *  - Model overview cards with hyperparameters and key metrics
 *  - Metrics comparison table across all models
 *  - Interactive confusion matrix with model toggle
 *  - Threshold optimization chart with draggable slider
 *  - Dataset F1-score comparison grouped bar chart
 */

import { useState, useMemo } from 'react';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { BarChart3, TrendingUp, Target, Database } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { COLORS, MODEL_NAMES, MODEL_DETAILS } from '../data/constants';
import { METRICS_DATA, CONFUSION_MATRICES } from '../data/metrics';
import { generateThresholdData } from '../data/generators';
import { Panel, PanelHeading } from '../components/Panel';

/**
 * Returns the metric-data prefix character for a given model name.
 * @param {string} model - Model name
 * @returns {string} Single-character prefix for accessing METRICS_DATA fields
 */
function metricPrefix(model) {
  const map = { RandomForest: 'r', XGBoost: 'x', LightGBM: 'l', MLP: 'm', StackingEnsemble: 'e' };
  return map[model] || 'e';
}

/** Returns the F1 score key for a model in METRICS_DATA */
function f1Key(model) {
  const map = { RandomForest: 'RF', XGBoost: 'XGB', LightGBM: 'LGBM', MLP: 'MLP', StackingEnsemble: 'Ens' };
  return map[model] || 'Ens';
}

/**
 * Model Performance page — inspect and compare ML model metrics.
 */
export function ModelPerformancePage() {
  const { colors } = useTheme();
  const [selectedModel, setSelectedModel] = useState('StackingEnsemble');
  const [thresholdValue, setThresholdValue] = useState(0.5);
  const thresholdData = useMemo(() => generateThresholdData(), []);

  /** Metrics at current threshold position */
  const thresholdMetrics = useMemo(() => {
    const idx = Math.min(Math.round(thresholdValue * 100), thresholdData.length - 1);
    return thresholdData[idx] || { precision: 0, recall: 0, f1: 0 };
  }, [thresholdValue, thresholdData]);

  const nslData = METRICS_DATA[0]; // NSL_KDD baseline metrics
  const bestValues = [0.988, 0.9906, 0.9887, 0.9895, 0.9996, 0.9756];

  const chartTooltipStyle = {
    background: colors.charcoal,
    border: `1px solid ${colors.border}`,
    fontFamily: 'Space Mono',
    fontSize: 10,
    color: colors.white,
  };

  return (
    <div className="space-y-4">
      {/* Model Overview Cards */}
      <div className="flex gap-3 flex-wrap">
        {MODEL_NAMES.map((model) => {
          const detail = MODEL_DETAILS[model];
          const prefix = metricPrefix(model);
          const isEnsemble = model === 'StackingEnsemble';
          const isActive = selectedModel === model;

          return (
            <Panel
              key={model}
              className={`flex-1 min-w-[200px] cursor-pointer transition-all ${
                isEnsemble ? 'border-[#a855f7]/50' : ''
              }`}
              style={{
                borderLeftWidth: '2px',
                borderLeftColor: isActive ? detail.color : 'transparent',
              }}
            >
              <div
                onClick={() => setSelectedModel(model)}
                role="button"
                tabIndex={0}
                aria-label={`Select ${model}`}
                onKeyDown={(e) => e.key === 'Enter' && setSelectedModel(model)}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2" style={{ background: detail.color }} />
                  <h4 className="font-display font-bold text-xs tracking-wider uppercase" style={{ color: detail.color }}>
                    {model}
                  </h4>
                  {isEnsemble && (
                    <span className="text-[8px] px-1 bg-[#a855f7]/20 text-[#a855f7] border border-[#a855f7]/30">PRIMARY</span>
                  )}
                </div>
                <p className="text-[9px] mb-1" style={{ color: colors.muted }}>{detail.type}</p>
                <p className="text-[8px] font-mono mb-3 break-all" style={{ color: colors.deepSlate }}>{detail.params}</p>

                {/* Mini metric grid */}
                <div className="grid grid-cols-2 gap-1">
                  {[
                    ['ACC', nslData[prefix + 'A']],
                    ['F1', nslData[f1Key(model)]],
                    ['PREC', nslData[prefix + 'P']],
                    ['REC', nslData[prefix + 'R']],
                  ].map(([label, value]) => (
                    <div key={label} className="px-2 py-1" style={{ background: colors.navy }}>
                      <span className="text-[7px] block" style={{ color: colors.muted }}>{label}</span>
                      <span
                        className="text-[11px] font-mono font-bold"
                        style={{ color: value >= 0.99 ? COLORS.cyan : value >= 0.98 ? COLORS.green : COLORS.amber }}
                      >
                        {value?.toFixed(4)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </Panel>
          );
        })}
      </div>

      {/* Metrics Comparison Table */}
      <Panel>
        <PanelHeading icon={BarChart3}>METRICS COMPARISON -- ALL MODELS (NSL_KDD)</PanelHeading>
        <div className="overflow-x-auto">
          <table className="w-full text-[11px]">
            <thead>
              <tr className="border-b" style={{ color: colors.muted, borderColor: colors.border }}>
                {['MODEL', 'ACCURACY', 'PRECISION', 'RECALL', 'F1', 'ROC-AUC', 'MCC'].map((h) => (
                  <th key={h} className="px-3 py-2 text-left font-display text-[10px] uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MODEL_NAMES.map((model) => {
                const prefix = metricPrefix(model);
                const values = [
                  nslData[prefix + 'A'], nslData[prefix + 'P'], nslData[prefix + 'R'],
                  nslData[f1Key(model)], nslData[prefix + 'U'], nslData[prefix + 'M'],
                ];
                return (
                  <tr
                    key={model}
                    className={`border-t hover:bg-[#1e293b]/30 ${model === 'StackingEnsemble' ? 'bg-[#a855f7]/5' : ''}`}
                    style={{ borderColor: colors.border + '80' }}
                  >
                    <td className="px-3 py-2 font-display font-bold" style={{ color: MODEL_DETAILS[model].color }}>
                      {model}
                    </td>
                    {values.map((v, i) => (
                      <td
                        key={i}
                        className="px-3 py-2 font-mono"
                        style={{ color: v >= bestValues[i] ? COLORS.cyan : colors.white }}
                      >
                        {v?.toFixed(4)}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Panel>

      {/* Confusion Matrix + Threshold Optimization Row */}
      <div className="flex gap-4 flex-wrap">
        {/* Confusion Matrix */}
        <Panel className="flex-1 min-w-[400px]">
          <PanelHeading icon={TrendingUp}>CONFUSION MATRIX -- {selectedModel.toUpperCase()}</PanelHeading>
          <div className="flex items-center gap-2 mb-4 flex-wrap">
            {MODEL_NAMES.map((m) => (
              <button
                key={m}
                onClick={() => setSelectedModel(m)}
                className={`text-[9px] px-2 py-1 border transition-all ${
                  selectedModel === m
                    ? 'border-[#00D4FF] text-[#00D4FF] bg-[#00D4FF]/10'
                    : 'border-[#1e293b] text-[#64748b]'
                }`}
                aria-pressed={selectedModel === m}
              >
                {m === 'RandomForest' ? 'RF' : m === 'StackingEnsemble' ? 'ENS' : m}
              </button>
            ))}
          </div>
          {(() => {
            const cm = CONFUSION_MATRICES[selectedModel];
            const total = cm.tp + cm.fp + cm.fn + cm.tn;
            const cells = [
              { label: 'TRUE POS', value: cm.tp, color: COLORS.green },
              { label: 'FALSE POS', value: cm.fp, color: COLORS.crimson },
              { label: 'FALSE NEG', value: cm.fn, color: COLORS.amber },
              { label: 'TRUE NEG', value: cm.tn, color: COLORS.green },
            ];
            return (
              <div className="flex gap-4">
                <div
                  className="flex flex-col justify-center text-[8px] font-display tracking-wider"
                  style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)', color: colors.muted }}
                >
                  ACTUAL
                </div>
                <div>
                  <div className="text-center text-[8px] mb-1 font-display tracking-wider" style={{ color: colors.muted }}>
                    PREDICTED
                  </div>
                  <div className="grid grid-cols-2 gap-1">
                    {cells.map((cell) => (
                      <div
                        key={cell.label}
                        className="p-4 text-center"
                        style={{ background: cell.color + '15', border: `1px solid ${cell.color}33` }}
                      >
                        <p className="text-[8px]" style={{ color: colors.muted }}>{cell.label}</p>
                        <p className="text-xl font-display font-bold" style={{ color: cell.color }}>
                          {cell.value.toLocaleString()}
                        </p>
                        <p className="text-[9px] mt-1" style={{ color: colors.slate }}>
                          {((cell.value / total) * 100).toFixed(1)}%
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })()}
        </Panel>

        {/* Threshold Optimization */}
        <Panel className="flex-1 min-w-[400px]">
          <PanelHeading icon={Target}>THRESHOLD OPTIMIZATION</PanelHeading>
          <div className="h-[220px]">
            <ResponsiveContainer>
              <LineChart data={thresholdData}>
                <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                <XAxis dataKey="threshold" stroke={colors.muted} tick={{ fontSize: 9 }} />
                <YAxis domain={[0, 1]} stroke={colors.muted} tick={{ fontSize: 9 }} />
                <Tooltip contentStyle={chartTooltipStyle} />
                <Legend wrapperStyle={{ fontSize: 9 }} />
                <Line dataKey="precision" stroke={COLORS.cyan} strokeWidth={2} dot={false} name="Precision" />
                <Line dataKey="recall" stroke={COLORS.amber} strokeWidth={2} dot={false} name="Recall" />
                <Line dataKey="f1" stroke={COLORS.green} strokeWidth={2} dot={false} name="F1" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Threshold Slider */}
          <div className="flex items-center gap-4 mt-3">
            <span className="text-[10px] font-display" style={{ color: colors.muted }}>THRESHOLD:</span>
            <input
              type="range"
              min={0} max={100}
              value={thresholdValue * 100}
              onChange={(e) => setThresholdValue(e.target.value / 100)}
              className="flex-1 accent-[#a855f7]"
              aria-label="Decision threshold"
            />
            <span className="text-lg font-display font-bold text-[#a855f7] w-12">{thresholdValue.toFixed(2)}</span>
          </div>

          {/* Threshold Metrics */}
          <div className="flex gap-3 mt-2">
            {[
              ['PRECISION', thresholdMetrics.precision, COLORS.cyan],
              ['RECALL', thresholdMetrics.recall, COLORS.amber],
              ['F1-SCORE', thresholdMetrics.f1, COLORS.green],
            ].map(([label, value, color]) => (
              <div key={label} className="flex-1 p-2 border text-center" style={{ background: colors.navy, borderColor: colors.border }}>
                <p className="text-[8px] tracking-wider" style={{ color: colors.muted }}>{label}</p>
                <p className="text-sm font-mono font-bold" style={{ color }}>{value.toFixed(4)}</p>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {/* Dataset F1-Score Comparison */}
      <Panel>
        <PanelHeading icon={Database}>DATASET F1-SCORE COMPARISON</PanelHeading>
        <div className="h-[300px]">
          <ResponsiveContainer>
            <BarChart data={METRICS_DATA} margin={{ bottom: 50 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
              <XAxis dataKey="dataset" stroke={colors.muted} tick={{ fontSize: 8, angle: -30, textAnchor: 'end' }} interval={0} />
              <YAxis domain={[0.96, 1.001]} stroke={colors.muted} tick={{ fontSize: 9 }} />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 9 }} />
              <Bar dataKey="RF" name="RandomForest" fill={COLORS.cyan} />
              <Bar dataKey="XGB" name="XGBoost" fill={COLORS.crimson} />
              <Bar dataKey="LGBM" name="LightGBM" fill={COLORS.green} />
              <Bar dataKey="MLP" name="MLP" fill={COLORS.amber} />
              <Bar dataKey="Ens" name="Ensemble" fill={COLORS.purple} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>
    </div>
  );
}
