import argparse
from pathlib import Path

from gprobs.data.monthly_sources import build_monthly_benchmark_real


def main() -> None:
    parser = argparse.ArgumentParser(description="Build real monthly benchmark data from user-supplied sources.")
    parser.add_argument("--config", default="config/sources.yml")
    parser.add_argument("--root", default=None)
    args = parser.parse_args()
    build_monthly_benchmark_real(
        config_path=Path(args.config),
        root=Path(args.root) if args.root else None,
    )


if __name__ == "__main__":
    main()
