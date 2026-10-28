import time

import pytest

from autoreport.scheduler import build_trigger, create_scheduler, make_job, send_email


def test_trigger_validation():
    assert build_trigger(cron="0 8 * * 1") is not None
    assert build_trigger(every_minutes=5) is not None
    with pytest.raises(ValueError):
        build_trigger()
    with pytest.raises(ValueError):
        build_trigger(cron="* * * * *", every_minutes=1)
    with pytest.raises(ValueError):
        build_trigger(cron="bad cron")
    with pytest.raises(ValueError):
        build_trigger(every_minutes=-5)


def test_job_generates_files(tmp_path, csv_file, small_template):
    files = make_job(str(small_template), str(csv_file), str(tmp_path), "html")()
    assert files and files[0].exists()


def test_job_swallows_errors(tmp_path):
    assert make_job("nonexistent", None, str(tmp_path), "html")() == []


def test_background_scheduler_fires(tmp_path, csv_file, small_template):
    from apscheduler.triggers.interval import IntervalTrigger

    calls = []
    job = make_job(str(small_template), str(csv_file), str(tmp_path), "html", on_done=calls.append)
    sched = create_scheduler(job, IntervalTrigger(seconds=1), blocking=False)
    sched.start()
    try:
        time.sleep(2.5)
    finally:
        sched.shutdown(wait=False)
    assert len(calls) >= 1


def test_send_email_mocked(tmp_path, monkeypatch):
    import smtplib

    f_html = tmp_path / "report.html"
    f_html.write_text("<h1>Report</h1>", encoding="utf-8")
    f_pdf = tmp_path / "report.pdf"
    f_pdf.write_bytes(b"%PDF-1.4...")

    sent_messages = []
    actions = []

    class MockSMTP:
        def __init__(self, host, port):
            actions.append(("init", host, port))

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            actions.append(("quit",))

        def starttls(self):
            actions.append(("starttls",))

        def login(self, user, password):
            actions.append(("login", user, password))

        def send_message(self, msg):
            sent_messages.append(msg)

    monkeypatch.setattr(smtplib, "SMTP", MockSMTP)

    send_email([f_html, f_pdf], "test@example.com", "smtp.test.com", 587,
               user="user@test.com", password="secretpassword")

    assert len(sent_messages) == 1
    msg = sent_messages[0]
    assert msg["To"] == "test@example.com"
    assert msg["From"] == "user@test.com"
    assert ("starttls",) in actions
    assert ("login", "user@test.com", "secretpassword") in actions
    assert len(msg.get_payload()) == 3  # text body + 2 attachments

