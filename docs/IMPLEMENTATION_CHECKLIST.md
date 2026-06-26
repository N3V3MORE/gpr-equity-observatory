# Implementation Checklist

This checklist compares the original project plan with the current repository.
It is written as a plain-English audit, not as a marketing summary.

## MVP Success

| Requirement | Status | Evidence |
| --- | --- | --- |
| Clean GitHub repo exists | Done | README, source package, tests, scripts, CI workflow |
| Base data pipeline works | Done | `python scripts/build_all.py` rebuilds all generated outputs |
| 20-country return panel exists | Done | `data/country_universe.csv` and generated returns panel |
| GPR shock series exists | Done | `scripts/build_gpr_dataset.py` and generated `gpr_daily.csv` |
| Event-study results exist | Done | Raw, abnormal-return, and robustness event-study scripts |
| Panel regression results exist | Done | Baseline, controlled, and sample-robustness panel scripts |
| Dashboard runs locally | Done | `streamlit run app.py` |
| README explains the project clearly | Done | `README.md` |
| Limitations are documented | Done | Research note, technical appendix, status note, results brief |
| Monthly benchmark layer exists | Done | sample/real monthly data paths, regressions, forecasts, validation, dashboard tab |
| Unified command path exists | Done | `python scripts/run_task.py ...` |

## Strong Profile Success

| Requirement | Status | Evidence |
| --- | --- | --- |
| Research note exists | Done | `docs/RESEARCH_NOTE.md` |
| Dashboard has screenshots or public deployment | Done | `reports/screenshots/` |
| Robustness checks exist | Done | Event-window/threshold checks and panel sample checks |
| Local projections or quantile analysis exists | Done | Both local projections and quantile regressions are implemented |
| ML drawdown model exists with time-aware validation | Done | Drawdown classifier with purged chronological validation folds |
| Project can be explained in interviews | Done | `docs/PROFILE_PACKAGING.md`, `docs/REVIEWER_GUIDE.md`, and `reports/RESULTS_BRIEF.md` |
| CV bullet sounds credible and specific | Done | `docs/PROFILE_PACKAGING.md` |
| Local-first launch path is documented | Done | `docs/LAUNCH_CHECKLIST.md` and `docs/DEPLOYMENT_GUIDE.md` |
| Reproducibility checklist exists | Done | `docs/REPRODUCIBILITY_CHECKLIST.md` |

## Excellent-Version Items

| Requirement | Status | Next step |
| --- | --- | --- |
| GDELT extension is integrated | Not started | Add only after choosing a narrow country/event scope |
| Country-specific GPR is integrated | Needs decision | Official pages exist, but data access is not a simple workbook link |
| Dashboard includes data quality, model diagnostics, and downloads | Mostly done | Data quality and model diagnostics exist; explicit download buttons are tracked in issue #2 |
| Tests and linting are present | Done | Pytest and Ruff are configured |
| GitHub Actions run tests | Done | `.github/workflows/tests.yml` |
| Monthly sample pipeline runs in CI | Done | monthly sample job in `.github/workflows/tests.yml` |
| Blog post is published | Drafted | `docs/BLOG_POST_DRAFT.md`; publishing is outside the repo |
| Walkthrough video or demo script exists | Partial | Three-minute script exists; video is not recorded |

Deployment details are documented in `docs/DEPLOYMENT_GUIDE.md`. External-data
choices are documented in `docs/DATA_SOURCE_DECISIONS.md`.
Future-agent continuation context is documented in
`docs/FUTURE_AGENT_HANDOFF.md`.
Current future work is tracked in the GitHub issues linked from
`docs/ROADMAP.md`.

## Current Evidence Summary

The current evidence should be described cautiously:

- The controlled panel regression finds a small negative GPR-jump association.
- The emerging-market interaction is not statistically strong after controls.
- Event robustness is mixed: the 90th-percentile shock definition is more
  supportive of emerging-market downside than the 95th-percentile definition.
- Sample robustness keeps the controlled GPR-jump coefficient negative, but the
  emerging-market interaction remains weak.
- The ML drawdown classifier has modest ranking signal, not a trading-grade
  forecast.
- Monthly sample mode is not empirical evidence.
- Monthly real mode is an aggregate benchmark, not a country-panel proof.

## Roadblocks That Need User Input

These are the main choices that require a human decision:

- Whether to use a FRED API key for richer macro controls.
- Whether to scrape or manually structure country-specific GPR data from the
  official country pages.
- Whether to deploy the Streamlit app publicly, and where.
- Whether to publish the blog post as-is or adapt it for a specific platform.
- Whether to record a walkthrough video.
- Whether to publish any real monthly benchmark outputs outside the local
  machine.

## Recommended Next Move

The project is already strong as a reproducible local research product. The
packaging branch has moved the public-facing docs, screenshots, reviewer guide,
reproducibility checklist, and launch checklist into release shape. The next
repo-level move is review:

1. Push the packaging branch and open a draft pull request when ready.
2. Review the branch before merge.
3. Decide whether the dashboard stays local-first or needs a documented public
   deployment snapshot.
4. Keep richer external data and dashboard usability additions in the GitHub
   backlog until those scopes are explicitly unlocked.
