import subprocess

import pytest

from scripts import run_task


def test_run_task_build_monthly_sample_dispatches_root(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, cwd, check=False):
        calls.append((command, cwd, check))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(run_task.subprocess, "run", fake_run)

    assert run_task.run_task("build-monthly-sample", root=tmp_path) == 0

    assert calls == [
        (
            [
                run_task.sys.executable,
                "scripts/build_monthly_benchmark_sample.py",
                "--root",
                str(tmp_path),
            ],
            run_task.PROJECT_ROOT,
            False,
        )
    ]


def test_run_task_propagates_failed_command(monkeypatch, tmp_path):
    def fake_run(command, cwd, check=False):
        return subprocess.CompletedProcess(command, 9)

    monkeypatch.setattr(run_task.subprocess, "run", fake_run)

    assert run_task.run_task("lint", root=tmp_path) == 9


def test_run_task_rejects_unknown_task():
    with pytest.raises(ValueError, match="unknown task"):
        run_task.run_task("not-a-task")


def test_run_task_all_includes_monthly_sample_validation(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, cwd, check=False):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(run_task.subprocess, "run", fake_run)

    assert run_task.run_task("all", root=tmp_path, min_train_months=24) == 0

    command_text = [" ".join(str(part) for part in command) for command in calls]
    assert any("build_monthly_benchmark_sample.py" in command for command in command_text)
    assert any("validate_monthly_benchmark.py" in command for command in command_text)
    assert any("--check-results" in command for command in command_text)


def test_run_task_monthly_real_pipeline_dispatches_full_local_workflow(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, cwd, check=False):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(run_task.subprocess, "run", fake_run)

    assert (
        run_task.run_task(
            "monthly-real",
            root=tmp_path,
            horizons="1,6",
            min_train_months=36,
            min_overlap_months=30,
            min_forecast_train_months=36,
        )
        == 0
    )

    command_text = [" ".join(str(part) for part in command) for command in calls]
    assert len(calls) == 5
    assert "build_monthly_benchmark_real.py" in command_text[0]
    assert f"--config {tmp_path / run_task.DEFAULT_CONFIG}" in command_text[0]
    assert "validate_monthly_benchmark.py --dataset monthly_benchmark_real" in command_text[1]
    assert "--min-overlap-months 30" in command_text[1]
    assert "run_monthly_benchmark_regressions.py --dataset monthly_benchmark_real" in command_text[2]
    assert "--horizons 1,6" in command_text[2]
    assert "run_monthly_benchmark_forecasts.py --dataset monthly_benchmark_real" in command_text[3]
    assert "--min-train-months 36" in command_text[3]
    assert "validate_monthly_benchmark.py --dataset monthly_benchmark_real --check-results" in command_text[4]
    assert "--min-forecast-train-months 36" in command_text[4]


def test_run_task_exposes_real_monthly_result_tasks(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, cwd, check=False):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(run_task.subprocess, "run", fake_run)

    assert run_task.run_task("run-monthly-regressions-real", root=tmp_path, horizons="3") == 0
    assert run_task.run_task("run-monthly-forecasts-real", root=tmp_path, min_train_months=48) == 0
    assert run_task.run_task("validate-monthly-real-results", root=tmp_path) == 0

    command_text = [" ".join(str(part) for part in command) for command in calls]
    assert "run_monthly_benchmark_regressions.py --dataset monthly_benchmark_real" in command_text[0]
    assert "--horizons 3" in command_text[0]
    assert "run_monthly_benchmark_forecasts.py --dataset monthly_benchmark_real" in command_text[1]
    assert "--min-train-months 48" in command_text[1]
    assert "validate_monthly_benchmark.py --dataset monthly_benchmark_real --check-results" in command_text[2]
