# Internal AI Review Context

Use this file when preparing a compact context bundle for an AI-assisted
internal review. Do not upload private local data or credentials.

Next.js is the single user-facing app. Python remains the research and export
backend. The frontend reads generated JSON from `frontend/public/data`.

## Best Files To Upload Or Paste

For a compact project review:

1. `README.md`
2. `docs/PROJECT_STATUS.md`
3. `docs/V5_NEXT_FRONTEND_PLAN.md`
4. `docs/REVIEWER_GUIDE.md`
5. `docs/REPRODUCIBILITY_CHECKLIST.md`
6. `docs/TECHNICAL_APPENDIX.md`
7. `reports/RESULTS_BRIEF.md`
8. `scripts/run_task.py`
9. `scripts/export_frontend_data.py`
10. `src/gprobs/dashboard/export.py`
11. `frontend/src/app/page.tsx`
12. `frontend/src/sections/Overview.tsx`
13. `frontend/src/sections/PredictionLab.tsx`
14. `frontend/src/lib/data.ts`
15. `tests/test_frontend_export.py`
16. `tests/test_frontend_project_contracts.py`
17. `tests/test_documentation_contracts.py`

For deeper method review, add the relevant files under `src/gprobs/analysis/`
and `src/gprobs/data/`.

## What Not To Upload

- `config/sources.yml`
- raw third-party market data
- local monthly source files
- credentials, API keys, `.env` files
- real local generated monthly outputs unless a publication policy exists
- local filesystem paths from the user's machine

## Architecture At A Glance

- Daily ETF workflow: public daily ETF data, daily GPR, market controls, daily
  panel, event studies, regressions, quantile regressions, local projections,
  rolling sensitivity, and Prediction Lab.
- Monthly benchmark workflow: deterministic sample mode and local real mode for
  developed/emerging aggregate benchmark checks.
- Prediction Lab: out-of-sample prediction rows from purged chronological folds,
  plus metrics, lift, calibration, threshold, country-risk, and feature
  importance outputs.
- Frontend handoff: Python exports JSON; Next.js renders it without
  recomputing analysis.

## Claim Rules

- Not a trading system.
- Not investment advice.
- Not causal evidence.
- Do not claim emerging markets always react more strongly.
- Monthly sample mode validates software behavior only.
- Monthly real mode is aggregate benchmark evidence, not country-clustered
  panel inference.

## Verification Commands

```powershell
uv run --all-extras ruff check .
uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q
uv run --all-extras python scripts/run_task.py monthly-sample --min-train-months 24
uv run --all-extras python scripts/run_task.py build-daily
uv run --all-extras python scripts/export_frontend_data.py
cd frontend
npm run lint
npm run build
```

Rendered frontend review should also check that the first page loads, there are
no console warnings or errors, the mobile viewport has no page-level horizontal
overflow, and `rolling_beta.json` loads only after Country Sensitivity is
revealed.
