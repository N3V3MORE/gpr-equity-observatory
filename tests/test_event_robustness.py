import pandas as pd

from gprobs.analysis.event_robustness import (
    build_event_robustness_table,
    summarize_window_endpoint,
)


def test_summarize_window_endpoint_keeps_final_relative_day_by_group():
    summary = pd.DataFrame(
        {
            "market_group": ["developed", "developed", "emerging", "emerging"],
            "relative_day": [-1, 1, -1, 1],
            "cumulative_average_abnormal_return": [0.01, -0.02, 0.03, -0.04],
            "event_count": [5, 5, 5, 5],
        }
    )

    endpoint = summarize_window_endpoint(
        summary,
        shock_quantile=0.95,
        window=1,
    )

    assert endpoint.columns.tolist() == [
        "shock_quantile",
        "window",
        "market_group",
        "cumulative_average_abnormal_return",
        "event_count",
    ]
    assert endpoint["market_group"].tolist() == ["developed", "emerging"]
    assert endpoint["cumulative_average_abnormal_return"].tolist() == [-0.02, -0.04]


def test_build_event_robustness_table_returns_grid_summary():
    panel = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10).tolist() * 2,
            "ticker": ["SPY"] * 10 + ["EWZ"] * 10,
            "country": ["United States"] * 10 + ["Brazil"] * 10,
            "market_group": ["developed"] * 10 + ["emerging"] * 10,
            "region": ["North America"] * 10 + ["Latin America"] * 10,
            "return": [0.01, 0.02, 0.01, -0.01, 0.02, 0.03, 0.01, -0.02, 0.01, 0.02] * 2,
            "global_market_return": [0.01, 0.01, 0.02, -0.01, 0.01, 0.02, 0.01, -0.01, 0.01, 0.02] * 2,
        }
    )
    gpr = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10),
            "gpr": [10, 20, 30, 40, 50, 200, 201, 202, 260, 261],
        }
    )

    robustness = build_event_robustness_table(
        panel,
        gpr,
        shock_quantiles=[0.80],
        windows=[1],
        min_gap_days=1,
        estimation_window=2,
        estimation_gap=1,
        min_estimation_obs=2,
    )

    assert set(robustness["market_group"]) == {"developed", "emerging"}
    assert robustness["shock_quantile"].tolist() == [0.80, 0.80]
    assert robustness["window"].tolist() == [1, 1]
