# Deployment Guide

Next.js is the single user-facing app. Python remains the research and export backend.

The deployment unit is a static Next.js build backed by generated JSON in
`frontend/public/data`.

## Local Run

Install dependencies and build the Python outputs:

```powershell
python -m pip install -r requirements.txt
uv sync --all-extras
python scripts/build_all.py
python scripts/export_frontend_data.py
```

Run checks:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

Run the Next.js app locally:

```powershell
cd frontend
npm install
npm run dev
```

Build the static site:

```powershell
cd frontend
npm run lint
npm run build
```

## Data Strategy

`frontend/public/data` is generated from local processed outputs and is ignored
by Git. A public static deployment needs one explicit choice:

- publish a reviewed static snapshot that includes selected generated JSON
- rebuild the JSON in a deployment pipeline before `npm run build`
- keep the project local-first and publish screenshots plus the results brief

Do not deploy an app that silently lacks processed data. Missing data should
show the app's empty state and rebuild instructions.

## Static Path Prefix

If the static app is hosted below a path prefix, set `NEXT_PUBLIC_BASE_PATH`
before building:

```powershell
$env:NEXT_PUBLIC_BASE_PATH="/gpr-equity-observatory"
cd frontend
npm run build
```

## Monthly Real-Mode Warning

Monthly real mode is local only unless a separate publication decision is made.
Do not commit `config/sources.yml`, raw monthly source files, real local paths,
or real generated monthly outputs. If real monthly outputs are published, the
source manifests must be checked for redaction and the UI must keep the
aggregate benchmark limitation visible.

## Recommendation

For a portfolio project, use the static Next.js app as the public surface and
keep Python as the reproducible backend/export path. Publish screenshots and
`reports/RESULTS_BRIEF.md` alongside the app so reviewers can understand the
evidence without rerunning the full pipeline.
