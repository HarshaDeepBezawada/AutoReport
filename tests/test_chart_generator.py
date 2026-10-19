from pathlib import Path

import pandas as pd
import pytest

from autoreport.chart_generator import generate_chart


def test_generate_chart(tmp_path):
    data = pd.DataFrame({
        "Product": ["Laptop", "Mobile", "Tablet"],
        "Sales": [50000, 30000, 20000],
    })

    output_file = tmp_path / "sales_chart.png"

    result = generate_chart(
        data=data,
        column="Sales",
        output_path=str(output_file),
    )

    assert Path(result).exists()
    assert Path(result).stat().st_size > 0


def test_generate_chart_missing_column(tmp_path):
    data = pd.DataFrame({
        "Sales": [50000, 30000],
    })

    with pytest.raises(ValueError, match="was not found"):
        generate_chart(
            data=data,
            column="Profit",
            output_path=str(tmp_path / "chart.png"),
        )


def test_generate_chart_non_numeric_column(tmp_path):
    data = pd.DataFrame({
        "Product": ["Laptop", "Mobile"],
    })

    with pytest.raises(ValueError, match="no numeric data"):
        generate_chart(
            data=data,
            column="Product",
            output_path=str(tmp_path / "chart.png"),
        )