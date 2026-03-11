"""CLI entrypoints for architecture audit."""

from pathlib import Path

import typer

app = typer.Typer(help="Analyze frontend architecture from Git commit history.")


@app.callback()
def main() -> None:
    """arch-audit command group."""


@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to analyze (e.g., ./src or ./frontend)."),
    max_files_per_commit: int = typer.Option(
        50,
        "--max-files-per-commit",
        min=1,
        help="Ignore commits touching more than this number of files.",
    ),
    min_cochange: int = typer.Option(
        1,
        "--min-cochange",
        min=1,
        help="Minimum co-change count required to keep an edge.",
    ),
    extensions: list[str] = typer.Option(
        [".ts", ".tsx", ".js", ".jsx"],
        "--extensions",
        help="Allowed file extensions for analysis.",
    ),
) -> None:
    """Run a placeholder architecture audit report."""
    typer.echo("Architecture Audit Report")
    typer.echo("=========================")
    typer.echo(f"Target path: {path}")
    typer.echo(f"max_files_per_commit={max_files_per_commit}")
    typer.echo(f"min_cochange={min_cochange}")
    typer.echo(f"extensions={','.join(extensions)}")
    typer.echo("")
    typer.echo("MVP scaffold ready. Analysis pipeline will be implemented next.")
