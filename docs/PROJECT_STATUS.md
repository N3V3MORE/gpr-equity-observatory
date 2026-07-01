# GPR Equity Observatory Status

Last updated: 2026-07-01

Next.js is the single user-facing app. Python remains the research and export backend. The frontend reads generated JSON from `frontend/public/data`.

This document separates what is implemented from what the evidence currently
says.

## Implemented

- 20-country daily ETF universe: 10 developed market proxies and 10 emerging
  market proxies.
- Daily ETF return panel from Yahoo Finance via `yfinance`.
- Daily Caldara-Iacoviello GPR data ingestion.
- No-key market controls: ACWI, VIX, WTI crude oil, US dollar ETF, and US
  10-year yield proxy.
- Event study, abnormal-return event study, robustness checks, panel
  regressions, sample-robustness checks, quantile regressions, local
  projections, rolling sensitivity, evidence summary, and generated results
  brief.
- Prediction Lab: purged chronological drawdown-risk classification diagnostics
  with out-of-sample predictions, calibration, lift, threshold metrics, and
  country risk summaries.
- Deterministic monthly benchmark sample mode under
  `monthly_benchmark_sample`.
- User-supplied monthly benchmark real mode under `monthly_benchmark_real`.
- Source manifests and redaction rules for monthly real GPR and Kenneth French
  factor inputs.
- Monthly developed/emerging HAC spread regressions.
- Monthly expanding-window forecast comparisons.
- Next.js app under `frontend/`.
- Beginner reader path, graph-first overview, readable event-study summary,
  regression translation table, and generated-file map in the Next.js app.
- Python exporter at `scripts/export_frontend_data.py` and
  `src/gprobs/dashboard/export.py`.
- Automated Python and frontend checks in the task runner and CI.

## Current Results

The strongest result is methodological: the project has a reproducible pipeline
that compares event-study, panel, quantile, local-projection, rolling,
Prediction Lab, and monthly benchmark evidence.

The controlled panel estimates remain small and statistically weak. The current
model does not give strong evidence that emerging ETFs have a different average
GPR-jump response after controls.

Prediction Lab is exploratory. The full-features model has modest ranking
signal, while the `gpr_only` model is weak. This means the current risk-ranking
signal mostly comes from volatility and the broader feature set, not from GPR
alone.

The overview evidence table is deliberately mixed. That is a warning not to
overstate a single headline result.

The monthly benchmark works as a separate local comparison layer. Sample mode
validates software behavior only. Real monthly outputs require user-supplied
source files and should be read as aggregate benchmark evidence, not
country-panel proof.

## Boundaries

- This is not a trading system.
- This is not investment advice.
- GPR shocks are not clean randomized experiments.
- ETF returns are USD returns, so they mix local equity movement and exchange
  rate exposure.
- The controlled sample starts in 2008 because ACWI starts then.
- Monthly developed/emerging outputs must remain separate from the daily ETF
  panel.

## Next Useful Work

- Decide whether to publish a static frontend snapshot.
- Decide whether real monthly benchmark outputs can be published.
- Keep reviewer-facing docs and screenshots current when major outputs or app
  views change.
- Scope any FRED, country-specific GPR, or GDELT extension before
  implementation.
