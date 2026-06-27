import json
from pathlib import Path

import pandas as pd

from gprobs.dashboard import export
from gprobs.dashboard.contracts import OUTPUT_SPECS


def _placeholder_value(column: str) -> object:
    text_defaults = {
        "country": "USA",
        "ticker": "EWZ",
        "market_group": "emerging",
        "region": "Americas",
        "event": "",
        "model_name": "constant_baseline",
        "term": "gpr_change_z",
        "bucket": "top_10_percent",
        "feature": "gpr_change_z",
        "method": "Panel regression",
        "focus": "Emerging-market interaction",
        "unit": "score",
        "inference": "weak evidence",
        "plain_english": "No strong asymmetry evidence.",
        "scenario": "full_sample",
        "market_id": "emerging",
        "market_class": "emerging",
    }
    return text_defaults.get(column, "")


def _write_minimal_processed(root: Path) -> None:
    text_columns = {
        "country",
        "ticker",
        "market_group",
        "region",
        "event",
        "model_name",
        "term",
        "bucket",
        "feature",
        "method",
        "focus",
        "unit",
        "inference",
        "plain_english",
        "scenario",
        "market_id",
        "market_class",
    }
    processed = root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    for _name, spec in OUTPUT_SPECS.items():
        rows = []
        for offset in range(2):
            row: dict[str, object] = {}
            for column in spec.required_columns:
                if column in spec.date_columns:
                    row[column] = pd.Timestamp("2024-01-01") + pd.Timedelta(days=offset)
                elif column in text_columns:
                    row[column] = _placeholder_value(column)
                else:
                    row[column] = 0.0
            rows.append(row)
        df = pd.DataFrame(rows)
        # Use the same filename the exporter expects, re-rooted under tmp_path.
        target = root / spec.path.relative_to(export.PROJECT_ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(target, index=False)


def test_build_frontend_payloads_returns_available_manifest(tmp_path):
    _write_minimal_processed(tmp_path)

    payloads = export.build_frontend_payloads(root=tmp_path)

    assert payloads["manifest"]["available"] is True
    assert payloads["manifest"]["country_count"] == 1
    assert payloads["copy"]["central_question"]
    assert payloads["copy"]["glossary"]
    assert isinstance(payloads["overview"]["headline"]["country_count"], int)
    assert isinstance(payloads["gpr_timeline"]["series"], list)
    assert isinstance(payloads["evidence_map"], list)
    assert isinstance(payloads["prediction_summary"]["model_comparison"], list)
    assert payloads["monthly"]["available"] is False


def test_write_frontend_payloads_writes_json_files(tmp_path):
    _write_minimal_processed(tmp_path)
    target = tmp_path / "frontend" / "public" / "data"

    export.export_frontend_data(root=tmp_path, target_dir=target)

    expected_files = [
        "manifest.json",
        "copy.json",
        "overview.json",
        "gpr_timeline.json",
        "evidence_map.json",
        "prediction_summary.json",
        "monthly.json",
        "country_coverage.json",
    ]
    for name in expected_files:
        path = target / name
        assert path.exists(), f"{name} was not written"
        json.loads(path.read_text(encoding="utf-8"))


def test_build_frontend_payloads_handles_missing_data(tmp_path):
    payloads = export.build_frontend_payloads(root=tmp_path)

    assert payloads["manifest"]["available"] is False
    assert payloads["manifest"]["missing_files"]
    assert payloads["copy"]["central_question"]
