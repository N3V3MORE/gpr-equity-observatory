# Deployment Guide

Next.js is the single user-facing app. Python remains the research and export backend.

The deployment unit is the checked `frontend/out` static artifact. It contains
only the reviewed JSON and downloads selected by
`publication/approved-snapshot.json`. Release preparation never downloads vendor
data or reruns models.

The commands and workflow below are implemented. A reviewed real snapshot and
publication approval are still missing. Pages configuration and verification
of a deployed URL remain owner actions. Synthetic browser tests demonstrate
software behavior; they cannot satisfy the publication gate or establish
research findings.

## Local Research Development

These commands rebuild research for local development. They are separate from
frontend checks and the release path below:

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
npm ci --strict-peer-deps
npm run dev
```

Build a local static preview (this does not grant publication approval):

```powershell
cd frontend
npm run lint
npm run build
```

## Data Strategy

`frontend/public/data` is generated from local processed outputs and is ignored
by Git. Public-v1 uses a selected, reviewed bundle under
`publication/snapshots/<snapshot_id>/`; a release stages that bundle into
`frontend/public/` before building. An arbitrary local export, an approved flag
alone, or a valid manifest with missing required payloads is insufficient.

Do not deploy an app that silently lacks processed data. The static research
introduction and limitations remain visible while data loads or fails; visitors
see an unavailable message and research links rather than maintainer commands.

### Public Reading View And Local Research View

The root page follows question -> snapshot-backed answer -> key evidence ->
methods, data, coverage, and limitations. Its introduction is server-rendered at
build time; interactive charts and JSON loading remain client-side. No runtime
backend is required. `/local/` preserves Prediction Lab, monthly demonstrations,
and extended diagnostics for local-profile snapshots. A public-profile manifest
cannot unlock that view, and the root view never requests optional datasets.

`manifest.build_date` is the snapshot-export date; `overview.headline.end_date`
is the data-through date. They must remain separately labeled.

Dataset selection (`profile: "public"`) is not publication approval. The Python
exporter and snapshot preparation command create candidates. Missing approval
leaves a candidate notice and keeps empirical takeaways out of the public
headline. No approved release or live demo URL is currently recorded.

Approved-data links use `approved_downloads` entries with `label`, `path`,
`table`, and `units`. Each path is a filename under `downloads/`. The publication
gate checks the CSV bytes against the corresponding exported table; a download
label or hash alone does not establish matching contents or units. Event-study,
controlled-regression, and date fixed-effects tables use `basis_points`;
country coverage uses `observations_and_dates`. These result tables are distinct
from raw third-party data, which must not be published automatically.

Current presentation screenshots use actual candidate outputs:
[desktop](../reports/screenshots/public-v1-candidate-desktop.png) and
[mobile](../reports/screenshots/public-v1-candidate-mobile.png). These are local
review evidence, not empirical replication or publication approval. Older
screenshots and the verification notes below describe earlier stages.

## Prepare And Review A Snapshot

Use the pinned Node version in `frontend/.nvmrc` and an existing Python export.
From a clean checkout, install locked dependencies and select a new candidate:

```powershell
cd frontend
npm ci --strict-peer-deps
npm run snapshot:prepare -- --source <existingPythonExportDir> --id <snapshot_id>
```

Preparation selects the eight required public datasets and manifest, creates
matching result CSVs, and writes `publication/snapshots/<snapshot_id>/` plus
`publication/<snapshot_id>.review-draft.json`. It refuses existing destinations.
Optional Prediction Lab, monthly, and diagnostic payloads are not selected.
Preparation is a presentation/export operation; it does not estimate results,
obtain source data, or approve publication.

The owner must inspect coverage, definitions, inference, claims, and source
provenance, and decide whether redistribution of every selected output is
permitted. A successful validator cannot make that research or rights decision.
After review, the manifest must declare `data_kind: "real"` and
`publication_status: "approved"`. Complete the draft and save the fixed review
record as `publication/approved-snapshot.json`:

| Review record field | Required content |
| --- | --- |
| `schema_version` | `1` |
| `snapshot_id` | Identifier matching the bundle and manifest |
| `snapshot_dir` | `publication/snapshots/<snapshot_id>` |
| `data_kind` | `real` |
| `review` | `status: "approved"`, reviewer identity in `reviewed_by`, ISO date/time in `reviewed_at`, and substantive `notes` |
| `sources` | Entries for `gpr`, `etf_prices`, and `controls`, each with `id`, source `url`, `retrieved_at`, source `sha256`, and `redistribution_review` |
| `files` | Exact bundle-relative file paths mapped to SHA-256 hashes, including the manifest, JSON, and approved downloads |

After reviewed edits, run `npm run snapshot:hashes -- --id <snapshot_id>` from
`frontend/` to print the canonical lowercase SHA-256 map for the record's
`files` field. This does not approve the snapshot. Source provenance fields are
reviewer attestations: the validator checks their declared shape but does not
retrieve or rehash raw source data or prove that self-declared provenance is
true. Do not fabricate retrieval dates, source hashes, review identities, or
permissions. Keep raw inputs, credentials, local source paths, and monthly
outputs outside the bundle.
Commit only the review record and selected reviewed bundle after inspecting the
diff. `build:public` requires those files to be tracked and unchanged from the
checked-out commit; uncommitted approval cannot produce a public release.
Scoped `.gitattributes` rules preserve the exact review and snapshot bytes across
Windows and Linux checkouts, so Git newline conversion cannot invalidate hashes.

## Validate And Build A Static Release

From `frontend/` in a fresh checkout containing the committed review and bundle:

```powershell
npm ci --strict-peer-deps
npm run snapshot:validate -- --tracked
npm run snapshot:stage
npm run checks
npx playwright install --with-deps chromium
$env:NEXT_PUBLIC_BASE_PATH="/gpr-equity-observatory"
npm run build:public
$env:GPR_BROWSER_PUBLICATION="1"
npm run test:browser
npm run snapshot:artifact
```

`snapshot:validate` without `--tracked` supports pre-commit review.
`snapshot:stage` places only validated approved files in the static public data
and download directories. It must not overwrite unrelated local research
exports; use a clean checkout for releases. `checks` runs lint, generated route
types/TypeScript, and runtime tests. `build:public` revalidates approval,
declared source-provenance fields, selected artifact hashes, the staged
allowlist, and the resulting export. Missing or malformed
required data, incompatible schemas, extra publication files, mismatched
downloads, and synthetic test markers fail the gate.

`build:public` records every output-file hash in the ignored
`frontend/.release-artifact.json` seal, outside `out`. Publication-mode browser
tests verify that seal at startup, and `snapshot:artifact` checks it again
immediately before workflow upload. No output files are modified after testing.

Publication-mode browser tests serve the existing `frontend/out` directory and
validate its data and download bytes again. They do not start a development
server, generate replacement data, or rebuild the artifact. Review the browser
results before treating the artifact as release-ready. The positive acceptance
case with an actually reviewed real snapshot remains blocked until the owner
supplies that review; a synthetic record is not a substitute.

### Controlled Browser Checks Without Research Data

Frontend CI uses clearly labeled synthetic fixtures in a clean workspace:

```powershell
cd frontend
npm ci --strict-peer-deps
npm run checks
npx playwright install --with-deps chromium
$env:GPR_BROWSER_PUBLICATION=""
$env:NEXT_PUBLIC_BASE_PATH=""
npm run build:test
npm run test:browser
```

Repeat from a clean workspace with
`NEXT_PUBLIC_BASE_PATH=/gpr-equity-observatory` to check the project prefix.
`build:test` refuses to replace conflicting local data. Its output is marked
`SYNTHETIC_TEST_ARTIFACT.txt` and must never be uploaded as research. The public
release gate rejects that marker even if fixture metadata claims approval.
Tests cover static research content, chart data and interactions, matching CSV
downloads and units, required-data errors, optional unavailable sections, null
observations, keyboard controls, mobile overflow, assets, and browser errors.

The existing Python checks and deterministic monthly sample job remain in CI.
Frontend pull requests do not trigger live vendor downloads or the full daily
empirical pipeline.

## Static Path Prefix

If the static app is hosted below a path prefix, set `NEXT_PUBLIC_BASE_PATH`
before building:

```powershell
$env:NEXT_PUBLIC_BASE_PATH="/gpr-equity-observatory"
npm run build:public
```

Set it to an empty string for root hosting, before building and browser tests.
The manual Pages workflow deliberately targets `/gpr-equity-observatory` and
checks that the existing Pages configuration agrees before deployment. A custom
domain/root deployment requires a reviewed workflow base-path change and fresh
checks; do not rewrite asset URLs after testing.

## Monthly Real-Mode Warning

Monthly real mode is local only unless a separate publication decision is made.
Do not commit `config/sources.yml`, raw monthly source files, real local paths,
or real generated monthly outputs. If real monthly outputs are published, the
source manifests must be checked for redaction and the UI must keep the
aggregate benchmark limitation visible.

## Manual GitHub Pages Deployment

`.github/workflows/pages.yml` runs only on `workflow_dispatch` from `main`.
It checks out the selected commit, requires the tracked approval record, runs
the release commands above, and uploads `frontend/out` once. A separate job
deploys that exact artifact without a rebuild. The build job has only
`contents: read`; the deployment job has only `pages: write` and
`id-token: write`. The `github-pages` environment is the approval boundary.
`configure-pages` uses `enablement: false`, so the workflow cannot enable Pages.

Official actions are pinned to verified release commits: checkout 7.0.1,
setup-node 7.0.0, configure-pages 6.0.0, upload-pages-artifact 5.0.0, and
deploy-pages 5.0.1. See the
[GitHub custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
and the official
[configure](https://github.com/actions/configure-pages/releases/tag/v6.0.0),
[upload](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0),
and [deploy](https://github.com/actions/deploy-pages/releases/tag/v5.0.1) releases.

Remaining owner actions, none performed by adding this workflow:

1. Complete provenance, redistribution, and claim review; commit the approved
   record and selected bundle on `main` through the repository's review process.
2. Enable Pages with **GitHub Actions** as its source. Protect `main`; restrict
   the `github-pages` environment to `main` and require deployment reviewers
   where the repository plan supports those protections.
3. Run the manual workflow from the approved `main` commit and review its
   validation/browser results before approving the deployment environment.
4. Open the actual `page_url` reported by the deployment. Check desktop/mobile
   rendering, keyboard controls, charts, data-through/export dates, asset/data
   requests, approved download contents/units, and browser errors. Record that
   result before describing the public launch as successful.

No Pages setting, environment protection, repository push, deployment, or live
URL verification is implied by local tests. Until the last step is complete,
there is no verified public launch.

### Rollback

Before deployment, a failed gate leaves the existing site untouched. Keep the
checked commit and workflow run for each release; the uploaded Pages artifact
is retained for seven days. For a deployed regression, restore the previous
approved code and review record through a reviewed revert on `main`, retaining
the matching bundle. Rerun the same validation, static build, browser checks,
and manual deployment. Never rebuild from an unrecorded local export or reuse
a synthetic test artifact. Verify the resulting URL again. No rollback requires
deleting raw or processed research files.

## Public-v1 Scope

The public-v1 direction is an explicitly reviewed, versioned research snapshot
feeding the existing static Next.js app, with GitHub Pages as the intended
host. Python remains the analysis and export backend. The commands and manual
workflow above implement publication checks; publication itself still requires
the owner's review and configuration.

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

## Historical Verification Notes

The sections below record earlier states and commands. They do not supersede
the current release gates, approval requirements, or owner actions above.

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

#### Dependency Audit Findings At The Toolchain Baseline

Before the follow-up fixes below, the locked full dependency audit reported
**4 vulnerable packages** (3 high, 1 moderate), covering **10 distinct
advisories** (7 high, 3 moderate). The production-only audit reported one moderate package,
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

#### Toolchain Baseline Verification

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
actual research outputs were unavailable at that baseline. Browser checks and fixtures live
outside the repository.

#### Follow-up Dependency And Icon Fixes: 2026-09-22

The direct PostCSS pin is now 8.5.23, matching Next's copy. The lockfile also
updates `baseline-browser-mapping` to 2.11.25, `brace-expansion` 1.x to 1.1.21,
and `browserslist` to 4.29.0 with its browser data dependencies. Full and
production-only `npm audit` checks report zero vulnerabilities. Strict peer
installation and the installed dependency-tree check pass without overrides.
The ESLint 9 exception remains: the published React, accessibility, and import
plugins still exclude ESLint 10 from their supported peers.

The layout now uses Next's existing `app/icon.svg` metadata convention, which
includes the configured base path, instead of overriding it with `/icon.svg`.
Recharts layout calculations are unchanged. The earlier pixel differences are
library layout changes: Recharts 3 rounds bar widths and preserves fractional
legend measurements. They do not justify hard-coded responsive offsets.

Compatible existing local daily outputs were recovered for UI validation:
20 countries, 2005-01-04 through 2026-06-30. The local export includes these
daily results and explicitly labeled monthly sample data. This exposed a
quantile-chart bug: unrelated regression coefficients were plotted with the
emerging-market GPR label. The exporter now reuses the legacy dashboard's
two-term GPR selection; a regression test verifies both terms across multiple
percentiles while preserving their estimates and inference fields. The quantile
axis displays one decimal place so half-basis-point ticks have distinct labels.
No models were rerun, and no numerical estimates or source CSVs were changed.

Recovered outputs are not an approved public snapshot. Daily provenance
manifests and snapshot review are still missing; local browser validation
does not establish empirical replication or authorize publication.
