from pathlib import Path
import subprocess

import pytest

from arch_audit.git_history import extract_commits


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_extract_commits_scopes_path_and_warns_for_sparse_history(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")

    _write(repo / "frontend" / "CheckoutForm.tsx", "export const x = 1;\n")
    _write(repo / "frontend" / "api" / "PaymentAPI.ts", "export const pay = () => {};\n")
    _write(repo / "backend" / "server.ts", "export const up = true;\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")

    _write(repo / "frontend" / "CheckoutForm.tsx", "export const x = 2;\n")
    _write(repo / "frontend" / "api" / "PaymentAPI.ts", "export const pay = () => 1;\n")
    _write(repo / "backend" / "server.ts", "export const up = false;\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "update frontend and backend")

    _write(repo / "frontend" / "CheckoutForm.test.ts", "describe('x', () => {});\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "add test file")

    with pytest.warns(UserWarning, match="Insufficient commit history"):
        commits = extract_commits(repo / "frontend")

    # backend changes are excluded by scope; test files are filtered out.
    assert commits
    assert all(all(path.startswith("frontend/") for path in commit) for commit in commits)
    flattened = [path for commit in commits for path in commit]
    assert all(not path.endswith(".test.ts") for path in flattened)
