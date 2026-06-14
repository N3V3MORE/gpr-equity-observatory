from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.data.market_data import download_adjusted_prices, load_country_universe
from gprobs.features.returns import build_returns_panel


def main():
    raw_dir = PROJECT_ROOT / "data" / "raw"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    universe = load_country_universe(PROJECT_ROOT / "data" / "country_universe.csv")
    tickers = universe["ticker"].tolist()

    prices = download_adjusted_prices(tickers=tickers, start="2005-01-01")
    returns = build_returns_panel(prices)

    prices.to_csv(raw_dir / "etf_adjusted_prices.csv")
    returns.to_csv(processed_dir / "returns_panel.csv", index=False)

    print(f"Saved {len(prices):,} price dates for {len(tickers)} ETFs.")
    print(f"Saved {len(returns):,} return observations.")


if __name__ == "__main__":
    main()
