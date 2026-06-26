from pathlib import Path

DOCS = Path("docs")


def test_phase8_documentation_files_exist():
    for filename in [
        "REPRODUCIBILITY.md",
        "DATA_SOURCES.md",
        "METHODOLOGY.md",
        "ROADMAP.md",
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
