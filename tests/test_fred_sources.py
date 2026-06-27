import json

import pandas as pd
import pytest


def _fred_payload(values: list[tuple[str, str]]) -> bytes:
    return json.dumps(
        {
            "observations": [
                {
                    "date": date,
                    "value": value,
                    "realtime_start": date,
                    "realtime_end": date,
                }
                for date, value in values
            ]
        }
    ).encode("utf-8")


def test_fred_api_key_is_not_required_for_import_parsing_or_lagging(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)

    from gprobs.data import fred_sources

    parsed = fred_sources.parse_fred_observations(
        _fred_payload([("2024-01-01", "5.25")]),
        fred_sources.DEFAULT_FRED_SERIES[1],
    )
    lagged = fred_sources.add_lagged_fred_features(parsed)

    assert parsed.loc[0, "policy_rate_effective_fed_funds"] == 5.25
    assert "policy_rate_effective_fed_funds_lag1d" in lagged.columns
    with pytest.raises(RuntimeError, match="FRED_API_KEY"):
        fred_sources.get_fred_api_key()


def test_parse_fred_observations_converts_values_to_numeric():
    from gprobs.data.fred_sources import DEFAULT_FRED_SERIES, parse_fred_observations

    assert DEFAULT_FRED_SERIES[0].series_id == "BAA10Y"
    assert DEFAULT_FRED_SERIES[0].column_name == "credit_spread_baa_10y"

    parsed = parse_fred_observations(
        _fred_payload(
            [
                ("2024-01-01", "4.75"),
                ("2024-01-02", "."),
                ("2024-01-03", "-1.25"),
            ]
        ),
        DEFAULT_FRED_SERIES[0],
    )

    assert parsed["date"].tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-01-02"),
        pd.Timestamp("2024-01-03"),
    ]
    assert parsed["credit_spread_baa_10y"].tolist()[:1] == [4.75]
    assert pd.isna(parsed.loc[1, "credit_spread_baa_10y"])
    assert parsed.loc[2, "credit_spread_baa_10y"] == -1.25


def test_lagged_fred_features_use_prior_observation_values():
    from gprobs.data.fred_sources import FRED_OUTPUT_COLUMNS, add_lagged_fred_features

    controls = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "credit_spread_baa_10y": [4.0, 4.2, 4.4],
            "policy_rate_effective_fed_funds": [5.25, 5.30, 5.35],
            "inflation_expectation_10y_breakeven": [2.1, 2.2, 2.3],
        }
    )

    lagged = add_lagged_fred_features(controls)

    assert lagged.columns.tolist() == FRED_OUTPUT_COLUMNS
    assert pd.isna(lagged.loc[0, "credit_spread_baa_10y_lag1d"])
    assert lagged.loc[1, "credit_spread_baa_10y_lag1d"] == 4.0
    assert lagged.loc[2, "policy_rate_effective_fed_funds_lag1d"] == 5.30
    assert lagged.loc[2, "inflation_expectation_10y_breakeven_lag1d"] == 2.2
    assert lagged.loc[1, "credit_spread_baa_10y_lag1d"] != lagged.loc[1, "credit_spread_baa_10y"]


def test_build_fred_macro_controls_writes_outputs_and_manifest_without_secret(tmp_path):
    from gprobs.data.fred_sources import (
        FRED_OUTPUT_COLUMNS,
        build_fred_macro_controls,
    )

    payloads = {
        "BAA10Y": _fred_payload([("2024-01-01", "2.00"), ("2024-01-02", "2.25")]),
        "DFF": _fred_payload([("2024-01-01", "5.25"), ("2024-01-02", "5.30")]),
        "T10YIE": _fred_payload([("2024-01-01", "2.10"), ("2024-01-02", ".")]),
    }
    requested_urls = []

    def fake_fetcher(url: str, timeout: int) -> bytes:
        requested_urls.append(url)
        for series_id, payload in payloads.items():
            if f"series_id={series_id}" in url:
                return payload
        raise AssertionError(f"unexpected FRED URL: {url}")

    controls = build_fred_macro_controls(
        root=tmp_path,
        api_key="secret-test-key",
        fetcher=fake_fetcher,
        retry_backoff_seconds=0,
    )

    processed_path = tmp_path / "data" / "processed" / "fred_macro_controls.csv"
    manifest_path = tmp_path / "data" / "metadata" / "fred_source_manifest.json"
    raw_paths = [
        tmp_path / "data" / "raw" / "fred" / f"{series_id}_observations.json"
        for series_id in payloads
    ]

    assert controls.columns.tolist() == FRED_OUTPUT_COLUMNS
    assert pd.read_csv(processed_path).columns.tolist() == FRED_OUTPUT_COLUMNS
    assert all(path.exists() for path in raw_paths)
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    assert manifest["manifest_type"] == "source_collection"
    assert [source["source_name"] for source in manifest["sources"]] == [
        "FRED BAA10Y",
        "FRED DFF",
        "FRED T10YIE",
    ]
    assert "secret-test-key" not in manifest_text
    assert "api_key" not in manifest_text
    assert all("api_key=secret-test-key" in url for url in requested_urls)
