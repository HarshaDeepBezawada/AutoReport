"""Chart factory: static Matplotlib/Seaborn PNGs and interactive Plotly figures.

``make_static_chart`` and ``make_plotly_chart`` take the same chart spec
(a dict from the YAML template) so both report formats stay in sync.
"""

from __future__ import annotations

import base64
import io
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")  # headless / cross-platform
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import seaborn as sns  # noqa: E402

PALETTE = ["#2F6FED", "#F2994A", "#27AE60", "#EB5757", "#9B51E0", "#56CCF2", "#F2C94C"]
CHART_TYPES = ("bar", "line", "pie", "scatter", "heatmap", "histogram")


class ChartError(Exception):
    """Raised for invalid chart specifications."""


def _need(spec: dict, *keys: str) -> None:
    missing = [k for k in keys if k not in spec]
    if missing:
        raise ChartError(f"Chart '{spec.get('type')}' needs: {', '.join(missing)}")


def _need_col(df: pd.DataFrame, *cols: str | None) -> None:
    for c in cols:
        if c and c not in df.columns:
            raise ChartError(f"Column '{c}' not found in data for chart")


def _prepare(df: pd.DataFrame, spec: dict[str, Any]) -> pd.DataFrame:
    """Aggregate data for charts that need ``agg`` (bar/line/pie)."""
    ctype = spec["type"]
    if ctype in ("bar", "pie") and "agg" in spec:
        _need(spec, "x", "y")
        out = df.groupby(spec["x"])[spec["y"]].agg(spec["agg"]).reset_index()
        out = out.sort_values(spec["y"], ascending=False)
        if spec.get("limit"):
            out = out.head(int(spec["limit"]))
        return out
    if ctype == "line" and "agg" in spec:
        _need(spec, "x", "y")
        out = df.groupby(pd.Grouper(key=spec["x"], freq=spec.get("freq", "ME")))[spec["y"]] \
            .agg(spec["agg"]).reset_index()
        return out
    return df


def _bar(ax, df, spec):
    _need(spec, "x", "y")
    _need_col(df, spec["x"], spec["y"])
    sns.barplot(data=df, x=spec["x"], y=spec["y"], color=PALETTE[0], ax=ax)
    ax.tick_params(axis="x", rotation=30)


def _line(ax, df, spec):
    _need(spec, "x", "y")
    _need_col(df, spec["x"], spec["y"])
    sns.lineplot(data=df, x=spec["x"], y=spec["y"], color=PALETTE[0], marker="o", ax=ax)
    ax.tick_params(axis="x", rotation=30)


def _pie(ax, df, spec):
    _need(spec, "x", "y")
    _need_col(df, spec["x"], spec["y"])
    vals = pd.to_numeric(df[spec["y"]], errors="coerce").fillna(0)
    if vals.sum() <= 0:
        raise ChartError(f"Cannot generate pie chart: values in '{spec['y']}' must sum to a positive number")
    ax.pie(vals, labels=df[spec["x"]], autopct="%1.1f%%",
           colors=PALETTE, startangle=90)
    ax.axis("equal")


def _scatter(ax, df, spec):
    _need(spec, "x", "y")
    _need_col(df, spec["x"], spec["y"], spec.get("hue"))
    hue = spec.get("hue")
    palette = PALETTE[: max(df[hue].nunique(), 1)] if hue else None
    sns.scatterplot(data=df, x=spec["x"], y=spec["y"], hue=hue, palette=palette,
                    color=None if hue else PALETTE[0], ax=ax)
    if hue:
        ax.legend(loc="upper right", framealpha=0.8)


def _heatmap(ax, df, spec):
    cols = spec.get("columns")
    if cols:
        _need_col(df, *cols)
        num = df[cols]
    else:
        num = df.select_dtypes("number")
    if num.shape[1] < 2:
        raise ChartError("Heatmap needs at least two numeric columns")
    corr = num.corr().fillna(0)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)


def _hist(ax, df, spec):
    _need(spec, "x")
    _need_col(df, spec["x"])
    sns.histplot(data=df, x=spec["x"], bins=spec.get("bins", 20), color=PALETTE[0], ax=ax)


_STATIC: dict[str, Callable] = {
    "bar": _bar, "line": _line, "pie": _pie,
    "scatter": _scatter, "heatmap": _heatmap, "histogram": _hist,
}


def _check_type(spec: dict) -> None:
    if spec.get("type") not in CHART_TYPES:
        raise ChartError(f"Unknown chart type '{spec.get('type')}'. Use one of {CHART_TYPES}")


def make_static_chart(df: pd.DataFrame, spec: dict[str, Any]) -> bytes:
    """Render a chart spec to PNG bytes using Matplotlib/Seaborn."""
    _check_type(spec)
    data = _prepare(df, spec)
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4), dpi=130)
    try:
        _STATIC[spec["type"]](ax, data, spec)
        if spec["type"] in ("bar", "line", "scatter", "histogram"):
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.set_title(spec.get("title", ""), fontsize=12, fontweight="bold")
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        return buf.getvalue()
    finally:
        plt.close(fig)


def png_to_data_uri(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode()


def make_plotly_chart(df: pd.DataFrame, spec: dict[str, Any]) -> go.Figure:
    """Build an interactive Plotly figure from the same chart spec."""
    _check_type(spec)
    data = _prepare(df, spec)
    t, title = spec["type"], spec.get("title", "")
    colors = PALETTE
    if t == "bar":
        _need(spec, "x", "y")
        _need_col(data, spec["x"], spec["y"])
        fig = px.bar(data, x=spec["x"], y=spec["y"], title=title, color_discrete_sequence=colors)
    elif t == "line":
        _need(spec, "x", "y")
        _need_col(data, spec["x"], spec["y"])
        fig = px.line(data, x=spec["x"], y=spec["y"], title=title, markers=True,
                      color_discrete_sequence=colors)
    elif t == "pie":
        _need(spec, "x", "y")
        _need_col(data, spec["x"], spec["y"])
        fig = px.pie(data, names=spec["x"], values=spec["y"], title=title,
                     color_discrete_sequence=colors)
    elif t == "scatter":
        _need(spec, "x", "y")
        _need_col(data, spec["x"], spec["y"], spec.get("hue"))
        fig = px.scatter(data, x=spec["x"], y=spec["y"], color=spec.get("hue"), title=title,
                         color_discrete_sequence=colors)
    elif t == "heatmap":
        cols = spec.get("columns")
        if cols:
            _need_col(data, *cols)
            num = data[cols]
        else:
            num = data.select_dtypes("number")
        if num.shape[1] < 2:
            raise ChartError("Heatmap needs at least two numeric columns")
        fig = px.imshow(num.corr().fillna(0).round(2), text_auto=True, title=title,
                        color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    else:  # histogram
        _need(spec, "x")
        _need_col(data, spec["x"])
        fig = px.histogram(data, x=spec["x"], nbins=spec.get("bins", 20), title=title,
                           color_discrete_sequence=colors)
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=20, t=50, b=40))
    return fig
