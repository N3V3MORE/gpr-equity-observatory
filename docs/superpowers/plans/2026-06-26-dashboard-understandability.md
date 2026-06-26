# Dashboard Understandability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Streamlit dashboard easier for a non-technical reviewer to understand without changing data generation, model logic, or research conclusions.

**Architecture:** Keep this branch in `app.py` because the dashboard has not yet been split into modules. Add small pure display helpers and constants in `app.py`, then call them from the existing render functions. Keep output schemas and generated CSV filenames unchanged.

**Tech Stack:** Python, Streamlit, pandas, Plotly Express, pytest, ruff, uv.

---

## Files

- Modify: `app.py`
  - Add display constants for intro text, tab labels, how-to-read notes, and Evidence Map columns.
  - Add small helpers: `classify_evidence_strength`, `build_evidence_map`, `render_intro`, `render_summary_cards`, `render_how_to_read`, `render_csv_download`, and `render_missing_data_message`.
  - Update existing tab renderers and `main()` orchestration only.
- Modify: `tests/test_app_structure.py`
  - Add structure and wording tests for tab labels, intro text, how-to-read notes, and missing-data helper presence.
- Create or modify: `tests/test_dashboard_display.py`
  - Add pure helper tests for evidence-strength labels and Evidence Map shaping.

## Task 1: Guided Overview

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app_structure.py`
- Create: `tests/test_dashboard_display.py`

- [ ] **Step 1: Write the failing structure tests**

Add to `tests/test_app_structure.py`:

```python
def test_dashboard_intro_keeps_cautious_project_framing():
    assert "20 country ETF proxies" in app.DASHBOARD_INTRO
    assert "does not strongly prove" in app.DASHBOARD_MAIN_TAKEAWAY
    assert "not as a trading system" in app.DASHBOARD_USE_NOTE


def test_dashboard_story_tab_labels_are_declared():
    assert app.DAILY_TAB_LABELS == [
        "Overview",
        "GPR Shock Timeline",
        "Market Response",
        "Robustness",
        "Regression Evidence",
        "Downside Risk",
        "Dynamic Response",
        "Prediction Lab",
        "Country Sensitivity",
        "Monthly Benchmark",
        "Data Quality",
    ]
```

- [ ] **Step 2: Write the failing Evidence Map tests**

Create `tests/test_dashboard_display.py`:

```python
import pandas as pd

import app


def test_classify_evidence_strength_uses_cautious_labels():
    assert app.classify_evidence_strength(pd.Series({"p_value": 0.03, "inference": "negative association"})) == "Useful signal"
    assert app.classify_evidence_strength(pd.Series({"p_value": 0.40, "inference": "mixed evidence"})) == "Mixed"
    assert app.classify_evidence_strength(pd.Series({"p_value": 0.80, "inference": "weak evidence"})) == "Weak"
    assert app.classify_evidence_strength(pd.Series({"p_value": pd.NA, "inference": "exploratory classifier"})) == "Exploratory"


def test_build_evidence_map_adds_strength_and_reader_columns():
    summary = pd.DataFrame(
        [
            {
                "method": "Panel regression",
                "focus": "Emerging-market interaction",
                "estimate": -0.5,
                "unit": "basis points",
                "p_value": 0.57,
                "inference": "weak evidence",
                "plain_english": "No strong asymmetry evidence.",
            }
        ]
    )

    evidence_map = app.build_evidence_map(summary)

    assert list(evidence_map.columns) == [
        "Method",
        "Question answered",
        "Direction",
        "Estimate",
        "p-value / metric",
        "Evidence strength",
        "Plain-English takeaway",
    ]
    assert evidence_map.loc[0, "Evidence strength"] == "Weak"
    assert evidence_map.loc[0, "Plain-English takeaway"] == "No strong asymmetry evidence."
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```powershell
uv run --all-extras pytest tests/test_app_structure.py tests/test_dashboard_display.py -q
```

Expected: failure because the new constants and helpers do not exist yet.

- [ ] **Step 4: Add minimal implementation**

In `app.py`, add the constants near the existing notice constants:

```python
DASHBOARD_INTRO = (
    "This dashboard studies whether equity markets respond to geopolitical risk "
    "shocks, using 20 country ETF proxies."
)
DASHBOARD_MAIN_TAKEAWAY = (
    "Geopolitical risk appears associated with equity-market risk, but the "
    "evidence does not strongly prove that emerging markets always react more "
    "than developed markets."
)
DASHBOARD_USE_NOTE = "Use this dashboard as a research observatory, not as a trading system."
DAILY_TAB_LABELS = [
    "Overview",
    "GPR Shock Timeline",
    "Market Response",
    "Robustness",
    "Regression Evidence",
    "Downside Risk",
    "Dynamic Response",
    "Prediction Lab",
    "Country Sensitivity",
    "Monthly Benchmark",
    "Data Quality",
]
```

Add pure helpers below `monthly_provenance_rows`:

```python
def classify_evidence_strength(row: pd.Series) -> str:
    inference = str(row.get("inference", "")).lower()
    p_value = pd.to_numeric(row.get("p_value"), errors="coerce")
    if "exploratory" in inference or pd.isna(p_value):
        return "Exploratory"
    if "mixed" in inference:
        return "Mixed"
    if p_value <= 0.10:
        return "Useful signal"
    if p_value <= 0.50:
        return "Mixed"
    return "Weak"


def build_evidence_map(evidence_summary: pd.DataFrame) -> pd.DataFrame:
    evidence_map = evidence_summary.copy()
    evidence_map["Evidence strength"] = evidence_map.apply(classify_evidence_strength, axis=1)
    evidence_map["Direction"] = evidence_map["estimate"].map(lambda value: "Positive" if value > 0 else "Negative" if value < 0 else "Near zero")
    evidence_map["Estimate"] = evidence_map.apply(lambda row: f"{row['estimate']:.3g} {row['unit']}", axis=1)
    evidence_map["p-value / metric"] = evidence_map["p_value"].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    return evidence_map.rename(
        columns={
            "method": "Method",
            "focus": "Question answered",
            "plain_english": "Plain-English takeaway",
        }
    )[
        [
            "Method",
            "Question answered",
            "Direction",
            "Estimate",
            "p-value / metric",
            "Evidence strength",
            "Plain-English takeaway",
        ]
    ]
```

Add rendering helpers:

```python
def render_intro() -> None:
    st.markdown(DASHBOARD_INTRO)
    st.markdown(f"**Main takeaway:** {DASHBOARD_MAIN_TAKEAWAY}")
    st.caption(DASHBOARD_USE_NOTE)


def render_summary_cards() -> None:
    cards = [
        ("Question", "Do emerging and developed ETF markets respond differently to GPR shocks?"),
        ("Data", "20 country ETF proxies, daily GPR data, and market controls."),
        ("Methods", "Event studies, regressions, quantile analysis, local projections, rolling betas, and drawdown-risk classification."),
        ("Bottom line", "Evidence is useful but mixed. Stronger for general risk association than for emerging-market asymmetry."),
    ]
    columns = st.columns(4)
    for column, (title, body) in zip(columns, cards, strict=True):
        with column:
            st.subheader(title)
            st.write(body)
```

Call `render_intro()` in `main()` under the title and `render_summary_cards()` at the start of `render_overview_tab`. Replace the Overview evidence table with `build_evidence_map(evidence_summary)`.

- [ ] **Step 5: Run tests to verify Task 1 passes**

Run:

```powershell
uv run --all-extras pytest tests/test_app_structure.py tests/test_dashboard_display.py -q
uv run --all-extras ruff check app.py tests/test_app_structure.py tests/test_dashboard_display.py
```

Expected: both commands exit 0.

- [ ] **Step 6: Commit Task 1**

```powershell
git add app.py tests/test_app_structure.py tests/test_dashboard_display.py
git commit -m "feat: add guided dashboard overview"
```

## Task 2: Story Tabs And Notes

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app_structure.py`

- [ ] **Step 1: Write failing tests for note coverage**

Add:

```python
def test_daily_tabs_have_how_to_read_notes():
    expected_keys = {
        "overview",
        "shocks",
        "market_response",
        "robustness",
        "regression",
        "downside_risk",
        "dynamic_response",
        "prediction_lab",
        "country_sensitivity",
        "data_quality",
    }
    assert set(app.HOW_TO_READ_NOTES) == expected_keys
    assert "Day 0" in app.HOW_TO_READ_NOTES["market_response"]
    assert "not a trading strategy" in app.HOW_TO_READ_NOTES["prediction_lab"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
uv run --all-extras pytest tests/test_app_structure.py -q
```

Expected: failure because `HOW_TO_READ_NOTES` is missing.

- [ ] **Step 3: Add notes and renderer**

Add `HOW_TO_READ_NOTES` near `DAILY_TAB_LABELS`, add:

```python
def render_how_to_read(tab_key: str) -> None:
    st.info(f"How to read this: {HOW_TO_READ_NOTES[tab_key]}")
```

Call it near the top of each daily tab renderer.

- [ ] **Step 4: Update `main()` to use `DAILY_TAB_LABELS`**

Replace the literal list passed to `st.tabs(...)` with `DAILY_TAB_LABELS`.

- [ ] **Step 5: Run focused checks and commit**

```powershell
uv run --all-extras pytest tests/test_app_structure.py -q
uv run --all-extras ruff check app.py tests/test_app_structure.py
git add app.py tests/test_app_structure.py
git commit -m "feat: add dashboard story tabs"
```

## Task 3: Shock Timeline And CSV Downloads

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app_structure.py`

- [ ] **Step 1: Write failing structure tests**

Add:

```python
def test_dashboard_download_and_timeline_helpers_are_defined():
    assert callable(app.render_csv_download)
    assert callable(app.build_gpr_shock_timeline)
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
uv run --all-extras pytest tests/test_app_structure.py -q
```

Expected: failure because helpers are missing.

- [ ] **Step 3: Add helpers**

Add:

```python
def render_csv_download(df: pd.DataFrame, label: str, filename: str) -> None:
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


def build_gpr_shock_timeline(gpr: pd.DataFrame):
    timeline = gpr.sort_values("date")
    top_shocks = gpr.sort_values("gpr_change", ascending=False).head(25)
    fig = px.line(timeline, x="date", y="gpr", title="GPR Index With Top Shock Dates")
    fig.add_scatter(
        x=top_shocks["date"],
        y=top_shocks["gpr"],
        mode="markers",
        name="Top GPR changes",
        customdata=top_shocks[["gpr_change", "event"]],
        hovertemplate="Date=%{x}<br>GPR=%{y}<br>GPR change=%{customdata[0]}<br>Event=%{customdata[1]}<extra></extra>",
    )
    return fig
```

Call `build_gpr_shock_timeline()` in `render_shocks_tab` before the table. Add `render_csv_download(...)` under major tables.

- [ ] **Step 4: Run focused checks and commit**

```powershell
uv run --all-extras pytest tests/test_app_structure.py tests/test_dashboard_display.py -q
uv run --all-extras ruff check app.py tests/test_app_structure.py tests/test_dashboard_display.py
git add app.py tests/test_app_structure.py tests/test_dashboard_display.py
git commit -m "feat: add dashboard timeline downloads"
```

## Task 4: Missing Data Message And Full Verification

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app_outputs.py`

- [ ] **Step 1: Write failing missing-data helper test**

Add to `tests/test_app_outputs.py`:

```python
def test_missing_data_message_helper_is_defined():
    assert callable(app.render_missing_data_message)
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
uv run --all-extras pytest tests/test_app_outputs.py -q
```

Expected: failure because `render_missing_data_message` is missing.

- [ ] **Step 3: Add helper and call it from `main()`**

Add:

```python
def render_missing_data_message(missing: list[Path]) -> None:
    st.error("Processed data files are missing.")
    st.write("To rebuild everything, run:")
    st.code("python scripts/build_all.py")
    with st.expander("Advanced: individual scripts"):
        from gprobs.pipeline import PIPELINE_STEPS

        st.code("\n".join(f"python scripts/{step.script_name}" for step in PIPELINE_STEPS))
    st.write("Missing files:")
    st.write([str(path) for path in missing])
```

Replace the current missing-file block in `main()` with:

```python
if missing:
    render_missing_data_message(missing)
    return
```

- [ ] **Step 4: Run full checks**

```powershell
uv run --all-extras ruff check .
uv run --all-extras pytest --cov=gprobs --cov=app --cov-report=term-missing -q
```

Expected: both commands exit 0.

- [ ] **Step 5: Run a Streamlit smoke test**

Run the dashboard:

```powershell
uv run --all-extras streamlit run app.py --server.headless true --server.port 8508
```

Open `http://127.0.0.1:8508/` and confirm the app returns HTTP 200. Stop the server after the check.

- [ ] **Step 6: Commit Task 4**

```powershell
git add app.py tests/test_app_outputs.py
git commit -m "feat: simplify dashboard missing data guidance"
```
