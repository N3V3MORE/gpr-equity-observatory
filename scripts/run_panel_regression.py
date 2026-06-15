import warnings
from pathlib import Path

import pandas as pd
from statsmodels.tools.sm_exceptions import ValueWarning

from gprobs.analysis.panel_regression import (
    run_baseline_panel_regression,
    run_controlled_panel_regression,
    run_date_fe_panel_regression,
    tidy_regression_results,
)
from gprobs.data.market_controls import merge_market_controls

PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
    date_fe_result = run_date_fe_panel_regression(panel)
    date_fe_table = tidy_regression_results(date_fe_result)

    baseline_table.to_csv(processed_dir / "panel_regression_baseline.csv", index=False)
    controlled_table.to_csv(processed_dir / "panel_regression_controlled.csv", index=False)
    date_fe_table.to_csv(processed_dir / "panel_regression_date_fe.csv", index=False)
    date_fe_table.to_csv(processed_dir / "panel_regression_two_way_fe.csv", index=False)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="covariance of constraints does not have full rank.*",
            category=ValueWarning,
        )
        warnings.filterwarnings(
            "ignore",
            message="invalid value encountered in sqrt",
            category=RuntimeWarning,
        )
        baseline_summary_text = baseline_result.summary().as_text()
        controlled_summary_text = controlled_result.summary().as_text()
        date_fe_summary_text = date_fe_result.summary().as_text()

    (processed_dir / "panel_regression_summary.txt").write_text(
        baseline_summary_text,
        encoding="utf-8",
    )
    (processed_dir / "panel_regression_controlled_summary.txt").write_text(
        controlled_summary_text,
        encoding="utf-8",
    )
    (processed_dir / "panel_regression_date_fe_summary.txt").write_text(
        date_fe_summary_text,
        encoding="utf-8",
    )
    (processed_dir / "panel_regression_two_way_fe_summary.txt").write_text(
        date_fe_summary_text,
        encoding="utf-8",
    )

    print("Saved baseline, controlled, and date fixed-effects panel regression results.")
    print(
        "Key term: gpr_change_z:emerging_market measures extra emerging-market "
        "sensitivity to a one-SD GPR jump."
    )


if __name__ == "__main__":
    main()
