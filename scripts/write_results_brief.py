from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.reporting.results_brief import build_results_brief


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    brief = build_results_brief(
        pd.read_csv(processed_dir / "evidence_summary.csv"),
        pd.read_csv(processed_dir / "panel_sample_robustness.csv"),
    )

    output_path = reports_dir / "RESULTS_BRIEF.md"
    output_path.write_text(brief, encoding="utf-8")
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
