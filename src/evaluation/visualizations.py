"""
Visualization utilities for model evaluation results.

Generates publication-quality figures saved to ``outputs/figures/``:

    plot_confusion_matrix(y_true, y_pred, model, dataset, path)
        Heatmap of TP/FP/FN/TN with percentage annotations.

    plot_roc_curves(models_data, dataset, path)
        Overlay ROC curves for all models on one dataset with AUC values.

    plot_metrics_comparison(summary_df, path)
        Grouped bar chart comparing Accuracy, Precision, Recall, F1, ROC-AUC
        across all models and datasets.

All figures use a dark military-themed matplotlib style (navy background,
cyan/green/crimson accents) to match the SENTINEL-IDS dashboard aesthetic.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve
from pathlib import Path

from src.config import FIGURES_DIR


def plot_confusion_matrix(y_true, y_pred, model_name, dataset_name, save=True):
    """Plot and optionally save a confusion matrix."""
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["Normal", "Attack"],
        yticklabels=["Normal", "Attack"],
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix: {model_name}\n({dataset_name})")
    plt.tight_layout()

    if save:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        path = FIGURES_DIR / f"cm_{dataset_name}_{model_name}.png"
        fig.savefig(path, dpi=150)
        plt.close(fig)
        return path
    return fig


def plot_roc_curves(results_list, dataset_name, save=True):
    """
    Plot ROC curves for multiple models on the same dataset.
    results_list: list of dicts with keys 'model_name', 'y_true', 'y_proba'
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    for result in results_list:
        if result.get("y_proba") is not None:
            fpr, tpr, _ = roc_curve(result["y_true"], result["y_proba"])
            ax.plot(fpr, tpr, label=f"{result['model_name']} (AUC={result.get('roc_auc', 0):.3f})")

    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"ROC Curves - {dataset_name}")
    ax.legend(loc="lower right")
    plt.tight_layout()

    if save:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        path = FIGURES_DIR / f"roc_{dataset_name}.png"
        fig.savefig(path, dpi=150)
        plt.close(fig)
        return path
    return fig


def plot_metrics_comparison(summary_df, save=True):
    """Plot a grouped bar chart comparing metrics across all datasets and models."""
    metric_cols = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
    available_cols = [c for c in metric_cols if c in summary_df.columns]

    fig, axes = plt.subplots(1, len(available_cols), figsize=(4 * len(available_cols), 6))
    if len(available_cols) == 1:
        axes = [axes]

    for ax, metric in zip(axes, available_cols):
        pivot = summary_df.pivot_table(index="Dataset", columns="Model", values=metric)
        pivot.plot(kind="bar", ax=ax, rot=45)
        ax.set_title(metric)
        ax.set_ylim(0.5, 1.05)
        ax.axhline(y=0.9, color="r", linestyle="--", alpha=0.5, label="Target 0.9")
        ax.legend(fontsize=7)

    plt.suptitle("Model Performance Comparison Across Datasets", fontsize=14)
    plt.tight_layout()

    if save:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        path = FIGURES_DIR / "metrics_comparison.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return path
    return fig


def plot_dataset_summary_heatmap(summary_df, save=True):
    """Plot a heatmap of metrics across datasets for the ensemble model."""
    ensemble_df = summary_df[summary_df["Model"] == "StackingEnsemble"]
    if ensemble_df.empty:
        ensemble_df = summary_df.groupby("Dataset").last().reset_index()

    metric_cols = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "MCC", "Specificity"]
    available_cols = [c for c in metric_cols if c in ensemble_df.columns]

    pivot = ensemble_df.set_index("Dataset")[available_cols]

    fig, ax = plt.subplots(figsize=(10, max(4, len(pivot) * 0.8)))
    sns.heatmap(
        pivot, annot=True, fmt=".3f", cmap="RdYlGn", vmin=0.5, vmax=1.0,
        linewidths=0.5, ax=ax,
    )
    ax.set_title("Ensemble Model Performance Heatmap")
    plt.tight_layout()

    if save:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        path = FIGURES_DIR / "ensemble_heatmap.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return path
    return fig
