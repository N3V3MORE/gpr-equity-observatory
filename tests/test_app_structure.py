import app


def test_dashboard_components_live_in_dashboard_components_module():
    from importlib import import_module

    components = import_module("gprobs.dashboard.components")

    assert components.BEGINNER_TAB_GUIDES is app.BEGINNER_TAB_GUIDES
    assert components.CENTRAL_PROJECT_QUESTION is app.CENTRAL_PROJECT_QUESTION
    assert components.DASHBOARD_INTRO is app.DASHBOARD_INTRO
    assert components.DASHBOARD_MAIN_TAKEAWAY is app.DASHBOARD_MAIN_TAKEAWAY
    assert components.DASHBOARD_MODES is app.DASHBOARD_MODES
    assert components.METHOD_MAP_ROWS is app.METHOD_MAP_ROWS
    assert components.OVERVIEW_CURRENT_ANSWER_POINTS is app.OVERVIEW_CURRENT_ANSWER_POINTS
    assert components.OVERVIEW_DOES_NOT_PROVE_POINTS is app.OVERVIEW_DOES_NOT_PROVE_POINTS
    assert components.OVERVIEW_JOB_STATEMENTS is app.OVERVIEW_JOB_STATEMENTS
    assert components.DASHBOARD_USE_NOTE is app.DASHBOARD_USE_NOTE
    assert components.GLOSSARY_TERMS is app.GLOSSARY_TERMS
    assert components.HOW_TO_READ_NOTES is app.HOW_TO_READ_NOTES
    assert components.PREDICTION_METRIC_EXPLANATIONS is app.PREDICTION_METRIC_EXPLANATIONS
    assert components.render_beginner_intro is app.render_beginner_intro
    assert components.render_beginner_takeaways is app.render_beginner_takeaways
    assert components.render_glossary is app.render_glossary
    assert components.render_intro is app.render_intro
    assert components.render_mode_selector is app.render_mode_selector
    assert components.render_summary_cards is app.render_summary_cards
    assert components.technical_details is app.technical_details
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

    assert prediction.BEGINNER_MODEL_COMPARISON_COLUMNS is app.BEGINNER_MODEL_COMPARISON_COLUMNS
    assert prediction.ML_VALIDATION_HEADING is app.ML_VALIDATION_HEADING
    assert prediction.ML_VALIDATION_CAPTION is app.ML_VALIDATION_CAPTION
    assert prediction.FEATURE_IMPORTANCE_CAPTION is app.FEATURE_IMPORTANCE_CAPTION
    assert prediction.PREDICTION_LAB_CONCLUSION is app.PREDICTION_LAB_CONCLUSION
    assert prediction.build_model_summary is app.build_model_summary
    assert prediction.best_model_metric_labels is app.best_model_metric_labels
    assert prediction.model_verdict_label is app.model_verdict_label


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


def test_dashboard_modes_and_glossary_terms_are_declared():
    assert app.DASHBOARD_MODES == ("Beginner", "Technical")
    for term in [
        "GPR",
        "ETF",
        "shock",
        "control",
        "p-value",
        "AUC",
        "average precision",
        "Brier score",
        "lift",
        "calibration",
    ]:
        assert term in app.GLOSSARY_TERMS
        assert app.GLOSSARY_TERMS[term]


def test_beginner_guides_cover_each_dashboard_tab():
    assert set(app.BEGINNER_TAB_GUIDES) == set(app.HOW_TO_READ_NOTES)
    for guide in app.BEGINNER_TAB_GUIDES.values():
        assert guide["question"].endswith("?")
        assert 2 <= len(guide["takeaways"]) <= 3
        assert guide["does_not_prove"]


def test_prediction_lab_beginner_copy_explains_risk_ranking_not_prices():
    guide = app.BEGINNER_TAB_GUIDES["prediction_lab"]
    prediction_copy = " ".join(
        [
            guide["question"],
            guide["does_not_prove"],
            *[body for _, body in guide["takeaways"]],
            app.PREDICTION_LAB_CONCLUSION,
        ]
    ).lower()

    assert "rank" in prediction_copy
    assert "drawdown risk" in prediction_copy
    assert "does not predict prices" in prediction_copy
    assert "gpr alone" in prediction_copy
    assert "modest" in prediction_copy

    for metric in ["AUC", "average precision", "Brier score", "lift", "calibration"]:
        assert metric in app.PREDICTION_METRIC_EXPLANATIONS
        assert app.PREDICTION_METRIC_EXPLANATIONS[metric]


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
    assert "No mode selector" in app.MONTHLY_MODE_PRIORITY_NOTICE


def test_monthly_empty_state_guides_full_sample_and_real_pipelines():
    from gprobs.dashboard import monthly

    assert monthly.MONTHLY_EMPTY_STATE_COMMANDS == [
        "python scripts/run_task.py monthly-sample --min-train-months 24",
        "python scripts/run_task.py monthly-real",
    ]
    assert "config/sources.yml" in monthly.MONTHLY_EMPTY_STATE_NOTE
    assert "local-only" in monthly.MONTHLY_EMPTY_STATE_NOTE


def test_dashboard_intro_keeps_cautious_project_framing():
    assert "20 country ETF proxies" in app.DASHBOARD_INTRO
    assert "does not strongly prove" in app.DASHBOARD_MAIN_TAKEAWAY
    assert "not as a trading system" in app.DASHBOARD_USE_NOTE


def test_overview_framing_answers_main_project_question():
    assert "geopolitical risk jumps" in app.CENTRAL_PROJECT_QUESTION
    assert "rank downside risk" in app.CENTRAL_PROJECT_QUESTION
    assert app.OVERVIEW_JOB_STATEMENTS == [
        (
            "Explanation",
            "Do markets look worse around geopolitical-risk shocks?",
        ),
        (
            "Prediction",
            "Does geopolitical risk help rank ETF-country observations by short-term drawdown risk?",
        ),
    ]

    assert list(app.METHOD_MAP_ROWS[0]) == ["Question", "Tool", "Output", "What to look for"]
    assert [row["Tool"] for row in app.METHOD_MAP_ROWS] == [
        "Event study",
        "Panel regression",
        "Quantile regression",
        "Local projection",
        "Prediction Lab",
        "Monthly benchmark",
    ]

    answer_copy = " ".join(app.OVERVIEW_CURRENT_ANSWER_POINTS)
    assert "associated with equity-market risk" in answer_copy
    assert "emerging-market asymmetry is mixed" in answer_copy
    assert "modest ranking signal" in answer_copy
    assert "GPR alone is weak" in answer_copy

    does_not_prove_copy = " ".join(app.OVERVIEW_DOES_NOT_PROVE_POINTS)
    for claim_boundary in [
        "causality",
        "investment advice",
        "trading system",
        "emerging markets always react more",
    ]:
        assert claim_boundary in does_not_prove_copy


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
