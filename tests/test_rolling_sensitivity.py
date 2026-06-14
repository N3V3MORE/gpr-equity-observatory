import pandas as pd

from gprobs.analysis.rolling_sensitivity import calculate_rolling_gpr_beta


def test_calculate_rolling_gpr_beta_returns_country_level_series():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
            ),
            "ticker": ["SPY", "SPY", "SPY", "SPY"],
            "country": ["United States"] * 4,
            "market_group": ["developed"] * 4,
            "return": [0.01, 0.02, 0.03, 0.04],
            "gpr": [100.0, 110.0, 120.0, 130.0],
        }
    )

    rolling = calculate_rolling_gpr_beta(panel, window=3, min_periods=2)

    assert rolling.columns.tolist() == [
        "date",
        "ticker",
        "country",
        "market_group",
        "rolling_gpr_beta",
    ]
    assert rolling["rolling_gpr_beta"].notna().sum() == 3
    assert rolling["rolling_gpr_beta"].iloc[-1] > 0
