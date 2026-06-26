import argparse
from pathlib import Path

import pandas as pd

from gprobs.analysis.forecasting import ForecastModelSpec, forecast_metric_rows
from gprobs.data.datasets import MONTHLY_BENCHMARK_REAL, MONTHLY_BENCHMARK_SAMPLE, dataset_files
from gprobs.project_paths import get_project_paths
from gprobs.reporting.outputs import table_path


def run_monthly_benchmark_forecasts(
    dataset: str = MONTHLY_BENCHMARK_SAMPLE,
    root: Path | None = None,
    min_train_months: int = 120,
) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    files = dataset_files(dataset)
    panel = pd.read_csv(paths.data_processed / files.analysis_panel, parse_dates=["date_month"])
    forecast_data = _forecast_dataset(panel, dataset)
    rows = forecast_metric_rows(
        forecast_data,
        "spread_fwd_1m",
        _model_specs(dataset),
        min_train_months=min_train_months,
    )
    output = table_path(paths, "table_03_forecast_comparison.csv", dataset)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).round(6).to_csv(output, index=False)


def _forecast_dataset(panel: pd.DataFrame, dataset: str) -> pd.DataFrame:
    target = (
        panel.pivot_table(index="date_month", columns="market_id", values="ret_fwd_1m")
        .assign(spread_fwd_1m=lambda frame: frame["emerging"] - frame["developed"])
        [["spread_fwd_1m"]]
        .reset_index()
    )
    feature_cols = (
        ["date_month", "sample_global_cycle", "gpr_global", "gdelt_risk_raw"]
        if dataset == MONTHLY_BENCHMARK_SAMPLE
        else ["date_month", "gpr_change"]
    )
    features = _month_level_features(panel, feature_cols)
    return target.merge(features, on="date_month").dropna()


def _model_specs(dataset: str) -> list[ForecastModelSpec]:
    if dataset == MONTHLY_BENCHMARK_REAL:
        return [
            ForecastModelSpec("historical_mean", []),
            ForecastModelSpec("gpr_only", ["gpr_change"], standardize_feature_cols=["gpr_change"]),
            ForecastModelSpec(
                "regularized_gpr_only",
                ["gpr_change"],
                ridge_alpha=1.0,
                standardize_feature_cols=["gpr_change"],
            ),
        ]
    return [
        ForecastModelSpec("historical_mean", []),
        ForecastModelSpec("macro_only", ["sample_global_cycle"]),
        ForecastModelSpec(
            "macro_plus_gpr",
            ["sample_global_cycle", "gpr_global"],
            standardize_feature_cols=["gpr_global"],
        ),
        ForecastModelSpec(
            "macro_plus_gpr_gdelt",
            ["sample_global_cycle", "gpr_global", "gdelt_risk_raw"],
            standardize_feature_cols=["gpr_global", "gdelt_risk_raw"],
        ),
        ForecastModelSpec(
            "regularized_linear",
            ["sample_global_cycle", "gpr_global", "gdelt_risk_raw"],
            ridge_alpha=1.0,
            standardize_feature_cols=["gpr_global", "gdelt_risk_raw"],
        ),
    ]


def _month_level_features(panel: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    value_cols = [column for column in feature_cols if column != "date_month"]
    uniqueness = panel.groupby("date_month")[value_cols].nunique(dropna=False)
    varying = uniqueness.gt(1).any(axis=1)
    if varying.any():
        sample = [pd.Timestamp(value).strftime("%Y-%m-%d") for value in uniqueness.index[varying][:5]]
        raise ValueError(f"forecast features must be unique within date_month; bad months: {sample}")
    return panel.drop_duplicates("date_month")[feature_cols]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run monthly benchmark forecasts.")
    parser.add_argument(
        "--dataset",
        choices=[MONTHLY_BENCHMARK_SAMPLE, MONTHLY_BENCHMARK_REAL],
        default=MONTHLY_BENCHMARK_SAMPLE,
    )
    parser.add_argument("--root", default=None)
    parser.add_argument("--min-train-months", type=int, default=120)
    args = parser.parse_args()
    run_monthly_benchmark_forecasts(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
        min_train_months=args.min_train_months,
    )


if __name__ == "__main__":
    main()
