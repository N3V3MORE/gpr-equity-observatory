from pathlib import Path

DOCS = Path("docs")
GITHUB = Path(".github")
PUBLIC_REVIEWER_DOCS = [
    Path("README.md"),
    DOCS / "PROJECT_STATUS.md",
    DOCS / "REVIEWER_GUIDE.md",
    DOCS / "TECHNICAL_APPENDIX.md",
    DOCS / "REPRODUCIBILITY_CHECKLIST.md",
]


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
    assert (DOCS / "internal" / "REVIEW_CONTEXT_FOR_AI_TOOLS.md").exists()


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


def test_feature_unlock_records_scope_and_preserves_guardrails():
    feature_lock = (DOCS / "FEATURE_LOCK.md").read_text(
        encoding="utf-8"
    ).lower()
    handoff = (DOCS / "FUTURE_AGENT_HANDOFF.md").read_text(
        encoding="utf-8"
    ).lower()
    roadmap = (DOCS / "ROADMAP.md").read_text(encoding="utf-8").lower()

    required_feature_unlock_phrases = [
        "status: lifted",
        "feature work is now unlocked",
        "record the chosen scope",
        "fred controls",
        "gdelt",
        "country-specific gpr",
        "raw third-party market data",
        "config/sources.yml",
    ]

    for phrase in required_feature_unlock_phrases:
        assert phrase in feature_lock

    assert "feature lock was lifted" in handoff
    assert "future work is open" in roadmap
    assert "explicit user request" not in roadmap


def test_github_templates_preserve_scope_guardrails():
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
        assert "scope" in template
        assert "scoped plan, issue, or pr description" in template

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


def test_release_hardening_issue_template_preserves_release_scope():
    release_template = (
        GITHUB / "ISSUE_TEMPLATE" / "release_hardening.md"
    ).read_text(encoding="utf-8").lower()

    required_phrases = [
        "release hardening",
        "scope and guardrail check",
        "preserves the current release baseline",
        "no new research, data, model, dashboard, or product behavior",
        "scoped plan, issue, or pr description",
        "config/sources.yml",
        "not framed as investment advice or a trading system",
        "sample-mode outputs are not presented as empirical evidence",
        "ruff check .",
        "pytest --cov=gprobs --cov=app --cov-report=term-missing -q",
    ]

    for phrase in required_phrases:
        assert phrase in release_template


def test_github_issue_template_config_routes_reviewers_to_docs():
    issue_config = (GITHUB / "ISSUE_TEMPLATE" / "config.yml").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "blank_issues_enabled: false",
        "contact_links:",
        "Reviewer guide",
        "docs/REVIEWER_GUIDE.md",
        "Roadmap and backlog",
        "docs/ROADMAP.md",
        "Reproducibility checklist",
        "docs/REPRODUCIBILITY_CHECKLIST.md",
    ]

    for phrase in required_phrases:
        assert phrase in issue_config


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


def test_monthly_real_workflow_docs_cover_full_local_pipeline():
    docs_to_check = [
        Path("README.md"),
        DOCS / "REPRODUCIBILITY_CHECKLIST.md",
    ]
    required_phrases = [
        "python scripts/run_task.py monthly-real",
        "python scripts/run_task.py run-monthly-regressions-real",
        "python scripts/run_task.py run-monthly-forecasts-real",
        "python scripts/run_task.py validate-monthly-real-results",
        "config/sources.yml",
        "local-only",
    ]

    for doc_path in docs_to_check:
        contents = doc_path.read_text(encoding="utf-8").lower()
        for phrase in required_phrases:
            assert phrase in contents, f"{phrase} missing from {doc_path}"


def test_public_reviewer_path_avoids_internal_ai_workflow_docs():
    for doc_path in PUBLIC_REVIEWER_DOCS:
        contents = doc_path.read_text(encoding="utf-8").lower()
        assert "chatgpt" not in contents, f"internal AI review path leaked into {doc_path}"
        assert "future_agent_handoff" not in contents, f"agent handoff leaked into {doc_path}"
        assert "future-agent" not in contents, f"agent wording leaked into {doc_path}"
        assert "explicit user request" not in contents, f"chat-history wording leaked into {doc_path}"


def test_internal_ai_review_context_routes_safe_context():
    guide = (DOCS / "internal" / "REVIEW_CONTEXT_FOR_AI_TOOLS.md").read_text(
        encoding="utf-8"
    ).lower()

    required_phrases = [
        "best files to upload or paste",
        "what not to upload",
        "config/sources.yml",
        "raw third-party market data",
        "daily etf workflow",
        "monthly benchmark workflow",
        "prediction lab",
        "out-of-sample prediction rows",
        "not a trading system",
        "verification commands",
    ]

    for phrase in required_phrases:
        assert phrase in guide


def test_committed_docs_do_not_leak_local_paths():
    docs_to_scan = [
        Path("README.md"),
        Path("AGENTS.md"),
        *DOCS.rglob("*.md"),
        *DOCS.rglob("*.txt"),
    ]
    forbidden_patterns = [
        "c:\\users\\",
        "/users/",
        "desktop\\code",
    ]

    for doc_path in docs_to_scan:
        contents = doc_path.read_text(encoding="utf-8").lower()
        for pattern in forbidden_patterns:
            assert pattern not in contents, f"{pattern} leaked into {doc_path}"
