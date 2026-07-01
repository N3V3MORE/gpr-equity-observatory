# Future Agent Handoff

Internal maintainer note. This file is for local agents and maintainers, not
the public reviewer path.

Last updated: 2026-07-01

Read this before changing code, docs, data, or Git state.

Feature lock was lifted on 2026-06-26. Read `docs/FEATURE_LOCK.md` before
making any change. New features are allowed only when their scope is recorded
and the standing data and claim-safety guardrails are preserved.

## Current State

GPR Equity Observatory remains the destination repository. Next.js is the single user-facing app. Python remains the research and export backend.

The GeoRiskLab + GPR Equity Observatory merge completed Phases 0 through 9.
The historical merge branch was `codex/pre-merge-gpr-cleanup`; do not treat
that branch as the current delivery branch.

The public UI contract is:

- Python builds validated daily/monthly outputs.
- `scripts/export_frontend_data.py` writes JSON to `frontend/public/data`.
- `frontend/` renders the public app and does not run research logic.
- `src/gprobs/dashboard/export.py` is the dashboard-facing backend contract.

Generated ignored outputs may exist locally. Do not commit or delete generated
raw/processed data unless the user explicitly asks.

## Important Paths

- Project status note: `docs/PROJECT_STATUS.md`
- v5 scope note: `docs/V5_NEXT_FRONTEND_PLAN.md`
- Beginner restart scope note: `docs/BEGINNER_RESTART_SCOPE.md`
- Reviewer guide: `docs/REVIEWER_GUIDE.md`
- Reproducibility checklist: `docs/REPRODUCIBILITY_CHECKLIST.md`
- Technical appendix: `docs/TECHNICAL_APPENDIX.md`
- Research note: `docs/RESEARCH_NOTE.md`
- Source policy: `docs/DATA_SOURCES.md`
- Roadmap: `docs/ROADMAP.md`
- Feature-lock policy: `docs/FEATURE_LOCK.md`
- AI review context guide: `docs/internal/REVIEW_CONTEXT_FOR_AI_TOOLS.md`

## What Is Implemented

- Daily 20-country ETF panel remains the primary empirical workflow.
- Daily Caldara-Iacoviello GPR ingestion remains in place.
- Market controls remain available through no-key public sources.
- Event study, abnormal-return event study, robustness checks, panel
  regressions, sample-robustness checks, quantile regressions, local
  projections, rolling sensitivity, evidence summary, and generated results
  brief are in the main workflow.
- Prediction Lab extends the drawdown classifier with six model variants,
  out-of-sample prediction rows, Brier score, threshold metrics, calibration,
  lift, and country risk summaries.
- The Next.js app now has a beginner reader path, graph-first overview,
  readable event-study summary table, regression translation table, and
  generated-file map. These are presentation helpers; they do not change model
  calculations or empirical claims.
- Monthly benchmark sample mode exists as deterministic software validation.
- Monthly benchmark real mode exists for user-supplied local GPR and Kenneth
  French factor files.
- Source manifests and redaction rules exist for real monthly inputs.
- Monthly developed/emerging HAC spread regressions exist.
- Monthly expanding-window forecast comparisons exist.
- `scripts/run_task.py` is the unified command path for daily, monthly,
  frontend export, and frontend verification tasks.
- CI includes Python lint/tests, deterministic monthly sample pipeline, and
  frontend lint/build checks.

## What Was Intentionally Not Done

- GeoRiskLab was not copied wholesale into this repository.
- Monthly benchmark outputs are not mixed into the daily ETF panel.
- Monthly sample outputs are not treated as empirical evidence.
- Monthly real aggregate benchmark outputs are not presented as country-panel
  proof.
- GDELT is not presented as a current real-data finding.
- Country-specific GPR data is not integrated yet.
- FRED controls are not integrated because that requires an API-key decision.
- No custom project MCP server was added.

## Commands Future Agents Should Use

Prefer the locked environment:

```powershell
uv sync --all-extras
```

Run the full verification set before calling broad code work complete:

```powershell
uv run --all-extras ruff check .
uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q
uv run --all-extras python scripts/run_task.py monthly-sample --min-train-months 24
uv run --all-extras python scripts/run_task.py build-daily
uv run --all-extras python scripts/export_frontend_data.py
cd frontend
npm run lint
npm run build
```

Useful focused commands:

```powershell
uv run --all-extras python scripts/run_task.py lint
uv run --all-extras python scripts/run_task.py test
uv run --all-extras python scripts/run_task.py validate-monthly-sample
uv run --all-extras python scripts/run_task.py export-frontend
uv run --all-extras python scripts/run_task.py frontend-lint
uv run --all-extras python scripts/run_task.py frontend-build
```

`build-monthly-real` requires `config/sources.yml` and local source files. Do
not invent those paths or commit that config.

## Data And Output Policy

- Do not commit raw third-party market data.
- Do not commit local source files.
- Do not commit credentials.
- Do not commit `config/sources.yml`.
- Do not commit real generated monthly outputs unless the user explicitly
  chooses a publication policy.
- Keep sample outputs and real outputs separate in names, paths, docs, and UI
  text.
- Treat source manifests and validation checks as part of the research
  contract.

## Interpretation Rules

- This is not a trading system.
- This is not investment advice.
- Do not claim causality.
- Do not claim that emerging markets always react more strongly.
- Use cautious language such as "associated with", "conditional response",
  "risk-classification experiment", and "benchmark estimate".
- Daily ETF results and monthly benchmark results answer different questions.
- Monthly sample mode validates software behavior only.
- Monthly real mode is an aggregate benchmark layer, not country-clustered
  panel inference.
- Prediction Lab is out-of-sample risk classification, not a price forecast.

## Current Results To Preserve

The project's strongest current result is methodological: the repository now
has a reproducible, tested workflow that compares event-study, panel, quantile,
local-projection, rolling-sensitivity, Prediction Lab, and monthly benchmark
evidence.

The current empirical story is mixed:

- Controlled daily panel estimates are small and statistically weak.
- Emerging-market interaction evidence is not strong after controls.
- Event robustness depends on shock and window definitions.
- Quantile and local-projection results are useful diagnostics, not proof.
- Prediction Lab has modest ranking signal. The `gpr_only` model is weak.
- Monthly sample outputs are not empirical findings.

## First Five Minutes For A New Agent

1. Run `git status -sb`.
2. Read `AGENTS.md`, `docs/FEATURE_LOCK.md`, this file, and
   `docs/V5_NEXT_FRONTEND_PLAN.md`.
3. If the task involves AI-assisted internal review, read
   `docs/internal/REVIEW_CONTEXT_FOR_AI_TOOLS.md`.
4. Read `docs/PROJECT_STATUS.md` and `docs/ROADMAP.md`.
5. Run focused checks for the requested change before editing.
