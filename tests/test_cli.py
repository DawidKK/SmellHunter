from pathlib import Path

import pytest
from typer.testing import CliRunner

from arch_audit.cli import app


runner = CliRunner()


def test_help_is_available() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "analyze" in result.stdout


def _write_mock_log(path: Path, commit_count: int) -> None:
    lines: list[str] = []
    for i in range(commit_count):
        if i % 3 == 0:
            lines.extend(
                [
                    "M\tfrontend/CheckoutForm.tsx",
                    "M\tfrontend/api/PaymentAPI.ts",
                    "",
                ]
            )
        elif i % 3 == 1:
            lines.extend(
                [
                    "M\tfrontend/CheckoutButton.tsx",
                    "M\tfrontend/api/PaymentAPI.ts",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "M\tfrontend/CheckoutWidget.tsx",
                    "M\tfrontend/api/PaymentAPI.ts",
                    "",
                ]
            )

    path.write_text("\n".join(lines), encoding="utf-8")


def test_analyze_with_mock_log_file_prints_clusters_and_smells(tmp_path: Path) -> None:
    mock_log = tmp_path / "mock_git_log.txt"
    _write_mock_log(mock_log, commit_count=35)

    result = runner.invoke(
        app,
        [
            "analyze",
            "./frontend",
            "--mock-log-file",
            str(mock_log),
            "--distance-threshold",
            "0.6",
        ],
    )

    assert result.exit_code == 0
    assert "Architecture Audit Report" in result.stdout
    assert "Detected clusters:" in result.stdout
    assert "Cluster 1" in result.stdout
    assert "CCP violations:" in result.stdout
    assert "REP risks:" in result.stdout
    assert "CRP risks:" in result.stdout


def test_analyze_distance_threshold_changes_clustering(tmp_path: Path) -> None:
    mock_log = tmp_path / "mock_git_log.txt"
    _write_mock_log(mock_log, commit_count=35)

    wide = runner.invoke(
        app,
        [
            "analyze",
            "./frontend",
            "--mock-log-file",
            str(mock_log),
            "--distance-threshold",
            "0.9",
        ],
    )
    tight = runner.invoke(
        app,
        [
            "analyze",
            "./frontend",
            "--mock-log-file",
            str(mock_log),
            "--distance-threshold",
            "0.05",
        ],
    )

    assert wide.exit_code == 0
    assert tight.exit_code == 0
    assert wide.stdout.count("Cluster ") < tight.stdout.count("Cluster ")


def test_sparse_history_warning_appears_for_mock_history(tmp_path: Path) -> None:
    mock_log = tmp_path / "small_mock_git_log.txt"
    _write_mock_log(mock_log, commit_count=3)

    with pytest.warns(UserWarning, match="Insufficient commit history"):
        result = runner.invoke(
            app,
            ["analyze", "./frontend", "--mock-log-file", str(mock_log)],
        )

    assert result.exit_code == 0
