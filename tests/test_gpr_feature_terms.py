from pathlib import Path

from gprobs.analysis import drawdown_model, panel_regression
from gprobs.data import gpr_data
from gprobs.features import shocks
from gprobs.features.gpr_terms import (
    EXPANDING_GPR_CHANGE_SHOCK_COLUMN,
    GPR_CHANGE_Z_COLUMN,
    GPR_CHANGE_Z_CONTEXTS,
    LEGACY_GPR_SHOCK_ALIASES,
    PREFERRED_GPR_SHOCK_COLUMN,
)


def test_gpr_feature_terms_document_overloaded_z_score_contexts():
    daily = GPR_CHANGE_Z_CONTEXTS["daily_descriptive"]
    panel = GPR_CHANGE_Z_CONTEXTS["panel_regression"]
    prediction = GPR_CHANGE_Z_CONTEXTS["prediction_lab_expanding"]
    monthly = GPR_CHANGE_Z_CONTEXTS["monthly_descriptive"]

    assert {daily.column, panel.column, prediction.column, monthly.column} == {GPR_CHANGE_Z_COLUMN}
    assert daily.time_aware is False
    assert monthly.time_aware is False
    assert panel.time_aware is False
    assert prediction.time_aware is True
    assert "full-sample" in daily.standardization.lower()
    assert "regression sample" in panel.standardization.lower()
    assert "prior expanding" in prediction.standardization.lower()


def test_code_modules_pin_gpr_feature_contexts_without_renaming_outputs():
    assert gpr_data.DAILY_GPR_CHANGE_Z_CONTEXT is GPR_CHANGE_Z_CONTEXTS["daily_descriptive"]
    assert shocks.MONTHLY_GPR_CHANGE_Z_CONTEXT is GPR_CHANGE_Z_CONTEXTS["monthly_descriptive"]
    assert panel_regression.PANEL_GPR_CHANGE_Z_CONTEXT is GPR_CHANGE_Z_CONTEXTS["panel_regression"]
    assert drawdown_model.PREDICTION_LAB_GPR_CHANGE_Z_CONTEXT is GPR_CHANGE_Z_CONTEXTS[
        "prediction_lab_expanding"
    ]
    assert drawdown_model.GPR_FEATURE_COLUMNS == [
        GPR_CHANGE_Z_COLUMN,
        EXPANDING_GPR_CHANGE_SHOCK_COLUMN,
    ]
    assert PREFERRED_GPR_SHOCK_COLUMN == EXPANDING_GPR_CHANGE_SHOCK_COLUMN
    assert {"gpr_change_shock", "gpr_shock", "gpr_shock_expanding"}.issubset(
        LEGACY_GPR_SHOCK_ALIASES
    )


def test_gpr_feature_definitions_doc_explains_contributor_safe_usage():
    contents = Path("docs/GPR_FEATURE_DEFINITIONS.md").read_text(encoding="utf-8").lower()

    required_phrases = [
        "daily descriptive z-score",
        "panel regression z-score",
        "prediction lab expanding z-score",
        "prior expanding",
        "not time-aware",
        "time-aware",
        "`gpr_change_shock_expanding`",
        "`gpr_change_shock`",
        "`gpr_shock`",
        "compatibility alias",
        "do not rename output columns",
    ]

    for phrase in required_phrases:
        assert phrase in contents
