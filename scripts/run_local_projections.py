from pathlib import Path

import pandas as pd

from gprobs.analysis.local_projection import estimate_local_projections
from gprobs.config import LOCAL_PROJECTION_MAX_HORIZON
from gprobs.data.market_controls import merge_market_controls

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )
    controls = pd.read_csv(processed_dir / "market_controls.csv", parse_dates=["date"])
    panel = merge_market_controls(panel, controls)

    results = estimate_local_projections(
        panel,
        max_horizon=LOCAL_PROJECTION_MAX_HORIZON,
        include_controls=True,
    )
    results.to_csv(processed_dir / "local_projection_results.csv", index=False)

    print(f"Saved {len(results):,} local projection response rows.")


if __name__ == "__main__":
    main()
