"""
Developer cockpit for GPR Equity Observatory.

This local page is for watching the project run.

It shows:
- output file status
- buttons to run steps
- live logs
- previews of generated outputs
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"


RUN_CONTROLS = {
    "gpr": ("Build GPR data", [sys.executable, "scripts/build_gpr_dataset.py"]),
    "daily": ("Run full daily pipeline", [sys.executable, "scripts/run_task.py", "build-daily"]),
    "export": (
        "Export public app data",
        [sys.executable, "scripts/run_task.py", "export-frontend"],
    ),
}


IMPORTANT_OUTPUTS = [
    "gpr_daily.csv",
    "analysis_panel.csv",
    "group_return_summary.csv",
    "event_study_abnormal_summary.csv",
    "panel_regression_controlled.csv",
    "panel_regression_date_fe.csv",
    "quantile_regression_results.csv",
    "local_projection_results.csv",
    "drawdown_model_metrics.csv",
    "drawdown_feature_importance.csv",
    "rolling_gpr_beta.csv",
    "large_return_flags.csv",
    "evidence_summary.csv",
]


def file_status(filename: str) -> dict:
    """Return a readable status row for one output file."""
    path = DATA / filename

    if not path.exists():
        return {
            "File": filename,
            "Exists?": "No",
            "Rows": "",
            "Last changed": "",
        }

    try:
        rows = len(pd.read_csv(path))
    except Exception:
        rows = "Could not read"

    last_changed = datetime.fromtimestamp(path.stat().st_mtime).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return {
        "File": filename,
        "Exists?": "Yes",
        "Rows": rows,
        "Last changed": last_changed,
    }


def show_output_status() -> None:
    """Show all important generated output files."""
    st.subheader("Output files")
    rows = [file_status(filename) for filename in IMPORTANT_OUTPUTS]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def run_command(label: str, command: list[str]) -> None:
    """Run one project command and stream its logs to the page."""
    st.write(f"Running: {label}")

    log_box = st.empty()
    logs: list[str] = []

    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    if process.stdout is not None:
        for line in process.stdout:
            logs.append(line.rstrip())
            log_box.code("\n".join(logs[-100:]))

    process.wait()

    if process.returncode != 0:
        raise RuntimeError(f"{label} failed with exit code {process.returncode}.")


def preview_outputs() -> None:
    """Preview a few outputs so the user sees what changed."""
    st.subheader("Preview latest outputs")

    gpr_path = DATA / "gpr_daily.csv"
    if gpr_path.exists():
        gpr = pd.read_csv(gpr_path, parse_dates=["date"])
        fig = px.line(gpr, x="date", y="gpr", title="Daily GPR")
        st.plotly_chart(fig, use_container_width=True)

        if "gpr_change" in gpr.columns:
            top_shocks = gpr.sort_values("gpr_change", ascending=False).head(10)
            st.write("Top GPR shocks")
            st.dataframe(top_shocks, use_container_width=True, hide_index=True)
    else:
        st.info("No GPR file yet.")

    evidence_path = DATA / "evidence_summary.csv"
    if evidence_path.exists():
        st.write("Evidence summary")
        evidence = pd.read_csv(evidence_path)
        st.dataframe(evidence, use_container_width=True, hide_index=True)
    else:
        st.info("No evidence summary yet.")


def main() -> None:
    st.set_page_config(page_title="GPR Dev Cockpit", layout="wide")

    st.title("GPR Dev Cockpit")
    st.write(
        "Use this page to run the project and watch files change. "
        "This is the beginner-friendly local control room; the public app still lives in `frontend/`."
    )

    show_output_status()

    st.divider()
    st.subheader("Run controls")

    col1, col2, col3, col4 = st.columns(4)
    run_gpr = col1.button("Run only GPR step")
    run_all = col2.button("Run full daily pipeline")
    export_frontend = col3.button("Export public app data")
    refresh = col4.button("Refresh file status")

    if refresh:
        st.rerun()

    if run_gpr:
        with st.status("Running GPR step...", expanded=True) as status:
            try:
                run_command(*RUN_CONTROLS["gpr"])
                status.update(label="GPR step complete", state="complete")
            except Exception as error:
                st.error(str(error))
                status.update(label="GPR step failed", state="error")

        show_output_status()
        preview_outputs()

    if run_all:
        with st.status("Running full daily pipeline...", expanded=True) as status:
            try:
                run_command(*RUN_CONTROLS["daily"])
                status.update(label="Full pipeline complete", state="complete")
            except Exception as error:
                st.error(str(error))
                status.update(label="Pipeline failed", state="error")

        show_output_status()
        preview_outputs()

    if export_frontend:
        with st.status("Exporting public app data...", expanded=True) as status:
            try:
                run_command(*RUN_CONTROLS["export"])
                status.update(label="Frontend export complete", state="complete")
            except Exception as error:
                st.error(str(error))
                status.update(label="Frontend export failed", state="error")

        show_output_status()
        preview_outputs()

    st.divider()
    preview_outputs()


if __name__ == "__main__":
    main()
