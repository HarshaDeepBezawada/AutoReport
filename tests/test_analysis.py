import pandas as pd
import pytest

from autoreport import analysis
from autoreport.analysis import trends


def test_summary_stats_values():
    d = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
    s = analysis.summary_stats(d)
    assert s.loc["x", "mean"] == 3
    assert s.loc["x", "median"] == 3
    assert s.loc["x", "max"] == 5


def test_group_aggregate_sorted(df):
    g = analysis.group_aggregate(df, "region", "revenue", ["sum"])
    assert g["sum"].is_monotonic_decreasing
    with pytest.raises(KeyError):
        analysis.group_aggregate(df, "nope", "revenue")


def test_correlations_shape(df):
    c = analysis.correlations(df)
    assert set(c.columns) == {"units", "revenue"}


def test_zscore_flags_planted_anomaly(df):
    flagged = analysis.flag_anomalies(df, "revenue", "zscore")
    assert 10 in flagged.index


def test_iqr_flags_planted_anomaly(df):
    assert 10 in analysis.flag_anomalies(df, "revenue", "iqr").index


def test_constant_series_has_no_anomalies():
    assert not analysis.zscore_anomalies(pd.Series([5] * 10)).any()


def test_anomaly_bad_method(df):
    with pytest.raises(ValueError):
        analysis.flag_anomalies(df, "revenue", "magic")


def test_growth_and_direction():
    s = pd.Series([100, 110, 121, 133, 146])
    assert analysis.overall_growth(s) == 46.0
    assert analysis.trend_direction(s)["direction"] == "upward"
    assert analysis.trend_direction(s[::-1].reset_index(drop=True))["direction"] == "downward"
    assert analysis.trend_direction(pd.Series([1, 2]))["direction"] == "insufficient data"


def test_moving_average():
    ma = analysis.moving_average(pd.Series([1, 2, 3, 4]), 2)
    assert ma.tolist() == [1.0, 1.5, 2.5, 3.5]


def test_resample_drops_partial_last_month():
    d = pd.DataFrame({"date": pd.date_range("2025-01-01", "2025-03-10"), "v": 1})
    full = trends.resample_series(d, "date", "v", drop_partial=False)
    trimmed = trends.resample_series(d, "date", "v")
    assert len(full) == 3 and len(trimmed) == 2


def test_seasonality():
    dates = pd.date_range("2024-01-01", periods=24, freq="MS")
    s = pd.Series(range(24), index=dates)
    seas = analysis.seasonality(s)
    assert len(seas) == 12
    with pytest.raises(TypeError):
        analysis.seasonality(pd.Series([1, 2, 3]))


def test_growth_rate():
    s = pd.Series([100.0, 110.0, 121.0])
    gr = analysis.growth_rate(s)
    assert pd.isna(gr.iloc[0])
    assert gr.iloc[1] == 10.0
    assert gr.iloc[2] == 10.0


def test_top_n():
    d = pd.DataFrame({"a": [1, 5, 2, 8, 3]})
    t = analysis.top_n(d, "a", n=3)
    assert t["a"].tolist() == [8, 5, 3]


def test_resample_series_with_nat():
    d = pd.DataFrame({
        "date": [pd.Timestamp("2025-01-01"), pd.NaT, pd.Timestamp("2025-02-01")],
        "v": [10, 20, 30]
    })
    res = analysis.resample_series(d, "date", "v")
    assert len(res) >= 1


def test_anomaly_non_numeric_and_constant():
    s = pd.Series(["10", "12", "invalid", "1000", "11"])
    mask = analysis.zscore_anomalies(s, threshold=1.4)
    assert mask.iloc[3]  # "1000" flagged
    iqr_mask = analysis.iqr_anomalies(pd.Series([1.0] * 20))
    assert not iqr_mask.any()

