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
