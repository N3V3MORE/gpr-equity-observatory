# Beginner Restart Scope

Last updated: 2026-07-01

This note records how `gpr_beginner_restart_pack.zip` is now being used in this
repository.

## Decision

Apply the restart pack as a local beginner layer:

```text
app_restart.py
app_dev_cockpit.py
docs/beginner/
```

These files make the project easier to enter. They do not replace the public
Next.js app, the Python research backend, or the generated JSON contract:

```text
Python pipeline -> frontend/public/data/*.json -> frontend/ Next.js app
```

The file and folder reduction is about the first path a reader sees. The
research, source-validation, and reproducibility folders stay in place unless
the user explicitly asks for a separate cleanup pass.

## In Scope

- Add the pack's beginner Streamlit dashboard and developer cockpit as local
  tools.
- Add `docs/beginner/` as the plain-English entry point.
- Keep the existing Next.js app as the public product path.
- Lead with graphs and translated tables before raw technical output.
- Hide raw statistical tables behind expanders.
- Explain what changed, what evidence is weak, and what must not be claimed.
- Keep monthly benchmark outputs separate from the daily ETF panel.

## Out Of Scope

- Do not teach TypeScript to parse raw CSVs or rerun analysis.
- Do not replace `src/gprobs/dashboard/export.py` with frontend-side research
  logic.
- Do not delete reproducibility, feature-lock, reviewer, source-policy, or
  validation docs as part of this beginner layer.
- Do not publish local real monthly outputs, raw third-party data,
  `config/sources.yml`, credentials, or local source paths.
- Do not turn Prediction Lab into a price forecast, trading signal, or
  investment tool.

## Claim Rules

Use language like "associated with", "mixed evidence", "limited ranking",
"risk-classification experiment", and "benchmark estimate".

Avoid language like "causes", "proves", "guaranteed", "predicts the market",
"trading signal", and "investment advice", except when warning readers what not
to claim.

## Rollback Slices

1. Scope and guardrail alignment.
2. Beginner app and cockpit files.
3. Beginner docs.
4. Focused lint, compile, app-load, and test checks.
5. Final verification, local smoke check, and contrarian review.
