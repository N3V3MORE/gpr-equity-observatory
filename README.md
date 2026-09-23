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

## Current Research Status

Read the estimates and uncertainty in [the results brief](reports/RESULTS_BRIEF.md)
alongside the snapshot shown in the app. Weak evidence is not proof of no effect,
and retaining an estimate's sign after excluding crisis windows does not establish
a robust GPR association.

The available daily candidate covers 20 countries from 2005-01-04 through
2026-06-30. It is awaiting provenance and publication review. The app labels it
as a candidate, withholds a public headline finding, and does not invent an
approved-data download or an already-live demo URL.

## How To Read The App

1. Research question and limitations, present in the static HTML before data loads.
2. Snapshot-backed current answer, or an explicit candidate-review notice.
3. Key event-study, controlled-panel, and date fixed-effects evidence.
4. Methods, sources, coverage, limitations, and approved downloads when available.

Data-through and snapshot-export dates are shown separately. Expandable details
retain inference, definitions, and CSV result downloads. Research-code and results
links remain usable during loading or a data error.

Prediction Lab, monthly demonstrations, and extended diagnostics are preserved at
`/local/` (under the deployment prefix when configured), using a local snapshot.
They are not fetched or shown in the default public journey. The frontend still
reads exported JSON only; it does not parse raw CSVs or rerun models.

Screenshots from the actual candidate, not synthetic chart fixtures:
[desktop](reports/screenshots/public-v1-candidate-desktop.png) ·
[mobile](reports/screenshots/public-v1-candidate-mobile.png).
These document presentation for review, not publication approval or replication.

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

Build a local static preview:

```powershell
cd frontend
npm run lint
npm run build
```

For reproducible public-v1 checks and the guarded Pages release path, use the
[deployment guide](docs/DEPLOYMENT_GUIDE.md). It documents synthetic browser
checks against `frontend/out`, preparation and review of existing Python
exports, `snapshot:validate`, `snapshot:stage`, and `build:public`. A reviewed
real snapshot is required for publication; the current candidate cannot pass
that gate. No live vendor download or empirical rebuild is required for frontend
checks, and the manual workflow does not enable Pages automatically.

Run Python checks:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

`frontend/public/data` is generated from Python outputs and is ignored by Git.
If generated data is missing or invalid, the static research introduction and
limitations remain visible with a visitor-facing unavailable state. Setup commands
stay in this documentation, not in the public page.

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
- Monthly sample mode validates the workflow; it is not empirical evidence.
- The two-market monthly benchmark is an aggregate comparison, not a country-panel proof.
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
