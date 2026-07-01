# 07 - Copy-Paste Prompts

Use these when asking Codex or another coding agent to work on the repo.

## Prompt 1: Start the beginner layer

```text
Read AGENTS.md and docs/beginner/00_START_HERE.md.

Create app_restart.py as a beginner-friendly Streamlit dashboard.

Only implement Step 1:
- project title
- plain-English summary table
- files used table
- output file status table

Do not edit app.py.
Do not edit scripts or src.
Do not add charts yet.
Keep the code simple and heavily commented.
```

## Prompt 2: Add live build cockpit

```text
Read AGENTS.md and docs/beginner/05_AGENT_ARCHITECTURE.md.

Create app_dev_cockpit.py.

The page should:
- list important output CSV files
- show whether each exists
- show row counts
- show last modified times
- have buttons to run pipeline steps
- show live logs from subprocess
- preview gpr_daily.csv and evidence_summary.csv when they exist

Do not change the actual pipeline scripts.
```

## Prompt 3: Improve table readability

```text
Read docs/beginner/03_USER_FACING_TABLES.md.

Update app_restart.py so raw technical outputs are not shown first.

For every raw result table:
- create a readable table first
- rename columns into plain English
- add a Plain-English note column
- hide raw data in an expander

Do not change the calculations.
```

## Prompt 4: Review claims

```text
Review app_restart.py, README.md, and docs/beginner/.

Find wording that overclaims results.

Replace words like causes, proves, predicts, guaranteed, and trading signal.

Use cautious words:
associated with, linked to, suggests, mixed, exploratory, not enough alone.

Do not change code logic.
```
