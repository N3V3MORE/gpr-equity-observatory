from pathlib import Path

import pandas as pd


COUNTRY_COLUMNS = ["country", "ticker", "market_group", "region"]


def load_country_universe(path: str | Path = "data/country_universe.csv") -> pd.DataFrame:
    """Load the MVP country and ETF list."""
    universe = pd.read_csv(path)
    missing_columns = [column for column in COUNTRY_COLUMNS if column not in universe.columns]
    if missing_columns:
        raise ValueError(f"Country universe is missing columns: {missing_columns}")

    return universe[COUNTRY_COLUMNS].copy()


def download_adjusted_prices(
    tickers: list[str],
    start: str = "2005-01-01",
    end: str | None = None,
) -> pd.DataFrame:
    """Download adjusted close prices from yfinance."""
    try:
        import yfinance as yf
    except ImportError as error:
        raise ImportError(
            "yfinance is required to download market data. "
            "Install dependencies with: python -m pip install -r requirements.txt"
        ) from error

    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
    )
    prices = extract_adjusted_close(data)
    prices.index.name = "date"
    return prices.sort_index()


def extract_adjusted_close(data: pd.DataFrame) -> pd.DataFrame:
    """Return one adjusted-close price column per ticker from yfinance output."""
    if data.empty:
        return pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        first_level = data.columns.get_level_values(0)
        second_level = data.columns.get_level_values(1)

        if "Adj Close" in first_level:
            prices = data["Adj Close"]
        elif "Close" in first_level:
            prices = data["Close"]
        elif "Adj Close" in second_level:
            prices = data.xs("Adj Close", level=1, axis=1)
        elif "Close" in second_level:
            prices = data.xs("Close", level=1, axis=1)
        else:
            raise ValueError("Could not find adjusted close or close prices in yfinance data.")
    elif "Adj Close" in data.columns:
        prices = data[["Adj Close"]].rename(columns={"Adj Close": "price"})
    elif "Close" in data.columns:
        prices = data[["Close"]].rename(columns={"Close": "price"})
    else:
        raise ValueError("Could not find adjusted close or close prices in yfinance data.")

    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    return prices.dropna(how="all")
