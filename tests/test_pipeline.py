from gprobs.pipeline import PIPELINE_STEPS


def test_pipeline_steps_are_in_dependency_order():
    script_names = [step.script_name for step in PIPELINE_STEPS]

    assert script_names == [
        "build_returns_panel.py",
        "build_gpr_dataset.py",
        "build_market_controls.py",
        "build_analysis_panel.py",
        "run_data_diagnostics.py",
        "run_event_study.py",
        "run_event_robustness.py",
        "run_panel_regression.py",
        "run_quantile_regression.py",
        "run_local_projections.py",
        "run_drawdown_model.py",
        "run_evidence_summary.py",
        "run_rolling_sensitivity.py",
        "plot_initial_trends.py",
    ]
