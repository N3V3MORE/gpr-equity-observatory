# Launch Checklist

Use this checklist when presenting GPR Equity Observatory as a portfolio
project. It keeps public launch work separate from future feature work.

## GitHub Repository

- Pin the repository on the GitHub profile if this is the project to lead with.
- Use [docs/PULL_REQUEST_DRAFT.md](PULL_REQUEST_DRAFT.md) when opening the
  packaging branch pull request.
- Use this repository description:

```text
Reproducible quant economics project studying geopolitical risk and equity-market responses across developed and emerging market ETF proxies.
```

- Suggested topics:
  - `python`
  - `economics`
  - `finance`
  - `econometrics`
  - `streamlit`
  - `geopolitical-risk`
  - `panel-data`
  - `event-study`
  - `reproducible-research`

## Public Materials

- Use [reports/RESULTS_BRIEF.md](../reports/RESULTS_BRIEF.md) for the short
  result summary.
- Use [docs/REVIEWER_GUIDE.md](REVIEWER_GUIDE.md) for reviewer navigation.
- Use [docs/PROFILE_PACKAGING.md](PROFILE_PACKAGING.md) for the CV bullet,
  LinkedIn summary, interview talking points, and walkthrough script.
- Use [docs/BLOG_POST_DRAFT.md](BLOG_POST_DRAFT.md) for a longer project
  narrative.
- Use [reports/screenshots](../reports/screenshots) for dashboard visuals.

## Pre-Launch Checks

- Confirm the README screenshot renders.
- Confirm the main claim remains cautious:

```text
Geopolitical risk is associated with equity-market risk, while the emerging-market asymmetry result remains mixed and not statistically strong in the current specification.
```

- Confirm the project is not described as causal, investment advice, or a
  trading system.
- Confirm `config/sources.yml`, raw source files, credentials, and local
  generated data are not committed.
- Run:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

## Deployment Decision

The default launch path is local-first: GitHub repository, screenshots, results
brief, blog/profile material, and local dashboard instructions.

Do not publish a Streamlit app until the data strategy in
[docs/DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) and
[#3 Decide deployment data strategy](https://github.com/N3V3MORE/gpr-equity-observatory/issues/3)
is resolved.

## Future Work Boundary

Feature work is unlocked, but keep these as scoped backlog items until the user
chooses one for implementation:

- dashboard CSV downloads and missing-data UI changes:
  [#2](https://github.com/N3V3MORE/gpr-equity-observatory/issues/2)
- FRED macro controls:
  [#4](https://github.com/N3V3MORE/gpr-equity-observatory/issues/4)
- country-specific GPR or GDELT:
  [#5](https://github.com/N3V3MORE/gpr-equity-observatory/issues/5)
