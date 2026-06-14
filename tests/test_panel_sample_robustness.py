import pandas as pd

from gprobs.analysis.panel_sample_robustness import (
    build_sample_robustness_table,
    filter_excluded_periods,
)


def _toy_controlled_panel() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=30)
    rows = []
    for date_index, date in enumerate(dates):
        for ticker, market_group, group_shift in [
            ("SPY", "developed", 0.0),
            ("EWZ", "emerging", -0.001),
        ]:
            gpr = 100 + date_index * 3
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "market_group": market_group,
                    "return": 0.001 * date_index + group_shift,
                    "gpr": gpr,
                    "global_market_return": 0.0005 * date_index,
                    "vix_change": (-1) ** date_index * 0.1,
                    "oil_change": 0.2 * date_index,
                    "dollar_return": 0.0001 * (date_index % 5),
                    "us10y_change": 0.01 * (date_index % 7),
                }
            )
    return pd.DataFrame(rows)


def test_filter_excluded_periods_removes_dates_inclusive():
    panel = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=5),
            "return": [1, 2, 3, 4, 5],
        }
    )

    filtered = filter_excluded_periods(
        panel,
        [("2020-01-02", "2020-01-04")],
    )

    assert filtered["date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2020-01-01",
        "2020-01-05",
    ]


def test_build_sample_robustness_table_keeps_key_gpr_terms_by_scenario():
    panel = _toy_controlled_panel()
    scenarios = {
        "Full sample": [],
        "Excluding middle window": [("2020-01-10", "2020-01-15")],
    }

    table = build_sample_robustness_table(
        panel,
        scenarios=scenarios,
        cluster_by_ticker=False,
    )

    assert table.columns.tolist() == [
        "scenario",
        "term",
        "estimate",
        "std_error",
        "t_stat",
        "p_value",
        "observation_count",
    ]
    assert table["scenario"].tolist() == [
        "Full sample",
        "Full sample",
        "Excluding middle window",
        "Excluding middle window",
    ]
    assert set(table["term"]) == {"gpr_z", "gpr_z:emerging_market"}
    assert table.loc[0, "observation_count"] == 60
    assert table.loc[2, "observation_count"] == 48
