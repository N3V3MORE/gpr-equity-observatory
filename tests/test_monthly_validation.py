import pandas as pd
import pytest

from gprobs.data.datasets import MONTHLY_BENCHMARK_SAMPLE
from gprobs.data.monthly_sample import build_monthly_benchmark_sample
from gprobs.project_paths import ProjectPaths
from gprobs.reporting.outputs import table_path
from scripts.run_monthly_benchmark_forecasts import run_monthly_benchmark_forecasts
from scripts.run_monthly_benchmark_regressions import run_monthly_benchmark_regressions
from scripts.validate_monthly_benchmark import validate_monthly_benchmark


def test_validate_monthly_benchmark_sample_writes_missingness_report(tmp_path):
    build_monthly_benchmark_sample(root=tmp_path)

    validate_monthly_benchmark(MONTHLY_BENCHMARK_SAMPLE, root=tmp_path)

    paths = ProjectPaths(tmp_path)
    output = table_path(paths, "table_00_missingness.csv", MONTHLY_BENCHMARK_SAMPLE)
    report = pd.read_csv(output)

    assert output.exists()
    assert {"column", "missing_count", "missing_share"}.issubset(report.columns)
    assert "ret_fwd_1m" in report["column"].tolist()


def test_validate_monthly_benchmark_rejects_missing_source_manifest(tmp_path):
    build_monthly_benchmark_sample(root=tmp_path)
    paths = ProjectPaths(tmp_path)
    source_manifest = paths.data_metadata / "monthly_benchmark" / "source_manifest.json"
    source_manifest.unlink()

    with pytest.raises(FileNotFoundError, match="source_manifest"):
        validate_monthly_benchmark(MONTHLY_BENCHMARK_SAMPLE, root=tmp_path)


def test_validate_monthly_benchmark_check_results_validates_model_tables(tmp_path):
    build_monthly_benchmark_sample(root=tmp_path)
    run_monthly_benchmark_regressions(MONTHLY_BENCHMARK_SAMPLE, root=tmp_path, horizons=[1])
    run_monthly_benchmark_forecasts(MONTHLY_BENCHMARK_SAMPLE, root=tmp_path, min_train_months=24)

    validate_monthly_benchmark(MONTHLY_BENCHMARK_SAMPLE, root=tmp_path, check_results=True)

    paths = ProjectPaths(tmp_path)
    assert table_path(paths, "table_02_baseline_regressions.csv", MONTHLY_BENCHMARK_SAMPLE).exists()
    assert table_path(paths, "table_03_forecast_comparison.csv", MONTHLY_BENCHMARK_SAMPLE).exists()
