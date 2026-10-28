"""Generate synthetic demo datasets (Sales, HR, Inventory). No real data used."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data"


def sales(rng: np.random.Generator, n: int = 1500) -> pd.DataFrame:
    dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 638, n), unit="D")
    region = rng.choice(["North", "South", "East", "West"], n, p=[.3, .25, .25, .2])
    product = rng.choice(["Laptop", "Phone", "Tablet", "Monitor", "Headset"], n)
    price = {"Laptop": 900, "Phone": 600, "Tablet": 350, "Monitor": 250, "Headset": 80}
    units = rng.integers(1, 12, n)
    base = np.array([price[p] for p in product]) * units
    season = 1 + 0.25 * np.sin((dates.month.values - 3) / 12 * 2 * np.pi)
    growth = 1 + (dates - dates.min()).days.values / 1500
    revenue = (base * season * growth * rng.normal(1, 0.08, n)).round(2)
    df = pd.DataFrame({"date": dates, "region": region, "product": product,
                       "units": units, "revenue": revenue,
                       "discount_pct": rng.choice([0, 5, 10, 15], n)})
    spikes = rng.choice(n, 8, replace=False)
    df.loc[spikes, "revenue"] *= rng.uniform(4, 6, 8)  # injected anomalies
    return df.sort_values("date").reset_index(drop=True)


def hr(rng: np.random.Generator, n: int = 400) -> pd.DataFrame:
    dept = rng.choice(["Engineering", "Sales", "Support", "Finance", "HR"], n, p=[.35, .25, .2, .1, .1])
    base = {"Engineering": 95000, "Sales": 70000, "Support": 52000, "Finance": 82000, "HR": 64000}
    tenure = rng.gamma(2.2, 2.0, n).round(1)
    salary = np.array([base[d] for d in dept]) + tenure * 1800 + rng.normal(0, 6000, n)
    df = pd.DataFrame({
        "employee_id": np.arange(1001, 1001 + n),
        "department": dept,
        "salary": salary.round(0),
        "tenure_years": tenure,
        "performance_score": np.clip(rng.normal(3.4, 0.7, n), 1, 5).round(1),
        "hire_date": pd.to_datetime("2026-06-30") - pd.to_timedelta((tenure * 365).astype(int), unit="D"),
        "remote_days": rng.integers(0, 6, n),
    })
    df.loc[rng.choice(n, 4, replace=False), "salary"] *= 2.2  # outliers
    return df


def inventory(rng: np.random.Generator, n: int = 600) -> pd.DataFrame:
    cat = rng.choice(["Electronics", "Furniture", "Stationery", "Apparel", "Toys"], n)
    cost = rng.gamma(3, 25, n).round(2)
    stock = rng.integers(0, 500, n)
    df = pd.DataFrame({
        "sku": [f"SKU-{i:05d}" for i in range(n)],
        "category": cat,
        "unit_cost": cost,
        "stock": stock,
        "reorder_level": rng.integers(20, 120, n),
        "sold_last_30d": np.clip(rng.poisson(40, n), 0, None),
        "last_restock": pd.to_datetime("2026-09-30") - pd.to_timedelta(rng.integers(0, 365, n), unit="D"),
    })
    df["stock_value"] = (df["unit_cost"] * df["stock"]).round(2)
    df.loc[rng.choice(n, 5, replace=False), "stock"] = rng.integers(2500, 4000, 5)
    df["stock_value"] = (df["unit_cost"] * df["stock"]).round(2)
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    s, h, i = sales(rng), hr(rng), inventory(rng)
    s.to_csv(OUT / "sales.csv", index=False)
    h.to_excel(OUT / "hr.xlsx", index=False)
    i.to_json(OUT / "inventory.json", orient="records", date_format="iso", indent=1)
    with closing(sqlite3.connect(OUT / "inventory.db")) as conn:
        i.to_sql("inventory", conn, if_exists="replace", index=False)
    print(f"Wrote sample data to {OUT}: sales.csv, hr.xlsx, inventory.json, inventory.db")


if __name__ == "__main__":
    main()
