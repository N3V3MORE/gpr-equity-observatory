import argparse
from pathlib import Path

from gprobs.config import DATA_START_DATE
from gprobs.data.market_controls import CONTROL_TICKERS, build_market_controls
from gprobs.data.market_data import download_adjusted_prices

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description="Build public market-control variables.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh cached raw market-control price downloads.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    raw_dir = PROJECT_ROOT / "data" / "raw"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    prices = download_adjusted_prices(
        tickers=list(CONTROL_TICKERS),
        start=DATA_START_DATE,
        cache_path=raw_dir / "yfinance_market_control_prices.pkl",
        refresh=args.refresh,
    )
    controls = build_market_controls(prices)

    prices.to_csv(raw_dir / "market_control_prices.csv")
    controls.to_csv(processed_dir / "market_controls.csv", index=False)

    first_date = controls["date"].min().date()
    last_date = controls["date"].max().date()
    print(f"Saved {len(controls):,} market-control dates from {first_date} to {last_date}.")


if __name__ == "__main__":
    main()
