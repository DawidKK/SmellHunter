# 🕵️ SmellHunter

SmellHunter is a CLI that detects frontend architectural smells using:
- 📚 **Git history mining** (temporal co-change)
- 🤖 **Machine learning** (scikit-learn agglomerative clustering)

It highlights potential violations of:
- 📦 **REP** (Reuse Equivalence Principle)
- 🧱 **CCP** (Common Closure Principle)
- 🪢 **CRP** (Common Reuse Principle)

## 🚀 Why Use It

SmellHunter helps you quickly find:
- Files that repeatedly change together
- Candidate architectural clusters
- Cross-module coupling risks that slow delivery

## 🧩 Problems It Solves

- **Hidden coupling:** files in different modules that always change together
- **Architecture drift:** folder structure no longer matches real change boundaries
- **Slow feature delivery:** one small change requires touching many distant areas
- **Noisy releases:** unrelated components moved together because of poor packaging
- **Refactor blind spots:** hard to see where component boundaries should be redrawn

## 🧠 Principles in 30 Seconds

- 📦 **REP**: if things are reused together, they should be packaged together.
  Example: checkout UI + payment client always shipped together but split across modules.

- 🧱 **CCP**: if things change together, they should live together.
  Example: one feature change repeatedly touches UI, API adapter, and shared state in different folders.

- 🪢 **CRP**: avoid forcing dependencies on unused parts.
  Example (MVP heuristic): a weakly cohesive cluster suggests over-grouping.

## 🛠️ Install

Prerequisites: Python 3.11+, `uv`, `git`

```bash
uv sync
```

## 💻 Run

Generic form:

```bash
uv run smell-hunter analyze [path-to-directory]
```

Examples:

```bash
uv run smell-hunter analyze ./frontend
uv run smell-hunter analyze ./src
uv run smell-hunter analyze .
```

With mocked history:

```bash
uv run smell-hunter analyze ./frontend --mock-log-file examples/mock_git_log.txt
```

## 🔧 Common Options

- `--max-files-per-commit` (default: `50`)
- `--min-cochange` (default: `1`)
- `--distance-threshold` (default: `0.85`)
- `--extensions` (default: `.ts,.tsx,.js,.jsx`)

## 🧷 Makefile Shortcuts

```bash
make help
make run
make run-mock
make test
```

You can override vars:

```bash
make run TARGET=./src DISTANCE=0.7
```

## ✅ Test

```bash
uv run pytest
```
