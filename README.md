# GPR Equity Observatory

GPR Equity Observatory is a reproducible economics research project on how
equity markets respond to geopolitical risk shocks.

The first MVP focuses on a clean data foundation:

- 20 country ETF proxies: 10 developed markets and 10 emerging markets.
- Daily adjusted ETF prices from `yfinance`.
- Daily log returns.
- A clear distinction between raw data, processed data, and code.

This is not an investment advice or trading project. It is an educational
research project about geopolitical risk, international equity markets, and
emerging-versus-developed market asymmetry.

## Project Layout

```text
data/country_universe.csv        MVP country and ETF list
data/raw/                        Downloaded source data, not committed
data/processed/                  Built research datasets, not committed
scripts/build_returns_panel.py   Builds the first ETF returns panel
scripts/build_gpr_dataset.py      Builds the daily GPR dataset
scripts/build_analysis_panel.py   Combines returns, country metadata, and GPR
scripts/build_market_controls.py  Builds no-key public market controls
scripts/plot_initial_trends.py    Creates the first GPR/returns figure
scripts/run_data_diagnostics.py   Builds coverage and large-return checks
scripts/run_event_study.py        Runs the first GPR shock event study
scripts/run_event_robustness.py   Checks event-study thresholds and windows
scripts/run_panel_regression.py   Runs the baseline panel regression
scripts/run_panel_sample_robustness.py Checks crisis-window sensitivity
scripts/run_quantile_regression.py Estimates tail-risk quantile regressions
scripts/run_local_projections.py  Estimates dynamic GPR shock response paths
scripts/run_drawdown_model.py     Trains a simple drawdown-risk classifier
scripts/run_evidence_summary.py   Builds a compact model comparison table
scripts/run_rolling_sensitivity.py Builds rolling GPR sensitivity estimates
scripts/build_all.py              Rebuilds the full MVP pipeline in order
app.py                            Streamlit dashboard
src/gprobs/                      Reusable project code
tests/                           Checks for data and feature logic
```

## Setup

```powershell
python -m pip install -r requirements.txt
pytest -q
```

For a plain-English summary of what is currently implemented and what the
results mean, see `docs/PROJECT_STATUS.md`.

The current research-note draft is in `docs/RESEARCH_NOTE.md`, with technical
details in `docs/TECHNICAL_APPENDIX.md`.

Profile and communication drafts are in `docs/PROFILE_PACKAGING.md` and
`docs/BLOG_POST_DRAFT.md`.

## Build the First Returns Panel

```powershell
python scripts/build_all.py
streamlit run app.py
```

Or run the pipeline step by step:

```powershell
python scripts/build_returns_panel.py
python scripts/build_gpr_dataset.py
python scripts/build_market_controls.py
python scripts/build_analysis_panel.py
python scripts/run_data_diagnostics.py
python scripts/run_event_study.py
python scripts/run_event_robustness.py
python scripts/run_panel_regression.py
python scripts/run_panel_sample_robustness.py
python scripts/run_quantile_regression.py
python scripts/run_local_projections.py
python scripts/run_drawdown_model.py
python scripts/run_evidence_summary.py
python scripts/run_rolling_sensitivity.py
python scripts/plot_initial_trends.py
streamlit run app.py
```

These commands download adjusted ETF prices, download daily GPR data, and write:

- `data/raw/etf_adjusted_prices.csv`
- `data/processed/returns_panel.csv`
- `data/processed/gpr_daily.csv`
- `data/processed/market_controls.csv`
- `data/processed/analysis_panel.csv`
- `data/processed/group_return_summary.csv`
- `reports/figures/gpr_and_group_returns.png`
- `data/processed/country_coverage_summary.csv`
- `data/processed/large_return_flags.csv`
- `data/processed/event_windows.csv`
- `data/processed/event_study_summary.csv`
- `data/processed/event_windows_abnormal.csv`
- `data/processed/event_study_abnormal_summary.csv`
- `data/processed/event_robustness_summary.csv`
- `data/processed/panel_regression_baseline.csv`
- `data/processed/panel_regression_summary.txt`
- `data/processed/panel_regression_controlled.csv`
- `data/processed/panel_regression_controlled_summary.txt`
- `data/processed/panel_sample_robustness.csv`
- `data/processed/quantile_regression_results.csv`
- `data/processed/local_projection_results.csv`
- `data/processed/drawdown_model_dataset.csv`
- `data/processed/drawdown_model_metrics.csv`
- `data/processed/drawdown_feature_importance.csv`
- `data/processed/evidence_summary.csv`
- `data/processed/rolling_gpr_beta.csv`

## Data Note

ETF returns are USD returns. That means they include both local equity-market
movement and exchange-rate exposure against the US dollar. This is useful for
studying global investor exposure, but it is not the same as a pure local market
index return.

The controlled regression uses no-key public market proxies from Yahoo Finance:
ACWI for global equities, `^VIX` for risk aversion, `CL=F` for WTI crude oil,
UUP for the US dollar, and `^TNX` for the US 10-year yield index. The controlled
sample starts later because ACWI begins in 2008. Oil is used as a daily level
change, not a log return, because WTI futures traded below zero in April 2020.

The panel sample-robustness output reruns the controlled model after excluding
COVID-crash and Russia-Ukraine invasion windows.

The abnormal-return event study estimates a simple pre-event market model for
each ETF using ACWI as the market proxy, then subtracts the expected return from
the observed ETF return inside the event window.

The event-study robustness output compares the final cumulative abnormal return
across alternative GPR shock thresholds and event-window lengths.

The local projection output estimates cumulative ETF return responses at several
daily horizons after GPR shock days. It is an association model, not a causal
claim.

The quantile regression output compares the GPR association at lower return
quantiles against the median. This is useful for checking whether GPR matters
more during bad market-return states than during typical days.

The drawdown classifier predicts whether a country ETF has a forward
20-trading-day cumulative log-return drawdown of at least 5 percent. It uses
chronological validation, not random train/test splits.

The evidence summary table collects the main model outputs into one
plain-English comparison table for the dashboard and research note.
