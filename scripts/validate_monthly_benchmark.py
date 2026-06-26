import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from gprobs.data.datasets import MONTHLY_BENCHMARK_REAL, MONTHLY_BENCHMARK_SAMPLE, dataset_files
from gprobs.project_paths import get_project_paths
from gprobs.reporting.outputs import table_path
from gprobs.validation.data_contracts import (
    assert_dates_are_month_start,
    assert_no_duplicate_keys,
    ensure_columns,
    missingness_report,
)

EXPECTED_REAL_SOURCES = {
    "Caldara-Iacoviello GPR",
    "Kenneth French Developed Factors",
    "Kenneth French Emerging Factors",
}


def validate_monthly_benchmark(
    dataset: str = MONTHLY_BENCHMARK_SAMPLE,
    root: Path | None = None,
    *,
    min_overlap_months: int = 24,
    min_forecast_train_months: int = 24,
    check_results: bool = False,
) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    files = dataset_files(dataset)

    panel_path = paths.data_processed / files.analysis_panel
    source_manifest_path = paths.data_metadata / files.source_manifest
    analysis_manifest_path = paths.data_metadata / files.analysis_manifest
    for required_path in [panel_path, source_manifest_path, analysis_manifest_path]:
        if not required_path.exists():
            raise FileNotFoundError(f"{required_path.name} is missing")

    _validate_source_manifest(source_manifest_path, dataset)
    analysis_manifest = _validate_analysis_manifest(analysis_manifest_path, dataset)
    panel = pd.read_csv(panel_path, parse_dates=["date_month"])
    _validate_panel(panel)

    if dataset == MONTHLY_BENCHMARK_REAL:
        gpr = pd.read_csv(paths.data_processed / files.gpr, parse_dates=["date_month"])
        returns = pd.read_csv(paths.data_processed / files.market_returns, parse_dates=["date_month"])
        _validate_real_inputs(gpr, returns, min_overlap_months, min_forecast_train_months)
        _validate_real_panel(panel, gpr, returns, analysis_manifest)

    if check_results:
        _validate_result_outputs(paths, dataset)

    output = table_path(paths, "table_00_missingness.csv", dataset)
    output.parent.mkdir(parents=True, exist_ok=True)
    missingness_report(panel).to_csv(output, index=False)


def _validate_source_manifest(path: Path, dataset: str) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("manifest_type") != "source_collection":
        raise ValueError(f"{path.name} must be a source_collection manifest")
    sources = manifest.get("sources", [])
    if not sources:
        raise ValueError(f"{path.name} must list at least one source")

    if dataset == MONTHLY_BENCHMARK_REAL:
        names = {source.get("source_name") for source in sources}
        if names != EXPECTED_REAL_SOURCES:
            raise ValueError("source_manifest_real.json must list expected monthly real sources")
        for source in sources:
            if not source.get("file_hash_sha256"):
                raise ValueError("real source manifest entries must include a file hash")
            raw_file_path = str(source.get("raw_file_path", ""))
            if ":\\" in raw_file_path or raw_file_path.startswith("/"):
                raise ValueError("real source manifests must not expose local absolute paths")

    if dataset == MONTHLY_BENCHMARK_SAMPLE:
        names = {source.get("source_name") for source in sources}
        if "Monthly benchmark deterministic sample" not in names:
            raise ValueError("monthly sample source manifest must describe deterministic sample data")


def _validate_analysis_manifest(path: Path, dataset: str) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest_dataset = manifest.get("dataset_mode") or manifest.get("dataset")
    if manifest_dataset != dataset:
        raise ValueError(f"{path.name} must describe {dataset}")
    if manifest.get("row_count", 1) <= 0:
        raise ValueError(f"{path.name} must record a positive row_count")
    return manifest


def _validate_panel(panel: pd.DataFrame) -> None:
    ensure_columns(
        panel,
        [
            "date_month",
            "market_id",
            "market_class",
            "excess_return",
            "ret_fwd_1m",
            "gpr_change_z",
            "gdelt_risk_raw",
            "gdelt_risk_z",
        ],
    )
    assert_dates_are_month_start(panel, "date_month")
    assert_no_duplicate_keys(panel, ["date_month", "market_id"])
    _validate_forward_return_missingness(panel, [1, 3, 6])


def _validate_real_inputs(
    gpr: pd.DataFrame,
    returns: pd.DataFrame,
    min_overlap_months: int,
    min_forecast_train_months: int,
) -> None:
    ensure_columns(gpr, ["date_month", "gpr_global", "source_download_date"])
    ensure_columns(returns, ["date_month", "market_id", "return_usd", "risk_free_rate", "excess_return"])
    assert_no_duplicate_keys(gpr, ["date_month"])
    assert_no_duplicate_keys(returns, ["date_month", "market_id"])

    coverage = returns.groupby("date_month")["market_id"].agg(lambda values: set(values))
    if coverage.empty or not coverage.eq({"developed", "emerging"}).all():
        raise ValueError("returns must contain developed and emerging markets for every month")

    overlap = set(pd.to_datetime(gpr["date_month"])) & set(pd.to_datetime(returns["date_month"]))
    if len(overlap) < min_overlap_months:
        raise ValueError(f"GPR and returns overlap must include at least {min_overlap_months} months")
    usable_months = len(overlap) - 2
    if usable_months <= min_forecast_train_months:
        raise ValueError(
            "real GPR and returns overlap is too short for the configured forecast split: "
            f"{len(overlap)} overlap months leaves {usable_months} usable forecast rows"
        )

    _require_finite_numeric(gpr, ["gpr_global"], "real GPR")
    _require_finite_numeric(returns, ["return_usd", "risk_free_rate", "excess_return"], "real returns")


def _validate_real_panel(panel: pd.DataFrame, gpr: pd.DataFrame, returns: pd.DataFrame, manifest: dict) -> None:
    common_dates = set(pd.to_datetime(gpr["date_month"])) & set(pd.to_datetime(returns["date_month"]))
    panel_dates = set(pd.to_datetime(panel["date_month"]).drop_duplicates())
    if panel_dates != common_dates:
        raise ValueError("analysis panel dates must match the common GPR and returns sample")
    sample_columns = [column for column in panel.columns if column.startswith("sample_")]
    if sample_columns:
        raise ValueError(f"real analysis panel contains sample-named columns: {sample_columns}")
    if manifest.get("used_placeholder_gdelt"):
        for column in ["gdelt_risk_raw", "gdelt_risk_z"]:
            if not pd.to_numeric(panel[column], errors="raise").eq(0).all():
                raise ValueError(f"{column} must be zero when placeholder GDELT is recorded")
    if manifest.get("used_placeholder_macro") and "placeholder_macro_zero" not in panel.columns:
        raise ValueError("real placeholder macro manifest requires placeholder_macro_zero column")


def _validate_forward_return_missingness(panel: pd.DataFrame, horizons: list[int]) -> None:
    for horizon in horizons:
        column = f"ret_fwd_{horizon}m"
        if column not in panel.columns:
            continue
        for _, group in panel.sort_values("date_month").groupby("market_id"):
            missing = group[column].isna().to_numpy()
            allowed = [False] * max(len(group) - horizon, 0) + [True] * min(horizon, len(group))
            if missing.tolist() != allowed:
                raise ValueError(f"{column} missing values must be only the final horizon rows")


def _validate_result_outputs(paths, dataset: str) -> None:
    regression_path = table_path(paths, "table_02_baseline_regressions.csv", dataset)
    if not regression_path.exists():
        raise FileNotFoundError(f"{regression_path.name} is missing; run monthly regressions first")
    _validate_regression_outputs(pd.read_csv(regression_path))

    forecast_path = table_path(paths, "table_03_forecast_comparison.csv", dataset)
    if not forecast_path.exists():
        raise FileNotFoundError(f"{forecast_path.name} is missing; run monthly forecasts first")
    _validate_forecast_outputs(pd.read_csv(forecast_path))


def _validate_regression_outputs(regressions: pd.DataFrame) -> None:
    ensure_columns(regressions, ["horizon", "term", "estimate", "std_error", "t_value", "p_value", "nobs"])
    assert_no_duplicate_keys(regressions, ["horizon", "term"])
    _require_finite_numeric(
        regressions,
        ["estimate", "std_error", "t_value", "p_value", "nobs", "adjusted_r2"],
        "monthly regression table",
    )
    if pd.to_numeric(regressions["std_error"], errors="raise").lt(0).any():
        raise ValueError("monthly regression standard errors must be non-negative")


def _validate_forecast_outputs(forecasts: pd.DataFrame) -> None:
    ensure_columns(
        forecasts,
        [
            "model",
            "rmse",
            "mae",
            "oos_r2",
            "n_forecasts",
            "first_forecast_date",
            "last_forecast_date",
            "forecast_window_aligned",
        ],
    )
    assert_no_duplicate_keys(forecasts, ["model"])
    _require_finite_numeric(forecasts, ["rmse", "mae", "oos_r2", "n_forecasts"], "monthly forecast table")
    if pd.to_numeric(forecasts["n_forecasts"], errors="raise").le(0).any():
        raise ValueError("n_forecasts must be positive")
    windows = forecasts[["n_forecasts", "first_forecast_date", "last_forecast_date"]]
    if len(windows.drop_duplicates()) != 1:
        raise ValueError("forecast rows must use the same forecast evaluation dates")


def _require_finite_numeric(df: pd.DataFrame, columns: list[str], context: str) -> None:
    ensure_columns(df, columns)
    for column in columns:
        values = pd.to_numeric(df[column], errors="raise")
        if not np.isfinite(values.to_numpy(dtype=float)).all():
            raise ValueError(f"{context} column {column} must contain only finite numeric values")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate monthly benchmark data and result outputs.")
    parser.add_argument(
        "--dataset",
        choices=[MONTHLY_BENCHMARK_SAMPLE, MONTHLY_BENCHMARK_REAL],
        default=MONTHLY_BENCHMARK_SAMPLE,
    )
    parser.add_argument("--root", default=None)
    parser.add_argument("--min-overlap-months", type=int, default=24)
    parser.add_argument("--min-forecast-train-months", type=int, default=24)
    parser.add_argument("--check-results", action="store_true")
    args = parser.parse_args()
    validate_monthly_benchmark(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
        min_overlap_months=args.min_overlap_months,
        min_forecast_train_months=args.min_forecast_train_months,
        check_results=args.check_results,
    )


if __name__ == "__main__":
    main()
