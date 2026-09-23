import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

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
        _strict_json(path.read_text(encoding="utf-8"))


def _strict_json(text: str):
    def reject_constant(value: str):
        raise ValueError(f"Nonstandard JSON token: {value}")

    return json.loads(text, parse_constant=reject_constant)


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_strict_json_decoder_rejects_nonstandard_tokens(token):
    with pytest.raises(ValueError, match="Nonstandard JSON token"):
        _strict_json(f'{{"value": {token}}}')


@pytest.mark.parametrize("missing", [
    None, float("nan"), np.float32("nan"), np.float64("nan"), pd.NA, pd.NaT, np.datetime64("NaT"),
])
def test_writer_preserves_nested_missing_values_as_null_without_mutation(tmp_path, missing):
    row = {"missing": missing}
    rows = [row, [missing]]
    payloads = {"example": {"rows": rows}}

    export.write_frontend_payloads(payloads, tmp_path)

    assert _strict_json((tmp_path / "example.json").read_text(encoding="utf-8")) == {
        "rows": [{"missing": None}, [None]],
    }
    assert payloads["example"]["rows"] is rows
    assert rows[0] is row
    assert row["missing"] is missing
    assert rows[1][0] is missing


def test_writer_preserves_finite_scalars_types_and_existing_date_format(tmp_path):
    values = [
        0, -2, 2**63, 0.0, -0.0, 1.125, -2.5, True, False, "0", "NaN", "Infinity", "",
        np.int32(-3), np.int64(4), np.uint64(2**63), np.float32(1.25), np.float64(-1.5),
        np.float32(0), np.float64(-0.0), np.bool_(True), np.bool_(False),
        pd.Timestamp("2024-01-02T03:04:05"), np.datetime64("2024-01-03"),
    ]
    originals = values.copy()
    payloads = {"example": {"values": values, "tuple": (np.int64(0), False)}}

    export.write_frontend_payloads(payloads, tmp_path)

    result = _strict_json((tmp_path / "example.json").read_text(encoding="utf-8"))
    expected = [
        0, -2, 2**63, 0.0, -0.0, 1.125, -2.5, True, False, "0", "NaN", "Infinity", "",
        -3, 4, 2**63, 1.25, -1.5, 0.0, -0.0, True, False, "2024-01-02", "2024-01-03",
    ]
    assert result["values"] == expected
    assert [type(value) for value in result["values"]] == [type(value) for value in expected]
    assert math.copysign(1, result["values"][4]) == -1
    assert math.copysign(1, result["values"][19]) == -1
    assert result["tuple"] == [0, False]
    assert payloads["example"]["values"] is values
    assert all(value is original for value, original in zip(values, originals, strict=True))
    assert isinstance(payloads["example"]["tuple"], tuple)


@pytest.mark.parametrize("infinity", [
    float("inf"), float("-inf"), np.float32("inf"), np.float32("-inf"),
    np.float64("inf"), np.float64("-inf"),
])
def test_writer_rejects_unexpected_nested_infinity_with_payload_and_path(tmp_path, infinity):
    row = {"estimate": infinity}
    payloads = {"regression": {"controlled": [{"estimate": 0}, row]}}
    target = tmp_path / "not_created"

    with pytest.raises(ValueError) as error:
        export.write_frontend_payloads(payloads, target)

    assert "Unexpected infinite number" in str(error.value)
    assert "regression['controlled'][1]['estimate']" in str(error.value)
    assert row["estimate"] is infinity
    assert payloads["regression"]["controlled"][1] is row
    assert not target.exists()


@pytest.mark.parametrize("invalid", [float("inf"), object()])
def test_later_serialization_failure_leaves_all_existing_files_unchanged(tmp_path, invalid):
    original = {"first.json": b"existing first\r\n", "later.json": b"existing later\n"}
    for name, content in original.items():
        (tmp_path / name).write_bytes(content)
    payloads = {"first": {"estimate": 0.5}, "later": {"rows": [invalid]}}

    with pytest.raises((ValueError, TypeError), match=r"later\['rows'\]\[0\]"):
        export.write_frontend_payloads(payloads, tmp_path)

    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == original
    assert payloads["first"] == {"estimate": 0.5}
    assert payloads["later"]["rows"][0] is invalid


@pytest.mark.parametrize(("field", "standard_error"), [
    ("t_stat", 0.1), ("average_abnormal_return", 0.0),
])
def test_event_export_only_allows_existing_undefined_zero_se_t_stat(tmp_path, field, standard_error):
    _write_minimal_processed(tmp_path)
    source = tmp_path / OUTPUT_SPECS["abnormal_event_study"].path.relative_to(export.PROJECT_ROOT)
    abnormal = pd.read_csv(source)
    abnormal.loc[0, "std_error"] = standard_error
    abnormal.loc[0, field] = float("inf")
    abnormal.to_csv(source, index=False)

    payloads = export.build_frontend_payloads(root=tmp_path)

    assert math.isinf(payloads["event_study"][0][field])
    with pytest.raises(ValueError) as error:
        export.write_frontend_payloads(payloads, tmp_path / "not_created")
    assert f"event_study[0]['{field}']" in str(error.value)


def test_build_frontend_payloads_handles_missing_data(tmp_path):
    payloads = export.build_frontend_payloads(root=tmp_path)

    assert payloads["manifest"]["available"] is False
    assert payloads["manifest"]["schema_version"] == 1
    assert payloads["manifest"]["profile"] == "local"
    assert payloads["manifest"]["datasets"] == ["copy"]
    assert payloads["manifest"]["missing_files"]
    assert payloads["copy"]["central_question"]


def _write_output(root: Path, name: str, table: pd.DataFrame) -> None:
    table.to_csv(root / OUTPUT_SPECS[name].path.relative_to(export.PROJECT_ROOT), index=False)


def _write_shock_selection_fixture(root: Path) -> None:
    _write_minimal_processed(root)
    panel_path = root / OUTPUT_SPECS["analysis_panel"].path.relative_to(export.PROJECT_ROOT)
    panel = pd.read_csv(panel_path)
    panel["date"] = ["2024-01-01", "2024-03-01"]
    _write_output(root, "analysis_panel", panel)
    gpr_path = root / OUTPUT_SPECS["gpr"].path.relative_to(export.PROJECT_ROOT)
    template = pd.read_csv(gpr_path).iloc[0].to_dict()
    gpr = pd.DataFrame([
        {**template, "date": date, "gpr": 100.0, "gpr_change": change, "gpr_change_shock": flag}
        for date, change, flag in [
            ("2023-12-25", 1000.0, True),
            ("2024-01-02", 900.0, True),
            ("2024-01-30", 4.0, True),
            ("2024-02-01", 50.0, False),
            ("2024-02-29", 10.0, True),
            ("2024-04-01", 2000.0, True),
        ]
    ])
    _write_output(root, "gpr", gpr)


def test_overview_dates_counts_and_highlights_use_the_displayed_sample(tmp_path):
    _write_shock_selection_fixture(tmp_path)
    # A selected peak can fail market-model history requirements for every ETF.
    pd.DataFrame({"event_date": ["2024-01-30", "2024-01-30"]}).to_csv(
        tmp_path / "data" / "processed" / "event_windows_abnormal.csv", index=False
    )

    payloads = export.build_frontend_payloads(root=tmp_path)
    headline = payloads["overview"]["headline"]
    timeline = payloads["gpr_timeline"]

    assert headline["shock_count"] == payloads["manifest"]["shock_count"] == 3
    assert headline["selected_event_count"] == 2
    assert headline["represented_event_count"] == 1
    assert headline["start_date"] == "2024-01-01"
    assert headline["end_date"] == "2024-03-01"
    assert [row["date"] for row in timeline["top_shocks"]] == [
        "2024-01-02", "2024-02-01", "2024-02-29", "2024-01-30",
    ]
    assert [row["date"] for row in timeline["selected_events"]] == ["2024-01-30", "2024-02-29"]
    assert [row["represented_in_abnormal_study"] for row in timeline["selected_events"]] == [True, False]
    # Clipping before selection would incorrectly promote January 2 to a peak.
    largest = timeline["top_shocks"][0]
    assert largest["gpr_change_shock"] is True
    assert largest["selected_for_event_study"] is False
    assert timeline["top_shocks"][1]["gpr_change_shock"] is False
    for row in timeline["series"] + timeline["top_shocks"] + timeline["selected_events"]:
        assert headline["start_date"] <= row["date"] <= headline["end_date"]
    definitions = payloads["overview"]["definitions"]
    assert "90%" in definitions["shock_days"] and "252" in definitions["shock_days"]
    assert "20 calendar" in definitions["selected_events"]
    assert "not calendar days" in definitions["event_alignment"]
    assert "not necessarily flagged" in definitions["largest_jumps"]


def test_unrecorded_event_membership_stays_unknown(tmp_path):
    _write_shock_selection_fixture(tmp_path)

    payloads = export.build_frontend_payloads(root=tmp_path)

    assert payloads["overview"]["headline"]["selected_event_count"] == 2
    assert payloads["overview"]["headline"]["represented_event_count"] is None
    assert all(row["represented_in_abnormal_study"] is None for row in payloads["gpr_timeline"]["selected_events"])


def test_recorded_event_dates_must_match_the_gpr_selection(tmp_path):
    _write_shock_selection_fixture(tmp_path)
    pd.DataFrame({"event_date": ["2024-01-02"]}).to_csv(
        tmp_path / "data" / "processed" / "event_windows_abnormal.csv", index=False
    )

    with pytest.raises(ValueError, match="Recorded abnormal event dates"):
        export.build_frontend_payloads(root=tmp_path)


@pytest.mark.parametrize("undefined_t_stat", [float("inf"), float("-inf")])
def test_event_inference_and_accumulation_are_exported_without_changing_estimates(tmp_path, undefined_t_stat):
    _write_minimal_processed(tmp_path)
    abnormal = pd.DataFrame([
        {
            "market_group": "emerging", "relative_day": day,
            "average_abnormal_return": average, "cumulative_average_abnormal_return": cumulative,
            "observation_count": observations, "event_count": events,
            "std_error": error, "t_stat": t_stat, "p_value": p_value,
        }
        for day, average, cumulative, observations, events, error, t_stat, p_value in [
            (-5, -0.001, -0.003, 9, 2, 0.001, -3.0, 0.05),
            (0, 0.002, 0.005, 10, 3, 0.002, 2.5, 0.10),
            (5, 0.003, 0.009, 10, 3, 0.0, undefined_t_stat, float("nan")),
        ]
    ])
    raw = pd.DataFrame([
        {
            "market_group": "emerging", "relative_day": day, "average_return": 0.012,
            "cumulative_average_return": cumulative, "observation_count": 20, "event_count": 6,
        }
        for day, cumulative in [(-3, 0.011), (0, 0.023), (5, 0.035)]
    ])
    _write_output(tmp_path, "abnormal_event_study", abnormal.assign(unpublished_note="internal"))
    _write_output(tmp_path, "event_study", raw.assign(unpublished_note="internal"))

    payloads = export.build_frontend_payloads(root=tmp_path)
    rows = {row["relative_day"]: row for row in payloads["event_study"]}
    assert all("unpublished_note" not in row for row in rows.values())

    for source in abnormal.to_dict(orient="records"):
        exported = rows[source["relative_day"]]
        for field, value in source.items():
            if field == "t_stat" and source["relative_day"] == 5 or pd.isna(value):
                assert exported[field] is None
            else:
                assert exported[field] == value
        assert exported["accumulation_start_day"] == -5
    for source in raw.to_dict(orient="records"):
        exported = rows[source["relative_day"]]
        assert exported["cumulative_average_return"] == source["cumulative_average_return"]
        assert exported["average_return"] == source["average_return"]
        assert exported["raw_accumulation_start_day"] == -3
        assert exported["raw_observation_count"] == 20
        assert exported["raw_event_count"] == 6
    assert rows[0]["cumulative_average_abnormal_return"] == 0.005  # No day-0 rebasing.
    assert rows[-3]["cumulative_average_abnormal_return"] is None
    assert rows[-5]["cumulative_average_return"] is None
    reader = payloads["reader_summaries"]["market_reaction"]
    assert [row["relative_day"] for row in reader] == [0, 5]
    for row in reader:
        for field in ["std_error", "t_stat", "p_value", "observation_count", "event_count", "accumulation_start_day"]:
            assert row[field] == rows[row["relative_day"]][field]
        assert "not rebased" in row["plain_note"]
        assert "not adjusted for dependence" in row["plain_note"]
    definitions = payloads["overview"]["definitions"]
    assert "decimal log-return" in definitions["return_units"]
    assert "multiplying by 100" in definitions["return_units"]
    assert "neither series resets" in definitions["accumulation"]
    assert "raw-window limitation, left unchanged" in definitions["accumulation"]
    assert "pre-inception events" in definitions["accumulation"]
    assert "not adjusted for dependence" in definitions["inference"]
    # A zero SE and missing p-value must not introduce nonstandard JSON Infinity/NaN.
    json.dumps(payloads["event_study"], allow_nan=False)
    json.dumps(reader, allow_nan=False)
    target = export.write_frontend_payloads(payloads, tmp_path / "exported")
    assert _strict_json((target / "event_study.json").read_text(encoding="utf-8")) == payloads["event_study"]


def test_empirical_takeaways_follow_snapshot_coefficients_and_country_count(tmp_path):
    _write_minimal_processed(tmp_path)
    columns = ["term", "estimate", "std_error", "t_stat", "p_value"]
    controlled = pd.DataFrame([
        ["gpr_change_z", -0.0012, 0.0003, -4.0, 0.002],
        ["gpr_change_z:emerging_market", 0.0004, 0.0008, 0.5, 0.65],
    ], columns=columns)
    date_fe = pd.DataFrame([
        ["gpr_change_z:emerging_market", -0.0007, 0.0009, -0.8, 0.45],
    ], columns=columns)
    _write_output(tmp_path, "controlled_regression", controlled)
    _write_output(tmp_path, "date_fe_regression", date_fe)
    controlled_before = controlled.copy(deep=True)
    date_fe_before = date_fe.copy(deep=True)

    first = export.build_frontend_payloads(root=tmp_path)

    assert first["copy"]["current_answer_points"] == export.build_snapshot_answer(controlled, date_fe)
    assert first["copy"]["main_takeaway"] == first["copy"]["current_answer_points"][0]
    assert "1 country ETF proxies" in first["copy"]["intro"]
    assert first["regression"]["controlled"] == controlled.to_dict(orient="records")
    assert first["regression"]["date_fe"] == date_fe.to_dict(orient="records")
    pd.testing.assert_frame_equal(controlled, controlled_before)
    pd.testing.assert_frame_equal(date_fe, date_fe_before)

    controlled.loc[0, ["estimate", "p_value"]] = [0.0001, 0.9]
    _write_output(tmp_path, "controlled_regression", controlled)
    second = export.build_frontend_payloads(root=tmp_path)

    assert second["copy"]["main_takeaway"] != first["copy"]["main_takeaway"]
    assert second["copy"]["current_answer_points"] == export.build_snapshot_answer(controlled, date_fe)
