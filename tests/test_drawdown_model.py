import pandas as pd

from gprobs.analysis.drawdown_model import (
    DEFAULT_FEATURE_COLUMNS,
    build_drawdown_dataset,
    evaluate_drawdown_classifier,
    fit_drawdown_feature_importance,
)


def test_build_drawdown_dataset_uses_future_returns_for_target():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
            ),
            "ticker": ["SPY"] * 4,
            "country": ["United States"] * 4,
            "market_group": ["developed"] * 4,
            "return": [0.01, -0.03, -0.04, 0.02],
            "gpr": [100.0, 120.0, 130.0, 110.0],
            "gpr_change": [0.0, 20.0, 10.0, -20.0],
            "gpr_change_shock_expanding": [False, True, False, False],
            "global_market_return": [0.01, -0.01, -0.02, 0.01],
            "vix_change": [0.1, 1.0, 0.5, -0.2],
            "oil_change": [1.0, -1.0, -0.5, 0.2],
            "dollar_return": [0.001, 0.002, -0.001, 0.0],
            "us10y_change": [0.1, -0.1, 0.0, 0.1],
        }
    )

    dataset = build_drawdown_dataset(panel, horizon=2, threshold=-0.05, volatility_window=2)

    first_row = dataset.loc[dataset["date"] == pd.Timestamp("2024-01-01")].iloc[0]
    second_row = dataset.loc[dataset["date"] == pd.Timestamp("2024-01-02")].iloc[0]

    assert first_row["forward_min_return"] == -0.07
    assert first_row["drawdown_risk"] == 1
    assert second_row["forward_min_return"] == -0.04
    assert second_row["drawdown_risk"] == 0
    assert dataset["date"].tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-01-02"),
    ]
    assert "lag_return_1d" in dataset.columns
    assert "rolling_volatility" in dataset.columns
    assert "gpr_change_z" in dataset.columns
    assert "gpr_z" not in dataset.columns
    assert "gpr_change_shock_expanding" in dataset.columns


def test_evaluate_drawdown_classifier_uses_chronological_folds():
    dataset = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                    "2024-01-06",
                    "2024-01-07",
                    "2024-01-08",
                ]
            ),
            "drawdown_risk": [0, 1, 0, 1, 0, 1, 0, 1],
            "gpr_change_z": [-1.0, 0.2, -0.8, 0.4, -0.5, 0.8, -0.2, 1.0],
            "gpr_change_shock_expanding": [0, 1, 0, 1, 0, 1, 0, 1],
            "global_market_return": [0.01, -0.01, 0.02, -0.02, 0.01, -0.01, 0.02, -0.02],
            "vix_change": [-1.0, 1.0, -0.5, 0.5, -1.0, 1.0, -0.5, 0.5],
            "oil_change": [1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0],
            "dollar_return": [0.001, 0.002, 0.001, 0.002, 0.001, 0.002, 0.001, 0.002],
            "us10y_change": [0.1, -0.1, 0.1, -0.1, 0.1, -0.1, 0.1, -0.1],
            "lag_return_1d": [0.01, -0.01, 0.02, -0.02, 0.01, -0.01, 0.02, -0.02],
            "rolling_volatility": [0.01] * 8,
            "emerging_market": [0, 0, 1, 1, 0, 0, 1, 1],
        }
    )

    metrics = evaluate_drawdown_classifier(dataset, n_splits=2, embargo_dates=1)

    assert metrics.columns.tolist() == [
        "fold",
        "model_name",
        "train_start",
        "train_end",
        "test_start",
        "test_end",
        "roc_auc",
        "average_precision",
        "base_rate",
        "observation_count",
    ]
    assert set(metrics["model_name"]) == {"constant_baseline", "volatility_only", "full_features"}
    assert (metrics["train_end"] < metrics["test_start"]).all()
    first_fold = metrics.loc[metrics["fold"] == 1].iloc[0]
    assert first_fold["train_end"] == pd.Timestamp("2024-01-01")
    assert first_fold["test_start"] == pd.Timestamp("2024-01-03")


def test_fit_drawdown_feature_importance_returns_one_row_per_feature():
    dataset = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=12),
            "drawdown_risk": [0, 1] * 6,
            "gpr_change_z": [-1.0, 1.0] * 6,
            "gpr_change_shock_expanding": [0, 1] * 6,
            "global_market_return": [0.01, -0.01] * 6,
            "vix_change": [-1.0, 1.0] * 6,
            "oil_change": [1.0, -1.0] * 6,
            "dollar_return": [0.001, 0.002] * 6,
            "us10y_change": [0.1, -0.1] * 6,
            "lag_return_1d": [0.01, -0.01] * 6,
            "rolling_volatility": [0.01] * 12,
            "emerging_market": [0, 1] * 6,
        }
    )

    importance = fit_drawdown_feature_importance(dataset)

    assert set(importance["feature"]) == set(DEFAULT_FEATURE_COLUMNS)
    assert len(importance) == len(DEFAULT_FEATURE_COLUMNS)
    assert importance["abs_coefficient"].is_monotonic_decreasing
