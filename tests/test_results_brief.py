import pandas as pd

from gprobs.dashboard.components import HOW_TO_READ_NOTES, build_snapshot_answer
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

    original_evidence = evidence.copy(deep=True)
    original_robustness = sample_robustness.copy(deep=True)
    brief = build_results_brief(evidence, sample_robustness)
    pd.testing.assert_frame_equal(evidence, original_evidence)
    pd.testing.assert_frame_equal(sample_robustness, original_robustness)

    assert "# GPR Equity Observatory Results Brief" in brief
    assert "Controlled panel regression" in brief
    assert "Date fixed-effects emerging interaction" in brief
    assert "-0.6 bps" in brief
    assert "| Drawdown classifier | 0.614 | n/a | cross-validation metric |" in brief
    assert "Prediction Lab treats the drawdown model as an out-of-sample risk-classification experiment" in brief
    assert "i.i.d. QuantReg asymptotic p-value" in brief
    assert "market-model abnormal return responses" in brief
    assert "Weak statistical evidence is not proof of no effect" in brief
    assert "Excluding COVID and Russia windows" in brief
    assert "does not establish a robust GPR association" in brief
    assert "not only a COVID" not in brief
    assert "separately published snapshot may differ" in brief
    assert "not day-0-onward returns" in brief
    assert "not adjusted for dependence between ETFs exposed to common events" in brief
    assert "-0.7 bps with p-value 0.022" in brief
    assert "## Known Raw Event-Window Limitation (Unchanged)" in brief
    assert "event before an ETF's first observation" in brief
    assert "Raw event counts and returns" in brief
    assert "requires a separate research change" in brief
    assert "leaves the estimator and its outputs unchanged" in brief
    assert "abnormal-return study rejects these cases through its estimation-history requirement" in brief


def test_snapshot_takeaways_follow_supplied_estimates_without_strength_claims():
    controlled = pd.DataFrame({
        "term": ["gpr_change_z", "gpr_change_z:emerging_market"],
        "estimate": [-0.00004, 0.0],
        "p_value": [0.325, 1.0],
    })
    date_fe = pd.DataFrame({
        "term": ["gpr_change_z:emerging_market"],
        "estimate": [0.00023],
        "p_value": [0.009],
    })
    before_controlled = controlled.copy(deep=True)
    before_date_fe = date_fe.copy(deep=True)

    answer = " ".join(build_snapshot_answer(controlled, date_fe))

    assert "-0.4 bps per one-SD daily GPR jump (p-value 0.325)" in answer
    assert "0.0 bps per one-SD daily GPR jump (p-value 1.000)" in answer
    assert "2.3 bps per one-SD daily GPR jump (p-value 0.009)" in answer
    assert "Weak statistical evidence is not proof of no effect" in answer
    assert "USD country ETF proxies" in answer
    assert "currency exposure" in answer
    assert "strong evidence" not in answer
    pd.testing.assert_frame_equal(controlled, before_controlled)
    pd.testing.assert_frame_equal(date_fe, before_date_fe)

    controlled.loc[0, ["estimate", "p_value"]] = [0.00012, 0.7]
    changed_answer = " ".join(build_snapshot_answer(controlled, date_fe))
    assert "1.2 bps per one-SD daily GPR jump (p-value 0.700)" in changed_answer
    assert "-0.4 bps" not in changed_answer


def test_event_copy_defines_accumulation_and_event_selection_without_ci_promise():
    note = HOW_TO_READ_NOTES["market_response"]
    assert "negative window boundary for a complete window" in note
    assert "earliest observed relative day" in note
    assert "not at day 0" in note
    assert "first observed trading date on or after" in note
    assert "not adjusted for dependence between ETFs exposed to common events" in note
    assert "confidence" not in note.lower()
    assert "largest daily GPR jumps" in HOW_TO_READ_NOTES["shocks"]
    assert "highlighted date need not be a selected event" in HOW_TO_READ_NOTES["shocks"]
    assert "does not display p-values or uncertainty" in HOW_TO_READ_NOTES["downside_risk"]
