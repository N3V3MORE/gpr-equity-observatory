import pandas as pd

from gprobs.config import MARKET_CONTROL_TICKERS
from gprobs.features.returns import calculate_log_returns

CONTROL_TICKERS = MARKET_CONTROL_TICKERS

CONTROL_COLUMNS = [
    "global_market_return",
    "vix_change",
    "oil_change",
    "dollar_return",
    "us10y_change",
]


def build_market_controls(prices: pd.DataFrame) -> pd.DataFrame:
    """Build daily no-key market controls from public Yahoo Finance proxies."""
    required_tickers = list(CONTROL_TICKERS)
    missing_tickers = [ticker for ticker in required_tickers if ticker not in prices.columns]
    if missing_tickers:
        raise ValueError(f"Market control prices are missing tickers: {missing_tickers}")

    controls = pd.DataFrame(index=prices.index)
    controls["global_market_return"] = calculate_log_returns(prices["ACWI"])
    controls["vix_change"] = prices["^VIX"].dropna().diff()
    controls["oil_change"] = prices["CL=F"].dropna().diff()
    controls["dollar_return"] = calculate_log_returns(prices["UUP"])
    controls["us10y_change"] = prices["^TNX"].dropna().diff()

    controls = controls.dropna().reset_index()
    controls = controls.rename(columns={controls.columns[0]: "date"})
    return controls[["date"] + CONTROL_COLUMNS]


def merge_market_controls(panel: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
    """Add same-day market controls to a country return panel."""
    missing_columns = [column for column in CONTROL_COLUMNS if column not in controls.columns]
    if missing_columns:
        raise ValueError(f"Market controls are missing columns: {missing_columns}")

    return panel.merge(controls[["date"] + CONTROL_COLUMNS], on="date", how="left")
