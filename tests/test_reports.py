import pytest
import yaml
from typer.testing import CliRunner

from autoreport.cli import app
from autoreport.generator import generate_report
from autoreport.template import TemplateError, list_templates, parse_template, validate_template
from autoreport.viz import ChartError, make_plotly_chart, make_static_chart

runner = CliRunner()


def test_builtin_templates_all_valid():
    names = {t["name"] for t in list_templates()}
    assert {"sales", "hr", "inventory"} <= names
    for t in list_templates():
        assert validate_template(yaml.safe_load(open(t["path"], encoding="utf-8"))) == []


def test_validate_template_reports_problems():
    probs = validate_template({"name": "x", "sections": [{"type": "bogus"}, {"type": "chart", "chart": {"type": "radar"}}]})
    assert any("title" in p for p in probs)
    assert any("unknown type" in p for p in probs)
    assert any("chart.type" in p for p in probs)
    with pytest.raises(TemplateError):
        parse_template({"name": "x"})


@pytest.mark.parametrize("spec", [
    {"type": "bar", "x": "region", "y": "revenue", "agg": "sum"},
    {"type": "pie", "x": "region", "y": "revenue", "agg": "sum"},
    {"type": "line", "x": "date", "y": "revenue"},
    {"type": "scatter", "x": "units", "y": "revenue", "hue": "region"},
    {"type": "histogram", "x": "revenue"},
    {"type": "heatmap", "columns": ["units", "revenue"]},
])
def test_every_chart_type_renders_both_ways(df, spec):
    assert make_static_chart(df, spec)[:8] == b"\x89PNG\r\n\x1a\n"
    assert make_plotly_chart(df, spec).data


def test_chart_errors(df):
    with pytest.raises(ChartError):
        make_static_chart(df, {"type": "radar"})
    with pytest.raises(ChartError):
        make_static_chart(df, {"type": "bar"})


def test_generate_html_and_pdf(tmp_path, csv_file, small_template):
    files = generate_report(str(small_template), str(csv_file), tmp_path / "out", "both")
    assert [f.suffix for f in files] == [".html", ".pdf"]
    html = files[0].read_text(encoding="utf-8")
    assert "Small Report" in html and "plotly" in html.lower()
    assert files[1].read_bytes()[:5] == b"%PDF-"


def test_generate_bad_format(tmp_path, csv_file, small_template):
    with pytest.raises(ValueError):
        generate_report(str(small_template), str(csv_file), tmp_path, "docx")


def test_cli_generate_and_errors(tmp_path, csv_file, small_template):
    ok = runner.invoke(app, ["generate", str(small_template), "-d", str(csv_file),
                             "-o", str(tmp_path / "o"), "-f", "html"])
    assert ok.exit_code == 0 and "Created" in ok.output
    bad = runner.invoke(app, ["generate", "nonexistent", "-d", str(csv_file)])
    assert bad.exit_code == 1 and "not found" in bad.output
    missing = runner.invoke(app, ["generate", str(small_template), "-d", str(tmp_path / "no.csv")])
    assert missing.exit_code == 1


def test_cli_validate_and_list(small_template, csv_file):
    assert runner.invoke(app, ["validate", str(small_template), "-d", str(csv_file)]).exit_code == 0
    out = runner.invoke(app, ["list-templates"])
    assert "sales" in out.output and "inventory" in out.output


def test_cli_validate_catches_bad_template(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("name: x\ntitle: y\nsections: []\n")
    r = runner.invoke(app, ["validate", str(p)])
    assert r.exit_code == 1


def test_cli_version():
    r = runner.invoke(app, ["--version"])
    assert r.exit_code == 0
    assert "autoreport" in r.output


def test_cli_schedule_validation(small_template, csv_file):
    # bad cron
    r = runner.invoke(app, ["schedule", str(small_template), "--cron", "not a cron"])
    assert r.exit_code == 1
    # bad template
    r2 = runner.invoke(app, ["schedule", "nonexistent_template", "--every", "10"])
    assert r2.exit_code == 1


def test_chart_missing_column_error(df):
    with pytest.raises(ChartError, match="not found in data"):
        make_static_chart(df, {"type": "bar", "x": "missing_col", "y": "revenue"})
    with pytest.raises(ChartError, match="not found in data"):
        make_plotly_chart(df, {"type": "line", "x": "date", "y": "missing_col"})

