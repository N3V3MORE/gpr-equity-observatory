import pandas as pd

from gprobs.reporting.results_brief import build_results_brief, format_percent


def test_format_percent_converts_return_units_to_percent_text():
    assert format_percent(-0.0019152235) == "-0.192%"
    assert format_percent(0.0022354858) == "0.224%"


def test_build_results_brief_summarizes_mixed_evidence_cautiously():
    evidence = pd.DataFrame(
        {
            "method": [
                "Controlled panel regression",
                "Controlled emerging interaction",
                "Date fixed-effects emerging interaction",
                "Tail-risk quantile regression",
                "Local projection developed",
                "Local projection emerging",
                "Drawdown classifier",
            ],
            "focus": [
                "Developed-market GPR coefficient",
                "Extra emerging-market GPR coefficient",
                "Extra emerging-market GPR coefficient with date FE",
                "10th-percentile GPR coefficient",
                "20-day cumulative abnormal response",
                "20-day cumulative abnormal response",
                "Mean ROC AUC",
            ],
            "estimate": [-0.000064, 0.000090, -0.000044, -0.000117, 0.0022, 0.0037, 0.614],
            "unit": [
                "basis_points",
                "basis_points",
                "basis_points",
                "basis_points",
                "percent",
                "percent",
                "score",
            ],
            "p_value": [0.006, 0.127, 0.041, 0.156, 0.034, 0.696, float("nan")],
            "inference": [
                "two-way clustered",
                "two-way clustered",
                "two-way clustered",
                "i.i.d. QuantReg asymptotic p-value",
                "two-way clustered",
                "two-way clustered",
                "cross-validation metric",
            ],
            "plain_english": [""] * 7,
        }
    )
    sample_robustness = pd.DataFrame(
        {
            "scenario": [
                "Excluding COVID and Russia windows",
                "Excluding COVID and Russia windows",
            ],
            "term": ["gpr_change_z", "gpr_change_z:emerging_market"],
            "estimate": [-0.000071, 0.000023],
            "std_error": [0.000031, 0.000066],
            "t_stat": [-2.29, 0.34],
            "p_value": [0.022, 0.733],
            "observation_count": [87150, 87150],
        }
    )

    brief = build_results_brief(evidence, sample_robustness)

    assert "# GPR Equity Observatory Results Brief" in brief
    assert "Controlled panel regression" in brief
    assert "Date fixed-effects emerging interaction" in brief
    assert "-0.6 bps" in brief
    assert "| Drawdown classifier | 0.614 | n/a | cross-validation metric |" in brief
    assert "Prediction Lab treats the drawdown model as an out-of-sample risk-classification experiment" in brief
    assert "i.i.d. QuantReg asymptotic p-value" in brief
    assert "market-model abnormal return responses" in brief
    assert "not strong evidence" in brief
    assert "Excluding COVID and Russia windows" in brief
