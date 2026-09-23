import pandas as pd

from gprobs.dashboard.formatting import (
    classify_evidence_strength,
    format_evidence_direction,
    format_evidence_estimate,
    format_p_value,
)


def build_evidence_map(evidence_summary: pd.DataFrame) -> pd.DataFrame:
    evidence_map = evidence_summary.copy()
    event_rows = evidence_map["method"].isin(
        ["Event robustness developed", "Event robustness emerging"]
    )
    evidence_map.loc[event_rows, "focus"] = "Pre-event-inclusive cumulative abnormal-return endpoint"
    evidence_map.loc[event_rows, "plain_english"] = (
        "Accumulation starts at each ETF-event's earliest observed relative day, including pre-event days. "
        "The p-value is not adjusted for dependence between ETFs exposed to common events."
    )
    evidence_map["Evidence strength"] = evidence_map.apply(classify_evidence_strength, axis=1)
    evidence_map.loc[event_rows, "Evidence strength"] = "Unadjusted event-study inference"
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
