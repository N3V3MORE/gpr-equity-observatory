# Reviewer Guide

Next.js is the single user-facing app. Python remains the research and export backend. The frontend reads generated JSON from `frontend/public/data`.

## 5-Minute Review

- Read the research status and boundaries in [README.md](../README.md).
- Open [reports/RESULTS_BRIEF.md](../reports/RESULTS_BRIEF.md).
- Inspect the actual candidate [desktop](../reports/screenshots/public-v1-candidate-desktop.png)
  and [mobile](../reports/screenshots/public-v1-candidate-mobile.png) screenshots.
  Other screenshots in that directory are historical views.
- Check the Boundaries section in the README before repeating any result.

Use this path to understand what the project claims and what it avoids
claiming.

## 15-Minute Review

- Read [docs/RESEARCH_NOTE.md](RESEARCH_NOTE.md).
- Read [docs/PROJECT_STATUS.md](PROJECT_STATUS.md).
- Review [docs/REPRODUCIBILITY_CHECKLIST.md](REPRODUCIBILITY_CHECKLIST.md).
- Inspect the Next.js sections under `frontend/src/sections`.

Use this path to judge whether the empirical story is coherent and cautious.

## 30-Minute Technical Review

- Read [docs/TECHNICAL_APPENDIX.md](TECHNICAL_APPENDIX.md).
- Inspect `scripts/build_all.py` and `scripts/run_task.py`.
- Inspect `src/gprobs/dashboard/export.py`, the backend UI contract.
- Inspect `frontend/src/lib` for labels, formatting, and runtime data loading.
- Inspect `tests/` for data, model, exporter, frontend, and docs checks.
- Follow the [deployment guide](DEPLOYMENT_GUIDE.md) for built-artifact browser
  checks and the reviewed-snapshot gate. Inspect the fixed publication review
  record and its bundle hashes before accepting a release artifact. A passing
  synthetic fixture suite is software evidence, not publication approval.

Use this path to assess maintainability, test coverage, and reproducibility.

## App Path

For a local research rebuild (separate from frontend release checks):

```powershell
python -m pip install -r requirements.txt
uv sync --all-extras
python scripts/build_all.py
python scripts/export_frontend_data.py
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
cd frontend
npm install
npm run dev
npm run build
```

For frontend review without market downloads or model runs, use the guide's
`npm run build:test` and `npm run test:browser` sequence in a clean workspace.
It serves the built `frontend/out` artifact with explicitly synthetic data.
Public release checks instead require the committed approved real bundle and
`npm run build:public`; the positive real-publication check remains blocked
until that review exists. Deployment and testing of an actual Pages URL are
separate owner actions, not implied by local browser checks.

Start with these app sections:

- Research question: static introduction and limitations, available without JavaScript.
- Current answer: derived from the displayed snapshot after approval; candidates
  show a review notice with their estimates in a separate detail.
- Key evidence: event-study and controlled/date fixed-effects results, with
  keyboard-accessible inference and definition tables and CSV downloads.
- Methods & data: source links, country coverage, limitations, and approved-data
  links only when a reviewed artifact is explicitly listed.

The data-through date is the last panel observation; the snapshot-export date
records when JSON was written. The current candidate is not an approved public
release. There is no live-demo URL to infer from the intended hosting provider.
Research-code and results links work independently of data loading.

Prediction Lab, monthly demonstrations, rolling sensitivity, and extended
diagnostics remain accessible at `/local/` with a local snapshot. They are
excluded from the default public page and its dataset requests.

The daily ETF workflow is primary. The monthly benchmark is a separate
aggregate layer and should not be mixed with the daily country ETF panel as one
empirical sample.

## What Not To Overclaim

- Do not describe the results as causal.
- Do not describe the project as a trading system or investment advice.
- Do not claim that emerging markets definitely react more strongly.
- Do not treat monthly sample mode as empirical evidence.
- Do not treat the two-market monthly benchmark as country-clustered panel
  proof.
