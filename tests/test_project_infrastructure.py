import json

import pandas as pd
import pytest

from gprobs.data.datasets import (
    DAILY_ETF,
    MONTHLY_BENCHMARK_REAL,
    MONTHLY_BENCHMARK_SAMPLE,
    dataset_files,
    dataset_output_filename,
)
from gprobs.data.source_metadata import source_manifest, write_source_collection_manifest
from gprobs.project_paths import ProjectPaths
from gprobs.reporting.outputs import figure_path, report_path, table_path
from gprobs.validation.data_contracts import (
    assert_dates_are_month_start,
    assert_no_duplicate_keys,
    assert_no_future_leakage,
    ensure_columns,
    missingness_report,
    standardize_month_start,
)


def test_project_paths_are_rooted_and_create_output_dirs(tmp_path):
    paths = ProjectPaths(tmp_path)

    assert paths.data_raw == tmp_path / "data" / "raw"
    assert paths.data_interim == tmp_path / "data" / "interim"
    assert paths.data_processed == tmp_path / "data" / "processed"
    assert paths.data_metadata == tmp_path / "data" / "metadata"
    assert paths.reports_figures == tmp_path / "reports" / "figures"
    assert paths.reports_tables == tmp_path / "reports" / "tables"

    paths.ensure_output_dirs()

    assert paths.data_processed.is_dir()
    assert paths.data_metadata.is_dir()
    assert paths.reports_figures.is_dir()
    assert paths.reports_tables.is_dir()


def test_dataset_files_keep_daily_and_monthly_outputs_separate():
    daily = dataset_files(DAILY_ETF)
    sample = dataset_files(MONTHLY_BENCHMARK_SAMPLE)
    real = dataset_files(MONTHLY_BENCHMARK_REAL)

    assert daily.analysis_panel == "analysis_panel.csv"
    assert sample.analysis_panel == "monthly_benchmark/sample_analysis_panel.csv"
    assert real.analysis_panel == "monthly_benchmark/analysis_panel.csv"
    assert sample.source_manifest == "monthly_benchmark/source_manifest.json"
    assert real.source_manifest == "monthly_benchmark/source_manifest_real.json"


def test_dataset_output_filename_applies_mode_specific_namespacing():
    assert dataset_output_filename("summary.csv", DAILY_ETF) == "summary.csv"
    assert (
        dataset_output_filename("summary.csv", MONTHLY_BENCHMARK_SAMPLE)
        == "monthly_benchmark/sample_summary.csv"
    )
    assert (
        dataset_output_filename("summary.csv", MONTHLY_BENCHMARK_REAL)
        == "monthly_benchmark/summary_real.csv"
    )

    with pytest.raises(ValueError, match="unknown dataset mode"):
        dataset_output_filename("summary.csv", "unknown")


def test_output_paths_use_dataset_output_filename(tmp_path):
    paths = ProjectPaths(tmp_path)

    assert table_path(paths, "summary.csv", MONTHLY_BENCHMARK_SAMPLE) == (
        tmp_path / "reports" / "tables" / "monthly_benchmark" / "sample_summary.csv"
    )
    assert figure_path(paths, "overview.png", MONTHLY_BENCHMARK_REAL) == (
        tmp_path / "reports" / "figures" / "monthly_benchmark" / "overview_real.png"
    )
    assert report_path(paths, MONTHLY_BENCHMARK_REAL) == (
        tmp_path / "reports" / "monthly_benchmark" / "main_report_real.pdf"
    )


def test_source_manifest_hashes_local_files_and_leaves_urls_unhashed(tmp_path):
    raw_file = tmp_path / "source.csv"
    raw_file.write_text("date,value\n2024-01-01,1\n", encoding="utf-8")

    local_manifest = source_manifest(
        source_name="Example local source",
        source_url="https://example.com/source",
        raw_file_path=str(raw_file),
        license_or_terms_note="test terms",
        script_version="test-version",
    )
    remote_manifest = source_manifest(
        source_name="Example remote source",
        source_url="https://example.com/source.csv",
        raw_file_path="https://example.com/source.csv",
        license_or_terms_note="test terms",
        script_version="test-version",
    )

    assert len(local_manifest["file_hash_sha256"]) == 64
    assert remote_manifest["file_hash_sha256"] == ""
    assert local_manifest["download_timestamp_utc"].endswith("+00:00")


def test_write_source_collection_manifest_records_sources(tmp_path):
    output_path = tmp_path / "metadata" / "source_manifest.json"

    write_source_collection_manifest(
        output_path,
        sources=[{"source_name": "A"}, {"source_name": "B"}],
    )

    manifest = json.loads(output_path.read_text(encoding="utf-8"))
    assert manifest["manifest_type"] == "source_collection"
    assert [source["source_name"] for source in manifest["sources"]] == ["A", "B"]


def test_data_contract_helpers_validate_common_panel_contracts():
    data = pd.DataFrame(
        {
            "date": ["2024-01-15", "2024-01-15", "2024-02-01"],
            "ticker": ["SPY", "SPY", "EWZ"],
            "value": [1.0, None, 3.0],
        }
    )

    ensure_columns(data, ["date", "ticker"])
    assert standardize_month_start(data["date"]).tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
    ]
    missing = missingness_report(data)
    assert missing.loc[missing["column"] == "value", "missing_count"].iloc[0] == 1

    with pytest.raises(ValueError, match="missing required columns: missing"):
        ensure_columns(data, ["date", "missing"])
    with pytest.raises(ValueError, match="duplicate keys found"):
        assert_no_duplicate_keys(data, ["date", "ticker"])
    with pytest.raises(ValueError, match="not month-start"):
        assert_dates_are_month_start(data, "date")
    with pytest.raises(ValueError, match="test dates must be after all training dates"):
        assert_no_future_leakage(
            pd.Series(pd.to_datetime(["2024-02-01"])),
            pd.Series(pd.to_datetime(["2024-01-01"])),
        )
