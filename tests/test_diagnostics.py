import pandas as pd

from gprobs.data.diagnostics import flag_large_returns, summarize_country_coverage


def test_flag_large_returns_keeps_only_abs_returns_above_threshold():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "ticker": ["SPY", "EWZ"],
            "country": ["United States", "Brazil"],
            "return": [0.05, -0.25],
        }
    )

    flagged = flag_large_returns(panel, threshold=0.20)

    assert len(flagged) == 1
    assert flagged.loc[0, "ticker"] == "EWZ"
    assert flagged.loc[0, "abs_return"] == 0.25


def test_summarize_country_coverage_counts_available_dates():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-01"]),
            "ticker": ["SPY", "SPY", "EWZ"],
            "country": ["United States", "United States", "Brazil"],
            "market_group": ["developed", "developed", "emerging"],
            "return": [0.01, 0.02, -0.03],
        }
    )

    coverage = summarize_country_coverage(panel)

    assert coverage.loc[coverage["ticker"] == "SPY", "observation_count"].iloc[0] == 2
    assert coverage.loc[coverage["ticker"] == "EWZ", "observation_count"].iloc[0] == 1
