import json
from pathlib import Path

import pandas as pd


def load_csv(file_path: str) -> pd.DataFrame:
    """Load data from a CSV file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    data = pd.read_csv(path)

    if data.empty:
        raise ValueError("The CSV file contains no data.")

    return data


def load_excel(file_path: str) -> pd.DataFrame:
    """Load data from an Excel file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    data = pd.read_excel(path)

    if data.empty:
        raise ValueError("The Excel file contains no data.")

    return data


def load_json(file_path: str) -> pd.DataFrame:
    """Load data from a JSON file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    data = pd.DataFrame(records)

    if data.empty:
        raise ValueError("The JSON file contains no data.")

    return data


def load_data(file_path: str) -> pd.DataFrame:
    """Load CSV, Excel, or JSON data based on file extension."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = path.suffix.lower()

    if extension == ".csv":
        return load_csv(file_path)

    elif extension in (".xlsx", ".xls"):
        return load_excel(file_path)

    elif extension == ".json":
        return load_json(file_path)

    else:
        raise ValueError(
            f"Unsupported file format: {extension}. "
            "Supported formats: CSV, XLSX, XLS, JSON."
        )

