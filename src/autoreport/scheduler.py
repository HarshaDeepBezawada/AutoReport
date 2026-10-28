"""Recurring report generation with APScheduler (+ optional email delivery)."""

from __future__ import annotations

import logging
import smtplib
from collections.abc import Callable
from email.message import EmailMessage
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .generator import generate_report

log = logging.getLogger("autoreport.scheduler")


def build_trigger(cron: str | None = None, every_minutes: int | None = None):
    """Create a trigger from a 5-field cron string or an interval in minutes."""
    if cron and every_minutes:
        raise ValueError("Use either a cron expression or an interval, not both")
    if cron:
        return CronTrigger.from_crontab(cron)
    if every_minutes:
        if every_minutes < 1:
            raise ValueError("Interval must be at least 1 minute")
        return IntervalTrigger(minutes=every_minutes)
    raise ValueError("Provide a cron expression or an interval")


def send_email(files: list[Path], to_addr: str, smtp_host: str, smtp_port: int = 587,
               user: str | None = None, password: str | None = None) -> None:
    """Email generated reports as attachments (needs a real SMTP server)."""
    msg = EmailMessage()
    msg["Subject"] = "AutoReport: scheduled report"
    msg["From"] = user or "autoreport@localhost"
    msg["To"] = to_addr
    msg.set_content("Your scheduled report is attached.")
    for f in files:
        subtype = "pdf" if f.suffix == ".pdf" else "html"
        msg.add_attachment(f.read_bytes(), maintype="application", subtype=subtype, filename=f.name)
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        if user and password:
            server.login(user, password)
        server.send_message(msg)


def make_job(template: str, data: str | None, output_dir: str, fmt: str,
             on_done: Callable[[list[Path]], None] | None = None,
             offline: bool = True) -> Callable[[], list[Path]]:
    """Return a callable that generates the report (used as the scheduled job)."""
    def job() -> list[Path]:
        try:
            files = generate_report(template, data, output_dir, fmt, offline=offline)
            log.info("Generated: %s", ", ".join(str(f) for f in files))
            if on_done:
                on_done(files)
            return files
        except Exception:  # keep the scheduler alive on failures
            log.exception("Scheduled report failed")
            return []
    return job


def create_scheduler(job: Callable, trigger, blocking: bool = True):
    """Register ``job`` on a new scheduler (blocking for CLI, background for tests)."""
    sched = BlockingScheduler() if blocking else BackgroundScheduler()
    sched.add_job(job, trigger, id="autoreport", max_instances=1, coalesce=True)
    return sched
