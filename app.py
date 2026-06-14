from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.dashboard.metrics import build_country_coverage, select_key_regression_terms


DATA_DIR = PROJECT_ROOT / "data" / "processed"

REQUIRED_FILES = {
    "analysis_panel": DATA_DIR / "analysis_panel.csv",
    "gpr": DATA_DIR / "gpr_daily.csv",
    "group_returns": DATA_DIR / "group_return_summary.csv",
    "event_study": DATA_DIR / "event_study_summary.csv",
    "regression": DATA_DIR / "panel_regression_baseline.csv",
}


@st.cache_data
def load_outputs():
    return {
        "analysis_panel": pd.read_csv(
            REQUIRED_FILES["analysis_panel"],
            parse_dates=["date"],
            low_memory=False,
        ),
        "gpr": pd.read_csv(REQUIRED_FILES["gpr"], parse_dates=["date"]),
        "group_returns": pd.read_csv(REQUIRED_FILES["group_returns"], parse_dates=["date"]),
        "event_study": pd.read_csv(REQUIRED_FILES["event_study"]),
        "regression": pd.read_csv(REQUIRED_FILES["regression"]),
    }


def missing_files():
    return [path for path in REQUIRED_FILES.values() if not path.exists()]


def main():
    st.set_page_config(page_title="GPR Equity Observatory", layout="wide")
    st.title("GPR Equity Observatory")

    missing = missing_files()
    if missing:
        st.error("Processed data files are missing.")
        st.code(
            "\n".join(
                [
                    "python scripts/build_returns_panel.py",
                    "python scripts/build_gpr_dataset.py",
                    "python scripts/build_analysis_panel.py",
                    "python scripts/run_event_study.py",
                    "python scripts/run_panel_regression.py",
                ]
            )
        )
        st.write("Missing files:")
        st.write([str(path) for path in missing])
        return

    outputs = load_outputs()
    panel = outputs["analysis_panel"]
    gpr = outputs["gpr"]
    group_returns = outputs["group_returns"]
    event_study = outputs["event_study"]
    regression = outputs["regression"]

    tab_overview, tab_shocks, tab_event, tab_regression, tab_coverage = st.tabs(
        ["Overview", "GPR Shocks", "Event Study", "Panel Regression", "Data Coverage"]
    )

    with tab_overview:
        start_date = panel["date"].min().date()
        end_date = panel["date"].max().date()
        country_count = panel["country"].nunique()
        shock_count = int(gpr["gpr_shock"].sum())

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Countries", country_count)
        col2.metric("Start date", str(start_date))
        col3.metric("End date", str(end_date))
        col4.metric("GPR shock days", f"{shock_count:,}")

        gpr_for_sample = gpr.loc[gpr["date"].between(panel["date"].min(), panel["date"].max())]
        fig = px.line(gpr_for_sample, x="date", y="gpr", title="Daily Geopolitical Risk")
        st.plotly_chart(fig, use_container_width=True)

        group_chart = group_returns.copy()
        group_chart["cumulative_average_return"] = group_chart.groupby("market_group")[
            "average_return"
        ].cumsum()
        fig = px.line(
            group_chart,
            x="date",
            y="cumulative_average_return",
            color="market_group",
            title="Cumulative Average ETF Log Returns",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_shocks:
        top_shocks = gpr.sort_values("gpr", ascending=False).head(25)
        st.dataframe(
            top_shocks[["date", "gpr", "gpr_act", "gpr_threat", "event"]],
            use_container_width=True,
            hide_index=True,
        )

    with tab_event:
        fig = px.line(
            event_study,
            x="relative_day",
            y="cumulative_average_return",
            color="market_group",
            markers=True,
            title="Average Cumulative ETF Returns Around GPR Shock Dates",
        )
        fig.add_vline(x=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(event_study, use_container_width=True, hide_index=True)

    with tab_regression:
        key_terms = select_key_regression_terms(regression)
        st.dataframe(key_terms, use_container_width=True, hide_index=True)
        st.caption(
            "The interaction term is the extra association between standardized GPR "
            "and returns for emerging market ETFs relative to developed market ETFs."
        )

    with tab_coverage:
        coverage = build_country_coverage(panel)
        st.dataframe(coverage, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
