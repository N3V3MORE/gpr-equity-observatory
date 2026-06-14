import argparse
from pathlib import Path

from gprobs.pipeline import run_pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description="Run the full reproducible pipeline.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh cached raw downloads before rebuilding derived outputs.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    run_pipeline(PROJECT_ROOT, refresh=args.refresh)


if __name__ == "__main__":
    main()
