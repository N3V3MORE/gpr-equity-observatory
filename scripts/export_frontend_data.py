"""Export chart-ready JSON into the Next.js frontend's public/data folder.

Run after the daily (and optional monthly) pipeline has produced
``data/processed/*.csv``. The frontend reads these JSON files at build time.
"""

import argparse
from pathlib import Path

from gprobs.dashboard.export import export_frontend_data

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export frontend JSON from processed outputs.")
    parser.add_argument(
        "--root",
        default=None,
        help="Project root containing data/processed. Defaults to this repo.",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Output directory for JSON files. Defaults to <root>/frontend/public/data.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root) if args.root else PROJECT_ROOT
    target = Path(args.target) if args.target else None
    output_dir = export_frontend_data(root=root, target_dir=target)
    print(f"Exported frontend JSON to {output_dir}")


if __name__ == "__main__":
    main()
