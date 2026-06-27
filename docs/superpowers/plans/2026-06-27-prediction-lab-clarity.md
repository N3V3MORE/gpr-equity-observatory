# Prediction Lab Clarity Scope

## Goal

Make Prediction Lab answer whether GPR adds useful out-of-sample drawdown-risk
ranking information beyond simple baseline and stress features.

## In Scope

- Keep the beginner model explanation column as `what_it_uses`.
- Use explicit baseline-delta columns for AUC, average precision, and Brier
  score.
- Keep cautious plain-English model verdicts.
- Add a visible Prediction Lab conclusion sentence.
- Keep metric explanations visible in the dashboard.

## Out Of Scope

- No changes to `src/gprobs/analysis/drawdown_model.py`.
- No model training changes.
- No pipeline output schema changes.
- No stronger prediction, trading, or investment-advice claims.

## Verification

- `uv run --all-extras ruff check .`
- `uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q`
