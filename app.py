from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from gprobs.config import DRAWDOWN_HORIZON_DAYS, DRAWDOWN_THRESHOLD
from gprobs.dashboard.metrics import build_country_coverage, select_key_regression_terms

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"


@dataclass(frozen=True)
class OutputSpec:
    path: Path
    date_columns: tuple[str, ...] = ()
    low_memory: bool | None = None


OUTPUT_SPECS = {
    "analysis_panel": OutputSpec(DATA_DIR / "analysis_panel.csv", date_columns=("date",), low_memory=False),
    "gpr": OutputSpec(DATA_DIR / "gpr_daily.csv", date_columns=("date",)),
    "group_returns": OutputSpec(DATA_DIR / "group_return_summary.csv", date_columns=("date",)),
    "event_study": OutputSpec(DATA_DIR / "event_study_summary.csv"),
    "abnormal_event_study": OutputSpec(DATA_DIR / "event_study_abnormal_summary.csv"),
    "event_robustness": OutputSpec(DATA_DIR / "event_robustness_summary.csv"),
    "regression": OutputSpec(DATA_DIR / "panel_regression_baseline.csv"),
    "controlled_regression": OutputSpec(DATA_DIR / "panel_regression_controlled.csv"),
    "date_fe_regression": OutputSpec(DATA_DIR / "panel_regression_two_way_fe.csv"),
    "panel_sample_robustness": OutputSpec(DATA_DIR / "panel_sample_robustness.csv"),
    "quantile_regression": OutputSpec(DATA_DIR / "quantile_regression_results.csv"),
    "local_projections": OutputSpec(DATA_DIR / "local_projection_results.csv"),
    "drawdown_metrics": OutputSpec(
        DATA_DIR / "drawdown_model_metrics.csv",
        date_columns=("train_start", "train_end", "test_start", "test_end"),
    ),
    "drawdown_importance": OutputSpec(DATA_DIR / "drawdown_feature_importance.csv"),
    "evidence_summary": OutputSpec(DATA_DIR / "evidence_summary.csv"),
    "rolling_beta": OutputSpec(DATA_DIR / "rolling_gpr_beta.csv", date_columns=("date",)),
    "large_returns": OutputSpec(DATA_DIR / "large_return_flags.csv", date_columns=("date",)),
}

REQUIRED_FILES = {name: spec.path for name, spec in OUTPUT_SPECS.items()}


@st.cache_data
def load_outputs():
    outputs = {}
    for name, spec in OUTPUT_SPECS.items():
        read_options = {}
        if spec.date_columns:
            read_options["parse_dates"] = list(spec.date_columns)
        if spec.low_memory is not None:
            read_options["low_memory"] = spec.low_memory
        outputs[name] = pd.read_csv(spec.path, **read_options)
    return outputs


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
                    "python scripts/run_event_robustness.py",
                    "python scripts/run_panel_regression.py",
                    "python scripts/run_panel_sample_robustness.py",
                    "python scripts/run_quantile_regression.py",
                    "python scripts/run_local_projections.py",
                    "python scripts/run_drawdown_model.py",
                    "python scripts/run_evidence_summary.py",
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
    event_robustness = outputs["event_robustness"]
    regression = outputs["regression"]
    controlled_regression = outputs["controlled_regression"]
    date_fe_regression = outputs["date_fe_regression"]
    panel_sample_robustness = outputs["panel_sample_robustness"]
    quantile_regression = outputs["quantile_regression"]
    local_projections = outputs["local_projections"]
    drawdown_metrics = outputs["drawdown_metrics"]
    drawdown_importance = outputs["drawdown_importance"]
    evidence_summary = outputs["evidence_summary"]
    rolling_beta = outputs["rolling_beta"]
    large_returns = outputs["large_returns"]

    (
        tab_overview,
        tab_shocks,
        tab_event,
        tab_robustness,
        tab_regression,
        tab_tail,
        tab_local,
        tab_ml,
        tab_rolling,
        tab_coverage,
    ) = st.tabs(
        [
            "Overview",
            "GPR Shocks",
            "Event Study",
            "Robustness",
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
        shock_count = int(gpr["gpr_change_shock"].sum())

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

        st.subheader("Evidence Summary")
        st.dataframe(evidence_summary, use_container_width=True, hide_index=True)
        st.caption(
            "This table collects the main outputs in one place. Treat weak "
            "p-values and exploratory ML metrics as signals to investigate, "
            "not as proof."
        )

    with tab_shocks:
        top_shocks = gpr.sort_values("gpr_change", ascending=False).head(25)
        st.dataframe(
            top_shocks[["date", "gpr", "gpr_change", "gpr_act", "gpr_threat", "event"]],
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

    with tab_robustness:
        robustness_chart = event_robustness.copy()
        robustness_chart["shock_quantile"] = robustness_chart["shock_quantile"].map(
            lambda value: f"{value:.0%}"
        )
        fig = px.bar(
            robustness_chart,
            x="window",
            y="cumulative_average_abnormal_return",
            color="market_group",
            facet_col="shock_quantile",
            barmode="group",
            title="Event-Study Robustness: End-of-Window Abnormal Return",
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(event_robustness, use_container_width=True, hide_index=True)
        st.caption(
            "This compares whether the event-study conclusion changes when the GPR "
            "shock threshold or post-shock window is changed."
        )

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
        st.subheader("Date Fixed-Effects H1 Model")
        date_fe_terms = select_key_regression_terms(date_fe_regression)
        st.dataframe(date_fe_terms, use_container_width=True, hide_index=True)
        st.caption(
            "The interaction term is the extra association between a standardized "
            "daily GPR jump and returns for emerging market ETFs relative to developed "
            "market ETFs. The date fixed-effects model absorbs common global shocks, "
            "so its interaction is the clean H1 estimand."
        )
        st.subheader("Sample Robustness")
        st.dataframe(
            panel_sample_robustness,
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "These rows rerun the controlled model after excluding major crisis "
            "windows. Large sign or p-value changes would warn that one episode "
            "is driving the result."
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
            title="Local Projection Abnormal Return Response to GPR Shock",
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
        headline_metrics = drawdown_metrics
        if "model_name" in drawdown_metrics.columns:
            headline_metrics = drawdown_metrics.loc[
                drawdown_metrics["model_name"] == "full_features"
            ]
        mean_auc = headline_metrics["roc_auc"].mean()
        mean_ap = headline_metrics["average_precision"].mean()
        mean_base_rate = headline_metrics["base_rate"].mean()

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
            f"This classifier predicts whether an ETF has a forward {DRAWDOWN_HORIZON_DAYS}-trading-day "
            f"cumulative log-return drawdown of at least {abs(DRAWDOWN_THRESHOLD):.0%}. Splits are chronological, "
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
