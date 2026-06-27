# Reproducibility Checklist

Use this checklist when rebuilding the project from a clean clone. Next.js is the single user-facing app. Python remains the research and export backend.
The app reads generated JSON from `frontend/public/data`.

## Environment

```powershell
python -m pip install -r requirements.txt
uv sync --all-extras
```

## Python Checks

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

## Rebuild

```powershell
python scripts/build_all.py
python scripts/run_task.py build-daily
python scripts/run_task.py monthly-sample --min-train-months 24
python scripts/export_frontend_data.py
```

The monthly sample pipeline is deterministic software validation. It is not
empirical evidence.

## Monthly Real Mode

Copy `config/sources.sample.yml` to `config/sources.yml`, point it at local GPR
and Kenneth French factor files, then run:

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

Monthly real mode is local-only unless a publication policy is chosen.

## Next.js App

```powershell
cd frontend
npm install
npm run lint
npm run dev
npm run build
```

The static build writes `frontend/out`. If the app is hosted below a path
prefix, set `NEXT_PUBLIC_BASE_PATH` before `npm run build`.

## Expected Local Outputs

Generated files are local by default and ignored by Git:

- `data/raw`
- `data/interim`
- `data/processed`
- `data/metadata`
- `reports/tables`
- `reports/figures`
- `frontend/public/data`
- `frontend/out`

Committed profile artifacts include `reports/RESULTS_BRIEF.md` and
`reports/screenshots`.

## Do Not Commit

- `.env` files, API keys, or credentials.
- `config/sources.yml`.
- Raw third-party market data.
- Local monthly source files.
- Real generated monthly outputs unless a data-publication decision is made.

Before showing the project widely, confirm that lint, tests, the Python export,
and the Next.js build pass, and that public wording remains cautious.
