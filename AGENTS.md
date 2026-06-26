# Agent Instructions

This repository is the destination for the GeoRiskLab + GPR Equity Observatory
merge unless the user explicitly says otherwise.

Before making project-level changes, read `docs/FUTURE_AGENT_HANDOFF.md`. It is
the current handoff entry point for the completed merge branch, release state,
verification commands, and remaining decisions.

This branch is feature locked. Read `docs/FEATURE_LOCK.md` before editing. Do
not add new research, data, model, dashboard, or product features unless the
user explicitly unlocks feature work.

## Project Direction

- Keep GPR Equity Observatory as the public Streamlit app and research product.
- Keep the daily 20-country ETF panel as the primary dashboard workflow.
- Port GeoRiskLab code selectively into `src/gprobs`; do not copy the whole
  GeoRiskLab repository into this repo.
- Keep daily ETF datasets and monthly aggregate benchmark datasets separate in
  names, output paths, docs, and dashboard text.
- Preserve sample/real data boundaries. Sample mode proves software behavior; it
  is not empirical evidence.

## Data Policy

- Do not commit raw third-party market data, local source files, credentials, or
  `config/sources.yml`.
- Do not delete generated raw/processed data unless the user specifically asks.
- Source manifests and validation checks are part of the research contract, not
  optional cleanup.
- Before importing MIT-licensed GeoRiskLab code, make an explicit license
  decision for this repository.

## Research Claims

- Do not describe results as causal unless the design actually supports it.
- Do not frame the project as a trading system or investment advice.
- Use cautious language such as "associated with", "conditional response", or
  "benchmark estimate" when discussing model results.
- Keep limitations visible when using the monthly two-market aggregate benchmark;
  it is not credible country-clustered panel inference.

## Checks

Run these before calling code work complete:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

Use `uv run --all-extras ...` for those commands if the local Python environment
does not already have the project dependencies installed.

## Local Agent State

- Do not commit `.claude/`.
- Do not commit `.serena/cache/`.
- Do not copy GeoRiskLab's local root name, `New folder`, into committed docs or
  config.
