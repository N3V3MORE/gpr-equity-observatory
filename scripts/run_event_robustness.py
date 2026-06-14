from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.analysis.event_robustness import build_event_robustness_table
from gprobs.data.market_controls import merge_market_controls


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )
    gpr = pd.read_csv(processed_dir / "gpr_daily.csv", parse_dates=["date"])
    controls = pd.read_csv(processed_dir / "market_controls.csv", parse_dates=["date"])

    controlled_panel = merge_market_controls(panel, controls)
    robustness = build_event_robustness_table(
        controlled_panel,
        gpr,
        shock_quantiles=[0.90, 0.95],
        windows=[3, 5, 10],
        min_gap_days=20,
        estimation_window=120,
        estimation_gap=20,
        min_estimation_obs=80,
    )

    robustness.to_csv(processed_dir / "event_robustness_summary.csv", index=False)
    print(f"Saved {len(robustness):,} event-study robustness rows.")


if __name__ == "__main__":
    main()
