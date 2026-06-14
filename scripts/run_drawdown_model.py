from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gprobs.analysis.drawdown_model import (
    build_drawdown_dataset,
    evaluate_drawdown_classifier,
    fit_drawdown_feature_importance,
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
    panel = merge_market_controls(panel, controls)

    dataset = build_drawdown_dataset(panel, horizon=20, threshold=-0.05)
    metrics = evaluate_drawdown_classifier(dataset, n_splits=5)
    importance = fit_drawdown_feature_importance(dataset)

    dataset.to_csv(processed_dir / "drawdown_model_dataset.csv", index=False)
    metrics.to_csv(processed_dir / "drawdown_model_metrics.csv", index=False)
    importance.to_csv(processed_dir / "drawdown_feature_importance.csv", index=False)

    event_rate = dataset["drawdown_risk"].mean()
    print(f"Saved {len(dataset):,} drawdown model rows.")
    print(f"Forward 20-day drawdown event rate: {event_rate:.2%}.")
    print(f"Saved {len(metrics):,} chronological validation folds.")
    print(f"Saved {len(importance):,} feature-importance rows.")


if __name__ == "__main__":
    main()
