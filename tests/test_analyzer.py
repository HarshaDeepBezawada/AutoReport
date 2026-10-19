from autoreport.data_loader import load_csv
from autoreport.analyzer import analyze_data


def test_analyze_sales():
    data = load_csv("data/sales.csv")
    result = analyze_data(data)

    assert result["Sales"]["total"] == 340000
    assert result["Sales"]["average"] == 42500
    assert result["Sales"]["minimum"] == 20000
    assert result["Sales"]["maximum"] == 70000