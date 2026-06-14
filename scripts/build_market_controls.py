from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.data.market_controls import CONTROL_TICKERS, build_market_controls
from gprobs.data.market_data import download_adjusted_prices


def main():
    raw_dir = PROJECT_ROOT / "data" / "raw"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    prices = download_adjusted_prices(tickers=list(CONTROL_TICKERS), start="2005-01-01")
    controls = build_market_controls(prices)

    prices.to_csv(raw_dir / "market_control_prices.csv")
    controls.to_csv(processed_dir / "market_controls.csv", index=False)

    first_date = controls["date"].min().date()
    last_date = controls["date"].max().date()
    print(f"Saved {len(controls):,} market-control dates from {first_date} to {last_date}.")


if __name__ == "__main__":
    main()
