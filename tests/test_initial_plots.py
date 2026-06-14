import pandas as pd

from gprobs.visuals.initial_plots import build_group_cumulative_returns


def test_build_group_cumulative_returns_pivots_groups_and_cumsums_returns():
    group_summary = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"]
            ),
            "market_group": ["developed", "emerging", "developed", "emerging"],
            "average_return": [0.01, -0.02, 0.03, 0.04],
            "country_count": [10, 10, 10, 10],
        }
    )

    cumulative = build_group_cumulative_returns(group_summary)

    assert cumulative.columns.tolist() == ["date", "developed", "emerging"]
    assert cumulative.loc[0, "developed"] == 0.01
    assert cumulative.loc[1, "developed"] == 0.04
    assert cumulative.loc[1, "emerging"] == 0.02
