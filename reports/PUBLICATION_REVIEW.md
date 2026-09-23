# Public-v1 publication review — 2026-09-23

**A real candidate is prepared, but publication remains blocked by rights and
attribution review.** It is not approved or deployed. This run recovered fresh
source provenance and reproduced the core results; it did not recover the old
results' acquisition history.

Repository delivery includes the exporter code, tests, and this review only.
The unapproved candidate bundle, review draft, source caches, and supporting
evidence remain local; their paths below do not exist in a fresh GitHub checkout.

## Candidate and evidence

- Snapshot: `daily-etf-20260923-jun2026-candidate`.
- Bundle: `publication/snapshots/daily-etf-20260923-jun2026-candidate/`.
- Unapproved review draft:
  `publication/daily-etf-20260923-jun2026-candidate.review-draft.json`.
- Local acquisition, reproduction, and validation evidence:
  `data/interim/public-review-20260923/`. This ignored directory must be retained
  separately; its source caches are **not** publication files.
- Starting checkout: clean `main` at
  `3a5606d64beeb50ce22e753c6df7944d4dbf98d0`. Existing exports and research files
  were preserved. Candidate preparation made no approval record, commit, push,
  deployment, or settings change. The later request to push code and this review
  does not approve or publish the candidate data.

The bundle has exactly 12 selected files: `data/{manifest,copy,overview,
gpr_timeline,event_study,regression,country_coverage,reader_summaries}.json` and
`downloads/{event_study,regression_controlled,regression_date_fe,country_coverage}.csv`.
The draft checksums all 12. No raw quotes, cookies, private paths, monthly sources,
Prediction Lab outputs, or optional datasets are included. The GPR timeline
does contain selected source-index values and event labels, so its rights review
is essential. The manifest remains `candidate` / `unreviewed`, and all reviewer
and redistribution-approval fields remain blank.

## What was reproduced

The project had no raw or processed daily inputs. A previously retained export
had usable results, but no evidence of acquisition timestamps, raw-source hashes,
or the processing run. It was used only for comparison.

Fresh retrieval used the existing official GPR XLS endpoint and Yahoo through
the locked `yfinance` dependency. Actual acquisitions occurred on 2026-09-23:
GPR completed 17:26:48.795 UTC; the ETF batch 17:26:51.149; controls 17:26:51.433;
and an INDA-only retry 17:28:37.983. A local yfinance cache-lock failure left INDA
empty in the first batch; validation stopped before fitting models. The retry
replaced only that empty series. Both attempts and all acquired files survive.

`completed-run-receipt.json` records the code revision, source-code and dependency
lock hashes, parameters, acquisition start/completion times, four source-cache
hashes, ten derived-output hashes, and processing functions. The GPR hash covers
original downloaded XLS bytes. Yahoo hashes cover the existing downloader's
serialized provider-returned OHLCV frames and request metadata, **not HTTP wire
bytes or a processed-return file substituted for a source hash**. The draft
records the original ETF batch plus the separate INDA source and their combination.

Only daily returns, GPR flags, controls, the panel, raw/abnormal event summaries,
and baseline/controlled/date-FE regressions were rebuilt. Existing Python
functions and estimators were used unchanged, sequentially, in
`uv run --locked --all-extras` (Python 3.14.4). These NumPy/statsmodels/linearmodels
estimators use CPU/OpenBLAS; the available GPU is not a supported backend.
No monthly, forecasting, Prediction Lab, robustness, quantile, or local-projection
models were run.

The market request was 2005-01-01 through exclusive 2026-07-01. Fresh GPR was
capped at inclusive 2026-06-29 before shock calculation, retaining all earlier
history, to match the retained candidate's GPR endpoint. This is a newly acquired
historical vintage, not a claim to reproduce the original acquisition exactly.

## Coverage and data quality

There are **20 ETFs and 101,258 return observations**, 2005-01-04–2026-06-30.
Fourteen ETFs have 5,405 observations from 2005-01-04. The shorter histories are:

| ETF | First return | Observations |
|---|---|---:|
| ECH | 2007-11-21 | 4,679 |
| INDA | 2012-02-06 | 3,620 |
| EIDO | 2010-05-10 | 4,060 |
| EPOL | 2010-05-27 | 4,047 |
| THD | 2008-04-02 | 4,590 |
| TUR | 2008-03-31 | 4,592 |

All end 2026-06-30. No duplicate source-price dates or panel `(date,ticker)` keys
were found; no interior ETF price gaps or missing returns remained after the
retry. Coverage equals the retained export, but source values are a fresh vintage.
Six observations exceed the existing absolute 0.20 log-return diagnostic threshold;
the largest magnitude is 0.26257079 (EWZ, 2020-03-16). These are review flags,
not automatic evidence of errors; log returns must not be described as identical
simple percentage changes.

The displayed GPR timeline has 7,847 dates, 2005-01-04–**2026-06-29**. Therefore
the 20 June 30 panel rows have missing GPR and are excluded from regressions.
Controls have 4,583 complete dates, 2008-03-31–2026-06-30. Their absence affects
11,647 panel rows across 822 dates, including nine dates after controls begin
(listed in `candidate-validation.json`); nothing was imputed. Baseline/date-FE models use 101,238 rows;
the controlled model uses 89,591. The full panel headline is not the sample size
of every fitted model.

There are **985 flagged shock days, 67 selected cluster-peak dates, and 50 dates
represented in the abnormal study** within displayed coverage. The top 25 jumps
are a separate ranking. The retained export had 988 flags and the same selected
dates: four flags dropped and one was added. Sixty-seven displayed GPR levels
and 100 changes differ, concentrated in the latest part of the history. Without
the old source files, the causes of every difference cannot be isolated. One
genuine GPR zero, two change zeros, and 7,843 null event labels remain intact.

## Current estimates and comparison

Regression estimates and standard errors below are **basis points per one-SD
daily GPR jump**. Their inference is clustered by ticker and date.

| Estimate | New estimate | New SE | New p | Retained export estimate / p | Old brief estimate / p |
|---|---:|---:|---:|---:|---:|
| Controlled developed-market association | -0.4283 | 0.4619 | 0.3538 | -0.4363 / 0.3515 | -0.4 / 0.325 |
| Controlled emerging differential | -0.6783 | 0.9767 | 0.4873 | -0.7234 / 0.4642 | -0.5 / 0.574 |
| Date-FE emerging differential | -0.6771 | 0.9713 | 0.4858 | -0.7392 / 0.4499 | -0.6 / 0.563 |

At relative day +5, abnormal cumulative log returns are -4.5622 bps for developed
ETFs (SE 11.6695, p=0.6960, 500 observations, 50 events) and +15.5754 bps for
emerging ETFs (SE 20.4147, p=0.4459, 463 observations, 50 events). Accumulation
includes days **-5 through +5**, not day 0 onward. Day 0 is each ETF's first
available trading observation on or after the selected event date. Existing
event-study SEs/p-values are **not adjusted for dependence between ETFs exposed
to common events**; no confidence intervals were invented. The maximum abnormal
cumulative-return difference from the retained export is 0.000833 bps.

The existing raw-window pre-inception alignment defect remains unchanged and
explicitly disclosed. Its raw fields remain in JSON, but do not feed the public
abnormal chart/table/CSV. The abnormal builder's estimation-history requirement
rejects those pre-inception cases. Fixing raw alignment requires a separate
research change. No estimator was silently corrected in this task.

Python-generated current-answer text follows the new estimates: conditional
associations in USD ETF proxies, including currency exposure, with weak statistical
evidence. This is neither causal evidence, proof of no effect, nor a trading
recommendation. The old brief remains historical and must not substitute for this
candidate's estimates. Sign retention across specifications is not a robustness claim.

## Rights and remaining owner decisions

Official sources were checked on **2026-09-23**:

- The [GPR source page](https://www.matteoiacoviello.com/gpr.htm) applies
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) to its material.
  Confirm attribution to Caldara–Iacoviello (2022), source and license links,
  actual download date, and disclosure of clipping/computed changes/flags.
  The current frontend links the authors' index, but does not yet display the
  license, acquisition date, and transformation disclosure together. Complete
  that attribution before publication; this report does not grant permission.
- [Yahoo US terms, section 2](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html#s2),
  updated August 4, 2026, include restrictions concerning automated collection,
  reuse, reproduction/distribution/derivatives, and materially substitutive
  products. No explicit grant for this project's aggregate estimate downloads
  was established. The owner must document the applicable permission or other
  basis for publishing ETF- and control-derived results. This includes ACWI,
  VIX, WTI, UUP, and the Treasury-yield proxy, not only country ETFs.
  [yfinance documentation](https://ranaroussi.github.io/yfinance/) and
  [Yahoo's provider disclosure](https://help.yahoo.com/kb/SLN2310.html) do not
  establish that permission. Software licenses do not license source market data.
- Review the June 29 GPR / June 30 ETF endpoints, unequal model samples, six
  large-return flags, unadjusted event inference, and retained raw-window
  limitation. Decide whether to select this exact candidate or request a
  separately scoped research revision. Then explicitly approve its exact hashes
  only after the rights and attribution questions are resolved.

Fresh-run acquisition and processing provenance is available; original-vintage
lineage remains unknown. Technical checks cannot resolve the outstanding rights
decision. Nothing here is a legal permission signoff.

## Checks and reproducibility

- `run_core.py` recorded the initial partial-download failure;
  `complete_core.py` completed the bounded retry and core reproduction.
- `uv run --locked --all-extras python scripts/export_frontend_data.py --root data/interim/public-review-20260923 --target data/interim/public-review-20260923/export --profile public` passed.
- From `frontend/`, `npm run snapshot:prepare -- --source ../data/interim/public-review-20260923/export --id daily-etf-20260923-jun2026-candidate` and `npm run snapshot:hashes -- --id daily-etf-20260923-jun2026-candidate` passed.
- Independent reconstruction matched acquired caches to returns, controls, GPR
  flags, and panel CSVs. All source/lock/code/output hashes checked. Public
  regression and event numbers equal their source CSV values; missingness and
  genuine zero values are checked separately. Candidate contract, all 12 hashes,
  and all four table/CSV unit conversions passed existing snapshot validators.
  Re-run the saved checks with
  `uv run --locked --all-extras python data/interim/public-review-20260923/validate_candidate.py --results candidate-validation-rerun.json`;
  the original `candidate-validation.json` is preserved.
- Exporter tests: **56 passed**; three existing event-definition/coverage tests
  passed. `uv run --locked --all-extras ruff check .` and `git diff --check` passed.
- The unchanged frontend/Python baseline has a successful
  [main CI run](https://github.com/N3V3MORE/gpr-equity-observatory/actions/runs/35893206889),
  including Python, deterministic monthly, and root/prefixed frontend jobs.
  Those results are reused, not claimed as a new empirical run.
- An isolated ordinary `npm run build` and
  `npm run test:browser -- tests/browser/artifact.spec.cjs` passed (**6 tests,
  exit 0**) using the exact candidate, preserving `candidate` / `unreviewed`.
  Actual-artifact desktop/mobile browser checks cover
  static research content, nonempty charts, keyboard details/downloads, exact
  requested datasets, assets/favicon, CSV equality, and horizontal overflow.
  All 12 built data/download hashes match. No browser errors or warnings occurred.
  Actual screenshots and `browser-checks.json` are in
  `data/interim/public-review-20260923/preview/evidence/root-final/`:
  `desktop-candidate.png`, `desktop-evidence.png`, `mobile-overview-full.png`,
  and `mobile-evidence.png` were visually inspected. No synthetic data was used.
  Next telemetry was disabled for this process after a sandbox permission error.
  Playwright teardown lingered; stopping only its identified local server let
  the runner exit successfully. Preview servers are stopped.
- `npm run snapshot:validate -- --tracked` and `npm run build:public` both exit 1
  because `publication/approved-snapshot.json` is absent: **expected guard
  rejections, not successful releases**.

Code changes are limited to `scripts/export_frontend_data.py`,
`src/gprobs/dashboard/export.py`, and `tests/test_frontend_export.py`: an explicit
public core-only export path, unchanged default local behavior, and regression
tests. This report and the selected candidate are new. Research estimators,
frontend source, old results, and original exports are unchanged. Keep the local
source receipts/caches when reviewing or reverting the exporter patch; no
published release needs rollback.
