"""Git history extraction for co-change analysis."""

from __future__ import annotations

from pathlib import Path
import subprocess
import warnings

from .commit_parser import parse_commit_blocks


class GitHistoryError(RuntimeError):
    """Raised when git history extraction fails."""


def extract_commits(
    repo_path: Path,
    *,
    max_files_per_commit: int = 50,
    extensions: list[str] | None = None,
) -> list[list[str]]:
    """Extract filtered commit file lists for a repository path or subdirectory.

    The function resolves the git root, scopes history to the provided path,
    ignores merges, and parses file-level changes from `--name-status -M` output.
    """
    target_path = repo_path.resolve()
    if not target_path.exists():
        raise GitHistoryError(f"Path does not exist: {target_path}")

    repo_root = _resolve_repo_root(target_path)
    scope_argument = _build_scope_argument(repo_root, target_path)

    command = [
        "git",
        "-C",
        str(repo_root),
        "log",
        "--no-merges",
        "--name-status",
        "-M",
        "--pretty=format:",
    ]
    if scope_argument is not None:
        command.extend(["--", scope_argument])

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise GitHistoryError("`git` executable not found in PATH") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise GitHistoryError(f"Failed to read git history: {stderr or exc}") from exc

    return extract_commits_from_log_output(
        result.stdout,
        max_files_per_commit=max_files_per_commit,
        extensions=extensions,
    )


def extract_commits_from_log_output(
    raw_log_output: str,
    *,
    max_files_per_commit: int = 50,
    extensions: list[str] | None = None,
) -> list[list[str]]:
    """Parse and filter commit history from raw `git log` output."""
    commits = parse_commit_blocks(
        raw_log_output,
        max_files_per_commit=max_files_per_commit,
        extensions=extensions,
    )
    if len(commits) < 30:
        warnings.warn(
            "Insufficient commit history for reliable architecture analysis",
            stacklevel=2,
        )
    return commits


def _resolve_repo_root(target_path: Path) -> Path:
    probe_path = target_path if target_path.is_dir() else target_path.parent
    command = ["git", "-C", str(probe_path), "rev-parse", "--show-toplevel"]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise GitHistoryError("`git` executable not found in PATH") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise GitHistoryError(f"Not a git repository: {stderr or probe_path}") from exc

    repo_root = Path(result.stdout.strip())
    return repo_root.resolve()


def _build_scope_argument(repo_root: Path, target_path: Path) -> str | None:
    if target_path == repo_root:
        return None

    try:
        relative_path = target_path.relative_to(repo_root)
    except ValueError as exc:
        raise GitHistoryError(f"Path is outside repository root: {target_path}") from exc

    relative_str = relative_path.as_posix()
    return relative_str or None
