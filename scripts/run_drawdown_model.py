from pathlib import Path

import pandas as pd

from gprobs.analysis.drawdown_model import (
    build_drawdown_dataset,
    evaluate_drawdown_classifier,
    fit_drawdown_feature_importance,
)
from gprobs.config import DRAWDOWN_HORIZON_DAYS, DRAWDOWN_N_SPLITS, DRAWDOWN_THRESHOLD
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
    panel = merge_market_controls(panel, controls)

    dataset = build_drawdown_dataset(
        panel,
        horizon=DRAWDOWN_HORIZON_DAYS,
        threshold=DRAWDOWN_THRESHOLD,
    )
    metrics = evaluate_drawdown_classifier(dataset, n_splits=DRAWDOWN_N_SPLITS)
    importance = fit_drawdown_feature_importance(dataset)

    dataset.to_csv(processed_dir / "drawdown_model_dataset.csv", index=False)
    metrics.to_csv(processed_dir / "drawdown_model_metrics.csv", index=False)
    importance.to_csv(processed_dir / "drawdown_feature_importance.csv", index=False)

    event_rate = dataset["drawdown_risk"].mean()
    print(f"Saved {len(dataset):,} drawdown model rows.")
    print(f"Forward {DRAWDOWN_HORIZON_DAYS}-day drawdown event rate: {event_rate:.2%}.")
    print(f"Saved {len(metrics):,} purged chronological validation folds.")
    print(f"Saved {len(importance):,} feature-importance rows.")


if __name__ == "__main__":
    main()
