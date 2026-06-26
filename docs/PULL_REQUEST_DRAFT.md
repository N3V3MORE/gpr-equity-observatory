# Draft Pull Request

## Title

```text
[codex] Polish reviewer path and launch packaging
```

## Body

```markdown
## Summary

This PR prepares the packaging branch on top of the GPR Equity Observatory merge
branch for review and portfolio presentation. It does not add new research,
data, model, dashboard, or product behavior.

## What Changed

- Clarified the README reviewer path and cautious public claim.
- Added `docs/REVIEWER_GUIDE.md` with 5-minute, 15-minute, and 30-minute review
  paths.
- Added `docs/REPRODUCIBILITY_CHECKLIST.md` for clean-clone rebuild checks.
- Clarified the local-first launch path in `docs/DEPLOYMENT_GUIDE.md`.
- Added `docs/LAUNCH_CHECKLIST.md` for GitHub/profile launch steps.
- Added `docs/SCREENSHOT_REFRESH.md` and refreshed the committed dashboard
  screenshots.
- Tightened `.github/PULL_REQUEST_TEMPLATE.md` with scope and
  interpretation guardrails.
- Tightened data-source, method, and release-hardening issue templates with
  scope gates.
- Added an issue-template chooser that disables blank issues and points
  reviewers to the reviewer guide, roadmap, and reproducibility checklist.
- Aligned setup commands across README, technical appendix, deployment guide,
  and reproducibility docs.
- Added documentation-contract tests that keep GitHub template guardrails and
  public setup commands from drifting.
- Removed machine-specific GeoRiskLab local path details from committed handoff
  and merge-plan docs.
- Linked the controlled GitHub backlog issues from `docs/ROADMAP.md`.
- Updated `docs/PROJECT_STATUS.md`, `docs/IMPLEMENTATION_CHECKLIST.md`, and
  `docs/FUTURE_AGENT_HANDOFF.md` to reflect the current release state.

## Feature Scope

This packaging branch does not add new research, data, model, dashboard, or
product behavior. Feature work was unlocked after this packaging pass; dashboard
CSV downloads and missing-data UI improvements are tracked in issue #2 and are
eligible for a later scoped feature branch.

## Validation

- [x] `uv run --all-extras pytest tests\test_documentation_contracts.py -q`
- [x] `uv run --all-extras ruff check .`
- [x] `uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q`
- [x] `uv run --all-extras python scripts/run_task.py monthly-sample --min-train-months 24`
- [x] `uv run --all-extras python scripts/run_task.py build-daily`
- [x] Browser smoke check of the refreshed dashboard screenshots.
- [x] Recent docs-only wording updates: `git diff --check` and
      `uv run --all-extras pytest tests\test_documentation_contracts.py -q`

## Notes For Reviewers

Start with:

- `README.md`
- `docs/REVIEWER_GUIDE.md`
- `reports/RESULTS_BRIEF.md`
- `docs/RESEARCH_NOTE.md`
- `docs/TECHNICAL_APPENDIX.md`
- `docs/PROFILE_PACKAGING.md`
- `docs/LAUNCH_CHECKLIST.md`
```
