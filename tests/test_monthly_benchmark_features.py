import numpy as np
import pandas as pd
import pytest

from gprobs.features.monthly_panel import build_monthly_analysis_panel
from gprobs.features.monthly_returns import make_forward_returns
from gprobs.features.shocks import make_gpr_shock_features


def test_make_forward_returns_uses_only_future_months():
    returns = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=4, freq="MS"),
            "market_id": ["developed"] * 4,
            "excess_return": [1.0, 2.0, 3.0, 4.0],
        }
    )

    result = make_forward_returns(returns, [1, 3])

    np.testing.assert_allclose(result["ret_fwd_1m"], [2.0, 3.0, 4.0, np.nan])
    np.testing.assert_allclose(result["ret_fwd_3m"], [9.0, np.nan, np.nan, np.nan])


def test_make_forward_returns_rejects_missing_calendar_months():
    returns = pd.DataFrame(
        {
            "date_month": pd.to_datetime(["2020-01-01", "2020-03-01"]),
            "market_id": ["developed", "developed"],
            "excess_return": [1.0, 3.0],
        }
    )

    with pytest.raises(ValueError, match="monthly sequence"):
        make_forward_returns(returns, [1])


def test_make_gpr_shock_features_adds_change_and_zscore_columns():
    gpr = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=4, freq="MS"),
            "gpr_global": [100.0, 105.0, 111.0, 118.0],
            "gprt_global": [60.0, 63.0, 67.0, 70.0],
            "gpra_global": [40.0, 42.0, 44.0, 48.0],
        }
    )

    result = make_gpr_shock_features(gpr)

    assert "gpr_change" in result.columns
    assert "gpr_change_z" in result.columns
    assert "gpr_log_change_z" in result.columns
    assert result["gpr_global_z"].equals(result["gpr_level_z"])
    assert result["gpr_change"].iloc[1] == 5.0


def test_build_monthly_analysis_panel_combines_sources_and_labels_tail_returns():
    market_returns = pd.DataFrame(
        {
            "date_month": list(pd.date_range("2020-01-01", periods=3, freq="MS")) * 2,
            "market_id": ["developed"] * 3 + ["emerging"] * 3,
            "market_class": ["developed"] * 3 + ["emerging"] * 3,
            "excess_return": [1.0, 2.0, 3.0, 0.5, 1.5, 2.5],
        }
    )
    gpr = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=3, freq="MS"),
            "gpr_global": [100.0, 105.0, 110.0],
            "gprt_global": [60.0, 63.0, 66.0],
            "gpra_global": [40.0, 42.0, 44.0],
        }
    )
    gdelt = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=3, freq="MS"),
            "country_iso3": ["GLB", "GLB", "GLB"],
            "risk_index_raw": [0.0, 0.5, 1.0],
            "risk_index_zscore": [-1.0, 0.0, 1.0],
        }
    )
    macro = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=3, freq="MS"),
            "country_iso3": ["GLB", "GLB", "GLB"],
            "indicator_code": ["sample_global_cycle"] * 3,
            "value": [0.0, 0.1, 0.2],
        }
    )

    panel = build_monthly_analysis_panel(market_returns, gpr, gdelt, macro)

    assert panel["market_id"].tolist() == ["developed", "emerging"] * 3
    assert {"ret_fwd_1m", "ret_fwd_3m", "ret_fwd_6m", "gpr_change_z", "spread_em_dev"}.issubset(
        panel.columns
    )
    trailing = panel["ret_fwd_1m"].isna()
    assert trailing.any()
    assert panel.loc[trailing, "neg_ret_1m"].isna().all()
