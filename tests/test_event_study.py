import pandas as pd

from gprobs.analysis.event_study import (
    build_event_windows,
    select_spaced_events,
    summarize_event_windows,
)


def test_select_spaced_events_keeps_shocks_at_least_gap_days_apart():
    gpr = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-05", "2024-01-25", "2024-02-01"]
            ),
            "gpr_shock": [True, True, True, False],
        }
    )

    events = select_spaced_events(gpr, min_gap_days=10)

    assert events.tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-01-25"),
    ]


def test_build_event_windows_aligns_weekend_event_to_next_trading_date():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-05", "2024-01-08", "2024-01-09"]),
            "ticker": ["SPY", "SPY", "SPY"],
            "country": ["United States", "United States", "United States"],
            "market_group": ["developed", "developed", "developed"],
            "region": ["North America", "North America", "North America"],
            "return": [0.01, -0.02, 0.03],
        }
    )
    event_dates = pd.to_datetime(["2024-01-06"])

    windows = build_event_windows(panel, event_dates, window=1)

    assert windows["event_date"].unique().tolist() == [pd.Timestamp("2024-01-06")]
    assert windows["event_trading_date"].unique().tolist() == [pd.Timestamp("2024-01-08")]
    assert windows["relative_day"].tolist() == [-1, 0, 1]


def test_summarize_event_windows_averages_then_cumsums_by_group():
    windows = pd.DataFrame(
        {
            "event_date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
            "market_group": ["developed", "developed"],
            "relative_day": [-1, 0],
            "return": [0.01, -0.02],
        }
    )

    summary = summarize_event_windows(windows)

    assert summary.columns.tolist() == [
        "market_group",
        "relative_day",
        "average_return",
        "cumulative_average_return",
        "observation_count",
        "event_count",
    ]
    assert summary.loc[1, "cumulative_average_return"] == -0.01
