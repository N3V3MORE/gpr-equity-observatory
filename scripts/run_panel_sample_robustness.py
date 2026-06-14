from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.analysis.panel_sample_robustness import build_sample_robustness_table
from gprobs.data.market_controls import merge_market_controls


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )
    controls = pd.read_csv(processed_dir / "market_controls.csv", parse_dates=["date"])

    controlled_panel = merge_market_controls(panel, controls)
    robustness = build_sample_robustness_table(controlled_panel)

    robustness.to_csv(processed_dir / "panel_sample_robustness.csv", index=False)
    print(f"Saved {len(robustness):,} panel sample-robustness rows.")


if __name__ == "__main__":
    main()
