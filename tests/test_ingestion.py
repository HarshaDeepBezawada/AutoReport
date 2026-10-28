import json
import sqlite3
from contextlib import closing

import pandas as pd
import pytest

from autoreport.ingestion import DataSourceError, get_source, validate_schema


def test_csv_loads_and_parses_dates(csv_file):
    out = get_source(str(csv_file)).load(date_columns=["date"])
    assert len(out) == 120
    assert pd.api.types.is_datetime64_any_dtype(out["date"])


def test_excel_loads(tmp_path, df):
    p = tmp_path / "d.xlsx"
    df.to_excel(p, index=False)
    assert len(get_source(str(p)).load()) == 120


def test_json_records_and_wrapped(tmp_path):
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"records": [{"a": 1}, {"a": 2}]}))
    assert get_source(str(p)).load()["a"].tolist() == [1, 2]


def test_sqlite_table_and_query(tmp_path, df):
    p = tmp_path / "d.db"
    conn = sqlite3.connect(p)
    df.to_sql("sales", conn, index=False)
    conn.close()
    assert len(get_source(str(p), table="sales").load()) == 120
    q = get_source(str(p), query="SELECT * FROM sales WHERE units > 5").load()
    assert (q["units"] > 5).all()


def test_sqlite_single_table_needs_no_option(tmp_path, df):
    p = tmp_path / "one.db"
    conn = sqlite3.connect(p)
    df.to_sql("only", conn, index=False)
    conn.close()
    assert len(get_source(str(p)).load()) == 120


def test_sqlite_multiple_tables_requires_choice(tmp_path, df):
    p = tmp_path / "two.db"
    conn = sqlite3.connect(p)
    df.to_sql("a", conn, index=False)
    df.to_sql("b", conn, index=False)
    conn.close()
    with pytest.raises(DataSourceError, match="tables found: a, b"):
        get_source(str(p)).load()


def test_sqlite_rejects_bad_table_name(tmp_path, df):
    p = tmp_path / "d.db"
    with closing(sqlite3.connect(p)) as conn:
        df.to_sql("sales", conn, index=False)
    with pytest.raises(DataSourceError):
        get_source(str(p), table="sales; DROP TABLE sales").load()


def test_unsupported_and_missing_file(tmp_path):
    with pytest.raises(DataSourceError, match="Unsupported"):
        get_source(str(tmp_path / "x.txt"))
    with pytest.raises(DataSourceError, match="not found"):
        get_source(str(tmp_path / "missing.csv"))


def test_schema_validation(df):
    validate_schema(df, {"revenue": "numeric", "region": "string", "date": "datetime"})
    with pytest.raises(DataSourceError, match="Missing"):
        validate_schema(df, {"nope": "numeric"})
    with pytest.raises(DataSourceError, match="should be numeric"):
        validate_schema(df, {"region": "numeric"})


def test_corrupt_file_wrapped(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json")
    with pytest.raises(DataSourceError, match="Failed to read"):
        get_source(str(p)).load()
