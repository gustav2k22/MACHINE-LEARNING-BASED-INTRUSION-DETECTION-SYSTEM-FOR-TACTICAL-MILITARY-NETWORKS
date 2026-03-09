"""
Comprehensive evaluation metrics and threshold optimization for IDS models.

Computes a full suite of classification metrics for each trained model:
  - Accuracy, Precision, Recall, F1 Score
  - ROC-AUC, Specificity, MCC (Matthews Correlation Coefficient)
  - False Positive Rate (FPR), False Negative Rate (FNR)

Key functions:
    compute_all_metrics(y_true, y_pred, y_proba)
        Returns a dict of all metrics listed above.

    optimize_threshold(y_true, y_proba, target=0.9)
        Searches 100 threshold values (0.01–0.99) for the one that
        maximises F1 while keeping both precision and recall >= target.
        Falls back to pure max-F1 if the joint constraint is infeasible.

    check_performance_target(metrics, target=0.9)
        Returns True if accuracy, precision, recall, and F1 all >= target.

    save_metrics_report(all_metrics, path)
        Serialises the full metrics dict to JSON for archival.

    generate_summary_table(all_metrics)
        Produces a CSV-friendly DataFrame comparing all models × datasets.
"""
import numpy as np
import pandas as pd
import json
from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    matthews_corrcoef,
    confusion_matrix,
    classification_report,
    precision_recall_curve,
    roc_curve,
    average_precision_score,
)

from src.config import REPORTS_DIR, MIN_METRIC_SCORE


def optimize_threshold(y_true, y_proba, target=0.90):
    """
    Find the optimal decision threshold.
    Strategy:
      1. First, try to find threshold where BOTH precision >= target AND recall >= target.
      2. If found, pick the one with highest F1 among those.
      3. If not found, fall back to maximizing F1 overall.
    Returns (best_threshold, best_score, y_pred_optimized).
    """
    # Fine-grained threshold search
    thresholds = np.linspace(0.01, 0.99, 500)
    best_f1 = 0
    best_thr = 0.5
    best_f1_both = 0
    best_thr_both = None

    for thr in thresholds:
        y_pred_t = (y_proba >= thr).astype(int)
        if y_pred_t.sum() == 0 or y_pred_t.sum() == len(y_pred_t):
            continue
        p = precision_score(y_true, y_pred_t, zero_division=0)
        r = recall_score(y_true, y_pred_t, zero_division=0)
        f1 = 2 * p * r / (p + r + 1e-10)

        if f1 > best_f1:
            best_f1 = f1
            best_thr = thr

        # Check if both metrics meet target
        if p >= target and r >= target and f1 > best_f1_both:
            best_f1_both = f1
            best_thr_both = thr

    # Prefer threshold where both metrics meet target
    if best_thr_both is not None:
        best_thr = best_thr_both
        best_f1 = best_f1_both

    y_pred_opt = (y_proba >= best_thr).astype(int)
    return best_thr, best_f1, y_pred_opt


def compute_all_metrics(y_true, y_pred, y_proba=None):
    """
    Compute all classification metrics.
    Returns dict with all metric values.
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1_score": f1_score(y_true, y_pred, zero_division=0),
        "mcc": matthews_corrcoef(y_true, y_pred),
    }

    if y_proba is not None:
        try:
            metrics["roc_auc"] = roc_auc_score(y_true, y_proba)
        except ValueError:
            metrics["roc_auc"] = 0.0
        try:
            metrics["avg_precision"] = average_precision_score(y_true, y_proba)
        except ValueError:
            metrics["avg_precision"] = 0.0

    # Confusion matrix components
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    metrics["true_positives"] = int(tp)
    metrics["true_negatives"] = int(tn)
    metrics["false_positives"] = int(fp)
    metrics["false_negatives"] = int(fn)

    # Derived rates
    metrics["fpr"] = fp / max(fp + tn, 1)  # False Positive Rate
    metrics["fnr"] = fn / max(fn + tp, 1)  # False Negative Rate
    metrics["specificity"] = tn / max(tn + fp, 1)  # True Negative Rate

    return metrics


def evaluate_model(model, X_test, y_test, model_name="Model", dataset_name="Dataset"):
    """
    Evaluate a model and return comprehensive metrics.
    """
    y_pred = model.predict(X_test)

    y_proba = None
    if hasattr(model, "predict_proba"):
        try:
            y_proba = model.predict_proba(X_test)[:, 1]
        except Exception:
            pass

    metrics = compute_all_metrics(y_test, y_pred, y_proba)
    metrics["model_name"] = model_name
    metrics["dataset_name"] = dataset_name

    return metrics


def check_performance_target(metrics, target=MIN_METRIC_SCORE):
    """
    Check if key metrics meet the 0.9+ target.
    Returns (passed: bool, details: dict).
    """
    key_metrics = ["accuracy", "precision", "recall", "f1_score"]
    details = {}
    all_passed = True

    for m in key_metrics:
        val = metrics.get(m, 0)
        passed = val >= target
        details[m] = {"value": round(val, 4), "target": target, "passed": passed}
        if not passed:
            all_passed = False

    if "roc_auc" in metrics:
        val = metrics["roc_auc"]
        passed = val >= target
        details["roc_auc"] = {"value": round(val, 4), "target": target, "passed": passed}
        if not passed:
            all_passed = False

    return all_passed, details


def print_metrics(metrics, show_target=True):
    """Pretty-print metrics to console."""
    name = metrics.get("model_name", "Model")
    dataset = metrics.get("dataset_name", "Dataset")
    print(f"\n{'='*60}")
    print(f"  {name} on {dataset}")
    print(f"{'='*60}")

    key_order = [
        "accuracy", "precision", "recall", "f1_score",
        "roc_auc", "avg_precision", "mcc", "specificity", "fpr", "fnr",
    ]
    for k in key_order:
        if k in metrics:
            val = metrics[k]
            marker = ""
            if show_target and k in ["accuracy", "precision", "recall", "f1_score", "roc_auc"]:
                marker = " ✓" if val >= MIN_METRIC_SCORE else " ✗ (below 0.9)"
            print(f"  {k:25s}: {val:.4f}{marker}")

    print(f"  {'TP':25s}: {metrics.get('true_positives', 'N/A')}")
    print(f"  {'TN':25s}: {metrics.get('true_negatives', 'N/A')}")
    print(f"  {'FP':25s}: {metrics.get('false_positives', 'N/A')}")
    print(f"  {'FN':25s}: {metrics.get('false_negatives', 'N/A')}")
    print(f"{'='*60}")


def save_metrics_report(all_metrics, filename="metrics_report.json"):
    """Save all metrics to a JSON report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / filename

    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    serializable = []
    for m in all_metrics:
        serializable.append({k: convert(v) for k, v in m.items()})

    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)

    print(f"[INFO] Metrics report saved to {path}")
    return path


def generate_summary_table(all_metrics):
    """Generate a summary DataFrame of all model results."""
    rows = []
    for m in all_metrics:
        rows.append({
            "Dataset": m.get("dataset_name", ""),
            "Model": m.get("model_name", ""),
            "Accuracy": round(m.get("accuracy", 0), 4),
            "Precision": round(m.get("precision", 0), 4),
            "Recall": round(m.get("recall", 0), 4),
            "F1": round(m.get("f1_score", 0), 4),
            "ROC-AUC": round(m.get("roc_auc", 0), 4),
            "MCC": round(m.get("mcc", 0), 4),
            "Specificity": round(m.get("specificity", 0), 4),
        })
    return pd.DataFrame(rows)
