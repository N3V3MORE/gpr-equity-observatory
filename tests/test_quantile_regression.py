import pandas as pd

from gprobs.analysis.quantile_regression import run_quantile_regressions


def test_run_quantile_regressions_returns_tidy_gpr_terms_by_quantile():
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
            "return": [
                0.01,
                -0.02,
                0.02,
                -0.03,
                0.03,
                -0.05,
                0.04,
                -0.06,
                0.01,
                -0.01,
                0.02,
                -0.04,
            ],
            "gpr": [100.0, 100.0, 120.0, 120.0, 140.0, 140.0, 160.0, 160.0, 130.0, 130.0, 150.0, 150.0],
        }
    )

    results = run_quantile_regressions(
        panel,
        quantiles=[0.10, 0.50],
        include_controls=False,
    )

    assert results.columns.tolist() == [
        "quantile",
        "term",
        "estimate",
        "std_error",
        "t_stat",
        "p_value",
    ]
    assert set(results["quantile"]) == {0.10, 0.50}
    assert "gpr_z" in results["term"].tolist()
    assert "gpr_z:emerging_market" in results["term"].tolist()
