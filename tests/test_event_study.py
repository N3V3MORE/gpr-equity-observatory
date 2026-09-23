import pandas as pd
import pytest

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
        "std_error",
        "t_stat",
        "p_value",
    ]
    assert round(summary.loc[1, "cumulative_average_abnormal_return"], 10) == -0.02
    assert pd.isna(summary.loc[1, "p_value"])


def test_summarize_abnormal_event_windows_adds_cross_sectional_inference():
    windows = pd.DataFrame(
        {
            "event_date": pd.to_datetime(["2024-01-01"] * 4),
            "ticker": ["SPY", "EWZ", "SPY", "EWZ"],
            "market_group": ["developed", "developed", "developed", "developed"],
            "relative_day": [-1, -1, 0, 0],
            "abnormal_return": [0.01, 0.03, -0.02, -0.04],
        }
    )

    summary = summarize_abnormal_event_windows(windows)

    endpoint = summary.loc[summary["relative_day"] == 0].iloc[0]
    assert round(endpoint["cumulative_average_abnormal_return"], 10) == -0.01
    assert endpoint["std_error"] > 0
    assert endpoint["t_stat"] < 0
    assert 0 <= endpoint["p_value"] <= 1


def test_existing_car_estimates_and_unadjusted_inference_include_pre_event_days():
    # Four ETF-event paths, but only two common events: freeze the current
    # estimator, including its unadjusted inference, during presentation changes.
    paths = [
        ("2024-01-05", "A", [0.01, -0.005, 0.002]),
        ("2024-01-05", "B", [0.02, -0.01, -0.004]),
        ("2024-02-05", "A", [-0.01, 0.02, -0.003]),
        ("2024-02-05", "B", [0.005, -0.002, 0.006]),
    ]
    windows = pd.DataFrame([
        {
            "event_date": pd.Timestamp(event_date), "ticker": ticker,
            "market_group": "developed", "relative_day": day,
            "abnormal_return": value,
        }
        for event_date, ticker, values in paths
        for day, value in zip([-2, -1, 0], values, strict=True)
    ])

    summary = summarize_abnormal_event_windows(windows)

    assert summary["cumulative_average_abnormal_return"].tolist() == pytest.approx(
        [0.00625, 0.007, 0.00725]
    )
    assert summary["std_error"].tolist() == pytest.approx(
        [0.00625, 0.001779513042005, 0.000629152869606]
    )
    assert summary["p_value"].tolist() == pytest.approx(
        [0.39100221895577, 0.02925897900278, 0.00140305562648]
    )
    assert summary["observation_count"].tolist() == [4, 4, 4]
    assert summary["event_count"].tolist() == [2, 2, 2]
    # Day-0 CAR includes days -2 and -1; it is not the day-0 return.
    assert summary.iloc[-1]["average_abnormal_return"] == pytest.approx(0.00025)


def test_truncated_car_starts_at_each_etf_events_first_available_day():
    windows = pd.DataFrame({
        "event_date": pd.to_datetime(["2024-01-05"] * 5),
        "ticker": ["A", "A", "A", "B", "B"],
        "market_group": ["developed"] * 5,
        "relative_day": [-2, -1, 0, -1, 0],
        "abnormal_return": [0.01, -0.005, 0.002, -0.01, -0.004],
    })

    summary = summarize_abnormal_event_windows(windows)

    assert summary["cumulative_average_abnormal_return"].tolist() == pytest.approx(
        [0.01, -0.0025, -0.0035]
    )
    assert summary["observation_count"].tolist() == [1, 2, 2]
    assert summary["event_count"].tolist() == [1, 1, 1]


def test_documented_raw_pre_inception_alignment_is_not_silently_changed():
    # This is a known raw-window defect, not a desired future estimator contract.
    # Fixing it requires a separate research change and regenerated raw outputs.
    panel = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=3),
        "ticker": ["ETF"] * 3, "country": ["Test"] * 3,
        "market_group": ["developed"] * 3, "region": ["Test"] * 3,
        "return": [0.01, 0.02, 0.03], "global_market_return": [0.001, 0.002, 0.003],
    })
    events = pd.to_datetime(["2000-01-01"])

    raw = build_event_windows(panel, events, window=1)
    abnormal = build_market_model_event_windows(
        panel, events, window=1, estimation_window=2, estimation_gap=0, min_estimation_obs=2
    )

    assert raw["event_date"].eq(pd.Timestamp("2000-01-01")).all()
    assert raw["event_trading_date"].eq(pd.Timestamp("2024-01-01")).all()
    assert raw["relative_day"].tolist() == [0, 1]
    assert abnormal.empty
