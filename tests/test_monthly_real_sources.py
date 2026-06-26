import json
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from gprobs.data.fama_french import load_fama_french_factor_returns
from gprobs.data.monthly_sources import (
    build_monthly_benchmark_real,
    load_caldara_iacoviello_gpr,
    resolve_monthly_source,
)


def _write_fama_french_zip(path: Path, rows: list[str]) -> Path:
    text = "\n".join(
        [
            "This file has a preamble",
            ",Mkt-RF,SMB,HML,RF",
            *rows,
            "Annual Factors: January-December",
            "",
        ]
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(path.with_suffix(".csv").name, text)
    return path


def _write_fixture_config(tmp_path: Path, gpr_path: Path, developed_zip: Path, emerging_zip: Path) -> Path:
    config = tmp_path / "sources.yml"
    config.write_text(
        "\n".join(
            [
                "gpr:",
                f"  path_or_url: {gpr_path}",
                "  loader: caldara_iacoviello",
                "",
                "fama_french:",
                f"  developed_zip: {developed_zip}",
                f"  emerging_zip: {emerging_zip}",
                "",
                "sample_period:",
                '  start: "2000-01-01"',
                '  end: "2000-04-01"',
            ]
        ),
        encoding="utf-8",
    )
    return config


def test_load_caldara_iacoviello_gpr_maps_columns_and_month_starts(tmp_path):
    source = tmp_path / "gpr.csv"
    source.write_text(
        "\n".join(
            [
                "month,GPR,GPRT,GPRA",
                "2000-01-15,100,60,40",
                "2000-02-01,120,70,50",
            ]
        ),
        encoding="utf-8",
    )

    gpr = load_caldara_iacoviello_gpr(source)

    assert gpr.to_dict("records") == [
        {
            "date_month": pd.Timestamp("2000-01-01"),
            "gpr_global": 100.0,
            "gprt_global": 60.0,
            "gpra_global": 40.0,
        },
        {
            "date_month": pd.Timestamp("2000-02-01"),
            "gpr_global": 120.0,
            "gprt_global": 70.0,
            "gpra_global": 50.0,
        },
    ]


def test_load_caldara_iacoviello_gpr_rejects_duplicate_months(tmp_path):
    source = tmp_path / "gpr.csv"
    source.write_text(
        "\n".join(
            [
                "month,GPR,GPRT,GPRA",
                "2000-01-01,100,60,40",
                "2000-01-15,120,70,50",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate keys"):
        load_caldara_iacoviello_gpr(source)


def test_load_fama_french_factor_returns_parses_safe_zip(tmp_path):
    source = _write_fama_french_zip(
        tmp_path / "developed.zip",
        [
            "200001,1.50,0.00,0.00,0.05",
            "200002,-0.50,0.00,0.00,0.04",
        ],
    )

    returns = load_fama_french_factor_returns(source, market_id="developed", market_class="developed")

    assert returns[["date_month", "market_id", "market_class", "return_usd", "excess_return"]].to_dict(
        "records"
    ) == [
        {
            "date_month": pd.Timestamp("2000-01-01"),
            "market_id": "developed",
            "market_class": "developed",
            "return_usd": 1.55,
            "excess_return": 1.5,
        },
        {
            "date_month": pd.Timestamp("2000-02-01"),
            "market_id": "developed",
            "market_class": "developed",
            "return_usd": -0.46,
            "excess_return": -0.5,
        },
    ]


def test_load_fama_french_factor_returns_rejects_unsafe_zip_shapes(tmp_path):
    no_csv = tmp_path / "no_csv.zip"
    with zipfile.ZipFile(no_csv, "w") as archive:
        archive.writestr("readme.txt", "not a factor file")

    multiple_csv = tmp_path / "multiple_csv.zip"
    with zipfile.ZipFile(multiple_csv, "w") as archive:
        archive.writestr("one.csv", ",Mkt-RF,SMB,HML,RF\n200001,1,0,0,0")
        archive.writestr("two.csv", ",Mkt-RF,SMB,HML,RF\n200001,1,0,0,0")

    with pytest.raises(ValueError, match="no CSV"):
        load_fama_french_factor_returns(no_csv, market_id="developed", market_class="developed")
    with pytest.raises(ValueError, match="exactly one CSV"):
        load_fama_french_factor_returns(multiple_csv, market_id="developed", market_class="developed")


def test_resolve_monthly_source_rejects_unsafe_sources(tmp_path):
    with pytest.raises(ValueError, match="expected SHA-256"):
        resolve_monthly_source("https://example.test/source.csv", tmp_path)
    with pytest.raises(ValueError, match="unsupported source URL scheme"):
        resolve_monthly_source("http://example.test/source.csv", tmp_path)
    with pytest.raises(ValueError, match="unsupported source URL scheme"):
        resolve_monthly_source("file:///tmp/source.csv", tmp_path)

    source = tmp_path / "source.csv"
    source.write_text("date,value\n2020-01-01,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256"):
        resolve_monthly_source(str(source), tmp_path, expected_sha256="0" * 64)


def test_build_monthly_benchmark_real_writes_redacted_common_sample_outputs(tmp_path):
    gpr = tmp_path / "gpr.csv"
    gpr.write_text(
        "\n".join(
            [
                "month,GPR,GPRT,GPRA",
                "2000-01-01,100,60,40",
                "2000-02-01,110,65,45",
                "2000-03-01,130,80,50",
                "2000-04-01,115,72,43",
            ]
        ),
        encoding="utf-8",
    )
    developed = _write_fama_french_zip(
        tmp_path / "developed.zip",
        [
            "200001,1.00,0.00,0.00,0.05",
            "200002,1.20,0.00,0.00,0.05",
            "200003,-0.40,0.00,0.00,0.05",
            "200004,0.80,0.00,0.00,0.05",
        ],
    )
    emerging = _write_fama_french_zip(
        tmp_path / "emerging.zip",
        [
            "200001,2.00,0.00,0.00,0.05",
            "200002,-0.30,0.00,0.00,0.05",
            "200003,0.60,0.00,0.00,0.05",
            "200004,1.10,0.00,0.00,0.05",
        ],
    )
    config = _write_fixture_config(tmp_path, gpr, developed, emerging)

    build_monthly_benchmark_real(config, root=tmp_path)

    processed = tmp_path / "data" / "processed" / "monthly_benchmark"
    metadata = tmp_path / "data" / "metadata" / "monthly_benchmark"
    panel = pd.read_csv(processed / "analysis_panel.csv", parse_dates=["date_month"])
    manifest = json.loads((metadata / "source_manifest_real.json").read_text(encoding="utf-8"))
    panel_manifest = json.loads((metadata / "analysis_panel_manifest_real.json").read_text(encoding="utf-8"))

    assert sorted(panel["market_id"].unique().tolist()) == ["developed", "emerging"]
    assert panel["date_month"].min() == pd.Timestamp("2000-01-01")
    assert panel["date_month"].max() == pd.Timestamp("2000-04-01")
    assert "placeholder_macro_zero" in panel.columns
    assert panel["gdelt_risk_raw"].eq(0).all()
    assert panel_manifest["dataset_mode"] == "monthly_benchmark_real"
    assert panel_manifest["aligned_to_common_gpr_returns_sample"] is True

    sources = manifest["sources"]
    assert [source["source_name"] for source in sources] == [
        "Caldara-Iacoviello GPR",
        "Kenneth French Developed Factors",
        "Kenneth French Emerging Factors",
    ]
    assert all(len(source["file_hash_sha256"]) == 64 for source in sources)
    assert all(str(tmp_path) not in source["raw_file_path"] for source in sources)
    assert all(source["raw_file_path"].startswith("local://") for source in sources)
