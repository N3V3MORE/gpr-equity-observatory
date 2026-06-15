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
    ]

    for helper_name in expected_helpers:
        assert callable(getattr(app, helper_name))
