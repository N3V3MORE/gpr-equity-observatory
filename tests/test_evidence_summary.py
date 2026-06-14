import pandas as pd
import pytest

from gprobs.analysis.evidence_summary import build_evidence_summary


def test_build_evidence_summary_collects_core_outputs_in_order():
    baseline = pd.DataFrame(
        {
            "term": ["gpr_z"],
            "estimate": [-0.10],
            "p_value": [0.03],
        }
    )
    controlled = pd.DataFrame(
        {
            "term": ["gpr_z", "gpr_z:emerging_market"],
            "estimate": [-0.06, 0.09],
            "p_value": [0.01, 0.13],
        }
    )
    quantile = pd.DataFrame(
        {
            "quantile": [0.10, 0.50],
            "term": ["gpr_z", "gpr_z"],
            "estimate": [-0.12, -0.04],
            "p_value": [0.16, 0.27],
        }
    )
    local_projections = pd.DataFrame(
        {
            "horizon": [20, 20],
            "market_group": ["developed", "emerging"],
            "estimate": [0.002, 0.004],
            "p_value": [0.04, 0.70],
        }
    )
    event_robustness = pd.DataFrame(
        {
            "shock_quantile": [0.90, 0.90],
            "window": [10, 10],
            "market_group": ["developed", "emerging"],
            "cumulative_average_abnormal_return": [-0.001, -0.002],
            "event_count": [100, 100],
        }
    )
    drawdown_metrics = pd.DataFrame(
        {
            "roc_auc": [0.60, 0.70],
            "average_precision": [0.30, 0.40],
            "base_rate": [0.20, 0.30],
        }
    )

    summary = build_evidence_summary(
        baseline,
        controlled,
        quantile,
        local_projections,
        event_robustness,
        drawdown_metrics,
    )

    assert summary.columns.tolist() == [
        "method",
        "focus",
        "estimate",
        "p_value",
        "plain_english",
    ]
    assert summary["method"].tolist() == [
        "Baseline panel regression",
        "Controlled panel regression",
        "Controlled emerging interaction",
        "Tail-risk quantile regression",
        "Local projection developed",
        "Local projection emerging",
        "Event robustness developed",
        "Event robustness emerging",
        "Drawdown classifier",
    ]
    assert summary.loc[1, "estimate"] == -0.06
    assert summary.loc[1, "p_value"] == 0.01
    assert summary.loc[8, "estimate"] == 0.65


def test_build_evidence_summary_raises_clear_error_for_missing_term():
    empty = pd.DataFrame(columns=["term", "estimate", "p_value"])
    minimal = pd.DataFrame(
        {
            "quantile": [0.10],
            "term": ["gpr_z"],
            "estimate": [-0.12],
            "p_value": [0.16],
        }
    )

    with pytest.raises(ValueError, match="Missing gpr_z"):
        build_evidence_summary(empty, empty, minimal, empty, empty, empty)
