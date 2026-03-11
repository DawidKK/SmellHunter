"""CLI entrypoints for architecture audit."""

from __future__ import annotations

from pathlib import Path

import typer

from .clustering import cluster_files
from .cochange_matrix import build_cochange_matrix
from .git_history import GitHistoryError, extract_commits, extract_commits_from_log_output
from .similarity import compute_distance_matrix, compute_jaccard_similarity
from .smell_detection import detect_smells

app = typer.Typer(help="Analyze frontend architecture from Git commit history.")


@app.callback()
def main() -> None:
    """smell-hunter command group."""


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
    distance_threshold: float = typer.Option(
        0.85,
        "--distance-threshold",
        min=0.000001,
        help="Agglomerative clustering distance threshold.",
    ),
    mock_log_file: Path | None = typer.Option(
        None,
        "--mock-log-file",
        help=(
            "Path to a text file containing mocked `git log --name-status -M --pretty=format:` "
            "output for testing without real history."
        ),
    ),
) -> None:
    """Run end-to-end architecture audit analysis."""
    try:
        if mock_log_file is not None:
            raw_output = mock_log_file.read_text(encoding="utf-8")
            commits = extract_commits_from_log_output(
                raw_output,
                max_files_per_commit=max_files_per_commit,
                extensions=extensions,
            )
            source = f"mock log file: {mock_log_file}"
        else:
            commits = extract_commits(
                path,
                max_files_per_commit=max_files_per_commit,
                extensions=extensions,
            )
            source = f"git history from: {path}"
    except FileNotFoundError as exc:
        raise typer.BadParameter(f"Mock log file not found: {mock_log_file}") from exc
    except GitHistoryError as exc:
        raise typer.Exit(code=_print_error(str(exc)))

    files, cochange_matrix, _graph = build_cochange_matrix(commits, min_cochange=min_cochange)
    similarity_matrix = compute_jaccard_similarity(cochange_matrix)
    distance_matrix = compute_distance_matrix(similarity_matrix)
    clusters = cluster_files(
        distance_matrix,
        distance_threshold=distance_threshold,
        file_names=files,
    )
    smells = detect_smells(
        clusters=clusters,
        files=files,
        cochange_matrix=cochange_matrix,
        similarity_matrix=similarity_matrix,
    )

    typer.echo("SmellHunter Report")
    typer.echo("=========================")
    typer.echo(f"Source: {source}")
    typer.echo(f"max_files_per_commit={max_files_per_commit}")
    typer.echo(f"min_cochange={min_cochange}")
    typer.echo(f"distance_threshold={distance_threshold}")
    typer.echo(f"extensions={','.join(extensions)}")
    typer.echo(f"Analyzed commits: {len(commits)}")
    typer.echo(f"Files in scope: {len(files)}")

    typer.echo("")
    typer.echo("Detected clusters:")
    if not clusters:
        typer.echo("(none)")
    else:
        for idx, cluster in enumerate(clusters, start=1):
            avg_similarity = _average_cluster_pair_value(cluster, similarity_matrix)
            avg_cochange = _average_cluster_pair_value(cluster, cochange_matrix)
            typer.echo("")
            typer.echo(f"Cluster {idx}")
            typer.echo("---------")
            typer.echo(
                f"size={len(cluster)} avg_similarity={avg_similarity:.3f} "
                f"avg_cochange={avg_cochange:.2f}"
            )
            for file_index in cluster:
                typer.echo(files[file_index])

    _print_smell_section("CCP violations", smells["ccp"])
    _print_smell_section("REP risks", smells["rep"])
    _print_smell_section("CRP risks", smells["crp"])


def _print_smell_section(title: str, findings: list[dict[str, object]]) -> None:
    typer.echo("")
    typer.echo(f"{title}:")
    if not findings:
        typer.echo("- none")
        return

    for finding in findings:
        cluster_id = finding["cluster_id"]
        message = finding["message"]
        typer.echo(f"- Cluster {cluster_id}: {message}")


def _print_error(message: str) -> int:
    typer.echo(f"Error: {message}", err=True)
    return 1


def _average_cluster_pair_value(cluster: list[int], matrix) -> float:
    if len(cluster) < 2:
        return 0.0
    values: list[float] = []
    for i in range(len(cluster)):
        for j in range(i + 1, len(cluster)):
            values.append(float(matrix[cluster[i], cluster[j]]))
    return sum(values) / len(values) if values else 0.0
