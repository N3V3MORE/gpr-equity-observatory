# Technical Appendix

Next.js is the single user-facing app. Python remains the research and export backend. The frontend reads generated JSON from `frontend/public/data`.

## Rebuild

```powershell
python -m pip install -r requirements.txt
uv sync --all-extras
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
python scripts/build_all.py
python scripts/export_frontend_data.py
cd frontend
npm run dev
npm run build
```

Useful task-runner commands:

```powershell
python scripts/run_task.py build-daily
python scripts/run_task.py monthly-sample --min-train-months 24
python scripts/run_task.py build-monthly-real
python scripts/run_task.py validate-monthly-real
python scripts/run_task.py export-frontend
python scripts/run_task.py frontend-lint
python scripts/run_task.py frontend-build
python scripts/run_task.py lint
python scripts/run_task.py test
```

## Main Source Files

- `src/gprobs/data/market_data.py`: ETF price downloads and country universe
  loading.
- `src/gprobs/data/gpr_data.py`: daily GPR ingestion and shock flags.
- `src/gprobs/data/analysis_panel.py`: daily ETF/GPR/metadata merge.
- `src/gprobs/analysis/`: event studies, regressions, quantile regressions,
  local projections, rolling sensitivity, and Prediction Lab models.
- `src/gprobs/data/monthly_sources.py`: monthly real source config loading,
  redaction, hashing, and common-sample alignment.
- `src/gprobs/analysis/monthly_benchmark.py`: monthly HAC benchmark
  regressions.
- `src/gprobs/analysis/forecasting.py`: expanding-window monthly forecasts.
- `src/gprobs/dashboard/export.py`: dashboard-facing backend JSON contract.
- `scripts/export_frontend_data.py`: writes `frontend/public/data/*.json`.
- `frontend/src/`: Next.js presentation layer.
- `scripts/run_task.py`: Windows-friendly task runner.

## Generated Outputs

Generated files are intentionally ignored by Git and can be rebuilt:

- daily raw and processed files under `data/raw` and `data/processed`
- source and analysis manifests under `data/metadata`
- monthly benchmark outputs under `data/processed/monthly_benchmark`
- monthly benchmark tables under `reports/tables/monthly_benchmark`
- chart-ready frontend JSON under `frontend/public/data`
- static Next.js output under `frontend/out`

Important daily outputs include:

- `analysis_panel.csv`
- `gpr_daily.csv`
- `group_return_summary.csv`
- `event_study_abnormal_summary.csv`
- `event_robustness_summary.csv`
- `panel_regression_controlled.csv`
- `panel_regression_date_fe.csv`
- `quantile_regression_results.csv`
- `local_projection_results.csv`
- `rolling_gpr_beta.csv`
- Prediction Lab metrics, calibration, lift, threshold, country-risk, and
  feature-importance CSVs
- `evidence_summary.csv`

## Variable Definitions

For GPR-specific z-score and shock-alias details, see
`docs/GPR_FEATURE_DEFINITIONS.md`.

- `return`: daily ETF log return.
- `gpr`: daily geopolitical risk index.
- `gpr_change`: daily change in the geopolitical risk index.
- `gpr_change_z`: standardized daily GPR change.
- `gpr_change_shock`: expanding-window top-quantile positive daily GPR-change
  indicator.
- `global_market_return`, `vix_change`, `oil_change`, `dollar_return`,
  `us10y_change`: market controls.
- `emerging_market`: indicator equal to 1 for emerging-market ETF proxies.
- `date_month`: month-start date for monthly benchmark observations.
- `market_id` and `market_class`: monthly aggregate market labels.
- `spread_em_dev`: emerging minus developed monthly excess-return spread.
- `drawdown_risk`: binary forward drawdown-risk label.
- `predicted_probability`: out-of-sample drawdown-risk probability.
- `lift`: event-rate multiple versus the out-of-sample base event rate.

## Model Notes

Panel regressions use ETF fixed effects and standardized daily GPR changes. The
controlled panel regression adds global market, VIX, oil, dollar, and US
10-year yield controls. The date fixed-effects specification reports the
emerging-market interaction because the common daily GPR jump is absorbed by
date effects.

Event studies use daily GPR-change shocks. Event-study robustness compares
end-of-window cumulative abnormal returns across shock thresholds and
post-shock windows.

Quantile regressions estimate lower-tail associations. Local projections
estimate cumulative market-model abnormal ETF return responses after shocks.

Prediction Lab compares purged chronological-validation model variants. Every
saved `predicted_probability` is out of sample. The current rebuild shows
modest ranking signal in the full feature set and weak performance for GPR
alone, so the lab should be read as an exploratory risk-classification
experiment.

Monthly benchmark regressions use the developed/emerging aggregate return
spread with HAC standard errors. This layer is separate from the daily ETF
panel.

## Known Caveats

- Free market data can revise or contain errors.
- ETF inception dates differ, so country coverage differs.
- ETF returns are USD returns, not pure local-currency index returns.
- GPR shocks can coincide with other macro-financial shocks.
- Results are associations, not causal estimates.
- Monthly sample mode is deterministic software validation only and not
  empirical evidence.
- Monthly real mode is an aggregate benchmark, not a country-panel proof.
- The project is not a trading system and not investment advice.
