# Feature Lock

Last updated: 2026-06-26

Status: lifted on 2026-06-26 by explicit user request: "Unlock feature lock"
followed by "All of it."

The GeoRiskLab + GPR Equity Observatory merge completed Phases 0 through 9.
Feature work is now unlocked across the roadmap, including dashboard
usability, prediction work, deployment/data strategy, FRED controls,
country-specific GPR, and GDELT scoping.

## What Unlock Means

New product, research, data, model, dashboard, or workflow features may now be
planned and implemented. Before implementation, record the chosen scope in a
plan, issue, or pull request so the change remains reviewable.

The completed merge scope remains the baseline:

- daily ETF GPR Observatory workflow
- monthly benchmark sample mode
- monthly benchmark real mode
- monthly HAC regressions
- monthly expanding-window forecast comparisons
- Monthly Benchmark dashboard tab
- source manifests and validation contracts
- consolidated documentation and profile packaging

## Standing Guardrails

Unlocking feature work does not relax the research, data, or claim-safety
rules:

- Do not commit raw third-party market data, credentials, or
  `config/sources.yml`.
- Do not commit real local monthly outputs unless the user chooses a
  publication policy.
- Keep daily ETF outputs and monthly benchmark outputs separate in names,
  paths, docs, and dashboard text.
- Keep sample mode visibly non-empirical.
- Do not describe results as causal unless the design supports it.
- Do not frame the project as investment advice or a trading system.
- Keep limitations visible for the monthly two-market aggregate benchmark.
- Prefer a new branch for larger features or risky refactors.

## Verification Gate

Before calling feature work complete, verify the relevant scope. For broad code
or dashboard changes, use:

```powershell
git status -sb
uv run --all-extras ruff check .
uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q
uv run --all-extras python scripts/run_task.py monthly-sample --min-train-months 24
uv run --all-extras python scripts/run_task.py build-daily
```

If dashboard behavior changes, also run a Streamlit smoke test.

## Current Next Moves

Feature work is unlocked. Good next moves include:

- push this branch and open a pull request
- decide public deployment policy
- decide whether real monthly benchmark outputs can be published
- improve dashboard usability
- extend the Prediction Lab
- plan FRED, country-specific GPR, or GDELT work with source validation
