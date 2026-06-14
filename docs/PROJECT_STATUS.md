# GPR Equity Observatory Status

Last updated: 2026-06-14

This document is a plain-English status note for the current project state. It
separates what is implemented from what the evidence currently says.

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
- Baseline and market-controlled panel regressions.
- Quantile regressions for tail-risk analysis.
- Local projections for dynamic response paths.
- Rolling GPR sensitivity by country.
- Simple drawdown-risk classifier with chronological validation.
- Streamlit dashboard.
- One-command pipeline rebuild: `python scripts/build_all.py`.
- Automated test workflow for GitHub Actions.

## Current Results

The strongest current result is methodological rather than a dramatic empirical
claim: the project now has a reproducible pipeline that can compare event-study,
panel, quantile, local-projection, rolling-sensitivity, and ML evidence.

The controlled panel regression estimates the main standardized GPR coefficient
at about `-0.000064`, with a p-value near `0.006`. The emerging-market
interaction is positive, about `0.000090`, but its p-value is about `0.127`.
That means the current model does not give strong statistical evidence that
emerging ETFs have a different average GPR response after controls.

The quantile regressions are directionally interesting but not decisive. The
10th-percentile GPR coefficient is more negative than the median coefficient,
which is consistent with downside concentration, but the p-values are not strong
enough to present as proof.

The local projections show small cumulative response estimates. Confidence
intervals are wide, especially for emerging markets, so these should be treated
as response-path diagnostics rather than headline conclusions.

The drawdown classifier is exploratory. Mean ROC AUC is about `0.614`, average
precision is about `0.370`, and the mean drawdown event rate is about `28.5%`.
Rolling volatility is the largest feature by standardized coefficient; GPR
features are small in the current version.

## Interpretation Rules

- This is not a trading system.
- This is not investment advice.
- GPR shocks are not clean randomized experiments.
- ETF returns are USD returns, so they mix local equity movement and exchange
  rate exposure.
- The controlled sample starts in 2008 because ACWI starts then.
- WTI crude oil is used as a level change, not a log return, because WTI futures
  traded below zero in April 2020.

## Next Useful Work

The next step should improve interpretation rather than add complexity. Good
options are:

- Write a compact research note from the current outputs.
- Add robustness checks for event-study windows and GPR shock thresholds.
- Add FRED controls if an API key is available.
- Add GDELT only after the research note and robustness checks are clearer.
