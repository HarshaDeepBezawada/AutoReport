from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def generate_chart(
    data: pd.DataFrame,
    column: str,
    output_path: str = "reports/chart.png",
) -> str:
    """Generate a bar chart for a numeric column."""

    if column not in data.columns:
        raise ValueError(f"Column '{column}' was not found.")

    # Convert the selected column into numeric values
    try:
        values = pd.to_numeric(data[column], errors="raise").dropna()
    except (ValueError, TypeError):
        raise ValueError(
            f"Column '{column}' contains no numeric data."
        ) from None

    if values.empty:
        raise ValueError(f"Column '{column}' contains no numeric data.")

    # Create the output folder if necessary
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Create the bar chart
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(values)), values)
    plt.title(f"{column} Analysis")
    plt.xlabel("Record")
    plt.ylabel(column)
    plt.tight_layout()

    # Save and close the chart
    plt.savefig(output, dpi=150)
    plt.close()

    return str(output)