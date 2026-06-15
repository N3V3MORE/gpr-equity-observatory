import pandas as pd

from gprobs.analysis.local_projection import (
    build_local_projection_data,
    estimate_local_projections,
)


def test_build_local_projection_data_creates_forward_cumulative_abnormal_returns():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                ]
            ),
            "ticker": ["SPY"] * 5,
            "country": ["United States"] * 5,
            "market_group": ["developed"] * 5,
            "return": [0.01, 0.02, -0.01, 0.03, 0.01],
            "global_market_return": [0.01, 0.02, 0.01, 0.02, 0.01],
            "gpr_shock": [False, False, True, False, False],
        }
    )

    projection_data = build_local_projection_data(
        panel,
        max_horizon=1,
        estimation_window=2,
        estimation_gap=0,
        min_estimation_obs=2,
    )

    assert projection_data.columns.tolist() == [
        "horizon",
        "date",
        "ticker",
        "country",
        "market_group",
        "cumulative_abnormal_return",
        "gpr_shock",
        "emerging_market",
    ]
    same_day = projection_data.loc[
        (projection_data["date"] == pd.Timestamp("2024-01-03"))
        & (projection_data["horizon"] == 0)
    ].iloc[0]
    next_day = projection_data.loc[
        (projection_data["date"] == pd.Timestamp("2024-01-03"))
        & (projection_data["horizon"] == 1)
    ].iloc[0]

    assert round(same_day["cumulative_abnormal_return"], 10) == -0.02
    assert round(next_day["cumulative_abnormal_return"], 10) == -0.01
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
                    "2024-01-05",
                    "2024-01-05",
                    "2024-01-06",
                    "2024-01-06",
                ]
            ),
            "ticker": ["SPY", "EWZ"] * 6,
            "country": ["United States", "Brazil"] * 6,
            "market_group": ["developed", "emerging"] * 6,
            "return": [0.01, 0.02, 0.02, 0.01, -0.01, -0.02, 0.03, 0.01, 0.02, -0.01, 0.01, 0.00],
            "global_market_return": [0.01, 0.01, 0.02, 0.02, 0.01, 0.01, 0.02, 0.02, 0.01, 0.01, 0.02, 0.02],
            "gpr_shock": [False, False, False, False, True, True, False, False, True, True, False, False],
        }
    )

    results = estimate_local_projections(
        panel,
        max_horizon=1,
        estimation_window=2,
        estimation_gap=0,
        min_estimation_obs=2,
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
                    "2024-01-05",
                    "2024-01-05",
                    "2024-01-06",
                    "2024-01-06",
                ]
            ),
            "ticker": ["SPY", "EWZ"] * 6,
            "country": ["United States", "Brazil"] * 6,
            "market_group": ["developed", "emerging"] * 6,
            "return": [0.01, 0.02, 0.02, 0.01, -0.01, -0.02, 0.03, 0.01, 0.02, -0.01, 0.01, 0.00],
            "gpr_shock": [False, False, False, False, True, True, False, False, True, True, False, False],
            "global_market_return": [0.01, 0.01, 0.02, 0.02, 0.01, 0.01, 0.02, 0.02, 0.01, 0.01, 0.02, 0.02],
            "vix_change": [None, None, -1.0, -1.0, 0.5, 0.5, -0.5, -0.5, 0.2, 0.2, -0.2, -0.2],
            "oil_change": [None, None, -1.0, -1.0, 2.0, 2.0, -2.0, -2.0, 1.0, 1.0, -1.0, -1.0],
            "dollar_return": [None, None, -0.002, -0.002, 0.003, 0.003, -0.004, -0.004, 0.002, 0.002, -0.001, -0.001],
            "us10y_change": [None, None, -0.1, -0.1, 0.2, 0.2, -0.2, -0.2, 0.1, 0.1, -0.1, -0.1],
        }
    )

    results = estimate_local_projections(
        panel,
        max_horizon=0,
        include_controls=True,
        estimation_window=2,
        estimation_gap=0,
        min_estimation_obs=2,
        cluster_by_ticker=True,
    )

    assert len(results) == 2


def test_estimate_local_projections_uses_abnormal_returns_instead_of_raw_market_drift():
    rows = []
    dates = pd.date_range("2024-01-01", periods=8)
    market_returns = [0.01, 0.02, 0.05, 0.00, 0.05, 0.00, 0.05, 0.00]
    shocks = [False, False, True, False, True, False, True, False]
    for ticker, country, market_group in [
        ("SPY", "United States", "developed"),
        ("EWZ", "Brazil", "emerging"),
    ]:
        for date, market_return, shock in zip(dates, market_returns, shocks, strict=True):
            abnormal_return = -0.01 if shock else 0.0
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "country": country,
                    "market_group": market_group,
                    "return": market_return + abnormal_return,
                    "global_market_return": market_return,
                    "gpr_shock": shock,
                }
            )
    panel = pd.DataFrame(rows)

    results = estimate_local_projections(
        panel,
        max_horizon=0,
        estimation_window=2,
        estimation_gap=0,
        min_estimation_obs=2,
        cluster_by_ticker=False,
    )

    developed = results.loc[
        (results["horizon"] == 0) & (results["market_group"] == "developed")
    ].iloc[0]
    assert developed["estimate"] < 0
