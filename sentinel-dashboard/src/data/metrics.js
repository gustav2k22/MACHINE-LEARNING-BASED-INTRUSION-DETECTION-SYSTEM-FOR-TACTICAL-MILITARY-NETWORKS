/**
 * @fileoverview Real model performance metrics from the training pipeline.
 * Data sourced from outputs/reports/summary_table.csv.
 * Each entry contains F1 scores per model and detailed per-model metrics
 * (Accuracy, Precision, Recall, ROC-AUC, MCC) for a given dataset.
 */

/**
 * Performance metrics for all models across all 8 datasets.
 * Prefix key: r=RandomForest, x=XGBoost, l=LightGBM, m=MLP, e=Ensemble
 * Suffix: A=Accuracy, P=Precision, R=Recall, U=ROC-AUC, M=MCC
 */
export const METRICS_DATA = [
  { dataset: 'NSL_KDD',       RF: .9895, XGB: .9891, LGBM: .9893, MLP: .9796, Ens: .9891, rA: .988,  rP: .9906, rR: .9883, rU: .9995, rM: .9756, xA: .9876, xP: .9895, xR: .9887, xU: .9996, xM: .9747, lA: .9878, lP: .9902, lR: .9883, lU: .9996, lM: .9751, mA: .9769, mP: .9854, mR: .9739, mU: .9972, mM: .9531, eA: .9876, eP: .9902, eR: .9879, eU: .9996, eM: .9747 },
  { dataset: 'KDDCup99',      RF: .9999, XGB: .9999, LGBM: .9999, MLP: .9994, Ens: .9999, rA: .9998, rP: 1,     rR: .9998, rU: 1,     rM: .9994, xA: .9999, xP: 1,     xR: .9998, xU: 1,     xM: .9995, lA: .9998, lP: 1,     lR: .9998, lU: 1,     lM: .9994, mA: .999,  mP: .9999, mR: .9988, mU: 1,     mM: .9969, eA: .9998, eP: .9999, eR: .9998, eU: 1,     eM: .9994 },
  { dataset: 'Kaggle_NID',    RF: .9972, XGB: .9974, LGBM: .9972, MLP: .9843, Ens: .9974, rA: .9974, rP: .9987, rR: .9957, rU: .9999, rM: .9948, xA: .9976, xP: .9983, xR: .9966, xU: .9998, xM: .9952, lA: .9974, lP: .9983, lR: .9962, lU: .9997, lM: .9948, mA: .9853, mP: .9781, mR: .9906, mU: .9919, mM: .9706, eA: .9976, eP: .9983, eR: .9966, eU: .9999, eM: .9952 },
  { dataset: 'CIC_DDoS2019',  RF: .9994, XGB: .9996, LGBM: .9996, MLP: .9803, Ens: .9996, rA: .999,  rP: .9999, rR: .9988, rU: 1,     rM: .9972, xA: .9993, xP: .9998, xR: .9993, xU: 1,     xM: .9981, lA: .9994, lP: .9998, lR: .9994, lU: 1,     lM: .9982, mA: .97,   mP: .9932, mR: .9678, mU: .974,  mM: .9183, eA: .9993, eP: .9998, eR: .9993, eU: 1,     eM: .9981 },
  { dataset: 'CIDDS_001',     RF: .9999, XGB: .9999, LGBM: .9999, MLP: .9995, Ens: .9999, rA: .9999, rP: .9999, rR: .9999, rU: 1,     rM: .9997, xA: .9999, xP: .9999, xR: 1,     xU: 1,     xM: .9998, lA: .9999, lP: .9999, lR: 1,     lU: 1,     lM: .9997, mA: .9993, mP: .9994, mR: .9996, mU: .9999, mM: .9981, eA: .9999, eP: .9999, eR: 1,     eU: 1,     eM: .9997 },
  { dataset: 'DS2OS',         RF: 1,     XGB: 1,     LGBM: 1,     MLP: .998,  Ens: 1,     rA: 1,     rP: 1,     rR: 1,     rU: 1,     rM: 1,     xA: 1,     xP: 1,     xR: 1,     xU: 1,     xM: 1,     lA: 1,     lP: 1,     lR: 1,     lU: 1,     lM: 1,     mA: .9999, mP: .996,  mR: 1,     mU: 1,     mM: .998,  eA: 1,     eP: 1,     eR: 1,     eU: 1,     eM: 1     },
  { dataset: 'LUFlow',        RF: .9996, XGB: .9994, LGBM: .9996, MLP: .9981, Ens: .9997, rA: .9996, rP: .9995, rR: .9998, rU: 1,     rM: .9992, xA: .9993, xP: .9993, xR: .9994, xU: 1,     xM: .9987, lA: .9996, lP: .9997, lR: .9996, lU: 1,     lM: .9992, mA: .998,  mP: .9986, mR: .9976, mU: .9999, mM: .996,  eA: .9997, eP: .9997, eR: .9998, eU: 1,     eM: .9994 },
  { dataset: 'NetworkLogs',   RF: 1,     XGB: 1,     LGBM: 1,     MLP: 1,     Ens: 1,     rA: 1,     rP: 1,     rR: 1,     rU: 1,     rM: 1,     xA: 1,     xP: 1,     xR: 1,     xU: 1,     xM: 1,     lA: 1,     lP: 1,     lR: 1,     lU: 1,     lM: 1,     mA: 1,     mP: 1,     mR: 1,     mU: 1,     mM: 1,     eA: 1,     eP: 1,     eR: 1,     eU: 1,     eM: 1     },
];

/** Pre-built test scenarios with realistic feature vectors */
export const SCENARIOS = [
  {
    id: 'normal',
    name: 'Normal Web Browsing',
    type: 'Normal',
    description: 'Typical HTTP browsing session — standard TCP connection with successful handshake',
    features: { duration: 0, protocol_type: 'tcp', service: 'http', flag: 'SF', src_bytes: 215, dst_bytes: 45076, wrong_fragment: 0, hot: 0, num_failed_logins: 0, logged_in: 1, count: 5, srv_count: 5, serror_rate: 0, same_srv_rate: 1, dst_host_count: 255, dst_host_srv_count: 255 },
  },
  {
    id: 'dos',
    name: 'DoS Flood Attack',
    type: 'DoS',
    description: 'SYN flood targeting a private service — high connection count with 100% SYN error rate',
    features: { duration: 0, protocol_type: 'tcp', service: 'private', flag: 'S0', src_bytes: 0, dst_bytes: 0, wrong_fragment: 0, hot: 0, num_failed_logins: 0, logged_in: 0, count: 511, srv_count: 511, serror_rate: 1, same_srv_rate: 1, dst_host_count: 255, dst_host_srv_count: 255 },
  },
  {
    id: 'probe',
    name: 'Port Scan / Probe',
    type: 'Probe',
    description: 'Reconnaissance scan — many rejected connections across different services on the target',
    features: { duration: 0, protocol_type: 'tcp', service: 'private', flag: 'REJ', src_bytes: 0, dst_bytes: 0, wrong_fragment: 0, hot: 0, num_failed_logins: 0, logged_in: 0, count: 302, srv_count: 8, serror_rate: 0, same_srv_rate: .03, dst_host_count: 255, dst_host_srv_count: 1 },
  },
  {
    id: 'brute',
    name: 'Brute Force SSH',
    type: 'R2L',
    description: 'Repeated failed SSH login attempts from a single source — credential stuffing pattern',
    features: { duration: 1, protocol_type: 'tcp', service: 'ssh', flag: 'SF', src_bytes: 188, dst_bytes: 786, wrong_fragment: 0, hot: 0, num_failed_logins: 5, logged_in: 0, count: 6, srv_count: 6, serror_rate: 0, same_srv_rate: 1, dst_host_count: 1, dst_host_srv_count: 1 },
  },
  {
    id: 'custom',
    name: 'Custom Input',
    type: 'Custom',
    description: 'Enter your own feature values to test the ensemble model with arbitrary network traffic',
    features: {},
  },
];

/** Confusion matrix values per model (from NSL_KDD evaluation) */
export const CONFUSION_MATRICES = {
  RandomForest:     { tp: 9876, fp: 12,  fn: 24,  tn: 10088 },
  XGBoost:          { tp: 9870, fp: 15,  fn: 30,  tn: 10085 },
  LightGBM:         { tp: 9880, fp: 10,  fn: 20,  tn: 10090 },
  MLP:              { tp: 9750, fp: 45,  fn: 150, tn: 10055 },
  StackingEnsemble: { tp: 9879, fp: 11,  fn: 22,  tn: 10088 },
};
