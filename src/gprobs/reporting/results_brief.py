import pandas as pd

from gprobs.reporting.formatting import format_basis_points, format_p_value, format_percent, format_score


def format_estimate(row: pd.Series) -> str:
    """Format estimate values using the row's structured unit."""
    unit = row.get("unit")
    if unit == "score":
        return format_score(row["estimate"])
    if unit == "basis_points":
        return format_basis_points(row["estimate"])
    if unit == "percent":
        return format_percent(row["estimate"])
    raise ValueError(f"Unknown estimate unit: {unit}")


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
        "| Method | Estimate | p-value | Inference |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['method']} | {format_estimate(row)} | "
            f"{format_p_value(row['p_value'])} | {row['inference']} |"
        )
    return lines


def build_results_brief(
    evidence_summary: pd.DataFrame,
    sample_robustness: pd.DataFrame,
) -> str:
    """Describe supplied model outputs without changing their estimates or inference."""
    controlled = _method_row(evidence_summary, "Controlled panel regression")
    interaction = _method_row(evidence_summary, "Controlled emerging interaction")
    date_fe_interaction = _method_row(
        evidence_summary,
        "Date fixed-effects emerging interaction",
    )
    quantile = _method_row(evidence_summary, "Tail-risk quantile regression")
    local_developed = _method_row(evidence_summary, "Local projection developed")
    local_emerging = _method_row(evidence_summary, "Local projection emerging")
    drawdown = _method_row(evidence_summary, "Drawdown classifier")

    robustness_scenario = "Excluding COVID and Russia windows"
    robust_gpr = _sample_row(sample_robustness, robustness_scenario, "gpr_change_z")
    robust_interaction = _sample_row(
        sample_robustness,
        robustness_scenario,
        "gpr_change_z:emerging_market",
    )

    lines = [
        "# GPR Equity Observatory Results Brief",
        "",
        "## Main Takeaway",
        "",
        "This brief describes the generated evidence-summary and sample-robustness outputs below. "
        "A separately published snapshot may differ; use its displayed estimates and uncertainty "
        "before applying this narrative to that snapshot.",
        "The controlled panel estimates conditional associations with daily GPR jumps. "
        "The date fixed-effects interaction reports the within-date emerging-market differential "
        "after absorbing common date shocks; it does not identify a separate global GPR coefficient.",
        "Weak statistical evidence is not proof of no effect. Neither an estimate's sign nor a "
        "single specification establishes a reliably larger emerging-market response.",
        "",
        "## Key Evidence",
        "",
        *_evidence_table(
            [
                controlled,
                interaction,
                date_fe_interaction,
                quantile,
                local_developed,
                local_emerging,
                drawdown,
            ]
        ),
        "",
        "Local projection rows are market-model abnormal return responses, not raw cumulative ETF returns.",
        "Prediction Lab treats the drawdown model as an out-of-sample risk-classification experiment, "
        "not as a trading signal.",
        "Event-study cumulative abnormal returns elsewhere in the dashboard start at each ETF-event's "
        "earliest observed relative day, normally the negative window boundary, and include pre-event "
        "returns. They are not day-0-onward returns. Their standard errors and t-test p-values are "
        "not adjusted for dependence between ETFs exposed to common events; no event-study "
        "confidence intervals are supplied here.",
        "",
        "## Known Raw Event-Window Limitation (Unchanged)",
        "",
        "The raw event-window builder can map an event before an ETF's first observation to that first "
        "observation, even when the event occurred years earlier. Raw event counts and returns can therefore "
        "include events predating the ETF's observed history. Correcting this requires a separate research "
        "change; this presentation patch leaves the estimator and its outputs unchanged. The primary "
        "abnormal-return study rejects these cases through its estimation-history requirement, so this "
        "particular mapping defect does not affect its table.",
        "",
        "## Sample Robustness",
        "",
        f"Under `{robustness_scenario}`, the controlled one-SD GPR-jump coefficient is "
        f"{format_basis_points(robust_gpr['estimate'])} with p-value "
        f"{format_p_value(robust_gpr['p_value'])}. The emerging interaction is "
        f"{format_basis_points(robust_interaction['estimate'])} with p-value "
        f"{format_p_value(robust_interaction['p_value'])}.",
        "",
        "These estimates describe a changed sample. Retaining the same sign after excluding crisis "
        "windows does not establish a robust GPR association: compare the magnitude, p-value, "
        "uncertainty and sample definition with the full-sample result.",
        "",
        "## How To Explain This",
        "",
        "- This is an empirical risk-response project, not a trading system.",
        "- Country ETFs are USD market proxies, not local equity indexes; their returns include currency exposure.",
        "- GPR jumps are not randomized events, so the results are associations.",
        "- The date fixed-effects specification identifies the emerging-market "
        "differential, not a separate global GPR-jump coefficient.",
        "- Conclusions should track the estimates and uncertainty in the displayed snapshot. "
        "Weak evidence is not proof of no effect, and these associations do not establish causality.",
        "",
    ]
    return "\n".join(lines)
