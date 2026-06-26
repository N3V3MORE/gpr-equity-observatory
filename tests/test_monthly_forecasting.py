import numpy as np
import pandas as pd
import pytest

from gprobs.analysis.forecast_metrics import evaluate_forecasts
from gprobs.analysis.forecasting import (
    ForecastModelSpec,
    expanding_window_forecast,
    forecast_metric_row,
    forecast_metric_rows,
    iter_expanding_window_frames,
)
from gprobs.analysis.time_splits import make_time_splits
from gprobs.data.datasets import MONTHLY_BENCHMARK_SAMPLE
from gprobs.data.monthly_sample import build_monthly_benchmark_sample
from gprobs.project_paths import ProjectPaths
from gprobs.reporting.outputs import table_path
from scripts.run_monthly_benchmark_forecasts import run_monthly_benchmark_forecasts


def test_make_time_splits_uses_future_test_windows():
    dates = pd.Series(pd.date_range("2020-01-01", periods=6, freq="MS"))

    splits = make_time_splits(dates, min_train_months=3, test_window=2)

    assert len(splits) == 2
    assert splits[0].train_dates[-1] == pd.Timestamp("2020-03-01")
    assert splits[0].test_dates == [pd.Timestamp("2020-04-01"), pd.Timestamp("2020-05-01")]


def test_make_time_splits_rejects_unsorted_dates():
    dates = pd.Series(pd.to_datetime(["2020-02-01", "2020-01-01"]))

    with pytest.raises(ValueError, match="increasing"):
        make_time_splits(dates, min_train_months=1, test_window=1)


def test_evaluate_forecasts_regression_metrics_and_oos_r2():
    metrics = evaluate_forecasts(
        [1.0, 2.0, 3.0],
        [1.0, 2.5, 2.5],
        task="regression",
        benchmark_pred=[2.0, 2.0, 2.0],
    )

    assert metrics["rmse"] == pytest.approx(np.sqrt(0.5 / 3))
    assert metrics["mae"] == pytest.approx(1 / 3)
    assert "oos_r2" in metrics


def test_expanding_window_forecast_standardizes_without_future_leakage():
    df = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=5, freq="MS"),
            "target": [1.0, 2.0, 3.0, 4.0, 5.0],
            "shock": [10.0, 20.0, 30.0, 40.0, 1000.0],
        }
    )

    forecasts = expanding_window_forecast(
        df,
        "target",
        ["shock"],
        min_train_months=2,
        standardize_feature_cols=["shock"],
        standardize_min_periods=2,
    )

    assert "benchmark_predicted" in forecasts.columns
    assert forecasts["benchmark_predicted"].iloc[0] == pytest.approx(3.5)


def test_iter_expanding_window_frames_uses_positional_windows():
    df = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=5, freq="MS"),
            "target": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    )

    windows = list(iter_expanding_window_frames(df, min_train_months=2, test_window=2))

    assert len(windows) == 2
    assert windows[0][0]["target"].tolist() == [1.0, 2.0]
    assert windows[0][1]["target"].tolist() == [3.0, 4.0]
    assert windows[1][0]["target"].tolist() == [1.0, 2.0, 3.0, 4.0]
    assert windows[1][1]["target"].tolist() == [5.0]


def test_forecast_metric_rows_aligns_models_to_common_historical_mean_benchmark():
    df = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=8, freq="MS"),
            "target": [1.0, 1.5, 2.0, 2.5, 2.7, 3.0, 3.2, 3.4],
            "shock": [10.0, 11.0, 13.0, 15.0, 16.0, 18.0, 21.0, 23.0],
        }
    )

    rows = forecast_metric_rows(
        df,
        "target",
        [
            ForecastModelSpec("historical_mean", []),
            ForecastModelSpec("shock_model", ["shock"], standardize_feature_cols=["shock"], standardize_min_periods=2),
        ],
        min_train_months=2,
    )

    by_model = {row["model"]: row for row in rows}
    assert by_model["historical_mean"]["oos_r2"] == 0.0
    assert by_model["shock_model"]["benchmark_model"] == "historical_mean"
    assert {row["n_forecasts"] for row in rows} == {4}
    assert {row["first_forecast_date"] for row in rows} == {"2020-05-01"}
    assert {row["last_forecast_date"] for row in rows} == {"2020-08-01"}


def test_forecast_metric_row_historical_mean_oos_r2_is_zero():
    df = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=5, freq="MS"),
            "target": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    )

    metrics = forecast_metric_row("historical_mean", df, "target", [], 3)

    assert metrics["oos_r2"] == 0.0
    assert metrics["n_forecasts"] == 2


def test_run_monthly_benchmark_forecasts_writes_monthly_namespaced_table(tmp_path):
    build_monthly_benchmark_sample(root=tmp_path)

    run_monthly_benchmark_forecasts(MONTHLY_BENCHMARK_SAMPLE, root=tmp_path, min_train_months=24)

    paths = ProjectPaths(tmp_path)
    output = table_path(paths, "table_03_forecast_comparison.csv", MONTHLY_BENCHMARK_SAMPLE)
    table = pd.read_csv(output)

    assert output.exists()
    assert not (tmp_path / "reports" / "tables" / "table_03_forecast_comparison.csv").exists()
    assert table["model"].tolist() == [
        "historical_mean",
        "macro_only",
        "macro_plus_gpr",
        "macro_plus_gpr_gdelt",
        "regularized_linear",
    ]
    assert table["forecast_window_aligned"].all()
