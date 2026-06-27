## Summary

What changed?

## Type

- [ ] Release hardening
- [ ] Data ingestion or source metadata
- [ ] Feature engineering
- [ ] Econometrics or forecasting
- [ ] Dashboard or reporting
- [ ] Documentation
- [ ] Tests or CI

## Scope and Guardrail Check

- [ ] Any new research, data, model, dashboard, or product behavior has a
      scoped plan, issue, or PR description linked here:
- [ ] Daily ETF outputs and monthly benchmark outputs remain separate in names,
      paths, docs, and dashboard text.
- [ ] Sample-mode outputs are not presented as empirical evidence.

## Checks

- [ ] `ruff check .` passes
- [ ] `pytest --cov=gprobs --cov=app --cov-report=term-missing -q` passes
- [ ] `npm run lint` passes if `frontend/` changed
- [ ] `npm run build` passes if `frontend/` changed
- [ ] `python scripts/run_task.py monthly-sample --min-train-months 24` passes
      if monthly benchmark behavior, validation, or docs changed
- [ ] `python scripts/run_task.py build-daily` passes if daily data, outputs,
      screenshots, or result docs changed
- [ ] No raw restricted data committed
- [ ] No secrets or local source paths committed
- [ ] `config/sources.yml` is not committed
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

Confirm:

- [ ] No causal claim was added without a supporting design.
- [ ] The project is not framed as investment advice or a trading system.
- [ ] Emerging-market asymmetry is not described as a strong result unless the
      validated evidence supports that wording.
