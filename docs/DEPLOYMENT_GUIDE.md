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

Installation reported 10 vulnerable dependency entries (1 moderate, 8 high,
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

### Public-v1 Toolchain Update: 2026-09-22

This stage updates tooling only. Node 24.21.0 LTS is pinned in
`frontend/.nvmrc` and used by frontend CI; use that Node version locally too.
Next.js and its ESLint configuration are pinned to 16.3.6. React/React DOM
19.2.8 and matching React 19 types provide App Router compatibility. Node 24
types require TypeScript 5.6, so TypeScript moves only to 5.6.3. Autoprefixer,
Tailwind, and the direct PostCSS dependency retain their existing versions.

`npm run lint` now invokes ESLint directly with the Next core-web-vitals flat
configuration. `npm run typecheck` generates route types before running
TypeScript without emitting files. CI keeps install, lint, type checking, and
build as separate steps and uses `npm ci --strict-peer-deps`. The existing
static export, trailing slashes, base-path handling, Python-to-JSON contract,
research calculations, and interpretation are unchanged. The HTML smooth-scroll
attribute retains Next's previous navigation behavior. One documented inline
exception to the newly enabled `react-hooks/set-state-in-effect` rule preserves
the existing immediate-load fallback when IntersectionObserver is unavailable;
the rule remains enabled elsewhere.

**Approved support exception:** ESLint 9.39.5 is end-of-life. It is retained
temporarily to preserve the current lint checks: the published React, import,
and accessibility plugins in Next 16.3.6's configuration do not declare ESLint
10 compatibility. No peer-dependency requirements are bypassed. Revisit this
pin when the complete plugin set supports ESLint 10; this stage is not a claim
that every dependency is maintained.

Recharts moves to the maintained 3.10.1 release, with its `react-is` peer pinned
to the same 19.2.8 version as React. No dependency overrides are needed. Following
the [Recharts 3 migration guide](https://github.com/recharts/recharts/wiki/3.0-migration-guide),
explicit chart props preserve the previous series order in legends/tooltips
and the previous keyboard behavior. Reference lines retain their previous
position behind bars, and the timeline tooltip omits the additional date row
introduced by Recharts 3 while retaining its date heading and both value rows.
Tooltip callback types now accept the values declared by Recharts 3; the
existing number formatting and all chart data transformations remain unchanged.

Official references checked for this migration:
[Next support policy](https://nextjs.org/support-policy),
[Next 16 migration](https://nextjs.org/docs/app/guides/upgrading/version-16),
[Next ESLint configuration](https://nextjs.org/docs/app/api-reference/config/eslint),
[Node 24.21.0 LTS](https://nodejs.org/en/blog/release/v24.21.0), and
[ESLint support policy](https://eslint.org/version-support/).

#### Remaining Dependency Audit Findings

The locked full dependency audit reports **4 vulnerable packages** (3 high,
1 moderate), covering **10 distinct advisories** (7 high, 3 moderate).
The production-only dependency audit reports one moderate package,
`baseline-browser-mapping`; npm's production classification includes build
tools shipped with Next and does not establish browser exposure.

| Locked package | Findings | Exposure in this project |
| --- | --- | --- |
| `baseline-browser-mapping` 2.10.40 | [Process termination on invalid options](https://github.com/advisories/GHSA-w5vr-8v7q-w6rv) | Next/Browserslist build targeting; no visitor-controlled options path found. |
| `brace-expansion` 1.1.15 | [CPU exhaustion](https://github.com/juliangruber/brace-expansion/security/advisories/GHSA-3jxr-9vmj-r5cp), [memory exhaustion](https://github.com/juliangruber/brace-expansion/security/advisories/GHSA-mh99-v99m-4gvg), [mitigation bypass](https://github.com/juliangruber/brace-expansion/security/advisories/GHSA-rgw5-rvv9-x895) | ESLint/plugin glob processing; hostile patterns could affect lint availability. |
| `browserslist` 4.28.4 | [Unbounded cache](https://github.com/browserslist/browserslist/security/advisories/GHSA-c83g-rgw3-j3cx), [malicious custom statistics](https://github.com/browserslist/browserslist/security/advisories/GHSA-73wf-gq98-2v4g) | Autoprefixer/Babel build configuration; no public query endpoint or custom statistics input found. |
| Root `postcss` 8.4.39 | [Unsafe style embedding](https://github.com/postcss/postcss/security/advisories/GHSA-qx2v-qp2m-jg93), [source-map file read](https://github.com/postcss/postcss/security/advisories/GHSA-6g55-p6wh-862q), [incomplete fix](https://github.com/postcss/postcss/security/advisories/GHSA-fxqj-rqcc-2cmp), [map traversal](https://github.com/postcss/postcss/security/advisories/GHSA-r28c-9q8g-f849) | Malicious CSS can expose build-host files; unsafe embedding of generated CSS can create browser XSS. Current CSS is repository-controlled; no CSS-upload or unsafe embedding path was found. |

Next's separate PostCSS 8.5.23 is outside the affected ranges listed above.
There are no remaining Next-package advisories in this audit. Static hosting
does not deploy request-time Next servers, Server Actions, middleware/proxy,
or image optimization, but it does not remove build-input, dependency, or
generated-output risks. These are source-based exposure assessments, not
exploit tests or a complete deployed-bundle audit. Unrelated dependency fixes
are deferred; no forced audit fix or peer-dependency bypass was used.

#### Toolchain Verification

On Node 24.21.0/npm 11.19.0, the final `npm ci --strict-peer-deps` succeeded
without peer-resolution warnings, and `npm ls --all --omit=optional` reported
a valid dependency tree. Lint and explicit type checking passed. Static builds
passed both without a prefix and with
`NEXT_PUBLIC_BASE_PATH=/gpr-equity-observatory`. Next emitted a local-environment
warning about ignoring an unrelated parent-directory lockfile; that file was
not changed. npm also reported the approved ESLint deprecation noted above and
left `unrs-resolver`'s postinstall blocked by the existing script policy; lint,
type checking, and builds succeeded without relaxing that policy.

Python lint passed and the existing full suite passed all 195 tests (77%
coverage). After the migration edits, 41 focused exporter/frontend/documentation/
task-runner tests passed. The exporter CLI was also exercised against the
checkout with output redirected to a temporary directory: it reported
`available=false` and 22 missing files. No repository research data was created
or changed.

There is no existing JavaScript/browser runtime test suite. Temporary Playwright
checks compared the old and upgraded static exports using synthetic JSON,
covering desktop (1440x1000) and mobile (390x844), missing/error/populated states,
all 13 charts, section links, details, CSV downloads, and lazy loading. Text,
axis ticks/domains, legend order, download bytes, and interactions matched.
Small library-level rounding differences remain (up to 1px in bar widths and
0.5px in rolling-chart positions); exact screenshot identity is not claimed.
The fallback without IntersectionObserver also passed. Prefixed checks verified
JavaScript, CSS, and JSON paths, but found the preexisting absolute `/icon.svg`
metadata URL returns 404 under a prefix; that unrelated fix is deferred.
These checks establish software compatibility, not empirical correctness;
actual research outputs remain unavailable. Browser checks and fixtures live
outside the repository.
