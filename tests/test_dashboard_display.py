import pandas as pd

import app


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
