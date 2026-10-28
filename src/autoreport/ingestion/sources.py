"""Data ingestion layer using the Adapter pattern.

Every source (CSV, Excel, JSON, SQLite, REST API) is wrapped by a
``DataSource`` subclass exposing the same ``load()`` method, so the rest of
the pipeline never needs to know where the data came from.
"""

from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from contextlib import closing
from pathlib import Path
from typing import Any

import pandas as pd


class DataSourceError(Exception):
    """Raised when a data source cannot be read or validated."""


class DataSource(ABC):
    """Common interface for all data adapters."""

    def __init__(self, location: str, **options: Any) -> None:
        self.location = location
        self.options = options

    @abstractmethod
    def _read(self) -> pd.DataFrame:
        """Read raw data into a DataFrame."""

    def load(self, schema: dict[str, str] | None = None,
             date_columns: list[str] | None = None) -> pd.DataFrame:
        """Load the data, parse dates and optionally validate a schema."""
        try:
            df = self._read()
        except DataSourceError:
            raise
        except Exception as exc:  # wrap any adapter failure uniformly
            raise DataSourceError(f"Failed to read '{self.location}': {exc}") from exc
        for col in date_columns or []:
            if col not in df.columns:
                raise DataSourceError(f"Date column '{col}' not found")
            df[col] = pd.to_datetime(df[col], errors="coerce")
        if schema:
            validate_schema(df, schema)
        return df


class CSVSource(DataSource):
    def _read(self) -> pd.DataFrame:
        return pd.read_csv(self.location, **self.options)


class ExcelSource(DataSource):
    def _read(self) -> pd.DataFrame:
        return pd.read_excel(self.location, **self.options)


class JSONSource(DataSource):
    def _read(self) -> pd.DataFrame:
        with open(self.location, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            # accept {"records": [...]} style payloads
            lists = [v for v in data.values() if isinstance(v, list)]
            data = lists[0] if lists else [data]
        return pd.json_normalize(data)


class SQLiteSource(DataSource):
    """Location is the database file; ``query`` or ``table`` selects data."""

    def _read(self) -> pd.DataFrame:
        query = self.options.get("query")
        table = self.options.get("table")
        # sqlite3's own context manager only commits; closing() really closes the file
        with closing(sqlite3.connect(self.location)) as conn:
            if not query and not table:
                # convenience: a database with exactly one table needs no options
                names = [r[0] for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%'")]
                if len(names) != 1:
                    raise DataSourceError(
                        "SQLite source needs a 'query' or 'table' option "
                        f"(tables found: {', '.join(names) or 'none'})")
                table = names[0]
            if not query:
                if not table.replace("_", "").isalnum():
                    raise DataSourceError(f"Invalid table name: {table!r}")
                query = f"SELECT * FROM {table}"
            return pd.read_sql_query(query, conn)


class APISource(DataSource):
    """Fetch JSON from a REST endpoint (no paid APIs needed)."""

    def _read(self) -> pd.DataFrame:
        import requests

        resp = requests.get(self.location, timeout=self.options.get("timeout", 15),
                            params=self.options.get("params"))
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            lists = [v for v in data.values() if isinstance(v, list)]
            data = lists[0] if lists else [data]
        return pd.json_normalize(data)


_REGISTRY: dict[str, type[DataSource]] = {
    ".csv": CSVSource,
    ".xlsx": ExcelSource,
    ".xls": ExcelSource,
    ".json": JSONSource,
    ".db": SQLiteSource,
    ".sqlite": SQLiteSource,
    ".sqlite3": SQLiteSource,
}


def get_source(location: str, **options: Any) -> DataSource:
    """Factory: pick the right adapter from the location."""
    if location.startswith(("http://", "https://")):
        return APISource(location, **options)
    suffix = Path(location).suffix.lower()
    cls = _REGISTRY.get(suffix)
    if cls is None:
        raise DataSourceError(
            f"Unsupported data source type '{suffix}'. "
            f"Supported: {', '.join(sorted(_REGISTRY))} or an http(s) URL"
        )
    if not Path(location).exists():
        raise DataSourceError(f"File not found: {location}")
    return cls(location, **options)


_DTYPE_CHECKS = {
    "numeric": pd.api.types.is_numeric_dtype,
    "string": lambda s: pd.api.types.is_string_dtype(s) or pd.api.types.is_object_dtype(s),
    "datetime": pd.api.types.is_datetime64_any_dtype,
}


def validate_schema(df: pd.DataFrame, schema: dict[str, str]) -> None:
    """Check required columns exist and match the expected kind.

    ``schema`` maps column name -> one of numeric / string / datetime / any.
    """
    missing = [c for c in schema if c not in df.columns]
    if missing:
        raise DataSourceError(f"Missing required columns: {', '.join(missing)}")
    for col, kind in schema.items():
        if kind == "any":
            continue
        check = _DTYPE_CHECKS.get(kind)
        if check is None:
            raise DataSourceError(f"Unknown schema type '{kind}' for column '{col}'")
        if not check(df[col]):
            raise DataSourceError(f"Column '{col}' should be {kind}, got {df[col].dtype}")
