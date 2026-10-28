"""HTML report builder (Jinja2 + embedded charts)."""

from __future__ import annotations

from datetime import datetime
from importlib import resources
from pathlib import Path
from typing import Any

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..viz import make_plotly_chart, make_static_chart, png_to_data_uri


def _env() -> Environment:
    folder = str(resources.files("autoreport") / "builders")
    return Environment(loader=FileSystemLoader(folder),
                       autoescape=select_autoescape(["html"]))


def prepare_sections(sections: list[dict[str, Any]], df: pd.DataFrame,
                     interactive: bool) -> list[dict[str, Any]]:
    """Attach rendered chart HTML (Plotly) or PNG data URIs to each section."""
    prepared: list[dict[str, Any]] = []
    for s in sections:
        s = dict(s)
        if "chart" in s:
            data = s.get("trend_df", df)
            spec = s["chart"]
            if interactive:
                fig = make_plotly_chart(data, spec)
                s["chart_html"] = fig.to_html(full_html=False, include_plotlyjs=False)
            else:
                s["chart_img"] = png_to_data_uri(make_static_chart(data, spec))
        prepared.append(s)
    return prepared


def build_html(title: str, description: str, sections: list[dict[str, Any]],
               df: pd.DataFrame, output: str | Path, interactive: bool = True,
               offline: bool = True) -> Path:
    """Render the report to ``output`` and return its path.

    When ``offline=True``, Plotly.js is embedded inline for 100% offline usage.
    """
    prepared = prepare_sections(sections, df, interactive)
    plotly_js = ""
    if interactive and offline:
        import plotly.offline as po
        plotly_js = po.get_plotlyjs()

    html = _env().get_template("report.html").render(
        title=title, description=description, sections=prepared, interactive=interactive,
        offline=offline, plotly_js=plotly_js,
        generated=datetime.now().strftime("%Y-%m-%d %H:%M"), n_rows=f"{len(df):,}",
    )
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
