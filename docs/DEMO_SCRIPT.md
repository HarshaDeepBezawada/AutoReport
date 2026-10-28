# 5-Minute Demo Script

Goal: show one workflow end to end, from raw data to a scheduled report.
Have a terminal open in the project folder with the virtual environment active.
Pre-open `sample_reports/sales.html` and `sample_reports/sales.pdf` as a fallback.

## 0:00 - 0:30 The problem

"Analysts rebuild the same weekly report by hand. AutoReport takes a data file
and a YAML template and produces the finished HTML and PDF automatically."

## 0:30 - 1:15 The data

```bash
python scripts/make_sample_data.py
head -5 data/sales.csv
```
Point out: 1,500 synthetic sales rows, with a few extreme transactions planted
on purpose so the anomaly detector has something to find.

## 1:15 - 2:00 The template

```bash
autoreport list-templates
cat src/autoreport/templates_builtin/sales.yaml
```
Point out: sections are plain YAML (KPIs, charts, trend, anomalies). "A new
report is a new file, not new code."

```bash
autoreport validate sales
```
Show the green "valid" message. Then break it live: change `type: bar` to
`type: radar`, re-run validate, and show the precise error message. Revert it.

## 2:00 - 3:15 Generate

```bash
autoreport generate sales
```
Open `reports/sales.html`: hover over the interactive charts, and note the KPI
tiles and the sentence "revenue shows an upward trend ... up 83.1%". Resize the
window to show the responsive layout.
Open `reports/sales.pdf`: same content with static charts, paginated, footer
and page numbers. "One chart spec drives both renderers."
Scroll to the anomalies table: the planted spikes appear.

## 3:15 - 4:00 Other sources and templates

```bash
autoreport generate hr -f pdf -o out/
autoreport generate inventory --data data/inventory.db
```
"Same tool, an Excel file and a SQLite database. CSV, JSON and REST APIs work
too, all behind one interface."

## 4:00 - 4:40 Scheduling

```bash
autoreport schedule sales --cron "0 8 * * 1"
```
"Every Monday at 8, with optional email delivery. A failed run is logged and
never kills the scheduler." Stop it with Ctrl+C.

## 4:40 - 5:00 Quality

```bash
pytest --cov=autoreport
python scripts/verify_performance.py
```
"58 tests, 100% full codebase test coverage, including edge cases: bad files, bad schemas, constant
data, partial months, and mocked SMTP. Plus 100,000 rows processed in ~14 seconds."

## If something goes wrong

- Charts blank in the HTML: Plotly loads from a CDN, so check the internet connection.
- Command not found: activate the virtual environment, then `pip install -e .`
- Any failure: open the pre-generated files in `sample_reports/`.
