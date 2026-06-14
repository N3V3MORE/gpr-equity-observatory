from pathlib import Path
import sys
import warnings

import pandas as pd
from statsmodels.tools.sm_exceptions import ValueWarning


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.analysis.panel_regression import (
    run_baseline_panel_regression,
    run_controlled_panel_regression,
    tidy_regression_results,
)
from gprobs.data.market_controls import merge_market_controls


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )
    controls = pd.read_csv(processed_dir / "market_controls.csv", parse_dates=["date"])

    baseline_result = run_baseline_panel_regression(panel)
    baseline_table = tidy_regression_results(baseline_result)

    controlled_panel = merge_market_controls(panel, controls)
    controlled_result = run_controlled_panel_regression(controlled_panel)
    controlled_table = tidy_regression_results(controlled_result)

    baseline_table.to_csv(processed_dir / "panel_regression_baseline.csv", index=False)
    controlled_table.to_csv(processed_dir / "panel_regression_controlled.csv", index=False)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="covariance of constraints does not have full rank.*",
            category=ValueWarning,
        )
        baseline_summary_text = baseline_result.summary().as_text()
        controlled_summary_text = controlled_result.summary().as_text()

    (processed_dir / "panel_regression_summary.txt").write_text(
        baseline_summary_text,
        encoding="utf-8",
    )
    (processed_dir / "panel_regression_controlled_summary.txt").write_text(
        controlled_summary_text,
        encoding="utf-8",
    )

    print("Saved baseline and controlled panel regression results.")
    print("Key term: gpr_z:emerging_market measures extra GPR sensitivity for emerging ETFs.")


if __name__ == "__main__":
    main()
