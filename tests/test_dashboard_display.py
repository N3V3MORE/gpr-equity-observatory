from importlib import import_module

import pandas as pd

import app


def test_formatting_helpers_render_reader_values():
    formatting = import_module("gprobs.dashboard.formatting")

    assert formatting.format_percent(0.1234) == "12.3%"
    assert formatting.format_basis_points(-0.0042) == "-42.0 bp"
    assert formatting.format_p_value(0.0321) == "0.032"
    assert formatting.format_p_value(pd.NA) == ""
    assert formatting.format_metric(pd.NA) == ""


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
                "estimate": -0.5,
                "unit": "basis points",
                "p_value": 0.57,
                "inference": "weak evidence",
                "plain_english": "No strong asymmetry evidence.",
            }
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
    assert (
        evidence_map.loc[0, "Plain-English takeaway"]
        == "No strong asymmetry evidence."
    )


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
