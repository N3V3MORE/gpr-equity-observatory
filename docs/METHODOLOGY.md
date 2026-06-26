# Methodology

GPR Equity Observatory combines a daily ETF empirical workflow with a monthly
developed/emerging benchmark workflow. The methods are complementary but not
interchangeable.

## Daily ETF Workflow

The daily ETF workflow studies how country ETF returns move around daily
geopolitical risk changes.

Main units:

- date
- ticker
- country
- market group

Main methods:

- GPR shock event studies
- market-model abnormal returns
- panel regressions with ETF fixed effects
- date fixed-effects interaction tests
- sample-robustness exclusions
- quantile regressions
- local projections
- rolling GPR sensitivities
- purged chronological drawdown classification

The daily workflow is the main dashboard product.

## Monthly Benchmark Workflow

The monthly benchmark workflow studies aggregate developed and emerging market
returns at monthly frequency.

Main units:

- month
- `developed` aggregate market
- `emerging` aggregate market

Main methods:

- deterministic sample-mode panel construction
- user-supplied real-mode source ingestion
- HAC spread regressions
- guarded panel-interaction helper
- expanding-window forecast comparisons
- OOS R2 against a historical-mean benchmark

The monthly benchmark is a lower-frequency benchmark layer. It is not the same
dataset as the daily ETF panel.

## Sample Mode

Sample mode exists to prove that the monthly benchmark software path works. It
is deterministic, safe for CI, and useful for tests. Sample mode is not
empirical evidence.

## Real Mode

Real mode uses user-supplied GPR and Kenneth French source files. Real mode
requires provenance manifests, source hashes, and validation checks. Real mode
outputs are local only by default.

## Inference Limits

The daily ETF regressions measure associations, not causal effects. GPR shocks
often coincide with other macro-financial news.

The monthly benchmark has only two aggregate markets. It can support a
developed/emerging spread regression with HAC standard errors, but it cannot
support credible country-clustered inference. It is not a country-panel proof.

The project is not a trading system and not investment advice.

## Forecasting Validation

Monthly forecasts use expanding windows. Each test month occurs after all
training months. Metrics are calculated on common forecast dates so model
comparisons use the same evaluation window.

OOS R2 is calculated against the historical-mean benchmark. Positive OOS R2 is
useful evidence for a benchmark model, but it is not a trading rule.

## Allowed Language

Use:

- associated with
- benchmark estimate
- response path
- validation design
- aggregate monthly comparison

Avoid:

- proves
- causes
- trading signal
- investment recommendation
- country-clustered monthly panel result
