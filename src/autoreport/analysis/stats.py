"""Statistical analysis: summaries, group-by aggregations, correlations."""

from __future__ import annotations

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
