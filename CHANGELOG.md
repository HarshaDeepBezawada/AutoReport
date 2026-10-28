# AutoReport — 15-Day Engineering Milestone Changelog

This changelog documents the complete day-by-day development trajectory of **AutoReport** following the official **Code A Nova 15-Day Internship Milestone Plan**.

---

## Week 1: Core Foundation & Ingestion

### Day 1: Project Setup & Architecture Skeleton
- Initialized clean Python package with modern `src` layout (`src/autoreport/`).
- Authored `pyproject.toml` targeting Python 3.11+ using `setuptools` build backend.
- Configured CLI entry point `autoreport = autoreport.cli:app` using **Typer**.
- Defined project directories: `data/`, `docs/`, `scripts/`, `src/`, `tests/`, `sample_reports/`.

### Day 2: Data Ingestion & Schema Validation (CSV & Excel)
- Built the `DataSource` abstract base class introducing the **Adapter Pattern**.
- Implemented `CSVSource` wrapping `pandas.read_csv` with encoding and delimiter controls.
- Implemented `ExcelSource` supporting `.xlsx` and `.xls` via `openpyxl`.
- Implemented `validate_schema()` enforcing expected data types (`numeric`, `string`, `datetime`, `any`).
- Implemented automated ISO date coercing via `pd.to_datetime(errors="coerce")`.

### Day 3: Structured Data Adapters (JSON, SQLite & REST API)
- Implemented `JSONSource` handling both flat record arrays and nested objects (`{"records": [...]}`).
- Implemented `SQLiteSource` with connection lifecycle management (`closing()`), automated table discovery, and SQL injection sanitization.
- Implemented `APISource` fetching HTTP/HTTPS JSON endpoints via `requests` with configurable timeouts.
- Implemented factory function `get_source(location, **options)`.

### Day 4: Statistical Analysis Engine
- Created `src/autoreport/analysis/stats.py`.
- Implemented `summary_stats()`: count, mean, median, standard deviation, min, percentiles (p25, p75, p95), and max.
- Implemented `group_aggregate()`: multi-aggregation grouping sorted descending by primary metric.
- Implemented `correlations()`: Pearson correlation matrix with zero-variance protection.
- Implemented `top_n()`: ranking and filtering top/bottom records.
- Implemented `compare_segments()` and `compare_periods()` for benchmark comparisons.

### Day 5: Time-Series Trend Analysis
- Created `src/autoreport/analysis/trends.py`.
- Implemented `resample_series()` with frequency aggregations (`ME`, `W`) and partial-period truncation (`drop_partial=True`).
- Implemented `moving_average()`: rolling moving average with `min_periods=1`.
- Implemented `growth_rate()`: period-over-period percentage delta.
- Implemented `overall_growth()`: total net growth percentage across the series.
- Implemented `trend_direction()`: Ordinary Least Squares (OLS) linear regression model fitting, evaluating $R^2$ and trajectory direction (`upward`, `downward`, `flat`).
- Implemented `seasonality()`: calendar month cyclical grouping.

---

## Week 2: Analytics, Visualizations & Templating

### Day 6: Statistical Anomaly Detection
- Created `src/autoreport/analysis/anomalies.py`.
- Implemented `zscore_anomalies()`: standard score outlier identification ($|z| > \tau$).
- Implemented `iqr_anomalies()`: non-parametric interquartile range fences ($Q_1 - 1.5 \cdot \text{IQR}$, $Q_3 + 1.5 \cdot \text{IQR}$).
- Implemented `flag_anomalies()`: tabular row extraction of detected outliers.
- Added numeric coercion protections to safely process dirty data and zero-IQR edge cases.

### Day 7: Static Visualization Engine (Matplotlib / Seaborn)
- Created `src/autoreport/viz/charts.py`.
- Implemented unified chart factory supporting 6 core chart types:
  1. `bar`: Categorical aggregation and counts.
  2. `line`: Continuous time-series curves with markers.
  3. `pie`: Proportional share distribution.
  4. `scatter`: Bi-variate distributions with categorical hue.
  5. `heatmap`: Divergent correlation matrices.
  6. `histogram`: Configurable frequency binning.
- Implemented headless rendering with `matplotlib.use("Agg")` and high-DPI (130 DPI) PNG byte streaming.
- Optimized scatter plot legends with fixed upper-right placement for high-volume datasets.

### Day 8: Interactive Web Visualizations (Plotly)
- Implemented `make_plotly_chart()` in `viz/charts.py`.
- Bound identical YAML chart specifications to Plotly Express and Graph Objects.
- Maintained unified styling, consistent company color palette (`PALETTE`), and responsive margins.
- Implemented offline Plotly.js embedding option (`build_html(..., offline=True)`).

### Day 9: Declarative YAML Report Template System
- Created `src/autoreport/template.py`.
- Formulated declarative YAML template specifications: `name`, `title`, `description`, `source`, `schema`, `date_columns`, `sections`.
- Supported section types: `text`, `kpis`, `summary`, `table`, `chart`, `trend`, `anomalies`, `comparison`, `narrative`.
- Implemented strict template structure validation with informative line-level error reporting.
- Authored production reference templates: `sales.yaml`, `hr.yaml`, `inventory.yaml`.

### Day 10: Responsive HTML Report Generator
- Created `src/autoreport/builders/html_builder.py` and `builders/report.html`.
- Implemented Jinja2 rendering pipeline with HTML auto-escaping.
- Built responsive CSS grid layout, KPI metric cards, horizontal-scrolling data tables, and executive summary callouts.
- Supported both 100% air-gapped embedded Plotly mode and lightweight CDN mode.

---

## Week 3: Document Generation, Automation & Submission

### Day 11: Paginated PDF Report Generator
- Created `src/autoreport/builders/pdf_builder.py`.
- Implemented ReportLab Platypus flowable document generation on A4 dimensions.
- Engineered dynamic canvas headers and running footers with automatic page numbering (`Page X`).
- Implemented intelligent table splitting: tables with $\le 12$ rows stay bound to headings (`KeepTogether`), while longer tables split gracefully across page breaks with repeated header rows (`repeatRows=1`).

### Day 12: Unified CLI Commands
- Finished `src/autoreport/cli.py` integrating:
  - `generate`: Single-shot report generation with format (`-f`), output (`-o`), name (`-n`), and offline flags.
  - `validate`: Pre-flight template and schema syntax verification.
  - `list-templates`: Template discovery and catalog listing.
  - `--version`: Package version inspection.

### Day 13: Scheduling Engine & Email Delivery
- Created `src/autoreport/scheduler.py`.
- Implemented APScheduler integration supporting 5-field cron syntax (`--cron "0 8 * * 1"`) and interval minutes (`--every 60`).
- Implemented error-resilient job wrapping preventing scheduler daemon crashes on data anomalies.
- Implemented `send_email()`: secure MIME multipart construction, STARTTLS negotiation, authentication, and report attachment delivery.

### Day 14: Comprehensive QA & Edge-Case Testing
- Formulated 6 comprehensive Pytest test suites in `tests/`.
- Covered empty datasets, corrupt files, zero-division safeguards, non-numeric inputs, and mocked external APIs/SMTP servers.
- Achieved **100% full codebase line coverage** (58 passed tests, 0 warnings).
- Implemented 100,000-row performance verification script (`scripts/verify_performance.py`), clocking report generation in **14.05 seconds**.

### Day 15: Documentation, Demonstration Evidence & Packaging
- Authored comprehensive documentation: `README.md`, `docs/USER_GUIDE.md`, `docs/DEMO_SCRIPT.md`, `docs/DEMO.md`, and `docs/PROJECT_DOCUMENTATION.md`.
- Regenerated reference sample reports in `sample_reports/`.
- Configured multi-OS GitHub Actions CI workflow (`.github/workflows/ci.yml`) testing Ubuntu, Windows, and macOS across Python 3.11, 3.12, and 3.13.
- Finalized repository hygiene and pushed complete codebase to GitHub.
