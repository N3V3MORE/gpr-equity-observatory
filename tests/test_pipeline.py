from gprobs.pipeline import PIPELINE_STEPS, run_pipeline


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
        "run_panel_sample_robustness.py",
        "run_quantile_regression.py",
        "run_local_projections.py",
        "run_drawdown_model.py",
        "run_evidence_summary.py",
        "run_rolling_sensitivity.py",
        "write_results_brief.py",
        "plot_initial_trends.py",
    ]


def test_run_pipeline_passes_refresh_to_network_download_steps(monkeypatch, tmp_path):
    calls = []

    def fake_run(args, cwd, check):
        calls.append(args)

    monkeypatch.setattr("gprobs.pipeline.subprocess.run", fake_run)

    run_pipeline(tmp_path, python_executable="python", refresh=True)

    args_by_script = {call[1].name: call for call in calls}
    assert args_by_script["build_returns_panel.py"][-1] == "--refresh"
    assert args_by_script["build_gpr_dataset.py"][-1] == "--refresh"
    assert args_by_script["build_market_controls.py"][-1] == "--refresh"
    assert args_by_script["build_analysis_panel.py"][-1] != "--refresh"
