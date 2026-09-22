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

## Public-v1 Scope

The public-v1 direction is an explicitly reviewed, versioned research snapshot
feeding the existing static Next.js app, with GitHub Pages as the intended
host. Python remains the analysis and export backend. The publication mechanism
and release checks are planned work; this section does not implement them or
authorize publication of local files. The alternatives under Data Strategy
above remain background context.

Core content is the daily ETF research question, event-study evidence,
controlled and date-fixed-effects results, sources, coverage, and limitations.
Keep the public story tied to the selected snapshot: the committed brief
describes mixed evidence, not an established larger emerging-market response.
Prediction Lab, monthly demonstrations, and extensive diagnostics remain
implemented and available locally but are not prerequisites for the core
public release. Preserve the legacy local applications.

No new models, data providers, backend, authentication, design system, database,
live refresh, or framework rewrite is included. Never automatically publish raw
third-party data, secrets, or local monthly outputs. Never delete raw or
processed research files. Future publication cleanup must be restricted to
generated publication directories.

The eventual release is ready only when an explicitly approved snapshot has
validated content, coverage, provenance, and artifact checksums; the static
build includes the essential research; and rendered charts, uncertainty
information, downloads, and mobile presentation have been checked. Missing
essential evidence must block a public build. Preserve a useful empty state
for local development. Deployment must not depend on downloading market data
or rerunning models.

### Baseline Stage: 2026-09-22

Starting point: clean `main` at `7fb82357a8704af1049bbe4e9f55e689ee966411`.
Release branch: `codex/public-v1-baseline`. This stage changes only this guide
and `AGENTS.md`; it records scope and verification without implementing fixes.

| Local asset | Availability |
| --- | --- |
| Required daily processed outputs | 0 of 22 expected CSVs |
| Frontend research exports | No `frontend/public/data` directory; 0 of 24 complete-export JSONs |
| Monthly sample and real outputs | Neither mode's panel, manifests, or result tables is present |
| Raw, interim, and metadata directories | Absent |
| Committed reference material | 20-country universe, results brief, and three screenshots |

The country universe specifies 10 developed and 10 emerging markets; it does
not establish actual observation coverage. With no processed outputs or source
manifests, dates, row counts, missingness, source hashes, and empirical results
cannot be verified locally. The results brief is a committed account of prior
results, not a fresh replication or a deployable research bundle.

A read-only call to `build_frontend_payloads()` returned `available=false`,
22 missing required files, and only the `copy` and `manifest` payloads. No JSON
was written. The exporter currently requires all daily outputs, including
Prediction Lab outputs. Its successful-export manifest has no schema version,
snapshot identifier, or artifact checksums; `build_date` is the export date,
not a source-retrieval date. These are release gaps, not changes in this stage.

Verification used the existing lockfiles, with Python 3.14.4 and
`uv sync --locked --all-extras`. Baseline Python checks:

```powershell
uv run --locked --all-extras ruff check .
uv run --locked --all-extras pytest tests/test_frontend_export.py tests/test_frontend_project_contracts.py tests/test_documentation_contracts.py tests/test_run_task.py -q
```

Ruff passed and all 41 focused tests passed before documentation edits. Export
tests use temporary placeholder data; frontend contract tests inspect source
structure. They do not verify empirical findings or browser behavior. No new
tests are needed for these documentation additions.

After the scope additions, all 18 documentation-contract tests passed:

```powershell
uv run --locked --all-extras pytest tests/test_documentation_contracts.py -q
```

Frontend checks used Node 22.22.2, npm 12.0.2, and the locked Next.js 14.2.35
dependencies, with telemetry disabled. From `frontend/`, `npm ci`,
`npm run lint`, and `npm run build` all exited successfully. Lint reported no
warnings or errors, and the build generated all five static pages without
warnings. `frontend/out/index.html` exists, but both `frontend/public/data`
and `frontend/out/data` remain absent. This is a successful build containing
no research JSON, not a usable research release. No browser test was run.

Installation reported 10 dependency security advisories (1 moderate, 8 high,
1 critical), deprecated dependencies, and a blocked `unrs-resolver` postinstall
script under npm's script policy. These findings were recorded without
upgrading dependencies or changing that policy; frontend lint and build still
passed. Both lockfiles are unchanged. The full Python suite and daily/monthly
pipeline tasks were intentionally excluded from this focused baseline.

The remaining release work is a reviewed populated snapshot, explicit export
selection and validation, safe handling of missing values, accurate inference
and sample labels, visitor-facing presentation, supported-runtime maintenance,
and checks of the rendered public site. No numerical or methodological changes
were made. No empirical pipeline, market-data download, or deployment was run.
