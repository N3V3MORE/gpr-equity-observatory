from pathlib import Path

import pandas as pd
import streamlit as st

DASHBOARD_INTRO = (
    "This dashboard studies whether equity markets respond to geopolitical risk shocks, "
    "using 20 country ETF proxies."
)
DASHBOARD_MAIN_TAKEAWAY = (
    "Geopolitical risk appears associated with equity-market risk, but the evidence "
    "does not strongly prove that emerging markets always react more than developed markets."
)
DASHBOARD_USE_NOTE = "Use this dashboard as a research observatory, not as a trading system."
HOW_TO_READ_NOTES = {
    "overview": (
        "Start with the summary cards, then use the Evidence Map to compare what each method says. "
        "Mixed or weak labels mean the result should stay cautious."
    ),
    "shocks": (
        "The line shows the GPR index over time. Markers highlight the largest daily GPR changes, "
        "which are the shock episodes used elsewhere in the dashboard."
    ),
    "market_response": (
        "The line shows average cumulative abnormal returns around GPR shock dates. Day 0 is the "
        "shock day. A negative line after day 0 means ETFs tended to underperform their "
        "market-model expectation after shocks."
    ),
    "regression": (
        "The key term is the emerging-market interaction. If it is negative and statistically strong, "
        "that would support the idea that emerging markets react more. In the current version, this "
        "evidence is not strong."
    ),
    "downside_risk": (
        "Lower return quantiles describe worse return days. A more negative coefficient in the lower "
        "tail suggests downside association, but p-values still determine how strong the evidence is."
    ),
    "dynamic_response": (
        "Each horizon shows the estimated cumulative abnormal-return response after a GPR shock. "
        "Confidence bands crossing zero indicate weak statistical evidence at that horizon."
    ),
    "prediction_lab": (
        "This is an exploratory risk classifier. AUC above 0.5 means some ranking signal, but it is "
        "not a trading strategy and should not be read as a price forecast."
    ),
    "country_sensitivity": (
        "The rolling beta shows how one country's ETF return sensitivity to GPR changes over time. "
        "Use it as a diagnostic, not as a stable country ranking."
    ),
    "monthly_benchmark": (
        "This tab is separate from the daily ETF panel. Sample mode validates the workflow, while real "
        "mode is aggregate benchmark evidence, not country-level panel evidence."
    ),
    "data_quality": (
        "Coverage and large-return flags help identify data limitations that may affect interpretation. "
        "They are checks on the research inputs, not standalone findings."
    ),
}


def render_intro() -> None:
    st.markdown(DASHBOARD_INTRO)
    st.markdown(f"**Main takeaway:** {DASHBOARD_MAIN_TAKEAWAY}")
    st.caption(DASHBOARD_USE_NOTE)


def render_summary_cards() -> None:
    cards = [
        (
            "Question",
            "Do emerging and developed ETF markets respond differently to GPR shocks?",
        ),
        ("Data", "20 country ETF proxies, daily GPR data, and market controls."),
        (
            "Methods",
            "Event studies, regressions, quantile analysis, local projections, rolling betas, "
            "and drawdown-risk classification.",
        ),
        (
            "Bottom line",
            "Evidence is useful but mixed. Stronger for general risk association than for "
            "emerging-market asymmetry.",
        ),
    ]
    columns = st.columns(4)
    for column, (title, body) in zip(columns, cards, strict=True):
        with column:
            st.subheader(title)
            st.write(body)


def render_how_to_read(tab_key: str) -> None:
    st.info(f"How to read this: {HOW_TO_READ_NOTES[tab_key]}")


def render_csv_download(df: pd.DataFrame, label: str, filename: str) -> None:
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=f"download-{filename}",
    )


def render_missing_data_message(missing: list[Path]) -> None:
    st.error("Processed data files are missing.")
    st.write("To rebuild everything, run:")
    st.code("python scripts/build_all.py")
    with st.expander("Advanced: individual scripts"):
        from gprobs.pipeline import PIPELINE_STEPS

        st.code("\n".join(f"python scripts/{step.script_name}" for step in PIPELINE_STEPS))
    st.write("Missing files:")
    st.write([str(path) for path in missing])
