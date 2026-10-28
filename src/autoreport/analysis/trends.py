"""Time-series trend analysis: moving averages, growth rates, seasonality."""

from __future__ import annotations

import numpy as np
import pandas as pd


def resample_series(df: pd.DataFrame, date_col: str, value_col: str,
                    freq: str = "ME", agg: str = "sum",
                    drop_partial: bool = True) -> pd.Series:
    """Aggregate a value column over time (default: month end).

    With ``drop_partial`` the final period is removed when the data stops
    before that period ends, so a half-finished month does not look like a crash.
    """
    clean_df = df.dropna(subset=[date_col])
    if clean_df.empty:
        return pd.Series(dtype=float)
    s = clean_df.set_index(date_col)[value_col].sort_index()
    out = s.resample(freq).agg(agg)
    if drop_partial and len(out) > 1 and s.index.max().normalize() < out.index[-1].normalize():
        out = out.iloc[:-1]
    return out


def moving_average(series: pd.Series, window: int = 3) -> pd.Series:
    """Simple moving average."""
    if window < 1:
        raise ValueError("window must be >= 1")
    return series.rolling(window=window, min_periods=1).mean()


def growth_rate(series: pd.Series) -> pd.Series:
    """Period-over-period growth rate in percent."""
    return (series.pct_change() * 100).round(2)


def overall_growth(series: pd.Series) -> float | None:
    """Growth from the first to the last non-zero value, in percent."""
    s = series.dropna()
    if len(s) < 2 or s.iloc[0] == 0:
        return None
    return round(float((s.iloc[-1] - s.iloc[0]) / abs(s.iloc[0]) * 100), 2)


def trend_direction(series: pd.Series) -> dict:
    """Fit a linear trend and describe its direction and strength."""
    s = series.dropna()
    if len(s) < 3:
        return {"direction": "insufficient data", "slope": 0.0, "r2": 0.0}
    x = np.arange(len(s))
    slope, intercept = np.polyfit(x, s.values, 1)
    pred = slope * x + intercept
    ss_res = float(((s.values - pred) ** 2).sum())
    ss_tot = float(((s.values - s.values.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    rel = abs(slope) / abs(s.mean()) if s.mean() else 0
    if rel < 0.005:
        direction = "flat"
    else:
        direction = "upward" if slope > 0 else "downward"
    return {"direction": direction, "slope": round(float(slope), 2), "r2": round(r2, 3)}


def seasonality(series: pd.Series) -> pd.Series:
    """Average value by calendar month (needs a DatetimeIndex)."""
    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError("seasonality requires a DatetimeIndex")
    return series.groupby(series.index.month).mean().round(2)
