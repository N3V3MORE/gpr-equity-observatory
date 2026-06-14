import pandas as pd


def build_country_coverage(panel: pd.DataFrame) -> pd.DataFrame:
    """Summarize available return observations by country ETF."""
    coverage = (
        panel.groupby(["country", "ticker", "market_group"], as_index=False)
        .agg(
            first_date=("date", "min"),
            last_date=("date", "max"),
            observation_count=("return", "count"),
        )
        .sort_values(["market_group", "country"])
        .reset_index(drop=True)
    )
    return coverage


def select_key_regression_terms(table: pd.DataFrame) -> pd.DataFrame:
    """Keep only the GPR terms that matter for the baseline interpretation."""
    terms = ["gpr_change_z", "gpr_change_z:emerging_market"]
    return table.loc[table["term"].isin(terms)].reset_index(drop=True)
