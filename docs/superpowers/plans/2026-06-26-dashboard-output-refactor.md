# Dashboard Output Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move dashboard output schemas, loading, validation, and missing-file detection out of `app.py` without changing dashboard behavior or generated output contracts.

**Architecture:** Create `src/gprobs/dashboard/outputs.py` as the seam for dashboard CSV output contracts. `app.py` remains the Streamlit orchestration file and imports the same names from the new module so current tests and callers continue to work.

**Tech Stack:** Python, pandas, Streamlit cache decorator, pytest, ruff, uv.

---

## Scope

This plan implements the txt file's code-cleanup PR 1 only:

- Move `OutputSpec`, `OUTPUT_SPECS`, `REQUIRED_FILES`, `load_outputs`, `validate_output_schema`, and `missing_files`.
- Keep monthly output loading in `app.py` for this slice because it currently depends on monthly dashboard rendering types and path configuration.
- Keep reusable Streamlit components, chart builders, and tab renderers in `app.py` for later cleanup slices.
- Do not change generated CSV paths, required columns, model code, data pipeline scripts, or dashboard research wording.

## Task 1: Pin Output Module Ownership

**Files:**
- Modify: `tests/test_app_outputs.py`
- Modify: `tests/test_output_schemas.py`

- [ ] **Step 1: Write failing tests**

Add imports and assertions requiring the output contract to live in `gprobs.dashboard.outputs`:

```python
from gprobs.dashboard import outputs as dashboard_outputs


def test_dashboard_output_contracts_live_in_dashboard_outputs_module():
    assert dashboard_outputs.OutputSpec is app.OutputSpec
    assert dashboard_outputs.OUTPUT_SPECS is app.OUTPUT_SPECS
    assert dashboard_outputs.REQUIRED_FILES is app.REQUIRED_FILES
    assert dashboard_outputs.load_outputs is app.load_outputs
    assert dashboard_outputs.validate_output_schema is app.validate_output_schema
    assert dashboard_outputs.missing_files is app.missing_files
```

- [ ] **Step 2: Verify red**

Run:

```powershell
uv run --all-extras pytest tests/test_app_outputs.py tests/test_output_schemas.py -q
```

Expected: failure because `gprobs.dashboard.outputs` does not exist yet.

## Task 2: Move Output Contracts

**Files:**
- Create: `src/gprobs/dashboard/outputs.py`
- Modify: `app.py`

- [ ] **Step 1: Create the new module**

Move this code from `app.py` to `src/gprobs/dashboard/outputs.py`:

- `PROJECT_ROOT`
- `DATA_DIR`
- `OutputSpec`
- `OUTPUT_SPECS`
- `REQUIRED_FILES`
- `load_outputs`
- `validate_output_schema`
- `missing_files`

The module imports should be:

```python
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st
```

- [ ] **Step 2: Import moved names in `app.py`**

Replace the moved definitions with:

```python
from gprobs.dashboard.outputs import (
    DATA_DIR,
    OUTPUT_SPECS,
    PROJECT_ROOT,
    REQUIRED_FILES,
    OutputSpec,
    load_outputs,
    missing_files,
    validate_output_schema,
)
```

Keep `PROJECT_ROOT` and `OutputSpec` re-exported through `app.py` because monthly code and current tests still use them.

- [ ] **Step 3: Verify green**

Run:

```powershell
uv run --all-extras pytest tests/test_app_outputs.py tests/test_output_schemas.py tests/test_app_structure.py -q
uv run --all-extras ruff check app.py src/gprobs/dashboard/outputs.py tests/test_app_outputs.py tests/test_output_schemas.py
```

Expected: both commands exit 0.

## Task 3: Commit PR 1 Refactor Slice

**Files:**
- Add: `src/gprobs/dashboard/outputs.py`
- Modify: `app.py`
- Modify: `tests/test_app_outputs.py`
- Modify: `tests/test_output_schemas.py`

- [ ] **Step 1: Review diff**

Run:

```powershell
git diff -- app.py src/gprobs/dashboard/outputs.py tests/test_app_outputs.py tests/test_output_schemas.py
```

Confirm the diff only moves output contracts and updates tests.

- [ ] **Step 2: Commit**

Run:

```powershell
git add app.py src/gprobs/dashboard/outputs.py tests/test_app_outputs.py tests/test_output_schemas.py
git commit -m "refactor: move dashboard output contracts"
```

## Verification Before Moving To PR 2

Run:

```powershell
uv run --all-extras ruff check .
uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

Do not start the component/chart refactor until this slice is committed and the worktree is clean.
