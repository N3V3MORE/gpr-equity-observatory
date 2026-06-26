# Future Agent Handoff

Last updated: 2026-06-26

This is the entry point for a fresh agent picking up the GeoRiskLab + GPR Equity
Observatory merge work. Read this before changing code, docs, data, or Git
state.

This branch is feature locked. Read `docs/FEATURE_LOCK.md` before making any
change. Release hardening is allowed; new features require an explicit user
unlock.

## Current Answer

The merge implementation is complete through Phases 0 through 9 on branch
`codex/pre-merge-gpr-cleanup`.

A forward-plan packaging branch, `codex/polish-readme-reviewer-path`, now sits
on top of the locked merge branch. It adds reviewer navigation, reproducibility
checklists, local-first launch guidance, refreshed screenshots, screenshot
refresh instructions, PR/issue template guardrails, a release-hardening issue
template, an issue-template chooser, setup-command alignment,
documentation-contract tests for those release guardrails, local path hygiene,
and links to the GitHub backlog issues. It does not add new research, data,
model, dashboard, or product behavior.

GPR Equity Observatory remains the destination repository and public Streamlit
research product. GeoRiskLab has been absorbed selectively as reproducibility,
provenance, validation, sample/real mode discipline, and a separate monthly
developed/emerging benchmark layer.

The current working tree was clean when this handoff was written. Generated
ignored outputs may exist locally from verification runs; do not commit or
delete them unless the user explicitly asks.

## Important Paths

- Destination repo: `C:\Users\Sushmit\Desktop\Code\GPR_Observer`
- Original GeoRiskLab local source was inspected during planning; the
  machine-specific local path is intentionally omitted from committed docs.
- GitHub remote for this repo:
  `https://github.com/N3V3MORE/gpr-equity-observatory.git`
- Canonical merge plan: `docs/GEORISKLAB_GPR_MERGE_PLAN.txt`
- Feature-lock policy: `docs/FEATURE_LOCK.md`
- Project status note: `docs/PROJECT_STATUS.md`
- Reviewer guide: `docs/REVIEWER_GUIDE.md`
- Reproducibility checklist: `docs/REPRODUCIBILITY_CHECKLIST.md`
- Screenshot refresh guide: `docs/SCREENSHOT_REFRESH.md`
- Launch checklist: `docs/LAUNCH_CHECKLIST.md`
- Draft pull request text: `docs/PULL_REQUEST_DRAFT.md`
- Requirement audit: `docs/IMPLEMENTATION_CHECKLIST.md`
- Reproducibility contract: `docs/REPRODUCIBILITY.md`
- Source policy: `docs/DATA_SOURCES.md`
- Research methods: `docs/METHODOLOGY.md`
- Public packaging state: `docs/PROFILE_PACKAGING.md`

## Branch And Commit State

The merge branch is `codex/pre-merge-gpr-cleanup`.

The current forward-plan packaging branch is
`codex/polish-readme-reviewer-path`.

Use `git log --oneline --decorate` for the full exact branch state, or add
`--max-count=16` for a short current view. Representative packaging branch
milestone commits include, newest first:

- `1dbd57e docs: refresh issue template summary`
- `1ba17fd docs: add issue template chooser`
- `f844038 docs: add release hardening issue template`
- `649ce1b docs: refresh guardrail summary`
- `c4aff24 test: cover setup command docs`
- `0ad135c test: cover template guardrails`
- `54fbdea docs: refresh release handoff`
- `1416412 docs: omit local GeoRiskLab path`
- `f6e0d34 docs: align setup commands`
- `e73bced docs: tighten issue templates`
- `5e4b43b docs: tighten pull request template`
- `5914430 docs: add pull request draft`
- `4a2aebc docs: update implementation checklist`
- `170c6e9 docs: update release next steps`
- `8930695 docs: update handoff after screenshot refresh`
- `41e060e docs: refresh dashboard screenshots`
- `33305db docs: add launch checklist`
- `655cc92 docs: add screenshot refresh guide`
- `1cf8451 docs: link project backlog issues`
- `76a2a45 docs: clarify local-first launch path`
- `bef1e46 docs: add reviewer guide`
- `bf1e60f docs: clarify reviewer path`

Current merge commits, newest first:

- `1025f5e docs: add future agent handoff`
- `f34792d docs: refresh final result metrics`
- `8c2835c docs: consolidate merged observatory story`
- `7fe03c2 feat: add monthly benchmark dashboard tab`
- `10e411c chore: add unified monthly task runner`
- `b7e20db feat: add monthly benchmark models`
- `3f60ae2 feat: add monthly benchmark real ingestion`
- `778ddd7 chore: add MIT license`
- `3c76eac feat: add monthly benchmark sample mode`
- `fc0578f chore: add shared merge infrastructure`
- `77369e4 chore: stabilize pre-merge cleanup`

Do not rewrite these commits or reset the branch unless the user asks for that
explicitly.

## What Is Implemented

- Daily 20-country ETF panel remains the primary empirical workflow.
- Daily GPR ingestion remains in place.
- Market controls remain available through no-key public sources.
- Event study, abnormal-return event study, robustness checks, panel
  regressions, quantile regressions, local projections, rolling sensitivity, ML
  drawdown classifier, evidence summary, and generated results brief are in the
  main workflow.
- Monthly benchmark sample mode exists as deterministic software validation.
- Monthly benchmark real mode exists for user-supplied local GPR and Kenneth
  French factor files.
- Source manifests and redaction rules exist for real monthly inputs.
- Monthly developed/emerging HAC spread regressions exist.
- Monthly expanding-window forecast comparisons with historical-mean benchmarks
  and OOS R2 exist.
- `scripts/run_task.py` is the unified command path for daily and monthly tasks.
- `app.py` includes a Monthly Benchmark tab.
- The dashboard can run when monthly outputs are absent; the monthly tab shows
  setup guidance instead of breaking the daily dashboard.
- CI includes the existing lint/test matrix and a deterministic monthly sample
  pipeline job.
- Docs now explain daily/monthly separation, sample/real boundaries, current
  findings, limitations, deployment, reproducibility, and profile packaging.
- The packaging branch adds a reviewer guide, reproducibility checklist,
  screenshot refresh guide, local-first launch guidance, launch checklist,
  draft pull request text, refreshed dashboard screenshots, a feature-lock-aware
  pull request template, feature-lock-aware issue templates, an issue-template
  chooser, aligned setup commands, documentation-contract coverage for release
  guardrails, machine-specific local-path cleanup, and a roadmap section linking
  to the controlled GitHub backlog.

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
- Dashboard CSV downloads and missing-data message simplification were not
  implemented on the packaging branch because they are dashboard feature work
  under the active feature lock. They are tracked in GitHub issue #2.

## GitHub Backlog Issues

Open backlog issues created from the forward plan:

- [#1 Package current project for portfolio use](https://github.com/N3V3MORE/gpr-equity-observatory/issues/1)
- [#2 Improve dashboard usability without changing models](https://github.com/N3V3MORE/gpr-equity-observatory/issues/2)
- [#3 Decide deployment data strategy](https://github.com/N3V3MORE/gpr-equity-observatory/issues/3)
- [#4 Plan future FRED macro-controls extension](https://github.com/N3V3MORE/gpr-equity-observatory/issues/4)
- [#5 Scope later country-specific GPR or GDELT extension](https://github.com/N3V3MORE/gpr-equity-observatory/issues/5)

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

The final merge pass completed these checks successfully:

- `uv run --all-extras ruff check .`
- `uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q`
- `uv run --all-extras python scripts/run_task.py monthly-sample --min-train-months 24`
- `uv run --all-extras python scripts/run_task.py build-daily`
- Headless Streamlit smoke test returned HTTP 200.
- Direct app loader check found daily outputs and monthly sample outputs with
  regression and forecast artifacts available.

If a future agent changes code, rerun the relevant full checks. Do not rely only
on this historical verification.

The packaging branch screenshot refresh was also validated with:

- in-app browser check against `http://127.0.0.1:8507/`
- page title `GPR Equity Observatory`
- Monthly Benchmark tab visible in the rendered app
- no browser console warnings or errors
- `uv run --all-extras ruff check .`
- `uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q`

The setup-command, GitHub-template, issue-template, and local-path hardening
docs were validated with:

- `uv run --all-extras pytest tests\test_documentation_contracts.py -q`
- `uv run --all-extras ruff check .`
- `uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q`

Recent docs-only branch-state and template wording maintenance was checked with:

- `git diff --check`
- `uv run --all-extras pytest tests\test_documentation_contracts.py -q`

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
- Use cautious language such as "associated with", "conditional response", and
  "benchmark estimate".
- Daily ETF results and monthly benchmark results answer different questions.
- Monthly sample mode validates software behavior only.
- Monthly real mode is an aggregate benchmark layer, not country-clustered panel
  inference.

## Current Results To Preserve

The project's strongest current result is methodological: the repository now has
a reproducible, tested workflow that compares event-study, panel, quantile,
local-projection, rolling-sensitivity, ML, and monthly benchmark evidence.

The current empirical story is mixed:

- Controlled daily panel estimates are small and statistically weak.
- Emerging-market interaction evidence is not strong after controls.
- Event robustness is more supportive at some shock/window definitions than
  others.
- Quantile and local-projection results are useful diagnostics, not proof.
- The drawdown classifier has modest ranking signal, not trading-grade forecast
  power.
- Monthly sample outputs are not empirical findings.

Keep this cautious framing unless new validated evidence changes it.

## Known Remaining Choices

These are not blockers for the completed merge branch. They are product or
research choices for the user. Because the branch is feature locked, treat the
data/research items as post-lock work unless the user explicitly unlocks feature
work:

- Push this branch and open a pull request.
- Decide whether to deploy the dashboard publicly.
- Decide whether to publish real monthly benchmark outputs.
- Decide whether to add FRED controls with an API key.
- Decide whether to integrate country-specific GPR data.
- Decide whether to build a narrow GDELT extension.
- Decide whether to publish the blog draft or record a walkthrough video.

## Suggested Skills For Future Agents

- Use `handoff` when preparing another continuation summary.
- Use `review` if asked to audit the branch before merge or PR.
- Use `github:yeet` if the user asks to push and open a draft PR.
- Use `github:gh-fix-ci` if GitHub Actions fail after push.
- Use `data-analytics:visualize-data` only if creating a new source-backed
  analytical chart or dashboard artifact.
- Use `superpowers:verification-before-completion` before claiming a code change
  is finished.

## First Five Minutes For A New Agent

1. Run `git status -sb`.
2. Read `AGENTS.md`, `docs/FEATURE_LOCK.md`, and this file.
3. Read `docs/PROJECT_STATUS.md` and `docs/ROADMAP.md` for the current
   user-facing status and issue backlog.
4. Read `docs/GEORISKLAB_GPR_MERGE_PLAN.txt` only if the task concerns merge
   history or unresolved planning detail.
5. Run focused checks for the requested change before editing.
