from pathlib import Path

import pandas as pd

from gprobs.reporting.results_brief import build_results_brief

PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
