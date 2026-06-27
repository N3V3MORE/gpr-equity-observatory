import argparse
from pathlib import Path

from gprobs.data.fred_sources import build_fred_macro_controls

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description="Build standalone FRED macro-control artifacts.")
    parser.add_argument("--refresh", action="store_true", help="Refresh cached raw FRED API responses.")
    parser.add_argument("--root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--start", default=None, help="Optional FRED observation_start date, YYYY-MM-DD.")
    parser.add_argument("--end", default=None, help="Optional FRED observation_end date, YYYY-MM-DD.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    controls = build_fred_macro_controls(
        root=args.root,
        refresh=args.refresh,
        start=args.start,
        end=args.end,
    )
    print(f"Saved {len(controls):,} FRED macro-control rows.")


if __name__ == "__main__":
    main()
