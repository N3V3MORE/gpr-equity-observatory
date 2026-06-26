# Deployment Guide

This guide explains what is ready for deployment and what still needs a choice.
It is intentionally practical: the current app runs locally, but a public
deployment needs a data strategy.

## Current Local Run

Local use is straightforward:

```powershell
python -m pip install -r requirements.txt
python scripts/build_all.py
streamlit run app.py
```

For the exact resolver-locked environment, run `uv sync --all-extras` first.
If the local Python environment does not already have dependencies installed,
run the same commands through `uv run --all-extras`.

The dashboard expects generated daily files in `data/processed/`. Those files
are not committed to Git because the project keeps downloaded and generated
market data out of version control.

The Monthly Benchmark tab is optional. If monthly benchmark outputs are absent,
the app still runs with the daily ETF dashboard and shows build instructions in
the monthly tab. To populate the deterministic monthly sample tab locally, run:

```powershell
python scripts/run_task.py monthly-sample --min-train-months 24
```

## Local-First Portfolio Path

The lowest-risk public presentation path is local-first:

- keep the Streamlit app as a locally runnable dashboard
- use [reports/RESULTS_BRIEF.md](../reports/RESULTS_BRIEF.md) as the short
  public result summary
- use [reports/screenshots](../reports/screenshots) for dashboard visuals
- use [docs/REVIEWER_GUIDE.md](REVIEWER_GUIDE.md) for reviewer navigation
- use [docs/BLOG_POST_DRAFT.md](BLOG_POST_DRAFT.md) or a shortened LinkedIn
  version for the project narrative
- use [docs/LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md) for the manual GitHub and
  profile steps

This path avoids committing generated market data and avoids a public app that
starts without its required processed files. It is a complete portfolio option,
not a fallback.

## Streamlit Community Cloud Path

The simplest public hosting option is Streamlit Community Cloud.

Official Streamlit deployment docs:

- [Prep and deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
- [Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)

Expected settings:

- Repository: this GitHub repository.
- Branch: `main`.
- Entry point: `app.py`.
- Python version: choose Python 3.11 if available.
- Dependencies: `requirements.txt`.

## Deployment Blocker

The current repository is not fully one-click deployable because
`data/processed/` is ignored by Git. On Streamlit Cloud, the app would start
without the processed CSV files unless we choose one of the options below.

This is not a code bug. It is a data-publication decision.

## Data Strategy Options

### Option A: Commit Small Processed Outputs

Commit selected generated CSVs under `data/processed/`.

Pros:

- Easiest deployment.
- Fast dashboard startup.
- Reproducible dashboard snapshot.

Cons:

- Needs a data-licensing comfort check.
- Generated outputs can become stale.
- The repo becomes larger.
- Monthly sample outputs are not empirical evidence and must be labelled as
  sample mode if published.

### Option B: Build Data During Deployment

Have the app or deployment process run the data pipeline before loading the
dashboard.

Pros:

- No generated market data committed.
- Always rebuilds from source scripts.

Cons:

- Slow and fragile for a hosted dashboard.
- Free data downloads can fail or rate-limit.
- Streamlit app startup becomes harder to explain.

### Option C: External Artifact Storage

Store processed outputs outside Git, then download them during deployment.

Pros:

- Keeps Git clean.
- Avoids slow full rebuilds on app startup.

Cons:

- Needs another storage location.
- Adds operational complexity.
- Requires deciding who can access the files.

### Monthly Real-Mode Warning

Do not commit `config/sources.yml`, raw monthly source files, or real local
paths. Real monthly outputs are local only by default. If they are published,
the source manifests must be checked for redaction and the dashboard must label
them as real monthly aggregate benchmark outputs.

## Recommendation

For a student profile project, use one of these paths:

1. Keep the dashboard local-first and use screenshots plus
   `reports/RESULTS_BRIEF.md` publicly.
2. If public deployment matters, choose Option A after checking whether you are
   comfortable committing derived processed outputs.

Do not deploy a public app that silently fails because processed data is
missing. That would weaken the project more than keeping it local and well
documented.

Do not deploy sample-mode monthly outputs as if they were empirical findings.
