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
    assert payloads["manifest"]["schema_version"] == 1
    assert payloads["manifest"]["profile"] == "local"
    assert payloads["manifest"]["datasets"] == sorted(set(payloads) - {"manifest"})
    assert payloads["manifest"]["country_count"] == 1
    assert payloads["copy"]["central_question"]
    assert payloads["copy"]["reader_path"] == [
        {
            "step": "1",
            "title": "Start with the question",
            "body": "The dashboard asks whether geopolitical risk jumps are associated with country ETF returns.",
        },
        {
            "step": "2",
            "title": "Look at the graphs",
            "body": "Use the GPR timeline and market-reaction charts before reading statistical tables.",
        },
        {
            "step": "3",
            "title": "Check the evidence labels",
            "body": "Weak or mixed evidence is a result; it is not a failed dashboard.",
        },
    ]
    assert payloads["copy"]["glossary"]
    assert "validates the monthly benchmark workflow" in payloads["copy"]["monthly_notices"]["sample"]
    assert "proves" not in payloads["copy"]["monthly_notices"]["sample"].lower()
    assert isinstance(payloads["overview"]["headline"]["country_count"], int)
    assert isinstance(payloads["gpr_timeline"]["series"], list)
    assert isinstance(payloads["evidence_map"], list)
    assert payloads["reader_summaries"]["output_files"]
    assert payloads["reader_summaries"]["market_reaction"][0]["plain_note"]
    assert payloads["reader_summaries"]["regression_translation"][0]["test"]
    assert isinstance(payloads["prediction_summary"]["model_comparison"], list)
    assert payloads["monthly"]["available"] is False


def test_quantile_export_keeps_both_gpr_terms_at_every_percentile(tmp_path):
    _write_minimal_processed(tmp_path)
    expected_rows = []
    nuisance_rows = []
    for quantile in [0.1, 0.5, 0.9]:
        for term, estimate in [
            ("gpr_change_z", -0.001),
            ("gpr_change_z:emerging_market", 0.002),
            ("Intercept", 0.1),
            ("C(ticker)[T.EWZ]", 0.2),
            ("global_market_return", 0.3),
        ]:
            row = {
                "quantile": quantile,
                "term": term,
                "estimate": estimate,
                "std_error": 0.003,
                "t_stat": 0.4,
                "p_value": 0.6,
                "inference": "weak evidence",
            }
            if term.startswith("gpr_change_z"):
                expected_rows.append(row)
            else:
                nuisance_rows.append(row)
    source_path = tmp_path / OUTPUT_SPECS["quantile_regression"].path.relative_to(export.PROJECT_ROOT)
    pd.DataFrame(nuisance_rows + expected_rows).to_csv(source_path, index=False)

    payloads = export.build_frontend_payloads(root=tmp_path)

    assert payloads["quantile_regression"] == expected_rows


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
        "reader_summaries.json",
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
    assert payloads["manifest"]["schema_version"] == 1
    assert payloads["manifest"]["profile"] == "local"
    assert payloads["manifest"]["datasets"] == ["copy"]
    assert payloads["manifest"]["missing_files"]
    assert payloads["copy"]["central_question"]
