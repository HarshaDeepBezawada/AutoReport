
import pandas as pd


def analyze_data(data: pd.DataFrame) -> dict:
    """Analyze all numeric columns in a dataset."""

    if data.empty:
        raise ValueError("Dataset contains no data.")

    # Select columns containing numbers
    numeric_data = data.select_dtypes(include="number")

    if numeric_data.empty:
        raise ValueError("Dataset contains no numeric columns.")

    results = {}

    # Analyze each numeric column
    for column in numeric_data.columns:
        values = numeric_data[column].dropna()

        if values.empty:
            continue

        results[column] = {
            "count": int(values.count()),
            "total": values.sum(),
            "average": values.mean(),
            "median": values.median(),
            "minimum": values.min(),
            "maximum": values.max(),
        }

    return results

