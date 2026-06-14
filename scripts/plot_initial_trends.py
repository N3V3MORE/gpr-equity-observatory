from pathlib import Path

import pandas as pd

from gprobs.visuals.initial_plots import plot_gpr_and_group_returns

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    figure_dir = PROJECT_ROOT / "reports" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    gpr = pd.read_csv(processed_dir / "gpr_daily.csv", parse_dates=["date"])
    group_summary = pd.read_csv(
        processed_dir / "group_return_summary.csv",
        parse_dates=["date"],
    )

    output_path = figure_dir / "gpr_and_group_returns.png"
    plot_gpr_and_group_returns(gpr, group_summary, output_path)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
