from typer.testing import CliRunner

from autoreport.cli import app

runner = CliRunner()


def test_hello_command():
    result = runner.invoke(app, ["hello"])

    assert result.exit_code == 0
    assert "Welcome to AutoReport!" in result.output


def test_analyze_command():
    result = runner.invoke(app, ["analyze", "data/sales.csv"])

    assert result.exit_code == 0
    assert "AUTOREPORT ANALYSIS" in result.output
    assert "340000" in result.output


def test_analyze_missing_file():
    result = runner.invoke(app, ["analyze", "data/unknown.csv"])

    assert result.exit_code == 1
    assert "File not found" in result.output


def test_chart_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    from pathlib import Path

    source_file = Path("data/sales.csv")
    source_file.parent.mkdir()
    source_file.write_text(
        "Product,Sales\nLaptop,50000\nMobile,30000\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["chart", "data/sales.csv"])

    assert result.exit_code == 0
    assert Path("reports/sales_chart.png").exists()


def test_html_report_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    from pathlib import Path

    source_file = Path("data/sales.csv")
    source_file.parent.mkdir()
    source_file.write_text(
        "Product,Sales\nLaptop,50000\nMobile,30000\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["report", "data/sales.csv"])

    assert result.exit_code == 0
    assert Path("reports/report.html").exists()


def test_pdf_report_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    from pathlib import Path

    source_file = Path("data/sales.csv")
    source_file.parent.mkdir()
    source_file.write_text(
        "Product,Sales\nLaptop,50000\nMobile,30000\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["pdf", "data/sales.csv"])

    assert result.exit_code == 0
    assert Path("reports/report.pdf").exists()