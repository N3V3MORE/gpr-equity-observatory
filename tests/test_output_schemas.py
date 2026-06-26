from contextlib import suppress

import app
from gprobs.dashboard import outputs as dashboard_outputs

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
        "gpr_shock",
        "gpr_change_shock",
        "gpr_change_shock_full_sample",
        "gpr_change_shock_expanding",
    },
    "gpr": {
        "date",
        "gpr",
        "gpr_act",
        "gpr_threat",
        "gpr_change",
        "gpr_change_z",
        "gpr_shock",
        "gpr_shock_full_sample",
        "gpr_shock_expanding",
        "gpr_change_shock",
        "gpr_change_shock_full_sample",
        "gpr_change_shock_expanding",
        "event",
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
        "std_error",
        "t_stat",
        "p_value",
    },
    "event_robustness": {
        "shock_quantile",
        "window",
        "market_group",
        "cumulative_average_abnormal_return",
        "event_count",
        "std_error",
        "t_stat",
        "p_value",
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
        "gpr_change_mean",
        "gpr_change_std",
    },
    "quantile_regression": {
        "quantile",
        "term",
        "estimate",
        "std_error",
        "t_stat",
        "p_value",
        "inference",
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
        "brier_score",
        "base_rate",
        "observation_count",
    },
    "drawdown_predictions": {
        "date",
        "ticker",
        "country",
        "market_group",
        "fold",
        "model_name",
        "train_start",
        "train_end",
        "test_start",
        "test_end",
        "drawdown_risk",
        "predicted_probability",
        "forward_min_return",
    },
    "drawdown_threshold_metrics": {
        "model_name",
        "threshold",
        "precision",
        "recall",
        "f1",
        "share_flagged",
        "event_rate_flagged",
        "observation_count",
    },
    "drawdown_calibration": {
        "model_name",
        "probability_decile",
        "mean_predicted_probability",
        "realized_event_rate",
        "observation_count",
    },
    "drawdown_lift": {
        "model_name",
        "bucket",
        "event_rate",
        "base_event_rate",
        "lift",
        "observation_count",
    },
    "drawdown_country_risk_summary": {
        "country",
        "market_group",
        "model_name",
        "average_predicted_probability",
        "realized_event_rate",
        "observation_count",
    },
    "drawdown_importance": {"feature", "coefficient", "abs_coefficient"},
    "evidence_summary": {
        "method",
        "focus",
        "estimate",
        "unit",
        "p_value",
        "inference",
        "plain_english",
    },
    "rolling_beta": {"date", "ticker", "country", "market_group", "rolling_gpr_beta"},
    "large_returns": {"date", "ticker", "country", "return", "abs_return"},
}

EXPECTED_MONTHLY_OUTPUT_COLUMNS = {
    "monthly_panel": {
        "date_month",
        "market_id",
        "market_class",
        "excess_return",
        "ret_fwd_1m",
        "gpr_global",
        "gpr_change_z",
        "spread_em_dev",
        "gdelt_risk_raw",
        "gdelt_risk_z",
    },
    "monthly_regressions": {
        "horizon",
        "term",
        "estimate",
        "std_error",
        "t_value",
        "p_value",
        "se_type",
        "nobs",
        "adjusted_r2",
    },
    "monthly_forecasts": {
        "model",
        "rmse",
        "mae",
        "oos_r2",
        "n_forecasts",
        "first_forecast_date",
        "last_forecast_date",
        "forecast_window_aligned",
    },
}


def test_app_uses_single_date_fe_panel_regression_filename():
    assert app.REQUIRED_FILES["date_fe_regression"].name == "panel_regression_date_fe.csv"


def test_dashboard_required_outputs_declare_expected_columns():
    assert set(EXPECTED_OUTPUT_COLUMNS) == set(app.OUTPUT_SPECS)

    for name, expected_columns in EXPECTED_OUTPUT_COLUMNS.items():
        assert expected_columns.issubset(set(app.OUTPUT_SPECS[name].required_columns))


def test_monthly_dashboard_outputs_are_optional_and_schema_checked():
    assert not set(app.MONTHLY_OUTPUT_SPECS).intersection(app.REQUIRED_FILES)

    for name, expected_columns in EXPECTED_MONTHLY_OUTPUT_COLUMNS.items():
        assert expected_columns.issubset(set(app.MONTHLY_OUTPUT_SPECS[name].required_columns))


def test_load_outputs_rejects_missing_required_columns(monkeypatch, tmp_path):
    bad_path = tmp_path / "gpr_daily.csv"
    bad_path.write_text("date,gpr\n2024-01-01,120\n", encoding="utf-8")
    monkeypatch.setattr(
        dashboard_outputs,
        "OUTPUT_SPECS",
        {
            "gpr": dashboard_outputs.OutputSpec(
                bad_path,
                date_columns=("date",),
                required_columns=("date", "gpr", "gpr_change"),
            )
        },
    )

    with suppress(AttributeError):
        dashboard_outputs.load_outputs.clear()

    try:
        dashboard_outputs.load_outputs()
    except ValueError as exc:
        assert "gpr_daily.csv is missing required columns: ['gpr_change']" in str(exc)
    else:
        raise AssertionError("load_outputs accepted a CSV with missing required columns")
