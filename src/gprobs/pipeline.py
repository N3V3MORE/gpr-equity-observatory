from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


@dataclass(frozen=True)
class PipelineStep:
    label: str
    script_name: str


PIPELINE_STEPS = [
    PipelineStep("Build ETF returns", "build_returns_panel.py"),
    PipelineStep("Build daily GPR data", "build_gpr_dataset.py"),
    PipelineStep("Build market controls", "build_market_controls.py"),
    PipelineStep("Build combined analysis panel", "build_analysis_panel.py"),
    PipelineStep("Run data diagnostics", "run_data_diagnostics.py"),
    PipelineStep("Run event studies", "run_event_study.py"),
    PipelineStep("Run panel regressions", "run_panel_regression.py"),
    PipelineStep("Run quantile regressions", "run_quantile_regression.py"),
    PipelineStep("Run local projections", "run_local_projections.py"),
    PipelineStep("Run drawdown model", "run_drawdown_model.py"),
    PipelineStep("Run rolling GPR sensitivity", "run_rolling_sensitivity.py"),
    PipelineStep("Plot initial trends", "plot_initial_trends.py"),
]


def run_pipeline(project_root: Path, python_executable: str = sys.executable) -> None:
    """Run the full reproducible MVP pipeline in dependency order."""
    scripts_dir = project_root / "scripts"

    for step in PIPELINE_STEPS:
        script_path = scripts_dir / step.script_name
        print(f"\n==> {step.label}", flush=True)
        subprocess.run(
            [python_executable, str(script_path)],
            cwd=project_root,
            check=True,
        )
