# Technical Appendix

## Rebuild

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run tests:

```powershell
pytest -q
```

Rebuild all generated data and figures:

```powershell
python scripts/build_all.py
```

Run the dashboard:

```powershell
streamlit run app.py
```

## Main Source Files

- `data/country_universe.csv`: country, ETF ticker, market group, and region.
- `src/gprobs/data/market_data.py`: ETF price downloads and country universe
  loading.
- `src/gprobs/data/gpr_data.py`: daily GPR ingestion and shock flags.
- `src/gprobs/data/market_controls.py`: public market-control construction.
- `src/gprobs/data/analysis_panel.py`: merge returns, country metadata, and GPR.
- `src/gprobs/data/diagnostics.py`: coverage and large-return checks.
- `src/gprobs/analysis/event_study.py`: raw and abnormal event studies.
- `src/gprobs/analysis/event_robustness.py`: event-study robustness checks.
- `src/gprobs/analysis/panel_regression.py`: mean panel regressions.
- `src/gprobs/analysis/panel_sample_robustness.py`: sample-exclusion checks.
- `src/gprobs/analysis/quantile_regression.py`: lower-tail regressions.
- `src/gprobs/analysis/local_projection.py`: dynamic response paths.
- `src/gprobs/analysis/drawdown_model.py`: drawdown-risk classifier.
- `src/gprobs/analysis/evidence_summary.py`: compact model comparison table.
- `src/gprobs/analysis/rolling_sensitivity.py`: rolling GPR beta.
- `src/gprobs/reporting/results_brief.py`: generated plain-English results brief.
- `app.py`: Streamlit dashboard.

## Generated Outputs

Generated files are intentionally ignored by Git and can be rebuilt:

- `data/raw/etf_adjusted_prices.csv`
- `data/raw/market_control_prices.csv`
- `data/processed/returns_panel.csv`
- `data/processed/gpr_daily.csv`
- `data/processed/market_controls.csv`
- `data/processed/analysis_panel.csv`
- `data/processed/group_return_summary.csv`
- `data/processed/country_coverage_summary.csv`
- `data/processed/large_return_flags.csv`
- `data/processed/event_windows.csv`
- `data/processed/event_study_summary.csv`
- `data/processed/event_windows_abnormal.csv`
- `data/processed/event_study_abnormal_summary.csv`
- `data/processed/event_robustness_summary.csv`
- `data/processed/panel_regression_baseline.csv`
- `data/processed/panel_regression_controlled.csv`
- `data/processed/panel_regression_date_fe.csv`
- `data/processed/panel_sample_robustness.csv`
- `data/processed/quantile_regression_results.csv`
- `data/processed/local_projection_results.csv`
- `data/processed/drawdown_model_dataset.csv`
- `data/processed/drawdown_model_metrics.csv`
- `data/processed/drawdown_feature_importance.csv`
- `data/processed/evidence_summary.csv`
- `data/processed/rolling_gpr_beta.csv`
- `reports/RESULTS_BRIEF.md`
- `reports/screenshots/dashboard_overview.png`
- `reports/screenshots/dashboard_robustness.png`
- `reports/screenshots/dashboard_panel_regression.png`
- `reports/figures/gpr_and_group_returns.png`

## Variable Definitions

- `return`: daily ETF log return.
- `gpr`: daily geopolitical risk index.
- `gpr_change`: daily change in the geopolitical risk index.
- `gpr_change_z`: standardized daily GPR change.
- `gpr_shock`: indicator for top-decile positive GPR jumps.
- `gpr_act`: GPR act subindex.
- `gpr_threat`: GPR threat subindex.
- `global_market_return`: daily ACWI log return.
- `vix_change`: daily VIX level change.
- `oil_change`: daily WTI crude oil futures level change.
- `dollar_return`: daily UUP log return.
- `us10y_change`: daily US 10-year yield proxy level change.
- `emerging_market`: indicator equal to 1 for emerging-market ETF proxies.

## Model Notes

Panel regressions use ETF fixed effects and standardized daily GPR changes. The
controlled panel regression adds global market, VIX, oil, dollar, and US
10-year yield controls. The H1 panel specification adds date fixed effects and
reports only `gpr_change_z:emerging_market`, because the common daily GPR jump is
absorbed by the date effects.

Panel standard errors are clustered by ticker and date in the main scripts. This
is more defensible than ticker-only clustering, but the ticker dimension still
has only 20 clusters, so p-values should be interpreted cautiously.

Panel sample robustness reruns the controlled model after excluding the
COVID-crash window, the Russia-Ukraine invasion window, and both windows
together. Date windows are removed inclusively.

Quantile regressions use the same GPR-change terms as the panel regression and
estimate coefficients at the 10th, 25th, and 50th percentiles.

Local projections estimate cumulative ETF return responses for horizons 0
through 20 trading days after a GPR shock.

Event-study robustness compares end-of-window cumulative abnormal returns across
90th- and 95th-percentile GPR-jump shock definitions and 3-, 5-, and
10-trading-day post-shock windows.

The drawdown classifier uses logistic regression with standardized features and
class balancing. Validation folds are chronological. No random time-series split
is used.

The evidence summary table is not a new model. It gathers headline rows from
the existing event-study, regression, quantile, local-projection, and ML outputs
so the dashboard can compare methods in one place.

The results brief is a generated Markdown report. It is intended for quick
review and profile packaging, not as a substitute for the research note.

## Known Caveats

- Free market data can revise or contain errors.
- ETF inception dates differ, so country coverage differs.
- ETF returns are USD returns, not pure local-currency index returns.
- GPR shocks can coincide with other macro-financial shocks.
- Results are associations, not causal estimates.
