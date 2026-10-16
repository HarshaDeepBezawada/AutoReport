import typer

app = typer.Typer(
    name="autoreport",
    help="Automated Report and Analytics Generator",
)


@app.callback()
def main():
    """
    AutoReport: Generate reports from your data.
    """
    pass


@app.command()
def hello():
    """
    Display a welcome message.
    """
    print("Welcome to AutoReport!")
    print("Your automated reporting project is ready.")


if __name__ == "__main__":
    app()