from pathlib import Path

import pandas as pd

from gprobs.analysis.event_robustness import build_event_robustness_table
from gprobs.config import (
    EVENT_ESTIMATION_GAP_DAYS,
    EVENT_ESTIMATION_WINDOW_DAYS,
    EVENT_MIN_ESTIMATION_OBS,
    EVENT_MIN_GAP_DAYS,
    EVENT_ROBUSTNESS_SHOCK_QUANTILES,
    EVENT_ROBUSTNESS_WINDOWS,
)
from gprobs.data.market_controls import merge_market_controls

PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
        shock_quantiles=EVENT_ROBUSTNESS_SHOCK_QUANTILES,
        windows=EVENT_ROBUSTNESS_WINDOWS,
        min_gap_days=EVENT_MIN_GAP_DAYS,
        estimation_window=EVENT_ESTIMATION_WINDOW_DAYS,
        estimation_gap=EVENT_ESTIMATION_GAP_DAYS,
        min_estimation_obs=EVENT_MIN_ESTIMATION_OBS,
    )

    robustness.to_csv(processed_dir / "event_robustness_summary.csv", index=False)
    print(f"Saved {len(robustness):,} event-study robustness rows.")


if __name__ == "__main__":
    main()
