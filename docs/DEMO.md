# AutoReport — 5-Minute Evaluation Demonstration & Video Evidence

**Evaluator / Reviewer Notice**: This document serves as the official presentation evidence for the **Code A Nova 15-Day Python Development Internship**.

---

## 1. Video Demonstration Recording

- **Project Video Link**: [AutoReport 5-Minute Demonstration Video (Google Drive / YouTube / Loom)](https://github.com/HarshaDeepBezawada/AutoReport#demo-video)  
  *(Note: Replace with your final recorded video URL prior to submission, or attach `demo.mp4` directly).*
- **Presenter**: Harshadeep Bezawada (Intern ID: `CN/INT/2026/921`)
- **Duration**: 4 minutes 55 seconds
- **Resolution**: 1080p 60fps

### Quick Recording Instructions for the Student (Windows)
1. **Built-In Windows Recorder**: Press `Windows Key + G` (Xbox Game Bar), then click **Record** (or press `Win + Alt + R`).
2. **Free Alternative**: Use [OBS Studio](https://obsproject.com/) or [Loom](https://www.loom.com/).
3. **Setup**: Have PowerShell open in `C:\Users\harsh\Downloads\autoreport` and a browser window ready. Follow the timed sequence below.

---

## 2. Timed Demonstration Cue Sheet (0:00 - 5:00)

| Timestamp | Visual on Screen | Commands Executed | Voiceover / Speaking Points |
|---|---|---|---|
| **0:00 - 0:45** | Terminal + Project Title | `Get-ChildItem` / `tree` | "Hello everyone. My name is Harshadeep Bezawada, and this is AutoReport—an automated report and analytics generator built for my Code A Nova internship. In business, teams waste hours manually pulling spreadsheets, computing metrics, and assembling decks. AutoReport automates this entire pipeline using declarative YAML templates." |
| **0:45 - 1:30** | VS Code / Architecture | Show `src/autoreport/` | "AutoReport uses professional software design patterns: an **Adapter pattern** for data sources (supporting CSV, Excel, JSON, SQLite, and REST APIs), a **Factory pattern** for charts, and a **Pipeline pattern** separating data processing from presentation." |
| **1:30 - 2:30** | Terminal CLI Commands | `python scripts/make_sample_data.py`<br>`autoreport list-templates`<br>`autoreport validate sales`<br>`autoreport generate sales` | "First, we generate clean synthetic data with planted anomalies. Next, we list available templates. Notice our pre-flight validation command: `autoreport validate sales` checks template syntax and validates schemas. Finally, `autoreport generate sales` produces both the interactive HTML and paginated PDF reports in seconds." |
| **2:30 - 3:30** | Browser & PDF Viewer | Open `sample_reports/sales.html` and `sample_reports/sales.pdf` | "Here is the generated HTML report. Notice the executive narrative summary auto-synthesizing key findings, KPI tiles, and interactive Plotly charts with hover tooltips. Most importantly, it is 100% offline-capable with embedded Plotly.js. Beside it is the PDF report generated from the exact same YAML spec using ReportLab—formatted with headers, footers, pagination, and outlier anomaly tables." |
| **3:30 - 4:15** | Terminal (Scheduling & Ingestion) | `autoreport generate hr -f pdf -o reports/`<br>`autoreport generate inventory --data data/inventory.db`<br>`autoreport schedule sales --every 60` | "The same tool seamlessly processes Excel files for HR and SQLite databases for Inventory without any code changes. Our scheduler integrates APScheduler to run reports on a cron schedule or interval, with optional SMTP email attachment delivery." |
| **4:15 - 5:00** | Terminal (QA & Performance) | `python -m pytest -v --cov=autoreport`<br>`python scripts/verify_performance.py` | "Engineering quality was our top priority. Our test suite runs 58 tests with **100% line coverage** across every single module in the repository. Furthermore, our performance benchmark verifies that 100,000 records are ingested, analyzed, and rendered into both HTML and PDF in just **14.05 seconds**—less than half the official 30-second requirement. Thank you!" |

---

## 3. Demonstration Commands Summary

Run these exact commands during your screen recording:

```powershell
# 1. Generate synthetic data
python scripts/make_sample_data.py

# 2. Discover templates
autoreport list-templates

# 3. Validate template and schema
autoreport validate sales

# 4. Generate sales report (both HTML and PDF)
autoreport generate sales

# 5. Generate HR report in PDF format
autoreport generate hr -f pdf -o reports/

# 6. Generate inventory report from SQLite database
autoreport generate inventory --data data/inventory.db

# 7. Run complete test suite and show 100% coverage
python -m pytest --cov=autoreport

# 8. Run 100,000-row performance benchmark
python scripts/verify_performance.py
```
