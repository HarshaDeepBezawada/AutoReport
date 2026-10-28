"""Command-line interface: generate, validate, list-templates, schedule."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer
import yaml

from . import __version__
from .generator import generate_report
from .ingestion import DataSourceError
from .scheduler import build_trigger, create_scheduler, make_job, send_email
from .template import (
    TemplateError,
    list_templates as _list_templates,
    load_data,
    load_template,
    resolve_template_path,
    validate_template,
)
from .viz import ChartError

app = typer.Typer(help="AutoReport - automated report & analytics generator.",
                  no_args_is_help=True, add_completion=False)


def _fail(msg: str) -> "typer.Exit":
    typer.secho(f"Error: {msg}", fg=typer.colors.RED, err=True)
    return typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def main(version: bool = typer.Option(False, "--version", "-V", help="Show version and exit.")) -> None:
    if version:
        typer.echo(f"autoreport {__version__}")
        raise typer.Exit()


@app.command()
def generate(
    template: str = typer.Argument(..., help="Template name (see list-templates) or path to a .yaml file."),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Data file or URL (overrides the template)."),
    output: Path = typer.Option(Path("reports"), "--output", "-o", help="Output directory."),
    fmt: str = typer.Option("both", "--format", "-f", help="html, pdf or both."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Base file name for the report."),
    template_dir: Optional[Path] = typer.Option(None, "--template-dir", help="Extra folder of templates."),
    offline: bool = typer.Option(True, "--offline/--online", help="Embed Plotly.js directly for 100% offline viewing without internet."),
) -> None:
    """Generate a report once."""
    try:
        files = generate_report(template, data, output, fmt, name, template_dir, offline=offline)
    except (TemplateError, DataSourceError, ChartError, ValueError, KeyError) as exc:
        raise _fail(str(exc))
    for f in files:
        typer.secho(f"Created {f}", fg=typer.colors.GREEN)


@app.command()
def validate(
    template: str = typer.Argument(..., help="Template name or path."),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Also load this data and check the schema."),
    template_dir: Optional[Path] = typer.Option(None, "--template-dir"),
) -> None:
    """Check a template (and optionally its data) without producing a report."""
    try:
        path = resolve_template_path(template, template_dir)
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (TemplateError, yaml.YAMLError) as exc:
        raise _fail(str(exc))
    problems = validate_template(raw)
    if problems:
        for p in problems:
            typer.secho(f"  - {p}", fg=typer.colors.RED, err=True)
        raise _fail(f"{path} has {len(problems)} problem(s)")
    if data or raw.get("source", {}).get("path"):
        try:
            tpl = load_template(str(path))
            df = load_data(tpl, data)
            typer.echo(f"Data OK: {len(df):,} rows, {len(df.columns)} columns")
        except (TemplateError, DataSourceError) as exc:
            raise _fail(str(exc))
    typer.secho(f"Template '{raw['name']}' is valid ({len(raw['sections'])} sections).",
                fg=typer.colors.GREEN)


@app.command("list-templates")
def list_templates(template_dir: Optional[Path] = typer.Option(None, "--template-dir")) -> None:
    """List available report templates."""
    items = _list_templates(template_dir)
    if not items:
        typer.echo("No templates found.")
        return
    for t in items:
        typer.secho(f"{t['name']:<12}", fg=typer.colors.CYAN, nl=False)
        typer.echo(f" {t['title']} - {t['description']}")


@app.command()
def schedule(
    template: str = typer.Argument(..., help="Template name or path."),
    data: Optional[str] = typer.Option(None, "--data", "-d"),
    output: Path = typer.Option(Path("reports"), "--output", "-o"),
    fmt: str = typer.Option("both", "--format", "-f"),
    cron: Optional[str] = typer.Option(None, "--cron", help="5-field cron, e.g. '0 8 * * 1' (Mondays 08:00)."),
    every: Optional[int] = typer.Option(None, "--every", help="Run every N minutes."),
    run_now: bool = typer.Option(True, "--run-now/--no-run-now", help="Generate once immediately."),
    email_to: Optional[str] = typer.Option(None, "--email-to", help="Email the report to this address."),
    smtp_host: str = typer.Option("localhost", "--smtp-host"),
    smtp_port: int = typer.Option(587, "--smtp-port"),
    offline: bool = typer.Option(True, "--offline/--online", help="Embed Plotly.js for offline viewing."),
) -> None:
    """Run the report on a schedule (Ctrl+C to stop)."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    try:
        trigger = build_trigger(cron, every)
        load_template(template)  # fail fast on bad templates
    except (ValueError, TemplateError) as exc:
        raise _fail(str(exc))
    on_done = (lambda files: send_email(files, email_to, smtp_host, smtp_port)) if email_to else None
    job = make_job(template, data, str(output), fmt, on_done, offline=offline)
    if run_now:
        job()
    sched = create_scheduler(job, trigger, blocking=True)
    typer.echo("Scheduler started. Press Ctrl+C to stop.")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        typer.echo("Scheduler stopped.")


if __name__ == "__main__":
    app()
