from pathlib import Path
 
import pandas as pd
 
 
def generate_html_report(
    data: pd.DataFrame,
    output_path: str = "reports/report.html",
) -> str:
    """Generate a professional HTML report containing dataset statistics."""
 
    if data.empty:
        raise ValueError("Dataset contains no data.")
 
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
 
    # Select numeric columns
    numeric_data = data.select_dtypes(include="number")
 
    # Create a preview of the first 20 rows
    table_html = data.head(20).to_html(
        index=False,
        border=0,
        classes="data-table",
        na_rep="N/A",
    )
 
    # Generate statistical summary
    if not numeric_data.empty:
        statistics_html = numeric_data.describe().round(2).to_html(
            border=0,
            classes="statistics-table",
            na_rep="N/A",
        )
    else:
        statistics_html = (
            "<p class='notice'>No numeric columns are available "
            "for statistical analysis.</p>"
        )
 
    # Build the HTML report
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoReport | Data Analytics Report</title>
 
    <style>
        * {{
            box-sizing: border-box;
        }}
 
        body {{
            font-family: Arial, Helvetica, sans-serif;
            margin: 0;
            padding: 30px;
            background-color: #f1f5f9;
            color: #1e293b;
        }}
 
        .container {{
            max-width: 1100px;
            margin: auto;
        }}
 
        .header {{
            background: #17365d;
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 25px;
        }}
 
        .header h1 {{
            margin-top: 0;
            margin-bottom: 10px;
        }}
 
        .header p {{
            margin-bottom: 0;
            color: #dbeafe;
        }}
 
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 18px;
            margin-bottom: 25px;
        }}
 
        .card {{
            background: white;
            padding: 22px;
            border-radius: 10px;
            border-left: 5px solid #2563eb;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}
 
        .card h3 {{
            margin: 0 0 12px;
            font-size: 14px;
            color: #64748b;
        }}
 
        .card p {{
            margin: 0;
            font-size: 28px;
            font-weight: bold;
            overflow-wrap: anywhere;
        }}
 
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            overflow-x: auto;
        }}
 
        h2 {{
            color: #17365d;
            margin-top: 0;
        }}
 
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 15px;
            font-size: 14px;
        }}
 
        th, td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            text-align: left;
        }}
 
        th {{
            background-color: #dbeafe;
            color: #17365d;
        }}
 
        tr:hover {{
            background-color: #f8fafc;
        }}
 
        .notice {{
            padding: 15px;
            background: #eff6ff;
            border-radius: 8px;
        }}
 
        .footer {{
            text-align: center;
            color: #64748b;
            font-size: 13px;
            padding: 15px;
        }}
 
        @media (max-width: 600px) {{
            body {{
                padding: 12px;
            }}
 
            .header, .section {{
                padding: 18px;
            }}
        }}
    </style>
</head>
 
<body>
    <div class="container">
 
        <div class="header">
            <h1>AutoReport Data Report</h1>
            <p>Automated Data Analytics Report</p>
        </div>
 
        <div class="summary">
            <div class="card">
                <h3>Total Rows</h3>
                <p>{len(data)}</p>
            </div>
 
            <div class="card">
                <h3>Total Columns</h3>
                <p>{len(data.columns)}</p>
            </div>
 
            <div class="card">
                <h3>Numeric Columns</h3>
                <p>{len(numeric_data.columns)}</p>
            </div>
        </div>
 
        <div class="section">
            <h2>Dataset Preview</h2>
            <p>Showing up to the first 20 rows of the dataset.</p>
            {table_html}
        </div>
 
        <div class="section">
            <h2>Statistical Summary</h2>
            <p>
                Review the count, mean, standard deviation,
                minimum, quartiles, and maximum for numeric columns.
            </p>
            {statistics_html}
        </div>
 
        <div class="footer">
            Generated by AutoReport | Automated Report and Analytics Generator
        </div>
 
    </div>
</body>
</html>
"""
 
    output.write_text(html, encoding="utf-8")
 
    return str(output)