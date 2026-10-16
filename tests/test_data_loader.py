from autoreport.data_loader import load_csv


def test_load_sales_csv():
    data = load_csv("data/sales.csv")

    assert not data.empty
    assert "Product" in data.columns
    assert "Sales" in data.columns
    assert len(data) == 8