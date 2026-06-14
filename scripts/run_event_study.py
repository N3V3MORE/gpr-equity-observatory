from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.analysis.event_study import (
    build_event_windows,
    select_spaced_events,
    summarize_event_windows,
)


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )
    gpr = pd.read_csv(processed_dir / "gpr_daily.csv", parse_dates=["date"])

    event_dates = select_spaced_events(gpr, min_gap_days=20)
    windows = build_event_windows(panel, event_dates, window=5)
    summary = summarize_event_windows(windows)

    windows.to_csv(processed_dir / "event_windows.csv", index=False)
    summary.to_csv(processed_dir / "event_study_summary.csv", index=False)

    print(f"Selected {len(event_dates):,} spaced GPR shock dates.")
    print(f"Saved {len(windows):,} event-window observations.")
    print(f"Saved {len(summary):,} event-study summary rows.")


if __name__ == "__main__":
    main()
