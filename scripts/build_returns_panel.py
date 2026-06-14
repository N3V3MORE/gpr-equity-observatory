import argparse
from pathlib import Path

from gprobs.config import DATA_START_DATE
from gprobs.data.market_data import download_adjusted_prices, load_country_universe
from gprobs.features.returns import build_returns_panel

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description="Build ETF price and return panels.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh cached raw ETF price downloads.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    raw_dir = PROJECT_ROOT / "data" / "raw"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    universe = load_country_universe(PROJECT_ROOT / "data" / "country_universe.csv")
    tickers = universe["ticker"].tolist()

    prices = download_adjusted_prices(
        tickers=tickers,
        start=DATA_START_DATE,
        cache_path=raw_dir / "yfinance_etf_prices.pkl",
        refresh=args.refresh,
    )
    returns = build_returns_panel(prices)

    prices.to_csv(raw_dir / "etf_adjusted_prices.csv")
    returns.to_csv(processed_dir / "returns_panel.csv", index=False)

    print(f"Saved {len(prices):,} price dates for {len(tickers)} ETFs.")
    print(f"Saved {len(returns):,} return observations.")


if __name__ == "__main__":
    main()
