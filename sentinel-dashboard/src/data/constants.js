/**
 * @fileoverview Application-wide constants for the SENTINEL-IDS dashboard.
 * Contains color palette, protocol lists, attack types, model names,
 * dataset identifiers, and navigation configuration.
 */

/** Color palette — military command center theme */
export const COLORS = {
  navy:     '#0A0E1A',
  charcoal: '#111827',
  darkPanel:'#080c16',
  cyan:     '#00D4FF',
  amber:    '#F59E0B',
  crimson:  '#DC2626',
  green:    '#10B981',
  white:    '#F9FAFB',
  border:   '#1e293b',
  muted:    '#64748b',
  purple:   '#a855f7',
  slate:    '#94a3b8',
  deepSlate:'#475569',
};

/** Light-theme overrides — applied when user selects light mode */
export const LIGHT_COLORS = {
  navy:     '#f8fafc',
  charcoal: '#ffffff',
  darkPanel:'#f1f5f9',
  white:    '#0f172a',
  border:   '#cbd5e1',
  muted:    '#64748b',
  slate:    '#475569',
  deepSlate:'#94a3b8',
};

/** Network protocols used in simulated traffic */
export const PROTOCOLS = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'SSH', 'FTP', 'DNS'];

/** Attack categories from the IDS classification taxonomy */
export const ATTACK_TYPES = ['DoS', 'Probe', 'R2L', 'U2R', 'DDoS'];

/** ML model names in the stacking ensemble */
export const MODEL_NAMES = ['RandomForest', 'XGBoost', 'LightGBM', 'MLP', 'StackingEnsemble'];

/** Benchmark datasets used for training and evaluation */
export const DATASETS = [
  'NSL_KDD', 'KDDCup99', 'Kaggle_NID', 'CIC_DDoS2019',
  'CIDDS_001', 'DS2OS', 'LUFlow', 'NetworkLogs',
];

/** Tactical network node labels for the threat map */
export const NETWORK_NODES = [
  'HQ-CMD', 'FWD-BASE', 'SAT-RELAY', 'DRONE-CTL',
  'COMMS-HUB', 'INTEL-OPS', 'LOG-NET', 'MED-SYS',
  'CRYPTO', 'RADAR', 'C2-NODE', 'SIGINT',
];

/** Feature keys used in the scenario testing form */
export const FEATURE_KEYS = [
  'duration', 'protocol_type', 'service', 'flag',
  'src_bytes', 'dst_bytes', 'wrong_fragment', 'hot',
  'num_failed_logins', 'logged_in', 'count', 'srv_count',
  'serror_rate', 'same_srv_rate', 'dst_host_count', 'dst_host_srv_count',
];

/** Model display metadata — type, hyperparameters, accent color */
export const MODEL_DETAILS = {
  RandomForest: {
    type: 'Ensemble (Bagging)',
    params: 'n_estimators=300, max_depth=25, class_weight=balanced',
    color: COLORS.cyan,
  },
  XGBoost: {
    type: 'Ensemble (Boosting)',
    params: 'n_estimators=300, max_depth=10, lr=0.1, scale_pos_weight=auto',
    color: COLORS.crimson,
  },
  LightGBM: {
    type: 'Ensemble (Boosting)',
    params: 'n_estimators=300, max_depth=15, lr=0.1, is_unbalance=True',
    color: COLORS.green,
  },
  MLP: {
    type: 'Neural Network',
    params: 'layers=(128,64,32), activation=relu, solver=adam',
    color: COLORS.amber,
  },
  StackingEnsemble: {
    type: 'Stacking Meta-Learner',
    params: 'base: RF+XGB+LGBM+MLP, meta: LogisticRegression, cv=5',
    color: COLORS.purple,
  },
};
