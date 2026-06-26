import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from gprobs.data.datasets import MONTHLY_BENCHMARK_SAMPLE, dataset_files
from gprobs.data.monthly_sample import build_monthly_benchmark_sample
from gprobs.project_paths import ProjectPaths


def test_build_monthly_benchmark_sample_writes_sources_panel_and_manifests(tmp_path):
    build_monthly_benchmark_sample(root=tmp_path)

    paths = ProjectPaths(tmp_path)
    files = dataset_files(MONTHLY_BENCHMARK_SAMPLE)

    for filename in [
        files.gpr,
        files.market_returns,
        files.gdelt,
        files.macro,
        files.analysis_panel,
    ]:
        assert (paths.data_processed / filename).exists()

    source_manifest = json.loads(
        (paths.data_metadata / files.source_manifest).read_text(encoding="utf-8")
    )
    analysis_manifest = json.loads(
        (paths.data_metadata / files.analysis_manifest).read_text(encoding="utf-8")
    )
    panel = pd.read_csv(paths.data_processed / files.analysis_panel)

    assert source_manifest["manifest_type"] == "source_collection"
    assert source_manifest["sources"][0]["source_name"] == "Monthly benchmark deterministic sample"
    assert analysis_manifest["dataset_mode"] == MONTHLY_BENCHMARK_SAMPLE
    assert analysis_manifest["row_count"] == len(panel)
    assert set(panel["market_id"]) == {"developed", "emerging"}
    assert {"gpr_change_z", "gdelt_risk_z", "sample_global_cycle", "ret_fwd_1m"}.issubset(
        panel.columns
    )


def test_build_monthly_benchmark_sample_script_writes_to_requested_root(tmp_path):
    root = Path(__file__).resolve().parents[1]

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_monthly_benchmark_sample.py",
            "--root",
            str(tmp_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    files = dataset_files(MONTHLY_BENCHMARK_SAMPLE)
    assert (tmp_path / "data" / "processed" / files.analysis_panel).exists()
