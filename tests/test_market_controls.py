import math

import pandas as pd

from gprobs.data.market_controls import build_market_controls, merge_market_controls


def test_build_market_controls_calculates_returns_and_level_changes():
    prices = pd.DataFrame(
        {
            "ACWI": [100.0, 110.0, 121.0],
            "^VIX": [20.0, 25.0, 23.0],
            "CL=F": [70.0, -37.0, 12.0],
            "UUP": [25.0, 26.0, 27.0],
            "^TNX": [40.0, 41.0, 39.5],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
    )

    controls = build_market_controls(prices)

    assert controls.columns.tolist() == [
        "date",
        "global_market_return",
        "vix_change",
        "oil_change",
        "dollar_return",
        "us10y_change",
    ]
    assert len(controls) == 2
    assert math.isclose(controls.loc[0, "global_market_return"], math.log(110.0 / 100.0))
    assert controls.loc[0, "vix_change"] == 5.0
    assert controls.loc[1, "oil_change"] == 49.0
    assert controls.loc[1, "us10y_change"] == -1.5


def test_merge_market_controls_adds_same_day_controls_to_panel():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02"]),
            "ticker": ["SPY"],
            "return": [0.01],
        }
    )
    controls = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02"]),
            "global_market_return": [0.02],
            "vix_change": [1.0],
            "oil_change": [2.0],
            "dollar_return": [-0.01],
            "us10y_change": [0.2],
        }
    )

    merged = merge_market_controls(panel, controls)

    assert merged.loc[0, "global_market_return"] == 0.02
    assert merged.loc[0, "vix_change"] == 1.0
