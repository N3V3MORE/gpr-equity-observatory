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
