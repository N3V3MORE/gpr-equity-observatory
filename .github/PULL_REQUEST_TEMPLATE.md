## Summary

What changed?

## Type

- [ ] Data ingestion or source metadata
- [ ] Feature engineering
- [ ] Econometrics or forecasting
- [ ] Dashboard or reporting
- [ ] Documentation
- [ ] Tests or CI

## Checks

- [ ] `ruff check .` passes
- [ ] `pytest --cov=gprobs --cov=app --cov-report=term-missing -q` passes
- [ ] No raw restricted data committed
- [ ] No secrets or local source paths committed
- [ ] Docs updated if methods, data, outputs, or claims changed

## Data and Reproducibility Impact

Does this change affect generated data, tables, figures, screenshots, manifests,
or dashboard outputs?

If yes, describe what must be rebuilt and which artifacts are intentionally
committed or ignored.

## Interpretation Impact

Does this change affect public-facing research claims?

If yes, explain how the README, research note, dashboard copy, or limitations
were updated to avoid overclaiming.
