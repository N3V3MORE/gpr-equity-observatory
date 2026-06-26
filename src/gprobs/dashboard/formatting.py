import pandas as pd


def format_percent(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.1%}"


def format_basis_points(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value) * 10_000:.1f} bp"


def format_p_value(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.3f}"


def format_metric(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.3g}"


def classify_evidence_strength(row: pd.Series) -> str:
    """Return a cautious display label for dashboard evidence summaries."""
    inference = str(row.get("inference", "")).lower()
    p_value = pd.to_numeric(row.get("p_value"), errors="coerce")
    if "exploratory" in inference or pd.isna(p_value):
        return "Exploratory"
    if "mixed" in inference:
        return "Mixed"
    if p_value <= 0.10:
        return "Useful signal"
    if p_value <= 0.50:
        return "Mixed"
    return "Weak"


def format_evidence_direction(estimate: float) -> str:
    if estimate > 0:
        return "Positive"
    if estimate < 0:
        return "Negative"
    return "Near zero"


def format_evidence_estimate(estimate: float, unit: str) -> str:
    metric = format_metric(estimate)
    return f"{metric} {unit}".strip()
