import argparse
from pathlib import Path

from gprobs.data.monthly_sample import build_monthly_benchmark_sample


def parse_args():
    parser = argparse.ArgumentParser(description="Build deterministic monthly benchmark sample data.")
    parser.add_argument("--root", default=None, help="Project root to write outputs into.")
    return parser.parse_args()


def main():
    args = parse_args()
    build_monthly_benchmark_sample(root=Path(args.root) if args.root else None)


if __name__ == "__main__":
    main()
