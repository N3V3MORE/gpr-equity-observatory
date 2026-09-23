import json
from pathlib import Path

from scripts import run_task

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_frontend_coverage_artifacts_are_ignored():
    gitignore = _read(".gitignore")

    assert ".coverage" in gitignore
    assert ".coverage.*" in gitignore


def test_frontend_checks_are_available_in_task_runner():
    assert "frontend-lint" in run_task.TASK_COMMANDS
    assert "frontend-build" in run_task.TASK_COMMANDS
    assert "export-frontend" in run_task.TASK_COMMANDS
    assert "dashboard" not in run_task.TASK_COMMANDS

    all_pipeline = run_task.PIPELINES["all"]
    assert all_pipeline.index("export-frontend") < all_pipeline.index("frontend-lint")
    assert "frontend-lint" in all_pipeline
    assert "frontend-build" in all_pipeline


def test_frontend_checks_are_enforced_in_ci_and_pr_template():
    workflow = _read(".github/workflows/tests.yml")
    pr_template = _read(".github/PULL_REQUEST_TEMPLATE.md")

    for expected in ["actions/setup-node", "npm ci", "npm run lint", "npm run build"]:
        assert expected in workflow

    assert "`npm run lint` passes" in pr_template
    assert "`npm run build` passes" in pr_template


def test_frontend_static_data_urls_support_base_path():
    next_config = _read("frontend/next.config.mjs")
    data_module = _read("frontend/src/lib/data.ts")

    assert "NEXT_PUBLIC_BASE_PATH" in next_config
    assert "NEXT_PUBLIC_BASE_PATH" in data_module
    assert '"/data"' not in data_module


def test_frontend_runtime_checks_are_available():
    package = json.loads(_read("frontend/package.json"))

    assert "test:runtime" in package["scripts"]
    assert list((ROOT / "frontend" / "tests").glob("*.test.cjs"))


def test_rolling_sensitivity_loads_only_when_revealed():
    lazy_component = _read("frontend/src/components/LazyRollingBeta.tsx")
    charts = _read("frontend/src/components/charts.tsx")

    assert "IntersectionObserver" in lazy_component
    assert "rootMargin" in lazy_component
    assert "setShouldLoad(true)" in lazy_component
    assert "Loading country sensitivity" not in lazy_component
    assert "Build the index once" in charts


def test_wide_evidence_table_cannot_force_mobile_page_overflow():
    table = _read("frontend/src/components/DataTable.tsx")

    assert "overflow-x-auto" in table
    assert 'className="w-full border-collapse text-sm"' in table


def test_static_research_introduction_precedes_client_evidence():
    page = _read("frontend/src/app/page.tsx")

    assert '"use client"' not in page
    assert page.index("How are geopolitical risk jumps associated") < page.index("Research limitations:")
    assert page.index("Research limitations:") < page.index("<ResearchDashboard")


def test_snapshot_answer_precedes_evidence_and_methods():
    overview = _read("frontend/src/sections/Overview.tsx")
    dashboard = _read("frontend/src/components/ResearchDashboard.tsx")
    methods = _read("frontend/src/sections/DataAndMethods.tsx")

    assert overview.index("Candidate estimates") < overview.index("Daily geopolitical risk over time")
    assert dashboard.index("<Overview") < dashboard.index("<HowMarketsReact") < dashboard.index("<DataAndMethods")
    assert "How the evidence is estimated" in methods
    assert "copy.reader_path" not in overview


def test_section_nav_scroll_is_contained_on_mobile():
    section_nav = _read("frontend/src/components/SectionNav.tsx")

    assert "overflow-x-hidden" in section_nav
    assert "w-full" in section_nav
    assert "max-w-full" in section_nav


def test_page_shell_clips_mobile_table_overflow():
    page = _read("frontend/src/app/page.tsx")

    assert '<main id="research-content" tabIndex={-1} className="overflow-x-hidden focus:outline-none">' in page


def test_reader_summaries_are_rendered():
    how_markets = _read("frontend/src/sections/HowMarketsReact.tsx")
    data_methods = _read("frontend/src/sections/DataAndMethods.tsx")

    assert "bundle.reader_summaries.market_reaction" in how_markets
    assert "MARKET_REACTION_READER_COLUMNS" in how_markets
    assert "bundle.reader_summaries.regression_translation" in how_markets
    assert "REGRESSION_TRANSLATION_COLUMNS" in how_markets
    assert "bundle.reader_summaries.output_files" in data_methods
    assert "OUTPUT_FILE_READER_COLUMNS" in data_methods


def test_prediction_lab_leads_with_lift_graph_before_model_table():
    prediction_lab = _read("frontend/src/sections/PredictionLab.tsx")

    assert prediction_lab.index("Bad-outcome lift by risk bucket") < prediction_lab.index("Model comparison")
    assert prediction_lab.index("Bottom line") < prediction_lab.index("Model comparison")
