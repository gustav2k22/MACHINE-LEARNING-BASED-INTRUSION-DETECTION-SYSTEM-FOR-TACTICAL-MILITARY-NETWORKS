"""
Streamlit-based Network Intrusion Detection Monitoring Dashboard.
Provides real-time monitoring, model metrics visualization, and threat analysis.
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import time
import os
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MODELS_DIR, REPORTS_DIR, FIGURES_DIR, DATASET_PATHS

# Page config
st.set_page_config(
    page_title="Military IDS Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_metrics_report():
    """Load the metrics report JSON."""
    path = REPORTS_DIR / "metrics_report.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


@st.cache_data
def load_summary_table():
    """Load the summary CSV."""
    path = REPORTS_DIR / "summary_table.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def render_header():
    """Render dashboard header."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: #e94560; margin: 0;">🛡️ Military Network IDS Monitor</h1>
        <p style="color: #a8a8a8; margin: 5px 0 0 0;">
            ML-Based Intrusion Detection System for Tactical Military Networks
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(summary_df):
    """Render top-level KPI metric cards."""
    if summary_df.empty:
        st.warning("No metrics data available. Run the training pipeline first.")
        return

    # Get ensemble metrics only
    ensemble_df = summary_df[summary_df["Model"] == "StackingEnsemble"]
    if ensemble_df.empty:
        ensemble_df = summary_df.groupby("Dataset").last().reset_index()

    cols = st.columns(6)
    metrics_map = {
        "Avg Accuracy": ensemble_df["Accuracy"].mean(),
        "Avg Precision": ensemble_df["Precision"].mean(),
        "Avg Recall": ensemble_df["Recall"].mean(),
        "Avg F1 Score": ensemble_df["F1"].mean(),
        "Avg ROC-AUC": ensemble_df["ROC-AUC"].mean() if "ROC-AUC" in ensemble_df else 0,
        "Datasets": len(ensemble_df),
    }

    for col, (label, value) in zip(cols, metrics_map.items()):
        with col:
            if isinstance(value, float):
                color = "#00ff88" if value >= 0.9 else "#ff6b6b"
                st.markdown(f"""
                <div style="background: #1a1a2e; padding: 15px; border-radius: 8px;
                            border-left: 4px solid {color}; text-align: center;">
                    <p style="color: #a8a8a8; margin: 0; font-size: 12px;">{label}</p>
                    <h2 style="color: {color}; margin: 5px 0;">{value:.4f}</h2>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #1a1a2e; padding: 15px; border-radius: 8px;
                            border-left: 4px solid #4ecdc4; text-align: center;">
                    <p style="color: #a8a8a8; margin: 0; font-size: 12px;">{label}</p>
                    <h2 style="color: #4ecdc4; margin: 5px 0;">{value}</h2>
                </div>
                """, unsafe_allow_html=True)


def render_performance_heatmap(summary_df):
    """Render performance heatmap across datasets and models."""
    st.subheader("Performance Heatmap")

    metric_cols = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "MCC", "Specificity"]
    available = [c for c in metric_cols if c in summary_df.columns]

    # Pivot for ensemble only
    ensemble_df = summary_df[summary_df["Model"] == "StackingEnsemble"]
    if ensemble_df.empty:
        ensemble_df = summary_df.groupby("Dataset").last().reset_index()

    if ensemble_df.empty:
        return

    pivot = ensemble_df.set_index("Dataset")[available]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="RdYlGn",
        zmin=0.5, zmax=1.0,
        text=np.round(pivot.values, 4),
        texttemplate="%{text}",
        textfont={"size": 12},
    ))
    fig.update_layout(
        height=max(300, len(pivot) * 60),
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_model_comparison(summary_df):
    """Render model comparison charts."""
    st.subheader("Model Comparison Across Datasets")

    metric = st.selectbox(
        "Select Metric",
        ["F1", "Accuracy", "Precision", "Recall", "ROC-AUC", "MCC"],
        index=0,
    )

    if metric not in summary_df.columns:
        st.warning(f"Metric {metric} not available.")
        return

    fig = px.bar(
        summary_df,
        x="Dataset", y=metric, color="Model",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.add_hline(y=0.9, line_dash="dash", line_color="red",
                  annotation_text="Target: 0.9")
    fig.update_layout(
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        yaxis=dict(range=[0.5, 1.05]),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_dataset_detail(summary_df, metrics_data):
    """Render detailed view for a specific dataset."""
    st.subheader("Dataset Detail View")

    datasets = summary_df["Dataset"].unique().tolist()
    if not datasets:
        return

    selected = st.selectbox("Select Dataset", datasets)
    ds_data = summary_df[summary_df["Dataset"] == selected]

    # Metrics table
    st.dataframe(
        ds_data.style.background_gradient(cmap="RdYlGn", vmin=0.5, vmax=1.0,
                                           subset=["Accuracy", "Precision", "Recall", "F1"]),
        use_container_width=True,
    )

    # Confusion matrix images
    col1, col2 = st.columns(2)
    with col1:
        cm_path = FIGURES_DIR / f"cm_{selected}_StackingEnsemble.png"
        if cm_path.exists():
            st.image(str(cm_path), caption="Stacking Ensemble Confusion Matrix")
        else:
            # Try other models
            for model in ["RandomForest", "XGBoost", "LightGBM"]:
                alt_path = FIGURES_DIR / f"cm_{selected}_{model}.png"
                if alt_path.exists():
                    st.image(str(alt_path), caption=f"{model} Confusion Matrix")
                    break

    with col2:
        roc_path = FIGURES_DIR / f"roc_{selected}.png"
        if roc_path.exists():
            st.image(str(roc_path), caption="ROC Curves")

    # Detailed metrics from JSON
    ds_metrics = [m for m in metrics_data if m.get("dataset_name") == selected]
    if ds_metrics:
        st.markdown("**Detailed Metrics:**")
        for m in ds_metrics:
            with st.expander(f"{m.get('model_name', 'Model')}"):
                detail_cols = st.columns(4)
                detail_items = [
                    ("Accuracy", m.get("accuracy")),
                    ("Precision", m.get("precision")),
                    ("Recall", m.get("recall")),
                    ("F1 Score", m.get("f1_score")),
                    ("ROC AUC", m.get("roc_auc")),
                    ("MCC", m.get("mcc")),
                    ("Specificity", m.get("specificity")),
                    ("FPR", m.get("fpr")),
                    ("FNR", m.get("fnr")),
                    ("True Positives", m.get("true_positives")),
                    ("True Negatives", m.get("true_negatives")),
                    ("False Positives", m.get("false_positives")),
                    ("False Negatives", m.get("false_negatives")),
                ]
                for i, (label, val) in enumerate(detail_items):
                    with detail_cols[i % 4]:
                        if val is not None:
                            if isinstance(val, float):
                                st.metric(label, f"{val:.4f}")
                            else:
                                st.metric(label, str(val))


def render_radar_chart(summary_df):
    """Render radar chart for ensemble performance."""
    st.subheader("Ensemble Performance Radar")

    ensemble_df = summary_df[summary_df["Model"] == "StackingEnsemble"]
    if ensemble_df.empty:
        ensemble_df = summary_df.groupby("Dataset").last().reset_index()

    if ensemble_df.empty:
        return

    metrics = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
    available = [m for m in metrics if m in ensemble_df.columns]

    fig = go.Figure()
    for _, row in ensemble_df.iterrows():
        values = [row.get(m, 0) for m in available]
        values.append(values[0])  # Close the polygon
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=available + [available[0]],
            fill="toself",
            name=row["Dataset"],
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0.5, 1.0]),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_threat_simulator(summary_df):
    """Simulated network monitoring panel."""
    st.subheader("Network Threat Monitor (Simulation)")

    col1, col2, col3 = st.columns(3)
    with col1:
        total_packets = np.random.randint(50000, 200000)
        st.metric("Total Packets Analyzed", f"{total_packets:,}")
    with col2:
        threats = np.random.randint(100, 5000)
        st.metric("Threats Detected", f"{threats:,}", delta=f"-{np.random.randint(10,50)}")
    with col3:
        uptime = 99.0 + np.random.random() * 0.99
        st.metric("System Uptime", f"{uptime:.2f}%")

    # Simulated time-series threat data
    n_points = 100
    timestamps = pd.date_range(end=pd.Timestamp.now(), periods=n_points, freq="1min")
    normal_traffic = np.random.poisson(500, n_points)
    attack_traffic = np.random.poisson(50, n_points)
    attack_traffic[60:75] = np.random.poisson(300, 15)  # Simulated spike

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps, y=normal_traffic, name="Normal Traffic",
        fill="tozeroy", line=dict(color="#00ff88"),
    ))
    fig.add_trace(go.Scatter(
        x=timestamps, y=attack_traffic, name="Attack Traffic",
        fill="tozeroy", line=dict(color="#ff6b6b"),
    ))
    fig.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Time",
        yaxis_title="Packets",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_sidebar():
    """Render sidebar with navigation and info."""
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "Select View",
            ["Overview", "Model Comparison", "Dataset Details",
             "Radar Analysis", "Threat Monitor"],
            index=0,
        )

        st.markdown("---")
        st.markdown("### System Info")

        # Check for trained models
        model_files = list(MODELS_DIR.glob("*.joblib")) if MODELS_DIR.exists() else []
        st.info(f"Trained models: {len(model_files)}")

        report_path = REPORTS_DIR / "metrics_report.json"
        if report_path.exists():
            mod_time = pd.Timestamp.fromtimestamp(report_path.stat().st_mtime)
            st.info(f"Last training: {mod_time.strftime('%Y-%m-%d %H:%M')}")

        st.markdown("---")
        st.markdown("### Target")
        st.markdown("All metrics >= **0.90**")

        return page


def main():
    """Main dashboard entry point."""
    render_header()

    # Load data
    summary_df = load_summary_table()
    metrics_data = load_metrics_report()

    page = render_sidebar()

    if summary_df.empty:
        st.warning(
            "No training results found. Run the training pipeline first:\n"
            "```bash\npython -m src.train_pipeline\n```"
        )
        return

    if page == "Overview":
        render_kpi_cards(summary_df)
        st.markdown("---")
        render_performance_heatmap(summary_df)
        st.markdown("---")
        render_threat_simulator(summary_df)

    elif page == "Model Comparison":
        render_kpi_cards(summary_df)
        st.markdown("---")
        render_model_comparison(summary_df)

    elif page == "Dataset Details":
        render_dataset_detail(summary_df, metrics_data)

    elif page == "Radar Analysis":
        render_radar_chart(summary_df)

    elif page == "Threat Monitor":
        render_threat_simulator(summary_df)


if __name__ == "__main__":
    main()
