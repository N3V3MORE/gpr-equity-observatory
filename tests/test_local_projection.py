import pandas as pd

from gprobs.analysis.local_projection import (
    build_local_projection_data,
    estimate_local_projections,
)


def test_build_local_projection_data_creates_forward_cumulative_returns():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "ticker": ["SPY", "SPY", "SPY"],
            "country": ["United States"] * 3,
            "market_group": ["developed"] * 3,
            "return": [0.01, 0.02, -0.03],
            "gpr_shock": [True, False, False],
        }
    )

    projection_data = build_local_projection_data(panel, max_horizon=1)

    assert projection_data.columns.tolist() == [
        "horizon",
        "date",
        "ticker",
        "country",
        "market_group",
        "cumulative_return",
        "gpr_shock",
        "emerging_market",
    ]
    same_day = projection_data.loc[
        (projection_data["date"] == pd.Timestamp("2024-01-01"))
        & (projection_data["horizon"] == 0)
    ].iloc[0]
    next_day = projection_data.loc[
        (projection_data["date"] == pd.Timestamp("2024-01-01"))
        & (projection_data["horizon"] == 1)
    ].iloc[0]

    assert same_day["cumulative_return"] == 0.01
    assert next_day["cumulative_return"] == 0.03
    assert same_day["gpr_shock"] == 1
    assert same_day["emerging_market"] == 0


def test_estimate_local_projections_returns_group_responses_by_horizon():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-04",
                ]
            ),
            "ticker": ["SPY", "EWZ"] * 4,
            "country": ["United States", "Brazil"] * 4,
            "market_group": ["developed", "emerging"] * 4,
            "return": [0.01, -0.02, 0.03, -0.01, 0.02, -0.03, 0.01, -0.02],
            "gpr_shock": [True, True, False, False, True, True, False, False],
        }
    )

    results = estimate_local_projections(
        panel,
        max_horizon=1,
        cluster_by_ticker=False,
    )

    assert results.columns.tolist() == [
        "horizon",
        "market_group",
        "estimate",
        "std_error",
        "ci_low",
        "ci_high",
        "p_value",
    ]
    assert set(results["horizon"]) == {0, 1}
    assert set(results["market_group"]) == {"developed", "emerging"}


def test_estimate_local_projections_drops_missing_control_rows_before_clustering():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-04",
                ]
            ),
            "ticker": ["SPY", "EWZ"] * 4,
            "country": ["United States", "Brazil"] * 4,
            "market_group": ["developed", "emerging"] * 4,
            "return": [0.01, -0.02, 0.03, -0.01, 0.02, -0.03, 0.01, -0.02],
            "gpr_shock": [True, True, False, False, True, True, False, False],
            "global_market_return": [None, None, 0.02, 0.02, -0.01, -0.01, 0.03, 0.03],
            "vix_change": [None, None, -1.0, -1.0, 0.5, 0.5, -0.5, -0.5],
            "oil_change": [None, None, -1.0, -1.0, 2.0, 2.0, -2.0, -2.0],
            "dollar_return": [None, None, -0.002, -0.002, 0.003, 0.003, -0.004, -0.004],
            "us10y_change": [None, None, -0.1, -0.1, 0.2, 0.2, -0.2, -0.2],
        }
    )

    results = estimate_local_projections(
        panel,
        max_horizon=0,
        include_controls=True,
        cluster_by_ticker=True,
    )

    assert len(results) == 2
