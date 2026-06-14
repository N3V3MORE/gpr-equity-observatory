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
scripts/plot_initial_trends.py    Creates the first GPR/returns figure
scripts/run_event_study.py        Runs the first GPR shock event study
scripts/run_panel_regression.py   Runs the baseline panel regression
app.py                            Streamlit dashboard
src/gprobs/                      Reusable project code
tests/                           Checks for data and feature logic
```

## Setup

```powershell
python -m pip install -r requirements.txt
pytest -q
```

## Build the First Returns Panel

```powershell
python scripts/build_returns_panel.py
python scripts/build_gpr_dataset.py
python scripts/build_analysis_panel.py
python scripts/plot_initial_trends.py
python scripts/run_event_study.py
python scripts/run_panel_regression.py
streamlit run app.py
```

These commands download adjusted ETF prices, download daily GPR data, and write:

- `data/raw/etf_adjusted_prices.csv`
- `data/processed/returns_panel.csv`
- `data/processed/gpr_daily.csv`
- `data/processed/analysis_panel.csv`
- `data/processed/group_return_summary.csv`
- `reports/figures/gpr_and_group_returns.png`
- `data/processed/event_windows.csv`
- `data/processed/event_study_summary.csv`
- `data/processed/panel_regression_baseline.csv`
- `data/processed/panel_regression_summary.txt`

## Data Note

ETF returns are USD returns. That means they include both local equity-market
movement and exchange-rate exposure against the US dollar. This is useful for
studying global investor exposure, but it is not the same as a pure local market
index return.
