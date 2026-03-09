"""
Interactive Model Testing Application for the ML-Based IDS.
Allows users to test trained models with pre-built attack scenarios
or custom feature inputs, with mobile-friendly responsive UI.
"""
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.graph_objects as go
from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MODELS_DIR, REPORTS_DIR, FIGURES_DIR, DATASET_PATHS

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="IDS Model Tester",
    page_icon="\u26a1",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Mobile-friendly CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global */
    .main .block-container { padding: 1rem 1rem 3rem 1rem; max-width: 100%; }
    /* Cards */
    .scenario-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155; border-radius: 12px; padding: 16px;
        margin-bottom: 12px; cursor: pointer; transition: all 0.3s ease;
    }
    .scenario-card:hover { border-color: #3b82f6; transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(59,130,246,0.2); }
    .attack-badge {
        display: inline-block; padding: 2px 10px; border-radius: 12px;
        font-size: 12px; font-weight: 600;
    }
    .badge-dos { background: #dc2626; color: white; }
    .badge-probe { background: #f59e0b; color: black; }
    .badge-r2l { background: #8b5cf6; color: white; }
    .badge-u2r { background: #ec4899; color: white; }
    .badge-ddos { background: #ef4444; color: white; }
    .badge-normal { background: #22c55e; color: white; }
    .badge-iot { background: #06b6d4; color: white; }
    .badge-scan { background: #f97316; color: white; }
    /* Result panels */
    .result-safe {
        background: linear-gradient(135deg, #064e3b, #065f46);
        border: 2px solid #10b981; border-radius: 12px; padding: 20px;
        text-align: center;
    }
    .result-attack {
        background: linear-gradient(135deg, #7f1d1d, #991b1b);
        border: 2px solid #ef4444; border-radius: 12px; padding: 20px;
        text-align: center;
    }
    /* Responsive */
    @media (max-width: 768px) {
        .main .block-container { padding: 0.5rem; }
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.1rem !important; }
        h3 { font-size: 1rem !important; }
    }
    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    /* Gauge */
    .confidence-gauge { text-align: center; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------
@st.cache_resource
def load_model_and_meta(dataset_name, model_type="best"):
    """Load a trained model and its metadata."""
    meta_path = MODELS_DIR / f"{dataset_name}_meta.joblib"
    if not meta_path.exists():
        return None, None

    meta = joblib.load(meta_path)

    n_features = len(meta["feature_names"])

    # Find model file
    model = None
    if model_type == "best":
        # Sort by modification time (newest first) to avoid stale models
        best_files = sorted(
            MODELS_DIR.glob(f"{dataset_name}_best_*.joblib"),
            key=lambda p: p.stat().st_mtime, reverse=True,
        )
        for bf in best_files:
            candidate = joblib.load(bf)
            # Verify feature compatibility
            try:
                dummy = np.zeros((1, n_features))
                candidate.predict(dummy)
                model = candidate
                break
            except Exception:
                continue
        # Fallback to ensemble if no compatible best model
        if model is None:
            ens_path = MODELS_DIR / f"{dataset_name}_StackingEnsemble.joblib"
            if ens_path.exists():
                model = joblib.load(ens_path)

    elif model_type == "ensemble":
        ens_path = MODELS_DIR / f"{dataset_name}_StackingEnsemble.joblib"
        if ens_path.exists():
            model = joblib.load(ens_path)

    return model, meta


def get_available_datasets():
    """Get list of datasets with trained models."""
    datasets = []
    for p in MODELS_DIR.glob("*_meta.joblib"):
        name = p.stem.replace("_meta", "")
        datasets.append(name)
    return sorted(datasets)


# ---------------------------------------------------------------------------
# Attack Scenario Definitions
# ---------------------------------------------------------------------------
SCENARIOS = {
    "NSL_KDD": {
        "normal_web_browsing": {
            "name": "Normal Web Browsing",
            "description": "Regular HTTP traffic from a user browsing the web. Typical benign session.",
            "badge": "badge-normal",
            "badge_text": "Normal",
            "expected": "Normal",
            "features": {
                "protocol_type": "tcp", "service": "http", "flag": "SF",
                "src_bytes": 215, "dst_bytes": 45076, "wrong_fragment": 0,
                "hot": 0, "num_failed_logins": 0, "logged_in": 1,
                "num_compromised": 0, "num_file_creations": 0, "is_guest_login": 0,
                "count": 5, "srv_count": 5, "serror_rate": 0.0, "rerror_rate": 0.0,
                "same_srv_rate": 1.0, "diff_srv_rate": 0.0, "srv_diff_host_rate": 0.0,
                "dst_host_count": 255, "dst_host_srv_count": 255,
                "dst_host_same_srv_rate": 1.0, "dst_host_diff_srv_rate": 0.0,
                "dst_host_same_src_port_rate": 0.0, "dst_host_serror_rate": 0.0,
                "dst_host_srv_serror_rate": 0.0, "dst_host_rerror_rate": 0.0,
                "dst_host_srv_rerror_rate": 0.0,
            },
        },
        "neptune_dos": {
            "name": "Neptune SYN Flood (DoS)",
            "description": "SYN flood attack sending many half-open connections to overwhelm the target server.",
            "badge": "badge-dos",
            "badge_text": "DoS",
            "expected": "Attack",
            "features": {
                "protocol_type": "tcp", "service": "private", "flag": "S0",
                "src_bytes": 0, "dst_bytes": 0, "wrong_fragment": 0,
                "hot": 0, "num_failed_logins": 0, "logged_in": 0,
                "num_compromised": 0, "num_file_creations": 0, "is_guest_login": 0,
                "count": 511, "srv_count": 511, "serror_rate": 1.0, "rerror_rate": 0.0,
                "same_srv_rate": 1.0, "diff_srv_rate": 0.0, "srv_diff_host_rate": 0.0,
                "dst_host_count": 255, "dst_host_srv_count": 255,
                "dst_host_same_srv_rate": 1.0, "dst_host_diff_srv_rate": 0.0,
                "dst_host_same_src_port_rate": 1.0, "dst_host_serror_rate": 1.0,
                "dst_host_srv_serror_rate": 1.0, "dst_host_rerror_rate": 0.0,
                "dst_host_srv_rerror_rate": 0.0,
            },
        },
        "portsweep_probe": {
            "name": "Portsweep (Probe/Scan)",
            "description": "Reconnaissance attack scanning multiple ports on a target to find open services.",
            "badge": "badge-probe",
            "badge_text": "Probe",
            "expected": "Attack",
            "features": {
                "protocol_type": "tcp", "service": "private", "flag": "REJ",
                "src_bytes": 0, "dst_bytes": 0, "wrong_fragment": 0,
                "hot": 0, "num_failed_logins": 0, "logged_in": 0,
                "num_compromised": 0, "num_file_creations": 0, "is_guest_login": 0,
                "count": 302, "srv_count": 8, "serror_rate": 0.0, "rerror_rate": 0.97,
                "same_srv_rate": 0.03, "diff_srv_rate": 0.07, "srv_diff_host_rate": 0.0,
                "dst_host_count": 255, "dst_host_srv_count": 1,
                "dst_host_same_srv_rate": 0.0, "dst_host_diff_srv_rate": 0.06,
                "dst_host_same_src_port_rate": 0.0, "dst_host_serror_rate": 0.0,
                "dst_host_srv_serror_rate": 0.0, "dst_host_rerror_rate": 1.0,
                "dst_host_srv_rerror_rate": 1.0,
            },
        },
        "guess_passwd_r2l": {
            "name": "Password Guessing (R2L)",
            "description": "Remote-to-local brute force attack attempting to guess user credentials via repeated login failures.",
            "badge": "badge-r2l",
            "badge_text": "R2L",
            "expected": "Attack",
            "features": {
                "protocol_type": "tcp", "service": "ftp", "flag": "SF",
                "src_bytes": 188, "dst_bytes": 786, "wrong_fragment": 0,
                "hot": 0, "num_failed_logins": 5, "logged_in": 0,
                "num_compromised": 0, "num_file_creations": 0, "is_guest_login": 0,
                "count": 6, "srv_count": 6, "serror_rate": 0.0, "rerror_rate": 0.0,
                "same_srv_rate": 1.0, "diff_srv_rate": 0.0, "srv_diff_host_rate": 0.0,
                "dst_host_count": 1, "dst_host_srv_count": 1,
                "dst_host_same_srv_rate": 1.0, "dst_host_diff_srv_rate": 0.0,
                "dst_host_same_src_port_rate": 1.0, "dst_host_serror_rate": 0.0,
                "dst_host_srv_serror_rate": 0.0, "dst_host_rerror_rate": 0.0,
                "dst_host_srv_rerror_rate": 0.0,
            },
        },
        "buffer_overflow_u2r": {
            "name": "Buffer Overflow (U2R)",
            "description": "User-to-root privilege escalation via buffer overflow on a local service.",
            "badge": "badge-u2r",
            "badge_text": "U2R",
            "expected": "Attack",
            "features": {
                "protocol_type": "tcp", "service": "telnet", "flag": "SF",
                "src_bytes": 4548, "dst_bytes": 2376, "wrong_fragment": 0,
                "hot": 3, "num_failed_logins": 0, "logged_in": 1,
                "num_compromised": 2, "num_file_creations": 1, "is_guest_login": 0,
                "count": 1, "srv_count": 1, "serror_rate": 0.0, "rerror_rate": 0.0,
                "same_srv_rate": 1.0, "diff_srv_rate": 0.0, "srv_diff_host_rate": 0.0,
                "dst_host_count": 10, "dst_host_srv_count": 10,
                "dst_host_same_srv_rate": 1.0, "dst_host_diff_srv_rate": 0.0,
                "dst_host_same_src_port_rate": 1.0, "dst_host_serror_rate": 0.0,
                "dst_host_srv_serror_rate": 0.0, "dst_host_rerror_rate": 0.0,
                "dst_host_srv_rerror_rate": 0.0,
            },
        },
    },
    "KDDCup99": {
        "normal_smtp": {
            "name": "Normal Email (SMTP)",
            "description": "Standard SMTP email delivery traffic between mail servers.",
            "badge": "badge-normal",
            "badge_text": "Normal",
            "expected": "Normal",
            "features": {
                "duration": 1, "protocol_type": "tcp", "service": "smtp", "flag": "SF",
                "src_bytes": 1032, "dst_bytes": 330, "wrong_fragment": 0,
                "hot": 0, "num_failed_logins": 0, "logged_in": 1,
                "num_compromised": 0, "num_file_creations": 0, "is_guest_login": 0,
                "count": 3, "srv_count": 3, "serror_rate": 0.0, "rerror_rate": 0.0,
                "same_srv_rate": 1.0, "diff_srv_rate": 0.0,
            },
        },
        "smurf_dos": {
            "name": "Smurf Attack (DoS)",
            "description": "ICMP broadcast amplification attack flooding the target with echo replies.",
            "badge": "badge-dos",
            "badge_text": "DoS",
            "expected": "Attack",
            "features": {
                "duration": 0, "protocol_type": "icmp", "service": "ecr_i", "flag": "SF",
                "src_bytes": 1032, "dst_bytes": 0, "wrong_fragment": 0,
                "hot": 0, "num_failed_logins": 0, "logged_in": 0,
                "num_compromised": 0, "num_file_creations": 0, "is_guest_login": 0,
                "count": 511, "srv_count": 511, "serror_rate": 0.0, "rerror_rate": 0.0,
                "same_srv_rate": 1.0, "diff_srv_rate": 0.0,
            },
        },
        "satan_probe": {
            "name": "SATAN Scan (Probe)",
            "description": "SATAN vulnerability scanner probing for known service weaknesses.",
            "badge": "badge-probe",
            "badge_text": "Probe",
            "expected": "Attack",
            "features": {
                "duration": 0, "protocol_type": "tcp", "service": "private", "flag": "S0",
                "src_bytes": 0, "dst_bytes": 0, "wrong_fragment": 0,
                "hot": 0, "num_failed_logins": 0, "logged_in": 0,
                "num_compromised": 0, "num_file_creations": 0, "is_guest_login": 0,
                "count": 166, "srv_count": 9, "serror_rate": 0.95, "rerror_rate": 0.0,
                "same_srv_rate": 0.05, "diff_srv_rate": 0.08, 
            },
        },
    },
    "Kaggle_NID": {
        "normal_http": {
            "name": "Normal HTTP Request",
            "description": "Legitimate web request with typical connection parameters.",
            "badge": "badge-normal",
            "badge_text": "Normal",
            "expected": "Normal",
            "features": {
                "duration": 0, "protocol_type": "tcp", "service": "http", "flag": "SF",
                "src_bytes": 267, "dst_bytes": 14515, "wrong_fragment": 0,
                "hot": 0, "num_failed_logins": 0, "logged_in": 1,
                "num_compromised": 0, "num_file_creations": 0, "is_guest_login": 0,
                "count": 15, "srv_count": 15, "serror_rate": 0.0, "rerror_rate": 0.0,
                "same_srv_rate": 1.0, "diff_srv_rate": 0.0,
            },
        },
        "land_attack": {
            "name": "Land Attack (DoS)",
            "description": "Attack where source and destination IP/port are the same, causing a loop.",
            "badge": "badge-dos",
            "badge_text": "DoS",
            "expected": "Attack",
            "features": {
                "duration": 0, "protocol_type": "tcp", "service": "http", "flag": "S0",
                "src_bytes": 0, "dst_bytes": 0, "wrong_fragment": 0,
                "hot": 0, "num_failed_logins": 0, "logged_in": 0,
                "num_compromised": 0, "num_file_creations": 0, "is_guest_login": 0,
                "count": 1, "srv_count": 1, "serror_rate": 1.0, "rerror_rate": 0.0,
                "same_srv_rate": 1.0, "diff_srv_rate": 0.0,
            },
        },
    },
    "DS2OS": {
        "normal_sensor_read": {
            "name": "Normal Sensor Reading",
            "description": "A legitimate temperature sensor writing its reading in the smart home.",
            "badge": "badge-normal",
            "badge_text": "Normal",
            "expected": "Normal",
            "features": {
                "sourceType": "/sensorService", "sourceLocation": "Kitchen",
                "destinationServiceType": "/sensorService",
                "accessedNodeType": "/sensorService", "operation": "write",
                "value_numeric": 22.5, "value_is_numeric": 1,
                "hour": 14, "minute": 30, "same_location": 1,
                "same_address": 1, "src_accesses_self": 1,
                "src_operation_freq": 0.15,
            },
        },
        "dos_attack_iot": {
            "name": "DoS Attack on IoT Hub",
            "description": "A denial-of-service attack flooding the smart home hub with malicious register requests.",
            "badge": "badge-dos",
            "badge_text": "DoS",
            "expected": "Attack",
            "features": {
                "sourceType": "/smartPhone", "sourceLocation": "room_1",
                "destinationServiceType": "/lightControler",
                "accessedNodeType": "/basic/text", "operation": "write",
                "value_numeric": 0.0, "value_is_numeric": 0,
                "hour": 3, "minute": 15, "same_location": 0,
                "same_address": 0, "src_accesses_self": 0,
                "src_operation_freq": 0.001,
            },
        },
        "malicious_control": {
            "name": "Malicious Device Control",
            "description": "Unauthorized command sent to a door lock from an unusual source at an odd hour.",
            "badge": "badge-iot",
            "badge_text": "Malicious Control",
            "expected": "Attack",
            "features": {
                "sourceType": "/smartPhone", "sourceLocation": "room_5",
                "destinationServiceType": "/doorLockService",
                "accessedNodeType": "/doorLockService", "operation": "write",
                "value_numeric": 1.0, "value_is_numeric": 1,
                "hour": 2, "minute": 45, "same_location": 0,
                "same_address": 0, "src_accesses_self": 0,
                "src_operation_freq": 0.0005,
            },
        },
        "spying_attack": {
            "name": "Spying / Data Exfiltration",
            "description": "Unauthorized read operations targeting sensor data across multiple rooms.",
            "badge": "badge-scan",
            "badge_text": "Spying",
            "expected": "Attack",
            "features": {
                "sourceType": "/smartPhone", "sourceLocation": "room_3",
                "destinationServiceType": "/sensorService",
                "accessedNodeType": "/basic/number", "operation": "read",
                "value_numeric": 0.0, "value_is_numeric": 0,
                "hour": 1, "minute": 10, "same_location": 0,
                "same_address": 0, "src_accesses_self": 0,
                "src_operation_freq": 0.0003,
            },
        },
    },
    "CIC_DDoS2019": {
        "benign_flow": {
            "name": "Benign Network Flow",
            "description": "Normal traffic flow with typical packet sizes and timing.",
            "badge": "badge-normal",
            "badge_text": "Normal",
            "expected": "Normal",
        },
        "ddos_syn": {
            "name": "DDoS SYN Flood",
            "description": "Distributed denial-of-service using SYN packet flooding from multiple sources.",
            "badge": "badge-ddos",
            "badge_text": "DDoS",
            "expected": "Attack",
        },
    },
    "CIDDS_001": {
        "normal_tcp_flow": {
            "name": "Normal TCP Flow",
            "description": "Standard TCP session with expected packet count and byte volume.",
            "badge": "badge-normal",
            "badge_text": "Normal",
            "expected": "Normal",
            "features": {
                "Duration": 0.5, "Proto": "TCP  ", "Src Pt": 49152,
                "Dst Pt": 80, "Packets": 12, "Bytes": 8456, "Flags": ".AP.S.",
            },
        },
        "port_scan": {
            "name": "Port Scan Attack",
            "description": "Rapid sequential connections to multiple ports with minimal data transfer.",
            "badge": "badge-probe",
            "badge_text": "Scan",
            "expected": "Attack",
            "features": {
                "Duration": 0.0, "Proto": "TCP  ", "Src Pt": 44321,
                "Dst Pt": 22, "Packets": 1, "Bytes": 40, "Flags": "....S.",
            },
        },
        "brute_force_ssh": {
            "name": "SSH Brute Force",
            "description": "Multiple rapid SSH login attempts indicating a credential brute force attack.",
            "badge": "badge-r2l",
            "badge_text": "Brute Force",
            "expected": "Attack",
            "features": {
                "Duration": 2.0, "Proto": "TCP  ", "Src Pt": 51234,
                "Dst Pt": 22, "Packets": 50, "Bytes": 3500, "Flags": ".AP.SF",
            },
        },
    },
    "LUFlow": {
        "normal_flow": {
            "name": "Normal Network Flow",
            "description": "Benign flow with balanced packet counts and normal entropy.",
            "badge": "badge-normal",
            "badge_text": "Normal",
            "expected": "Normal",
            "features": {
                "avg_ipt": 0.05, "bytes_in": 1500, "bytes_out": 3200,
                "dest_port": 443, "entropy": 4.5, "num_pkts_out": 10,
                "num_pkts_in": 8, "proto": 6, "src_port": 52341,
                "total_entropy": 36.0, "duration": 1.2,
            },
        },
        "malicious_flow": {
            "name": "Malicious C2 Beacon",
            "description": "Command-and-control communication with periodic low-volume suspicious traffic.",
            "badge": "badge-r2l",
            "badge_text": "C2 Beacon",
            "expected": "Attack",
            "features": {
                "avg_ipt": 30.0, "bytes_in": 120, "bytes_out": 80,
                "dest_port": 8443, "entropy": 7.8, "num_pkts_out": 2,
                "num_pkts_in": 2, "proto": 6, "src_port": 61234,
                "total_entropy": 15.6, "duration": 60.0,
            },
        },
    },
    "NetworkLogs": {
        "normal_https": {
            "name": "Normal HTTPS Request",
            "description": "Standard HTTPS web request from a regular browser.",
            "badge": "badge-normal",
            "badge_text": "Normal",
            "expected": "Normal",
            "features": {
                "Port": 443, "Request_Type": "HTTPS", "Protocol": "TCP",
                "Payload_Size": 1200, "User_Agent": "Mozilla/5.0",
                "Status": "Success", "Scan_Type": "Normal",
            },
        },
        "nmap_scan": {
            "name": "Nmap Port Scan",
            "description": "Aggressive network reconnaissance using nmap scanner targeting multiple ports.",
            "badge": "badge-probe",
            "badge_text": "Port Scan",
            "expected": "Attack",
            "features": {
                "Port": 22, "Request_Type": "SSH", "Protocol": "TCP",
                "Payload_Size": 60, "User_Agent": "nmap/7.80",
                "Status": "Failure", "Scan_Type": "PortScan",
            },
        },
        "bot_attack": {
            "name": "Bot Attack (Automated)",
            "description": "Automated bot sending rapid requests with scripted user-agent strings.",
            "badge": "badge-dos",
            "badge_text": "Bot Attack",
            "expected": "Attack",
            "features": {
                "Port": 80, "Request_Type": "HTTP", "Protocol": "TCP",
                "Payload_Size": 50, "User_Agent": "python-requests/2.25.1",
                "Status": "Failure", "Scan_Type": "BotAttack",
            },
        },
        "nikto_vuln_scan": {
            "name": "Nikto Vulnerability Scan",
            "description": "Web vulnerability scanner probing for known exploits and misconfigurations.",
            "badge": "badge-scan",
            "badge_text": "Vuln Scan",
            "expected": "Attack",
            "features": {
                "Port": 80, "Request_Type": "HTTP", "Protocol": "TCP",
                "Payload_Size": 90, "User_Agent": "Nikto/2.1.6",
                "Status": "Failure", "Scan_Type": "PortScan",
            },
        },
    },
}


# ---------------------------------------------------------------------------
# Prediction engine
# ---------------------------------------------------------------------------
def prepare_input(features_dict, meta):
    """Convert user input dict to model-ready numpy array."""
    feature_names = meta["feature_names"]
    scaler = meta.get("scaler")
    encoders = meta.get("encoders", {})

    row = {}
    for fname in feature_names:
        val = features_dict.get(fname, 0)
        if fname in encoders:
            enc = encoders[fname]
            str_val = str(val)
            if str_val in list(enc.classes_):
                val = enc.transform([str_val])[0]
            else:
                val = 0
        else:
            try:
                val = float(val)
            except (ValueError, TypeError):
                val = 0
        row[fname] = val

    df = pd.DataFrame([row], columns=feature_names)
    if scaler is not None:
        df = pd.DataFrame(scaler.transform(df), columns=feature_names)
    return df.values


def predict_single(model, meta, features_dict):
    """Run prediction on a single sample."""
    X = prepare_input(features_dict, meta)
    pred = model.predict(X)[0]
    proba = None
    if hasattr(model, "predict_proba"):
        try:
            proba = model.predict_proba(X)[0]
        except Exception:
            pass

    threshold = 0.5
    thresholds = meta.get("optimal_thresholds", {})
    if thresholds:
        threshold = list(thresholds.values())[0] if thresholds else 0.5

    label = "Attack" if pred == 1 else "Normal"
    confidence = None
    if proba is not None:
        if pred == 1:
            confidence = proba[1]
        else:
            confidence = proba[0]

    return {
        "prediction": label,
        "pred_int": int(pred),
        "confidence": float(confidence) if confidence is not None else None,
        "proba_normal": float(proba[0]) if proba is not None else None,
        "proba_attack": float(proba[1]) if proba is not None else None,
        "threshold": threshold,
    }


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def render_header():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
                padding: 24px; border-radius: 16px; margin-bottom: 20px;
                border: 1px solid #334155;">
        <h1 style="color: #3b82f6; margin: 0; font-size: 1.8rem;">
            \u26a1 IDS Model Testing Console</h1>
        <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.95rem;">
            Test trained intrusion detection models with pre-built attack scenarios or custom inputs.
            All 8 datasets supported. Mobile-friendly.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_confidence_gauge(result):
    """Render a Plotly gauge showing prediction confidence."""
    is_attack = result["pred_int"] == 1
    attack_prob = result.get("proba_attack", 0.5 if is_attack else 0.0)
    if attack_prob is None:
        attack_prob = 1.0 if is_attack else 0.0

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=attack_prob * 100,
        number={"suffix": "%", "font": {"size": 36, "color": "white"}},
        title={"text": "Attack Probability", "font": {"size": 16, "color": "#94a3b8"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#475569",
                     "tickfont": {"color": "#94a3b8"}},
            "bar": {"color": "#ef4444" if attack_prob > 0.5 else "#22c55e"},
            "bgcolor": "#1e293b",
            "borderwidth": 2,
            "bordercolor": "#334155",
            "steps": [
                {"range": [0, 30], "color": "#064e3b"},
                {"range": [30, 70], "color": "#78350f"},
                {"range": [70, 100], "color": "#7f1d1d"},
            ],
            "threshold": {
                "line": {"color": "#f59e0b", "width": 3},
                "thickness": 0.8,
                "value": result.get("threshold", 0.5) * 100,
            },
        },
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )
    return fig


def render_result(result, expected=None):
    """Render the prediction result panel."""
    is_attack = result["pred_int"] == 1
    css_class = "result-attack" if is_attack else "result-safe"
    icon = "\u26a0\ufe0f" if is_attack else "\u2705"
    label = result["prediction"]

    correct = None
    if expected:
        correct = (expected == "Attack" and is_attack) or (expected == "Normal" and not is_attack)

    verdict_color = "#ef4444" if is_attack else "#22c55e"

    st.markdown(f"""
    <div class="{css_class}">
        <h2 style="color: white; margin: 0; font-size: 2rem;">{icon} {label}</h2>
        <p style="color: #d1d5db; margin: 8px 0 0 0; font-size: 1.1rem;">
            The model classifies this traffic as <strong style="color: {verdict_color};">{label}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    if correct is not None:
        if correct:
            st.success(f"Correct! Expected: {expected}, Got: {label}")
        else:
            st.error(f"Mismatch! Expected: {expected}, Got: {label}")


# ---------------------------------------------------------------------------
# Main pages
# ---------------------------------------------------------------------------
def page_scenario_testing():
    """Pre-built scenario testing page."""
    st.markdown("## Pre-Built Attack Scenarios")
    st.markdown("Select a dataset and run curated attack/normal scenarios to verify model accuracy.")

    datasets = get_available_datasets()
    if not datasets:
        st.error("No trained models found. Run `python3 -m src.train_pipeline` first.")
        return

    # Dataset filter - limit to those with scenarios
    scenario_datasets = [d for d in datasets if d in SCENARIOS]
    selected_ds = st.selectbox("Select Dataset", scenario_datasets,
                               format_func=lambda x: f"{x} ({len(SCENARIOS.get(x, {}))} scenarios)")

    if selected_ds not in SCENARIOS:
        st.info("No pre-built scenarios for this dataset. Use Custom Testing.")
        return

    model_choice = st.radio("Model", ["Best Model", "Stacking Ensemble"], horizontal=True)
    model_type = "best" if model_choice == "Best Model" else "ensemble"
    model, meta = load_model_and_meta(selected_ds, model_type)

    if model is None:
        st.error(f"Could not load {model_choice} for {selected_ds}")
        return

    st.markdown("---")

    scenarios = SCENARIOS[selected_ds]

    # Run All button
    if st.button("Run All Scenarios", type="primary", use_container_width=True):
        results_summary = []
        progress = st.progress(0)
        for i, (key, scenario) in enumerate(scenarios.items()):
            if "features" not in scenario:
                continue
            result = predict_single(model, meta, scenario["features"])
            correct = (scenario["expected"] == result["prediction"])
            results_summary.append({
                "Scenario": scenario["name"],
                "Expected": scenario["expected"],
                "Predicted": result["prediction"],
                "Confidence": f"{(result['confidence'] or 0) * 100:.1f}%",
                "Correct": "\u2705" if correct else "\u274c",
            })
            progress.progress((i + 1) / len(scenarios))

        if results_summary:
            st.markdown("### Results Summary")
            df = pd.DataFrame(results_summary)
            st.dataframe(df, use_container_width=True, hide_index=True)
            n_correct = sum(1 for r in results_summary if r["Correct"] == "\u2705")
            st.metric("Accuracy", f"{n_correct}/{len(results_summary)} correct")

    st.markdown("---")

    # Individual scenario cards
    for key, scenario in scenarios.items():
        if "features" not in scenario:
            continue

        badge = scenario.get("badge", "badge-normal")
        badge_text = scenario.get("badge_text", "")

        with st.expander(f"{scenario['name']}  \u2014  _{scenario['description']}_"):
            st.markdown(f'<span class="attack-badge {badge}">{badge_text}</span> &nbsp; '
                        f'**Expected:** {scenario["expected"]}',
                        unsafe_allow_html=True)

            # Show features
            with st.container():
                feat_cols = st.columns(3)
                for i, (fname, fval) in enumerate(scenario["features"].items()):
                    with feat_cols[i % 3]:
                        st.text(f"{fname}: {fval}")

            if st.button(f"Run \u25b6", key=f"run_{selected_ds}_{key}", use_container_width=True):
                with st.spinner("Analyzing traffic..."):
                    time.sleep(0.3)
                    result = predict_single(model, meta, scenario["features"])

                col1, col2 = st.columns([1, 1])
                with col1:
                    render_result(result, expected=scenario["expected"])
                with col2:
                    fig = render_confidence_gauge(result)
                    st.plotly_chart(fig, use_container_width=True)

                # Probability breakdown
                if result["proba_normal"] is not None:
                    st.markdown("**Probability Breakdown:**")
                    prob_cols = st.columns(2)
                    with prob_cols[0]:
                        st.metric("Normal", f"{result['proba_normal']*100:.2f}%")
                    with prob_cols[1]:
                        st.metric("Attack", f"{result['proba_attack']*100:.2f}%")


def page_custom_testing():
    """Custom feature input testing page."""
    st.markdown("## Custom Traffic Testing")
    st.markdown("Manually enter feature values to test the model on custom network traffic.")

    datasets = get_available_datasets()
    if not datasets:
        st.error("No trained models found.")
        return

    selected_ds = st.selectbox("Select Dataset", datasets, key="custom_ds")
    model_choice = st.radio("Model", ["Best Model", "Stacking Ensemble"],
                            horizontal=True, key="custom_model")
    model_type = "best" if model_choice == "Best Model" else "ensemble"
    model, meta = load_model_and_meta(selected_ds, model_type)

    if model is None:
        st.error(f"Could not load model for {selected_ds}")
        return

    feature_names = meta["feature_names"]
    encoders = meta.get("encoders", {})

    st.markdown(f"**{selected_ds}** requires **{len(feature_names)}** features:")

    # Build input form
    features_input = {}
    cols = st.columns(min(3, len(feature_names)))

    for i, fname in enumerate(feature_names):
        with cols[i % len(cols)]:
            if fname in encoders:
                enc = encoders[fname]
                options = list(enc.classes_)
                features_input[fname] = st.selectbox(f"{fname}", options, key=f"custom_{fname}")
            else:
                features_input[fname] = st.number_input(
                    f"{fname}", value=0.0, format="%.4f", key=f"custom_{fname}"
                )

    if st.button("Analyze Traffic", type="primary", use_container_width=True):
        with st.spinner("Running inference..."):
            time.sleep(0.3)
            result = predict_single(model, meta, features_input)

        col1, col2 = st.columns([1, 1])
        with col1:
            render_result(result)
        with col2:
            fig = render_confidence_gauge(result)
            st.plotly_chart(fig, use_container_width=True)

        if result["proba_normal"] is not None:
            st.markdown("**Probability Breakdown:**")
            prob_cols = st.columns(2)
            with prob_cols[0]:
                st.metric("Normal", f"{result['proba_normal']*100:.2f}%")
            with prob_cols[1]:
                st.metric("Attack", f"{result['proba_attack']*100:.2f}%")


def page_batch_testing():
    """Batch CSV testing page."""
    st.markdown("## Batch Testing (CSV Upload)")
    st.markdown("Upload a CSV file with feature columns to classify multiple traffic samples at once.")

    datasets = get_available_datasets()
    if not datasets:
        st.error("No trained models found.")
        return

    selected_ds = st.selectbox("Select Dataset", datasets, key="batch_ds")
    model, meta = load_model_and_meta(selected_ds, "best")

    if model is None:
        st.error(f"Could not load model for {selected_ds}")
        return

    feature_names = meta["feature_names"]
    st.info(f"Expected columns: {', '.join(feature_names)}")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        st.write(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        st.dataframe(df.head(), use_container_width=True)

        if st.button("Classify All Rows", type="primary", use_container_width=True):
            results = []
            progress = st.progress(0)
            for idx in range(len(df)):
                row_dict = df.iloc[idx].to_dict()
                result = predict_single(model, meta, row_dict)
                results.append({
                    "Row": idx,
                    "Prediction": result["prediction"],
                    "Attack_Prob": f"{(result['proba_attack'] or 0)*100:.1f}%",
                })
                progress.progress((idx + 1) / len(df))

            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True, hide_index=True)

            n_attacks = sum(1 for r in results if r["Prediction"] == "Attack")
            n_normal = len(results) - n_attacks
            st.markdown(f"**Summary:** {n_normal} Normal, {n_attacks} Attack out of {len(results)} total")


def page_model_info():
    """Model information and performance page."""
    st.markdown("## Model Information")

    datasets = get_available_datasets()
    if not datasets:
        st.error("No trained models found.")
        return

    summary_path = REPORTS_DIR / "summary_table.csv"
    if summary_path.exists():
        summary_df = pd.read_csv(summary_path)
        st.markdown("### Performance Summary (All Datasets)")
        st.dataframe(
            summary_df.style.background_gradient(
                cmap="RdYlGn", vmin=0.8, vmax=1.0,
                subset=["Accuracy", "Precision", "Recall", "F1"]
            ),
            use_container_width=True, hide_index=True,
        )

    selected_ds = st.selectbox("Inspect Dataset", datasets, key="info_ds")
    _, meta = load_model_and_meta(selected_ds, "best")
    if meta:
        st.markdown(f"**Features ({len(meta['feature_names'])}):** `{', '.join(meta['feature_names'])}`")
        if meta.get("encoders"):
            st.markdown("**Categorical Encoders:**")
            for name, enc in meta["encoders"].items():
                st.text(f"  {name}: {list(enc.classes_)}")
        if meta.get("optimal_thresholds"):
            st.markdown(f"**Optimal Thresholds:** {meta['optimal_thresholds']}")

    # Show confusion matrix and ROC if available
    col1, col2 = st.columns(2)
    cm_path = FIGURES_DIR / f"cm_{selected_ds}_StackingEnsemble.png"
    roc_path = FIGURES_DIR / f"roc_{selected_ds}.png"
    if cm_path.exists():
        with col1:
            st.image(str(cm_path), caption="Confusion Matrix (Ensemble)")
    if roc_path.exists():
        with col2:
            st.image(str(roc_path), caption="ROC Curves")


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
def main():
    render_header()

    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "Select",
            ["Scenario Testing", "Custom Testing",
             "Batch Testing", "Model Info"],
            index=0,
        )

        st.markdown("---")
        st.markdown("### Quick Stats")
        datasets = get_available_datasets()
        st.info(f"Datasets: {len(datasets)}")
        model_files = list(MODELS_DIR.glob("*_best_*.joblib"))
        st.info(f"Trained Models: {len(model_files)}")

        st.markdown("---")
        st.markdown(
            "<p style='color: #64748b; font-size: 12px;'>"
            "ML-Based IDS for Tactical Military Networks</p>",
            unsafe_allow_html=True,
        )

    if page == "Scenario Testing":
        page_scenario_testing()
    elif page == "Custom Testing":
        page_custom_testing()
    elif page == "Batch Testing":
        page_batch_testing()
    elif page == "Model Info":
        page_model_info()


if __name__ == "__main__":
    main()
