import pandas as pd

from gprobs.dashboard.metrics import build_country_coverage, select_key_regression_terms


def test_build_country_coverage_summarizes_dates_and_observation_counts():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-01"]),
            "country": ["United States", "United States", "Brazil"],
            "ticker": ["SPY", "SPY", "EWZ"],
            "market_group": ["developed", "developed", "emerging"],
            "return": [0.01, 0.02, -0.03],
        }
    )

    coverage = build_country_coverage(panel)

    assert coverage.columns.tolist() == [
        "country",
        "ticker",
        "market_group",
        "first_date",
        "last_date",
        "observation_count",
    ]
    assert coverage.loc[coverage["ticker"] == "SPY", "observation_count"].iloc[0] == 2


def test_select_key_regression_terms_keeps_gpr_terms_only():
    table = pd.DataFrame(
        {
            "term": ["Intercept", "gpr_change_z", "gpr_change_z:emerging_market"],
            "estimate": [0.0, 0.1, -0.2],
            "p_value": [1.0, 0.05, 0.10],
        }
    )

    selected = select_key_regression_terms(table)

    assert selected["term"].tolist() == ["gpr_change_z", "gpr_change_z:emerging_market"]
