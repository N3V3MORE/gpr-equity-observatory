# Dashboard Understandability Design

Date: 2026-06-26

## Scope

Improve the Streamlit dashboard so a non-technical reviewer can understand the
research question, evidence shape, and limitations quickly. This is a
front-end-only branch for issue #2 style usability work.

## Approved Direction

Use the combined mockup direction approved on 2026-06-26:

1. Add a guided first screen with a cautious plain-English project summary.
2. Add four Overview cards: Question, Data, Methods, and Bottom line.
3. Add an Evidence Map that presents the existing `evidence_summary` output
   with cautious evidence-strength labels.
4. Rename and reorder the main daily-dashboard tabs into a story sequence:
   Overview, GPR Shock Timeline, Market Response, Regression Evidence,
   Downside Risk, Dynamic Response, Prediction Lab, Country Sensitivity, and
   Data Quality.
5. Add a short "How to read this" note to each daily-dashboard tab.
6. Add a visual GPR shock timeline with top-shock markers using existing GPR
   output data.
7. Add CSV download buttons under major dashboard tables.
8. Simplify the missing-data message so the first recommendation is
   `python scripts/build_all.py`, with advanced individual commands hidden in
   an expander.

## Guardrails

- Do not change model logic, data generation scripts, regression logic, or ML
  logic.
- Do not add external data.
- Do not change generated CSV schemas.
- Do not describe results as causal.
- Do not frame the dashboard as investment advice or a trading system.
- Preserve sample/real data boundaries and monthly benchmark limitations.

## Implementation Plan

Use small commits:

1. Scope record commit.
2. Guided Overview commit.
3. Story tabs and how-to-read notes commit.
4. Timeline, downloads, and missing-data utility commit.

Each implementation commit should add or update focused tests before changing
dashboard behavior, then run the relevant checks before committing.

## Verification

At minimum, run:

```powershell
uv run --all-extras ruff check .
uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

If dashboard behavior changes materially, also run a Streamlit smoke test.
