# GPR Equity Observatory

GPR Equity Observatory is a reproducible economics research project on how
equity markets respond to geopolitical risk shocks.

It is built as a profile-ready project: a tested Python data pipeline, empirical
models, an interactive Streamlit dashboard, screenshots, and plain-English
research notes.

![Dashboard overview](reports/screenshots/dashboard_overview.png)

## One-Sentence Summary

I built a reproducible quant economics platform that measures how geopolitical
risk is associated with equity-market returns across 20 developed and emerging
market country ETF proxies.

## What The Project Does

- Builds a 20-country ETF return panel using free public data.
- Adds the Caldara-Iacoviello geopolitical risk index.
- Compares developed and emerging market ETF responses.
- Runs event studies, panel regressions, quantile regressions, local
  projections, rolling sensitivity estimates, and a simple drawdown-risk model.
- Presents the results in a Streamlit dashboard and written research notes.

This is not a trading system and it is not investment advice. It is an
educational economics project about geopolitical risk, international equity
markets, and empirical research design.

## Main Finding

The current evidence should be reported carefully.

The controlled panel regression finds a small negative association between daily
geopolitical-risk jumps and ETF returns. However, the date fixed-effects H1 test
does not find a statistically strong extra emerging-market effect.

In plain English: the project finds evidence that geopolitical risk matters for
equity-market risk, but it should not claim to prove that emerging markets always
react more strongly.

See [reports/RESULTS_BRIEF.md](reports/RESULTS_BRIEF.md) for the short generated
summary.

## Why This Works As A Profile Project

This project shows more than one isolated chart or model. It demonstrates:

- economics research framing
- data collection and cleaning
- reproducible Python workflow
- econometric modelling
- cautious interpretation of statistical evidence
- dashboard communication
- testing and continuous integration

The most important strength is honesty: the project reports mixed evidence
instead of forcing a dramatic result.

## Quick Start

Install dependencies:

```powershell
python -m pip install -e .
```

For local development and CI-style checks, install the dev extra:

```powershell
python -m pip install -r requirements.txt
```

Rebuild the data and results:

```powershell
python scripts/build_all.py
```

Run the dashboard:

```powershell
streamlit run app.py
```

Run the checks:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

The build command downloads public data and writes generated files into
`data/raw/`, `data/processed/`, and `reports/figures/`. Those generated folders
are intentionally not committed to Git.

## Repository Map

```text
app.py                         Streamlit dashboard
data/country_universe.csv      20-country ETF universe
scripts/build_all.py           Full rebuild pipeline
scripts/build_*.py             Data construction scripts
scripts/run_*.py               Empirical model scripts
scripts/write_results_brief.py Plain-English results summary
src/gprobs/                    Reusable project code
tests/                         Data and feature checks
reports/RESULTS_BRIEF.md       Short generated findings summary
reports/screenshots/           Dashboard screenshots for profile use
docs/PROJECT_STATUS.md         Current implementation and results status
docs/RESEARCH_NOTE.md          Applied economics research note draft
docs/TECHNICAL_APPENDIX.md     Data, model, and reproducibility details
docs/PROFILE_PACKAGING.md      CV, LinkedIn, and interview materials
```

## Methods Included

- ETF daily log returns
- GPR shock event studies
- Market-model abnormal returns
- Panel regressions with market controls
- Sample robustness checks
- Quantile regressions for downside-risk analysis
- Local projections for response paths
- Rolling GPR sensitivity estimates
- Time-aware drawdown-risk classification

## Important Limitations

- ETF returns are USD returns, so they combine local equity-market movement and
  currency exposure against the US dollar.
- The results are associations, not clean causal estimates.
- Free market data can contain revisions, missing values, or provider limits.
- The current project runs locally. Public dashboard deployment is a separate
  optional step because generated data files are not committed by default.

## Profile Materials

Use [docs/PROFILE_PACKAGING.md](docs/PROFILE_PACKAGING.md) for:

- a CV bullet
- a LinkedIn summary
- interview talking points
- a three-minute walkthrough script
- what not to overclaim

Screenshots are already saved in [reports/screenshots](reports/screenshots).

## Sources

- Caldara and Iacoviello Geopolitical Risk Index:
  <https://www.policyuncertainty.com/gpr.html>
- Caldara, Dario, and Matteo Iacoviello. 2022. "Measuring Geopolitical Risk."
  American Economic Review.
- ETF and market proxy data are retrieved through `yfinance` for educational
  research use.
- The dashboard is built with Streamlit.
