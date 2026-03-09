"""
Dataset-specific loading and preprocessing for all 8 benchmark intrusion datasets.

Each ``load_*`` function handles the unique file formats, column layouts, and
label taxonomies of its dataset, producing a unified DataFrame with:
  - Numeric feature columns (categorical columns label-encoded)
  - A binary ``label`` column (0 = Normal, 1 = Attack)

Supported datasets and their loaders:
    NSL_KDD / KDDCup99 / Kaggle_NID  — load_kdd_family()
    CIC_DDoS2019                      — load_cic_ddos()
    CIDDS_001                         — load_cidds()
    DS2OS                             — load_ds2os()  (IoT, rich feature engineering)
    LUFlow                            — load_luflow()
    NetworkLogs                       — load_network_logs()

Utility helpers:
    _encode_categoricals(df)  — Label-encode string columns
    _safe_numeric(df)         — Coerce all columns to numeric, fill NaN with 0
    _sample_if_needed(df, n)  — Stratified down-sample if row count exceeds n
    load_dataset(name)        — Dispatcher that routes to the correct loader
"""
import os
import glob
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm

from src.config import DATASET_PATHS, MAX_SAMPLE_SIZE, RANDOM_STATE


def _safe_numeric(df, exclude_cols=None):
    """Convert all columns except excluded ones to numeric where possible."""
    exclude_cols = exclude_cols or []
    for col in df.columns:
        if col not in exclude_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _sample_if_needed(df, max_rows=MAX_SAMPLE_SIZE):
    """Downsample large datasets while preserving class distribution."""
    if len(df) > max_rows:
        df = df.groupby("label", group_keys=False).apply(
            lambda x: x.sample(
                n=min(len(x), int(max_rows * len(x) / len(df))),
                random_state=RANDOM_STATE,
            )
        )
    return df.reset_index(drop=True)


def _encode_categoricals(df, categorical_cols):
    """Label-encode categorical columns and return the dataframe and encoders."""
    encoders = {}
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = df[col].astype(str).fillna("unknown")
            df[col] = le.fit_transform(df[col])
            encoders[col] = le
    return df, encoders


# --------------------------------------------------------------------------
# NSL-KDD / KDDCup99 / Kaggle Network Intrusion (same schema)
# --------------------------------------------------------------------------
KDD_COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root",
    "num_file_creations", "num_shells", "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count", "serror_rate",
    "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate",
    "diff_srv_rate", "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate", "dst_host_srv_serror_rate", "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate", "class",
]

KDD_CATEGORICAL = ["protocol_type", "service", "flag"]

# Attack type mapping for KDD-family datasets
KDD_ATTACK_MAP = {
    "normal": 0, "normal.": 0,
    # DoS
    "back": 1, "back.": 1, "land": 1, "land.": 1, "neptune": 1, "neptune.": 1,
    "pod": 1, "pod.": 1, "smurf": 1, "smurf.": 1, "teardrop": 1, "teardrop.": 1,
    "apache2": 1, "udpstorm": 1, "processtable": 1, "mailbomb": 1,
    # Probe
    "satan": 1, "satan.": 1, "ipsweep": 1, "ipsweep.": 1, "nmap": 1, "nmap.": 1,
    "portsweep": 1, "portsweep.": 1, "mscan": 1, "saint": 1,
    # R2L
    "guess_passwd": 1, "guess_passwd.": 1, "ftp_write": 1, "ftp_write.": 1,
    "imap": 1, "imap.": 1, "phf": 1, "phf.": 1, "multihop": 1, "multihop.": 1,
    "warezmaster": 1, "warezmaster.": 1, "warezclient": 1, "warezclient.": 1,
    "spy": 1, "spy.": 1, "xlock": 1, "xsnoop": 1, "snmpguess": 1,
    "snmpgetattack": 1, "httptunnel": 1, "sendmail": 1, "named": 1,
    "worm": 1,
    # U2R
    "buffer_overflow": 1, "buffer_overflow.": 1, "loadmodule": 1, "loadmodule.": 1,
    "rootkit": 1, "rootkit.": 1, "perl": 1, "perl.": 1, "sqlattack": 1,
    "xterm": 1, "ps": 1,
}


def _detect_kdd_shift(df):
    """
    Detect if KDD-family CSV has shifted columns.
    If the 'duration' column (first col) contains non-numeric strings like 'tcp',
    the data is shifted: no duration col, extra difficulty col at end.
    """
    first_col = df.columns[0]
    sample_vals = df[first_col].head(20).astype(str).str.strip().str.lower()
    non_numeric = sample_vals.apply(lambda x: not x.replace('.', '', 1).replace('-', '', 1).isdigit())
    return non_numeric.mean() > 0.5  # Most values are non-numeric


def load_kdd_family(dataset_name):
    """Load NSL_KDD, KDDCup99, or Kaggle_NID dataset."""
    path = DATASET_PATHS[dataset_name]
    train_files = sorted(glob.glob(str(path / "fold_*_train.csv")))
    test_files = sorted(glob.glob(str(path / "fold_*_test.csv")))

    if not train_files:
        raise FileNotFoundError(f"No train files found in {path}")

    # Use fold_1 for efficiency
    df_train = pd.read_csv(train_files[0], low_memory=False)
    df_test = pd.read_csv(test_files[0], low_memory=False) if test_files else None

    # Detect column shift: some KDD datasets (e.g. NSL-KDD) have no duration
    # column but have an extra difficulty column at the end, causing misalignment
    # with the header.
    shifted = _detect_kdd_shift(df_train)

    if shifted:
        print(f"  [INFO] Detected shifted columns in {dataset_name}, reassigning...")
        # The actual column order is: protocol_type, service, flag, src_bytes, ...
        # ..., dst_host_srv_rerror_rate, class_label, difficulty
        # (no duration column, extra difficulty column at end)
        KDD_SHIFTED = KDD_COLUMNS[1:]  # Remove 'duration' from front
        KDD_SHIFTED.append("difficulty")  # Add difficulty at end
        # KDD_SHIFTED now has: protocol_type...dst_host_srv_rerror_rate, class, difficulty = 42 cols
        if len(df_train.columns) == len(KDD_SHIFTED):
            df_train.columns = KDD_SHIFTED
            if df_test is not None:
                df_test.columns = KDD_SHIFTED
        else:
            print(f"  [WARN] Column count mismatch: expected {len(KDD_SHIFTED)}, got {len(df_train.columns)}")
    else:
        # Fix column names if header is missing or malformed
        if "class" not in df_train.columns and len(df_train.columns) >= 41:
            if len(df_train.columns) == 43:
                df_train.columns = KDD_COLUMNS + ["difficulty"]
                if df_test is not None:
                    df_test.columns = KDD_COLUMNS + ["difficulty"]
            elif len(df_train.columns) == 42:
                # Could be standard 41 features + class, or with difficulty
                # Check if last column looks like difficulty (numeric small integers)
                last_col_vals = pd.to_numeric(df_train.iloc[:, -1], errors="coerce")
                second_last_vals = df_train.iloc[:, -2].astype(str).str.strip().str.lower()
                has_labels = any(v in KDD_ATTACK_MAP for v in second_last_vals.head(20))
                if has_labels:
                    # second-to-last is the real label, last is difficulty
                    df_train.columns = KDD_COLUMNS + ["difficulty"]
                    if df_test is not None:
                        df_test.columns = KDD_COLUMNS + ["difficulty"]
            elif len(df_train.columns) == 41:
                df_train.columns = KDD_COLUMNS
                if df_test is not None:
                    df_test.columns = KDD_COLUMNS

    df = pd.concat([df_train, df_test], ignore_index=True) if df_test is not None else df_train

    # Identify the label column
    label_col = "class"
    if label_col not in df.columns:
        # Try to find it by looking for columns containing known attack names
        for candidate in df.columns:
            uniques = df[candidate].dropna().astype(str).str.strip().str.lower().unique()[:30]
            if any(v in KDD_ATTACK_MAP for v in uniques):
                label_col = candidate
                break

    # Map to binary label
    df["label"] = df[label_col].astype(str).str.strip().str.lower().map(KDD_ATTACK_MAP)
    # For any unmapped attacks, mark as attack (1)
    df["label"] = df["label"].fillna(1).astype(int)

    # Drop original label and difficulty columns
    drop_cols = [label_col]
    if "difficulty" in df.columns:
        drop_cols.append("difficulty")
    df = df.drop(columns=drop_cols, errors="ignore")

    # Encode categoricals
    cat_cols = [c for c in KDD_CATEGORICAL if c in df.columns]
    df, encoders = _encode_categoricals(df, cat_cols)

    # Convert remaining to numeric
    df = _safe_numeric(df, exclude_cols=["label"])
    df = df.fillna(0)
    df = _sample_if_needed(df)

    return df, encoders


# --------------------------------------------------------------------------
# CIC-DDoS2019
# --------------------------------------------------------------------------
def load_cic_ddos2019():
    """Load CIC-DDoS2019 dataset."""
    path = DATASET_PATHS["CIC_DDoS2019"]
    train_files = sorted(glob.glob(str(path / "fold_*_train.csv")))

    if not train_files:
        raise FileNotFoundError(f"No train files in {path}")

    df = pd.read_csv(train_files[0], low_memory=False)

    # The CIC-DDoS dataset may not have proper headers - detect
    # If first row looks numeric and there are ~80+ columns, it's the CIC flow format
    if len(df.columns) > 70:
        # Last column is typically the label
        label_col = df.columns[-1]
        # Check if label column contains attack names or binary labels
        sample_vals = df[label_col].dropna().astype(str).str.strip().str.lower().unique()[:10]

        if any("benign" in str(v) for v in sample_vals):
            df["label"] = df[label_col].astype(str).str.strip().str.lower().apply(
                lambda x: 0 if "benign" in x else 1
            )
        else:
            # Assume numeric: 0 = normal, anything else = attack
            df["label"] = pd.to_numeric(df[label_col], errors="coerce").fillna(1)
            df["label"] = (df["label"] != 0).astype(int)

        df = df.drop(columns=[label_col], errors="ignore")
    else:
        # Fallback: last column is label
        label_col = df.columns[-1]
        df["label"] = pd.to_numeric(df[label_col], errors="coerce").fillna(1)
        df["label"] = (df["label"] != 0).astype(int)
        df = df.drop(columns=[label_col], errors="ignore")

    # Remove infinite values and NaNs
    df = df.replace([np.inf, -np.inf], np.nan)
    df = _safe_numeric(df, exclude_cols=["label"])
    df = df.fillna(0)
    df = _sample_if_needed(df)

    return df, {}


# --------------------------------------------------------------------------
# CIDDS-001
# --------------------------------------------------------------------------
def load_cidds001():
    """Load CIDDS-001 flow-based dataset."""
    path = DATASET_PATHS["CIDDS_001"]
    train_files = sorted(glob.glob(str(path / "fold_*_train.csv")))

    if not train_files:
        raise FileNotFoundError(f"No train files in {path}")

    # CIDDS-001 is very large (~3GB per fold), read only a chunk
    df = pd.read_csv(train_files[0], nrows=MAX_SAMPLE_SIZE, low_memory=False)

    # Expected columns: Date first seen, Duration, Proto, Src IP Addr, Src Pt,
    # Dst IP Addr, Dst Pt, Packets, Bytes, Flows, Flags, Tos, class, attackType, attackID, attackDescription
    # Clean column names
    df.columns = df.columns.str.strip()

    label_col = "class"
    if label_col not in df.columns:
        for c in df.columns:
            if "class" in c.lower() or "label" in c.lower():
                label_col = c
                break

    # Binary label
    df["label"] = df[label_col].astype(str).str.strip().str.lower().apply(
        lambda x: 0 if x in ["normal", "0", "benign"] else 1
    )

    # Drop non-feature columns
    drop_cols = [label_col, "attackType", "attackID", "attackDescription",
                 "Date first seen", "Src IP Addr", "Dst IP Addr"]
    # Also drop columns that exist
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols, errors="ignore")

    # Encode categoricals
    cat_cols = [c for c in ["Proto", "Flags"] if c in df.columns]
    df, encoders = _encode_categoricals(df, cat_cols)

    # Parse numeric fields (Bytes may have M/K suffixes)
    for col in ["Bytes", "Packets", "Duration", "Flows", "Src Pt", "Dst Pt", "Tos"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            # Handle suffixes like "9.1 M"
            df[col] = df[col].str.replace(r'\s*M\s*$', 'e6', regex=True)
            df[col] = df[col].str.replace(r'\s*K\s*$', 'e3', regex=True)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = _safe_numeric(df, exclude_cols=["label"])
    df = df.fillna(0)
    df = _sample_if_needed(df)

    return df, encoders


# --------------------------------------------------------------------------
# DS2OS (IoT dataset)
# --------------------------------------------------------------------------
def load_ds2os():
    """Load DS2OS IoT traffic dataset with rich feature engineering."""
    path = DATASET_PATHS["DS2OS"]
    all_files = sorted(glob.glob(str(path / "fold_*.csv")))

    if not all_files:
        raise FileNotFoundError(f"No CSV files in {path}")

    # Load all folds to maximize attack samples for this imbalanced dataset
    dfs = []
    for f in all_files:
        dfs.append(pd.read_csv(f, low_memory=False))
    df = pd.concat(dfs, ignore_index=True).drop_duplicates()
    df.columns = df.columns.str.strip()

    # Label column is 'normality'
    label_col = "normality"
    if label_col not in df.columns:
        for c in df.columns:
            if "normal" in c.lower() or "label" in c.lower() or "class" in c.lower():
                label_col = c
                break

    df["label"] = df[label_col].astype(str).str.strip().str.lower().apply(
        lambda x: 0 if x == "normal" else 1
    )

    # --- Rich Feature Engineering for IoT Data ---

    # 1. Parse numeric value from 'value' column
    if "value" in df.columns:
        df["value_numeric"] = pd.to_numeric(df["value"], errors="coerce").fillna(0)
        df["value_is_none"] = (df["value"].astype(str).str.strip().str.lower() == "none").astype(int)
        df["value_is_numeric"] = pd.to_numeric(df["value"], errors="coerce").notna().astype(int)

    # 2. Temporal features from timestamp
    if "timestamp" in df.columns:
        ts = pd.to_numeric(df["timestamp"], errors="coerce")
        ts_sec = ts / 1000  # Convert ms to seconds
        df["hour"] = (ts_sec % 86400 / 3600).fillna(0).astype(int)
        df["minute"] = (ts_sec % 3600 / 60).fillna(0).astype(int)

    # 3. Interaction features
    cat_feature_cols = ["sourceType", "destinationServiceType", "accessedNodeType",
                        "operation", "sourceLocation", "destinationLocation"]
    # Source-destination type pair
    if "sourceType" in df.columns and "destinationServiceType" in df.columns:
        df["src_dst_type"] = df["sourceType"].astype(str) + "_" + df["destinationServiceType"].astype(str)
    if "sourceType" in df.columns and "operation" in df.columns:
        df["src_operation"] = df["sourceType"].astype(str) + "_" + df["operation"].astype(str)
    # Same location flag
    if "sourceLocation" in df.columns and "destinationLocation" in df.columns:
        df["same_location"] = (df["sourceLocation"] == df["destinationLocation"]).astype(int)
    # Same address flag
    if "sourceAddress" in df.columns and "destinationServiceAddress" in df.columns:
        df["same_address"] = (df["sourceAddress"] == df["destinationServiceAddress"]).astype(int)
    if "sourceAddress" in df.columns and "accessedNodeAddress" in df.columns:
        df["src_accesses_self"] = (df["sourceAddress"] == df["accessedNodeAddress"]).astype(int)

    # 4. Frequency encoding for high-cardinality categorical columns
    freq_cols = ["sourceID", "sourceAddress", "destinationServiceAddress",
                 "accessedNodeAddress", "sourceType", "destinationServiceType",
                 "accessedNodeType", "operation", "sourceLocation",
                 "destinationLocation", "src_dst_type", "src_operation"]
    for col in freq_cols:
        if col in df.columns:
            freq = df[col].value_counts(normalize=True)
            df[f"{col}_freq"] = df[col].map(freq).fillna(0)

    # 5. Drop original high-cardinality string columns, keep engineered features
    drop_cols = [label_col, "timestamp", "value",
                 "sourceID", "sourceAddress", "destinationServiceAddress",
                 "accessedNodeAddress", "src_dst_type", "src_operation"]
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols, errors="ignore")

    # 6. Encode remaining low-cardinality categoricals
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if "label" in cat_cols:
        cat_cols.remove("label")
    df, encoders = _encode_categoricals(df, cat_cols)

    df = _safe_numeric(df, exclude_cols=["label"])
    df = df.fillna(0)
    df = _sample_if_needed(df)

    return df, encoders


# --------------------------------------------------------------------------
# LUFlow (Lancaster University Flow dataset)
# --------------------------------------------------------------------------
def load_luflow():
    """Load LUFlow dataset from archive (2)."""
    path = DATASET_PATHS["LUFlow"]
    csv_files = sorted(glob.glob(str(path / "**/*.csv"), recursive=True))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files in {path}")

    dfs = []
    for f in csv_files:
        try:
            chunk = pd.read_csv(f, low_memory=False)
            dfs.append(chunk)
        except Exception:
            continue

    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()

    # Label column
    label_col = "label"
    if label_col not in df.columns:
        for c in df.columns:
            if "label" in c.lower():
                label_col = c
                break

    # Map: benign=0, outlier=1, malicious=1
    df["label"] = df[label_col].astype(str).str.strip().str.lower().apply(
        lambda x: 0 if x == "benign" else 1
    )
    if label_col != "label":
        df = df.drop(columns=[label_col], errors="ignore")

    # Drop IP and timestamp columns
    drop_cols = ["src_ip", "dest_ip", "time_start", "time_end"]
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols, errors="ignore")

    # Encode categoricals
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if "label" in cat_cols:
        cat_cols.remove("label")
    df, encoders = _encode_categoricals(df, cat_cols)

    df = _safe_numeric(df, exclude_cols=["label"])
    df = df.fillna(0)
    df = _sample_if_needed(df)

    return df, encoders


# --------------------------------------------------------------------------
# Network Logs (archive 5)
# --------------------------------------------------------------------------
def load_network_logs():
    """Load Network_logs and Time-Series_Network_logs datasets."""
    path = DATASET_PATHS["NetworkLogs"]

    dfs = []
    for fname in ["Network_logs.csv", "Time-Series_Network_logs.csv"]:
        fpath = path / fname
        if fpath.exists():
            chunk = pd.read_csv(fpath, low_memory=False)
            dfs.append(chunk)

    if not dfs:
        raise FileNotFoundError(f"No CSV files in {path}")

    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()

    # Label: 'Intrusion' column (0=normal, 1=attack)
    label_col = "Intrusion"
    if label_col not in df.columns:
        for c in df.columns:
            if "intrusion" in c.lower() or "label" in c.lower():
                label_col = c
                break

    df["label"] = pd.to_numeric(df[label_col], errors="coerce").fillna(0).astype(int)
    df["label"] = (df["label"] != 0).astype(int)

    # Drop non-feature columns
    drop_cols = [label_col, "Timestamp", "Source_IP", "Destination_IP"]
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols, errors="ignore")

    # Encode categoricals
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if "label" in cat_cols:
        cat_cols.remove("label")
    df, encoders = _encode_categoricals(df, cat_cols)

    df = _safe_numeric(df, exclude_cols=["label"])
    df = df.fillna(0)
    df = _sample_if_needed(df)

    return df, encoders


# --------------------------------------------------------------------------
# Master loader
# --------------------------------------------------------------------------
LOADERS = {
    "NSL_KDD": lambda: load_kdd_family("NSL_KDD"),
    "KDDCup99": lambda: load_kdd_family("KDDCup99"),
    "Kaggle_NID": lambda: load_kdd_family("Kaggle_NID"),
    "CIC_DDoS2019": load_cic_ddos2019,
    "CIDDS_001": load_cidds001,
    "DS2OS": load_ds2os,
    "LUFlow": load_luflow,
    "NetworkLogs": load_network_logs,
}


def load_dataset(name):
    """
    Load and preprocess a dataset by name.
    Returns (DataFrame with 'label' column, encoders_dict).
    """
    if name not in LOADERS:
        raise ValueError(f"Unknown dataset: {name}. Available: {list(LOADERS.keys())}")

    print(f"[INFO] Loading dataset: {name} ...")
    df, encoders = LOADERS[name]()
    print(f"[INFO] {name}: {df.shape[0]} rows, {df.shape[1]} cols, "
          f"attack_ratio={df['label'].mean():.3f}")
    return df, encoders


def load_all_datasets():
    """Load all datasets. Returns dict of {name: (df, encoders)}."""
    results = {}
    for name in LOADERS:
        try:
            results[name] = load_dataset(name)
        except Exception as e:
            print(f"[WARN] Failed to load {name}: {e}")
    return results
