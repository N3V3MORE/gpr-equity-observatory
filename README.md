# GPR Equity Observatory

GPR Equity Observatory tests how far public data can answer a careful
question: do equity markets behave differently when geopolitical risk jumps?

It uses 20 country ETF proxies, the Caldara-Iacoviello GPR index, market
controls, event studies, regressions, local projections, rolling sensitivity,
and an out-of-sample drawdown-risk lab. Next.js is the single user-facing app.
Python remains the research and export backend.

## One-Sentence Summary

An applied economics project on geopolitical risk, international ETF returns,
and the limits of what public data can show.

## What The Project Does

- Builds a 20-country daily ETF return panel from public data.
- Adds daily Caldara-Iacoviello geopolitical risk data.
- Compares developed and emerging market ETF responses.
- Runs event studies, panel regressions, quantile regressions, local
  projections, rolling sensitivity estimates, and Prediction Lab diagnostics.
- Adds a separate monthly developed/emerging benchmark layer with deterministic
  sample mode, local real mode, source manifests, HAC regressions, and
  expanding-window forecast comparisons.
- Exports validated Python outputs into `frontend/public/data` for the Next.js
  app.

## Main Finding

The current evidence should be reported carefully: geopolitical risk is
associated with equity-market risk, but the emerging-market asymmetry result is
mixed and not statistically strong in the current specification.

Prediction Lab shows modest drawdown-risk ranking signal. GPR alone is weak
relative to volatility and broader market features. The monthly benchmark is a
separate aggregate comparison layer; sample mode is software validation and the
real monthly benchmark is not a country-panel proof.

See [reports/RESULTS_BRIEF.md](reports/RESULTS_BRIEF.md) for the generated
short summary.

## Quick Start

Install the regular development environment:

```powershell
python -m pip install -r requirements.txt
```

For the exact resolved environment:

```powershell
uv sync --all-extras
```

Build the daily outputs, optional monthly sample outputs, and frontend JSON:

```powershell
python scripts/build_all.py
python scripts/run_task.py monthly-sample --min-train-months 24
python scripts/export_frontend_data.py
```

Run the Next.js app:

```powershell
cd frontend
npm install
npm run dev
```

Build the static frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Run Python checks:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

`frontend/public/data` is generated from Python outputs and is ignored by Git.
If the generated data is missing, the app renders an empty state with rebuild
commands instead of recomputing analysis in TypeScript.

## Monthly Real Mode

Monthly real mode is local-only by default. Copy `config/sources.sample.yml` to
`config/sources.yml`, point it at local GPR and Kenneth French factor files,
then run:

```powershell
python scripts/run_task.py monthly-real
```

To run the steps individually:

```powershell
python scripts/run_task.py build-monthly-real
python scripts/run_task.py validate-monthly-real
python scripts/run_task.py run-monthly-regressions-real
python scripts/run_task.py run-monthly-forecasts-real
python scripts/run_task.py validate-monthly-real-results
```

Do not commit `config/sources.yml`, raw third-party market data, local monthly
source files, or real generated monthly outputs unless a separate publication
policy is chosen.

## Repository Map

```text
frontend/                         Next.js + TypeScript app
frontend/public/data/             generated JSON UI contract
scripts/export_frontend_data.py   Python-to-Next.js export handoff
src/gprobs/dashboard/export.py    dashboard-facing backend contract
scripts/build_all.py              daily rebuild pipeline
scripts/run_task.py               daily, monthly, export, and verification tasks
src/gprobs/                       reusable research/data/model code
tests/                            data, model, exporter, frontend, and docs checks
reports/RESULTS_BRIEF.md          generated short findings summary
reports/screenshots/              reviewer/profile screenshots
docs/REVIEWER_GUIDE.md            short review paths
docs/REPRODUCIBILITY_CHECKLIST.md clean-clone rebuild checklist
docs/TECHNICAL_APPENDIX.md        data, model, and output details
```

## Reviewer Path

- Start with this README and [reports/RESULTS_BRIEF.md](reports/RESULTS_BRIEF.md).
- Use [docs/REVIEWER_GUIDE.md](docs/REVIEWER_GUIDE.md) for 5-minute,
  15-minute, and technical review paths.
- Use [docs/REPRODUCIBILITY_CHECKLIST.md](docs/REPRODUCIBILITY_CHECKLIST.md)
  for the clean rebuild sequence.
- Use [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for the static
  Next.js deployment shape.
- Use [reports/screenshots](reports/screenshots) for visual review.

## Profile Summary

Built a tested research observatory that studies geopolitical risk and
international ETF returns with public data, cautious econometric interpretation,
an out-of-sample drawdown-risk lab, and a static Next.js frontend backed by
validated Python exports.

Useful interview framing:

- The project is strongest as a reproducible research workflow, not as a bold
  trading claim.
- The evidence is mixed, and the app makes those limits visible.
- The frontend is presentation-only; Python owns the analysis and exported UI
  contract.

## Boundaries

- ETF returns are USD returns, so they combine local equity movement and
  currency exposure.
- Daily ETF findings and monthly benchmark findings answer related but
  different questions.
- Monthly sample mode proves the workflow runs; it is not empirical evidence.
- The two-market monthly benchmark is useful as an aggregate comparison, not as
  a country-panel proof.
- Results are associations, not clean causal estimates.
- This is not a trading system and it is not investment advice.

## Sources

- Caldara and Iacoviello Geopolitical Risk Index:
  <https://www.policyuncertainty.com/gpr.html>
- Caldara, Dario, and Matteo Iacoviello. 2022. "Measuring Geopolitical Risk."
  American Economic Review.
- ETF and market proxy data are retrieved through `yfinance` for educational
  research use.
- Monthly real benchmark mode uses user-supplied Caldara-Iacoviello monthly GPR
  and Kenneth French developed/emerging factor files; those local source files
  stay outside Git.
