# Beginner Restart Scope

Last updated: 2026-07-01

This note records how `gpr_beginner_restart_pack.zip` is being used in this
repository.

## Decision

Use the restart pack as a readability brief, not as a replacement app.

The pack's useful ideas are:

- show the main question before technical output
- lead with graphs and translated tables
- hide raw statistical tables behind details
- explain what changed, what evidence is weak, and what must not be claimed
- keep each improvement small enough to review and roll back

The pack's literal Streamlit files are not being copied into the public product.
This repo's current product path is still:

```text
Python pipeline -> frontend/public/data/*.json -> frontend/ Next.js app
```

## In Scope

- Make the existing Next.js app easier to understand on first load.
- Add graph-forward sections that answer one plain question at a time.
- Add beginner-facing labels, captions, and glossary text through the Python
  export contract when the wording depends on research outputs.
- Preserve technical tables as review material, usually behind details sections.
- Keep monthly benchmark outputs separate from the daily ETF panel.

## Out Of Scope

- Do not add `app_restart.py` or `app_dev_cockpit.py` as public entry points.
- Do not teach TypeScript to parse raw CSVs or rerun analysis.
- Do not replace `src/gprobs/dashboard/export.py` with frontend-side research
  logic.
- Do not publish local real monthly outputs, raw third-party data,
  `config/sources.yml`, credentials, or local source paths.
- Do not turn Prediction Lab into a price forecast, trading signal, or
  investment tool.

## Claim Rules

Use language like "associated with", "mixed evidence", "limited ranking
signal", and "benchmark estimate".

Avoid language like "causes", "proves", "guaranteed", "predicts the market",
"trading signal", and "investment advice".

## Rollback Slices

1. Scope note and guardrail alignment.
2. Python export changes with focused tests.
3. Overview page simplification and graph-forward first screen.
4. Market reaction and regression translation improvements.
5. Prediction Lab and monthly benchmark readability pass.
6. Final verification, rendered app smoke check, and contrarian review.
