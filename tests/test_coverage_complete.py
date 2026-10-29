"""Comprehensive edge case and branch tests to achieve maximum coverage and robustness."""

import pandas as pd
import pytest
from typer.testing import CliRunner

from autoreport import analysis
from autoreport.builders.html_builder import build_html
from autoreport.builders.pdf_builder import _kpi_table, _styles, _table, build_pdf
from autoreport.cli import app
from autoreport.ingestion import DataSourceError, get_source, validate_schema
from autoreport.template import (
    TemplateError,
    _fmt,
    build_report_data,
    list_templates,
    load_data,
    load_template,
    parse_template,
    resolve_template_path,
    validate_template,
)
from autoreport.viz import ChartError, make_plotly_chart, make_static_chart, png_to_data_uri

runner = CliRunner()


def test_analysis_all_edge_cases(df):
    # flag_anomalies on missing column
    with pytest.raises(KeyError, match="not found"):
        analysis.flag_anomalies(df, "nonexistent_col")

    # summary_stats with no numeric columns
    empty_df = pd.DataFrame({"text": ["a", "b"]})
    assert analysis.summary_stats(empty_df).empty
    assert analysis.summary_stats(df, columns=["nonexistent"]).empty

    # correlations with specific column list
    corr = analysis.correlations(df, columns=["units", "revenue"])
    assert corr.shape == (2, 2)

    # moving_average with invalid window
    with pytest.raises(ValueError, match="window must be >= 1"):
        analysis.moving_average(pd.Series([1, 2, 3]), window=0)

    # overall_growth with short series or 0 denominator
    assert analysis.overall_growth(pd.Series([10])) is None
    assert analysis.overall_growth(pd.Series([0, 10, 20])) is None

    # trend_direction with flat slope
    flat_s = pd.Series([100.0, 100.01, 99.99, 100.0])
    assert analysis.trend_direction(flat_s)["direction"] == "flat"

    # resample_series with empty cleaned dataframe (all NaT)
    d_nat = pd.DataFrame({"date": [pd.NaT, pd.NaT], "val": [1, 2]})
    assert analysis.trends.resample_series(d_nat, "date", "val").empty


def test_ingestion_edge_cases(tmp_path, df):
    # missing date column in load
    csv_p = tmp_path / "data.csv"
    df.to_csv(csv_p, index=False)
    with pytest.raises(DataSourceError, match="Date column 'not_there' not found"):
        get_source(str(csv_p)).load(date_columns=["not_there"])

    # validate_schema with "any" type
    validate_schema(df, {"revenue": "any", "region": "any"})

    # validate_schema with unknown type
    with pytest.raises(DataSourceError, match="Unknown schema type 'special'"):
        validate_schema(df, {"revenue": "special"})


def test_charts_edge_cases(df):
    # bar chart with agg and limit
    bar_spec = {"type": "bar", "x": "region", "y": "revenue", "agg": "sum", "limit": 2}
    png = make_static_chart(df, bar_spec)
    assert png.startswith(b"\x89PNG")
    fig = make_plotly_chart(df, bar_spec)
    assert len(fig.data[0].x) == 2

    # line chart with agg and freq
    line_spec = {"type": "line", "x": "date", "y": "revenue", "agg": "mean", "freq": "W"}
    png_line = make_static_chart(df, line_spec)
    assert png_line.startswith(b"\x89PNG")
    fig_line = make_plotly_chart(df, line_spec)
    assert fig_line.data

    # pie chart with sum <= 0
    zero_df = pd.DataFrame({"cat": ["A", "B"], "val": [0, 0]})
    with pytest.raises(ChartError, match="must sum to a positive number"):
        make_static_chart(zero_df, {"type": "pie", "x": "cat", "y": "val"})

    # png_to_data_uri
    uri = png_to_data_uri(b"fake_png_data")
    assert uri.startswith("data:image/png;base64,")


def test_html_and_pdf_builders_complete(tmp_path, df):
    # HTML builder with interactive=False (static embedded charts)
    spec = {"type": "bar", "x": "region", "y": "revenue"}
    sections = [
        {"type": "text", "title": "Overview", "text": "Report intro text."},
        {"type": "chart", "title": "Chart", "chart": spec},
        {"type": "table", "title": "Table", "table": {"columns": ["A"], "rows": [[1]]}},
    ]
    html_out = tmp_path / "static_report.html"
    build_html("Static Report", "desc", sections, df, html_out, interactive=False)
    assert html_out.exists()
    content = html_out.read_text(encoding="utf-8")
    assert "data:image/png;base64," in content

    # PDF builder with empty table, empty KPIs, text section, and >12 rows table
    long_rows = [[f"row_{i}", i * 10] for i in range(20)]
    pdf_sections = [
        {"type": "text", "title": "Section Title", "text": "Paragraph body text.", "narrative": "Narrative note."},
        {"type": "kpis", "title": "KPIs", "kpis": [{"label": "Metric", "value": "100"}]},
        {"type": "table", "title": "Empty Table", "table": {"columns": ["Empty"], "rows": []}},
        {"type": "table", "title": "Long Table", "table": {"columns": ["Name", "Value"], "rows": long_rows}},
        {"type": "chart", "title": "Chart With Table", "chart": spec, "table": {"columns": ["Name", "Val"], "rows": [["x", 1]]}},
    ]
    pdf_out = tmp_path / "edge_report.pdf"
    build_pdf("Edge Report", "desc", pdf_sections, df, pdf_out)
    assert pdf_out.exists()
    assert pdf_out.read_bytes().startswith(b"%PDF-")


def test_template_and_pipeline_complete(tmp_path, df):
    # list_templates with invalid extra_dir or bad yaml
    bad_dir = tmp_path / "non_existent_folder"
    assert list_templates(bad_dir)  # skips missing dir safely

    custom_dir = tmp_path / "custom_tpls"
    custom_dir.mkdir()
    (custom_dir / "broken.yaml").write_text("invalid: [yaml: broken", encoding="utf-8")
    valid_custom = custom_dir / "custom.yaml"
    valid_custom.write_text("name: custom_one\ntitle: Custom\nsections: [{type: text}]", encoding="utf-8")
    tpls = list_templates(custom_dir)
    assert any(t["name"] == "custom_one" for t in tpls)

    # resolve_template_path from extra_dir
    found_path = resolve_template_path("custom_one", custom_dir)
    assert found_path == valid_custom

    # load_template with corrupted yaml syntax
    corrupted_p = tmp_path / "bad.yaml"
    corrupted_p.write_text("name: [unclosed list", encoding="utf-8")
    with pytest.raises(TemplateError, match="Invalid YAML"):
        load_template(str(corrupted_p))

    # validate_template error branches
    assert "YAML mapping" in validate_template("string instead of dict")[0]
    assert any("missing 'type'" in p for p in validate_template({"name": "x", "title": "y", "sections": ["not a dict"]}))
    assert any("kpis' needs 'items'" in p for p in validate_template({"name": "x", "title": "y", "sections": [{"type": "kpis"}]}))
    assert any("trend' needs 'column'" in p for p in validate_template({"name": "x", "title": "y", "sections": [{"type": "trend"}]}))

    # load_data without path
    no_src_tpl = parse_template({"name": "x", "title": "y", "sections": [{"type": "text"}]})
    with pytest.raises(DataSourceError, match="No data source"):
        load_data(no_src_tpl)

    # load_data with empty dataframe
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("colA,colB\n", encoding="utf-8")
    with pytest.raises(DataSourceError, match="contains no rows"):
        load_data(no_src_tpl, str(empty_csv))

    # _fmt helper branches
    assert _fmt(None) == "n/a"
    assert _fmt(float("nan")) == "n/a"
    assert _fmt(12.345, "percent") == "12.3%"
    assert _fmt(50000) == "50,000"
    assert _fmt("plain_str") == "plain_str"

    # build_report_data with unknown KPI agg
    bad_kpi_tpl = parse_template({
        "name": "x", "title": "y",
        "sections": [{"type": "kpis", "items": [{"label": "bad", "column": "revenue", "agg": "invalid_agg"}]}]
    })
    with pytest.raises(TemplateError, match="Unknown KPI aggregation"):
        build_report_data(bad_kpi_tpl, df)

    # build_report_data with plain table sorted ascending
    tbl_tpl = parse_template({
        "name": "x", "title": "y",
        "sections": [
            {"type": "text", "text": "Intro text"},
            {"type": "table", "columns": ["region", "units"], "sort_by": "units", "ascending": True, "limit": 5}
        ]
    })
    items = build_report_data(tbl_tpl, df)
    assert items[0]["text"] == "Intro text"
    assert len(items[1]["table"]["rows"]) == 5

    # build_report_data with group_by table
    group_tpl = parse_template({
        "name": "g", "title": "G",
        "sections": [{"type": "table", "group_by": "region", "value": "revenue"}]
    })
    g_items = build_report_data(group_tpl, df)
    assert len(g_items[0]["table"]["rows"]) == df["region"].nunique()


def test_pdf_builder_empty_helpers():
    st = _styles()
    t = _table({}, 100, st)
    assert t is not None
    k = _kpi_table([], 100, st)
    assert k is not None


def test_charts_unknown_type_handling(df):
    with pytest.raises(ChartError, match="Unknown chart type"):
        make_static_chart(df, {"type": "unknown_kind"})
    with pytest.raises(ChartError, match="Unknown chart type"):
        make_plotly_chart(df, {"type": "unknown_kind"})

    # heatmap with fewer than 2 numeric columns without explicit columns key
    single_num_df = pd.DataFrame({"only_one": [1, 2, 3], "text": ["a", "b", "c"]})
    with pytest.raises(ChartError, match="Heatmap needs at least two numeric columns"):
        make_static_chart(single_num_df, {"type": "heatmap"})
    with pytest.raises(ChartError, match="Heatmap needs at least two numeric columns"):
        make_plotly_chart(single_num_df, {"type": "heatmap"})



def test_cli_advanced_branches(tmp_path, csv_file, monkeypatch):
    # CLI validate with bad YAML
    bad_yaml = tmp_path / "syntax_err.yaml"
    bad_yaml.write_text("name: [unclosed", encoding="utf-8")
    res_bad = runner.invoke(app, ["validate", str(bad_yaml)])
    assert res_bad.exit_code == 1

    # CLI validate with data loading error
    good_yaml = tmp_path / "valid.yaml"
    good_yaml.write_text("name: v\ntitle: V\nschema: {missing_col: numeric}\nsections: [{type: text}]", encoding="utf-8")
    res_data_err = runner.invoke(app, ["validate", str(good_yaml), "-d", str(csv_file)])
    assert res_data_err.exit_code == 1
    assert "Missing required columns" in res_data_err.output

    # CLI list-templates when empty
    monkeypatch.setattr("autoreport.cli._list_templates", lambda *a, **k: [])
    res_empty_tpl = runner.invoke(app, ["list-templates"])
    assert "No templates found." in res_empty_tpl.output

    # CLI schedule with mocked scheduler and run_now=True
    class MockSched:
        def __init__(self):
            self.started = False

        def start(self):
            self.started = True
            raise KeyboardInterrupt()

    monkeypatch.setattr("autoreport.cli.create_scheduler", lambda job, trigger, blocking: MockSched())
    res_sched = runner.invoke(app, ["schedule", "sales", "--every", "10", "--run-now"])
    assert res_sched.exit_code == 0
    assert "Scheduler stopped." in res_sched.output


def test_comparison_and_narrative_full_coverage(df):
    # test compare_segments
    with pytest.raises(KeyError, match="must exist"):
        analysis.compare_segments(df, "nonexistent", "revenue")

    seg = analysis.compare_segments(df, "region", "revenue")
    assert "share_pct" in seg.columns
    assert "diff_from_avg" in seg.columns
    assert "index_vs_avg" in seg.columns
    assert len(seg) == df["region"].nunique()

    # test compare_periods
    p_res = analysis.compare_periods(df, "date", "revenue", freq="ME")
    assert "current" in p_res
    assert "previous" in p_res
    assert "growth_pct" in p_res
    assert "narrative" in p_res

    # test compare_periods with insufficient data (< 2 periods)
    short_df = df.head(1).copy()
    p_short = analysis.compare_periods(short_df, "date", "revenue")
    assert p_short["current"] is None
    assert p_short["narrative"] == "Insufficient periods for comparison."

    # test validate_template for comparison without segment or date
    bad_cmp_dict = {
        "name": "bad_cmp", "title": "Bad",
        "sections": [{"type": "comparison", "value": "revenue"}]
    }
    problems = validate_template(bad_cmp_dict)
    assert any("'comparison' needs 'segment' (or 'date')" in p for p in problems)

    with pytest.raises(TemplateError, match="'comparison' needs 'segment'"):
        parse_template(bad_cmp_dict)

    # test build_report_data when comparison value is invalid/None
    bad_val_cmp = parse_template({
        "name": "bvc", "title": "BVC",
        "sections": [{"type": "comparison", "segment": "region", "value": "revenue"}]
    })
    bad_val_cmp.sections[0].options["value"] = None
    with pytest.raises(TemplateError, match="requires a valid 'value' column"):
        build_report_data(bad_val_cmp, df)

    # test build_report_data with period comparison
    period_cmp_tpl = parse_template({
        "name": "pc", "title": "PC",
        "sections": [{"type": "comparison", "title": "Period Comparison", "date": "date", "value": "revenue"}]
    })
    p_items = build_report_data(period_cmp_tpl, df)
    assert p_items[0]["type"] == "comparison"
    assert "kpis" in p_items[0]

    # test build_report_data with narrative section having bad data to trigger exception branches
    bad_dates_df = pd.DataFrame({
        "metric_col": [10, 20, 30],
        "date_col": ["invalid_date_1", "invalid_date_2", "invalid_date_3"],
        "segment_col": ["A", "B", "C"],
        "anomaly_col": ["str1", "str2", "str3"]
    })
    narrative_tpl = parse_template({
        "name": "nar", "title": "NAR",
        "sections": [{
            "type": "narrative",
            "metric": "metric_col",
            "date": "date_col",
            "segment": "segment_col",
            "anomaly_col": "anomaly_col"
        }]
    })
    n_items = build_report_data(narrative_tpl, bad_dates_df)
    assert any(term in n_items[0]["narrative"] for term in ("Executive performance summary", "Automated intelligence summary", "summary across"))

    # Trigger exception branches in narrative
    bad_anom_tpl = parse_template({
        "name": "nar2", "title": "NAR2",
        "sections": [{
            "type": "narrative",
            "metric": "metric_col",
            "date": "date_col",
            "segment": "segment_col",
            "anomaly_col": "anomaly_col",
            "anomaly_method": "invalid_method"
        }]
    })
    empty_df = pd.DataFrame(columns=["metric_col", "date_col", "segment_col", "anomaly_col"])
    n_items_empty = build_report_data(bad_anom_tpl, empty_df)
    assert any(term in n_items_empty[0]["narrative"] for term in ("Executive performance summary", "Automated intelligence summary", "summary across"))





