from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.data.gpr_data import download_daily_gpr, mark_top_quantile_shocks


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    gpr = download_daily_gpr()
    gpr = mark_top_quantile_shocks(gpr, quantile=0.95)

    output_path = processed_dir / "gpr_daily.csv"
    gpr.to_csv(output_path, index=False)

    first_date = gpr["date"].min().date()
    last_date = gpr["date"].max().date()
    shock_count = int(gpr["gpr_shock"].sum())

    print(f"Saved {len(gpr):,} daily GPR observations from {first_date} to {last_date}.")
    print(f"Flagged {shock_count:,} days at or above the 95th percentile of GPR.")


if __name__ == "__main__":
    main()
