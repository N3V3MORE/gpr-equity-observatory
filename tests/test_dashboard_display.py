from importlib import import_module

import pandas as pd
import pytest

import app


def test_formatting_helpers_render_reader_values():
    formatting = import_module("gprobs.dashboard.formatting")

    assert formatting.format_percent(0.1234) == "12.3%"
    assert formatting.format_basis_points(-0.0042) == "-42.0 bps"
    assert formatting.format_p_value(0.0321) == "0.032"
    assert formatting.format_p_value(0.0004) == "<0.001"
    assert formatting.format_p_value(pd.NA) == "n/a"
    assert formatting.format_metric(pd.NA) == "n/a"


def test_format_evidence_estimate_uses_structured_units():
    formatting = import_module("gprobs.dashboard.formatting")

    assert formatting.format_evidence_estimate(-0.0042, "basis_points") == "-42.0 bps"
    assert formatting.format_evidence_estimate(0.1234, "percent") == "12.3%"
    assert formatting.format_evidence_estimate(0.6142, "score") == "0.614"

    with pytest.raises(ValueError, match="Unknown estimate unit"):
        formatting.format_evidence_estimate(1.0, "basis points")


def test_classify_evidence_strength_uses_cautious_labels():
    assert (
        app.classify_evidence_strength(
            pd.Series({"p_value": 0.03, "inference": "negative association"})
        )
        == "Useful signal"
    )
    assert (
        app.classify_evidence_strength(
            pd.Series({"p_value": 0.40, "inference": "mixed evidence"})
        )
        == "Mixed"
    )
    assert (
        app.classify_evidence_strength(
            pd.Series({"p_value": 0.80, "inference": "weak evidence"})
        )
        == "Weak"
    )
    assert (
        app.classify_evidence_strength(
            pd.Series({"p_value": pd.NA, "inference": "exploratory classifier"})
        )
        == "Exploratory"
    )


def test_build_evidence_map_adds_strength_and_reader_columns():
    summary = pd.DataFrame(
        [
            {
                "method": "Panel regression",
                "focus": "Emerging-market interaction",
                "estimate": -0.00005,
                "unit": "basis_points",
                "p_value": 0.57,
                "inference": "weak evidence",
                "plain_english": "No strong asymmetry evidence.",
            },
            {
                "method": "Drawdown classifier",
                "focus": "Mean ROC AUC",
                "estimate": 0.6142,
                "unit": "score",
                "p_value": pd.NA,
                "inference": "exploratory classifier",
                "plain_english": "Exploratory risk-ranking metric.",
            },
        ]
    )

    evidence_map = app.build_evidence_map(summary)

    assert list(evidence_map.columns) == [
        "Method",
        "Question answered",
        "Direction",
        "Estimate",
        "p-value / metric",
        "Evidence strength",
        "Plain-English takeaway",
    ]
    assert evidence_map.loc[0, "Evidence strength"] == "Weak"
    assert evidence_map.loc[0, "Estimate"] == "-0.5 bps"
    assert evidence_map.loc[0, "p-value / metric"] == "0.570"
    assert (
        evidence_map.loc[0, "Plain-English takeaway"]
        == "No strong asymmetry evidence."
    )
    assert evidence_map.loc[1, "Evidence strength"] == "Exploratory"
    assert evidence_map.loc[1, "Estimate"] == "0.614"
    assert evidence_map.loc[1, "p-value / metric"] == "n/a"


def test_build_gpr_shock_timeline_marks_top_shocks():
    charts = import_module("gprobs.dashboard.charts")

    assert charts.build_gpr_shock_timeline is app.build_gpr_shock_timeline

    gpr = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=4, freq="D"),
            "gpr": [100, 110, 90, 130],
            "gpr_change": [0, 10, -20, 40],
            "event": ["", "Shock A", "", "Shock B"],
        }
    )

    fig = app.build_gpr_shock_timeline(gpr)

    assert len(fig.data) == 2
    assert fig.data[1].name == "Top GPR changes"
    assert list(fig.data[1].x) == [
        pd.Timestamp("2024-01-04"),
        pd.Timestamp("2024-01-02"),
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-01-03"),
    ]
