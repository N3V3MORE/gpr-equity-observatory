import math

import pandas as pd

from gprobs.features.returns import build_returns_panel, calculate_log_returns


def test_calculate_log_returns_uses_log_price_ratio():
    prices = pd.Series(
        [100.0, 110.0, 121.0],
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        name="SPY",
    )

    returns = calculate_log_returns(prices)

    assert len(returns) == 2
    assert math.isclose(returns.iloc[0], math.log(110.0 / 100.0))
    assert math.isclose(returns.iloc[1], math.log(121.0 / 110.0))


def test_calculate_log_returns_does_not_bridge_missing_prices():
    prices = pd.Series(
        [100.0, None, 121.0],
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        name="SPY",
    )

    returns = calculate_log_returns(prices)

    assert returns.empty


def test_build_returns_panel_converts_wide_prices_to_long_returns():
    prices = pd.DataFrame(
        {
            "SPY": [100.0, 105.0, 110.0],
            "EWZ": [50.0, 45.0, 48.0],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
    )

    panel = build_returns_panel(prices)

    assert panel.columns.tolist() == ["date", "ticker", "return"]
    assert panel["ticker"].tolist() == ["SPY", "SPY", "EWZ", "EWZ"]
    assert panel["date"].tolist() == [
        pd.Timestamp("2024-01-02"),
        pd.Timestamp("2024-01-03"),
        pd.Timestamp("2024-01-02"),
        pd.Timestamp("2024-01-03"),
    ]
