# AutoReport — Project Demonstration & Video Evidence

**Internship Organization**: Code A Nova (15-Day Python Development Internship)  
**Presenter**: Harshadeep Bezawada  
**Project**: AutoReport — Automated Report & Analytics Generator  

---

## 1. Video Demonstration Recording

- **Official Video Link**: [AutoReport 5-Minute Demonstration Video (Google Drive)](https://drive.google.com/file/d/1oPhKqFStkFfacsF1el7Nq7Sai8XLWLgj/view?usp=drive_link)
- **Presenter**: Harshadeep Bezawada
- **Duration**: ~5 minutes
- **Resolution**: 1080p Full HD

> ### ⚠️ Browser Compatibility & Playback Notice
> If the Google Drive video preview does not load or stream directly in your current browser, please open the link in a **different web browser** (such as Google Chrome, Microsoft Edge, or Mozilla Firefox) or click the **Download** button on Google Drive to view the video file locally.

---

## 2. Key Capabilities Demonstrated in the Video

The 5-minute evaluation video walks through the complete end-to-end functionality of AutoReport in a live terminal and browser session:

| Step | Action / Feature | Command / Evidence | Description |
|:---:|:---|:---|:---|
| **1** | **Data Generation** | `python scripts/make_sample_data.py` | Generates realistic synthetic multi-domain datasets (Sales CSV, HR Excel, Inventory JSON & SQLite) with planted statistical anomalies. |
| **2** | **Template Discovery** | `autoreport list-templates` | Inspects and displays all registered declarative YAML templates (`sales`, `hr`, `inventory`) in a formatted table. |
| **3** | **Pre-flight Validation** | `autoreport validate sales` | Verifies YAML syntax, section specifications, metric definitions, and dataset column schema before generation. |
| **4** | **Dual Report Generation** | `autoreport generate sales` | Concurrently builds both an interactive, zero-dependency offline **HTML report** (with embedded Plotly.js) and a paginated **PDF report** (with ReportLab). |
| **5** | **Report Artifact Inspection** | `sample_reports/sales.html`<br>`sample_reports/sales.pdf` | Inspects executive narrative summaries, KPI metric cards, comparative period/segment benchmarks, and interactive/static charts. |
| **6** | **Multi-Source Ingestion** | `autoreport generate hr -f pdf`<br>`autoreport generate inventory --data data/inventory.db` | Demonstrates the Adapter Pattern loading Excel workbooks (`.xlsx`) and SQLite relational databases seamlessly without code alterations. |
| **7** | **Test Rigor & Coverage** | `python -m pytest -v --cov=autoreport` | Runs the comprehensive Pytest suite: **59 tests passed, 100% line coverage** (821 / 821 statements) across all modules. |
| **8** | **High-Scale Benchmark** | `python scripts/verify_performance.py` | Ingests, analyzes, and renders 100,000 records in **2.53 seconds** (well below the 30-second budget). |

---

## 3. Pre-Generated Deliverables

The generated demonstration reports from this video are committed directly in the repository for immediate offline evaluation:
- [Sales Report (HTML)](../sample_reports/sales.html) | [Sales Report (PDF)](../sample_reports/sales.pdf)
- [HR Report (HTML)](../sample_reports/hr.html) | [HR Report (PDF)](../sample_reports/hr.pdf)
- [Inventory Report (HTML)](../sample_reports/inventory.html) | [Inventory Report (PDF)](../sample_reports/inventory.pdf)
