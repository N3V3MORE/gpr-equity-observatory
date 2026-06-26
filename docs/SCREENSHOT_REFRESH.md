# Screenshot Refresh

Use this guide when dashboard visuals change enough that the public screenshots
are no longer representative.

## Current Public Screenshots

- `reports/screenshots/dashboard_overview.png`
- `reports/screenshots/dashboard_robustness.png`
- `reports/screenshots/dashboard_panel_regression.png`

These files are committed profile artifacts. Raw downloaded data and generated
processed outputs remain local by default.

## When To Refresh

Refresh screenshots when:

- dashboard layout or tab content has visibly changed
- a screenshot no longer matches the current dashboard narrative
- profile or blog material needs an updated visual

Do not refresh screenshots just because the files are old. If the visible UI is
still representative, leave them unchanged.

## Manual Refresh Process

1. Rebuild the daily workflow:

```powershell
python scripts/build_all.py
```

2. Optional, build monthly sample outputs if the Monthly Benchmark tab is part
   of the screenshot pass:

```powershell
python scripts/run_task.py monthly-sample --min-train-months 24
```

3. Run the dashboard:

```powershell
streamlit run app.py
```

4. Capture the same public views:

- Overview tab as `reports/screenshots/dashboard_overview.png`
- Robustness tab as `reports/screenshots/dashboard_robustness.png`
- Panel Regression tab as `reports/screenshots/dashboard_panel_regression.png`

5. Check each image before committing:

- the tab title and main content are visible
- text is readable
- no local paths, credentials, or raw source details are shown
- sample-mode monthly outputs are not presented as empirical evidence

6. Run checks:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

## Interpretation Guardrails

Screenshots are presentation artifacts. They should not change the analysis,
the generated outputs, or the cautious public claim. The current public claim is
that geopolitical risk is associated with equity-market risk, while the
emerging-market asymmetry result remains mixed and not statistically strong in
the current specification.
