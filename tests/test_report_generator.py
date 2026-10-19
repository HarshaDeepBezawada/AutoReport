from pathlib import Path

from autoreport.data_loader import load_csv
from autoreport.report_generator import generate_html_report


def test_generate_html_report(tmp_path):
    # Load the sample sales dataset
    data = load_csv("data/sales.csv")

    # Generate the report inside pytest's temporary folder
    output_file = tmp_path / "report.html"

    result = generate_html_report(
        data=data,
        output_path=str(output_file),
    )

    # Check that the report was created
    assert Path(result).exists()

    # Read the generated HTML
    html = Path(result).read_text(encoding="utf-8")

    # Check that important report content is present
    assert "AutoReport Data Report" in html
    assert "Dataset Preview" in html
    assert "Statistical Summary" in html
    assert "Laptop" in html
    assert "Sales" in html