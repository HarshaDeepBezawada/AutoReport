import pandas as pd
import pytest

from autoreport.data_loader import load_csv, load_excel, load_json


def test_load_sales_csv():
    data = load_csv("data/sales.csv")

    assert not data.empty
    assert "Product" in data.columns
    assert "Sales" in data.columns
    assert len(data) == 8


def test_missing_csv_file():
    with pytest.raises(FileNotFoundError):
        load_csv("data/does_not_exist.csv")


def test_empty_csv_file(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("Product,Sales\n", encoding="utf-8")

    with pytest.raises(ValueError, match="contains no data"):
        load_csv(str(empty_file))


def test_load_excel_file(tmp_path):
    excel_file = tmp_path / "sales.xlsx"

    data = pd.DataFrame({
        "Product": ["Laptop", "Mobile"],
        "Sales": [50000, 30000],
    })

    data.to_excel(excel_file, index=False)

    result = load_excel(str(excel_file))

    assert len(result) == 2
    assert "Product" in result.columns
    assert result["Sales"].sum() == 80000


def test_load_json_file(tmp_path):
    json_file = tmp_path / "sales.json"

    json_file.write_text(
        '[{"Product": "Laptop", "Sales": 50000},'
        '{"Product": "Mobile", "Sales": 30000}]',
        encoding="utf-8",
    )

    result = load_json(str(json_file))

    assert len(result) == 2
    assert "Product" in result.columns
    assert result["Sales"].sum() == 80000