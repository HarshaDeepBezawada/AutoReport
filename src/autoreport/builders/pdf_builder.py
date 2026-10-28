"""PDF report builder using ReportLab (pure Python, cross-platform)."""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from xml.sax.saxutils import escape

from ..viz import make_static_chart

BLUE = colors.HexColor("#2F6FED")
LIGHT = colors.HexColor("#F3F4F8")
GRID = colors.HexColor("#E5E7EB")


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=base["Title"], fontSize=24, leading=30, textColor=BLUE,
                                alignment=0, spaceAfter=6),
        "sub": ParagraphStyle("s", parent=base["Normal"], textColor=colors.grey, fontSize=10),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], textColor=colors.HexColor("#1f2937"),
                             spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("b", parent=base["BodyText"], fontSize=10, leading=14),
        "cell": ParagraphStyle("c", parent=base["BodyText"], fontSize=8, leading=10),
    }


def _table(payload: dict, width: float, st: dict) -> Table:
    if not payload.get("columns"):
        return Table([[""]])
    header = [Paragraph(f"<b>{escape(str(c))}</b>", st["cell"]) for c in payload["columns"]]
    rows = [[Paragraph(escape(str(v)), st["cell"]) for v in r] for r in payload["rows"]]
    t = Table([header] + rows, colWidths=[width / len(header)] * len(header), repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFBFF")]),
    ]))
    return t


def _kpi_table(kpis: list[dict], width: float, st: dict) -> Table:
    if not kpis:
        return Table([[""]])
    cells = [[Paragraph(f"<font size=8 color='#6b7280'>{escape(k['label'].upper())}</font><br/>"
                        f"<font size=16 color='#2F6FED'><b>{escape(k['value'])}</b></font>", st["body"])
              for k in kpis[:4]]]
    t = Table(cells, colWidths=[width / len(cells[0])] * len(cells[0]))
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, GRID), ("INNERGRID", (0, 0), (-1, -1), 0.5, GRID),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFBFF")),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def _footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Created with AutoReport")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(title: str, description: str, sections: list[dict[str, Any]],
              df: pd.DataFrame, output: str | Path) -> Path:
    """Render the report to a PDF file and return its path."""
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm, title=title, author="AutoReport")
    width = A4[0] - 4 * cm
    st = _styles()
    story: list = [
        Paragraph(escape(title), st["title"]),
        Paragraph(escape(f"{description}  |  Generated {datetime.now():%Y-%m-%d %H:%M}  |  "
                         f"{len(df):,} records"), st["sub"]),
        Spacer(1, 10),
    ]
    for s in sections:
        block: list = []  # heading + first content kept together to avoid orphaned headings
        if s.get("title"):
            block.append(Paragraph(escape(s["title"]), st["h2"]))
        if s.get("text"):
            block.append(Paragraph(escape(s["text"]), st["body"]))
        if s.get("narrative"):
            block.append(Paragraph(escape(s["narrative"]), st["body"]))
            block.append(Spacer(1, 4))
        if s.get("kpis"):
            block.append(_kpi_table(s["kpis"], width, st))
        if "chart" in s:
            data = s.get("trend_df", df)
            png = make_static_chart(data, s["chart"])
            block.append(Image(io.BytesIO(png), width=width, height=width * 4 / 7))
        if s.get("table"):
            tbl = _table(s["table"], width, st)
            if "chart" in s:
                block.append(Spacer(1, 4))
                block.append(tbl)
            else:
                # long tables may split across pages, so only the heading stays with it
                block.append(Spacer(1, 2))
                story.append(KeepTogether(block + [tbl]) if len(s["table"]["rows"]) <= 12
                             else KeepTogether(block))
                if len(s["table"]["rows"]) > 12:
                    story.append(tbl)
                story.append(Spacer(1, 8))
                continue
        story.append(KeepTogether(block))
        story.append(Spacer(1, 8))
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return out
