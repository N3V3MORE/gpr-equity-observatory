import argparse
from pathlib import Path

import pandas as pd

from gprobs.analysis.monthly_benchmark import run_spread_regression
from gprobs.data.datasets import MONTHLY_BENCHMARK_REAL, MONTHLY_BENCHMARK_SAMPLE, dataset_files
from gprobs.project_paths import get_project_paths
from gprobs.reporting.outputs import table_path


def run_monthly_benchmark_regressions(
    dataset: str = MONTHLY_BENCHMARK_SAMPLE,
    root: Path | None = None,
    horizons: list[int] | None = None,
) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    files = dataset_files(dataset)
    panel = pd.read_csv(paths.data_processed / files.analysis_panel, parse_dates=["date_month"])
    controls = ["sample_global_cycle"] if dataset == MONTHLY_BENCHMARK_SAMPLE else []
    rows = []
    for horizon in horizons or [1, 3, 6]:
        result = run_spread_regression(panel, horizon=horizon, shock_col="gpr_change_z", controls=controls)
        rows.append(result.to_frame())

    output = table_path(paths, "table_02_baseline_regressions.csv", dataset)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.concat(rows, ignore_index=True).round(6).to_csv(output, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run monthly benchmark regressions.")
    parser.add_argument(
        "--dataset",
        choices=[MONTHLY_BENCHMARK_SAMPLE, MONTHLY_BENCHMARK_REAL],
        default=MONTHLY_BENCHMARK_SAMPLE,
    )
    parser.add_argument("--root", default=None)
    parser.add_argument("--horizons", default="1,3,6")
    args = parser.parse_args()
    run_monthly_benchmark_regressions(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
        horizons=_parse_horizons(args.horizons),
    )


def _parse_horizons(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


if __name__ == "__main__":
    main()
