"""Parsers for git log output used by history mining."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import PurePosixPath
import re

DEFAULT_EXTENSIONS = frozenset({".ts", ".tsx", ".js", ".jsx"})
DEFAULT_IGNORED_DIRECTORIES = frozenset(
    {"node_modules", "dist", "build", ".next", "coverage"}
)
_TEST_FILE_PATTERN = re.compile(r"\.(test|spec)\.ts$")


def parse_commit_blocks(
    raw_log_output: str,
    *,
    max_files_per_commit: int = 50,
    extensions: Iterable[str] | None = None,
    ignored_directories: Iterable[str] | None = None,
    ignore_tests: bool = True,
) -> list[list[str]]:
    """Parse `git log --name-status` output into filtered commit file lists.

    Input is expected to be grouped into commit blocks separated by blank lines.
    Supports rename lines (e.g. `R100 old new`) and maps historical paths to the
    latest known path within parsed history.
    """
    allowed_extensions = _normalize_extensions(extensions)
    ignored_dirs = set(ignored_directories or DEFAULT_IGNORED_DIRECTORIES)

    commits: list[list[str]] = []
    path_aliases: dict[str, str] = {}
    current_files: list[str] = []

    for line in raw_log_output.splitlines():
        stripped = line.strip()
        if not stripped:
            _finalize_commit(
                commits,
                current_files,
                allowed_extensions,
                ignored_dirs,
                ignore_tests,
                max_files_per_commit,
            )
            current_files = []
            continue

        parsed_files = _parse_change_line(stripped)
        if not parsed_files:
            continue

        if len(parsed_files) == 2:
            old_path, new_path = parsed_files
            canonical_new = _resolve_canonical_path(new_path, path_aliases)
            path_aliases[old_path] = canonical_new
            path_aliases[new_path] = canonical_new
            current_files.append(canonical_new)
            continue

        canonical_path = _resolve_canonical_path(parsed_files[0], path_aliases)
        current_files.append(canonical_path)

    _finalize_commit(
        commits,
        current_files,
        allowed_extensions,
        ignored_dirs,
        ignore_tests,
        max_files_per_commit,
    )

    return commits


def _parse_change_line(line: str) -> tuple[str, ...] | None:
    """Parse one `git log --name-status` line and return changed path(s)."""
    parts = line.split("\t")
    if not parts:
        return None

    status = parts[0]
    if status.startswith("R"):
        if len(parts) < 3:
            return None
        return parts[1], parts[2]

    if status.startswith("C"):
        if len(parts) < 3:
            return None
        # Copy keeps both files present in history; treat destination as changed.
        return (parts[2],)

    if len(parts) >= 2:
        return (parts[1],)

    # Fallback for plain name-only output lines.
    if "/" in status or "." in status:
        return (status,)

    return None


def _finalize_commit(
    commits: list[list[str]],
    current_files: list[str],
    allowed_extensions: set[str],
    ignored_dirs: set[str],
    ignore_tests: bool,
    max_files_per_commit: int,
) -> None:
    if not current_files:
        return

    filtered = _filter_and_deduplicate(
        current_files,
        allowed_extensions,
        ignored_dirs,
        ignore_tests,
    )
    if not filtered:
        return

    if len(filtered) > max_files_per_commit:
        return

    commits.append(filtered)


def _filter_and_deduplicate(
    files: list[str],
    allowed_extensions: set[str],
    ignored_dirs: set[str],
    ignore_tests: bool,
) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for file_path in files:
        if file_path in seen:
            continue
        if _should_ignore_file(file_path, allowed_extensions, ignored_dirs, ignore_tests):
            continue
        seen.add(file_path)
        result.append(file_path)
    return result


def _should_ignore_file(
    file_path: str,
    allowed_extensions: set[str],
    ignored_dirs: set[str],
    ignore_tests: bool,
) -> bool:
    normalized = file_path.strip().replace("\\", "/")
    if not normalized:
        return True

    path = PurePosixPath(normalized)
    if any(part in ignored_dirs for part in path.parts):
        return True

    if path.suffix not in allowed_extensions:
        return True

    if ignore_tests and _TEST_FILE_PATTERN.search(path.name):
        return True

    return False


def _resolve_canonical_path(path: str, path_aliases: dict[str, str]) -> str:
    normalized = path.strip().replace("\\", "/")
    while normalized in path_aliases and path_aliases[normalized] != normalized:
        normalized = path_aliases[normalized]
    return normalized


def _normalize_extensions(extensions: Iterable[str] | None) -> set[str]:
    raw = extensions or DEFAULT_EXTENSIONS
    normalized: set[str] = set()
    for extension in raw:
        value = extension.strip().lower()
        if not value:
            continue
        if not value.startswith("."):
            value = f".{value}"
        normalized.add(value)
    return normalized or set(DEFAULT_EXTENSIONS)
