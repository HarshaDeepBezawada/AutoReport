"""High-level orchestration: template + data -> HTML/PDF files."""

from __future__ import annotations

from pathlib import Path

from .builders import build_html, build_pdf
from .template import build_report_data, load_data, load_template

FORMATS = ("html", "pdf", "both")


def generate_report(template: str, data: str | None = None, output_dir: str | Path = "reports",
                    fmt: str = "both", basename: str | None = None,
                    template_dir: str | Path | None = None) -> list[Path]:
    """Generate one or more report files and return their paths."""
    if fmt not in FORMATS:
        raise ValueError(f"format must be one of {FORMATS}")
    tpl = load_template(template, template_dir)
    df = load_data(tpl, data)
    sections = build_report_data(tpl, df)
    out_dir = Path(output_dir)
    name = basename or tpl.name
    produced: list[Path] = []
    if fmt in ("html", "both"):
        produced.append(build_html(tpl.title, tpl.description, sections, df, out_dir / f"{name}.html"))
    if fmt in ("pdf", "both"):
        produced.append(build_pdf(tpl.title, tpl.description, sections, df, out_dir / f"{name}.pdf"))
    return produced
