"""
Centralized configuration for the ML-Based Intrusion Detection System.

Defines all project-wide constants, file paths, dataset mappings, model
hyperparameter defaults, and performance thresholds. Every other module
imports from here so that changes propagate consistently.

Sections:
    - Project paths (root, datasets, models, outputs, reports, figures)
    - Dataset directory mappings (8 benchmark datasets)
    - Dataset category groups (traditional, flow-based, IoT)
    - Training parameters (random state, sample size, split ratio, CV folds)
    - Performance target (minimum metric score for pass/fail)
    - Model name constants
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
FIGURES_DIR = OUTPUTS_DIR / "figures"

# Dataset directory mappings
DATASET_PATHS = {
    "NSL_KDD": DATASETS_DIR / "NSL_KDD (Unzipped Files)",
    "KDDCup99": DATASETS_DIR / "KDDCup99 (Unzipped Files)",
    "CIC_DDoS2019": DATASETS_DIR / "CIC_DDoS2019 (Unzipped Files)",
    "CIDDS_001": DATASETS_DIR / "CIDDS-001 (Unzipped Files)",
    "DS2OS": DATASETS_DIR / "DS2OS (Unzipped Files)",
    "Kaggle_NID": DATASETS_DIR / "Kaggle_Network_Intrusion_Dataset (Unzipped Files)",
    "LUFlow": DATASETS_DIR / "archive (2) (Unzipped Files)",
    "NetworkLogs": DATASETS_DIR / "archive (5) (Unzipped Files)",
}

# Dataset categories for the multi-model ensemble
DATASET_GROUPS = {
    "traditional_network": ["NSL_KDD", "KDDCup99", "Kaggle_NID"],
    "flow_based": ["CIDDS_001", "CIC_DDoS2019", "LUFlow"],
    "iot_application": ["DS2OS", "NetworkLogs"],
}

# Random seed for reproducibility
RANDOM_STATE = 42

# Model training config
MAX_SAMPLE_SIZE = 200_000  # Max rows per dataset for training (memory management)
TEST_SIZE = 0.2
N_CV_FOLDS = 5

# Performance target
MIN_METRIC_SCORE = 0.90

# Ensemble model names
MODEL_NAMES = [
    "RandomForest",
    "XGBoost",
    "LightGBM",
    "MLP",
]

META_LEARNER = "LogisticRegression"
