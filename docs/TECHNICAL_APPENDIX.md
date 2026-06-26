# Technical Appendix

## Rebuild

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

For an exact resolver-locked environment, use:

```powershell
uv sync --all-extras
```

`requirements.txt` installs the editable project with development tools.
`uv.lock` records the exact resolved package graph.

Run checks:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

Rebuild all generated daily data and figures:

```powershell
python scripts/build_all.py
```

Run the dashboard:

```powershell
streamlit run app.py
```

For time-boxed review paths, see [docs/REVIEWER_GUIDE.md](REVIEWER_GUIDE.md).
For a practical clean-clone rebuild sequence, see
[docs/REPRODUCIBILITY_CHECKLIST.md](REPRODUCIBILITY_CHECKLIST.md).

Unified task runner:

```powershell
python scripts/run_task.py build-daily
python scripts/run_task.py monthly-sample --min-train-months 24
python scripts/run_task.py build-monthly-real
python scripts/run_task.py validate-monthly-real
python scripts/run_task.py lint
python scripts/run_task.py test
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
- `src/gprobs/analysis/local_projection.py`: dynamic abnormal-return response
  paths.
- `src/gprobs/analysis/drawdown_model.py`: drawdown-risk Prediction Lab
  classifiers and diagnostics.
- `src/gprobs/analysis/evidence_summary.py`: compact model comparison table.
- `src/gprobs/analysis/rolling_sensitivity.py`: rolling GPR beta.
- `src/gprobs/data/monthly_sample.py`: deterministic monthly benchmark sample
  data.
- `src/gprobs/data/monthly_sources.py`: monthly real source config loading,
  redaction, hashing, and common-sample alignment.
- `src/gprobs/data/fama_french.py`: Kenneth French developed/emerging factor
  zip parsing.
- `src/gprobs/features/monthly_panel.py`: monthly aggregate analysis panel.
- `src/gprobs/analysis/monthly_benchmark.py`: monthly HAC spread regression and
  guarded panel interaction helper.
- `src/gprobs/analysis/forecasting.py`: expanding-window forecast generation.
- `src/gprobs/analysis/forecast_metrics.py`: forecast metrics and OOS R2.
- `scripts/run_task.py`: unified Windows-friendly task runner.
- `scripts/validate_monthly_benchmark.py`: monthly benchmark data/result
  validation.
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
- `data/processed/drawdown_model_predictions.csv`
- `data/processed/drawdown_model_threshold_metrics.csv`
- `data/processed/drawdown_model_calibration.csv`
- `data/processed/drawdown_model_lift.csv`
- `data/processed/drawdown_country_risk_summary.csv`
- `data/processed/drawdown_feature_importance.csv`
- `data/processed/evidence_summary.csv`
- `data/processed/rolling_gpr_beta.csv`
- `reports/RESULTS_BRIEF.md`
- `reports/screenshots/dashboard_overview.png`
- `reports/screenshots/dashboard_robustness.png`
- `reports/screenshots/dashboard_panel_regression.png`
- `reports/figures/gpr_and_group_returns.png`

Monthly benchmark generated files are also ignored by Git and can be rebuilt:

- `data/processed/monthly_benchmark/sample_gpr_monthly.csv`
- `data/processed/monthly_benchmark/sample_market_returns_monthly.csv`
- `data/processed/monthly_benchmark/sample_gdelt_country_monthly.csv`
- `data/processed/monthly_benchmark/sample_macro_controls_monthly.csv`
- `data/processed/monthly_benchmark/sample_analysis_panel.csv`
- `data/processed/monthly_benchmark/gpr_monthly.csv`
- `data/processed/monthly_benchmark/market_returns_monthly.csv`
- `data/processed/monthly_benchmark/gdelt_country_monthly.csv`
- `data/processed/monthly_benchmark/macro_controls_monthly.csv`
- `data/processed/monthly_benchmark/analysis_panel.csv`
- `data/metadata/monthly_benchmark/source_manifest.json`
- `data/metadata/monthly_benchmark/analysis_panel_manifest.json`
- `data/metadata/monthly_benchmark/source_manifest_real.json`
- `data/metadata/monthly_benchmark/analysis_panel_manifest_real.json`
- `reports/tables/monthly_benchmark/sample_table_00_missingness.csv`
- `reports/tables/monthly_benchmark/sample_table_02_baseline_regressions.csv`
- `reports/tables/monthly_benchmark/sample_table_03_forecast_comparison.csv`

## Variable Definitions

For GPR-specific z-score and shock-alias details, see
`docs/GPR_FEATURE_DEFINITIONS.md`.

- `return`: daily ETF log return.
- `gpr`: daily geopolitical risk index.
- `gpr_change`: daily change in the geopolitical risk index.
- `gpr_change_z`: standardized daily GPR change. The name is reused across
  descriptive, regression, and Prediction Lab contexts; the GPR feature
  definitions note explains which versions are time-aware.
- `gpr_change_shock`: expanding-window top-quantile positive daily GPR-change
  indicator using only prior observations for the threshold.
- `gpr_change_shock_full_sample`: full-sample top-quantile positive daily
  GPR-change indicator retained for comparison only.
- `gpr_change_shock_expanding`: expanding-window top-quantile positive daily
  GPR-change indicator using only prior observations for the threshold.
- `gpr_shock_full_sample`: full-sample GPR-change shock indicator.
- `gpr_shock_expanding`: expanding-window GPR-change shock indicator.
- `gpr_shock`: compatibility alias for the expanding-window shock flag.
- `gpr_act`: GPR act subindex.
- `gpr_threat`: GPR threat subindex.
- `global_market_return`: daily ACWI log return.
- `vix_change`: daily VIX level change.
- `oil_change`: daily WTI crude oil futures level change.
- `dollar_return`: daily UUP log return.
- `us10y_change`: daily US 10-year yield proxy level change.
- `emerging_market`: indicator equal to 1 for emerging-market ETF proxies.
- `date_month`: month-start date for monthly benchmark observations.
- `market_id`: monthly aggregate market label, currently `developed` or
  `emerging`.
- `market_class`: monthly market class label used for benchmark grouping.
- `gpr_global`, `gprt_global`, `gpra_global`: monthly GPR level and subindexes.
- `ret_fwd_1m`, `ret_fwd_3m`, `ret_fwd_6m`: forward monthly excess returns.
- `spread_em_dev`: emerging minus developed monthly excess-return spread.
- `gdelt_risk_raw`, `gdelt_risk_z`: monthly GDELT risk placeholders or
  validated real features when added later.
- `drawdown_risk`: binary forward drawdown-risk label.
- `predicted_probability`: out-of-sample drawdown-risk probability from a
  purged chronological fold.
- `probability_decile`: within-model predicted-risk decile for calibration.
- `lift`: event-rate multiple versus the out-of-sample base event rate.

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
together. Date windows are removed inclusively. GPR changes are standardized
once on the full controlled sample and reused across all subsamples.

Quantile regressions use the same GPR-change terms as the panel regression and
estimate coefficients at the 10th, 25th, and 50th percentiles. Their p-values
are statsmodels QuantReg i.i.d. asymptotic p-values, not cluster-robust panel
p-values.

Local projections estimate cumulative market-model abnormal ETF return responses
for horizons 0 through 20 trading days after a GPR shock. For each ticker and
base date, the expected return path comes from a trailing pre-date market model
using `global_market_return`; the projection dependent variable is the forward
sum of observed ETF returns minus those expected returns.
Standard errors are clustered by ticker and date. The developed row reports the
base GPR-shock response. The emerging row reports the combined
developed-plus-interaction response, and its p-value is computed from that
combined estimate and standard error rather than from the interaction term
alone.

Event studies use daily GPR-change shocks. When multiple shock days occur inside
the minimum-gap window, the event date is the largest `gpr_change` in that
cluster rather than the first shock day.

Event-study robustness compares end-of-window cumulative abnormal returns across
90th- and 95th-percentile GPR-change shock definitions and 3-, 5-, and
10-trading-day post-shock windows. Endpoint p-values use a cross-sectional
t-test over event-ticker cumulative abnormal returns.

Prediction Lab compares six purged chronological-validation model variants per
fold: `constant_baseline`, `volatility_only`, `gpr_only`,
`market_controls_only`, `volatility_plus_gpr`, and `full_features`. Every saved
`predicted_probability` is out of sample. Training dates immediately before each
test fold are embargoed by the forward-label horizon, and incomplete
end-of-series forward labels are dropped.

Prediction Lab writes five diagnostic outputs beyond the original dataset,
metrics, and feature-importance files:

- `drawdown_model_predictions.csv`: fold/model probabilities with train/test
  date windows.
- `drawdown_model_threshold_metrics.csv`: precision, recall, F1, share flagged,
  and flagged event rate at thresholds 0.10 through 0.50.
- `drawdown_model_calibration.csv`: realized event rates by predicted-risk
  decile.
- `drawdown_model_lift.csv`: top-10-percent and top-20-percent event-rate lift.
- `drawdown_country_risk_summary.csv`: average predicted risk and realized
  event rate by country, market group, and model.

The latest rebuild shows modest ranking signal. The full-features model has
mean ROC AUC around `0.617`, average precision around `0.373`, and top-decile
lift around `1.47x`. The `gpr_only` model is weak, so the Prediction Lab should
be read as an exploratory risk-classification experiment, not a trading signal
or proof that GPR alone forecasts drawdowns.

The evidence summary table is not a new model. It gathers headline rows from
the existing event-study, regression, quantile, local-projection, and ML outputs
so the dashboard can compare methods in one place. It carries structured
`unit` and `inference` fields so estimates and p-values are labelled
consistently.

The results brief is a generated Markdown report. It is intended for quick
review and profile packaging, not as a substitute for the research note.

Monthly benchmark regressions use the developed/emerging aggregate return
spread as the dependent variable and HAC standard errors. This is an aggregate
benchmark layer. It must not be described as country-clustered panel evidence.

The monthly panel-interaction helper preserves a weak-cluster guard. Clustered
standard errors require at least three `market_id` clusters, so the current
two-market aggregate design intentionally rejects clustered panel inference.

Monthly forecasts use expanding windows. Each test month occurs after all
training months, and forecast metrics are aligned to common evaluation dates
before OOS R2 is calculated against the historical-mean benchmark.

Monthly real mode reads user-supplied sources from `config/sources.yml`. Local
source paths are hashed but redacted in manifests. HTTPS sources require an
expected SHA-256 hash and unsupported URL schemes are rejected.

## Known Caveats

- Free market data can revise or contain errors.
- ETF inception dates differ, so country coverage differs.
- ETF returns are USD returns, not pure local-currency index returns.
- GPR shocks can coincide with other macro-financial shocks.
- Results are associations, not causal estimates.
- Monthly sample mode is deterministic software validation only.
- Monthly real mode currently includes explicit placeholder GDELT and macro
  columns until validated real inputs are added.
