"""YAML report template loading, validation and the analysis pipeline.

A template defines the data source, schema, and an ordered list of sections.
Section types: ``summary``, ``kpis``, ``table``, ``chart``, ``trend``,
``anomalies``, ``text``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from . import analysis
from .ingestion import DataSourceError, get_source
from .viz import CHART_TYPES

SECTION_TYPES = ("summary", "kpis", "table", "chart", "trend", "anomalies", "text")


class TemplateError(Exception):
    """Raised when a template is malformed."""


@dataclass
class Section:
    type: str
    title: str = ""
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportTemplate:
    name: str
    title: str
    description: str
    source: dict[str, Any]
    schema: dict[str, str]
    date_columns: list[str]
    sections: list[Section]


def builtin_dir() -> Path:
    return Path(str(resources.files("autoreport") / "templates_builtin"))


def list_templates(extra_dir: str | Path | None = None) -> list[dict[str, str]]:
    """Return name/title/description for every built-in (and extra) template."""
    found: list[dict[str, str]] = []
    dirs = [builtin_dir()] + ([Path(extra_dir)] if extra_dir else [])
    for d in dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.y*ml")):
            try:
                raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            found.append({
                "name": raw.get("name", p.stem),
                "title": raw.get("title", ""),
                "description": raw.get("description", ""),
                "path": str(p),
            })
    return found


def resolve_template_path(name_or_path: str, extra_dir: str | Path | None = None) -> Path:
    p = Path(name_or_path)
    if p.suffix in (".yaml", ".yml") and p.exists():
        return p
    for t in list_templates(extra_dir):
        if t["name"] == name_or_path:
            return Path(t["path"])
    raise TemplateError(f"Template '{name_or_path}' not found")


def load_template(name_or_path: str, extra_dir: str | Path | None = None) -> ReportTemplate:
    path = resolve_template_path(name_or_path, extra_dir)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise TemplateError(f"Invalid YAML in {path}: {exc}") from exc
    return parse_template(raw)


def parse_template(raw: Any) -> ReportTemplate:
    """Validate a parsed YAML mapping and build a ReportTemplate."""
    problems = validate_template(raw)
    if problems:
        raise TemplateError("; ".join(problems))
    sections = []
    for s in raw["sections"]:
        opts = {k: v for k, v in s.items() if k not in ("type", "title")}
        sections.append(Section(type=s["type"], title=s.get("title", ""), options=opts))
    return ReportTemplate(
        name=raw["name"], title=raw["title"], description=raw.get("description", ""),
        source=raw.get("source", {}), schema=raw.get("schema", {}) or {},
        date_columns=raw.get("date_columns", []) or [], sections=sections,
    )


def validate_template(raw: Any) -> list[str]:
    """Return a list of problems (empty list means the template is valid)."""
    if not isinstance(raw, dict):
        return ["Template must be a YAML mapping"]
    problems = [f"Missing required key '{k}'" for k in ("name", "title", "sections") if k not in raw]
    sections = raw.get("sections")
    if sections is not None and (not isinstance(sections, list) or not sections):
        problems.append("'sections' must be a non-empty list")
        sections = []
    for i, s in enumerate(sections or [], start=1):
        if not isinstance(s, dict) or "type" not in s:
            problems.append(f"Section {i}: missing 'type'")
            continue
        t = s["type"]
        if t not in SECTION_TYPES:
            problems.append(f"Section {i}: unknown type '{t}'")
        elif t == "chart" and s.get("chart", {}).get("type") not in CHART_TYPES:
            problems.append(f"Section {i}: chart.type must be one of {CHART_TYPES}")
        elif t == "kpis" and not s.get("items"):
            problems.append(f"Section {i}: 'kpis' needs 'items'")
        elif t in ("trend", "anomalies") and "column" not in s and "value" not in s:
            problems.append(f"Section {i}: '{t}' needs 'column' (or 'value')")
    return problems


def load_data(tpl: ReportTemplate, data_path: str | None = None) -> pd.DataFrame:
    """Load the data for a template, allowing a CLI override of the file."""
    src = dict(tpl.source)
    location = data_path or src.pop("path", None)
    src.pop("path", None)
    if not location:
        raise DataSourceError("No data source: pass --data or set source.path in the template")
    df = get_source(str(location), **src).load(
        schema=tpl.schema or None, date_columns=tpl.date_columns or None)
    if df.empty:
        raise DataSourceError("The data source contains no rows")
    return df


# ---------------------------------------------------------------------------
# Pipeline: turn template + data into a render-ready structure
# ---------------------------------------------------------------------------

_KPI_AGGS = {"sum", "mean", "median", "count", "min", "max", "nunique"}


def _fmt(v: Any, fmt: str = "") -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    if fmt == "currency":
        return f"${v:,.0f}"
    if fmt == "percent":
        return f"{v:,.1f}%"
    if isinstance(v, float):
        return f"{v:,.2f}"
    return f"{v:,}" if isinstance(v, int) else str(v)


def _table_payload(df: pd.DataFrame, max_rows: int = 25) -> dict:
    d = df.head(max_rows).copy()
    for c in d.columns:
        if pd.api.types.is_datetime64_any_dtype(d[c]):
            d[c] = d[c].dt.strftime("%Y-%m-%d")
    return {"columns": [str(c) for c in d.columns],
            "rows": [[_fmt(v) if isinstance(v, float) else v for v in r] for r in d.values.tolist()]}


def build_report_data(tpl: ReportTemplate, df: pd.DataFrame) -> list[dict[str, Any]]:
    """Run each section's analysis and return render-ready dictionaries."""
    out: list[dict[str, Any]] = []
    for sec in tpl.sections:
        o = sec.options
        item: dict[str, Any] = {"type": sec.type, "title": sec.title}
        if sec.type == "text":
            item["text"] = o.get("text", "")
        elif sec.type == "kpis":
            kpis = []
            for k in o["items"]:
                agg = k.get("agg", "sum")
                if agg not in _KPI_AGGS:
                    raise TemplateError(f"Unknown KPI aggregation '{agg}'")
                val = getattr(df[k["column"]], agg)()
                val = val.item() if hasattr(val, "item") else val
                kpis.append({"label": k["label"], "value": _fmt(val, k.get("format", ""))})
            item["kpis"] = kpis
        elif sec.type == "summary":
            stats = analysis.summary_stats(df, o.get("columns"))
            item["table"] = _table_payload(stats.reset_index().rename(columns={"index": "column"}))
        elif sec.type == "table":
            if "group_by" in o:
                res = analysis.group_aggregate(df, o["group_by"], o["value"], o.get("aggs"))
            else:
                res = df[o["columns"]] if o.get("columns") else df
                if o.get("sort_by"):
                    res = res.sort_values(o["sort_by"], ascending=o.get("ascending", False))
            item["table"] = _table_payload(res, o.get("limit", 25))
        elif sec.type == "chart":
            item["chart"] = o["chart"]
        elif sec.type == "trend":
            col = o.get("column") or o["value"]
            s = analysis.resample_series(df, o["date"], col, o.get("freq", "ME"),
                                         o.get("agg", "sum"), o.get("drop_partial", True))
            ma = analysis.moving_average(s, o.get("window", 3))
            info = analysis.trend_direction(s)
            growth = analysis.overall_growth(s)
            trend_df = pd.DataFrame({o["date"]: s.index, col: s.values,
                                     "moving_avg": ma.values.round(2)})
            item["trend_df"] = trend_df
            item["chart"] = {"type": "line", "x": o["date"], "y": col,
                             "title": o.get("title") or f"{col} over time"}
            item["narrative"] = (
                f"{col} shows {'an' if info['direction'][0] in 'ui' else 'a'} {info['direction']} "
                f"trend (R-squared = {info['r2']})"
                + (f", {'up' if growth >= 0 else 'down'} {abs(growth):.1f}% from first to last period."
                   if growth is not None else ".")
            )
        elif sec.type == "anomalies":
            col = o.get("column") or o["value"]
            method = o.get("method", "zscore")
            flagged = analysis.flag_anomalies(df, col, method, o.get("threshold"))
            cols = o.get("show") or list(df.columns)[:6]
            item["table"] = _table_payload(flagged[cols], 15)
            item["narrative"] = (
                f"{len(flagged)} of {len(df):,} records flagged as anomalous in '{col}' "
                f"using the {'Z-score' if method == 'zscore' else 'IQR'} method."
            )
        out.append(item)
    return out
