from pathlib import Path

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf_report(
    data: pd.DataFrame,
    output_path: str = "reports/report.pdf",
) -> str:
    """Generate a PDF report containing data and statistical summaries."""

    if data.empty:
        raise ValueError("Dataset contains no data.")

    # Create the output folder if it doesn't exist
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Create the PDF document
    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    content = []

    # Report title
    content.append(
        Paragraph("AutoReport Data Report", styles["Title"])
    )
    content.append(Spacer(1, 15))

    # Dataset information
    content.append(
        Paragraph(f"Total rows: {len(data)}", styles["Normal"])
    )
    content.append(
        Paragraph(f"Total columns: {len(data.columns)}", styles["Normal"])
    )
    content.append(Spacer(1, 15))

    # Dataset preview
    content.append(
        Paragraph("Dataset Preview (first 20 rows)", styles["Heading2"])
    )

    preview = data.head(20).fillna("").astype(str)

    preview_table_data = [
        [str(column) for column in preview.columns]
    ] + preview.values.tolist()

    preview_table = Table(
        preview_table_data,
        repeatRows=1,
    )

    preview_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    content.append(preview_table)
    content.append(Spacer(1, 20))

    # Statistical summary
    content.append(
        Paragraph("Statistical Summary", styles["Heading2"])
    )

    numeric_data = data.select_dtypes(include="number")

    if not numeric_data.empty:
        statistics = numeric_data.describe().round(2)

        statistics_table_data = [
            ["Statistic"] + [str(column) for column in statistics.columns]
        ]

        for statistic, row in statistics.iterrows():
            statistics_table_data.append(
                [str(statistic)] + [
                    f"{value:.2f}" for value in row
                ]
            )

        statistics_table = Table(
            statistics_table_data,
            repeatRows=1,
        )

        statistics_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        content.append(statistics_table)
    else:
        content.append(
            Paragraph("No numeric columns available.", styles["Normal"])
        )

    # Generate the PDF
    document.build(content)

    return str(output)