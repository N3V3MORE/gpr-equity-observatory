import argparse
from pathlib import Path

from gprobs.config import DEFAULT_GPR_SHOCK_QUANTILE
from gprobs.data.gpr_data import download_daily_gpr, mark_top_quantile_shocks

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description="Build the cleaned daily GPR dataset.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh the cached raw GPR download.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    raw_dir = PROJECT_ROOT / "data" / "raw"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    gpr = download_daily_gpr(
        cache_path=raw_dir / "gpr_daily_recent.xls",
        refresh=args.refresh,
    )
    gpr = mark_top_quantile_shocks(gpr, quantile=DEFAULT_GPR_SHOCK_QUANTILE)

    output_path = processed_dir / "gpr_daily.csv"
    gpr.to_csv(output_path, index=False)

    first_date = gpr["date"].min().date()
    last_date = gpr["date"].max().date()
    shock_count = int(gpr["gpr_shock"].sum())

    print(f"Saved {len(gpr):,} daily GPR observations from {first_date} to {last_date}.")
    percentile = f"{DEFAULT_GPR_SHOCK_QUANTILE:.0%}"
    print(f"Flagged {shock_count:,} days at or above the {percentile} percentile of GPR.")


if __name__ == "__main__":
    main()
