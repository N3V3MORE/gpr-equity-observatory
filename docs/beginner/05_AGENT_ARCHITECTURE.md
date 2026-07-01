# 05 - Agent Architecture

This project should use agents like small assistants, not like one giant genius.

Each agent gets one job.

## Overall flow

```text
User asks for a simple improvement
  goes to
Planner Agent
  breaks into one small task
  then assigns to
UI Agent, Data Agent, Table Agent, QA Agent, or Docs Agent
  then
Claim Safety Agent reviews wording
```

## Agent 1: Planner Agent

Mission:

```text
Turn vague requests into one small next step.
```

Allowed files:

```text
docs/beginner/
```

Not allowed:

```text
Do not edit model code.
Do not rewrite the whole dashboard.
```

Output:

```text
A short task plan with files to touch and definition of done.
```

## Agent 2: Beginner UI Agent

Mission:

```text
Make Streamlit pages easier to understand.
```

Allowed files:

```text
app_restart.py
app_dev_cockpit.py
```

Rules:

```text
Use simple code.
Use comments.
Use clear headings.
Use readable tables before raw tables.
Hide technical tables in expanders.
```

Not allowed:

```text
Do not change research calculations.
Do not invent claims.
```

## Agent 3: Table Translation Agent

Mission:

```text
Convert raw CSV outputs into readable user-facing tables.
```

Allowed files:

```text
app_restart.py
docs/beginner/03_USER_FACING_TABLES.md
```

Rules:

```text
Every table answers a question.
Every column name is human-readable.
Every row has plain-English interpretation.
```

## Agent 4: Data Pipeline Agent

Mission:

```text
Keep the original data pipeline working.
```

Allowed files:

```text
scripts/
src/gprobs/data/
src/gprobs/features/
src/gprobs/models/
tests/
```

Rules:

```text
Preserve existing output filenames.
Preserve existing dashboard compatibility.
Add tests when changing calculations.
```

## Agent 5: QA Agent

Mission:

```text
Run checks and catch broken files.
```

Allowed files:

```text
tests/
docs/beginner/qa/
```

Checks:

```text
uv run --all-extras pytest -q
uv run --all-extras ruff check .
uv run --all-extras python scripts/run_task.py build-daily if requested
streamlit import smoke check
```

## Agent 6: Claim Safety Agent

Mission:

```text
Make sure the project does not overclaim.
```

Allowed files:

```text
app_restart.py
README.md
docs/
reports/
```

Rules:

```text
Prefer association language.
Do not say causation.
Do not say trading signal.
Do not say proven.
Do not turn a weak or mixed result into a headline.
```

## Agent 7: Documentation Agent

Mission:

```text
Make the project understandable for a beginner.
```

Allowed files:

```text
README.md
docs/beginner/
docs/REVIEWER_GUIDE.md
```

Rules:

```text
Write short sections.
Use tables.
Use examples.
Avoid jargon unless it is explained immediately.
```

## Why not one huge agent?

One huge agent will try to refactor everything.

This project needs small safe steps.
