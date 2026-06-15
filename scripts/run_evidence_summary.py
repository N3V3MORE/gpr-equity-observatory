from pathlib import Path

import pandas as pd

from gprobs.analysis.evidence_summary import build_evidence_summary

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    summary = build_evidence_summary(
        pd.read_csv(processed_dir / "panel_regression_baseline.csv"),
        pd.read_csv(processed_dir / "panel_regression_controlled.csv"),
        pd.read_csv(processed_dir / "panel_regression_two_way_fe.csv"),
        pd.read_csv(processed_dir / "quantile_regression_results.csv"),
        pd.read_csv(processed_dir / "local_projection_results.csv"),
        pd.read_csv(processed_dir / "event_robustness_summary.csv"),
        pd.read_csv(processed_dir / "drawdown_model_metrics.csv"),
    )

    summary.to_csv(processed_dir / "evidence_summary.csv", index=False)
    print(f"Saved {len(summary):,} evidence-summary rows.")


if __name__ == "__main__":
    main()
