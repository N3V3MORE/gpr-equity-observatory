from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.data.diagnostics import flag_large_returns, summarize_country_coverage


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )

    coverage = summarize_country_coverage(panel)
    large_returns = flag_large_returns(panel, threshold=0.20)

    coverage.to_csv(processed_dir / "country_coverage_summary.csv", index=False)
    large_returns.to_csv(processed_dir / "large_return_flags.csv", index=False)

    print(f"Saved coverage summary for {len(coverage):,} country ETFs.")
    print(f"Flagged {len(large_returns):,} returns above 20 percent in absolute value.")


if __name__ == "__main__":
    main()
