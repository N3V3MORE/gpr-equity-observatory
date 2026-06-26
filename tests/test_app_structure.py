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
