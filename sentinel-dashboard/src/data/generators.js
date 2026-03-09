/**
 * @fileoverview Mock data generators for the SENTINEL-IDS dashboard.
 * Produces realistic simulated network packets, timeline data, alerts,
 * and threshold optimization curves for demonstration purposes.
 */

import { PROTOCOLS, ATTACK_TYPES, MODEL_NAMES, DATASETS } from './constants';

/**
 * Generate a random IPv4 address in the 10.x–250.x range.
 * @returns {string} IP address string
 */
export function randomIP() {
  const o = () => Math.floor(Math.random() * 256);
  return `${10 + Math.floor(Math.random() * 240)}.${o()}.${o()}.${o()}`;
}

/**
 * Generate a simulated network packet with classification result.
 * @param {boolean|null} forceAttack - Force attack (true) or normal (false), or null for random
 * @returns {object} Packet object with IP addresses, protocol, prediction, confidence, etc.
 */
export function generatePacket(forceAttack = null) {
  const isAttack = forceAttack !== null ? forceAttack : Math.random() < 0.18;
  const attackType = isAttack ? ATTACK_TYPES[Math.floor(Math.random() * ATTACK_TYPES.length)] : null;

  return {
    id: Date.now() + Math.random(),
    timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19),
    sourceIP: randomIP(),
    destIP: randomIP(),
    protocol: PROTOCOLS[Math.floor(Math.random() * PROTOCOLS.length)],
    prediction: isAttack ? 'ATTACK' : 'NORMAL',
    confidence: isAttack ? 85 + Math.random() * 14.9 : 92 + Math.random() * 7.9,
    model: MODEL_NAMES[Math.floor(Math.random() * (MODEL_NAMES.length - 1))],
    attackType,
    severity: isAttack ? (Math.random() > 0.5 ? 'HIGH' : 'CRITICAL') : 'LOW',
    featureSummary: `bytes=${Math.floor(Math.random() * 50000)}, pkts=${Math.floor(Math.random() * 200)}`,
  };
}

/**
 * Generate 60 minutes of timeline data showing normal vs. attack traffic counts.
 * @returns {Array<{time: string, normal: number, attacks: number}>}
 */
export function generateTimeline() {
  const data = [];
  const now = Date.now();
  for (let i = 59; i >= 0; i--) {
    const t = new Date(now - i * 60000);
    data.push({
      time: `${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}`,
      normal: 40 + Math.floor(Math.random() * 60),
      attacks: Math.floor(Math.random() * 15),
    });
  }
  return data;
}

/**
 * Generate a list of historical alert records.
 * @param {number} count - Number of alerts to generate
 * @returns {Array<object>} Sorted array of alert objects (newest first)
 */
export function generateAlerts(count = 80) {
  const alerts = [];
  for (let i = 0; i < count; i++) {
    const date = new Date(Date.now() - Math.random() * 604800000); // up to 7 days ago
    alerts.push({
      id: i + 1,
      timestamp: date.toISOString().replace('T', ' ').slice(0, 19),
      sourceIP: randomIP(),
      destIP: randomIP(),
      attackType: ATTACK_TYPES[Math.floor(Math.random() * ATTACK_TYPES.length)],
      severity: ['HIGH', 'CRITICAL', 'MEDIUM'][Math.floor(Math.random() * 3)],
      confidence: (85 + Math.random() * 14.9).toFixed(1),
      dataset: DATASETS[Math.floor(Math.random() * DATASETS.length)],
      status: Math.random() > 0.3 ? 'OPEN' : 'RESOLVED',
      features: {
        src_bytes: Math.floor(Math.random() * 50000),
        dst_bytes: Math.floor(Math.random() * 10000),
        duration: +(Math.random() * 10).toFixed(2),
        protocol: PROTOCOLS[Math.floor(Math.random() * PROTOCOLS.length)],
      },
    });
  }
  return alerts.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
}

/**
 * Generate precision/recall/F1 values across decision thresholds (0.0 to 1.0).
 * Used for the threshold optimization visualization.
 * @returns {Array<{threshold: number, precision: number, recall: number, f1: number}>}
 */
export function generateThresholdData() {
  const data = [];
  for (let t = 0; t <= 100; t++) {
    const threshold = t / 100;
    const precision = threshold < 0.3 ? 0.7 + threshold : Math.min(1, 0.8 + threshold * 0.2);
    const recall = threshold < 0.5 ? 1 - threshold * 0.1 : Math.max(0.6, 1 - threshold * 0.8);
    const f1 = 2 * (precision * recall) / (precision + recall + 0.001);
    data.push({
      threshold,
      precision: +precision.toFixed(4),
      recall: +recall.toFixed(4),
      f1: +f1.toFixed(4),
    });
  }
  return data;
}

/**
 * Simulate running a prediction on a scenario.
 * Returns per-model predictions and feature importance values.
 * @param {object} scenario - The selected scenario object
 * @returns {object} Prediction result with verdict, confidence, per-model breakdown, feature importance
 */
export function simulatePrediction(scenario) {
  const isAttack = scenario.id !== 'normal' && scenario.id !== 'custom';
  const isCustomAttack = scenario.id === 'custom' && Math.random() > 0.5;
  const attack = isAttack || isCustomAttack;
  const confidence = attack ? 88 + Math.random() * 11 : 95 + Math.random() * 4.5;

  const perModel = {
    RandomForest: { verdict: attack, probability: attack ? .82 + Math.random() * .17 : .05 + Math.random() * .1 },
    XGBoost:      { verdict: attack, probability: attack ? .85 + Math.random() * .14 : .03 + Math.random() * .08 },
    LightGBM:     { verdict: attack, probability: attack ? .87 + Math.random() * .12 : .04 + Math.random() * .09 },
    MLP:          { verdict: attack ? Math.random() > .15 : false, probability: attack ? .75 + Math.random() * .2 : .08 + Math.random() * .12 },
  };

  const featureImportance = [
    { feature: 'serror_rate',         impact: attack ? .85 : -.3 },
    { feature: 'count',               impact: attack ? .72 : -.15 },
    { feature: 'srv_count',           impact: attack ? .65 : -.1 },
    { feature: 'dst_host_srv_count',  impact: attack ? .55 : .08 },
    { feature: 'same_srv_rate',       impact: attack ? .48 : -.45 },
    { feature: 'flag',                impact: attack ? .42 : -.2 },
    { feature: 'src_bytes',           impact: attack ? -.15 : .55 },
    { feature: 'logged_in',           impact: attack ? -.35 : .48 },
    { feature: 'dst_bytes',           impact: attack ? -.28 : .4 },
    { feature: 'duration',            impact: attack ? .1 : .15 },
  ];

  return {
    isAttack: attack,
    attackType: attack ? (scenario.type === 'Custom' ? 'DoS' : scenario.type) : null,
    confidence,
    perModel,
    featureImportance,
    scenarioName: scenario.name,
    timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19),
  };
}
