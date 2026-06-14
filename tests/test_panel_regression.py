import pandas as pd

from gprobs.analysis.panel_regression import (
    prepare_panel_regression_data,
    run_baseline_panel_regression,
    tidy_regression_results,
)


def test_prepare_panel_regression_data_adds_emerging_flag_and_standardized_gpr():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02"]),
            "ticker": ["SPY", "EWZ", "SPY"],
            "market_group": ["developed", "emerging", "developed"],
            "return": [0.01, -0.02, 0.03],
            "gpr": [100.0, 100.0, 200.0],
        }
    )

    prepared = prepare_panel_regression_data(panel)

    assert prepared["emerging_market"].tolist() == [0, 1, 0]
    assert round(prepared["gpr_z"].mean(), 10) == 0
    assert {"date", "ticker", "return", "gpr_z", "emerging_market"}.issubset(
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
            "gpr": [100.0, 100.0, 120.0, 120.0, 140.0, 140.0, 160.0, 160.0],
        }
    )

    result = run_baseline_panel_regression(panel, cluster_by_ticker=False)

    assert "gpr_z" in result.params.index
    assert "gpr_z:emerging_market" in result.params.index


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
            "gpr": [100.0, 100.0, 120.0, 120.0, 140.0, 140.0, 160.0, 160.0],
        }
    )
    result = run_baseline_panel_regression(panel, cluster_by_ticker=False)

    table = tidy_regression_results(result)

    assert table.columns.tolist() == ["term", "estimate", "std_error", "t_stat", "p_value"]
    assert "gpr_z" in table["term"].tolist()
