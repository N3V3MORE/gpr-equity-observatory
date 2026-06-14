from pathlib import Path

import pandas as pd

from gprobs.data.analysis_panel import build_analysis_panel, build_group_return_summary
from gprobs.data.market_data import load_country_universe

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    returns = pd.read_csv(processed_dir / "returns_panel.csv", parse_dates=["date"])
    gpr = pd.read_csv(processed_dir / "gpr_daily.csv", parse_dates=["date"])
    universe = load_country_universe(PROJECT_ROOT / "data" / "country_universe.csv")

    panel = build_analysis_panel(returns, universe, gpr)
    summary = build_group_return_summary(panel)

    panel.to_csv(processed_dir / "analysis_panel.csv", index=False)
    summary.to_csv(processed_dir / "group_return_summary.csv", index=False)

    print(f"Saved {len(panel):,} country-day observations.")
    print(f"Saved {len(summary):,} group-day average return observations.")


if __name__ == "__main__":
    main()
