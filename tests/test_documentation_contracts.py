from pathlib import Path

DOCS = Path("docs")


def test_phase8_documentation_files_exist():
    for filename in [
        "REPRODUCIBILITY.md",
        "DATA_SOURCES.md",
        "METHODOLOGY.md",
        "ROADMAP.md",
        "FUTURE_AGENT_HANDOFF.md",
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
