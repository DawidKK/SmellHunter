from typer.testing import CliRunner

from arch_audit.cli import app


runner = CliRunner()


def test_help_is_available() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "analyze" in result.stdout


def test_analyze_placeholder_output() -> None:
    result = runner.invoke(app, ["analyze", "./src"])
    assert result.exit_code == 0
    assert "Architecture Audit Report" in result.stdout
    assert "Target path: src" in result.stdout
