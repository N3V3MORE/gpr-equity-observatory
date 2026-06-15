import pandas as pd

from gprobs.analysis.event_study import (
    build_event_windows,
    build_market_model_event_windows,
    select_peak_cluster_events,
    select_spaced_events,
    summarize_abnormal_event_windows,
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


def test_select_peak_cluster_events_keeps_largest_gpr_change_in_nearby_cluster():
    gpr = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-05", "2024-01-10", "2024-01-30"]),
            "gpr_shock": [True, True, True, True],
            "gpr_change": [20.0, 80.0, 40.0, 30.0],
        }
    )

    events = select_peak_cluster_events(gpr, min_gap_days=20)

    assert events.tolist() == [pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-30")]


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


def test_build_market_model_event_windows_calculates_abnormal_returns():
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
            "region": ["North America"] * 5,
            "return": [0.03, 0.05, 0.07, 0.11, 0.13],
            "global_market_return": [0.01, 0.02, 0.03, 0.04, 0.05],
        }
    )

    windows = build_market_model_event_windows(
        panel,
        event_dates=pd.to_datetime(["2024-01-04"]),
        window=1,
        estimation_window=2,
        estimation_gap=1,
        min_estimation_obs=2,
    )

    assert windows["relative_day"].tolist() == [-1, 0, 1]
    assert round(windows.loc[0, "expected_return"], 10) == 0.07
    assert round(windows.loc[0, "abnormal_return"], 10) == 0.0
    assert round(windows.loc[1, "abnormal_return"], 10) == 0.02


def test_summarize_abnormal_event_windows_cumsums_abnormal_returns():
    windows = pd.DataFrame(
        {
            "event_date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
            "market_group": ["developed", "developed"],
            "relative_day": [-1, 0],
            "abnormal_return": [0.01, -0.03],
        }
    )

    summary = summarize_abnormal_event_windows(windows)

    assert summary.columns.tolist() == [
        "market_group",
        "relative_day",
        "average_abnormal_return",
        "cumulative_average_abnormal_return",
        "observation_count",
        "event_count",
    ]
    assert round(summary.loc[1, "cumulative_average_abnormal_return"], 10) == -0.02
