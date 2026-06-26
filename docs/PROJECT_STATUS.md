# GPR Equity Observatory Status

Last updated: 2026-06-26

This document is a plain-English status note for the current project state. It
separates what is implemented from what the evidence currently says.

For a requirement-by-requirement audit against the original project plan, see
`docs/IMPLEMENTATION_CHECKLIST.md`.

For future-agent continuation context, including branch state, completed merge
commits, verification commands, and remaining decisions, see
`docs/FUTURE_AGENT_HANDOFF.md`.

## Implemented

- 20-country ETF universe: 10 developed market proxies and 10 emerging market
  proxies.
- Daily ETF return panel from Yahoo Finance via `yfinance`.
- Daily Caldara-Iacoviello GPR data ingestion.
- No-key market controls: ACWI, VIX, WTI crude oil, US dollar ETF, and US
  10-year yield proxy.
- Data diagnostics: coverage and large-return flags.
- Event study using raw returns.
- Market-model abnormal-return event study.
- Event-study robustness checks across GPR-jump thresholds and event windows.
- Baseline, market-controlled, and date fixed-effects panel regressions.
- Panel sample-robustness checks excluding major crisis windows.
- Quantile regressions for tail-risk analysis.
- Local projections for dynamic abnormal-return response paths.
- Rolling GPR sensitivity by country.
- Simple drawdown-risk classifier with purged chronological validation.
- Compact evidence summary table for comparing methods.
- Generated plain-English results brief for quick review.
- Streamlit dashboard.
- One-command pipeline rebuild: `python scripts/build_all.py`.
- Unified task runner: `python scripts/run_task.py ...`.
- Deterministic monthly benchmark sample mode under the
  `monthly_benchmark_sample` dataset.
- User-supplied monthly benchmark real mode under the
  `monthly_benchmark_real` dataset.
- Source manifests and redaction rules for monthly real GPR and Kenneth French
  factor inputs.
- Monthly developed/emerging HAC spread regressions.
- Monthly expanding-window forecast comparisons with historical-mean
  benchmarks and OOS R2.
- Monthly benchmark validation for data contracts, source manifests, and model
  result tables.
- Automated test workflow for GitHub Actions.
- CI monthly sample pipeline job.

## Current Results

The strongest current result is methodological rather than a dramatic empirical
claim: the project now has a reproducible pipeline that can compare event-study,
panel, quantile, local-projection, rolling-sensitivity, and ML evidence.

The controlled panel regression estimates the developed-market GPR-jump
coefficient at about `-0.4` basis points per one-SD jump, with a p-value near
`0.325`. The controlled emerging-market interaction is about `-0.5` basis
points, with a p-value near `0.574`. The date fixed-effects H1 interaction is
also about `-0.6` basis points, with a p-value near `0.563`. That means the
current model does not give strong statistical evidence that emerging ETFs have
a different average GPR-jump response.

The sample-robustness checks keep the controlled GPR-jump coefficient negative
after excluding COVID and Russia-Ukraine windows, but the estimates remain small
and statistically weak. This argues against a strong emerging-market asymmetry
claim.

The quantile regressions are directionally interesting but not decisive. The
10th-percentile GPR-jump coefficient is about `-0.8` basis points with a p-value
near `0.271`, so it should not be presented as proof.

The local projections now use cumulative market-model abnormal returns. At the
20-day horizon, the developed-market response is near zero while the
emerging-market response is negative. These should still be treated as
response-path diagnostics rather than headline conclusions.

The drawdown classifier is exploratory. Mean ROC AUC is about `0.617`, average
precision is about `0.373`, and the mean drawdown event rate is about `28.6%`.
Rolling volatility is the largest feature by standardized coefficient; GPR
features are small in the current version.

The overview evidence table is deliberately mixed. For example, the baseline
panel coefficient is positive, while the controlled panel coefficient is
negative. That is a warning not to overstate a single headline result.

`reports/RESULTS_BRIEF.md` now gives a short generated summary of these results
for interviews, profile packaging, or quick project review.

The monthly benchmark layer is newly integrated as infrastructure. The
deterministic monthly sample pipeline is a software validation target. Real
monthly benchmark outputs require user-supplied source files and should be
interpreted as aggregate benchmark evidence, not country-panel proof.

## Interpretation Rules

- This is not a trading system.
- This is not investment advice.
- GPR shocks are not clean randomized experiments.
- ETF returns are USD returns, so they mix local equity movement and exchange
  rate exposure.
- The controlled sample starts in 2008 because ACWI starts then.
- WTI crude oil is used as a level change, not a log return, because WTI futures
  traded below zero in April 2020.
- Monthly sample outputs are not empirical findings.
- Monthly developed/emerging outputs must remain separate from the daily ETF
  panel.

## Next Useful Work

Good next options are:

- Capture refreshed dashboard screenshots now that the Monthly Benchmark tab is
  implemented.
- Add FRED controls if an API key is available.
- Add country-specific GPR data where coverage is reliable.
- Add GDELT only after the research note and robustness checks are clearer.
