from pathlib import Path

import pandas as pd

from gprobs.analysis.rolling_sensitivity import calculate_rolling_gpr_beta
from gprobs.config import ROLLING_BETA_MIN_PERIODS, ROLLING_BETA_WINDOW_DAYS

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )

    rolling = calculate_rolling_gpr_beta(
        panel,
        window=ROLLING_BETA_WINDOW_DAYS,
        min_periods=ROLLING_BETA_MIN_PERIODS,
    )
    rolling.to_csv(processed_dir / "rolling_gpr_beta.csv", index=False)

    print(f"Saved {len(rolling):,} rolling GPR beta observations.")


if __name__ == "__main__":
    main()
