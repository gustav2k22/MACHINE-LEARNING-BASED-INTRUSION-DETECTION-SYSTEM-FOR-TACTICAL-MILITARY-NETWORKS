"""
Multi-model stacking ensemble for intrusion detection.

Implements a two-level stacking architecture:

  **Level 0 — Base learners** (trained on original features):
    - RandomForest  (300 trees, balanced class weights, depth 25)
    - XGBoost       (300 rounds, dynamic scale_pos_weight, depth 10)
    - LightGBM      (300 rounds, is_unbalance=True, depth 15)
    - MLP           (128→64→32 neurons, ReLU, Adam, early stopping)

  **Level 1 — Meta-learner** (trained on 5-fold CV predictions of base learners):
    - LogisticRegression with max_iter=1000

Key functions:
    build_base_models(imbalance_ratio)  — Instantiate base classifiers
    train_stacking_ensemble(models, X, y) — Fit stacking meta-learner
    save_model(model, path) / load_model(path) — Persistence via joblib

The ``imbalance_ratio`` parameter adjusts XGBoost's ``scale_pos_weight``
dynamically based on the actual class distribution of each dataset.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict
import xgboost as xgb
import lightgbm as lgb
import joblib
from pathlib import Path

from src.config import RANDOM_STATE, MODELS_DIR


def build_base_models(imbalance_ratio=1.0):
    """Build the base classifiers for the ensemble.
    
    Args:
        imbalance_ratio: ratio of majority/minority class count.
            Used to set scale_pos_weight for XGBoost.
    """
    spw = max(1.0, imbalance_ratio * 0.5)  # Conservative class weight
    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=300,
            max_depth=25,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=300,
            max_depth=10,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            scale_pos_weight=spw,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "LightGBM": lgb.LGBMClassifier(
            n_estimators=300,
            max_depth=15,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            is_unbalance=True,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbose=-1,
        ),
        "MLP": MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation="relu",
            solver="adam",
            alpha=0.001,
            batch_size=256,
            learning_rate="adaptive",
            learning_rate_init=0.001,
            max_iter=200,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=15,
            random_state=RANDOM_STATE,
        ),
    }
    return models


def build_stacking_ensemble(base_models=None, imbalance_ratio=1.0):
    """
    Build a stacking ensemble that combines all base models
    with a LogisticRegression meta-learner.
    """
    if base_models is None:
        base_models = build_base_models(imbalance_ratio=imbalance_ratio)

    estimators = [(name, model) for name, model in base_models.items()]

    stacking = StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=RANDOM_STATE,
        ),
        cv=5,
        stack_method="predict_proba",
        n_jobs=-1,
        passthrough=False,
    )
    return stacking


def train_individual_models(X_train, y_train, dataset_name="unknown"):
    """
    Train each base model individually and return fitted models.
    """
    minority = (y_train == 1).sum()
    majority = (y_train == 0).sum()
    imbalance_ratio = majority / max(minority, 1)
    base_models = build_base_models(imbalance_ratio=imbalance_ratio)
    fitted = {}

    for name, model in base_models.items():
        print(f"  Training {name} on {dataset_name}...")
        model.fit(X_train, y_train)
        fitted[name] = model
        print(f"  {name} trained.")

    return fitted


def train_stacking_ensemble(X_train, y_train, dataset_name="unknown"):
    """
    Train the full stacking ensemble.
    """
    print(f"  Training Stacking Ensemble on {dataset_name}...")
    minority = (y_train == 1).sum()
    majority = (y_train == 0).sum()
    imbalance_ratio = majority / max(minority, 1)
    ensemble = build_stacking_ensemble(imbalance_ratio=imbalance_ratio)
    ensemble.fit(X_train, y_train)
    print(f"  Stacking Ensemble trained.")
    return ensemble


def save_model(model, dataset_name, model_name="ensemble"):
    """Save a trained model to disk."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    path = MODELS_DIR / f"{dataset_name}_{model_name}.joblib"
    joblib.dump(model, path)
    print(f"  Model saved: {path}")
    return path


def load_model(dataset_name, model_name="ensemble"):
    """Load a trained model from disk."""
    path = MODELS_DIR / f"{dataset_name}_{model_name}.joblib"
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    return joblib.load(path)
