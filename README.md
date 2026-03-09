# ML-Based Intrusion Detection System for Tactical Military Networks

A production-grade, multi-model ensemble Intrusion Detection System (IDS) trained and validated across **8 diverse network intrusion datasets**, achieving **0.9+ scores on all key metrics** (Accuracy, Precision, Recall, F1, ROC-AUC) for every dataset.

---

## Architecture

```
src/
├── config.py                  # Centralized configuration (paths, params, thresholds)
├── train_pipeline.py          # Main training orchestrator
├── data/
│   ├── preprocessor.py        # Dataset-specific loaders for all 8 datasets
│   └── feature_engineering.py # Scaling, feature selection, SMOTE balancing
├── models/
│   └── ensemble.py            # RF, XGBoost, LightGBM, MLP + Stacking meta-learner
├── evaluation/
│   ├── metrics.py             # Comprehensive metrics + threshold optimization
│   └── visualizations.py      # Confusion matrices, ROC curves, comparison charts
└── monitoring/
    └── dashboard.py           # Streamlit real-time monitoring dashboard
```

## Datasets (8 Total)

| Dataset | Type | Samples | Attack Ratio | Source |
|---|---|---|---|---|
| **NSL_KDD** | Traditional network | ~125K | ~53% | KDD'99 improved |
| **KDDCup99** | Traditional network | ~200K | ~80% | UCI repository |
| **Kaggle_NID** | Traditional network | ~25K | ~47% | Kaggle |
| **CIC_DDoS2019** | Flow-based DDoS | ~200K | ~69% | Canadian Institute |
| **CIDDS-001** | Flow-based | ~200K | ~72% | Coburg University |
| **DS2OS** | IoT application | ~71K | ~2.2% | IoT smart environment |
| **LUFlow** | Flow-based | ~200K | ~52% | Lancaster University |
| **NetworkLogs** | Application logs | ~17K | ~10% | Network activity logs |

## Models

The system uses a **multi-model ensemble** approach:

- **RandomForest** — 300 trees, balanced class weights, depth-25
- **XGBoost** — 300 boosting rounds, dynamic `scale_pos_weight` for imbalanced data
- **LightGBM** — 300 rounds, `is_unbalance=True`, depth-15
- **MLP** — 3-layer neural network (128→64→32), adaptive learning rate, early stopping
- **StackingEnsemble** — All 4 base models + LogisticRegression meta-learner

### Key Techniques
- **Dynamic class weighting**: XGBoost `scale_pos_weight` computed from actual class distribution
- **Threshold optimization**: When default 0.5 threshold fails targets, searches for optimal threshold maximizing F1 while keeping precision and recall ≥ 0.9
- **Adaptive SMOTE balancing**: Conservative for extreme imbalance (>10:1), moderate for balanced datasets
- **Rich feature engineering**: Frequency encoding, interaction features, and value parsing for IoT data (DS2OS)

## Results

**ALL 8 datasets exceed the 0.9 target on all key metrics.**

| Dataset | Best Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|---|
| NSL_KDD | RandomForest | 0.9880 | 0.9906 | 0.9883 | 0.9895 | 0.9995 |
| KDDCup99 | LightGBM | 0.9998 | 1.0000 | 0.9998 | 0.9999 | 1.0000 |
| Kaggle_NID | XGBoost | 0.9976 | 0.9983 | 0.9966 | 0.9974 | 0.9999 |
| CIC_DDoS2019 | LightGBM | 0.9994 | 0.9998 | 0.9994 | 0.9996 | 1.0000 |
| CIDDS_001 | XGBoost | 0.9999 | 0.9999 | 1.0000 | 0.9999 | 1.0000 |
| DS2OS | RandomForest | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| LUFlow | StackingEnsemble | 0.9997 | 0.9997 | 0.9998 | 0.9997 | 1.0000 |
| NetworkLogs | RandomForest | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Quick Start

### 1. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

> **macOS**: If XGBoost fails, run `brew install libomp` first.

### 2. Train All Models

```bash
# Train on all 8 datasets
python3 -m src.train_pipeline

# Train on a specific dataset
python3 -m src.train_pipeline NSL_KDD
```

### 3. Launch Monitoring Dashboard

```bash
streamlit run src/monitoring/dashboard.py
```

## Outputs

After training, the system generates:

```
models/                        # Trained model files (.joblib)
├── {dataset}_best_{model}.joblib
├── {dataset}_StackingEnsemble.joblib
└── {dataset}_meta.joblib      # Scaler, feature names, thresholds

outputs/
├── reports/
│   ├── metrics_report.json    # Full metrics for all models/datasets
│   └── summary_table.csv      # Consolidated results table
└── figures/
    ├── {dataset}_{model}_confusion_matrix.png
    ├── {dataset}_roc_curves.png
    └── metrics_comparison.png
```

## Evaluation Metrics

For each model on each dataset, the system computes:

| Metric | Description | Target |
|---|---|---|
| **Accuracy** | Overall correctness | ≥ 0.90 |
| **Precision** | True positive rate among predictions | ≥ 0.90 |
| **Recall** | True positive rate among actual positives | ≥ 0.90 |
| **F1 Score** | Harmonic mean of precision and recall | ≥ 0.90 |
| **ROC-AUC** | Area under ROC curve | ≥ 0.90 |
| **MCC** | Matthews Correlation Coefficient | Reported |
| **Specificity** | True negative rate | Reported |
| **FPR / FNR** | False positive / negative rates | Reported |

## SENTINEL-IDS React Dashboard

A production-grade, military-themed React dashboard for real-time IDS monitoring and analysis. Built with clean architecture, system theme awareness, and full accessibility support.

### Dashboard Architecture

```
sentinel-dashboard/src/
├── App.jsx                    # Root component — ThemeProvider + routing
├── context/
│   └── ThemeContext.jsx       # Dark/light mode with OS preference detection
├── hooks/
│   └── useSimulation.js       # Real-time packet, timeline, threat state
├── components/
│   ├── Panel.jsx              # Themed container + section heading
│   ├── KPICard.jsx            # Key Performance Indicator metric card
│   ├── SeverityBadge.jsx      # Color-coded alert severity badge
│   ├── ThreatMap.jsx          # Animated SVG tactical network map
│   ├── Sidebar.jsx            # Navigation sidebar with branding
│   └── TopBar.jsx             # Status bar with clock, threat level, theme toggle
├── pages/
│   ├── DashboardPage.jsx      # Page 1: Live monitoring, KPIs, traffic feed
│   ├── ScenarioTestPage.jsx   # Page 2: Scenario testing with predictions
│   ├── ModelPerformancePage.jsx # Page 3: Model metrics, confusion matrix, charts
│   ├── ArchitecturePage.jsx   # Page 4: System diagrams, pipeline, class diagram
│   └── AlertsPage.jsx         # Page 5: Filterable alert feed with CSV export
├── data/
│   ├── constants.js           # Colors, protocols, models, datasets
│   ├── metrics.js             # Real model performance data + scenarios
│   └── generators.js          # Mock data generators for simulation
└── index.css                  # Tailwind + custom animations + scanline overlay
```

### Dashboard Pages

| Page | Description |
|---|---|
| **Live Monitoring** | KPI cards, animated threat map, 60-min timeline, attack distribution, live traffic feed, active alerts |
| **Scenario Testing** | Pre-built attack scenarios, custom feature input, ensemble prediction with per-model breakdown, SHAP-style feature importance |
| **Model Performance** | Model overview cards, metrics comparison table, interactive confusion matrix, threshold optimization slider, dataset F1 comparison |
| **System Architecture** | 4-layer architecture diagram, stacking ensemble flow, 11-step preprocessing pipeline, UML class diagram |
| **Alerts & Reports** | Searchable/filterable alert table, pagination, severity and type filters, CSV export, alert detail modal |

### Theme Support

- **OS preference detection** via `prefers-color-scheme` media query
- **Manual toggle** in the top bar (Sun/Moon icon)
- **Smooth transitions** between dark military theme and light mode
- All components use theme-aware colors from `ThemeContext`

### Running the Dashboard

```bash
cd sentinel-dashboard
npm install
npm run dev          # Development server at localhost:5173
npm run build        # Production build to dist/
```

### Tech Stack

- **React 19** with hooks (useState, useEffect, useMemo, useCallback, useRef)
- **Vite 7** for fast dev/build
- **Tailwind CSS 4** for utility-first styling
- **Recharts** for AreaChart, PieChart, BarChart, LineChart
- **Lucide React** for military-grade iconography

## Streamlit Monitoring Dashboard

The Streamlit dashboard provides:

- **Model Performance Overview** — Per-dataset metric cards
- **Comparative Analysis** — Side-by-side model comparisons with heatmaps
- **Confusion Matrices** — Visual true/false positive/negative breakdowns
- **ROC Curves** — Per-dataset ROC curves with AUC values
- **Simulated Threat Monitor** — Real-time threat detection simulation

## Interactive Model Testing

```bash
streamlit run src/testing/model_tester.py
```

- **Pre-built Scenarios** — Normal browsing, DoS flood, port scan, brute force SSH
- **Custom Input** — Enter arbitrary feature vectors for prediction
- **Batch Testing** — Evaluate multiple samples simultaneously
- **Model Info** — Inspect loaded model metadata, feature names, thresholds

## Project Configuration

Key settings in `src/config.py`:

| Parameter | Value | Description |
|---|---|---|
| `RANDOM_STATE` | 42 | Reproducibility seed |
| `MAX_SAMPLE_SIZE` | 200,000 | Max rows per dataset |
| `TEST_SIZE` | 0.2 | Train/test split ratio |
| `N_CV_FOLDS` | 5 | Cross-validation folds |
| `MIN_METRIC_SCORE` | 0.90 | Performance target |

## License

This project is for academic and research purposes in tactical military network security.
