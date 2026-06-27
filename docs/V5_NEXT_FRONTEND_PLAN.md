# v5 Next.js Frontend Consolidation

Last updated: 2026-06-27

v5 makes Next.js the single user-facing app for GPR Equity Observatory. Python
remains the research and export backend.

## Scope

- `frontend/` is the canonical public dashboard.
- `src/gprobs/dashboard/export.py` is the dashboard-facing backend contract.
- `frontend/public/data/*.json` is generated and presentation-only.
- Streamlit is retired from the public product path.
- No research logic, model output semantics, data-source rules, or empirical
  conclusions change as part of v5.

## Guardrails

- Keep the daily 20-country ETF workflow separate from the monthly benchmark.
- Keep monthly sample mode visibly non-empirical.
- Do not commit raw third-party data, local source files, credentials, or
  `config/sources.yml`.
- Do not present the project as causal, investment advice, or a trading system.
- Keep the monthly two-market aggregate benchmark limitations visible.

## Required v5 Workflow

```powershell
python scripts/build_all.py
python scripts/run_task.py monthly-sample --min-train-months 24
python scripts/export_frontend_data.py
cd frontend
npm run lint
npm run build
```

The frontend may run locally with `npm run dev` after the Python export step.
