from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.analysis.quantile_regression import run_quantile_regressions
from gprobs.data.market_controls import merge_market_controls


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )
    controls = pd.read_csv(processed_dir / "market_controls.csv", parse_dates=["date"])
    panel = merge_market_controls(panel, controls)

    results = run_quantile_regressions(
        panel,
        quantiles=[0.10, 0.25, 0.50],
        include_controls=True,
    )
    results.to_csv(processed_dir / "quantile_regression_results.csv", index=False)

    print(f"Saved {len(results):,} quantile regression coefficient rows.")


if __name__ == "__main__":
    main()
