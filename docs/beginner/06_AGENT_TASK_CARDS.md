# 06 - Agent Task Cards

Copy one task card into Codex or another coding agent.

## Task card 1: Create beginner home page

```text
You are the Beginner UI Agent.

Goal:
Create or update app_restart.py so it opens a beginner-friendly Streamlit page.

Files allowed:
app_restart.py

Do:
- show project title
- show a Project Summary Table
- show a Files Used Table
- show an Output File Status Table
- use simple pandas and Streamlit only
- include comments for a beginner

Do not:
- edit app.py
- edit scripts/
- edit src/
- add regressions
- add new research claims

Definition of done:
uv run --all-extras streamlit run app_restart.py works
the page explains the project without requiring code knowledge
missing files show clear warnings
```

## Task card 2: Add GPR page

```text
You are the Beginner UI Agent.

Goal:
Add a GPR Data page to app_restart.py.

Files allowed:
app_restart.py

Use:
data/processed/gpr_daily.csv

Show:
- daily GPR line chart
- top 25 GPR shock table
- recent GPR rows

Rules:
- rename columns into plain English
- add a short explanation above every chart and table
- hide raw table in an expander

Definition of done:
a beginner can explain what GPR is and identify the biggest shocks
```

## Task card 3: Add market reaction page

```text
You are the Table Translation Agent.

Goal:
Add a Market Reaction page to app_restart.py.

Files allowed:
app_restart.py

Use:
data/processed/group_return_summary.csv
data/processed/event_study_abnormal_summary.csv

Show:
- cumulative developed versus emerging return chart
- event-study chart
- readable Market Reaction Table

Rules:
- do not show raw technical table first
- include Direction and Evidence Strength columns
- use plain-English notes

Definition of done:
the page says whether market reaction is clear, mixed, or weak
```

## Task card 4: Add regression translation page

```text
You are the Table Translation Agent.

Goal:
Add a Regression Results page to app_restart.py.

Files allowed:
app_restart.py

Use:
data/processed/panel_regression_controlled.csv
data/processed/panel_regression_date_fe.csv
data/processed/quantile_regression_results.csv

Show:
- Regression Translation Table first
- raw tables only inside expanders

Rules:
- explain p-values with simple labels
- do not claim causation
- do not say emerging markets react more unless evidence supports it

Definition of done:
a beginner can explain what the regression page says in two sentences
```

## Task card 5: Add dev cockpit

```text
You are the Beginner UI Agent.

Goal:
Create app_dev_cockpit.py.

Files allowed:
app_dev_cockpit.py

Show:
- buttons to run major pipeline steps
- live logs
- progress bar
- output file status table
- preview of latest GPR chart and evidence table

Rules:
- do not change pipeline scripts
- run scripts through subprocess
- show errors clearly
- never fail silently

Definition of done:
uv run --all-extras streamlit run app_dev_cockpit.py opens and shows file status
```

## Task card 6: QA pass

```text
You are the QA Agent.

Goal:
Check that the beginner files do not break the original project.

Run:
uv run --all-extras python -m compileall app_restart.py app_dev_cockpit.py
uv run --all-extras pytest -q
uv run --all-extras ruff check .

Report:
- what passed
- what failed
- exact command output summary
- smallest safe fix if needed

Do not:
- rewrite unrelated code
- change research logic
```
