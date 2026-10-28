"""Performance verification script for Code A Nova evaluation.

Benchmarks AutoReport against the official task constraint:
- Must handle datasets up to 100,000 rows without memory issues.
- Reports must generate in under 30 seconds for standard datasets.
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

from autoreport.generator import generate_report
from autoreport.template import build_report_data, load_data, load_template


def generate_benchmark_dataset(n: int = 100_000, seed: int = 42) -> pd.DataFrame:
    print(f"Generating synthetic benchmark dataset ({n:,} rows)...")
    rng = np.random.default_rng(seed)
    dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 730, n), unit="D")
    df = pd.DataFrame({
        "date": dates,
        "region": rng.choice(["North", "South", "East", "West"], n, p=[0.3, 0.25, 0.25, 0.2]),
        "product": rng.choice(["Laptop", "Phone", "Tablet", "Monitor", "Headset"], n),
        "units": rng.integers(1, 12, n),
        "revenue": rng.normal(1000, 100, n).round(2),
        "discount_pct": rng.choice([0, 5, 10, 15], n),
    })
    return df


def run_benchmark(n_rows: int = 100_000) -> bool:
    print("=" * 70)
    print("AUTOREPORT PERFORMANCE BENCHMARK (100K ROWS)")
    print("=" * 70)

    df = generate_benchmark_dataset(n_rows)

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_file = Path(tmpdir) / f"benchmark_{n_rows}.csv"
        out_dir = Path(tmpdir) / "output"

        t_csv_start = time.perf_counter()
        df.to_csv(csv_file, index=False)
        t_csv = time.perf_counter() - t_csv_start
        print(f"Dataset written to disk: {csv_file.stat().st_size / (1024 * 1024):.2f} MB in {t_csv:.2f}s")

        print("\n--- Pipeline Step Breakdown ---")
        # Step 1: Template & Data Loading
        t0 = time.perf_counter()
        tpl = load_template("sales")
        loaded_df = load_data(tpl, str(csv_file))
        t_load = time.perf_counter() - t0
        print(f"  1. Ingestion & Schema Validation: {t_load:.2f}s")

        # Step 2: Statistical & Analytical Processing
        t0 = time.perf_counter()
        _ = build_report_data(tpl, loaded_df)
        t_analysis = time.perf_counter() - t0
        print(f"  2. Analysis (Stats, Trend, Anomalies, KPIs): {t_analysis:.2f}s")

        # Step 3: Full End-to-End Generation (HTML + PDF with Charts)
        print("\n--- End-to-End Report Generation (HTML + PDF) ---")
        t_gen_start = time.perf_counter()
        reports = generate_report("sales", str(csv_file), out_dir, fmt="both")
        t_gen_total = time.perf_counter() - t_gen_start

        print(f"Total generation time: {t_gen_total:.2f}s")
        for r in reports:
            print(f"  - Generated: {r.name} ({r.stat().st_size / 1024:.1f} KB)")

        threshold = 30.0
        passed = t_gen_total < threshold
        print("\n" + "=" * 70)
        print(f"BENCHMARK RESULT: {'VERIFIED PASS' if passed else 'FAIL'}")
        print(f"Measured time: {t_gen_total:.2f}s (Threshold: < {threshold:.1f}s)")
        print("=" * 70)
        return passed


if __name__ == "__main__":
    success = run_benchmark(100_000)
    sys.exit(0 if success else 1)
