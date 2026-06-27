# Clarify Project Question Scope

## Goal

Make the public dashboard answer one central question more clearly:

> When geopolitical risk jumps, does it help us understand or rank downside
> risk in international equity markets, especially for emerging markets?

## In Scope

- Add a stronger "What are we solving?" section to the Overview tab.
- Add a Method Map that links each dashboard method to its research or
  prediction job.
- Add a cautious "What the answer is so far" summary.
- Add a visible "What this does not prove" box.
- Update tab-facing copy only where it reinforces the central question.

## Out Of Scope

- No model logic changes.
- No output schema changes.
- No data pipeline changes.
- No new datasets.
- No stronger causal, trading, or emerging-market-asymmetry claims.

## Verification

- `uv run --all-extras ruff check .`
- `uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q`
