# 08 - Running Commands

Use PowerShell from the repo root.

## 1. Install requirements

```powershell
uv sync --all-extras
```

## 2. Run the original full pipeline

```powershell
uv run --all-extras python scripts/run_task.py build-daily
```

## 3. Run the beginner dashboard

```powershell
uv run --all-extras streamlit run app_restart.py
```

## 4. Run the dev cockpit

```powershell
uv run --all-extras streamlit run app_dev_cockpit.py
```

## 5. Run tests

```powershell
uv run --all-extras pytest -q
```

## 6. Run linting

```powershell
uv run --all-extras ruff check .
```

## 7. If Streamlit opens the wrong page

Stop the terminal with:

```powershell
Ctrl + C
```

Then run the exact command again.

## 8. If a file is missing

Run:

```powershell
uv run --all-extras python scripts/run_task.py build-daily
```

Then refresh the Streamlit page.

## 9. If the full pipeline is too slow

Use the dev cockpit and run only one step at a time.
