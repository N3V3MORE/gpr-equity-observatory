import argparse
import subprocess
import sys
from pathlib import Path

from gprobs.data.datasets import MONTHLY_BENCHMARK_REAL, MONTHLY_BENCHMARK_SAMPLE

DEFAULT_CONFIG = "config/sources.yml"
PROJECT_ROOT = Path(__file__).resolve().parents[1]

TASK_COMMANDS = {
    "setup": [[sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]],
    "build-daily": [[sys.executable, "scripts/build_all.py"]],
    "build-fred": [[sys.executable, "scripts/build_fred_macro_controls.py"]],
    "build-monthly-sample": [[sys.executable, "scripts/build_monthly_benchmark_sample.py"]],
    "build-monthly-real": [[sys.executable, "scripts/build_monthly_benchmark_real.py", "--config", DEFAULT_CONFIG]],
    "validate-daily": [[sys.executable, "scripts/run_data_diagnostics.py"]],
    "validate-monthly-sample": [
        [sys.executable, "scripts/validate_monthly_benchmark.py", "--dataset", MONTHLY_BENCHMARK_SAMPLE]
    ],
    "validate-monthly-real": [
        [sys.executable, "scripts/validate_monthly_benchmark.py", "--dataset", MONTHLY_BENCHMARK_REAL]
    ],
    "run-monthly-regressions-sample": [
        [sys.executable, "scripts/run_monthly_benchmark_regressions.py", "--dataset", MONTHLY_BENCHMARK_SAMPLE]
    ],
    "run-monthly-regressions-real": [
        [sys.executable, "scripts/run_monthly_benchmark_regressions.py", "--dataset", MONTHLY_BENCHMARK_REAL]
    ],
    "run-monthly-forecasts-sample": [
        [sys.executable, "scripts/run_monthly_benchmark_forecasts.py", "--dataset", MONTHLY_BENCHMARK_SAMPLE]
    ],
    "run-monthly-forecasts-real": [
        [sys.executable, "scripts/run_monthly_benchmark_forecasts.py", "--dataset", MONTHLY_BENCHMARK_REAL]
    ],
    "validate-monthly-sample-results": [
        [
            sys.executable,
            "scripts/validate_monthly_benchmark.py",
            "--dataset",
            MONTHLY_BENCHMARK_SAMPLE,
            "--check-results",
        ]
    ],
    "validate-monthly-real-results": [
        [
            sys.executable,
            "scripts/validate_monthly_benchmark.py",
            "--dataset",
            MONTHLY_BENCHMARK_REAL,
            "--check-results",
        ]
    ],
    "dashboard": [[sys.executable, "-m", "streamlit", "run", "app.py"]],
    "test": [[sys.executable, "-m", "pytest", "--cov=gprobs", "--cov=app", "--cov-report=term-missing", "-q"]],
    "lint": [[sys.executable, "-m", "ruff", "check", "."]],
}

PIPELINES = {
    "all": [
        "build-daily",
        "build-monthly-sample",
        "validate-monthly-sample",
        "run-monthly-regressions-sample",
        "run-monthly-forecasts-sample",
        "validate-monthly-sample-results",
        "lint",
        "test",
    ],
    "monthly-sample": [
        "build-monthly-sample",
        "validate-monthly-sample",
        "run-monthly-regressions-sample",
        "run-monthly-forecasts-sample",
        "validate-monthly-sample-results",
    ],
    "monthly-real": [
        "build-monthly-real",
        "validate-monthly-real",
        "run-monthly-regressions-real",
        "run-monthly-forecasts-real",
        "validate-monthly-real-results",
    ],
}

ROOT_AWARE_SCRIPTS = {
    "scripts/build_fred_macro_controls.py",
    "scripts/build_monthly_benchmark_sample.py",
    "scripts/build_monthly_benchmark_real.py",
    "scripts/validate_monthly_benchmark.py",
    "scripts/run_monthly_benchmark_regressions.py",
    "scripts/run_monthly_benchmark_forecasts.py",
}


def run_task(
    name: str,
    root: Path | None = None,
    *,
    config: str = DEFAULT_CONFIG,
    horizons: str = "1,3,6",
    min_train_months: int = 120,
    min_overlap_months: int = 24,
    min_forecast_train_months: int = 24,
) -> int:
    task_names = PIPELINES.get(name, [name])
    root = Path(root) if root is not None else PROJECT_ROOT
    for task_name in task_names:
        if task_name not in TASK_COMMANDS:
            valid = ", ".join(sorted([*TASK_COMMANDS, *PIPELINES]))
            raise ValueError(f"unknown task '{task_name}'. Valid tasks: {valid}")
        for command in TASK_COMMANDS[task_name]:
            command_with_options = _command_with_options(
                command,
                config=_rooted_default_config(config, root),
                horizons=horizons,
                min_train_months=min_train_months,
                min_overlap_months=min_overlap_months,
                min_forecast_train_months=min_forecast_train_months,
            )
            result = subprocess.run(_command_with_root(command_with_options, root), cwd=PROJECT_ROOT, check=False)
            if result.returncode != 0:
                return result.returncode
    return 0


def _command_with_options(
    command: list[str],
    *,
    config: str,
    horizons: str,
    min_train_months: int,
    min_overlap_months: int,
    min_forecast_train_months: int,
) -> list[str]:
    if len(command) < 2:
        return command
    script = command[1].replace("\\", "/")
    result = list(command)
    if script == "scripts/build_monthly_benchmark_real.py":
        result = _replace_option(result, "--config", config)
    if script == "scripts/run_monthly_benchmark_regressions.py":
        result = _append_missing_option(result, "--horizons", horizons)
    if script == "scripts/run_monthly_benchmark_forecasts.py":
        result = _append_missing_option(result, "--min-train-months", str(min_train_months))
    if script == "scripts/validate_monthly_benchmark.py":
        result = _append_missing_option(result, "--min-overlap-months", str(min_overlap_months))
        result = _append_missing_option(result, "--min-forecast-train-months", str(min_forecast_train_months))
    return result


def _rooted_default_config(config: str, root: Path) -> str:
    if config != DEFAULT_CONFIG:
        return config
    return str(root / config)


def _command_with_root(command: list[str], root: Path) -> list[str]:
    if len(command) < 2:
        return command
    script = command[1].replace("\\", "/")
    if script not in ROOT_AWARE_SCRIPTS:
        return command
    return [*command, "--root", str(root)]


def _replace_option(command: list[str], option: str, value: str) -> list[str]:
    if option not in command:
        return [*command, option, value]
    index = command.index(option)
    return [*command[: index + 1], value, *command[index + 2 :]]


def _append_missing_option(command: list[str], option: str, value: str) -> list[str]:
    if option in command:
        return command
    return [*command, option, value]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GPR Equity Observatory project tasks.")
    parser.add_argument("task", choices=sorted([*TASK_COMMANDS, *PIPELINES]))
    parser.add_argument("--root", default=None)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--horizons", default="1,3,6")
    parser.add_argument("--min-train-months", type=int, default=120)
    parser.add_argument("--min-overlap-months", type=int, default=24)
    parser.add_argument("--min-forecast-train-months", type=int, default=24)
    args = parser.parse_args()
    raise SystemExit(
        run_task(
            args.task,
            root=Path(args.root) if args.root else None,
            config=args.config,
            horizons=args.horizons,
            min_train_months=args.min_train_months,
            min_overlap_months=args.min_overlap_months,
            min_forecast_train_months=args.min_forecast_train_months,
        )
    )


if __name__ == "__main__":
    main()
