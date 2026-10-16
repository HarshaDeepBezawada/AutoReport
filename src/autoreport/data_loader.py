import pandas as pd
from pathlib import Path


def load_csv(file_path: str) -> pd.DataFrame:
    """Load data from a CSV file."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    data = pd.read_csv(path)

    if data.empty:
        raise ValueError("The CSV file contains no data.")

    return data