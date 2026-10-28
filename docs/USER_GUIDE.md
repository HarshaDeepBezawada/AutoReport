# AutoReport User Guide

## 1. CLI reference

Run `autoreport --help` or `autoreport <command> --help` at any time.

### `autoreport generate TEMPLATE`

Generate a report once.

| Option | Default | Meaning |
|---|---|---|
| `TEMPLATE` | required | Built-in name (`sales`, `hr`, `inventory`) or path to a `.yaml` file |
| `--data, -d` | template's `source.path` | Data file or URL. Overrides the template |
| `--output, -o` | `reports/` | Output folder (created if missing) |
| `--format, -f` | `both` | `html`, `pdf` or `both` |
| `--name, -n` | template name | Base file name |
| `--template-dir` | none | Extra folder searched for templates |

```bash
autoreport generate sales
autoreport generate hr -f pdf -o out/ -n q3_hr
autoreport generate my_template.yaml -d export.xlsx
```

Exit code is `0` on success and `1` on any error (bad template, missing file,
schema mismatch), with a one-line message on stderr.

### `autoreport validate TEMPLATE`

Checks the template structure without producing a report. If a data file is
given (or the template has `source.path`) it also loads the data and verifies
the schema.

```bash
autoreport validate sales
autoreport validate my_template.yaml --data export.csv
```

### `autoreport list-templates`

Lists built-in templates and any in `--template-dir`.

### `autoreport schedule TEMPLATE`

Runs the report repeatedly until you press Ctrl+C.

| Option | Meaning |
|---|---|
| `--cron "0 8 * * 1"` | 5-field cron (minute hour day month weekday) |
| `--every N` | Every N minutes (use instead of `--cron`) |
| `--run-now / --no-run-now` | Generate once immediately (default: yes) |
| `--email-to`, `--smtp-host`, `--smtp-port` | Email each report as an attachment |

```bash
autoreport schedule sales --cron "0 9 * * 1-5"      # weekdays 09:00
autoreport schedule hr --every 60 -f pdf
autoreport schedule sales --cron "0 8 * * 1" --email-to boss@example.com --smtp-host smtp.example.com
```

A failed run is logged and the scheduler keeps going. Email delivery requires a reachable SMTP
server that accepts STARTTLS on the configured port. Automated unit tests mock SMTP
safely to ensure full test coverage without needing live external credentials.

For OS-level scheduling instead, call `autoreport generate ...` from cron
(Linux/macOS) or Windows Task Scheduler.

### Performance Verification

To test high-volume data ingestion and generation under load:
```bash
python scripts/verify_performance.py
```
This automatically runs an end-to-end benchmark on 100,000 synthetic records and validates that execution time satisfies the official `< 30s` constraint (measured: ~2.53s).


## 2. Data sources

The adapter is chosen from the file extension (or `http(s)://` for APIs).

| Source | Extensions | Options (set in template `source:`) |
|---|---|---|
| CSV | `.csv` | any `pandas.read_csv` option, e.g. `sep: ";"` |
| Excel | `.xlsx`, `.xls` | any `pandas.read_excel` option, e.g. `sheet_name: Q3` |
| JSON | `.json` | array of records, or an object holding one array |
| SQLite | `.db`, `.sqlite`, `.sqlite3` | `table: name` or `query: "SELECT ..."`. A database with a single table needs neither |
| REST API | `http(s)://...` | `params`, `timeout`. The response must be JSON |

## 3. Template authoring guide

A template is a YAML file. Start by copying one from
`src/autoreport/templates_builtin/`.

```yaml
name: sales                     # required, used for the output file name
title: Sales Performance Report # required, shown at the top
description: Short subtitle     # optional
source:
  path: data/sales.csv          # optional; --data overrides it
schema:                         # optional; checked at load time
  region: string                #   string | numeric | datetime | any
  revenue: numeric
date_columns: [date]            # parsed as dates
sections: [ ... ]               # required, rendered in order
```

### Section types

Every section accepts an optional `title`.

**`text`**: a paragraph.
```yaml
- {type: text, title: Overview, text: "What this report covers."}
```

**`kpis`**: headline number tiles. `agg` is one of
`sum, mean, median, count, min, max, nunique`. `format` is `currency`,
`percent` or omitted.
```yaml
- type: kpis
  items:
    - {label: Total Revenue, column: revenue, agg: sum, format: currency}
```

**`summary`**: count, mean, median, std, min, 25th/75th/95th percentile, max.
```yaml
- {type: summary, columns: [units, revenue]}
```

**`table`**: either a group-by comparison or a plain column listing.
```yaml
- {type: table, group_by: region, value: revenue, aggs: [sum, mean, count]}
- {type: table, columns: [sku, stock], sort_by: stock, limit: 10}
```

**`chart`**: `type` is `bar`, `line`, `pie`, `scatter`, `heatmap` or `histogram`.

| Chart | Keys |
|---|---|
| bar, pie | `x`, `y`, optional `agg` (sum/mean/count...), `limit` |
| line | `x`, `y`, optional `agg` + `freq` (`ME` month, `W` week) |
| scatter | `x`, `y`, optional `hue` |
| histogram | `x`, optional `bins` |
| heatmap | optional `columns` (correlation matrix of numeric columns) |

```yaml
- type: chart
  title: Revenue by Region
  chart: {type: bar, x: region, y: revenue, agg: sum, title: Revenue by Region}
```

**`trend`**: monthly (or weekly...) series with moving average, direction,
growth and an auto-written sentence.
```yaml
- {type: trend, date: date, column: revenue, freq: ME, agg: sum, window: 3}
```
The last period is dropped when the data ends mid-period. Set
`drop_partial: false` to keep it.

**`anomalies`**: flags unusual rows. `method` is `zscore` (default threshold 3)
or `iqr` (default multiplier 1.5). `show` picks the columns to display.
```yaml
- {type: anomalies, column: revenue, method: zscore, threshold: 3, show: [date, region, revenue]}
```

### Check your template

```bash
autoreport validate my_template.yaml --data my_data.csv
```
Validation names the section and the problem, e.g.
`Section 4: chart.type must be one of (...)`.

## 4. Extending AutoReport

- **New data format**: subclass `DataSource`, implement `_read()`, add the extension to `_REGISTRY` in `ingestion/sources.py`.
- **New chart type**: add a function to `_STATIC` in `viz/charts.py`, a branch in `make_plotly_chart`, and the name to `CHART_TYPES`.
- **New section type**: add it to `SECTION_TYPES` and `validate_template`, compute it in `build_report_data`, and render it in `report.html` and `pdf_builder.py`.

## 5. Troubleshooting

| Message | Fix |
|---|---|
| `Missing required columns: x` | The data lacks a column listed in `schema`. Check spelling or fix the schema |
| `Column 'x' should be numeric` | The column holds text, often from stray symbols such as `$` or `,`. Clean the source |
| `Date column 'x' not found` | `date_columns` names a column that does not exist |
| `Template 'x' not found` | Use a built-in name or the path to a `.yaml` file |
| `SQLite source needs a 'query' or 'table'` | The database has several tables; set `table:` in `source:` |
| Scheduler error about a time zone | Run `pip install tzdata` (already a dependency; needed on Windows) |
| HTML charts blank | Interactive charts load Plotly from a CDN, so open the file with internet access |
