# ChatGPT Web Analysis Guide

Use this file when asking ChatGPT web or another general-purpose reviewer to
analyze the project. It gives a compact reading path and warns against common
misreadings.

## Fast Context

GPR Equity Observatory is a reproducible economics research project about how
equity-market risk is associated with geopolitical risk shocks.

The public product is a Streamlit dashboard and research note built around a
daily 20-country ETF panel. A separate monthly developed/emerging benchmark
layer exists for reproducibility and aggregate comparison.

The current `main` branch includes the GeoRiskLab merge, dashboard
understandability/refactor work, monthly benchmark layer, and Prediction Lab
extension. As of 2026-06-26, `main` is pushed to `origin/main` at merge commit
`599e56b`.

## Best Files To Upload Or Paste

If ChatGPT web has a file limit, use this order:

1. `README.md`
2. `docs/CHATGPT_WEB_ANALYSIS_GUIDE.md`
3. `reports/RESULTS_BRIEF.md`
4. `docs/PROJECT_STATUS.md`
5. `docs/RESEARCH_NOTE.md`
6. `docs/TECHNICAL_APPENDIX.md`
7. `docs/REPRODUCIBILITY_CHECKLIST.md`
8. `docs/REVIEWER_GUIDE.md`
9. `pyproject.toml`
10. `app.py`
11. `src/gprobs/analysis/drawdown_model.py`
12. `src/gprobs/dashboard/outputs.py`
13. `scripts/run_task.py`
14. `tests/test_drawdown_model.py`
15. `tests/test_output_schemas.py`

For a code-focused review, add `src/gprobs/analysis/`, `src/gprobs/data/`,
`src/gprobs/features/`, `scripts/`, and `tests/`.

For a public/profile review, add `docs/PROFILE_PACKAGING.md`,
`docs/BLOG_POST_DRAFT.md`, `docs/LAUNCH_CHECKLIST.md`, and
`reports/screenshots/`.

## What Not To Upload

Do not upload or paste:

- `config/sources.yml`
- raw third-party market data
- local monthly source files
- credentials or `.env` files
- unredacted local manifests
- generated real monthly outputs unless a publication policy is chosen

Generated daily outputs under `data/processed/` can be rebuilt locally and are
not committed by default. If you need ChatGPT to inspect output schemas, use
`src/gprobs/dashboard/outputs.py` and `docs/TECHNICAL_APPENDIX.md` first.

## Architecture At A Glance

- `app.py`: Streamlit dashboard orchestration and tab rendering.
- `src/gprobs/dashboard/outputs.py`: dashboard CSV contracts and loaders.
- `src/gprobs/dashboard/components.py`: reusable Streamlit display helpers.
- `src/gprobs/dashboard/charts.py`: reusable Plotly chart helpers.
- `scripts/build_all.py`: full daily workflow rebuild.
- `scripts/run_task.py`: unified daily/monthly task runner.
- `src/gprobs/data/`: data ingestion, source metadata, diagnostics, and
  monthly real/sample source handling.
- `src/gprobs/features/`: daily and monthly feature construction.
- `src/gprobs/analysis/`: event studies, regressions, local projections,
  forecasting, rolling sensitivity, and drawdown Prediction Lab logic.
- `src/gprobs/reporting/results_brief.py`: generated Markdown results brief.
- `tests/`: data-contract, model-behavior, dashboard, docs, and task-runner
  tests.

## Data And Output Boundaries

The daily ETF workflow is the main empirical workflow:

- 20 country ETF proxies.
- Daily Caldara-Iacoviello GPR data.
- Public market controls.
- Event studies, panel regressions, quantile regressions, local projections,
  rolling sensitivity, and Prediction Lab outputs.

The monthly benchmark workflow is separate:

- deterministic sample mode for software validation
- real mode for user-supplied monthly GPR and Kenneth French factor files
- source manifests and redaction checks
- aggregate developed/emerging HAC regressions and expanding-window forecasts

Do not mix daily ETF outputs and monthly aggregate benchmark outputs as one
panel. Do not treat monthly sample mode as empirical evidence.

## Current Result Snapshot

The current empirical story is mixed and should stay cautious:

- Controlled daily panel estimates are small and statistically weak.
- The date fixed-effects emerging-market interaction is not strong evidence of
  a different emerging-market average response.
- Quantile and local-projection results are useful diagnostics, not proof.
- Event-study robustness depends on shock and window definitions.
- The Prediction Lab has modest ranking signal, not trading-grade forecast
  power.
- `gpr_only` is weak as a standalone drawdown-risk model.
- Volatility/full-feature models rank drawdown risk better than the standalone
  GPR model.

Current Prediction Lab summary after the latest rebuild:

- full-features mean ROC AUC: about `0.617`
- full-features average precision: about `0.373`
- mean out-of-sample base event rate: about `28.6%`
- full-features top-decile lift: about `1.47x`
- out-of-sample prediction rows: `454,860`

## Claim Rules

Use this wording:

- "associated with"
- "conditional response"
- "risk-classification experiment"
- "benchmark estimate"
- "mixed evidence"
- "not statistically strong"

Do not claim:

- causality
- investment advice
- a trading system. The project is not a trading system.
- strong emerging-market asymmetry
- country-clustered inference from the two-market monthly benchmark
- empirical findings from monthly sample mode

## Verification Commands

Use the locked environment when possible:

```powershell
uv sync --all-extras
uv run --all-extras ruff check .
uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q
uv run --all-extras python scripts/run_task.py monthly-sample --min-train-months 24
uv run --all-extras python scripts/run_task.py build-daily
uv run --all-extras streamlit run app.py
```

The most recent post-push validation on `main` passed:

- daily rebuild
- monthly sample task
- Ruff
- full pytest suite
- named `build-daily` task
- Streamlit HTTP smoke check
- output sanity checks for Prediction Lab probabilities, folds, and metric
  bounds

## Good Review Prompts

Use prompts like these:

- "Review this project for statistical overclaims and unclear evidence
  framing."
- "Review whether the README, status note, research note, and technical
  appendix agree with each other."
- "Review the Prediction Lab design for leakage, out-of-sample discipline, and
  interpretability."
- "Review the dashboard output contracts and tests for missing schema coverage."
- "Suggest documentation improvements without changing research conclusions."

Avoid asking ChatGPT to invent new findings from sample monthly data or ignored
generated files.
