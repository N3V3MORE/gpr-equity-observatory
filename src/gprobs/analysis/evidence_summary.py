import math

import pandas as pd


SUMMARY_COLUMNS = ["method", "focus", "estimate", "p_value", "plain_english"]


def _single_row(table: pd.DataFrame, mask: pd.Series, label: str) -> pd.Series:
    rows = table.loc[mask]
    if rows.empty:
        raise ValueError(f"Missing {label} in evidence summary inputs.")
    return rows.iloc[0]


def _term_row(table: pd.DataFrame, term: str, label: str) -> pd.Series:
    return _single_row(table, table["term"] == term, label)


def _quantile_row(
    table: pd.DataFrame,
    quantile: float,
    term: str,
    label: str,
) -> pd.Series:
    mask = (table["quantile"].sub(quantile).abs() < 1e-9) & (table["term"] == term)
    return _single_row(table, mask, label)


def _local_projection_row(
    table: pd.DataFrame,
    horizon: int,
    market_group: str,
) -> pd.Series:
    mask = (table["horizon"] == horizon) & (table["market_group"] == market_group)
    return _single_row(table, mask, f"{horizon}-day {market_group} local projection")


def _event_robustness_row(
    table: pd.DataFrame,
    shock_quantile: float,
    window: int,
    market_group: str,
) -> pd.Series:
    mask = (
        (table["shock_quantile"].sub(shock_quantile).abs() < 1e-9)
        & (table["window"] == window)
        & (table["market_group"] == market_group)
    )
    return _single_row(
        table,
        mask,
        f"{shock_quantile:.0%} shock {window}-day {market_group} event robustness",
    )


def _add_row(
    rows: list[dict],
    method: str,
    focus: str,
    estimate: float,
    p_value: float,
    plain_english: str,
) -> None:
    rows.append(
        {
            "method": method,
            "focus": focus,
            "estimate": float(estimate),
            "p_value": p_value,
            "plain_english": plain_english,
        }
    )


def build_evidence_summary(
    baseline_regression: pd.DataFrame,
    controlled_regression: pd.DataFrame,
    quantile_regression: pd.DataFrame,
    local_projections: pd.DataFrame,
    event_robustness: pd.DataFrame,
    drawdown_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """Build a compact plain-English table from existing model outputs."""
    rows: list[dict] = []

    baseline_gpr = _term_row(baseline_regression, "gpr_z", "gpr_z")
    _add_row(
        rows,
        "Baseline panel regression",
        "Developed-market GPR coefficient",
        baseline_gpr["estimate"],
        float(baseline_gpr["p_value"]),
        "Before market controls, this is the developed-market GPR association.",
    )

    controlled_gpr = _term_row(controlled_regression, "gpr_z", "controlled gpr_z")
    _add_row(
        rows,
        "Controlled panel regression",
        "Developed-market GPR coefficient",
        controlled_gpr["estimate"],
        float(controlled_gpr["p_value"]),
        "After market controls, this is the developed-market GPR association.",
    )

    interaction = _term_row(
        controlled_regression,
        "gpr_z:emerging_market",
        "gpr_z:emerging_market",
    )
    _add_row(
        rows,
        "Controlled emerging interaction",
        "Extra emerging-market GPR coefficient",
        interaction["estimate"],
        float(interaction["p_value"]),
        "This is the extra emerging-market response after controls.",
    )

    q10_gpr = _quantile_row(
        quantile_regression,
        0.10,
        "gpr_z",
        "10th-percentile gpr_z",
    )
    _add_row(
        rows,
        "Tail-risk quantile regression",
        "10th-percentile GPR coefficient",
        q10_gpr["estimate"],
        float(q10_gpr["p_value"]),
        "This checks whether GPR matters on bad return days.",
    )

    horizon = int(local_projections["horizon"].max())
    for market_group in ["developed", "emerging"]:
        lp_row = _local_projection_row(local_projections, horizon, market_group)
        _add_row(
            rows,
            f"Local projection {market_group}",
            f"{horizon}-day cumulative response",
            lp_row["estimate"],
            float(lp_row["p_value"]),
            "This is the cumulative return response after a GPR shock.",
        )

    for market_group in ["developed", "emerging"]:
        event_row = _event_robustness_row(event_robustness, 0.90, 10, market_group)
        _add_row(
            rows,
            f"Event robustness {market_group}",
            "90th-percentile shock, 10-day endpoint",
            event_row["cumulative_average_abnormal_return"],
            math.nan,
            "This is the abnormal-return endpoint under a wider shock definition.",
        )

    if drawdown_metrics.empty:
        raise ValueError("Missing drawdown metrics in evidence summary inputs.")
    mean_auc = round(float(drawdown_metrics["roc_auc"].mean()), 6)
    mean_ap = float(drawdown_metrics["average_precision"].mean())
    mean_base_rate = float(drawdown_metrics["base_rate"].mean())
    _add_row(
        rows,
        "Drawdown classifier",
        "Mean ROC AUC",
        mean_auc,
        math.nan,
        f"Average precision is {mean_ap:.3f} versus base rate {mean_base_rate:.1%}.",
    )

    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)
