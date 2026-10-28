"""Anomaly detection: Z-score and IQR outlier flagging."""

from __future__ import annotations

import pandas as pd


def zscore_anomalies(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Boolean mask of values whose |z-score| exceeds ``threshold``."""
    s = pd.to_numeric(series, errors="coerce")
    std = s.std()
    if not std or pd.isna(std):
        return pd.Series(False, index=series.index)
    return (((s - s.mean()) / std).abs() > threshold).fillna(False)


def iqr_anomalies(series: pd.Series, k: float = 1.5) -> pd.Series:
    """Boolean mask of values outside [Q1 - k*IQR, Q3 + k*IQR]."""
    s = pd.to_numeric(series, errors="coerce")
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0 or pd.isna(iqr):
        return pd.Series(False, index=series.index)
    return ((s < q1 - k * iqr) | (s > q3 + k * iqr)).fillna(False)


def flag_anomalies(df: pd.DataFrame, column: str, method: str = "zscore",
                   threshold: float | None = None) -> pd.DataFrame:
    """Return the rows of ``df`` that are anomalous in ``column``."""
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found")
    if method == "zscore":
        mask = zscore_anomalies(df[column], threshold or 3.0)
    elif method == "iqr":
        mask = iqr_anomalies(df[column], threshold or 1.5)
    else:
        raise ValueError(f"Unknown method '{method}' (use 'zscore' or 'iqr')")
    return df[mask]
