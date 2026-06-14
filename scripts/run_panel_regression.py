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
    tidy_regression_results,
)


def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"

    panel = pd.read_csv(
        processed_dir / "analysis_panel.csv",
        parse_dates=["date"],
        low_memory=False,
    )

    result = run_baseline_panel_regression(panel)
    table = tidy_regression_results(result)

    table.to_csv(processed_dir / "panel_regression_baseline.csv", index=False)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="covariance of constraints does not have full rank.*",
            category=ValueWarning,
        )
        summary_text = result.summary().as_text()

    (processed_dir / "panel_regression_summary.txt").write_text(
        summary_text,
        encoding="utf-8",
    )

    print("Saved baseline panel regression results.")
    print("Key term: gpr_z:emerging_market measures extra GPR sensitivity for emerging ETFs.")


if __name__ == "__main__":
    main()
