# Merged Update Summary

This file is retained as a concise summary of the branch that was merged into
`main`. It is no longer a pending pull-request draft.

## Current State

The reviewer-path, dashboard, monthly benchmark, and Prediction Lab work is
merged and pushed to `main`.

Latest pushed merge commit when this file was updated:

```text
599e56b Merge prediction lab and dashboard updates
```

## What Changed

- Clarified the README reviewer path and cautious public claim.
- Added `docs/CHATGPT_WEB_ANALYSIS_GUIDE.md` for efficient ChatGPT web review.
- Added `docs/REVIEWER_GUIDE.md` with 5-minute, 15-minute, and 30-minute review
  paths.
- Added `docs/REPRODUCIBILITY_CHECKLIST.md` for clean-clone rebuild checks.
- Clarified the local-first launch path in `docs/DEPLOYMENT_GUIDE.md`.
- Added `docs/LAUNCH_CHECKLIST.md` for GitHub/profile launch steps.
- Added `docs/SCREENSHOT_REFRESH.md` and refreshed dashboard screenshots.
- Tightened `.github/PULL_REQUEST_TEMPLATE.md` with scope and interpretation
  guardrails.
- Tightened data-source, method, and release-hardening issue templates with
  scope gates.
- Added an issue-template chooser that disables blank issues and points
  reviewers to the reviewer guide, roadmap, and reproducibility checklist.
- Aligned setup commands across README, technical appendix, deployment guide,
  and reproducibility docs.
- Added documentation-contract tests that keep GitHub template guardrails,
  ChatGPT web context guidance, and public setup commands from drifting.
- Removed machine-specific GeoRiskLab local path details from committed handoff
  docs.
- Linked the controlled GitHub backlog issues from `docs/ROADMAP.md`.
- Added guided dashboard story tabs, Evidence Map, GPR Shock Timeline, reader
  notes, CSV downloads, and clearer missing-data guidance.
- Split dashboard output contracts, formatting, reusable components, and chart
  helpers into `src/gprobs/dashboard/`.
- Extended Prediction Lab with out-of-sample predictions, model variants, Brier
  score, threshold metrics, calibration, lift, and country risk summary.

## Feature Scope

The merged state preserves the daily ETF workflow as the primary public product
and keeps the monthly benchmark layer separate. The Prediction Lab extension is
an out-of-sample risk-classification experiment, not a trading signal.

## Validation

Recent post-push validation on `main` passed:

- `uv run --all-extras python scripts\build_all.py`
- `uv run --all-extras python scripts\run_task.py monthly-sample --min-train-months 24`
- `uv run --all-extras ruff check .`
- `uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q`
- `uv run --all-extras python scripts\run_task.py build-daily`
- Streamlit HTTP smoke check
- Prediction Lab output sanity checks

## Notes For Reviewers

Start with:

- `docs/CHATGPT_WEB_ANALYSIS_GUIDE.md`
- `README.md`
- `reports/RESULTS_BRIEF.md`
- `docs/PROJECT_STATUS.md`
- `docs/RESEARCH_NOTE.md`
- `docs/TECHNICAL_APPENDIX.md`
- `docs/PROFILE_PACKAGING.md`
