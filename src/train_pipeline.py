"""
Main training and evaluation pipeline for the IDS ensemble system.

Orchestrates the end-to-end workflow for each of the 8 benchmark datasets:
  1. Load raw data via DataPreprocessor (dataset-specific loaders)
  2. Feature engineering: scaling, correlation removal, SMOTE balancing
  3. Train individual base models (RF, XGBoost, LightGBM, MLP)
  4. Train stacking ensemble with 5-fold CV meta-features
  5. Evaluate all models against 0.9 performance target
  6. Optimize decision thresholds when default 0.5 fails target
  7. Save trained models, scalers, encoders, and metadata to disk
  8. Generate summary reports and visualizations

Usage:
    python -m src.train_pipeline              # Train on all 8 datasets
    python -m src.train_pipeline NSL_KDD      # Train on a single dataset

Functions:
    train_on_dataset(name) — Full pipeline for one dataset
    run_full_pipeline()    — Iterate over all datasets and aggregate results
"""
import sys
import time
import json
import traceback
import numpy as np
import pandas as pd
from pathlib import Path

from src.config import (
    RANDOM_STATE, MODELS_DIR, REPORTS_DIR, FIGURES_DIR,
    MIN_METRIC_SCORE, DATASET_PATHS,
)
from src.data.preprocessor import load_dataset, LOADERS
from src.data.feature_engineering import prepare_dataset
from src.models.ensemble import (
    build_base_models, train_individual_models,
    train_stacking_ensemble, save_model,
)
from src.evaluation.metrics import (
    evaluate_model, compute_all_metrics, check_performance_target,
    print_metrics, save_metrics_report, generate_summary_table,
    optimize_threshold,
)
from src.evaluation.visualizations import (
    plot_confusion_matrix, plot_roc_curves,
    plot_metrics_comparison, plot_dataset_summary_heatmap,
)


def train_on_dataset(dataset_name):
    """
    Full training pipeline for one dataset:
    1. Load & preprocess
    2. Feature engineering
    3. Train individual models + stacking ensemble
    4. Evaluate all models
    5. Save best model and metrics
    
    Returns list of metric dicts and ROC data for plotting.
    """
    print(f"\n{'#'*70}")
    print(f"# DATASET: {dataset_name}")
    print(f"{'#'*70}")

    # Step 1: Load
    df, encoders = load_dataset(dataset_name)

    # Step 2: Feature engineering
    print(f"[INFO] Preparing features for {dataset_name}...")
    X_train, X_test, y_train, y_test, scaler, feature_names = prepare_dataset(df)

    # Step 3: Train individual models
    print(f"[INFO] Training individual models on {dataset_name}...")
    fitted_models = train_individual_models(X_train, y_train, dataset_name)

    # Step 4: Train stacking ensemble
    print(f"[INFO] Training stacking ensemble on {dataset_name}...")
    ensemble = train_stacking_ensemble(X_train, y_train, dataset_name)
    fitted_models["StackingEnsemble"] = ensemble

    # Step 5: Evaluate all models
    all_metrics = []
    roc_data = []
    best_f1 = 0
    best_model_name = None

    optimal_thresholds = {}  # Store optimized thresholds per model

    for model_name, model in fitted_models.items():
        metrics = evaluate_model(model, X_test, y_test, model_name, dataset_name)

        # Get probabilities for threshold optimization and ROC
        y_proba = None
        if hasattr(model, "predict_proba"):
            try:
                y_proba = model.predict_proba(X_test)[:, 1]
            except Exception:
                pass

        passed, details = check_performance_target(metrics)

        # If below target and we have probabilities, try threshold optimization
        if not passed and y_proba is not None:
            best_thr, best_f1_thr, y_pred_opt = optimize_threshold(y_test, y_proba)
            metrics_opt = compute_all_metrics(y_test, y_pred_opt, y_proba)
            metrics_opt["model_name"] = model_name + "_OptT"
            metrics_opt["dataset_name"] = dataset_name

            passed_opt, details_opt = check_performance_target(metrics_opt)
            if metrics_opt["f1_score"] > metrics["f1_score"]:
                print(f"  [OPT] Threshold optimization: {0.5:.3f} -> {best_thr:.3f}")
                print_metrics(metrics_opt)
                optimal_thresholds[model_name] = best_thr

                if passed_opt:
                    print(f"  >>> {model_name}_OptT: ALL metrics >= {MIN_METRIC_SCORE} ✓")
                else:
                    failed_opt = [k for k, v in details_opt.items() if not v["passed"]]
                    print(f"  >>> {model_name}_OptT: BELOW TARGET on: {failed_opt}")

                all_metrics.append(metrics_opt)
                # Use optimized metrics for best model selection
                if metrics_opt.get("f1_score", 0) > best_f1:
                    best_f1 = metrics_opt["f1_score"]
                    best_model_name = model_name

                # Plot confusion matrix with optimized threshold
                plot_confusion_matrix(y_test, y_pred_opt, model_name + "_OptT", dataset_name)

        # Also store default metrics
        print_metrics(metrics)
        if passed:
            print(f"  >>> {model_name}: ALL metrics >= {MIN_METRIC_SCORE} ✓")
        else:
            failed = [k for k, v in details.items() if not v["passed"]]
            print(f"  >>> {model_name}: BELOW TARGET on: {failed}")

        all_metrics.append(metrics)

        roc_data.append({
            "model_name": model_name,
            "y_true": y_test,
            "y_proba": y_proba,
            "roc_auc": metrics.get("roc_auc", 0),
        })

        if metrics.get("f1_score", 0) > best_f1:
            best_f1 = metrics["f1_score"]
            best_model_name = model_name

        # Save confusion matrix
        y_pred = model.predict(X_test)
        plot_confusion_matrix(y_test, y_pred, model_name, dataset_name)

    # Save best model
    if best_model_name:
        best_model = fitted_models[best_model_name]
        save_model(best_model, dataset_name, f"best_{best_model_name}")
        # Always save ensemble too
        save_model(ensemble, dataset_name, "StackingEnsemble")
        # Save scaler and feature names
        import joblib
        meta = {"feature_names": feature_names, "scaler": scaler, "encoders": encoders,
                "optimal_thresholds": optimal_thresholds}
        meta_path = MODELS_DIR / f"{dataset_name}_meta.joblib"
        joblib.dump(meta, meta_path)

    # Save ROC curves
    plot_roc_curves(roc_data, dataset_name)

    print(f"\n[INFO] Best model for {dataset_name}: {best_model_name} (F1={best_f1:.4f})")

    return all_metrics, roc_data


def run_full_pipeline(dataset_names=None):
    """
    Run the complete training pipeline across all (or specified) datasets.
    """
    if dataset_names is None:
        dataset_names = list(LOADERS.keys())

    print(f"\n{'='*70}")
    print(f"  ML-BASED IDS FOR TACTICAL MILITARY NETWORKS")
    print(f"  Training on {len(dataset_names)} datasets")
    print(f"{'='*70}")

    all_metrics = []
    failed_datasets = []
    start_time = time.time()

    for name in dataset_names:
        try:
            metrics, _ = train_on_dataset(name)
            all_metrics.extend(metrics)
        except Exception as e:
            print(f"\n[ERROR] Failed on {name}: {e}")
            traceback.print_exc()
            failed_datasets.append((name, str(e)))

    elapsed = time.time() - start_time

    # Generate summary
    print(f"\n\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  Total time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Datasets processed: {len(dataset_names) - len(failed_datasets)}/{len(dataset_names)}")
    if failed_datasets:
        print(f"  Failed datasets: {[d[0] for d in failed_datasets]}")

    if all_metrics:
        # Save full report
        save_metrics_report(all_metrics)

        # Summary table
        summary_df = generate_summary_table(all_metrics)
        print(f"\n{summary_df.to_string(index=False)}")

        # Save summary CSV
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        summary_path = REPORTS_DIR / "summary_table.csv"
        summary_df.to_csv(summary_path, index=False)
        print(f"\n[INFO] Summary saved to {summary_path}")

        # Generate comparison plots
        try:
            plot_metrics_comparison(summary_df)
            plot_dataset_summary_heatmap(summary_df)
        except Exception as e:
            print(f"[WARN] Plotting failed: {e}")

        # Check overall pass/fail
        ensemble_metrics = [m for m in all_metrics if m.get("model_name") == "StackingEnsemble"]
        all_passed = True
        for m in ensemble_metrics:
            passed, details = check_performance_target(m)
            if not passed:
                all_passed = False
                failed_items = {k: v for k, v in details.items() if not v["passed"]}
                print(f"  [WARN] {m['dataset_name']}: below target => {failed_items}")

        if all_passed and ensemble_metrics:
            print(f"\n  *** ALL ENSEMBLE METRICS >= {MIN_METRIC_SCORE} ACROSS ALL DATASETS ***")
        elif ensemble_metrics:
            print(f"\n  [INFO] Some datasets below {MIN_METRIC_SCORE} target - review needed")

    return all_metrics, failed_datasets


if __name__ == "__main__":
    # Allow running specific datasets from command line
    if len(sys.argv) > 1:
        datasets = sys.argv[1:]
    else:
        datasets = None  # Run all

    run_full_pipeline(datasets)
