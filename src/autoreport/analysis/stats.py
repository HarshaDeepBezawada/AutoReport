"""Statistical analysis: summaries, group-by aggregations, correlations."""

from __future__ import annotations

from typing import Any

import pandas as pd


def summary_stats(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Mean, median, std dev, min, max and percentiles for numeric columns."""
    num = df.select_dtypes("number")
    if columns:
        num = num[[c for c in columns if c in num.columns]]
    if num.empty:
        return pd.DataFrame()
    out = pd.DataFrame({
        "count": num.count(),
        "mean": num.mean(),
        "median": num.median(),
        "std": num.std(),
        "min": num.min(),
        "p25": num.quantile(0.25),
        "p75": num.quantile(0.75),
        "p95": num.quantile(0.95),
        "max": num.max(),
    })
    return out.round(2)


def group_aggregate(df: pd.DataFrame, by: str, value: str,
                    aggs: list[str] | None = None) -> pd.DataFrame:
    """Group-by aggregation, sorted by the first aggregate (descending)."""
    aggs = aggs or ["sum", "mean", "count"]
    if by not in df.columns or value not in df.columns:
        raise KeyError(f"Columns '{by}'/'{value}' must exist in the data")
    out = df.groupby(by)[value].agg(aggs).reset_index()
    return out.sort_values(aggs[0], ascending=False).round(2).reset_index(drop=True)


def correlations(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Pearson correlation matrix over numeric columns."""
    num = df.select_dtypes("number")
    if columns:
        num = num[[c for c in columns if c in num.columns]]
    return num.corr().round(2) if num.shape[1] > 1 else pd.DataFrame()


def top_n(df: pd.DataFrame, by: str, n: int = 5, ascending: bool = False) -> pd.DataFrame:
    """Top (or bottom) ``n`` rows by a column."""
    return df.sort_values(by, ascending=ascending).head(n).reset_index(drop=True)


def compare_segments(df: pd.DataFrame, segment_col: str, value_col: str,
                     agg: str = "sum") -> pd.DataFrame:
    """Compare performance across segments relative to the benchmark/average.

    Returns a DataFrame with total, share_pct, diff_from_mean, and index_vs_mean.
    """
    if segment_col not in df.columns or value_col not in df.columns:
        raise KeyError(f"Columns '{segment_col}'/'{value_col}' must exist in the data")
    grouped = df.groupby(segment_col)[value_col].agg(agg).reset_index()
    total = grouped[value_col].sum()
    mean_val = grouped[value_col].mean()
    grouped["share_pct"] = ((grouped[value_col] / total) * 100).round(1) if total else 0.0
    grouped["diff_from_avg"] = (grouped[value_col] - mean_val).round(2)
    grouped["index_vs_avg"] = ((grouped[value_col] / mean_val) * 100).round(1) if mean_val else 100.0
    return grouped.sort_values(value_col, ascending=False).reset_index(drop=True)


def compare_periods(df: pd.DataFrame, date_col: str, value_col: str,
                    freq: str = "ME", agg: str = "sum") -> dict[str, Any]:
    """Compare the most recent period to the prior period.

    Returns current, previous, absolute change, percentage growth, and narrative summary.
    """
    from .trends import resample_series
    s = resample_series(df, date_col, value_col, freq=freq, agg=agg, drop_partial=True)
    if len(s) < 2:
        return {
            "current": None,
            "previous": None,
            "diff": 0.0,
            "growth_pct": None,
            "narrative": "Insufficient periods for comparison.",
        }
    curr = float(s.iloc[-1])
    prev = float(s.iloc[-2])
    diff = curr - prev
    pct = round((diff / abs(prev)) * 100, 2) if prev != 0 else None
    direction = "grew" if diff > 0 else "declined" if diff < 0 else "remained flat"
    curr_str = f"{curr:,.2f}"
    prev_str = f"{prev:,.2f}"
    pct_str = f"{abs(pct):.1f}%" if pct is not None else "n/a"
    narrative = f"{value_col} {direction} by {pct_str} ({curr_str} vs {prev_str} in previous period)."
    return {
        "current": round(curr, 2),
        "previous": round(prev, 2),
        "diff": round(diff, 2),
        "growth_pct": pct,
        "narrative": narrative,
    }
