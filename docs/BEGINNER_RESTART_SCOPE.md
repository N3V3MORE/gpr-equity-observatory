# Beginner Restart Scope

Last updated: 2026-07-01

This note records how `gpr_beginner_restart_pack.zip` is being used.

## Decision

Use the restart pack as a readability brief, not as a replacement app.

The pack's useful ideas are:

- readable table first, raw table second
- one visible idea per section
- plain-English notes beside charts and tables
- cautious claim language
- missing-data messages that tell the reader what happened

The pack's Streamlit files are not copied into the public product path. The
repository now treats `frontend/` as the single user-facing app, so the simpler
front door belongs in the Next.js app and the Python JSON exporter.

## In Scope

- Make the first page easier to read before showing technical detail.
- Keep the existing graphs, but put each graph next to the question it answers.
- Add beginner-friendly summaries through `src/gprobs/dashboard/export.py` when
  the frontend needs new reader-facing data.
- Keep raw or technical tables behind details sections when a simpler table can
  answer the first reader question.
- Update docs so a new reader knows what to open first and what not to claim.

## Out Of Scope

- Do not add a second public Streamlit dashboard.
- Do not make the frontend read raw CSV files.
- Do not change model calculations, source ingestion, or generated result
  semantics as part of this readability pass.
- Do not merge monthly benchmark outputs into the daily ETF story.
- Do not describe any result as causal, a trading signal, or investment advice.

## Rollback Plan

This work should be committed in small slices:

1. scope note
2. export contract and tests
3. frontend reading-flow changes
4. docs refresh
5. verification fixes, if any

