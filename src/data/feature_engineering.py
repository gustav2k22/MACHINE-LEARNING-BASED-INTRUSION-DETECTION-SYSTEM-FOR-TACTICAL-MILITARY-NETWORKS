"""
Feature engineering pipeline: scaling, feature selection, and class balancing.

Transforms a raw labelled DataFrame into train/test arrays ready for model
training.  The main entry point is ``prepare_dataset(df)``, which executes:

  1. **Remove constant features** — VarianceThreshold(0) to drop zero-variance cols
  2. **Remove highly correlated features** — Pearson |r| > 0.95 elimination
  3. **Train-test split** — 80/20 stratified split preserving class distribution
  4. **Robust scaling** — RobustScaler (median/IQR) for outlier-resistant normalisation
  5. **Class balancing** — Tiered SMOTE strategy:
       - Extreme imbalance (>10:1): conservative 3x minority oversample
       - Moderate imbalance (>3:1): SMOTE to 50% of majority
       - Near-balanced: skip balancing entirely

Returns:
    X_train, X_test, y_train, y_test, scaler, feature_names
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline

from src.config import RANDOM_STATE, TEST_SIZE


def remove_constant_features(X, threshold=0.01):
    """Remove features with near-zero variance."""
    selector = VarianceThreshold(threshold=threshold)
    X_selected = selector.fit_transform(X)
    kept_cols = X.columns[selector.get_support()].tolist()
    return pd.DataFrame(X_selected, columns=kept_cols, index=X.index), selector


def remove_highly_correlated(X, threshold=0.95):
    """Remove one of each pair of features with correlation above threshold."""
    corr_matrix = X.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
    return X.drop(columns=to_drop, errors="ignore"), to_drop


def prepare_dataset(df, scale=True, balance=True, remove_corr=True):
    """
    Full feature engineering pipeline for a single dataset.
    
    Returns:
        X_train, X_test, y_train, y_test, scaler, feature_names
    """
    # Separate features and label
    y = df["label"].astype(int)
    X = df.drop(columns=["label"])

    # Ensure all numeric
    X = X.apply(pd.to_numeric, errors="coerce").fillna(0)

    # Replace infinities
    X = X.replace([np.inf, -np.inf], 0)

    # Remove constant features
    if X.shape[1] > 5:
        X, _ = remove_constant_features(X)

    # Remove highly correlated features
    if remove_corr and X.shape[1] > 10:
        X, dropped = remove_highly_correlated(X, threshold=0.95)

    feature_names = X.columns.tolist()

    # Train-test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # Scale features
    scaler = None
    if scale:
        scaler = RobustScaler()
        X_train = pd.DataFrame(
            scaler.fit_transform(X_train), columns=feature_names, index=X_train.index
        )
        X_test = pd.DataFrame(
            scaler.transform(X_test), columns=feature_names, index=X_test.index
        )

    # Balance classes — strategy depends on imbalance severity
    if balance:
        minority_count = y_train.value_counts().min()
        majority_count = y_train.value_counts().max()
        imbalance_ratio = majority_count / max(minority_count, 1)

        if imbalance_ratio > 10 and minority_count >= 6:
            # Extreme imbalance: very conservative SMOTE (3x minority only)
            try:
                target_minority = min(minority_count * 3, int(majority_count * 0.15))
                smote = SMOTE(
                    sampling_strategy=target_minority / majority_count,
                    random_state=RANDOM_STATE,
                    k_neighbors=min(5, minority_count - 1),
                )
                X_train_arr, y_train = smote.fit_resample(X_train, y_train)
                X_train = pd.DataFrame(X_train_arr, columns=feature_names)
                print(f"  [INFO] Extreme imbalance ({imbalance_ratio:.1f}:1): conservative SMOTE to {target_minority} minority")
            except Exception as e:
                print(f"  [WARN] SMOTE failed, using original: {e}")
        elif imbalance_ratio > 1.5 and minority_count >= 6:
            # Moderate imbalance: SMOTE to 60% of majority + light undersampling
            try:
                smote_target = min(int(majority_count * 0.6), minority_count * 5)
                smote = SMOTE(
                    sampling_strategy=min(1.0, smote_target / majority_count),
                    random_state=RANDOM_STATE,
                    k_neighbors=min(5, minority_count - 1),
                )
                under = RandomUnderSampler(
                    sampling_strategy=0.7,
                    random_state=RANDOM_STATE,
                )
                resampler = ImbPipeline([("smote", smote), ("under", under)])
                X_train_arr, y_train = resampler.fit_resample(X_train, y_train)
                X_train = pd.DataFrame(X_train_arr, columns=feature_names)
            except Exception as e:
                print(f"[WARN] Balancing failed, proceeding with original distribution: {e}")

    print(f"  Features: {len(feature_names)}, "
          f"Train: {len(X_train)} (attack={y_train.mean():.2f}), "
          f"Test: {len(X_test)} (attack={y_test.mean():.2f})")

    return X_train, X_test, y_train, y_test, scaler, feature_names
