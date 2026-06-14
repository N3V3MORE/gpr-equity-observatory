from pathlib import Path

import pandas as pd

from gprobs.analysis.event_study import (
    build_event_windows,
    build_market_model_event_windows,
    select_spaced_events,
    summarize_abnormal_event_windows,
    summarize_event_windows,
)
from gprobs.config import (
    EVENT_ESTIMATION_GAP_DAYS,
    EVENT_ESTIMATION_WINDOW_DAYS,
    EVENT_MIN_ESTIMATION_OBS,
    EVENT_MIN_GAP_DAYS,
    EVENT_WINDOW_DAYS,
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

    event_dates = select_spaced_events(gpr, min_gap_days=EVENT_MIN_GAP_DAYS)
    windows = build_event_windows(panel, event_dates, window=EVENT_WINDOW_DAYS)
    summary = summarize_event_windows(windows)

    controlled_panel = merge_market_controls(panel, controls)
    abnormal_windows = build_market_model_event_windows(
        controlled_panel,
        event_dates,
        window=EVENT_WINDOW_DAYS,
        estimation_window=EVENT_ESTIMATION_WINDOW_DAYS,
        estimation_gap=EVENT_ESTIMATION_GAP_DAYS,
        min_estimation_obs=EVENT_MIN_ESTIMATION_OBS,
    )
    abnormal_summary = summarize_abnormal_event_windows(abnormal_windows)

    windows.to_csv(processed_dir / "event_windows.csv", index=False)
    summary.to_csv(processed_dir / "event_study_summary.csv", index=False)
    abnormal_windows.to_csv(processed_dir / "event_windows_abnormal.csv", index=False)
    abnormal_summary.to_csv(processed_dir / "event_study_abnormal_summary.csv", index=False)

    print(f"Selected {len(event_dates):,} spaced GPR shock dates.")
    print(f"Saved {len(windows):,} event-window observations.")
    print(f"Saved {len(summary):,} event-study summary rows.")
    print(f"Saved {len(abnormal_windows):,} abnormal event-window observations.")
    print(f"Saved {len(abnormal_summary):,} abnormal event-study summary rows.")


if __name__ == "__main__":
    main()
