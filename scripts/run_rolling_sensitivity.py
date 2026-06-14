from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.analysis.rolling_sensitivity import calculate_rolling_gpr_beta


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )

    rolling = calculate_rolling_gpr_beta(panel, window=252, min_periods=126)
    rolling.to_csv(processed_dir / "rolling_gpr_beta.csv", index=False)

    print(f"Saved {len(rolling):,} rolling GPR beta observations.")


if __name__ == "__main__":
    main()
