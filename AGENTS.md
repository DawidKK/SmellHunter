# AGENTS.md

## Project Overview

This project is a **CLI tool for analyzing frontend architecture using Git commit history**.

The tool mines Git history to detect **architectural coupling between files** and diagnose potential violations of component design principles:

- **REP — Reuse Equivalence Principle**
- **CCP — Common Closure Principle**
- **CRP — Common Reuse Principle**

The application analyzes **temporal coupling** (files that change together across commits) and uses **unsupervised machine learning** to identify clusters of files that likely belong together architecturally.

The tool must run from the **command line** and operate on an existing Git repository.

Example usage:

```
smell-hunter analyze ./src
```

Output should include:

- detected file clusters
- architectural smells
- REP / CCP / CRP violations

The tool should remain **simple and MVP-friendly**, but structured so that future improvements are possible.

---

# Core Concepts

## Temporal Coupling

Temporal coupling means that files frequently **change together in commits**.

Example commit history:

Commit 1
CheckoutForm.tsx
PaymentAPI.ts

Commit 2
CheckoutButton.tsx
PaymentAPI.ts

Commit 3
CheckoutForm.tsx
CheckoutButton.tsx

These relationships can be represented as a **co-change graph**.

Nodes:

```
file
```

Edges:

```
weight = number of commits where both files changed together
```

This graph becomes the basis for machine learning.

---

# Machine Learning Approach

The project must use **scikit-learn**.

ML should be **unsupervised**.

Primary ML tasks:

1. Construct **co-change matrix**
2. Convert it into **similarity matrix**
3. Cluster files based on similarity

## Selected Model: Agglomerative Clustering

The primary ML algorithm for this project must be:

```
Agglomerative Clustering
```

This is a **hierarchical clustering algorithm** that progressively merges similar data points.

Reasons for choosing it:

- Works well with **similarity / distance matrices**
- Does **not require labeled data**
- Does **not require specifying number of clusters in advance**
- Naturally models **hierarchical architecture structures**
- Works well for **small datasets (50–500 files)** typical for repositories
- Produces clusters that are easy to explain

Implementation should use **scikit-learn**:

```python
from sklearn.cluster import AgglomerativeClustering
```

Recommended configuration:

```
metric="precomputed"
linkage="average"
distance_threshold=<configurable>
n_clusters=None
```

---

## Similarity Metric

Use **Jaccard similarity** between files.

Formula:

```
similarity(A,B) =
commits where A and B changed together
/
commits where A OR B changed
```

Distance matrix used by clustering:

```
distance = 1 - similarity
```

---

# Architectural Smell Detection

## CCP Violations

Definition:

Components that change together should live together.

Detection logic:

1. Identify clusters via ML
2. Inspect directory structure of cluster files
3. If cluster files are spread across many directories → CCP violation

Example output:

```
CCP violation detected

Files frequently changing together:
CheckoutForm.tsx
CheckoutButton.tsx
PaymentAPI.ts

These files are located in different modules.
Consider grouping them into a common module.
```

---

## REP Violations

Definition:

Components reused together should be packaged together.

Approximation approach:

Combine:

- temporal coupling
- folder structure

If files frequently change together but belong to separate modules → REP risk.

---

## CRP Violations

Definition:

A module should not depend on components it does not use.

Approximation:

If files are imported but **rarely or never change together**, this may indicate unnecessary dependencies.

---

# Git History Mining

Git history is the main data source.

Preferred command:

```
git log --no-merges --name-only --pretty=format:
```

This returns file lists per commit.

Each block separated by an empty line represents a commit.

Example:

```
src/CheckoutForm.tsx
src/PaymentAPI.ts

src/CheckoutButton.tsx
src/PaymentAPI.ts
```

This should be parsed into:

```
[
  ["src/CheckoutForm.tsx", "src/PaymentAPI.ts"],
  ["src/CheckoutButton.tsx", "src/PaymentAPI.ts"]
]
```

---

# Important Edge Cases

The system must account for several Git-related pitfalls.

## Merge commits

Merge commits often include many unrelated files.

They must be ignored.

Use:

```
--no-merges
```

---

## Large refactor commits

Large commits often represent:

- file moves
- formatting changes
- dependency upgrades
- automated refactors

These commits distort coupling analysis.

Ignore commits touching too many files.

Recommended threshold:

```
ignore commits with > 50 files
```

---

## File renames

Renames break historical continuity.

Use rename detection:

```
git log --name-status -M
```

Example output:

```
R100 old_file new_file
```

Map both names to the same logical file.

---

## Generated or build artifacts

Generated files change frequently and must be ignored.

Ignore directories:

```
node_modules
dist
build
.next
coverage
```

---

## Test files

Test files often change together with implementation.

Tests should either be ignored or handled separately.

Ignore patterns:

```
*.test.ts
*.spec.ts
```

---

## Sparse commit history

Small repositories may not have enough data.

If commit count < 30, the tool should warn:

```
Insufficient commit history for reliable architecture analysis
```

---

## Monorepo structures

Repositories may contain multiple systems.

Example:

```
frontend/
backend/
mobile/
```

The CLI must allow **scoping analysis to a directory**.

Example:

```
smell-hunter analyze ./frontend
```

---

## Binary files

Ignore non-source files.

Allowed extensions:

```
.ts
.tsx
.js
.jsx
```

---

# Graph Construction

Construct co-change graph.

Nodes:

```
files
```

Edges:

```
co-change frequency
```

Example:

```
CheckoutForm.tsx <-> PaymentAPI.ts weight=3
CheckoutButton.tsx <-> PaymentAPI.ts weight=2
```

Use **NetworkX** for graph construction.

---

# CLI Requirements

The application must expose a CLI.

Suggested command:

```
smell-hunter analyze <path>
```

Optional flags:

```
--max-files-per-commit
--min-cochange
--extensions
```

---

# Python Environment

This project must use **uv** for dependency management.

Required dependencies:

```
uv add scikit-learn
uv add networkx
uv add numpy
uv add typer
```

Optional:

```
uv add gitpython
```

---

# Recommended Project Structure

```
smell_hunter/
    __init__.py

    cli.py
    git_history.py
    commit_parser.py

    cochange_matrix.py
    similarity.py

    clustering.py
    smell_detection.py

    filters.py

main.py
AGENTS.md
pyproject.toml
```

Responsibilities:

**git_history.py**

- extract commit history

**commit_parser.py**

- convert raw git output into structured commits

**cochange_matrix.py**

- build co-change counts

**similarity.py**

- compute similarity metrics

**clustering.py**

- run Agglomerative Clustering using scikit-learn

**smell_detection.py**

- detect REP / CCP / CRP violations

**cli.py**

- CLI interface

---

# Expected CLI Output

Example:

```
Architecture Audit Report
=========================

Analyzed commits: 312

Detected clusters:

Cluster 1
---------
CheckoutForm.tsx
CheckoutButton.tsx
PaymentAPI.ts

Potential CCP violation:
Files frequently change together but are located in different modules.

Cluster 2
---------
Dashboard.tsx
Chart.tsx
UserCard.tsx

Possible REP issue:
These components appear strongly coupled but are packaged separately.
```

---

# Implementation Priorities (Hackathon)

The MVP should focus on:

1. Git history mining
2. Co-change matrix generation
3. Jaccard similarity calculation
4. Agglomerative clustering using scikit-learn
5. Basic architecture smell reporting

---

# Non-Goals (for MVP)

Do NOT implement:

- AST parsing
- dependency graph extraction
- LLM-based analysis
- deep learning models

The focus is **Git history mining + ML clustering**.

---

# Quality Guidelines

The code should:

- remain modular
- be easy to extend
- handle large repositories efficiently
- avoid loading entire Git history into memory if possible
- use streaming when parsing Git output

---

# Summary

This tool mines **Git commit history** to build a **co-change graph**, uses **Agglomerative Clustering (scikit-learn)** to detect logical component groups, and compares those groups with the repository structure to identify **architecture principle violations**.
