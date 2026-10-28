# AutoReport — Automated Report & Analytics Generator

[![Build & Tests](https://github.com/HarshaDeepBezawada/AutoReport/actions/workflows/ci.yml/badge.svg)](https://github.com/HarshaDeepBezawada/AutoReport/actions)
[![Coverage](https://img.shields.io/badge/Coverage-100%25%20(821%2F821)-brightgreen.svg)](#7-testing--code-coverage)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](pyproject.toml)
[![Cross-Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#3-technology-stack)

AutoReport is a production-grade, CLI-driven report automation and analytics generator developed in Python. It ingests data across diverse formats (CSV, Excel, JSON, SQLite, REST API), performs rigorous statistical, trend, and anomaly analysis, creates publication-quality visualizations, and produces responsive **HTML** (with interactive, zero-dependency offline Plotly figures) and paginated **PDF** reports (with ReportLab and static charts) driven entirely by declarative YAML templates.

Developed for the **Code A Nova 15-Day Python Development Internship**.

---

## 1. Problem Statement & Architecture

Organizations and data teams repeatedly waste hundreds of hours manually pulling data, recomputing summary statistics, calculating rolling trends, identifying anomalies, plotting charts, and assembling weekly or monthly slide decks. 

**AutoReport** solves this by establishing a reusable, configurable automation pipeline:
- **Declarative YAML Templates**: Add or customize reports by writing YAML specifications, not Python code.
- **Unified Adapter Pattern**: All data sources inherit from a shared `DataSource` abstraction with schema validation.
- **Dual-Renderer Visualization Factory**: A single chart specification drives both interactive Plotly figures for web reports and Matplotlib/Seaborn vector/raster plots for PDF documents.
- **Executive Narratives & Comparative Analysis**: Automatically calculates period-over-period and segment-over-segment benchmarks with plain-English business narratives.
- **Offline Self-Contained HTML**: Zero-dependency offline HTML reports bundle Plotly.js directly for viewing in secure, air-gapped corporate environments.
- **Integrated Scheduling & Delivery**: Autonomous recurring report runs using APScheduler (cron & interval) with optional email distribution.

```
                              ┌─────────────────────────┐
                              │     Data Sources        │
                              │ CSV / XLSX / JSON / SQL │
                              │     REST Endpoints      │
                              └────────────┬────────────┘
                                           │ (Adapter Pattern)
                                           ▼
┌────────────────────────┐    ┌─────────────────────────┐
│     Report Template    │───►│      AutoReport         │
│  YAML (Sections, KPIs, │    │    Pipeline Engine      │
│  Charts, Anomalies)    │    └────────────┬────────────┘
└────────────────────────┘                 │
                                           ├──────────────────────────┐
                                           ▼                          ▼
                              ┌─────────────────────────┐┌─────────────────────────┐
                              │      HTML Builder       ││       PDF Builder       │
                              │ (Jinja2 + Offline Plotly)││ (ReportLab + Matplotlib)
                              └────────────┬────────────┘└────────────┬────────────┘
                                           │                          │
                                           ▼                          ▼
                                   reports/*.html              reports/*.pdf
```

---

## 2. Key Features

| Domain | Implemented Capabilities |
|---|---|
| **Data Ingestion** | CSV, Excel (`.xlsx`, `.xls`), JSON (records or wrapped objects), SQLite (`.db`, `.sqlite`, `.sqlite3`), REST APIs (`http://`, `https://`) with automatic schema and type validation. |
| **Statistical Analysis** | Count, mean, median, standard deviation, percentiles (p25, p75, p95), min, max, group-by aggregations, Pearson correlation matrix, top-N ranking. |
| **Comparative Analysis** | Segment-vs-segment benchmarks (share %, variance from mean, index vs avg) and Period-vs-period comparisons (current vs prior, absolute variance, growth %). |
| **Executive Narratives** | Automated dynamic synthesis of plain-English insights (e.g., *"Revenue grew by 12.4% ($1.02M vs $907K in previous period). 3 anomalies detected."*). |
| **Trend Detection** | Time-series resampling, moving averages, period-over-period growth rate, overall percentage growth, regression slope & direction, calendar month seasonality. |
| **Anomaly Flagging** | Z-score thresholding and Interquartile Range (IQR) outlier detection with clean tabular summaries. |
| **Visualizations** | **6 Supported Chart Types**: Bar, Line, Pie, Scatter, Heatmap, and Histogram. |
| **Dual Reporting** | **Offline-First HTML** (bundles Plotly.js directly with `--offline` for zero-internet air-gapped viewing; supports `--online` for CDN link) and paginated **PDF** (running headers, footers, page numbering, table split protection). |
| **Automation** | APScheduler cron expressions (e.g. `0 8 * * 1`) and interval triggers, error resilience, and automated email attachment delivery via SMTP. |

---

## 3. Technology Stack

- **Language**: Python 3.11+ (Fully tested on 3.11, 3.12, 3.13, and 3.14)
- **CLI Framework**: Typer (Rich-powered modern terminal interface)
- **Data Processing**: Pandas 2.0+, NumPy
- **Visualizations**: Matplotlib, Seaborn, Plotly
- **Report Generation**: Jinja2 (HTML), ReportLab (PDF)
- **Configuration**: PyYAML
- **Scheduling**: APScheduler (CronTrigger, IntervalTrigger)
- **Network / API**: Requests
- **Testing**: pytest, pytest-cov (100% line coverage over 820 statements)
- **CI / CD**: GitHub Actions cross-platform matrix (Ubuntu, Windows, macOS)

---

## 4. Installation & Setup

### Prerequisites
- Python 3.11 or later installed.
- Git.

### Clone and Install

```bash
# 1. Clone the repository
git clone https://github.com/HarshaDeepBezawada/AutoReport.git
cd AutoReport

# 2. Create and activate a virtual environment
# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# 3. Install in editable mode with development dependencies
pip install -e ".[dev]"
```

Verify installation:
```bash
autoreport --help
autoreport --version
```

---

## 5. Quick Start & Usage Examples

### 1. Generate Synthetic Demo Data
Create the sample sales, HR, and inventory datasets in `data/`:
```bash
python scripts/make_sample_data.py
```

### 2. Inspect Available Templates
```bash
autoreport list-templates
```
Output:
```
sales        Sales Performance Report - Revenue, regional and product performance with trend, comparison and anomaly checks
hr           HR Workforce Report - Headcount, compensation and performance across departments
inventory    Inventory Status Report - Stock levels, value and fast/slow movers by category
```

### 3. Validate a Template & Schema
```bash
autoreport validate sales
autoreport validate inventory --data data/inventory.json
```

### 4. Generate Reports (One-Shot)
```bash
# Generate both HTML (offline bundled) and PDF reports
autoreport generate sales

# Force offline Plotly embedding (default, zero internet required)
autoreport generate sales --offline

# Use CDN script tag to keep HTML under ~50 KB for web hosting
autoreport generate sales --online

# Generate only PDF to a custom folder
autoreport generate hr -f pdf -o output/ -n q4_workforce

# Generate inventory report overriding the data source with SQLite
autoreport generate inventory --data data/inventory.db
```
Generated reports are saved in `reports/` (or your chosen `-o` folder).

### 5. Run on a Schedule
```bash
# Run every Monday at 08:00
autoreport schedule sales --cron "0 8 * * 1"

# Run every 60 minutes with immediate execution
autoreport schedule hr --every 60

# Run with automated email distribution
autoreport schedule sales --cron "0 8 * * 1" --email-to team@company.com --smtp-host smtp.company.com
```

---

## 6. Performance Benchmarks

The official Code A Nova task specification requires:
1. Capability to process datasets up to **100,000 rows** without memory bottlenecks.
2. Standard report generation completing in **under 30 seconds**.

### Benchmark Execution

Run the dedicated benchmark verification script:
```bash
python scripts/verify_performance.py
```

### Measured Results (Environment: Python 3.14.6, Windows AMD64)

```
======================================================================
AUTOREPORT PERFORMANCE BENCHMARK (100K ROWS)
======================================================================
Generating synthetic benchmark dataset (100,000 rows)...
Dataset written to disk: 3.51 MB in 0.12s

--- Pipeline Step Breakdown ---
  1. Ingestion & Schema Validation: 0.13s
  2. Analysis (Stats, Trend, Anomalies, KPIs, Comparisons): 0.06s

--- End-to-End Report Generation (HTML + PDF) ---
Total generation time: 2.40s - 2.53s
  - Generated: sales.html (5967.0 KB, offline Plotly bundled)
  - Generated: sales.pdf (280.2 KB, paginated ReportLab PDF)

======================================================================
BENCHMARK RESULT: VERIFIED PASS
Measured time: 2.53s (Threshold: < 30.0s — 11.8x faster than budget)
======================================================================
```
*AutoReport processes 100,000 rows and builds both HTML and PDF reports in **~2.53 seconds**, completing **11.8x faster** than the 30-second budget.*

---

## 7. Testing & Code Coverage

AutoReport includes a comprehensive test suite covering:
- Ingestion from all 5 sources (CSV, Excel, JSON, SQLite, REST API).
- Statistical engine, period comparisons, segment benchmarks, and dynamic executive narratives.
- Edge cases: corrupted JSON, missing files, unsupported formats, invalid SQL, all-constant data, missing dates/NaT, non-numeric inputs, and empty datasets.
- All 6 chart types across both static (Matplotlib/Seaborn) and interactive (Plotly) paths.
- HTML builder escaping, offline bundle embedding, and ReportLab PDF multi-page pagination.
- Scheduling triggers, error resilience, and mocked SMTP email delivery.

### Run Tests:

```bash
# Run full test suite with coverage report
python -m pytest --cov=autoreport --cov-report=term-missing
```

### Actual Test Coverage Results:

```
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
src\autoreport\__init__.py                    1      0   100%
src\autoreport\analysis\__init__.py           4      0   100%
src\autoreport\analysis\anomalies.py         24      0   100%
src\autoreport\analysis\stats.py             49      0   100%
src\autoreport\analysis\trends.py            42      0   100%
src\autoreport\builders\__init__.py           3      0   100%
src\autoreport\builders\html_builder.py      35      0   100%
src\autoreport\builders\pdf_builder.py       78      0   100%
src\autoreport\cli.py                        76      0   100%
src\autoreport\generator.py                  19      0   100%
src\autoreport\ingestion\__init__.py          2      0   100%
src\autoreport\ingestion\sources.py          92      0   100%
src\autoreport\scheduler.py                  52      0   100%
src\autoreport\template.py                  208      0   100%
src\autoreport\viz\__init__.py                2      0   100%
src\autoreport\viz\charts.py                134      0   100%
-----------------------------------------------------------------------
TOTAL                                       821      0   100%
======================= 59 passed, 0 warnings =======================
```
- **Total Tests**: 59 passed, 0 failed.
- **Coverage**: **100%** across every single module and line in the entire codebase (**821 / 821 statements covered**, far exceeding the official `> 70%` requirement).
- **Static Analysis & Type Checking**: 0 warnings in `ruff check .`, 0 issues in `mypy src`.

---

## 8. Project Structure

```
AutoReport/
├── .github/
│   └── workflows/
│       └── ci.yml                       # Multi-OS & multi-Python CI matrix (Ubuntu, Win, Mac)
├── data/                                # Sample datasets
│   ├── sales.csv                        # Sales records (CSV)
│   ├── hr.xlsx                          # HR personnel data (Excel)
│   ├── inventory.json                   # Inventory records (JSON)
│   └── inventory.db                     # SQLite database copy
├── demo/                                # Project demonstration records
│   └── .gitkeep
├── docs/                                # Documentation
│   ├── PROJECT_DOCUMENTATION.md         # Master technical audit & compliance report
│   └── USER_GUIDE.md                    # CLI reference manual & template authoring guide
├── sample_reports/                      # Pre-generated deliverables
│   ├── sales.html / sales.pdf
│   ├── hr.html / hr.pdf
│   └── inventory.html / inventory.pdf
├── scripts/                             # Utility & validation scripts
│   ├── make_sample_data.py              # Generates synthetic data
│   └── verify_performance.py           # 100K rows benchmark verification
├── src/autoreport/                      # Core package source
│   ├── __init__.py
│   ├── cli.py                           # Typer CLI application
│   ├── generator.py                     # Report orchestration
│   ├── template.py                      # YAML parsing & data pipeline
│   ├── scheduler.py                     # APScheduler & SMTP emailer
│   ├── analysis/                        # Analytics modules
│   │   ├── stats.py                     # Summary stats, group-by, correlations, comparisons
│   │   ├── trends.py                    # Time series, moving avg, seasonality
│   │   └── anomalies.py                 # Z-score and IQR outlier detection
│   ├── builders/                        # Report renderers
│   │   ├── html_builder.py              # Jinja2 HTML builder (offline & CDN Plotly)
│   │   ├── pdf_builder.py               # ReportLab PDF builder
│   │   └── report.html                  # Jinja2 template
│   ├── ingestion/                       # Data adapters
│   │   └── sources.py                   # CSV, Excel, JSON, SQLite, API
│   ├── templates_builtin/               # YAML report templates
│   │   ├── sales.yaml
│   │   ├── hr.yaml
│   │   └── inventory.yaml
│   └── viz/                             # Visualization factory
│       └── charts.py                    # Dual static & Plotly chart factory
├── tests/                               # Comprehensive pytest suite
│   ├── conftest.py                      # Shared fixtures
│   ├── test_analysis.py                 # Analytics tests
│   ├── test_api_source.py               # REST API mock tests
│   ├── test_coverage_complete.py        # Edge-case & 100% coverage tests (59 tests)
│   ├── test_ingestion.py                # Data adapter tests
│   ├── test_reports.py                  # CLI & report builder tests
│   └── test_scheduler.py                # Scheduling & SMTP email tests
├── CHANGELOG.md                         # 15-day milestone changelog (Day 1 - Day 15)
├── pyproject.toml                       # Package configuration & metadata
└── README.md                            # Project overview & documentation
```

---

## 9. Design Decisions & Highlights

1. **One Chart Spec, Two Renderers**: Rather than duplicating chart logic for web and print, each YAML chart definition is fed to both Matplotlib (for vector/raster PDF rendering) and Plotly (for interactive HTML).
2. **Offline-First HTML Reports**: By default (`--offline`), generated HTML reports embed `plotly.offline.get_plotlyjs()`, producing fully self-contained reports that open cleanly without internet access in secure corporate environments. For lightweight file sizes (~50 KB), `--online` switches to the official CDN link.
3. **Automated Executive Narratives & Comparative Benchmarks**: Reports auto-generate synthesized natural-language summaries and period-over-period / segment-over-segment comparative benchmarks, fulfilling operational business reporting requirements.
4. **Partial Period Protection**: In trend analysis, the final time period is automatically truncated if the dataset ends mid-month, preventing false drops in monthly trend curves (`drop_partial: false` disables this).
5. **Security & Data Handling**:
   - Jinja2 HTML auto-escaping prevents script injection from raw data strings.
   - SQL queries parameterize table selection and validate table identifiers against alphanumeric characters.
   - Passwords and SMTP credentials are never stored in templates or logged to console.

---

## 10. Deliverables Checklist

- [x] **Deliverable 1**: Standard Python package installable via `pip install -e .` with `src` layout.
- [x] **Deliverable 2**: 3 Built-in sample report templates (`sales.yaml`, `hr.yaml`, `inventory.yaml`).
- [x] **Deliverable 3**: Sample datasets for demonstration across CSV, Excel, JSON, and SQLite (`data/`).
- [x] **Deliverable 4**: Generated sample reports in both PDF and HTML formats (`sample_reports/`).
- [x] **Deliverable 5**: Complete User Guide with CLI manual and template guide (`docs/USER_GUIDE.md`).
- [x] **Deliverable 6**: Master technical documentation & audit report (`docs/PROJECT_DOCUMENTATION.md`).
- [x] **Deliverable 7**: Project demonstration records and sample report presentations (`demo/`, `sample_reports/`).
- [x] **Deliverable 8**: 100K-row performance benchmark verification in ~2.53s (`scripts/verify_performance.py`).
- [x] **Deliverable 9**: 100% test coverage over 821 statements with 59 automated tests (`tests/`).
- [x] **Deliverable 10**: Cross-platform CI matrix workflow with Ruff linting and Mypy static typing (`.github/workflows/ci.yml`) and 15-day progress log (`CHANGELOG.md`).
