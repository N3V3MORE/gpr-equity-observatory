from contextlib import suppress

import app

EXPECTED_OUTPUT_COLUMNS = {
    "analysis_panel": {
        "date",
        "ticker",
        "country",
        "market_group",
        "region",
        "return",
        "gpr",
        "gpr_change",
        "gpr_change_z",
        "gpr_change_shock",
        "gpr_change_shock_expanding",
    },
    "gpr": {
        "date",
        "gpr",
        "gpr_change",
        "gpr_change_z",
        "gpr_shock_full_sample",
        "gpr_shock_expanding",
        "gpr_change_shock",
        "gpr_change_shock_expanding",
    },
    "group_returns": {"date", "market_group", "average_return", "country_count"},
    "event_study": {
        "market_group",
        "relative_day",
        "average_return",
        "cumulative_average_return",
        "observation_count",
        "event_count",
    },
    "abnormal_event_study": {
        "market_group",
        "relative_day",
        "average_abnormal_return",
        "cumulative_average_abnormal_return",
        "observation_count",
        "event_count",
    },
    "event_robustness": {
        "shock_quantile",
        "window",
        "market_group",
        "cumulative_average_abnormal_return",
        "event_count",
    },
    "regression": {"term", "estimate", "std_error", "t_stat", "p_value"},
    "controlled_regression": {"term", "estimate", "std_error", "t_stat", "p_value"},
    "date_fe_regression": {"term", "estimate", "std_error", "t_stat", "p_value"},
    "panel_sample_robustness": {
        "scenario",
        "term",
        "estimate",
        "std_error",
        "t_stat",
        "p_value",
        "observation_count",
    },
    "quantile_regression": {
        "quantile",
        "term",
        "estimate",
        "std_error",
        "t_stat",
        "p_value",
    },
    "local_projections": {
        "horizon",
        "market_group",
        "estimate",
        "std_error",
        "ci_low",
        "ci_high",
        "p_value",
    },
    "drawdown_metrics": {
        "fold",
        "model_name",
        "train_start",
        "train_end",
        "test_start",
        "test_end",
        "roc_auc",
        "average_precision",
        "base_rate",
        "observation_count",
    },
    "drawdown_importance": {"feature", "coefficient", "abs_coefficient"},
    "evidence_summary": {"method", "focus", "estimate", "p_value", "plain_english"},
    "rolling_beta": {"date", "ticker", "country", "market_group", "rolling_gpr_beta"},
    "large_returns": {"date", "ticker", "country", "return", "abs_return"},
}


def test_app_uses_original_two_way_fe_panel_regression_filename():
    assert app.REQUIRED_FILES["date_fe_regression"].name == "panel_regression_two_way_fe.csv"


def test_dashboard_required_outputs_declare_expected_columns():
    assert set(EXPECTED_OUTPUT_COLUMNS) == set(app.OUTPUT_SPECS)

    for name, expected_columns in EXPECTED_OUTPUT_COLUMNS.items():
        assert expected_columns.issubset(set(app.OUTPUT_SPECS[name].required_columns))


def test_load_outputs_rejects_missing_required_columns(monkeypatch, tmp_path):
    bad_path = tmp_path / "gpr_daily.csv"
    bad_path.write_text("date,gpr\n2024-01-01,120\n", encoding="utf-8")
    monkeypatch.setattr(
        app,
        "OUTPUT_SPECS",
        {
            "gpr": app.OutputSpec(
                bad_path,
                date_columns=("date",),
                required_columns=("date", "gpr", "gpr_change"),
            )
        },
    )

    with suppress(AttributeError):
        app.load_outputs.clear()

    try:
        app.load_outputs()
    except ValueError as exc:
        assert "gpr_daily.csv is missing required columns: ['gpr_change']" in str(exc)
    else:
        raise AssertionError("load_outputs accepted a CSV with missing required columns")
