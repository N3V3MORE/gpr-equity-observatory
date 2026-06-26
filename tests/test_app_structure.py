import app


def test_dashboard_components_live_in_dashboard_components_module():
    from importlib import import_module

    components = import_module("gprobs.dashboard.components")

    assert components.DASHBOARD_INTRO is app.DASHBOARD_INTRO
    assert components.DASHBOARD_MAIN_TAKEAWAY is app.DASHBOARD_MAIN_TAKEAWAY
    assert components.DASHBOARD_USE_NOTE is app.DASHBOARD_USE_NOTE
    assert components.HOW_TO_READ_NOTES is app.HOW_TO_READ_NOTES
    assert components.render_intro is app.render_intro
    assert components.render_summary_cards is app.render_summary_cards
    assert components.render_how_to_read is app.render_how_to_read
    assert components.render_csv_download is app.render_csv_download
    assert components.render_missing_data_message is app.render_missing_data_message


def test_evidence_map_helper_lives_in_dashboard_evidence_module():
    from importlib import import_module

    evidence = import_module("gprobs.dashboard.evidence")

    assert evidence.build_evidence_map is app.build_evidence_map


def test_prediction_summary_helpers_live_in_dashboard_prediction_module():
    from importlib import import_module

    prediction = import_module("gprobs.dashboard.prediction")

    assert prediction.ML_VALIDATION_HEADING is app.ML_VALIDATION_HEADING
    assert prediction.ML_VALIDATION_CAPTION is app.ML_VALIDATION_CAPTION
    assert prediction.FEATURE_IMPORTANCE_CAPTION is app.FEATURE_IMPORTANCE_CAPTION
    assert prediction.build_model_summary is app.build_model_summary
    assert prediction.best_model_metric_labels is app.best_model_metric_labels


def test_dashboard_tab_render_helpers_are_defined():
    expected_helpers = [
        "render_overview_tab",
        "render_shocks_tab",
        "render_event_tab",
        "render_robustness_tab",
        "render_regression_tab",
        "render_tail_tab",
        "render_local_tab",
        "render_ml_tab",
        "render_rolling_tab",
        "render_coverage_tab",
        "render_monthly_benchmark_tab",
    ]

    for helper_name in expected_helpers:
        assert callable(getattr(app, helper_name))


def test_ml_tab_uses_purged_validation_wording():
    assert app.ML_VALIDATION_HEADING == "Purged Chronological Validation"
    assert app.ML_VALIDATION_CAPTION == (
        "Splits are purged chronological, so the model trains only on earlier dates "
        "and excludes dates immediately before the test fold to reduce forward-label leakage."
    )


def test_monthly_tab_uses_required_limitation_wording():
    assert "not empirical evidence" in app.MONTHLY_SAMPLE_NOTICE
    assert "benchmark" in app.MONTHLY_REAL_NOTICE
    assert "country-clustered" in app.MONTHLY_CLUSTER_NOTICE


def test_dashboard_intro_keeps_cautious_project_framing():
    assert "20 country ETF proxies" in app.DASHBOARD_INTRO
    assert "does not strongly prove" in app.DASHBOARD_MAIN_TAKEAWAY
    assert "not as a trading system" in app.DASHBOARD_USE_NOTE


def test_dashboard_story_tab_labels_are_declared():
    assert app.DASHBOARD_TAB_LABELS == [
        "Overview",
        "GPR Shock Timeline",
        "Market Response",
        "Regression Evidence",
        "Downside Risk",
        "Dynamic Response",
        "Prediction Lab",
        "Country Sensitivity",
        "Monthly Benchmark",
        "Data Quality",
    ]
    assert app.DAILY_TAB_LABELS is app.DASHBOARD_TAB_LABELS


def test_daily_tabs_have_how_to_read_notes():
    expected_keys = {
        "overview",
        "shocks",
        "market_response",
        "regression",
        "downside_risk",
        "dynamic_response",
        "prediction_lab",
        "country_sensitivity",
        "monthly_benchmark",
        "data_quality",
    }

    assert set(app.HOW_TO_READ_NOTES) == expected_keys
    assert "Day 0" in app.HOW_TO_READ_NOTES["market_response"]
    assert "not a trading strategy" in app.HOW_TO_READ_NOTES["prediction_lab"]
    assert "not country-level panel evidence" in app.HOW_TO_READ_NOTES["monthly_benchmark"]


def test_dashboard_download_and_timeline_helpers_are_defined():
    assert callable(app.render_csv_download)
    assert callable(app.build_gpr_shock_timeline)
