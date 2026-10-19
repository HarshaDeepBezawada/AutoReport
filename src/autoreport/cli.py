
import typer

from autoreport.data_loader import load_data
from autoreport.analyzer import analyze_data
from autoreport.chart_generator import generate_chart
from autoreport.report_generator import generate_html_report
from autoreport.pdf_generator import generate_pdf_report

app = typer.Typer(
    name="autoreport",
    help="Automated Report and Analytics Generator",
)


@app.callback()
def main():
    """AutoReport: Generate reports from your data."""
    pass


@app.command()
def hello():
    """Display a welcome message."""
    print("Welcome to AutoReport!")
    print("Your automated reporting project is ready.")


@app.command()
def analyze(file_path: str):
    """Analyze a CSV, Excel, or JSON file."""
    try:
        data = load_data(file_path)
        results = analyze_data(data)

        print("\n===== AUTOREPORT ANALYSIS =====")
        print(f"File: {file_path}")

        for column, stats in results.items():
            print(f"\nColumn: {column}")
            print(f"Count: {stats['count']}")
            print(f"Total: {stats['total']}")
            print(f"Average: {stats['average']:.2f}")
            print(f"Median: {stats['median']:.2f}")
            print(f"Minimum: {stats['minimum']}")
            print(f"Maximum: {stats['maximum']}")

        print("\nAnalysis completed successfully!")

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        raise typer.Exit(code=1)


@app.command()
def chart(file_path: str, column: str = "Sales"):
    """Generate a chart from a CSV, Excel, or JSON file."""
    try:
        data = load_data(file_path)

        output_path = generate_chart(
            data=data,
            column=column,
            output_path=f"reports/{column.lower()}_chart.png",
        )

        print("\n===== AUTOREPORT CHART =====")
        print(f"Input file: {file_path}")
        print(f"Column: {column}")
        print(f"Chart saved to: {output_path}")

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        raise typer.Exit(code=1)


@app.command()
def report(file_path: str):
    """Generate an HTML report from a CSV, Excel, or JSON file."""
    try:
        data = load_data(file_path)

        output_path = generate_html_report(
            data=data,
            output_path="reports/report.html",
        )

        print("\n===== AUTOREPORT HTML REPORT =====")
        print(f"Input file: {file_path}")
        print(f"HTML report saved to: {output_path}")

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        raise typer.Exit(code=1)


@app.command()
def pdf(file_path: str):
    """Generate a PDF report from a CSV, Excel, or JSON file."""
    try:
        data = load_data(file_path)

        output_path = generate_pdf_report(
            data=data,
            output_path="reports/report.pdf",
        )

        print("\n===== AUTOREPORT PDF REPORT =====")
        print(f"Input file: {file_path}")
        print(f"PDF report saved to: {output_path}")

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

