from pathlib import Path

from autoreport.data_loader import load_csv
from autoreport.pdf_generator import generate_pdf_report


def test_generate_pdf_report(tmp_path):
    # Load the sample dataset
    data = load_csv("data/sales.csv")

    # Store the PDF in pytest's temporary folder
    output_file = tmp_path / "report.pdf"

    # Generate the PDF
    result = generate_pdf_report(
        data=data,
        output_path=str(output_file),
    )

    # Verify that the PDF exists
    assert Path(result).exists()

    # Verify that the file is not empty
    assert Path(result).stat().st_size > 0

    # Verify that it is a PDF file
    with open(result, "rb") as file:
        assert file.read(5) == b"%PDF-"