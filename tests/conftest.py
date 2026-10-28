import json
import sqlite3

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def df() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 120
    out = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=n, freq="D"),
        "region": rng.choice(["N", "S", "E"], n),
        "units": rng.integers(1, 10, n),
        "revenue": rng.normal(1000, 50, n).round(2),
    })
    out.loc[10, "revenue"] = 9000  # obvious anomaly
    return out


@pytest.fixture
def csv_file(tmp_path, df):
    p = tmp_path / "data.csv"
    df.to_csv(p, index=False)
    return p


@pytest.fixture
def small_template(tmp_path):
    tpl = tmp_path / "t.yaml"
    tpl.write_text("""
name: small
title: Small Report
description: test
schema: {region: string, units: numeric, revenue: numeric}
date_columns: [date]
sections:
  - {type: kpis, title: KPIs, items: [{label: Total, column: revenue, agg: sum, format: currency}]}
  - {type: summary, title: Stats, columns: [revenue]}
  - {type: chart, title: C, chart: {type: bar, x: region, y: revenue, agg: sum}}
  - {type: trend, title: T, date: date, column: revenue}
  - {type: anomalies, title: A, column: revenue, show: [date, revenue]}
""", encoding="utf-8")
    return tpl
