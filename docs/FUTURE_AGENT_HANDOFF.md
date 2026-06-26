# Future Agent Handoff

Internal maintainer note. This file is for local agents and maintainers, not
the public reviewer path.

Last updated: 2026-06-26

This is the entry point for a fresh agent picking up GPR Equity Observatory.
Read this before changing code, docs, data, or Git state.

For an AI-assisted internal review context, use
`docs/internal/REVIEW_CONTEXT_FOR_AI_TOOLS.md`. It lists a compact file bundle,
safe upload boundaries, current result snapshot, and review prompts.

Feature lock was lifted on 2026-06-26. Read `docs/FEATURE_LOCK.md` before
making any change. New features are allowed only when their scope is recorded
and the standing data and claim-safety guardrails are preserved.

## Current State

The repository is on `main`, pushed to `origin/main`.

Latest pushed state checked in this handoff:

- `599e56b Merge prediction lab and dashboard updates`
- working tree was clean when this handoff was written

GPR Equity Observatory remains the destination repository and public Streamlit
research product. GeoRiskLab has been absorbed selectively as reproducibility,
provenance, validation, sample/real mode discipline, and a separate monthly
developed/emerging benchmark layer.

The GeoRiskLab + GPR Equity Observatory merge completed Phases 0 through 9. The
historical merge branch was `codex/pre-merge-gpr-cleanup`; do not treat that
branch as the current delivery branch.

The former forward-plan packaging and dashboard work has also been merged to
`main`: reviewer navigation, reproducibility checklists, local-first launch
guidance, refreshed screenshots, screenshot refresh instructions, PR/issue
template guardrails, issue-template chooser, documentation-contract tests,
guided dashboard tabs, dashboard helper refactors, and the Prediction Lab
extension.

Generated ignored outputs may exist locally from verification runs. Do not
commit or delete generated raw/processed data unless the user explicitly asks.

## Important Paths

- Destination repo: `<local project root>`
- GitHub remote:
  `https://github.com/N3V3MORE/gpr-equity-observatory.git`
- AI review context guide: `docs/internal/REVIEW_CONTEXT_FOR_AI_TOOLS.md`
- Project status note: `docs/PROJECT_STATUS.md`
- Reviewer guide: `docs/REVIEWER_GUIDE.md`
- Reproducibility checklist: `docs/REPRODUCIBILITY_CHECKLIST.md`
- Technical appendix: `docs/TECHNICAL_APPENDIX.md`
- Research note: `docs/RESEARCH_NOTE.md`
- Source policy: `docs/DATA_SOURCES.md`
- Roadmap: `docs/ROADMAP.md`
- Feature-lock policy: `docs/FEATURE_LOCK.md`
- Historical merge plan: `docs/GEORISKLAB_GPR_MERGE_PLAN.txt`

Read `docs/GEORISKLAB_GPR_MERGE_PLAN.txt` only when merge history matters. It
is long and historical; it is not the shortest context path for review.

## What Is Implemented

- Daily 20-country ETF panel remains the primary empirical workflow.
- Daily Caldara-Iacoviello GPR ingestion remains in place.
- Market controls remain available through no-key public sources.
- Event study, abnormal-return event study, robustness checks, panel
  regressions, sample-robustness checks, quantile regressions, local
  projections, rolling sensitivity, evidence summary, and generated results
  brief are in the main workflow.
- Prediction Lab extends the drawdown classifier with six model variants,
  out-of-sample prediction rows, Brier score, threshold metrics, calibration,
  lift, and country risk summaries.
- Monthly benchmark sample mode exists as deterministic software validation.
- Monthly benchmark real mode exists for user-supplied local GPR and Kenneth
  French factor files.
- Source manifests and redaction rules exist for real monthly inputs.
- Monthly developed/emerging HAC spread regressions exist.
- Monthly expanding-window forecast comparisons with historical-mean benchmarks
  and OOS R2 exist.
- `scripts/run_task.py` is the unified command path for daily and monthly tasks.
- `app.py` includes guided daily tabs, Prediction Lab, and Monthly Benchmark.
- The dashboard can run when monthly outputs are absent; the monthly tab shows
  setup guidance instead of breaking the daily dashboard.
- CI includes the existing lint/test matrix and a deterministic monthly sample
  pipeline job.
- Docs explain daily/monthly separation, sample/real boundaries, current
  findings, limitations, deployment, reproducibility, and profile packaging.

## What Was Intentionally Not Done

- GeoRiskLab was not copied wholesale into this repository.
- The original GeoRiskLab dashboard was not imported.
- Monthly benchmark outputs are not mixed into the daily ETF panel.
- Monthly sample outputs are not treated as empirical evidence.
- Monthly real aggregate benchmark outputs are not presented as country-panel
  proof.
- GDELT is not presented as a current real-data finding.
- Country-specific GPR data is not integrated yet.
- FRED controls are not integrated because that requires an API-key decision.
- No custom project MCP server was added; existing local filesystem, Git,
  semantic navigation, GitHub tools, and search tools were sufficient.

## GitHub Backlog Issues

Open backlog issues created from the forward plan:

- [#1 Package current project for portfolio use](https://github.com/N3V3MORE/gpr-equity-observatory/issues/1)
- [#2 Improve dashboard usability without changing models](https://github.com/N3V3MORE/gpr-equity-observatory/issues/2)
- [#3 Decide deployment data strategy](https://github.com/N3V3MORE/gpr-equity-observatory/issues/3)
- [#4 Plan future FRED macro-controls extension](https://github.com/N3V3MORE/gpr-equity-observatory/issues/4)
- [#5 Scope later country-specific GPR or GDELT extension](https://github.com/N3V3MORE/gpr-equity-observatory/issues/5)

Some issue labels may now be partially satisfied by work already merged to
`main`; check current code and docs before opening new work.

## Commands Future Agents Should Use

Prefer the locked environment:

```powershell
uv sync --all-extras
```

Run the full verification set before calling code work complete:

```powershell
uv run --all-extras ruff check .
uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q
uv run --all-extras python scripts/run_task.py monthly-sample --min-train-months 24
uv run --all-extras python scripts/run_task.py build-daily
```

Run the dashboard:

```powershell
uv run --all-extras streamlit run app.py
```

Useful focused commands:

```powershell
uv run --all-extras python scripts/run_task.py lint
uv run --all-extras python scripts/run_task.py test
uv run --all-extras python scripts/run_task.py validate-monthly-sample
uv run --all-extras python scripts/run_task.py build-monthly-real
uv run --all-extras python scripts/run_task.py validate-monthly-real
```

`build-monthly-real` requires `config/sources.yml` and local source files. Do
not invent those paths or commit that config.

## Verification Already Completed

Recent post-push validation on `main` completed successfully:

- `uv run --all-extras python scripts\build_all.py`
- `uv run --all-extras python scripts\run_task.py monthly-sample --min-train-months 24`
- `uv run --all-extras ruff check .`
- `uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q`
- `uv run --all-extras python scripts\run_task.py build-daily`
- headless Streamlit smoke test returned HTTP 200
- Prediction Lab output sanity checks: probabilities bounded, all saved
  prediction rows out of sample, metric ranges valid, expected model variants
  present

If a future agent changes code or docs, rerun the relevant checks. Do not rely
only on historical verification.

## Data And Output Policy

- Do not commit raw third-party market data.
- Do not commit local source files.
- Do not commit credentials.
- Do not commit `config/sources.yml`.
- Do not commit real generated monthly outputs unless the user explicitly
  chooses a publication policy.
- Do not delete generated local data unless the user asks.
- Keep sample outputs and real outputs separate in names, paths, docs, and UI
  text.
- Treat source manifests and validation checks as part of the research contract,
  not optional cleanup.

## Interpretation Rules

- This is not a trading system.
- This is not investment advice.
- Do not claim causality.
- Do not claim that emerging markets always react more strongly.
- Use cautious language such as "associated with", "conditional response",
  "risk-classification experiment", and "benchmark estimate".
- Daily ETF results and monthly benchmark results answer different questions.
- Monthly sample mode validates software behavior only.
- Monthly real mode is an aggregate benchmark layer, not country-clustered panel
  inference.
- Prediction Lab is out-of-sample risk classification, not a price forecast.

## Current Results To Preserve

The project's strongest current result is methodological: the repository now has
a reproducible, tested workflow that compares event-study, panel, quantile,
local-projection, rolling-sensitivity, Prediction Lab, and monthly benchmark
evidence.

The current empirical story is mixed:

- Controlled daily panel estimates are small and statistically weak.
- Emerging-market interaction evidence is not strong after controls.
- Event robustness depends on shock and window definitions.
- Quantile and local-projection results are useful diagnostics, not proof.
- Prediction Lab has modest ranking signal. The full-feature model has mean ROC
  AUC around `0.617`, average precision around `0.373`, and top-decile lift
  around `1.47x`; the `gpr_only` model is weak.
- Monthly sample outputs are not empirical findings.

Keep this cautious framing unless new validated evidence changes it.

## Known Remaining Choices

These are not blockers for the current `main` state. They are product or
research choices for the user:

- Decide whether to deploy the dashboard publicly.
- Decide whether to publish real monthly benchmark outputs.
- Decide whether to add FRED controls with an API key.
- Decide whether to integrate country-specific GPR data.
- Decide whether to build a narrow GDELT extension.
- Decide whether to publish the blog draft or record a walkthrough video.

## Suggested Skills For Future Agents

- Use `handoff` when preparing another continuation summary.
- Use `review` if asked to audit the branch or repository.
- Use `github:gh-fix-ci` if GitHub Actions fail after push.
- Use `data-analytics:visualize-data` only if creating a new source-backed
  analytical chart or dashboard artifact.
- Use `superpowers:verification-before-completion` before claiming a code
  change is finished.

## First Five Minutes For A New Agent

1. Run `git status -sb`.
2. Read `AGENTS.md`, `docs/FEATURE_LOCK.md`, and this file.
3. If the task involves AI-assisted internal review, read
   `docs/internal/REVIEW_CONTEXT_FOR_AI_TOOLS.md`.
4. Read `docs/PROJECT_STATUS.md` and `docs/ROADMAP.md` for user-facing status
   and backlog.
5. Run focused checks for the requested change before editing.
