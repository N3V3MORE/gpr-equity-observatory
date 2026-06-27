# Reviewer Guide

Next.js is the single user-facing app. Python remains the research and export backend. The frontend reads generated JSON from `frontend/public/data`.

## 5-Minute Review

- Read the main finding in [README.md](../README.md).
- Open [reports/RESULTS_BRIEF.md](../reports/RESULTS_BRIEF.md).
- Skim [reports/screenshots](../reports/screenshots) for the app shape.
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

Use this path to assess maintainability, test coverage, and reproducibility.

## App Path

When running the app locally:

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

Start with these app sections:

- Overview: project question, method map, and evidence map.
- Market Response: event-study, robustness, regression, tail, and dynamic
  response evidence.
- Prediction Lab: out-of-sample drawdown-risk classification diagnostics.
- Country Sensitivity: lazy-loaded rolling GPR sensitivity.
- Data & Methods: country coverage, monthly benchmark status, and provenance.

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
