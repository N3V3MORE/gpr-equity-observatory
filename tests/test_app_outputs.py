import json

import pandas as pd

import app


def test_required_files_are_derived_from_output_specs():
    assert {
        name: spec.path for name, spec in app.OUTPUT_SPECS.items()
    } == app.REQUIRED_FILES


def test_load_outputs_reads_each_declared_output(monkeypatch, tmp_path):
    analysis_path = tmp_path / "analysis_panel.csv"
    gpr_path = tmp_path / "gpr_daily.csv"
    analysis_path.write_text("date,value\n2024-01-01,1\n", encoding="utf-8")
    gpr_path.write_text("date,gpr\n2024-01-01,120\n", encoding="utf-8")

    monkeypatch.setattr(
        app,
        "OUTPUT_SPECS",
        {
            "analysis_panel": app.OutputSpec(analysis_path, date_columns=("date",), low_memory=False),
            "gpr": app.OutputSpec(gpr_path, date_columns=("date",)),
        },
    )

    outputs = app.load_outputs()

    assert outputs["analysis_panel"].loc[0, "date"] == pd.Timestamp("2024-01-01")
    assert outputs["gpr"].loc[0, "gpr"] == 120


def test_missing_files_ignores_optional_monthly_outputs(monkeypatch, tmp_path):
    daily_path = tmp_path / "daily.csv"
    daily_path.write_text("date,value\n2024-01-01,1\n", encoding="utf-8")

    monkeypatch.setattr(
        app,
        "OUTPUT_SPECS",
        {"daily": app.OutputSpec(daily_path, required_columns=("date", "value"))},
    )
    monkeypatch.setattr(app, "REQUIRED_FILES", {"daily": daily_path})

    assert app.missing_files() == []


def test_load_monthly_outputs_returns_none_when_optional_files_are_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(app, "MONTHLY_MODES", {"sample": app.MonthlyModeConfig(root=tmp_path)})

    assert app.load_monthly_outputs() is None


def test_load_monthly_outputs_reads_sample_bundle(monkeypatch, tmp_path):
    panel_path = tmp_path / "sample_analysis_panel.csv"
    regression_path = tmp_path / "sample_table_02_baseline_regressions.csv"
    forecast_path = tmp_path / "sample_table_03_forecast_comparison.csv"
    source_manifest_path = tmp_path / "source_manifest.json"
    analysis_manifest_path = tmp_path / "analysis_panel_manifest.json"

    panel_path.write_text(
        "\n".join(
            [
                "date_month,market_id,market_class,excess_return,ret_fwd_1m,gpr_global,gpr_change_z,spread_em_dev,gdelt_risk_raw,gdelt_risk_z",
                "2020-01-01,developed,developed,1.0,0.5,100,0.1,0.7,0.0,0.0",
                "2020-01-01,emerging,emerging,1.7,0.6,100,0.1,0.7,0.0,0.0",
            ]
        ),
        encoding="utf-8",
    )
    regression_path.write_text(
        "horizon,term,estimate,std_error,t_value,p_value,se_type,nobs,adjusted_r2\n"
        "1,gpr_change_z,-0.1,0.2,-0.5,0.6,HAC,24,0.1\n",
        encoding="utf-8",
    )
    forecast_path.write_text(
        "model,rmse,mae,oos_r2,n_forecasts,first_forecast_date,last_forecast_date,forecast_window_aligned\n"
        "historical_mean,1,1,0,12,2021-01-01,2021-12-01,True\n",
        encoding="utf-8",
    )
    source_manifest_path.write_text(
        json.dumps({"sources": [{"source_name": "Monthly benchmark deterministic sample"}]}),
        encoding="utf-8",
    )
    analysis_manifest_path.write_text(
        json.dumps(
            {
                "dataset_mode": "monthly_benchmark_sample",
                "row_count": 2,
                "sample_start": "2020-01-01",
                "sample_end": "2020-01-01",
                "used_placeholder_gdelt": True,
                "used_placeholder_macro": True,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        app,
        "MONTHLY_MODES",
        {
            "sample": app.MonthlyModeConfig(
                root=tmp_path,
                panel=panel_path.name,
                regressions=regression_path.name,
                forecasts=forecast_path.name,
                source_manifest=source_manifest_path.name,
                analysis_manifest=analysis_manifest_path.name,
            )
        },
    )

    bundle = app.load_monthly_outputs()

    assert bundle is not None
    assert bundle.mode == "sample"
    assert bundle.mode_label == "Sample"
    assert bundle.panel.loc[0, "date_month"] == pd.Timestamp("2020-01-01")
    assert bundle.source_names == ["Monthly benchmark deterministic sample"]

    provenance = app.monthly_provenance_rows(bundle)
    assert {"field", "value"}.issubset(provenance.columns)
    assert provenance.loc[provenance["field"] == "dataset_mode", "value"].iloc[0] == "monthly_benchmark_sample"
    assert provenance.loc[provenance["field"] == "source_count", "value"].iloc[0] == "1"
