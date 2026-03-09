/**
 * @fileoverview Page 4 — System Architecture.
 * Visualizes the IDS system design with:
 *  - 4-layer architecture diagram (Data, Preprocessing, Model, Evaluation)
 *  - Stacking ensemble flow diagram
 *  - 11-step preprocessing pipeline stepper
 *  - UML-style class diagram for core modules
 */

import { useState } from 'react';
import { Layers, Cpu, Activity, FileText } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { COLORS } from '../data/constants';
import { Panel, PanelHeading } from '../components/Panel';

/** Architecture layer definitions */
const LAYERS = [
  {
    id: 'data',
    name: 'DATA LAYER',
    color: COLORS.cyan,
    items: ['NSL-KDD', 'KDDCup99', 'Kaggle NID', 'CIC-DDoS2019', 'CIDDS-001', 'DS2OS', 'LUFlow', 'NetworkLogs'],
  },
  {
    id: 'preprocessing',
    name: 'PREPROCESSING LAYER',
    color: COLORS.green,
    items: ['Data Loading & Cleaning', 'Feature Engineering', 'SMOTE Balancing', 'Scaling (RobustScaler)', 'Train/Test Split'],
  },
  {
    id: 'model',
    name: 'MODEL LAYER',
    color: COLORS.amber,
    items: ['Random Forest', 'XGBoost', 'LightGBM', 'MLP Neural Net', 'Stacking Meta-Learner'],
  },
  {
    id: 'evaluation',
    name: 'EVALUATION & DEPLOYMENT',
    color: COLORS.purple,
    items: ['Threshold Optimization', 'Metrics Computation', 'Visualization', 'Interactive Testing', 'Monitoring Dashboard'],
  },
];

/** Preprocessing pipeline steps */
const PIPELINE_STEPS = [
  { step: '01', name: 'Load Dataset CSV Files',     description: 'Read raw data from 8 benchmark datasets' },
  { step: '02', name: 'Clean & Map Labels',          description: 'Binary: Normal=0, Attack=1' },
  { step: '03', name: 'Encode Categorical Features', description: 'Label Encoding for string columns' },
  { step: '04', name: 'Convert to Numeric',          description: 'Handle missing values, type coercion' },
  { step: '05', name: 'Remove Constant Features',    description: 'Variance Threshold filter' },
  { step: '06', name: 'Remove Correlated Features',  description: 'Pearson |r| > 0.95 elimination' },
  { step: '07', name: 'Train-Test Split',            description: '80/20 stratified split' },
  { step: '08', name: 'Scale Features',              description: 'RobustScaler for outlier resistance' },
  { step: '09', name: 'Class Balancing',             description: 'Tiered SMOTE strategy' },
  { step: '10', name: 'Train Models',                description: 'RF, XGB, LGBM, MLP + Stacking' },
  { step: '11', name: 'Evaluate & Optimize',         description: 'Threshold opt, save best model' },
];

/** Class diagram entries for the core Python modules */
const CLASS_DIAGRAM = [
  {
    name: 'DataPreprocessor',
    color: COLORS.cyan,
    attributes: ['dataset_paths: Dict', 'max_sample_size: int', 'random_state: int'],
    methods: ['load_dataset(name)', 'load_kdd_family()', 'load_ds2os()', '_encode_categoricals()'],
  },
  {
    name: 'FeatureEngineer',
    color: COLORS.green,
    attributes: ['test_size: float', 'scaler: RobustScaler', 'feature_names: List'],
    methods: ['prepare_dataset(df)', 'remove_constant_features()', 'remove_highly_correlated()', 'balance_classes()'],
  },
  {
    name: 'EnsembleIDS',
    color: COLORS.crimson,
    attributes: ['base_models: Dict', 'meta_learner: LR', 'imbalance_ratio: float'],
    methods: ['build_base_models()', 'train_stacking_ensemble()', 'save_model()', 'load_model()'],
  },
  {
    name: 'MetricsEvaluator',
    color: COLORS.purple,
    attributes: ['min_metric_score: float', 'target: float'],
    methods: ['compute_all_metrics()', 'evaluate_model()', 'optimize_threshold()'],
  },
  {
    name: 'Visualizer',
    color: COLORS.amber,
    attributes: ['figures_dir: Path', 'reports_dir: Path'],
    methods: ['plot_confusion_matrix()', 'plot_roc_curves()', 'plot_metrics_comparison()'],
  },
  {
    name: 'TrainingPipeline',
    color: '#f97316',
    attributes: ['dataset_names: List', 'all_metrics: List'],
    methods: ['train_on_dataset()', 'run_full_pipeline()', 'save_results()'],
  },
];

/** Base learners for the ensemble flow diagram */
const BASE_LEARNERS = [
  { name: 'Random Forest', color: COLORS.cyan },
  { name: 'XGBoost',       color: COLORS.crimson },
  { name: 'LightGBM',      color: COLORS.green },
  { name: 'MLP Neural Net', color: COLORS.amber },
];

/** Downward arrow SVG used between flow diagram stages */
function DownArrow() {
  return (
    <div className="flex justify-center py-1">
      <svg width={20} height={20} aria-hidden="true">
        <polygon points="10,18 4,6 16,6" fill={COLORS.muted} />
      </svg>
    </div>
  );
}

/**
 * System Architecture page — diagrams of the IDS pipeline and module structure.
 */
export function ArchitecturePage() {
  const { colors } = useTheme();
  const [activeLayer, setActiveLayer] = useState(null);

  return (
    <div className="space-y-6">
      {/* Layered Architecture Diagram */}
      <Panel>
        <PanelHeading icon={Layers}>SYSTEM ARCHITECTURE</PanelHeading>
        <div className="space-y-2">
          {LAYERS.map((layer, i) => (
            <div key={layer.id}>
              <div
                className="border p-4 transition-all"
                style={{
                  borderColor: activeLayer === layer.id ? layer.color : colors.border,
                  boxShadow: activeLayer === layer.id ? `0 0 15px ${layer.color}22` : 'none',
                }}
                onMouseEnter={() => setActiveLayer(layer.id)}
                onMouseLeave={() => setActiveLayer(null)}
                role="region"
                aria-label={layer.name}
              >
                <h4 className="font-display font-bold text-xs tracking-[.2em] mb-3" style={{ color: layer.color }}>
                  {layer.name}
                </h4>
                <div className="flex gap-2 flex-wrap">
                  {layer.items.map((item) => (
                    <span
                      key={item}
                      className="px-3 py-1.5 text-[10px] font-mono border"
                      style={{ borderColor: layer.color + '33', background: layer.color + '10', color: layer.color }}
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
              {i < LAYERS.length - 1 && <DownArrow />}
            </div>
          ))}
        </div>
      </Panel>

      {/* Stacking Ensemble Flow */}
      <Panel>
        <PanelHeading icon={Cpu}>STACKING ENSEMBLE FLOW</PanelHeading>
        <div className="flex flex-col items-center space-y-2">
          {/* Input */}
          <div className="px-6 py-3 border text-center" style={{ borderColor: colors.border, background: colors.navy }}>
            <p className="text-[10px] font-display tracking-wider" style={{ color: colors.muted }}>INPUT</p>
            <p className="text-sm font-display font-bold" style={{ color: colors.white }}>Feature Vector (X)</p>
          </div>
          <DownArrow />

          {/* Base Learners */}
          <div className="flex gap-3 flex-wrap justify-center">
            {BASE_LEARNERS.map((model) => (
              <div
                key={model.name}
                className="px-4 py-3 border text-center min-w-[130px]"
                style={{ borderColor: model.color + '50', background: model.color + '10' }}
              >
                <p className="text-[11px] font-display font-bold" style={{ color: model.color }}>{model.name}</p>
                <p className="text-[8px] mt-1" style={{ color: colors.muted }}>Base Learner</p>
              </div>
            ))}
          </div>
          <DownArrow />

          {/* Meta-Features */}
          <div className="px-8 py-3 border border-[#F59E0B]/50 bg-[#F59E0B]/10 text-center">
            <p className="text-[10px] font-display tracking-wider" style={{ color: colors.muted }}>META-FEATURES</p>
            <p className="text-sm font-display font-bold text-[#F59E0B]">5-Fold CV Predictions</p>
          </div>
          <DownArrow />

          {/* Meta-Learner */}
          <div className="px-8 py-3 border border-[#a855f7]/50 bg-[#a855f7]/10 text-center">
            <p className="text-[10px] font-display tracking-wider" style={{ color: colors.muted }}>META-LEARNER</p>
            <p className="text-sm font-display font-bold text-[#a855f7]">Logistic Regression</p>
          </div>
          <DownArrow />

          {/* Output */}
          <div className="px-8 py-3 border border-[#10B981]/50 bg-[#10B981]/10 text-center">
            <p className="text-[10px] font-display tracking-wider" style={{ color: colors.muted }}>OUTPUT</p>
            <p className="text-sm font-display font-bold text-[#10B981]">Normal / Attack</p>
          </div>
        </div>
      </Panel>

      {/* Preprocessing Pipeline */}
      <Panel>
        <PanelHeading icon={Activity}>PREPROCESSING PIPELINE</PanelHeading>
        <div className="relative ml-6">
          <div className="absolute left-0 top-0 bottom-0 w-px" style={{ background: colors.border }} />
          {PIPELINE_STEPS.map((step, i) => (
            <div
              key={step.step}
              className="relative pl-8 pb-4 animate-fade-in"
              style={{ animationDelay: `${i * 0.08}s` }}
            >
              <div className="absolute left-[-8px] top-1 w-4 h-4 border border-[#00D4FF] flex items-center justify-center" style={{ background: colors.navy }}>
                <div className="w-1.5 h-1.5 bg-[#00D4FF]" />
              </div>
              <div className="flex items-baseline gap-3">
                <span className="text-[10px] text-[#00D4FF] font-mono font-bold">{step.step}</span>
                <div>
                  <p className="text-[11px] font-display font-bold" style={{ color: colors.white }}>{step.name}</p>
                  <p className="text-[9px]" style={{ color: colors.muted }}>{step.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Panel>

      {/* Class Diagram */}
      <Panel>
        <PanelHeading icon={FileText}>CLASS DIAGRAM</PanelHeading>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {CLASS_DIAGRAM.map((cls) => (
            <div key={cls.name} className="border overflow-hidden" style={{ borderColor: colors.border }}>
              <div className="px-3 py-2" style={{ background: cls.color + '20', borderBottom: `2px solid ${cls.color}` }}>
                <h5 className="text-[11px] font-display font-bold tracking-wider" style={{ color: cls.color }}>
                  {cls.name}
                </h5>
              </div>
              <div className="px-3 py-2 border-b" style={{ borderColor: colors.border }}>
                {cls.attributes.map((attr) => (
                  <p key={attr} className="text-[9px] font-mono" style={{ color: colors.slate }}>- {attr}</p>
                ))}
              </div>
              <div className="px-3 py-2">
                {cls.methods.map((method) => (
                  <p key={method} className="text-[9px] font-mono text-[#00D4FF]">+ {method}</p>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
