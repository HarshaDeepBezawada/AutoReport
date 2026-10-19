# AutoReport - Automated Report & Analytics Generator

AutoReport is a Python-based command-line application that simplifies data analysis and report generation. It allows users to load datasets, analyze numerical data, generate charts, and create HTML and PDF reports using simple terminal commands.

The project is designed to make routine data analysis easier, faster, and more accessible.

## Features

* **Multiple Data Formats:** Load datasets from CSV, Excel (`.xlsx`), and JSON files.
* **Statistical Analysis:** Calculate count, total, average, median, minimum, and maximum for numerical data.
* **Data Visualization:** Generate charts from numerical columns.
* **HTML Reports:** Create structured HTML reports with dataset previews and statistical summaries.
* **PDF Reports:** Generate PDF reports from datasets.
* **Command-Line Interface:** Run analysis and report-generation tasks directly from the terminal.
* **Automated Testing:** Includes a pytest test suite to verify core functionality.

## Technology Stack

* **Python** — Core programming language
* **Typer** — Command-line interface
* **Pandas** — Data loading and analysis
* **NumPy** — Numerical computing
* **Matplotlib** — Data visualization
* **Plotly** — Interactive visualization library
* **ReportLab** — PDF generation
* **pytest** — Automated testing

## Project Structure

```text
AutoReport/
├── data/
│   ├── sales.csv
│   ├── sales.json
│   └── sales.xlsx
├── reports/                  # Generated reports (not tracked by Git)
├── src/
│   └── autoreport/
│       ├── __init__.py
│       ├── analyzer.py
│       ├── chart_generator.py
│       ├── cli.py
│       ├── data_loader.py
│       ├── pdf_generator.py
│       └── report_generator.py
├── tests/
│   ├── test_analyzer.py
│   ├── test_chart_generator.py
│   ├── test_cli.py
│   ├── test_data_loader.py
│   ├── test_pdf_generator.py
│   └── test_report_generator.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Requirements

* Python 3.11 or later
* pip

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AutoReport
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows Command Prompt:**

```cmd
venv\Scripts\activate
```

### 4. Install the project

```bash
python -m pip install -e .
```

## Usage

Run these commands from the project directory after activating the virtual environment and installing AutoReport.

### Display available commands

```bash
autoreport --help
```

### Analyze a dataset

```bash
autoreport analyze data/sales.csv
```

You can also analyze JSON or Excel datasets:

```bash
autoreport analyze data/sales.json
autoreport analyze data/sales.xlsx
```

The analysis displays numerical statistics such as count, total, average, median, minimum, and maximum.

### Generate a chart

```bash
autoreport chart data/sales.csv
```

By default, the generated chart is saved in the `reports/` directory.

### Generate an HTML report

```bash
autoreport report data/sales.csv
```

The generated report is saved as:

```text
reports/report.html
```

Open the report in your default browser:

```cmd
start reports\report.html
```

### Generate a PDF report

```bash
autoreport pdf data/sales.csv
```

The generated PDF is saved as:

```text
reports/report.pdf
```

**Note:** Replace `data/sales.csv` with the path to your own supported dataset.

## Running Tests

AutoReport includes automated tests for its core functionality.

Run the complete test suite using:

```bash
python -m pytest
```

To run tests with coverage information:

```bash
python -m pytest --cov=autoreport --cov-report=term-missing
```

The current test suite contains **17 tests, all passing**.

## Current Project Status

Implemented:

* CSV, Excel, and JSON data loading
* Numerical data analysis
* Chart generation
* HTML report generation
* PDF report generation
* Command-line commands
* Automated tests

Future improvements may include:

* SQLite database support
* Grouped statistical analysis
* Trend detection and anomaly identification
* YAML-based report templates
* Interactive charts embedded in HTML reports
* Scheduled report generation

## Contributing

Contributions, suggestions, and bug reports are welcome. Feel free to fork the repository and experiment with additional features.

## License

A license has not yet been selected. Licensing terms will be added in a future update.
