# Implementation Checklist

This checklist compares the original project goals with the current v5
repository. It is an audit note, not marketing copy.

## MVP Success

| Requirement | Status | Evidence |
| --- | --- | --- |
| Clean GitHub repo exists | Done | README, source package, tests, scripts, CI workflow |
| Base data pipeline works | Done | `python scripts/build_all.py` rebuilds generated daily outputs |
| 20-country return panel exists | Done | `data/country_universe.csv` and generated returns panel |
| GPR shock series exists | Done | `scripts/build_gpr_dataset.py` and generated `gpr_daily.csv` |
| Event-study results exist | Done | Raw, abnormal-return, and robustness event-study scripts |
| Panel regression results exist | Done | Baseline, controlled, and sample-robustness panel scripts |
| Next.js app runs locally | Done | `python scripts/export_frontend_data.py`, then `npm run dev` in `frontend/` |
| README explains the project clearly | Done | `README.md` |
| Limitations are documented | Done | Research note, technical appendix, status note, results brief |
| Monthly benchmark layer exists | Done | sample/real monthly paths, regressions, forecasts, validation |
| Unified command path exists | Done | `python scripts/run_task.py ...` |

## Strong Profile Success

| Requirement | Status | Evidence |
| --- | --- | --- |
| Research note exists | Done | `docs/RESEARCH_NOTE.md` |
| Dashboard has screenshots or public deployment | Done | `reports/screenshots/` and static Next.js build path |
| Robustness checks exist | Done | Event-window/threshold checks and panel sample checks |
| Local projections or quantile analysis exists | Done | Both local projections and quantile regressions are implemented |
| ML drawdown model exists with time-aware validation | Done | Drawdown classifier with purged chronological validation folds |
| Project can be explained in interviews | Done | `README.md`, `docs/REVIEWER_GUIDE.md`, and `reports/RESULTS_BRIEF.md` |
| Local-first launch path is documented | Done | `docs/DEPLOYMENT_GUIDE.md` |
| Reproducibility checklist exists | Done | `docs/REPRODUCIBILITY_CHECKLIST.md` |

## Excellent-Version Items

| Requirement | Status | Next step |
| --- | --- | --- |
| Unified frontend system | Done | Next.js is the single user-facing app |
| Python-to-frontend export contract | Done | `src/gprobs/dashboard/export.py` and `frontend/public/data` |
| GDELT extension is integrated | Not started | Add only after choosing a narrow country/event scope |
| Country-specific GPR is integrated | Needs decision | Scope source access and validation first |
| Tests and linting are present | Done | Pytest, Ruff, Next lint, and frontend build |
| GitHub Actions run tests | Done | `.github/workflows/tests.yml` |
| Monthly sample pipeline runs in CI | Done | monthly sample job in GitHub Actions |
| Walkthrough video exists | Not started | Record only after the v5 frontend screenshots are final |

## Current Evidence Summary

The current evidence should be described cautiously:

- The controlled panel regression finds a small negative GPR-jump association.
- The emerging-market interaction is not statistically strong after controls.
- Event robustness is mixed.
- Prediction Lab has modest ranking signal, not a trading-grade forecast.
- The standalone `gpr_only` drawdown-risk model is weak.
- Monthly sample mode validates software behavior only.
- Monthly real mode is an aggregate benchmark, not a country-panel proof.

## Remaining Human Choices

- Whether to publish a static frontend snapshot.
- Whether to use a FRED API key for richer macro controls.
- Whether to scrape or manually structure country-specific GPR data.
- Whether to publish any real monthly benchmark outputs outside the local
  machine.
- Whether to record a walkthrough video.

## Recommended Next Move

Keep the repo Next.js-first, refresh screenshots after visual changes, and keep
external data additions in the backlog until each scope is explicitly chosen
and source validation is planned.
