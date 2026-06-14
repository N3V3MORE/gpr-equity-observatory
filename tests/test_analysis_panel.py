import pandas as pd

from gprobs.data.analysis_panel import build_analysis_panel, build_group_return_summary


def test_build_analysis_panel_adds_country_metadata_and_gpr():
    returns = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
            "ticker": ["SPY", "EWZ"],
            "return": [0.01, -0.02],
        }
    )
    universe = pd.DataFrame(
        {
            "country": ["United States", "Brazil"],
            "ticker": ["SPY", "EWZ"],
            "market_group": ["developed", "emerging"],
            "region": ["North America", "Latin America"],
        }
    )
    gpr = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "gpr": [150.0],
            "gpr_shock": [True],
        }
    )

    panel = build_analysis_panel(returns, universe, gpr)

    assert panel.columns.tolist() == [
        "date",
        "ticker",
        "country",
        "market_group",
        "region",
        "return",
        "gpr",
        "gpr_shock",
    ]
    brazil_row = panel.loc[panel["ticker"] == "EWZ"].iloc[0]
    assert brazil_row["country"] == "Brazil"
    assert brazil_row["gpr"] == 150.0


def test_build_group_return_summary_averages_returns_by_date_and_group():
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-01"]),
            "market_group": ["developed", "developed", "emerging"],
            "return": [0.01, 0.03, -0.02],
        }
    )

    summary = build_group_return_summary(panel)

    assert summary.columns.tolist() == ["date", "market_group", "average_return", "country_count"]
    assert summary.loc[0, "average_return"] == 0.02
    assert summary.loc[0, "country_count"] == 2
