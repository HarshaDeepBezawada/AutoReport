# AutoReport — Automated Report & Analytics Generator

AutoReport is a production-grade, CLI-driven report automation and analytics generator developed in Python. It ingests data across diverse formats (CSV, Excel, JSON, SQLite, REST API), performs rigorous statistical, trend, and anomaly analysis, creates publication-quality visualizations, and produces responsive **HTML** (with interactive Plotly figures) and paginated **PDF** reports (with ReportLab and static charts) driven entirely by declarative YAML templates.

Developed for the **Code A Nova 15-Day Python Development Internship**.

---

## 1. Problem Statement & Architecture

Organizations and data teams repeatedly waste hundreds of hours manually pulling data, recomputing summary statistics, calculating rolling trends, identifying anomalies, plotting charts, and assembling weekly or monthly slide decks. 

**AutoReport** solves this by establishing a reusable, configurable automation pipeline:
- **Declarative YAML Templates**: Add or customize reports by writing YAML specifications, not Python code.
- **Unified Adapter Pattern**: All data sources inherit from a shared `DataSource` abstraction with schema validation.
- **Dual-Renderer Visualization Factory**: A single chart specification drives both interactive Plotly figures for web reports and Matplotlib/Seaborn vector/raster plots for PDF documents.
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
                              │ (Jinja2 + Plotly Charts)││  (ReportLab + Matplotlib)
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
| **Trend Detection** | Time-series resampling, moving averages, period-over-period growth rate, overall percentage growth, regression slope & direction, calendar month seasonality. |
| **Anomaly Flagging** | Z-score thresholding and Interquartile Range (IQR) outlier detection with clean tabular summaries. |
| **Visualizations** | **6 Supported Chart Types**: Bar, Line, Pie, Scatter, Heatmap, and Histogram. |
| **Dual Reporting** | Responsive, modern HTML (with embedded or CDN Plotly charts) and paginated PDF (with running headers, footers, page numbering, and table split protection). |
| **Automation** | APScheduler cron expressions (e.g. `0 8 * * 1`) and interval triggers, error resilience, and automated email attachment delivery via SMTP. |

---

## 3. Technology Stack

- **Language**: Python 3.11+ (Verified on Python 3.14)
- **CLI Framework**: Typer (Rich-powered modern terminal interface)
- **Data Processing**: Pandas 2.0+, NumPy
- **Visualizations**: Matplotlib, Seaborn, Plotly
- **Report Generation**: Jinja2 (HTML), ReportLab (PDF)
- **Configuration**: PyYAML
- **Scheduling**: APScheduler (CronTrigger, IntervalTrigger)
- **Network / API**: Requests
- **Testing**: pytest, pytest-cov

---

## 4. Installation & Setup

### Prerequisites
- Python 3.11 or later installed.
- Git (optional, for version control).

### Windows (PowerShell / Command Prompt)

```powershell
# Clone or navigate to the project directory
cd autoreport

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install the package and dependencies in editable mode
pip install -e ".[dev]"
```

### Linux / macOS

```bash
cd autoreport
python3 -m venv .venv
source .venv/bin/activate
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
sales        Sales Performance Report - Revenue, regional and product performance with trend and anomaly checks
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
# Generate both HTML and PDF reports
autoreport generate sales

# Generate only PDF to a custom folder
autoreport generate hr -f pdf -o output/ -n q4_workforce

# Generate inventory report overriding the data source with SQLite
autoreport generate inventory --data data/inventory.db
```
Generated reports are placed in `reports/` (or your chosen `-o` folder).

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

A dedicated benchmark script is included in `scripts/verify_performance.py`:
```bash
python scripts/verify_performance.py
```

### Measured Results (Environment: Python 3.14.6, Windows AMD64)

```
======================================================================
AUTOREPORT PERFORMANCE BENCHMARK (100K ROWS)
======================================================================
Generating synthetic benchmark dataset (100,000 rows)...
Dataset written to disk: 3.51 MB in 0.11s

--- Pipeline Step Breakdown ---
  1. Ingestion & Schema Validation: 0.11s
  2. Analysis (Stats, Trend, Anomalies, KPIs): 0.04s

--- End-to-End Report Generation (HTML + PDF) ---
Total generation time: 14.05s
  - Generated: sales.html (1259.3 KB)
  - Generated: sales.pdf (279.1 KB)

======================================================================
BENCHMARK RESULT: VERIFIED PASS
Measured time: 14.05s (Threshold: < 30.0s)
======================================================================
```
*AutoReport processes 100,000 rows and builds both HTML and PDF reports in ~14.05s, less than half the permitted 30-second budget.*

---

## 7. Testing & Code Coverage

AutoReport includes comprehensive unit, integration, and CLI tests covering:
- Ingestion from all 5 sources (CSV, Excel, JSON, SQLite, REST API).
- Edge cases: corrupted JSON, missing files, unsupported formats, invalid SQL, all-constant data, missing dates/NaT, and non-numeric inputs.
- All 6 chart types across both static and Plotly rendering paths.
- HTML builder escaping and ReportLab PDF multi-page pagination.
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
src\autoreport\analysis\stats.py             23      0   100%
src\autoreport\analysis\trends.py            42      0   100%
src\autoreport\builders\__init__.py           3      0   100%
src\autoreport\builders\html_builder.py      33      0   100%
src\autoreport\builders\pdf_builder.py       78      0   100%
src\autoreport\cli.py                        76      0   100%
src\autoreport\generator.py                  19      0   100%
src\autoreport\ingestion\__init__.py          2      0   100%
src\autoreport\ingestion\sources.py          92      0   100%
src\autoreport\scheduler.py                  52      0   100%
src\autoreport\template.py                  162      0   100%
src\autoreport\viz\__init__.py                2      0   100%
src\autoreport\viz\charts.py                133      0   100%
-----------------------------------------------------------------------
TOTAL                                       746      0   100%
======================= 58 passed, 0 warnings =======================
```
- **Total Tests**: 58 passed, 0 failed.
- **Coverage**: **100%** across every single module and line in the entire codebase (far exceeding the official `> 70%` requirement).

---

## 8. Project Structure

```
autoreport/
├── data/                                # Sample datasets
│   ├── sales.csv                        # Sales records (CSV)
│   ├── hr.xlsx                          # HR personnel data (Excel)
│   ├── inventory.json                   # Inventory records (JSON)
│   └── inventory.db                     # SQLite database copy
├── docs/                                # Documentation
│   ├── USER_GUIDE.md                    # CLI manual & template guide
│   └── DEMO_SCRIPT.md                   # 5-minute presentation script
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
│   │   ├── stats.py                     # Summary stats, group-by, correlations
│   │   ├── trends.py                    # Time series, moving avg, seasonality
│   │   └── anomalies.py                 # Z-score and IQR outlier detection
│   ├── builders/                        # Report renderers
│   │   ├── html_builder.py              # Jinja2 HTML builder
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
│   ├── test_ingestion.py                # Data adapter tests
│   ├── test_reports.py                  # CLI & report builder tests
│   └── test_scheduler.py                # Scheduling & SMTP email tests
├── pyproject.toml                       # Package configuration & metadata
└── README.md                            # Project overview
```

---

## 9. Design Decisions & Limitations

1. **One Chart Spec, Two Renderers**: Rather than duplicating chart logic for web and print, each YAML chart definition is fed to both Matplotlib (for vector/raster PDF rendering) and Plotly (for interactive HTML).
2. **Partial Period Protection**: In trend analysis, the final time period is automatically truncated if the dataset ends mid-month, preventing false drops in monthly trend curves (`drop_partial: false` disables this).
3. **HTML Offline Viewing**: The generated HTML reports load Plotly.js from `cdn.plot.ly` to keep HTML report file sizes under ~50 KB for typical datasets. When opening reports completely offline, static PDF reports serve as the zero-dependency fallback.
4. **Security & Data Handling**:
   - Jinja2 HTML auto-escaping prevents script injection from raw data strings.
   - SQL queries parameterize table selection and validate table identifiers against alphanumeric characters.
   - Passwords and SMTP credentials are never stored in templates or logged to console.

---

## 10. Deliverables Checklist

- [x] Python package installable via `pip install -e .`
- [x] Clean, modular source code repository with `src/` layout.
- [x] 3 Built-in sample report templates (`sales.yaml`, `hr.yaml`, `inventory.yaml`).
- [x] Sample datasets for demonstration (`data/`).
- [x] Generated sample reports in both PDF and HTML formats (`sample_reports/`).
- [x] Complete User Guide with CLI reference & template authoring guide (`docs/USER_GUIDE.md`).
- [x] 5-minute walkthrough presentation script (`docs/DEMO_SCRIPT.md`).
- [x] 100K-row performance benchmark verification (`scripts/verify_performance.py`).
