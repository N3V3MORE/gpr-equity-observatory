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


def test_rolling_sensitivity_loads_only_when_revealed():
    lazy_component = _read("frontend/src/components/LazyRollingBeta.tsx")
    charts = _read("frontend/src/components/charts.tsx")

    assert "IntersectionObserver" in lazy_component
    assert "rootMargin" in lazy_component
    assert "setShouldLoad(true)" in lazy_component
    assert "Loading country sensitivity" not in lazy_component
    assert "Build the index once" in charts


def test_wide_evidence_table_cannot_force_mobile_page_overflow():
    overview = _read("frontend/src/sections/Overview.tsx")

    assert "min-w-0" in overview


def test_overview_renders_beginner_reader_path_before_method_map():
    overview = _read("frontend/src/sections/Overview.tsx")

    assert "copy.reader_path" in overview
    assert "Read this first" in overview
    assert overview.index("Read this first") < overview.index("Method map")


def test_overview_leads_with_gpr_graph_before_method_map():
    overview = _read("frontend/src/sections/Overview.tsx")

    assert overview.index("Daily geopolitical risk over time") < overview.index("Method map")


def test_section_nav_scroll_is_contained_on_mobile():
    section_nav = _read("frontend/src/components/SectionNav.tsx")

    assert "overflow-x-hidden" in section_nav
    assert "w-full" in section_nav
    assert "max-w-full" in section_nav


def test_page_shell_clips_mobile_table_overflow():
    page = _read("frontend/src/app/page.tsx")

    assert '<main className="overflow-x-hidden">' in page


def test_reader_summaries_are_loaded_and_rendered():
    data_module = _read("frontend/src/lib/data.ts")
    how_markets = _read("frontend/src/sections/HowMarketsReact.tsx")
    data_methods = _read("frontend/src/sections/DataAndMethods.tsx")

    assert "reader_summaries.json" in data_module
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
