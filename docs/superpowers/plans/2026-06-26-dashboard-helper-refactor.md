# Dashboard Helper Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Continue the dashboard cleanup by moving reusable helper logic out of `app.py` without changing rendered dashboard behavior.

**Architecture:** Add small modules under `src/gprobs/dashboard` that hide formatting and display helper implementation behind narrow interfaces. Keep `app.py` as the orchestration and tab-rendering file until each helper group is moved and tested.

**Tech Stack:** Python, pandas, Streamlit, Plotly Express, pytest, ruff, uv.

---

## Scope

This plan covers the txt file's PR 2 cleanup in small slices:

1. Move pure formatting/evidence helpers to `src/gprobs/dashboard/formatting.py`.
2. Move Streamlit UI helpers to `src/gprobs/dashboard/components.py`.
3. Move Plotly chart builders to `src/gprobs/dashboard/charts.py`.

Do not move tab render functions in this plan unless the helper moves are clean and fully verified. Do not change output schemas, generated data, model code, or research wording.

## Task 1: Pure Formatting Helpers

**Files:**
- Create: `src/gprobs/dashboard/formatting.py`
- Modify: `app.py`
- Modify: `tests/test_dashboard_display.py`

- [ ] **Step 1: Write failing tests**

Add tests that import `gprobs.dashboard.formatting` and assert:

```python
from gprobs.dashboard import formatting


def test_formatting_helpers_render_reader_values():
    assert formatting.format_percent(0.1234) == "12.3%"
    assert formatting.format_basis_points(-0.0042) == "-42.0 bp"
    assert formatting.format_p_value(0.0321) == "0.032"
    assert formatting.format_p_value(pd.NA) == ""
    assert formatting.format_metric(pd.NA) == ""
```

- [ ] **Step 2: Verify red**

Run:

```powershell
uv run --all-extras pytest tests/test_dashboard_display.py -q
```

Expected: failure because `gprobs.dashboard.formatting` does not exist yet.

- [ ] **Step 3: Move pure helpers**

Create `src/gprobs/dashboard/formatting.py` with:

- `format_percent`
- `format_basis_points`
- `format_p_value`
- `format_metric`
- `classify_evidence_strength`
- `format_evidence_direction`
- `format_evidence_estimate`

Import those helpers into `app.py` and remove the moved helper bodies from `app.py`.

- [ ] **Step 4: Verify green and commit**

Run:

```powershell
uv run --all-extras pytest tests/test_dashboard_display.py tests/test_app_structure.py -q
uv run --all-extras ruff check app.py src/gprobs/dashboard/formatting.py tests/test_dashboard_display.py
git add app.py src/gprobs/dashboard/formatting.py tests/test_dashboard_display.py
git commit -m "refactor: move dashboard formatting helpers"
```

## Task 2: UI Components

Move Streamlit helpers after Task 1 is committed:

- `render_intro`
- `render_summary_cards`
- `render_how_to_read`
- `render_csv_download`
- `render_missing_data_message`

Add tests that require the helpers to live in `gprobs.dashboard.components`.

## Task 3: Chart Builders

Move Plotly helpers after Task 2 is committed:

- `build_gpr_shock_timeline`
- group-return chart builder
- event-study chart builder
- robustness chart builder
- quantile chart builder
- local-projection chart builder
- feature-importance chart builder
- rolling-beta chart builder

Add tests that require the chart builders to live in `gprobs.dashboard.charts`.

## Verification Before Completion

Run:

```powershell
uv run --all-extras ruff check .
uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

If rendered dashboard behavior is affected, also run a Streamlit smoke test.
