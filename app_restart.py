"""
Beginner dashboard for GPR Equity Observatory.

This file is intentionally simple.

It does not replace the public Next.js app or the full Streamlit app.
It reads generated CSV files and explains them in a beginner-friendly way.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"


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


def load_csv(filename: str, date_columns: list[str] | None = None) -> pd.DataFrame | None:
    """Load one generated CSV file.

    Returns None when the file is missing.
    This keeps the page readable instead of crashing.
    """
    path = DATA / filename

    if not path.exists():
        return None

    if date_columns:
        return pd.read_csv(path, parse_dates=date_columns)

    return pd.read_csv(path)


def output_file_status() -> pd.DataFrame:
    """Show which generated files exist."""
    rows = []

    for filename in IMPORTANT_OUTPUTS:
        path = DATA / filename

        if not path.exists():
            rows.append(
                {
                    "File": filename,
                    "Exists?": "No",
                    "Rows": "",
                    "Beginner meaning": file_meaning(filename),
                }
            )
            continue

        try:
            row_count = len(pd.read_csv(path))
        except Exception:
            row_count = "Could not read"

        rows.append(
            {
                "File": filename,
                "Exists?": "Yes",
                "Rows": row_count,
                "Beginner meaning": file_meaning(filename),
            }
        )

    return pd.DataFrame(rows)


def file_meaning(filename: str) -> str:
    """Translate file names into plain English."""
    meanings = {
        "gpr_daily.csv": "Daily geopolitical risk data.",
        "analysis_panel.csv": "Main merged dataset: ETF returns plus GPR data.",
        "group_return_summary.csv": "Average returns for developed and emerging markets.",
        "event_study_abnormal_summary.csv": "Market reaction around GPR shock days.",
        "panel_regression_controlled.csv": "Regression after adding market controls.",
        "panel_regression_date_fe.csv": "Cleaner developed versus emerging comparison.",
        "quantile_regression_results.csv": "Checks whether bad return days behave differently.",
        "local_projection_results.csv": "Response path after GPR shock days.",
        "drawdown_model_metrics.csv": "Prediction Lab model scores.",
        "drawdown_feature_importance.csv": "Variables that mattered most in the model.",
        "rolling_gpr_beta.csv": "Country sensitivity to GPR over time.",
        "large_return_flags.csv": "Potentially unusual ETF return days.",
        "evidence_summary.csv": "Compact summary of the main evidence.",
    }
    return meanings.get(filename, "Generated project output.")


def evidence_strength_from_pvalue(p_value: float | None) -> str:
    """Convert a p-value into a beginner label."""
    if p_value is None or pd.isna(p_value):
        return "Not applicable"
    if p_value < 0.05:
        return "Conventional p < 0.05"
    if p_value < 0.10:
        return "Suggestive p < 0.10"
    return "Weak in this run"


def direction_from_value(value: float | None) -> str:
    """Convert a number into a direction label."""
    if value is None or pd.isna(value):
        return "Unknown"
    if value > 0:
        return "Positive"
    if value < 0:
        return "Negative"
    return "Flat"


def show_project_summary() -> None:
    """First table: explain the whole project."""
    summary = pd.DataFrame(
        [
            {
                "Question": "What is this project?",
                "Simple answer": "It checks whether geopolitical risk is linked to equity-market risk.",
                "Evidence used": (
                    "GPR data, country ETF returns, event studies, regressions, "
                    "and prediction diagnostics."
                ),
                "How to read it": "Project setup is clear",
                "What this means": "The project is a research dashboard, not a trading tool.",
            },
            {
                "Question": "What is GPR?",
                "Simple answer": "GPR is a news-based geopolitical risk index.",
                "Evidence used": "Daily Caldara-Iacoviello GPR file.",
                "How to read it": "Input source is documented",
                "What this means": "Higher GPR means more geopolitical risk in the news.",
            },
            {
                "Question": "Do markets react after GPR shocks?",
                "Simple answer": "The evidence is mixed.",
                "Evidence used": "Event studies and regressions.",
                "How to read it": "Compare methods before concluding",
                "What this means": "Some results point negative, but the project should not overclaim.",
            },
            {
                "Question": "Do emerging markets react more?",
                "Simple answer": "Not clearly supported in the current results.",
                "Evidence used": "Date fixed-effects regression.",
                "How to read it": "Treat as limited evidence",
                "What this means": "This is a careful finding, not a dramatic headline.",
            },
            {
                "Question": "Is Prediction Lab a trading model?",
                "Simple answer": "No.",
                "Evidence used": "Drawdown-risk classification diagnostics.",
                "How to read it": "Risk-ranking experiment only",
                "What this means": "It is exploratory risk ranking, not investment advice.",
            },
        ]
    )

    st.subheader("Project summary")
    st.write("This table explains the whole project before showing technical outputs.")
    st.dataframe(summary, use_container_width=True, hide_index=True)


def show_files_used() -> None:
    """Second table: explain the important files."""
    files = pd.DataFrame(
        [
            {
                "File": "data/country_universe.csv",
                "What it contains": "20 country ETFs and their developed or emerging label.",
                "Why we need it": "It tells the project which markets to study.",
                "Beginner meaning": "This is the country list.",
            },
            {
                "File": "data/processed/gpr_daily.csv",
                "What it contains": "Daily geopolitical risk values.",
                "Why we need it": "This is the main risk variable.",
                "Beginner meaning": "This tells us when geopolitical risk rose.",
            },
            {
                "File": "data/processed/analysis_panel.csv",
                "What it contains": "ETF returns merged with GPR data.",
                "Why we need it": "Most models use this combined file.",
                "Beginner meaning": "This is the main working dataset.",
            },
            {
                "File": "data/processed/evidence_summary.csv",
                "What it contains": "Main results summarized across methods.",
                "Why we need it": "It helps compare all evidence in one place.",
                "Beginner meaning": "This is the first results table to read.",
            },
        ]
    )

    st.subheader("Files used")
    st.write("This table explains the files before showing charts and results.")
    st.dataframe(files, use_container_width=True, hide_index=True)


def show_gpr_page() -> None:
    """Show GPR data, chart, and shock table."""
    gpr = load_csv("gpr_daily.csv", ["date"])

    st.header("GPR Data")
    st.write("This page shows geopolitical risk over time and the biggest risk jumps.")

    if gpr is None:
        st.warning("Missing `data/processed/gpr_daily.csv`. Run the pipeline first.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("First date", str(gpr["date"].min().date()))
    col2.metric("Latest date", str(gpr["date"].max().date()))
    col3.metric("Rows", f"{len(gpr):,}")

    fig = px.line(gpr, x="date", y="gpr", title="Daily geopolitical risk")
    st.plotly_chart(fig, use_container_width=True)

    if "gpr_change" in gpr.columns:
        top_shocks = gpr.sort_values("gpr_change", ascending=False).head(25).copy()

        shock_columns = [
            col
            for col in ["date", "gpr", "gpr_change", "gpr_act", "gpr_threat", "event"]
            if col in top_shocks.columns
        ]

        shock_table = top_shocks[shock_columns].rename(
            columns={
                "date": "Date",
                "gpr": "GPR level",
                "gpr_change": "Daily jump",
                "gpr_act": "Actual event risk",
                "gpr_threat": "Threat risk",
                "event": "Event label",
            }
        )

        shock_table["Plain-English note"] = "Large increase in geopolitical risk."

        st.subheader("Biggest GPR jumps")
        st.write("These are the days where the GPR index jumped the most.")
        st.dataframe(shock_table, use_container_width=True, hide_index=True)

    with st.expander("Show raw GPR data"):
        st.dataframe(gpr.tail(100), use_container_width=True, hide_index=True)


def show_market_reaction_page() -> None:
    """Show simple market reaction outputs."""
    group_returns = load_csv("group_return_summary.csv", ["date"])
    event_study = load_csv("event_study_abnormal_summary.csv")

    st.header("Market Reaction")
    st.write("This page asks whether markets moved around GPR shock days.")

    if group_returns is not None:
        chart_data = group_returns.copy()
        chart_data["cumulative_average_return"] = chart_data.groupby("market_group")[
            "average_return"
        ].cumsum()

        fig = px.line(
            chart_data,
            x="date",
            y="cumulative_average_return",
            color="market_group",
            title="Cumulative average ETF returns by market group",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Missing `group_return_summary.csv`.")

    if event_study is not None:
        key_days = event_study[event_study["relative_day"].isin([0, 1, 5, 10])].copy()
        if key_days.empty:
            key_days = event_study.copy()

        value_col = "cumulative_average_abnormal_return"
        key_days["Direction"] = key_days[value_col].apply(direction_from_value)
        key_days["Evidence strength"] = key_days["p_value"].apply(evidence_strength_from_pvalue)
        key_days["Plain-English note"] = key_days.apply(
            lambda row: (
                f"{row['market_group']} markets moved "
                f"{str(row['Direction']).lower()} by this point. "
                f"Evidence strength: {str(row['Evidence strength']).lower()}."
            ),
            axis=1,
        )

        reaction_table = key_days[
            [
                "market_group",
                "relative_day",
                value_col,
                "Direction",
                "Evidence strength",
                "Plain-English note",
            ]
        ].rename(
            columns={
                "market_group": "Market group",
                "relative_day": "Days after shock",
                value_col: "Cumulative abnormal return",
            }
        )

        st.subheader("Market reaction summary")
        st.dataframe(reaction_table, use_container_width=True, hide_index=True)

        with st.expander("Show raw event-study table"):
            st.dataframe(event_study, use_container_width=True, hide_index=True)
    else:
        st.warning("Missing `event_study_abnormal_summary.csv`.")


def show_regression_page() -> None:
    """Show readable regression interpretation."""
    controlled = load_csv("panel_regression_controlled.csv")
    date_fe = load_csv("panel_regression_date_fe.csv")
    quantile = load_csv("quantile_regression_results.csv")

    st.header("Regression Results")
    st.write(
        "This page translates the regression tables. "
        "The raw statistical tables are hidden below the readable summary."
    )

    rows = []

    if controlled is not None and not controlled.empty:
        first = controlled.iloc[0]
        rows.append(
            {
                "Test": "Controlled GPR effect",
                "What it checks": "Whether GPR changes are linked to ETF returns after market controls.",
                "Direction": direction_from_value(first.get("estimate")),
                "P-value": first.get("p_value"),
                "Evidence strength": evidence_strength_from_pvalue(first.get("p_value")),
                "Plain-English note": "Use this as association evidence, not a causal estimate.",
            }
        )

    if date_fe is not None and not date_fe.empty:
        first = date_fe.iloc[0]
        rows.append(
            {
                "Test": "Developed versus emerging comparison",
                "What it checks": "Whether emerging markets have a different GPR response.",
                "Direction": direction_from_value(first.get("estimate")),
                "P-value": first.get("p_value"),
                "Evidence strength": evidence_strength_from_pvalue(first.get("p_value")),
                "Plain-English note": "This is the cleaner test for emerging-market asymmetry.",
            }
        )

    if quantile is not None and not quantile.empty:
        first = quantile.iloc[0]
        rows.append(
            {
                "Test": "Downside-risk check",
                "What it checks": "Whether worse return days are more sensitive to GPR.",
                "Direction": direction_from_value(first.get("estimate")),
                "P-value": first.get("p_value"),
                "Evidence strength": evidence_strength_from_pvalue(first.get("p_value")),
                "Plain-English note": "This is a risk diagnostic, not a final answer.",
            }
        )

    if rows:
        st.subheader("Regression translation table")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.warning("Regression files are missing or empty.")

    with st.expander("Show raw controlled regression"):
        if controlled is not None:
            st.dataframe(controlled, use_container_width=True, hide_index=True)
        else:
            st.write("Missing file.")

    with st.expander("Show raw date fixed-effects regression"):
        if date_fe is not None:
            st.dataframe(date_fe, use_container_width=True, hide_index=True)
        else:
            st.write("Missing file.")

    with st.expander("Show raw quantile regression"):
        if quantile is not None:
            st.dataframe(quantile, use_container_width=True, hide_index=True)
        else:
            st.write("Missing file.")


def show_prediction_page() -> None:
    """Show readable Prediction Lab summary."""
    metrics = load_csv("drawdown_model_metrics.csv")
    importance = load_csv("drawdown_feature_importance.csv")

    st.header("Prediction Lab")
    st.write(
        "This page explains the drawdown-risk experiment. "
        "It is not a trading signal."
    )

    if metrics is None:
        st.warning("Missing `drawdown_model_metrics.csv`.")
    else:
        model_table = (
            metrics.groupby("model_name", as_index=False)
            .agg(
                {
                    "roc_auc": "mean",
                    "average_precision": "mean",
                    "base_rate": "mean",
                    "observation_count": "sum",
                }
            )
            .rename(
                columns={
                    "model_name": "Model",
                    "roc_auc": "AUC score",
                    "average_precision": "Average precision",
                    "base_rate": "Normal event rate",
                    "observation_count": "Rows tested",
                }
            )
        )

        def usefulness(auc: float) -> str:
            if auc >= 0.70:
                return "Clearer ranking"
            if auc >= 0.60:
                return "Limited ranking"
            return "Weak ranking"

        model_table["Usefulness"] = model_table["AUC score"].apply(usefulness)
        model_table["Plain-English note"] = model_table["Usefulness"].map(
            {
                "Clearer ranking": (
                    "The model separates higher-risk and lower-risk cases better "
                    "than the weaker variants."
                ),
                "Limited ranking": "The model has some ranking ability, but the result is limited.",
                "Weak ranking": "The model does not add much reliable information in this run.",
            }
        )

        st.subheader("Prediction Lab translation table")
        st.dataframe(model_table, use_container_width=True, hide_index=True)

        with st.expander("Show raw model metrics"):
            st.dataframe(metrics, use_container_width=True, hide_index=True)

    if importance is not None and not importance.empty:
        top = importance.sort_values("abs_coefficient", ascending=False).head(20)
        fig = px.bar(
            top,
            x="abs_coefficient",
            y="feature",
            orientation="h",
            title="Top model features",
        )
        st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="GPR Beginner Dashboard", layout="wide")

    st.title("GPR Equity Observatory")
    st.caption("Beginner-friendly restart dashboard.")

    tab_start, tab_gpr, tab_market, tab_reg, tab_pred = st.tabs(
        [
            "Start Here",
            "GPR Data",
            "Market Reaction",
            "Regression Results",
            "Prediction Lab",
        ]
    )

    with tab_start:
        show_project_summary()
        show_files_used()

        st.subheader("Output file status")
        st.write("This tells you which generated files exist right now.")
        st.dataframe(output_file_status(), use_container_width=True, hide_index=True)

    with tab_gpr:
        show_gpr_page()

    with tab_market:
        show_market_reaction_page()

    with tab_reg:
        show_regression_page()

    with tab_pred:
        show_prediction_page()


if __name__ == "__main__":
    main()
