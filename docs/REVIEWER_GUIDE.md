# Reviewer Guide

This guide gives reviewers a short path through the project without requiring
them to inspect every script first.

## 5-Minute Review

- If using ChatGPT web or another external reviewer, start with
  [docs/CHATGPT_WEB_ANALYSIS_GUIDE.md](CHATGPT_WEB_ANALYSIS_GUIDE.md). It lists
  the smallest useful file bundle and the claim-safety rules.
- Read the main finding in [README.md](../README.md).
- Open [reports/RESULTS_BRIEF.md](../reports/RESULTS_BRIEF.md) for the generated
  result summary.
- Skim [reports/screenshots](../reports/screenshots) to see the dashboard shape.
- Check [docs/PROFILE_PACKAGING.md](PROFILE_PACKAGING.md) for the short project
  explanation and interview framing.

Use this path to understand what the project is, what it claims, and what it
does not claim.

## 15-Minute Review

- Read [docs/RESEARCH_NOTE.md](RESEARCH_NOTE.md) for the research question,
  methods, current results, and limitations.
- Open [docs/PROJECT_STATUS.md](PROJECT_STATUS.md) to see what is implemented
  and which future work has been scoped.
- Review [docs/REPRODUCIBILITY_CHECKLIST.md](REPRODUCIBILITY_CHECKLIST.md) for
  the commands needed to rebuild and check the project.
- Look at the dashboard screenshots, especially the overview, robustness, and
  panel-regression images.

Use this path to judge whether the empirical story is coherent and cautious.

## 30-Minute Technical Review

- Read [docs/TECHNICAL_APPENDIX.md](TECHNICAL_APPENDIX.md) for data definitions,
  generated outputs, model notes, and known caveats.
- Inspect `scripts/run_task.py` for the unified task runner and `scripts/build_all.py`
  for the daily rebuild path.
- Inspect `src/gprobs/analysis/` for the empirical model implementations.
- Inspect `tests/` for data-contract, dashboard-output, model-behavior, and
  documentation checks.
- Run the checks from
  [docs/REPRODUCIBILITY_CHECKLIST.md](REPRODUCIBILITY_CHECKLIST.md) if you want
  local verification.

Use this path to assess maintainability, test coverage, and reproducibility.

## Dashboard Path

When running the Streamlit app locally, start with these tabs:

- Overview: data scope, GPR series, and top-level context.
- Panel Regression: controlled and date fixed-effects results.
- Robustness: event-study and sample-robustness checks.
- Tail Risk and Local Projections: downside and response-path diagnostics.
- Prediction Lab: out-of-sample drawdown-risk classification diagnostics.
- Monthly Benchmark: separate lower-frequency benchmark status and tables.
- Data Coverage: coverage gaps and large-return flags.

The daily ETF dashboard is the primary workflow. The monthly benchmark tab is a
separate aggregate layer and should not be mixed with the daily country ETF
panel as one empirical sample.

## What Not To Overclaim

- Do not describe the results as causal.
- Do not describe the project as a trading system or investment advice.
- Do not claim that emerging markets definitely react more strongly.
- Do not treat monthly sample mode as empirical evidence.
- Do not treat the two-market monthly benchmark as country-clustered panel
  proof.

The current project finds cautious evidence that geopolitical risk is associated
with equity-market risk, while the emerging-market asymmetry result remains
mixed and not statistically strong in the current specification.

## Local Run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

For the exact locked environment:

```powershell
uv sync --all-extras
```

Build the daily workflow:

```powershell
python scripts/build_all.py
```

Run the dashboard:

```powershell
streamlit run app.py
```

Run checks:

```powershell
ruff check .
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```
