from importlib import import_module

import pandas as pd
import pytest

import app


def test_formatting_helpers_render_reader_values():
    formatting = import_module("gprobs.dashboard.formatting")

    assert formatting.format_percent(0.1234) == "12.3%"
    assert formatting.format_basis_points(-0.0042) == "-42.0 bps"
    assert formatting.format_p_value(0.0321) == "0.032"
    assert formatting.format_p_value(0.0004) == "<0.001"
    assert formatting.format_p_value(pd.NA) == "n/a"
    assert formatting.format_metric(pd.NA) == "n/a"


def test_format_evidence_estimate_uses_structured_units():
    formatting = import_module("gprobs.dashboard.formatting")

    assert formatting.format_evidence_estimate(-0.0042, "basis_points") == "-42.0 bps"
    assert formatting.format_evidence_estimate(0.1234, "percent") == "12.3%"
    assert formatting.format_evidence_estimate(0.6142, "score") == "0.614"

    with pytest.raises(ValueError, match="Unknown estimate unit"):
        formatting.format_evidence_estimate(1.0, "basis points")


def test_classify_evidence_strength_uses_cautious_labels():
    assert (
        app.classify_evidence_strength(
            pd.Series({"p_value": 0.03, "inference": "negative association"})
        )
        == "Useful signal"
    )
    assert (
        app.classify_evidence_strength(
            pd.Series({"p_value": 0.40, "inference": "mixed evidence"})
        )
        == "Mixed"
    )
    assert (
        app.classify_evidence_strength(
            pd.Series({"p_value": 0.80, "inference": "weak evidence"})
        )
        == "Weak"
    )
    assert (
        app.classify_evidence_strength(
            pd.Series({"p_value": pd.NA, "inference": "exploratory classifier"})
        )
        == "Exploratory"
    )


def test_build_evidence_map_adds_strength_and_reader_columns():
    summary = pd.DataFrame(
        [
            {
                "method": "Panel regression",
                "focus": "Emerging-market interaction",
                "estimate": -0.00005,
                "unit": "basis_points",
                "p_value": 0.57,
                "inference": "weak evidence",
                "plain_english": "No strong asymmetry evidence.",
            },
            {
                "method": "Drawdown classifier",
                "focus": "Mean ROC AUC",
                "estimate": 0.6142,
                "unit": "score",
                "p_value": pd.NA,
                "inference": "exploratory classifier",
                "plain_english": "Exploratory risk-ranking metric.",
            },
        ]
    )

    evidence_map = app.build_evidence_map(summary)

    assert list(evidence_map.columns) == [
        "Method",
        "Question answered",
        "Direction",
        "Estimate",
        "p-value / metric",
        "Evidence strength",
        "Plain-English takeaway",
    ]
    assert evidence_map.loc[0, "Evidence strength"] == "Weak"
    assert evidence_map.loc[0, "Estimate"] == "-0.5 bps"
    assert evidence_map.loc[0, "p-value / metric"] == "0.570"
    assert (
        evidence_map.loc[0, "Plain-English takeaway"]
        == "No strong asymmetry evidence."
    )
    assert evidence_map.loc[1, "Evidence strength"] == "Exploratory"
    assert evidence_map.loc[1, "Estimate"] == "0.614"
    assert evidence_map.loc[1, "p-value / metric"] == "n/a"


def test_prediction_lab_best_metric_labels_include_model_names():
    metrics = pd.DataFrame(
        {
            "model_name": ["constant_baseline", "gpr_only", "full_features"],
            "roc_auc": [0.50, 0.51, 0.63],
            "average_precision": [0.25, 0.22, 0.38],
            "brier_score": [0.22, 0.20, 0.18],
            "base_rate": [0.25, 0.25, 0.25],
            "observation_count": [10, 10, 10],
        }
    )
    lift = pd.DataFrame(
        {
            "model_name": ["constant_baseline", "gpr_only", "full_features"],
            "bucket": ["top_10_percent", "top_10_percent", "top_10_percent"],
            "lift": [1.0, 1.1, 1.5],
        }
    )

    summary = app.build_model_summary(metrics, lift)
    labels = app.best_model_metric_labels(summary)

    assert labels["auc"] == ("Best model AUC (full_features)", "0.630")
    assert labels["ap"] == ("Best model AP (full_features)", "0.380")
    assert labels["lift"] == ("Top-decile lift (full_features)", "1.50x")


def test_build_model_summary_adds_baseline_deltas_and_verdicts():
    metrics = pd.DataFrame(
        {
            "model_name": [
                "constant_baseline",
                "weak_model",
                "modest_model",
                "useful_model",
            ],
            "roc_auc": [0.50, 0.55, 0.62, 0.68],
            "average_precision": [0.25, 0.29, 0.37, 0.44],
            "brier_score": [0.21, 0.205, 0.19, 0.17],
            "base_rate": [0.25, 0.25, 0.25, 0.25],
            "observation_count": [100, 100, 100, 100],
        }
    )
    lift = pd.DataFrame(
        {
            "model_name": [
                "constant_baseline",
                "weak_model",
                "modest_model",
                "useful_model",
            ],
            "bucket": ["top_10_percent"] * 4,
            "lift": [1.0, 1.15, 1.45, 1.85],
        }
    )

    summary = app.build_model_summary(metrics, lift)

    assert list(summary.columns) == [
        "model_name",
        "what_it_uses",
        "mean_roc_auc",
        "delta_auc_vs_constant_baseline",
        "mean_average_precision",
        "delta_ap_vs_constant_baseline",
        "mean_brier_score",
        "delta_brier_vs_constant_baseline",
        "mean_base_rate",
        "observation_count",
        "top_decile_lift",
        "model_verdict",
    ]
    by_model = summary.set_index("model_name")
    assert by_model.loc["constant_baseline", "what_it_uses"] == "Average historical event rate only"
    assert by_model.loc["constant_baseline", "model_verdict"] == "No useful ranking signal"
    assert by_model.loc["weak_model", "model_verdict"] == "Weak ranking signal"
    assert by_model.loc["modest_model", "model_verdict"] == "Modest ranking signal"
    assert by_model.loc["useful_model", "model_verdict"] == "Useful signal, not trading-grade"
    assert by_model.loc["modest_model", "delta_auc_vs_constant_baseline"] == pytest.approx(0.12)
    assert by_model.loc["modest_model", "delta_ap_vs_constant_baseline"] == pytest.approx(0.12)
    assert by_model.loc["modest_model", "delta_brier_vs_constant_baseline"] == pytest.approx(0.02)


def test_prediction_lab_model_descriptions_match_feature_groups():
    metrics = pd.DataFrame(
        {
            "model_name": [
                "constant_baseline",
                "volatility_only",
                "gpr_only",
                "market_controls_only",
                "volatility_plus_gpr",
                "full_features",
            ],
            "roc_auc": [0.50, 0.60, 0.51, 0.58, 0.61, 0.63],
            "average_precision": [0.25, 0.33, 0.26, 0.31, 0.34, 0.36],
            "brier_score": [0.22, 0.20, 0.218, 0.205, 0.198, 0.19],
            "base_rate": [0.25] * 6,
            "observation_count": [100] * 6,
        }
    )
    lift = pd.DataFrame(
        {
            "model_name": [
                "constant_baseline",
                "volatility_only",
                "gpr_only",
                "market_controls_only",
                "volatility_plus_gpr",
                "full_features",
            ],
            "bucket": ["top_10_percent"] * 6,
            "lift": [1.0, 1.35, 1.05, 1.2, 1.4, 1.5],
        }
    )

    descriptions = app.build_model_summary(metrics, lift).set_index("model_name")["what_it_uses"]

    assert descriptions.to_dict() == {
        "full_features": "All available features",
        "volatility_plus_gpr": "Volatility plus GPR",
        "volatility_only": "Recent ETF volatility",
        "market_controls_only": "Global market, VIX, oil, dollar, and rates",
        "gpr_only": "GPR features only",
        "constant_baseline": "Average historical event rate only",
    }


def test_model_verdict_helper_uses_cautious_plain_english_labels():
    assert app.model_verdict_label(0.50, 0.00, 1.00) == "No useful ranking signal"
    assert app.model_verdict_label(0.55, 0.05, 1.15) == "Weak ranking signal"
    assert app.model_verdict_label(0.62, 0.12, 1.45) == "Modest ranking signal"
    assert app.model_verdict_label(0.68, 0.18, 1.85) == "Useful signal, not trading-grade"


def test_prediction_lab_beginner_model_comparison_columns_are_declared():
    assert app.BEGINNER_MODEL_COMPARISON_COLUMNS == [
        "model_name",
        "what_it_uses",
        "mean_roc_auc",
        "delta_auc_vs_constant_baseline",
        "mean_average_precision",
        "delta_ap_vs_constant_baseline",
        "top_decile_lift",
        "mean_brier_score",
        "delta_brier_vs_constant_baseline",
        "model_verdict",
    ]


def test_build_gpr_shock_timeline_marks_top_shocks():
    charts = import_module("gprobs.dashboard.charts")

    assert charts.build_gpr_shock_timeline is app.build_gpr_shock_timeline

    gpr = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=4, freq="D"),
            "gpr": [100, 110, 90, 130],
            "gpr_change": [0, 10, -20, 40],
            "event": ["", "Shock A", "", "Shock B"],
        }
    )

    fig = app.build_gpr_shock_timeline(gpr)

    assert len(fig.data) == 2
    assert fig.data[1].name == "Top GPR changes"
    assert list(fig.data[1].x) == [
        pd.Timestamp("2024-01-04"),
        pd.Timestamp("2024-01-02"),
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-01-03"),
    ]


def test_dashboard_chart_builders_cover_monthly_and_prediction_views():
    charts = import_module("gprobs.dashboard.charts")
    monthly = pd.DataFrame(
        {
            "date_month": pd.to_datetime(["2024-01-01", "2024-02-01"]),
            "gpr_change_z": [0.2, -0.1],
            "spread_em_dev": [0.01, -0.02],
        }
    )
    calibration = pd.DataFrame(
        {
            "probability_decile": [1, 2],
            "realized_event_rate": [0.1, 0.2],
            "model_name": ["full_features", "full_features"],
        }
    )
    lift = pd.DataFrame(
        {
            "bucket": ["top_10_percent"],
            "lift": [1.5],
            "model_name": ["full_features"],
        }
    )
    forecasts = pd.DataFrame({"model": ["historical_mean"], "oos_r2": [0.0]})
    importance = pd.DataFrame({"feature": ["volatility"], "abs_coefficient": [0.8]})

    assert charts.build_monthly_gpr_shock_chart(monthly).layout.title.text == "Monthly GPR Shock Measure"
    assert (
        charts.build_monthly_spread_chart(monthly).layout.title.text
        == "Emerging Minus Developed Aggregate Return Spread"
    )
    assert (
        charts.build_monthly_forecast_chart(forecasts).layout.title.text
        == "Monthly Forecast OOS R2 Versus Historical Mean"
    )
    assert (
        charts.build_prediction_calibration_chart(calibration).layout.title.text
        == "Realized Drawdown Rate by Predicted-Risk Decile"
    )
    assert charts.build_prediction_lift_chart(lift).layout.title.text == "Drawdown Event Lift in Highest-Risk Buckets"
    assert charts.build_feature_importance_chart(importance).layout.title.text == "Drawdown Model Feature Importance"
