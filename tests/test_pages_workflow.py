"""Security and artifact-handoff contracts for the manual Pages release."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _workflow():
    # BaseLoader preserves GitHub's `on` key instead of treating it as YAML 1.1 bool.
    return yaml.load(
        (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )


def test_pages_release_is_manual_and_only_from_main():
    workflow = _workflow()
    assert set(workflow["on"]) == {"workflow_dispatch"}
    assert workflow["on"]["workflow_dispatch"] == ""
    assert workflow["permissions"] == {}
    assert workflow["concurrency"]["cancel-in-progress"] == "false"
    for job in workflow["jobs"].values():
        assert job["if"] == (
            "github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main'"
        )
    checkout = workflow["jobs"]["build"]["steps"][0]
    assert checkout["with"]["ref"] == "${{ github.sha }}"
    assert checkout["with"]["persist-credentials"] == "false"


def test_pages_separates_build_and_protected_deployment_permissions():
    jobs = _workflow()["jobs"]
    assert jobs["build"]["permissions"] == {"contents": "read"}
    deploy = jobs["deploy"]
    assert deploy["permissions"] == {"pages": "write", "id-token": "write"}
    assert deploy["needs"] == "build"
    assert deploy["environment"] == {
        "name": "github-pages",
        "url": "${{ steps.deployment.outputs.page_url }}",
    }
    configuration = next(
        step for step in deploy["steps"] if "actions/configure-pages@" in step.get("uses", "")
    )
    assert configuration["with"] == {"enablement": "false"}
    assert any(
        step.get("run") == 'test "$CONFIGURED_BASE_PATH" = "$NEXT_PUBLIC_BASE_PATH"'
        for step in deploy["steps"]
    )


def test_pages_uploads_once_only_after_all_real_release_gates():
    workflow = _workflow()
    build = workflow["jobs"]["build"]
    assert build["defaults"]["run"]["working-directory"] == "frontend"
    assert workflow["env"]["NEXT_PUBLIC_BASE_PATH"] == "/gpr-equity-observatory"
    steps = build["steps"]
    commands = [step["run"] for step in steps if "run" in step]
    assert commands == [
        "git ls-files --error-unmatch publication/approved-snapshot.json",
        "npm ci --strict-peer-deps",
        "npm run snapshot:validate -- --tracked",
        "npm run snapshot:stage",
        "npm run checks",
        "npx playwright install --with-deps chromium",
        "npm run build:public",
        "npm run test:browser",
        "npm run snapshot:artifact",
    ]
    browser = next(step for step in steps if step.get("run") == "npm run test:browser")
    assert browser["env"] == {"GPR_BROWSER_PUBLICATION": "1"}
    uploads = [step for step in steps if "actions/upload-pages-artifact@" in step.get("uses", "")]
    assert len(uploads) == 1
    assert steps[-1] == uploads[0]
    assert steps[-2]["run"] == "npm run snapshot:artifact"
    assert uploads[0]["with"]["path"] == "frontend/out"
    deploy = workflow["jobs"]["deploy"]["steps"][-1]
    assert deploy["uses"].startswith("actions/deploy-pages@")
    assert deploy["with"]["artifact_name"] == uploads[0]["with"]["name"]


def test_pages_uses_pinned_official_actions_and_does_not_rebuild_during_deploy():
    workflow = _workflow()
    for job in workflow["jobs"].values():
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"actions/[a-z-]+@[0-9a-f]{40}", step["uses"])
    deploy_steps = workflow["jobs"]["deploy"]["steps"]
    assert len(deploy_steps) == 3
    assert not any("checkout" in step.get("uses", "") for step in deploy_steps)
    assert not any("npm" in step.get("run", "") for step in deploy_steps)


def test_existing_python_and_deterministic_monthly_jobs_remain_in_ci():
    workflow = yaml.load(
        (ROOT / ".github/workflows/tests.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    python = workflow["jobs"]["pytest"]
    assert python["strategy"]["matrix"]["os"] == ["ubuntu-latest", "windows-latest"]
    python_commands = "\n".join(step.get("run", "") for step in python["steps"])
    assert "ruff check ." in python_commands
    assert "pytest --cov=gprobs --cov=app --cov-report=term-missing -q" in python_commands
    monthly = workflow["jobs"]["monthly-sample-pipeline"]
    assert any(
        "monthly-sample --min-train-months 24" in step.get("run", "")
        for step in monthly["steps"]
    )
    frontend = workflow["jobs"]["frontend"]
    assert frontend["strategy"]["matrix"]["base-path"] == ["", "/gpr-equity-observatory"]
    assert frontend["env"]["NEXT_PUBLIC_BASE_PATH"] == "${{ matrix.base-path }}"
    frontend_commands = "\n".join(step.get("run", "") for step in frontend["steps"])
    for command in ["npm run lint", "npm run typecheck", "npm run test:runtime",
                    "npm run build:test", "npm run test:browser"]:
        assert command in frontend_commands
    for excluded in ["build_all.py", "build-daily", "download", "yfinance"]:
        assert excluded not in frontend_commands
    assert not any("upload" in step.get("uses", "") for step in frontend["steps"])
    assert "GPR_BROWSER_PUBLICATION" not in frontend["env"]
