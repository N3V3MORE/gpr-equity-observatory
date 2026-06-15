import pandas as pd

from gprobs.analysis.panel_regression import (
    prepare_panel_regression_data,
    run_baseline_panel_regression,
    run_controlled_panel_regression,
    run_date_fe_panel_regression,
    tidy_regression_results,
)


def test_prepare_panel_regression_data_adds_emerging_flag_and_standardized_gpr_change():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-03",
                ]
            ),
            "ticker": ["SPY", "EWZ"] * 3,
            "market_group": ["developed", "emerging"] * 3,
            "return": [0.01, -0.02, 0.03, -0.01, 0.02, -0.03],
            "gpr": [100.0, 100.0, 200.0, 200.0, 150.0, 150.0],
        }
    )

    prepared = prepare_panel_regression_data(panel)

    assert prepared["emerging_market"].tolist() == [0, 1, 0, 1]
    assert round(prepared["gpr_change_z"].mean(), 10) == 0
    assert {"date", "ticker", "return", "gpr_change_z", "emerging_market"}.issubset(
        prepared.columns
    )


def test_run_baseline_panel_regression_estimates_expected_terms():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-04",
                ]
            ),
            "ticker": ["SPY", "EWZ"] * 4,
            "market_group": ["developed", "emerging"] * 4,
            "return": [0.01, -0.02, 0.02, -0.03, 0.03, -0.05, 0.04, -0.06],
            "gpr": [100.0, 100.0, 120.0, 120.0, 150.0, 150.0, 145.0, 145.0],
        }
    )

    result = run_baseline_panel_regression(panel, cluster_by_ticker=False)

    assert "gpr_change_z" in result.params.index
    assert "gpr_change_z:emerging_market" in result.params.index


def test_run_controlled_panel_regression_estimates_control_terms():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-04",
                    "2024-01-05",
                    "2024-01-05",
                    "2024-01-06",
                    "2024-01-06",
                ]
            ),
            "ticker": ["SPY", "EWZ"] * 6,
            "market_group": ["developed", "emerging"] * 6,
            "return": [0.01, -0.02, 0.02, -0.03, 0.03, -0.05, 0.04, -0.06, 0.01, -0.01, 0.02, -0.04],
            "gpr": [100.0, 100.0, 120.0, 120.0, 140.0, 140.0, 160.0, 160.0, 130.0, 130.0, 150.0, 150.0],
            "global_market_return": [0.01, 0.01, 0.02, 0.02, -0.01, -0.01, 0.03, 0.03, 0.01, 0.01, -0.02, -0.02],
            "vix_change": [1.0, 1.0, -1.0, -1.0, 0.5, 0.5, -0.5, -0.5, 0.2, 0.2, -0.2, -0.2],
            "oil_change": [1.0, 1.0, -1.0, -1.0, 2.0, 2.0, -2.0, -2.0, 1.0, 1.0, -1.0, -1.0],
            "dollar_return": [0.001, 0.001, -0.002, -0.002, 0.003, 0.003, -0.004, -0.004, 0.002, 0.002, -0.001, -0.001],
            "us10y_change": [0.1, 0.1, -0.1, -0.1, 0.2, 0.2, -0.2, -0.2, 0.3, 0.3, -0.3, -0.3],
        }
    )

    result = run_controlled_panel_regression(panel, cluster_by_ticker=False)

    assert "gpr_change_z" in result.params.index
    assert "gpr_change_z:emerging_market" in result.params.index
    assert "global_market_return" in result.params.index
    assert "vix_change" in result.params.index


def test_run_date_fe_panel_regression_identifies_emerging_interaction_only():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-04",
                ]
            ),
            "ticker": ["SPY", "EWZ"] * 4,
            "market_group": ["developed", "emerging"] * 4,
            "return": [0.01, -0.01, 0.01, -0.03, 0.01, -0.04, 0.01, -0.06],
            "gpr": [100.0, 100.0, 130.0, 130.0, 120.0, 120.0, 180.0, 180.0],
        }
    )

    result = run_date_fe_panel_regression(panel, cluster_by_ticker=False)

    assert "gpr_change_z:emerging_market" in result.params.index
    assert "gpr_change_z" not in result.params.index
    assert result.df_resid < len(panel) - 1


def test_tidy_regression_results_returns_readable_table():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-04",
                ]
            ),
            "ticker": ["SPY", "EWZ"] * 4,
            "market_group": ["developed", "emerging"] * 4,
            "return": [0.01, -0.02, 0.02, -0.03, 0.03, -0.05, 0.04, -0.06],
            "gpr": [100.0, 100.0, 120.0, 120.0, 150.0, 150.0, 145.0, 145.0],
        }
    )
    result = run_baseline_panel_regression(panel, cluster_by_ticker=False)

    table = tidy_regression_results(result)

    assert table.columns.tolist() == ["term", "estimate", "std_error", "t_stat", "p_value"]
    assert "gpr_change_z" in table["term"].tolist()
