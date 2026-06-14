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
    "abnormal_event_study": DATA_DIR / "event_study_abnormal_summary.csv",
    "regression": DATA_DIR / "panel_regression_baseline.csv",
    "controlled_regression": DATA_DIR / "panel_regression_controlled.csv",
    "quantile_regression": DATA_DIR / "quantile_regression_results.csv",
    "local_projections": DATA_DIR / "local_projection_results.csv",
    "drawdown_metrics": DATA_DIR / "drawdown_model_metrics.csv",
    "drawdown_importance": DATA_DIR / "drawdown_feature_importance.csv",
    "rolling_beta": DATA_DIR / "rolling_gpr_beta.csv",
    "large_returns": DATA_DIR / "large_return_flags.csv",
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
        "abnormal_event_study": pd.read_csv(REQUIRED_FILES["abnormal_event_study"]),
        "regression": pd.read_csv(REQUIRED_FILES["regression"]),
        "controlled_regression": pd.read_csv(REQUIRED_FILES["controlled_regression"]),
        "quantile_regression": pd.read_csv(REQUIRED_FILES["quantile_regression"]),
        "local_projections": pd.read_csv(REQUIRED_FILES["local_projections"]),
        "drawdown_metrics": pd.read_csv(
            REQUIRED_FILES["drawdown_metrics"],
            parse_dates=["train_start", "train_end", "test_start", "test_end"],
        ),
        "drawdown_importance": pd.read_csv(REQUIRED_FILES["drawdown_importance"]),
        "rolling_beta": pd.read_csv(REQUIRED_FILES["rolling_beta"], parse_dates=["date"]),
        "large_returns": pd.read_csv(REQUIRED_FILES["large_returns"], parse_dates=["date"]),
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
                    "python scripts/build_market_controls.py",
                    "python scripts/build_analysis_panel.py",
                    "python scripts/run_data_diagnostics.py",
                    "python scripts/run_event_study.py",
                    "python scripts/run_panel_regression.py",
                    "python scripts/run_quantile_regression.py",
                    "python scripts/run_local_projections.py",
                    "python scripts/run_drawdown_model.py",
                    "python scripts/run_rolling_sensitivity.py",
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
    abnormal_event_study = outputs["abnormal_event_study"]
    regression = outputs["regression"]
    controlled_regression = outputs["controlled_regression"]
    quantile_regression = outputs["quantile_regression"]
    local_projections = outputs["local_projections"]
    drawdown_metrics = outputs["drawdown_metrics"]
    drawdown_importance = outputs["drawdown_importance"]
    rolling_beta = outputs["rolling_beta"]
    large_returns = outputs["large_returns"]

    tab_overview, tab_shocks, tab_event, tab_regression, tab_tail, tab_local, tab_ml, tab_rolling, tab_coverage = st.tabs(
        [
            "Overview",
            "GPR Shocks",
            "Event Study",
            "Panel Regression",
            "Tail Risk",
            "Local Projections",
            "ML Drawdown",
            "Rolling Beta",
            "Data Coverage",
        ]
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
            abnormal_event_study,
            x="relative_day",
            y="cumulative_average_abnormal_return",
            color="market_group",
            markers=True,
            title="Average Cumulative Abnormal Returns Around GPR Shock Dates",
        )
        fig.add_vline(x=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(abnormal_event_study, use_container_width=True, hide_index=True)

        fig = px.line(
            event_study,
            x="relative_day",
            y="cumulative_average_return",
            color="market_group",
            markers=True,
            title="Raw Average Cumulative ETF Returns Around GPR Shock Dates",
        )
        fig.add_vline(x=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(event_study, use_container_width=True, hide_index=True)

    with tab_regression:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Baseline")
            key_terms = select_key_regression_terms(regression)
            st.dataframe(key_terms, use_container_width=True, hide_index=True)
        with col2:
            st.subheader("With Market Controls")
            controlled_terms = select_key_regression_terms(controlled_regression)
            st.dataframe(controlled_terms, use_container_width=True, hide_index=True)
        st.caption(
            "The interaction term is the extra association between standardized GPR "
            "and returns for emerging market ETFs relative to developed market ETFs. "
            "The controlled model also includes global equity, VIX, oil, dollar, "
            "and US 10-year yield controls."
        )

    with tab_tail:
        key_quantile_terms = select_key_regression_terms(quantile_regression)
        fig = px.line(
            key_quantile_terms,
            x="quantile",
            y="estimate",
            color="term",
            markers=True,
            title="GPR Coefficients Across Return Quantiles",
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(key_quantile_terms, use_container_width=True, hide_index=True)
        st.caption(
            "Lower quantiles describe worse return days. A more negative coefficient "
            "at the 10th percentile than at the median suggests stronger downside "
            "association, but p-values still matter."
        )

    with tab_local:
        fig = px.line(
            local_projections,
            x="horizon",
            y="estimate",
            color="market_group",
            markers=True,
            title="Local Projection Response to GPR Shock",
        )
        for group, group_data in local_projections.groupby("market_group"):
            fig.add_scatter(
                x=group_data["horizon"],
                y=group_data["ci_low"],
                mode="lines",
                line={"width": 0},
                showlegend=False,
                hoverinfo="skip",
            )
            fig.add_scatter(
                x=group_data["horizon"],
                y=group_data["ci_high"],
                mode="lines",
                fill="tonexty",
                line={"width": 0},
                name=f"{group} 95% CI",
                hoverinfo="skip",
            )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(local_projections, use_container_width=True, hide_index=True)

    with tab_ml:
        mean_auc = drawdown_metrics["roc_auc"].mean()
        mean_ap = drawdown_metrics["average_precision"].mean()
        mean_base_rate = drawdown_metrics["base_rate"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Mean ROC AUC", f"{mean_auc:.3f}")
        col2.metric("Mean average precision", f"{mean_ap:.3f}")
        col3.metric("Mean event rate", f"{mean_base_rate:.1%}")

        fig = px.bar(
            drawdown_importance,
            x="abs_coefficient",
            y="feature",
            orientation="h",
            title="Drawdown Model Feature Importance",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Chronological Validation")
        st.dataframe(drawdown_metrics, use_container_width=True, hide_index=True)
        st.caption(
            "This classifier predicts whether an ETF has a forward 20-trading-day "
            "cumulative log-return drawdown of at least 5%. Splits are chronological, "
            "so the model is always tested on later dates than it trains on."
        )

    with tab_rolling:
        countries = sorted(rolling_beta["country"].dropna().unique())
        selected_country = st.selectbox("Country", countries)
        country_beta = rolling_beta.loc[
            rolling_beta["country"] == selected_country
        ].dropna(subset=["rolling_gpr_beta"])

        fig = px.line(
            country_beta,
            x="date",
            y="rolling_gpr_beta",
            title=f"Rolling GPR Sensitivity: {selected_country}",
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)

    with tab_coverage:
        coverage = build_country_coverage(panel)
        st.subheader("Country Coverage")
        st.dataframe(coverage, use_container_width=True, hide_index=True)
        st.subheader("Large Daily Return Flags")
        st.dataframe(large_returns, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
