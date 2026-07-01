from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_beginner_restart_files_are_present():
    assert (ROOT / "app_restart.py").exists()
    assert (ROOT / "app_dev_cockpit.py").exists()
    assert (ROOT / "docs/beginner/00_START_HERE.md").exists()
    assert (ROOT / "docs/beginner/10_FOLDER_MAP.md").exists()


def test_beginner_layer_keeps_public_app_boundary_visible():
    agents = _read("AGENTS.md")
    scope = _read("docs/BEGINNER_RESTART_SCOPE.md")
    start_here = _read("docs/beginner/00_START_HERE.md")

    assert "Beginner Restart Layer" in agents
    assert "local" in agents
    assert "beginner layer" in agents
    assert "They do not replace the public" in scope
    assert "public app still lives in `frontend/`" in start_here


def test_beginner_apps_use_cautious_reader_labels():
    app = _read("app_restart.py")

    assert 'return "Strong"' not in app
    assert "Useful signal" not in app
    assert '"Confidence"' not in app
    assert "Conventional p < 0.05" in app
    assert "Risk-ranking experiment only" in app
    assert "What not to claim" in app
    assert "drawdown_model_lift.csv" in app
    assert "Lift table" in app


def test_dev_cockpit_uses_project_task_runner_for_broad_tasks():
    cockpit = _read("app_dev_cockpit.py")

    assert "scripts/run_task.py" in cockpit
    assert "build-daily" in cockpit
    assert "export-frontend" in cockpit
    assert "st.progress" in cockpit
    assert "PIPELINE_STEPS" not in cockpit


def test_beginner_command_docs_use_locked_environment():
    commands = _read("docs/beginner/08_RUNNING_COMMANDS.md")

    assert "uv sync --all-extras" in commands
    assert "uv run --all-extras python scripts/run_task.py build-daily" in commands
    assert "python -m pip install -r requirements.txt" not in commands
