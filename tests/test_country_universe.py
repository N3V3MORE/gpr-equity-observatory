from pathlib import Path

import pandas as pd


def test_country_universe_has_mvp_20_country_sample():
    path = Path("data/country_universe.csv")

    universe = pd.read_csv(path)

    assert len(universe) == 20
    assert universe.columns.tolist() == ["country", "ticker", "market_group", "region"]
    assert universe["ticker"].is_unique
    assert set(universe["market_group"]) == {"developed", "emerging"}
    assert (universe["market_group"] == "developed").sum() == 10
    assert (universe["market_group"] == "emerging").sum() == 10
