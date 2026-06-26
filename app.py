import pandas as pd
import plotly.express as px
import streamlit as st

from gprobs.config import DRAWDOWN_HORIZON_DAYS, DRAWDOWN_THRESHOLD
from gprobs.dashboard.charts import (
    build_feature_importance_chart,
    build_gpr_shock_timeline,
    build_prediction_calibration_chart,
    build_prediction_lift_chart,
)
from gprobs.dashboard.components import (
    DASHBOARD_INTRO,
    DASHBOARD_MAIN_TAKEAWAY,
    DASHBOARD_USE_NOTE,
    HOW_TO_READ_NOTES,
    render_csv_download,
    render_how_to_read,
    render_intro,
    render_missing_data_message,
    render_summary_cards,
)
from gprobs.dashboard.evidence import build_evidence_map
from gprobs.dashboard.formatting import classify_evidence_strength
from gprobs.dashboard.metrics import build_country_coverage, select_key_regression_terms
from gprobs.dashboard.monthly import (
    MONTHLY_CLUSTER_NOTICE,
    MONTHLY_MODE_PRIORITY_NOTICE,
    MONTHLY_MODES,
    MONTHLY_OUTPUT_SPECS,
    MONTHLY_REAL_NOTICE,
    MONTHLY_SAMPLE_NOTICE,
    MonthlyModeConfig,
    MonthlyOutputBundle,
    load_monthly_outputs,
    monthly_provenance_rows,
    render_monthly_benchmark_tab,
)
from gprobs.dashboard.outputs import (
    OUTPUT_SPECS,
    PROJECT_ROOT,
    REQUIRED_FILES,
    OutputSpec,
    load_outputs,
    missing_files,
    validate_output_schema,
)
from gprobs.dashboard.prediction import (
    FEATURE_IMPORTANCE_CAPTION,
    ML_VALIDATION_CAPTION,
    ML_VALIDATION_HEADING,
    best_model_metric_labels,
    build_model_summary,
)

__all__ = [
    "DASHBOARD_INTRO",
    "DASHBOARD_MAIN_TAKEAWAY",
    "DASHBOARD_TAB_LABELS",
    "DASHBOARD_USE_NOTE",
    "DAILY_TAB_LABELS",
    "FEATURE_IMPORTANCE_CAPTION",
    "HOW_TO_READ_NOTES",
    "ML_VALIDATION_CAPTION",
    "ML_VALIDATION_HEADING",
    "MONTHLY_CLUSTER_NOTICE",
    "MONTHLY_MODE_PRIORITY_NOTICE",
    "MONTHLY_MODES",
    "MONTHLY_OUTPUT_SPECS",
    "MONTHLY_REAL_NOTICE",
    "MONTHLY_SAMPLE_NOTICE",
    "OUTPUT_SPECS",
    "PROJECT_ROOT",
    "REQUIRED_FILES",
    "MonthlyModeConfig",
    "MonthlyOutputBundle",
    "OutputSpec",
    "best_model_metric_labels",
    "build_evidence_map",
    "build_model_summary",
    "classify_evidence_strength",
    "load_outputs",
    "load_monthly_outputs",
    "monthly_provenance_rows",
    "render_csv_download",
    "render_how_to_read",
    "render_intro",
    "render_missing_data_message",
    "render_monthly_benchmark_tab",
    "render_summary_cards",
    "missing_files",
    "validate_output_schema",
]

DASHBOARD_TAB_LABELS = [
    "Overview",
    "GPR Shock Timeline",
    "Market Response",
    "Regression Evidence",
    "Downside Risk",
    "Dynamic Response",
    "Prediction Lab",
    "Country Sensitivity",
    "Monthly Benchmark",
    "Data Quality",
]
DAILY_TAB_LABELS = DASHBOARD_TAB_LABELS


def render_overview_tab(
    panel: pd.DataFrame,
    gpr: pd.DataFrame,
    group_returns: pd.DataFrame,
    evidence_summary: pd.DataFrame,
) -> None:
    render_how_to_read("overview")
    render_summary_cards()

    start_date = panel["date"].min().date()
    end_date = panel["date"].max().date()
    country_count = panel["country"].nunique()
    shock_count = int(gpr["gpr_change_shock"].sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Countries", country_count)
    col2.metric("Start date", str(start_date))
    col3.metric("End date", str(end_date))
    col4.metric("GPR shock days", f"{shock_count:,}")

    fig = px.line(
        gpr.loc[gpr["date"].between(panel["date"].min(), panel["date"].max())],
        x="date", y="gpr", title="Daily Geopolitical Risk",
    )
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

    st.subheader("Evidence Map")
    evidence_map = build_evidence_map(evidence_summary)
    st.dataframe(evidence_map, use_container_width=True, hide_index=True)
    render_csv_download(evidence_map, "Download Evidence Map CSV", "evidence_map.csv")
    st.caption(
        "This table collects the main outputs in one place. Treat weak "
        "p-values and exploratory ML metrics as signals to investigate, "
        "not as proof."
    )


def render_shocks_tab(gpr: pd.DataFrame) -> None:
    render_how_to_read("shocks")
    st.plotly_chart(build_gpr_shock_timeline(gpr), use_container_width=True)
    top_shocks = gpr.sort_values("gpr_change", ascending=False).head(25)
    top_shocks_table = top_shocks[["date", "gpr", "gpr_change", "gpr_act", "gpr_threat", "event"]]
    st.dataframe(top_shocks_table, use_container_width=True, hide_index=True)
    render_csv_download(top_shocks_table, "Download Top Shocks CSV", "top_gpr_shocks.csv")


def render_event_tab(
    event_study: pd.DataFrame,
    abnormal_event_study: pd.DataFrame,
) -> None:
    render_how_to_read("market_response")
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
    render_csv_download(
        abnormal_event_study,
        "Download Abnormal Event Study CSV",
        "event_study_abnormal_summary.csv",
    )

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
    render_csv_download(event_study, "Download Raw Event Study CSV", "event_study_summary.csv")


def render_robustness_tab(event_robustness: pd.DataFrame) -> None:
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
    render_csv_download(
        event_robustness,
        "Download Event Robustness CSV",
        "event_robustness_summary.csv",
    )
    st.caption(
        "This compares whether the event-study conclusion changes when the GPR "
        "shock threshold or post-shock window is changed."
    )


def render_regression_tab(
    regression: pd.DataFrame,
    controlled_regression: pd.DataFrame,
    date_fe_regression: pd.DataFrame,
    panel_sample_robustness: pd.DataFrame,
) -> None:
    render_how_to_read("regression")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Baseline")
        key_terms = select_key_regression_terms(regression)
        st.dataframe(key_terms, use_container_width=True, hide_index=True)
        render_csv_download(key_terms, "Download Baseline Terms CSV", "panel_regression_baseline_terms.csv")
    with col2:
        st.subheader("With Market Controls")
        controlled_terms = select_key_regression_terms(controlled_regression)
        st.dataframe(controlled_terms, use_container_width=True, hide_index=True)
        render_csv_download(
            controlled_terms,
            "Download Controlled Terms CSV",
            "panel_regression_controlled_terms.csv",
        )
    st.subheader("Date Fixed-Effects H1 Model")
    date_fe_terms = select_key_regression_terms(date_fe_regression)
    st.dataframe(date_fe_terms, use_container_width=True, hide_index=True)
    render_csv_download(date_fe_terms, "Download Date FE Terms CSV", "panel_regression_date_fe_terms.csv")
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
    render_csv_download(
        panel_sample_robustness,
        "Download Sample Robustness CSV",
        "panel_sample_robustness.csv",
    )
    st.caption(
        "These rows rerun the controlled model after excluding major crisis "
        "windows. Large sign or p-value changes would warn that one episode "
        "is driving the result."
    )


def render_tail_tab(quantile_regression: pd.DataFrame) -> None:
    render_how_to_read("downside_risk")
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
    render_csv_download(key_quantile_terms, "Download Quantile Terms CSV", "quantile_regression_terms.csv")
    st.caption(
        "Lower quantiles describe worse return days. A more negative coefficient "
        "at the 10th percentile than at the median suggests stronger downside "
        "association, but p-values still matter."
    )


def render_local_tab(local_projections: pd.DataFrame) -> None:
    render_how_to_read("dynamic_response")
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
    render_csv_download(local_projections, "Download Local Projections CSV", "local_projection_results.csv")


def render_ml_tab(
    drawdown_metrics: pd.DataFrame,
    drawdown_importance: pd.DataFrame,
    drawdown_threshold_metrics: pd.DataFrame,
    drawdown_calibration: pd.DataFrame,
    drawdown_lift: pd.DataFrame,
    drawdown_country_risk_summary: pd.DataFrame,
) -> None:
    render_how_to_read("prediction_lab")
    st.caption(
        "This is an out-of-sample risk-classification experiment. It asks whether current GPR and market "
        "conditions help rank short-horizon drawdown risk; it is not a trading signal."
    )

    model_summary = build_model_summary(drawdown_metrics, drawdown_lift)
    best_labels = best_model_metric_labels(model_summary)
    mean_base_rate = drawdown_metrics["base_rate"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(*best_labels["auc"])
    col2.metric(*best_labels["ap"])
    col3.metric(*best_labels["lift"])
    col4.metric("Mean event rate", f"{mean_base_rate:.1%}")

    st.subheader("Model Comparison")
    st.dataframe(model_summary, use_container_width=True, hide_index=True)
    render_csv_download(model_summary, "Download Model Comparison CSV", "drawdown_model_comparison.csv")

    st.subheader("Calibration")
    st.plotly_chart(build_prediction_calibration_chart(drawdown_calibration), use_container_width=True)
    st.dataframe(drawdown_calibration, use_container_width=True, hide_index=True)
    render_csv_download(drawdown_calibration, "Download Calibration CSV", "drawdown_model_calibration.csv")

    st.subheader("Lift")
    st.plotly_chart(build_prediction_lift_chart(drawdown_lift), use_container_width=True)
    st.dataframe(drawdown_lift, use_container_width=True, hide_index=True)
    render_csv_download(drawdown_lift, "Download Lift CSV", "drawdown_model_lift.csv")

    st.subheader("Threshold Metrics")
    st.dataframe(drawdown_threshold_metrics, use_container_width=True, hide_index=True)
    render_csv_download(
        drawdown_threshold_metrics,
        "Download Threshold Metrics CSV",
        "drawdown_model_threshold_metrics.csv",
    )

    st.subheader("Country Risk Summary")
    st.dataframe(drawdown_country_risk_summary, use_container_width=True, hide_index=True)
    render_csv_download(
        drawdown_country_risk_summary,
        "Download Country Risk Summary CSV",
        "drawdown_country_risk_summary.csv",
    )

    st.plotly_chart(build_feature_importance_chart(drawdown_importance), use_container_width=True)
    st.caption(FEATURE_IMPORTANCE_CAPTION)
    render_csv_download(drawdown_importance, "Download Feature Importance CSV", "drawdown_feature_importance.csv")

    st.subheader(ML_VALIDATION_HEADING)
    st.dataframe(drawdown_metrics, use_container_width=True, hide_index=True)
    render_csv_download(drawdown_metrics, "Download Drawdown Metrics CSV", "drawdown_model_metrics.csv")
    st.caption(
        f"This classifier predicts whether an ETF has a forward {DRAWDOWN_HORIZON_DAYS}-trading-day "
        f"cumulative log-return drawdown of at least {abs(DRAWDOWN_THRESHOLD):.0%}. "
        f"{ML_VALIDATION_CAPTION}"
    )


def render_rolling_tab(rolling_beta: pd.DataFrame) -> None:
    render_how_to_read("country_sensitivity")
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


def render_coverage_tab(panel: pd.DataFrame, large_returns: pd.DataFrame) -> None:
    render_how_to_read("data_quality")
    coverage = build_country_coverage(panel)
    st.subheader("Country Coverage")
    st.dataframe(coverage, use_container_width=True, hide_index=True)
    render_csv_download(coverage, "Download Country Coverage CSV", "country_coverage.csv")
    st.subheader("Large Daily Return Flags")
    st.dataframe(large_returns, use_container_width=True, hide_index=True)
    render_csv_download(large_returns, "Download Large Return Flags CSV", "large_return_flags.csv")


def main():
    st.set_page_config(page_title="GPR Equity Observatory", layout="wide")
    st.title("GPR Equity Observatory")
    render_intro()

    missing = missing_files()
    if missing:
        render_missing_data_message(missing)
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
    drawdown_threshold_metrics = outputs["drawdown_threshold_metrics"]
    drawdown_calibration = outputs["drawdown_calibration"]
    drawdown_lift = outputs["drawdown_lift"]
    drawdown_country_risk_summary = outputs["drawdown_country_risk_summary"]
    drawdown_importance = outputs["drawdown_importance"]
    evidence_summary = outputs["evidence_summary"]
    rolling_beta = outputs["rolling_beta"]
    large_returns = outputs["large_returns"]
    monthly_outputs = load_monthly_outputs()

    (
        tab_overview,
        tab_shocks,
        tab_event,
        tab_regression,
        tab_tail,
        tab_local,
        tab_ml,
        tab_rolling,
        tab_monthly,
        tab_coverage,
    ) = st.tabs(DASHBOARD_TAB_LABELS)

    with tab_overview:
        render_overview_tab(panel, gpr, group_returns, evidence_summary)

    with tab_shocks:
        render_shocks_tab(gpr)

    with tab_event:
        render_event_tab(event_study, abnormal_event_study)
        st.divider()
        render_robustness_tab(event_robustness)

    with tab_regression:
        render_regression_tab(
            regression,
            controlled_regression,
            date_fe_regression,
            panel_sample_robustness,
        )

    with tab_tail:
        render_tail_tab(quantile_regression)

    with tab_local:
        render_local_tab(local_projections)

    with tab_ml:
        render_ml_tab(
            drawdown_metrics,
            drawdown_importance,
            drawdown_threshold_metrics,
            drawdown_calibration,
            drawdown_lift,
            drawdown_country_risk_summary,
        )

    with tab_rolling:
        render_rolling_tab(rolling_beta)

    with tab_monthly:
        render_monthly_benchmark_tab(monthly_outputs)

    with tab_coverage:
        render_coverage_tab(panel, large_returns)


if __name__ == "__main__":
    main()
