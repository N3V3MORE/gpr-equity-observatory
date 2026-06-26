import app


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
    assert app.DAILY_TAB_LABELS == [
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
        "data_quality",
    }

    assert set(app.HOW_TO_READ_NOTES) == expected_keys
    assert "Day 0" in app.HOW_TO_READ_NOTES["market_response"]
    assert "not a trading strategy" in app.HOW_TO_READ_NOTES["prediction_lab"]


def test_dashboard_download_and_timeline_helpers_are_defined():
    assert callable(app.render_csv_download)
    assert callable(app.build_gpr_shock_timeline)
