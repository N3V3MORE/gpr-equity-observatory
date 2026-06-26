# Reproducibility Checklist

Use this checklist when rebuilding the project from a clean clone. The goal is
to verify the software workflow, not to publish raw third-party data.

## Environment

- Use Python 3.11 or newer.
- Install regular development dependencies:

```powershell
python -m pip install -r requirements.txt
```

- For the exact resolver-locked environment, use:

```powershell
uv sync --all-extras
```

## Checks

- Run lint:

```powershell
ruff check .
```

- Run tests with the same coverage target used by the repo:

```powershell
pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

If the local Python environment does not already have the project dependencies,
run the same commands through `uv run --all-extras`.

## Rebuild

- Rebuild the daily ETF workflow:

```powershell
python scripts/build_all.py
```

- Or use the unified task runner:

```powershell
python scripts/run_task.py build-daily
python scripts/run_task.py monthly-sample --min-train-months 24
```

The monthly sample pipeline is deterministic software validation. It is not
empirical evidence.

## Dashboard

- Run the Streamlit dashboard:

```powershell
streamlit run app.py
```

The app expects daily processed outputs under `data/processed/`. If monthly
benchmark outputs are absent, the Monthly Benchmark tab should show setup
guidance instead of breaking the daily dashboard.

## Expected Local Outputs

Generated files are local by default and ignored by Git:

- `data/raw/`
- `data/interim/`
- `data/processed/`
- `data/metadata/`
- `reports/tables/`
- `reports/figures/`

Committed profile artifacts include `reports/RESULTS_BRIEF.md` and
`reports/screenshots/`.

## External Data Caveats

- Free public market data can revise, fail temporarily, or hit provider limits.
- ETF inception dates differ, so country coverage can differ by ticker.
- ETF returns are USD returns and include currency exposure.
- Monthly real mode requires local user-supplied GPR and Kenneth French files.

If public data downloads fail, retry later, check provider availability, and
avoid rewriting model conclusions from a partial rebuild.

## Do Not Commit

- `.env` files, API keys, or credentials.
- `config/sources.yml`.
- Raw third-party market data.
- Local monthly source files.
- Real generated monthly outputs unless a data-publication decision is made.

Before showing the project widely, confirm that lint and tests pass, the daily
pipeline rebuilds, the dashboard runs locally, and the public wording remains
cautious.

For ChatGPT web or another external reviewer, use
`docs/CHATGPT_WEB_ANALYSIS_GUIDE.md` to choose a safe, compact file bundle and
avoid uploading local-only data or credentials.
