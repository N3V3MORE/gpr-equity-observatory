from pathlib import Path

import pandas as pd

from gprobs.config import LARGE_RETURN_THRESHOLD
from gprobs.data.diagnostics import flag_large_returns, summarize_country_coverage

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )

    coverage = summarize_country_coverage(panel)
    large_returns = flag_large_returns(panel, threshold=LARGE_RETURN_THRESHOLD)

    coverage.to_csv(processed_dir / "country_coverage_summary.csv", index=False)
    large_returns.to_csv(processed_dir / "large_return_flags.csv", index=False)

    print(f"Saved coverage summary for {len(coverage):,} country ETFs.")
    threshold_percent = f"{LARGE_RETURN_THRESHOLD:.0%}"
    print(f"Flagged {len(large_returns):,} returns above {threshold_percent} in absolute value.")


if __name__ == "__main__":
    main()
