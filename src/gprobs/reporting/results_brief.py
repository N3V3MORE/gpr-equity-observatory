import math

import pandas as pd


def format_percent(value: float, digits: int = 3) -> str:
    """Format a decimal return or coefficient as percentage text."""
    return f"{float(value) * 100:.{digits}f}%"


def format_p_value(value: float) -> str:
    """Format p-values without false precision."""
    if value is None or math.isnan(float(value)):
        return "n/a"
    if float(value) < 0.001:
        return "<0.001"
    return f"{float(value):.3f}"


def format_estimate(row: pd.Series) -> str:
    """Format estimate values using the unit implied by the row."""
    if row["method"] == "Drawdown classifier":
        return f"{float(row['estimate']):.3f}"
    return format_percent(row["estimate"])


def _method_row(evidence: pd.DataFrame, method: str) -> pd.Series:
    rows = evidence.loc[evidence["method"] == method]
    if rows.empty:
        raise ValueError(f"Evidence summary is missing method: {method}")
    return rows.iloc[0]


def _sample_row(
    sample_robustness: pd.DataFrame,
    scenario: str,
    term: str,
) -> pd.Series:
    mask = (
        (sample_robustness["scenario"] == scenario)
        & (sample_robustness["term"] == term)
    )
    rows = sample_robustness.loc[mask]
    if rows.empty:
        raise ValueError(f"Sample robustness is missing {term} for {scenario}.")
    return rows.iloc[0]


def _evidence_table(rows: list[pd.Series]) -> list[str]:
    lines = [
        "| Method | Estimate | p-value |",
        "| --- | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['method']} | {format_estimate(row)} | "
            f"{format_p_value(row['p_value'])} |"
        )
    return lines


def build_results_brief(
    evidence_summary: pd.DataFrame,
    sample_robustness: pd.DataFrame,
) -> str:
    """Build a concise Markdown brief from generated model outputs."""
    controlled = _method_row(evidence_summary, "Controlled panel regression")
    interaction = _method_row(evidence_summary, "Controlled emerging interaction")
    quantile = _method_row(evidence_summary, "Tail-risk quantile regression")
    local_developed = _method_row(evidence_summary, "Local projection developed")
    local_emerging = _method_row(evidence_summary, "Local projection emerging")
    drawdown = _method_row(evidence_summary, "Drawdown classifier")

    robustness_scenario = "Excluding COVID and Russia windows"
    robust_gpr = _sample_row(sample_robustness, robustness_scenario, "gpr_z")
    robust_interaction = _sample_row(
        sample_robustness,
        robustness_scenario,
        "gpr_z:emerging_market",
    )

    lines = [
        "# GPR Equity Observatory Results Brief",
        "",
        "## Main Takeaway",
        "",
        "The current evidence is mixed. The controlled panel regression finds a "
        "negative GPR-return association, but the emerging-market interaction is "
        "not strong evidence of a reliably larger emerging-market response.",
        "",
        "## Key Evidence",
        "",
        *_evidence_table(
            [
                controlled,
                interaction,
                quantile,
                local_developed,
                local_emerging,
                drawdown,
            ]
        ),
        "",
        "## Sample Robustness",
        "",
        f"Under `{robustness_scenario}`, the controlled GPR coefficient is "
        f"{format_percent(robust_gpr['estimate'])} with p-value "
        f"{format_p_value(robust_gpr['p_value'])}. The emerging interaction is "
        f"{format_percent(robust_interaction['estimate'])} with p-value "
        f"{format_p_value(robust_interaction['p_value'])}.",
        "",
        "That means the main controlled GPR coefficient is not only a COVID or "
        "Russia-Ukraine result. But the emerging-market asymmetry claim remains "
        "weak in the current specification.",
        "",
        "## How To Explain This",
        "",
        "- This is an empirical risk-response project, not a trading system.",
        "- ETF returns are USD returns, so they include currency exposure.",
        "- GPR shocks are not randomized events, so the results are associations.",
        "- The best current conclusion is cautious: GPR is linked to equity risk, "
        "but emerging-market asymmetry is not yet a strong finding.",
        "",
    ]
    return "\n".join(lines)
