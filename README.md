# 🕵️ SmellHunter

SmellHunter is a CLI tool that mines Git history to reveal **architectural coupling** in frontend codebases.
It identifies files that frequently change together, clusters them with unsupervised ML, and reports potential violations of core component packaging principles.

> 📚 **Tech approach:** SmellHunter combines **Git history mining** (temporal co-change analysis) with **machine learning** (scikit-learn agglomerative clustering) to detect architectural smells.

## 🚀 Project Overview

Modern frontend repositories often accumulate hidden architectural coupling:

- components scattered across directories but changed together every sprint
- modules packaged by folder conventions instead of real change patterns
- weakly related files grouped together in ways that slow delivery

SmellHunter helps make this visible using **temporal coupling** from commit history.

### 🎯 What Problems It Solves

- Detects files that are tightly coupled in practice (not only in theory).
- Finds clusters of files that likely belong to the same architectural boundary.
- Flags risks related to REP, CCP, and CRP so teams can reduce change friction.
- Supports monorepo-style scoped analysis (`./frontend`, `./src`, etc.).

## 🧠 Core Principles (REP / CCP / CRP)

SmellHunter reports risks using practical approximations of these principles.

### 📦 REP — Reuse Equivalence Principle

**Definition:** Things reused together should be packaged together.

**Why it matters:** If two files are consistently changed/released together but live in separate modules, consumers may pull too much or coordinate across unnecessary boundaries.

**Example (nested structure):**

- `frontend/features/checkout/components/forms/CheckoutForm.tsx`
- `frontend/features/checkout/components/buttons/SubmitPaymentButton.tsx`
- `frontend/features/checkout/services/payment/PaymentGatewayClient.ts`
- `frontend/shared/lib/currency/formatMoney.ts`

If these files are consistently reused and changed together but are packaged across distant folders (`features/checkout` and `shared/lib`), SmellHunter marks a **REP risk**.

### 🧱 CCP — Common Closure Principle

**Definition:** Things that change together should close together (live in the same component/module boundary).

**Why it matters:** Frequent cross-module edits increase regression risk and slow down releases.

**Example (nested structure):**

- `frontend/features/checkout/pages/CheckoutPage.tsx`
- `frontend/features/checkout/components/summary/OrderSummaryCard.tsx`
- `frontend/features/payments/infrastructure/http/StripePaymentClient.ts`
- `frontend/shared/state/cart/cartSelectors.ts`

If a single product change repeatedly touches these files across multiple modules (`checkout`, `payments`, `shared/state`), SmellHunter can flag a **CCP violation**.

### 🪢 CRP — Common Reuse Principle

**Definition:** Don’t force consumers to depend on things they don’t use.

**Why it matters:** Over-grouped modules create accidental coupling and unnecessary rebuild/retest scope.

**Example (MVP approximation, nested structure):**

Cluster candidate:

- `frontend/features/dashboard/widgets/revenue/RevenueChart.tsx`
- `frontend/features/dashboard/widgets/activity/RecentActivityList.tsx`
- `frontend/features/auth/session/tokenStorage.ts`
- `frontend/shared/network/retry/backoffPolicy.ts`

If these files end up clustered together but show weak temporal cohesion (low average similarity), SmellHunter marks a **CRP risk** indicating likely over-grouping.

## ⚙️ How SmellHunter Works

1. Reads Git history (`git log --no-merges --name-status -M --pretty=format:`).
2. Applies filtering (extensions, test files, generated dirs, large commits).
3. Builds a co-change matrix and weighted co-change graph.
4. Computes Jaccard similarity and distance matrices.
5. Runs `AgglomerativeClustering` (scikit-learn) on precomputed distances.
6. Reports clusters and REP/CCP/CRP findings.

## 🛠️ Installation

### 📋 Prerequisites

- Python 3.11+
- `uv`
- `git`

### 📦 Install Dependencies (Project Local)

```bash
uv sync
```

### ▶️ Run Without Installation (Recommended During Development)

```bash
uv run smell-hunter --help
```

### 🧰 Install as a Local CLI Tool

```bash
uv tool install --from . smell-hunter
```

Then use:

```bash
smell-hunter --help
```

## 💻 Usage

### 🧪 Analyze Real Repository History

```bash
uv run smell-hunter analyze ./frontend
```

### 🎭 Analyze Mocked History Data

```bash
uv run smell-hunter analyze ./frontend --mock-log-file examples/mock_git_log.txt
```

### 🔧 Common Options

- `--max-files-per-commit` (default: `50`)
- `--min-cochange` (default: `1`)
- `--distance-threshold` (default: `0.85`)
- `--extensions` (default: `.ts,.tsx,.js,.jsx`)
- `--mock-log-file` (use text file in git-log name-status format)

## 🧷 Makefile Shortcuts

To simplify commands:

```bash
make help
make install
make test
make run
make run-mock
make run-mock-tight
```

You can override variables:

```bash
make run TARGET=./src DISTANCE=0.7
make run-mock MOCK_LOG=examples/mock_git_log.txt MIN_COCHANGE=2
```

## ✨ Example Output (Abridged)

```text
🕵️ SmellHunter Report
================================
📊 Summary
  Commits analyzed: 184
  Files in scope: 27

🧩 Detected clusters:
  Cluster 1
  ---------
  size=6 | avg_similarity=0.312 | avg_cochange=7.40
   • frontend/features/checkout/pages/CheckoutPage.tsx
   • frontend/features/checkout/components/forms/CheckoutForm.tsx
   • frontend/features/checkout/components/summary/OrderSummaryCard.tsx
   • frontend/features/payments/infrastructure/http/StripePaymentClient.ts
   • frontend/shared/state/cart/cartSelectors.ts
   • frontend/shared/lib/currency/formatMoney.ts

🧱 CCP violations:
  ⚠️ Cluster 1: Files in this cluster change together but are spread across directories (frontend/features/checkout, frontend/features/payments/infrastructure/http, frontend/shared/lib/currency, frontend/shared/state/cart).
```

## ✅ Testing

Run all tests:

```bash
uv run pytest
```

Or via Makefile:

```bash
make test
```

## 📝 Notes

- SmellHunter is intentionally MVP-focused: it uses Git history + ML clustering.
- It does not yet perform AST import graph analysis.
- CRP detection is currently heuristic and based on cluster cohesion.
