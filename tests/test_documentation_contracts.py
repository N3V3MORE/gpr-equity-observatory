from pathlib import Path

DOCS = Path("docs")
GITHUB = Path(".github")


def test_phase8_documentation_files_exist():
    for filename in [
        "REPRODUCIBILITY.md",
        "DATA_SOURCES.md",
        "METHODOLOGY.md",
        "ROADMAP.md",
        "FUTURE_AGENT_HANDOFF.md",
        "FEATURE_LOCK.md",
    ]:
        assert (DOCS / filename).exists()


def test_core_docs_explain_daily_monthly_modes_and_claim_limits():
    required_phrases = [
        "daily etf",
        "monthly benchmark",
        "sample mode",
        "real mode",
        "local only",
        "not empirical evidence",
        "not a trading system",
        "not investment advice",
        "not causal",
    ]
    combined = "\n".join(
        (DOCS / filename).read_text(encoding="utf-8")
        for filename in [
            "REPRODUCIBILITY.md",
            "DATA_SOURCES.md",
            "METHODOLOGY.md",
            "ROADMAP.md",
            "TECHNICAL_APPENDIX.md",
            "PROJECT_STATUS.md",
        ]
    ).lower()

    for phrase in required_phrases:
        assert phrase in combined


def test_profile_packaging_mentions_monthly_layer_without_overclaiming():
    profile = (DOCS / "PROFILE_PACKAGING.md").read_text(encoding="utf-8").lower()

    assert "monthly benchmark" in profile
    assert "not empirical evidence" in profile
    assert "not a country-panel proof" in profile


def test_future_agent_handoff_records_branch_checks_and_boundaries():
    handoff = (DOCS / "FUTURE_AGENT_HANDOFF.md").read_text(
        encoding="utf-8"
    ).lower()

    required_phrases = [
        "codex/pre-merge-gpr-cleanup",
        "phases 0 through 9",
        "gpr equity observatory remains the destination",
        "monthly benchmark sample mode",
        "monthly benchmark real mode",
        "uv run --all-extras ruff check .",
        "uv run --all-extras pytest",
        "headless streamlit smoke test returned http 200",
        "do not commit `config/sources.yml`",
        "no custom project mcp server",
    ]

    for phrase in required_phrases:
        assert phrase in handoff


def test_feature_lock_blocks_new_scope_without_user_unlock():
    feature_lock = (DOCS / "FEATURE_LOCK.md").read_text(
        encoding="utf-8"
    ).lower()
    handoff = (DOCS / "FUTURE_AGENT_HANDOFF.md").read_text(
        encoding="utf-8"
    ).lower()
    roadmap = (DOCS / "ROADMAP.md").read_text(encoding="utf-8").lower()

    required_feature_lock_phrases = [
        "feature locked",
        "release-hardening mode",
        "new features require an explicit user decision",
        "add fred controls",
        "add gdelt ingestion or analysis",
        "add country-specific gpr data",
        "commit raw third-party data",
        "config/sources.yml",
    ]

    for phrase in required_feature_lock_phrases:
        assert phrase in feature_lock

    assert "this branch is feature locked" in handoff
    assert "post-lock work" in roadmap


def test_github_templates_preserve_feature_lock_guardrails():
    pr_template = (GITHUB / "PULL_REQUEST_TEMPLATE.md").read_text(
        encoding="utf-8"
    ).lower()
    data_template = (GITHUB / "ISSUE_TEMPLATE" / "data_source.md").read_text(
        encoding="utf-8"
    ).lower()
    method_template = (GITHUB / "ISSUE_TEMPLATE" / "method_task.md").read_text(
        encoding="utf-8"
    ).lower()

    for template in [pr_template, data_template, method_template]:
        assert "feature-lock" in template
        assert "explicit unlock decision" in template

    required_pr_phrases = [
        "daily etf outputs and monthly benchmark outputs remain separate",
        "sample-mode outputs are not presented as empirical evidence",
        "config/sources.yml",
        "not framed as investment advice or a trading system",
        "emerging-market asymmetry is not described as a strong result",
    ]

    for phrase in required_pr_phrases:
        assert phrase in pr_template

    assert "real/sample mode cannot be confused" in data_template
    assert "daily and monthly outputs stay separate" in data_template
    assert "no causal, trading, or strong emerging-market asymmetry claim" in (
        method_template
    )


def test_public_setup_docs_share_core_commands():
    setup_docs = [
        Path("README.md"),
        DOCS / "TECHNICAL_APPENDIX.md",
        DOCS / "DEPLOYMENT_GUIDE.md",
        DOCS / "REPRODUCIBILITY_CHECKLIST.md",
    ]
    required_commands = [
        "python -m pip install -r requirements.txt",
        "uv sync --all-extras",
        "python scripts/build_all.py",
        "streamlit run app.py",
        "ruff check .",
        "pytest --cov=gprobs --cov=app --cov-report=term-missing -q",
    ]

    for doc_path in setup_docs:
        contents = doc_path.read_text(encoding="utf-8")
        for command in required_commands:
            assert command in contents, f"{command} missing from {doc_path}"
