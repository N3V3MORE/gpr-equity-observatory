import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from gprobs.config import DRAWDOWN_HORIZON_DAYS, DRAWDOWN_THRESHOLD
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
from gprobs.dashboard.formatting import (
    classify_evidence_strength,
    format_evidence_direction,
    format_evidence_estimate,
    format_p_value,
)
from gprobs.dashboard.metrics import build_country_coverage, select_key_regression_terms
from gprobs.dashboard.outputs import (
    OUTPUT_SPECS,
    PROJECT_ROOT,
    REQUIRED_FILES,
    OutputSpec,
    load_outputs,
    missing_files,
    validate_output_schema,
)

__all__ = [
    "DASHBOARD_INTRO",
    "DASHBOARD_MAIN_TAKEAWAY",
    "DASHBOARD_USE_NOTE",
    "HOW_TO_READ_NOTES",
    "OUTPUT_SPECS",
    "REQUIRED_FILES",
    "OutputSpec",
    "load_outputs",
    "render_csv_download",
    "render_how_to_read",
    "render_intro",
    "render_missing_data_message",
    "render_summary_cards",
    "missing_files",
    "validate_output_schema",
]

ML_VALIDATION_HEADING = "Purged Chronological Validation"
ML_VALIDATION_CAPTION = (
    "Splits are purged chronological, so the model trains only on earlier dates "
    "and excludes dates immediately before the test fold to reduce forward-label leakage."
)
MONTHLY_SAMPLE_NOTICE = "Sample mode is not empirical evidence. It only proves the monthly benchmark workflow runs."
MONTHLY_REAL_NOTICE = "Real monthly aggregate mode is a benchmark, not a country-panel proof."
MONTHLY_CLUSTER_NOTICE = "The two-market aggregate design cannot support country-clustered inference."
MONTHLY_MODE_PRIORITY_NOTICE = "If real monthly outputs are present, the dashboard shows real mode before sample mode."
DAILY_TAB_LABELS = [
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


@dataclass(frozen=True)
class MonthlyModeConfig:
    root: Path = PROJECT_ROOT
    mode_label: str = "Sample"
    dataset_mode: str = "monthly_benchmark_sample"
    panel: str = "data/processed/monthly_benchmark/sample_analysis_panel.csv"
    source_manifest: str = "data/metadata/monthly_benchmark/source_manifest.json"
    analysis_manifest: str = "data/metadata/monthly_benchmark/analysis_panel_manifest.json"
    regressions: str = "reports/tables/monthly_benchmark/sample_table_02_baseline_regressions.csv"
    forecasts: str = "reports/tables/monthly_benchmark/sample_table_03_forecast_comparison.csv"

    def path(self, relative_path: str) -> Path:
        return self.root / relative_path


@dataclass(frozen=True)
class MonthlyOutputBundle:
    mode: str
    mode_label: str
    panel: pd.DataFrame
    source_manifest: dict
    analysis_manifest: dict
    source_names: list[str]
    regressions: pd.DataFrame | None = None
    forecasts: pd.DataFrame | None = None


MONTHLY_MODES = {
    "real": MonthlyModeConfig(
        mode_label="Real",
        dataset_mode="monthly_benchmark_real",
        panel="data/processed/monthly_benchmark/analysis_panel.csv",
        source_manifest="data/metadata/monthly_benchmark/source_manifest_real.json",
        analysis_manifest="data/metadata/monthly_benchmark/analysis_panel_manifest_real.json",
        regressions="reports/tables/monthly_benchmark/table_02_baseline_regressions_real.csv",
        forecasts="reports/tables/monthly_benchmark/table_03_forecast_comparison_real.csv",
    ),
    "sample": MonthlyModeConfig(),
}

MONTHLY_OUTPUT_SPECS = {
    "monthly_panel": OutputSpec(
        Path("monthly_benchmark_analysis_panel.csv"),
        date_columns=("date_month",),
        required_columns=(
            "date_month",
            "market_id",
            "market_class",
            "excess_return",
            "ret_fwd_1m",
            "gpr_global",
            "gpr_change_z",
            "spread_em_dev",
            "gdelt_risk_raw",
            "gdelt_risk_z",
        ),
    ),
    "monthly_regressions": OutputSpec(
        Path("monthly_benchmark_regressions.csv"),
        required_columns=(
            "horizon",
            "term",
            "estimate",
            "std_error",
            "t_value",
            "p_value",
            "se_type",
            "nobs",
            "adjusted_r2",
        ),
    ),
    "monthly_forecasts": OutputSpec(
        Path("monthly_benchmark_forecasts.csv"),
        required_columns=(
            "model",
            "rmse",
            "mae",
            "oos_r2",
            "n_forecasts",
            "first_forecast_date",
            "last_forecast_date",
            "forecast_window_aligned",
        ),
    ),
}


def load_monthly_outputs() -> MonthlyOutputBundle | None:
    for mode, config in MONTHLY_MODES.items():
        bundle = _load_monthly_output_mode(mode, config)
        if bundle is not None:
            return bundle
    return None


def _load_monthly_output_mode(mode: str, config: MonthlyModeConfig) -> MonthlyOutputBundle | None:
    panel_path = config.path(config.panel)
    source_manifest_path = config.path(config.source_manifest)
    analysis_manifest_path = config.path(config.analysis_manifest)
    if not all(path.exists() for path in [panel_path, source_manifest_path, analysis_manifest_path]):
        return None

    panel = pd.read_csv(panel_path, parse_dates=["date_month"])
    validate_output_schema(panel, MONTHLY_OUTPUT_SPECS["monthly_panel"])
    source_manifest = _read_json(source_manifest_path)
    analysis_manifest = _read_json(analysis_manifest_path)
    source_names = [
        source.get("source_name", "Unknown source")
        for source in source_manifest.get("sources", [])
    ]

    regressions = _read_optional_monthly_csv(
        config.path(config.regressions),
        MONTHLY_OUTPUT_SPECS["monthly_regressions"],
    )
    forecasts = _read_optional_monthly_csv(
        config.path(config.forecasts),
        MONTHLY_OUTPUT_SPECS["monthly_forecasts"],
    )
    return MonthlyOutputBundle(
        mode=mode,
        mode_label=config.mode_label,
        panel=panel,
        source_manifest=source_manifest,
        analysis_manifest=analysis_manifest,
        source_names=source_names,
        regressions=regressions,
        forecasts=forecasts,
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_monthly_csv(path: Path, spec: OutputSpec) -> pd.DataFrame | None:
    if not path.exists():
        return None
    output = pd.read_csv(path)
    validate_output_schema(output, spec)
    return output


def monthly_provenance_rows(bundle: MonthlyOutputBundle) -> pd.DataFrame:
    manifest = bundle.analysis_manifest
    rows = [
        ("mode", bundle.mode_label),
        ("dataset_mode", str(manifest.get("dataset_mode") or manifest.get("dataset") or "")),
        ("source_count", str(len(bundle.source_names))),
        ("row_count", str(manifest.get("row_count", ""))),
        ("sample_start", str(manifest.get("sample_start") or manifest.get("start_date") or "")),
        ("sample_end", str(manifest.get("sample_end") or manifest.get("end_date") or "")),
        ("used_placeholder_gdelt", str(manifest.get("used_placeholder_gdelt", ""))),
        ("used_placeholder_macro", str(manifest.get("used_placeholder_macro", ""))),
    ]
    return pd.DataFrame(rows, columns=["field", "value"])


def build_evidence_map(evidence_summary: pd.DataFrame) -> pd.DataFrame:
    evidence_map = evidence_summary.copy()
    evidence_map["Evidence strength"] = evidence_map.apply(classify_evidence_strength, axis=1)
    evidence_map["Direction"] = evidence_map["estimate"].map(format_evidence_direction)
    evidence_map["Estimate"] = evidence_map.apply(
        lambda row: format_evidence_estimate(row["estimate"], row["unit"]),
        axis=1,
    )
    evidence_map["p-value / metric"] = evidence_map["p_value"].map(format_p_value)
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
        hovertemplate=(
            "Date=%{x}<br>GPR=%{y}<br>GPR change=%{customdata[0]}"
            "<br>Event=%{customdata[1]}<extra></extra>"
        ),
    )
    return fig


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
) -> None:
    render_how_to_read("prediction_lab")
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


def render_monthly_benchmark_tab(bundle: MonthlyOutputBundle | None) -> None:
    if bundle is None:
        st.info("Monthly benchmark outputs are not available yet.")
        st.code(
            "\n".join(
                [
                    "python scripts/run_task.py monthly-sample --min-train-months 24",
                    "python scripts/run_task.py build-monthly-real",
                    "python scripts/run_task.py validate-monthly-real",
                ]
            )
        )
        st.caption(f"{MONTHLY_SAMPLE_NOTICE} {MONTHLY_REAL_NOTICE} {MONTHLY_CLUSTER_NOTICE}")
        return

    panel = bundle.panel.copy()
    panel["date_month"] = pd.to_datetime(panel["date_month"])
    month_level = panel.drop_duplicates("date_month").sort_values("date_month")
    start_date = panel["date_month"].min().date()
    end_date = panel["date_month"].max().date()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mode", bundle.mode_label)
    col2.metric("Start month", str(start_date))
    col3.metric("End month", str(end_date))
    col4.metric("Sources", len(bundle.source_names))

    if bundle.mode == "sample":
        st.warning(MONTHLY_SAMPLE_NOTICE)
    else:
        st.info(MONTHLY_REAL_NOTICE)
    st.caption(MONTHLY_CLUSTER_NOTICE)
    st.caption(MONTHLY_MODE_PRIORITY_NOTICE)

    st.subheader("Source and Provenance Status")
    provenance = monthly_provenance_rows(bundle)
    st.dataframe(provenance, use_container_width=True, hide_index=True)
    render_csv_download(provenance, "Download Monthly Provenance CSV", "monthly_provenance.csv")
    if bundle.source_names:
        sources = pd.DataFrame({"source_name": bundle.source_names})
        st.dataframe(sources, use_container_width=True, hide_index=True)
        render_csv_download(sources, "Download Monthly Sources CSV", "monthly_sources.csv")

    gpr_fig = px.line(
        month_level,
        x="date_month",
        y="gpr_change_z",
        title="Monthly GPR Shock Measure",
    )
    gpr_fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(gpr_fig, use_container_width=True)

    spread_fig = px.line(
        month_level,
        x="date_month",
        y="spread_em_dev",
        title="Emerging Minus Developed Aggregate Return Spread",
    )
    spread_fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(spread_fig, use_container_width=True)

    st.subheader("Benchmark Regression Table")
    if bundle.regressions is None:
        st.info("Monthly benchmark regression output is not available yet.")
    else:
        st.dataframe(bundle.regressions, use_container_width=True, hide_index=True)
        render_csv_download(
            bundle.regressions,
            "Download Monthly Regressions CSV",
            "monthly_benchmark_regressions.csv",
        )

    st.subheader("Forecast Comparison")
    if bundle.forecasts is None:
        st.info("Monthly benchmark forecast output is not available yet.")
    else:
        forecast_fig = px.bar(
            bundle.forecasts,
            x="model",
            y="oos_r2",
            title="Monthly Forecast OOS R2 Versus Historical Mean",
        )
        forecast_fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(forecast_fig, use_container_width=True)
        st.dataframe(bundle.forecasts, use_container_width=True, hide_index=True)
        render_csv_download(
            bundle.forecasts,
            "Download Monthly Forecasts CSV",
            "monthly_benchmark_forecasts.csv",
        )


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
    ) = st.tabs(DAILY_TAB_LABELS)

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
        render_ml_tab(drawdown_metrics, drawdown_importance)

    with tab_rolling:
        render_rolling_tab(rolling_beta)

    with tab_monthly:
        render_monthly_benchmark_tab(monthly_outputs)

    with tab_coverage:
        render_coverage_tab(panel, large_returns)


if __name__ == "__main__":
    main()
