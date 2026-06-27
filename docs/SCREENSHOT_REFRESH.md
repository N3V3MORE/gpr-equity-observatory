# Screenshot Refresh

Use this guide when Next.js app visuals change enough that public screenshots
are no longer representative.

## Current Public Screenshots

- `reports/screenshots/dashboard_overview.png`
- `reports/screenshots/dashboard_robustness.png`
- `reports/screenshots/dashboard_panel_regression.png`

These files are committed profile artifacts. Raw downloaded data and generated
processed outputs remain local by default.

## When To Refresh

Refresh screenshots when:

- app layout or section content has visibly changed
- a screenshot no longer matches the current project narrative
- profile material needs an updated visual

Do not refresh screenshots only because the files are old.

## Manual Refresh Process

1. Rebuild the daily workflow:

```powershell
python scripts/build_all.py
```

2. Optional, build monthly sample outputs if Data & Methods needs monthly
   benchmark content:

```powershell
python scripts/run_task.py monthly-sample --min-train-months 24
```

3. Export frontend data and run the app:

```powershell
python scripts/export_frontend_data.py
cd frontend
npm run dev
```

4. Capture representative public views:

- Overview as `reports/screenshots/dashboard_overview.png`
- Market Response as `reports/screenshots/dashboard_robustness.png`
- Regression Evidence or Data & Methods as
  `reports/screenshots/dashboard_panel_regression.png`

5. Check each image before committing:

- the section heading and main content are visible
- text is readable
- no local paths, credentials, or raw source details are shown
- sample-mode monthly outputs are not presented as empirical evidence

6. Run checks:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
cd frontend
npm run lint
npm run build
```

## Interpretation Guardrails

Screenshots are presentation artifacts. They should not change the analysis,
the generated outputs, or the cautious public claim.
