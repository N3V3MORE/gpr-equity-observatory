# Reproducibility

Next.js is the single user-facing app. Python remains the research and export backend. The frontend reads generated JSON from `frontend/public/data`.

The project has two related but separate pipelines:

- The daily ETF pipeline is the main GPR Equity Observatory workflow.
- The monthly benchmark pipeline is a lower-frequency developed/emerging
  aggregate benchmark.

The two pipelines stay separate in files, charts, and interpretation.

## Environment

```powershell
python -m pip install -r requirements.txt
uv sync --all-extras
```

The project requires Python 3.11 or newer.

## Daily ETF Pipeline

```powershell
python scripts/build_all.py
python scripts/run_task.py build-daily
```

Generated daily outputs are written under `data/raw`, `data/processed`, and
`reports/figures`. They are local only by default and ignored by Git.

## Monthly Benchmark Pipeline

Sample mode:

```powershell
python scripts/run_task.py monthly-sample --min-train-months 24
```

Sample mode validates the software path and is not empirical evidence.

Real mode:

```powershell
copy config\sources.sample.yml config\sources.yml
python scripts/run_task.py monthly-real
```

Real mode uses user-supplied local GPR and Kenneth French factor files. The
source config, raw files, real generated outputs, and real manifests are local
only unless intentionally published.

## Frontend Export And App

```powershell
python scripts/export_frontend_data.py
cd frontend
npm install
npm run dev
npm run build
```

The exporter writes `frontend/public/data/*.json`. The TypeScript app does not
run model logic.

## Checks

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
cd frontend
npm run lint
npm run build
```

## What Is Committed

Committed:

- source code
- tests
- configuration samples
- documentation
- screenshots
- generated results brief

Local only by default:

- `config/sources.yml`
- `data/raw`
- `data/interim`
- `data/processed`
- `data/metadata`
- `frontend/public/data`
- real monthly source manifests and generated result tables

## Claims Boundary

This is not a trading system and not investment advice. The empirical results
are not causal. Sample mode validates software behavior only. Monthly real mode
is an aggregate benchmark, not a country-panel proof.
