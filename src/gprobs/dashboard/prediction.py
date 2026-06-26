import pandas as pd

ML_VALIDATION_HEADING = "Purged Chronological Validation"
ML_VALIDATION_CAPTION = (
    "Splits are purged chronological, so the model trains only on earlier dates "
    "and excludes dates immediately before the test fold to reduce forward-label leakage."
)
FEATURE_IMPORTANCE_CAPTION = (
    "Feature importance is a full-sample interpretive diagnostic for the fitted "
    "drawdown-risk classifier, not out-of-sample evidence by itself."
)


def build_model_summary(drawdown_metrics: pd.DataFrame, drawdown_lift: pd.DataFrame) -> pd.DataFrame:
    model_summary = (
        drawdown_metrics.groupby("model_name", as_index=False)
        .agg(
            mean_roc_auc=("roc_auc", "mean"),
            mean_average_precision=("average_precision", "mean"),
            mean_brier_score=("brier_score", "mean"),
            mean_base_rate=("base_rate", "mean"),
            observation_count=("observation_count", "sum"),
        )
        .sort_values("mean_roc_auc", ascending=False)
    )
    top_decile_lift = drawdown_lift.loc[
        drawdown_lift["bucket"] == "top_10_percent",
        ["model_name", "lift"],
    ].rename(columns={"lift": "top_decile_lift"})
    return model_summary.merge(top_decile_lift, on="model_name", how="left")


def best_model_metric_labels(model_summary: pd.DataFrame) -> dict[str, tuple[str, str]]:
    return {
        "auc": _best_metric_label(model_summary, "mean_roc_auc", "Best model AUC", "{:.3f}"),
        "ap": _best_metric_label(model_summary, "mean_average_precision", "Best model AP", "{:.3f}"),
        "lift": _best_metric_label(model_summary, "top_decile_lift", "Top-decile lift", "{:.2f}x"),
    }


def _best_metric_label(
    model_summary: pd.DataFrame,
    metric_col: str,
    label: str,
    value_format: str,
) -> tuple[str, str]:
    metric_values = pd.to_numeric(model_summary[metric_col], errors="coerce")
    if metric_values.isna().all():
        return label, "n/a"
    best_row = model_summary.loc[metric_values.idxmax()]
    model_name = best_row["model_name"]
    return f"{label} ({model_name})", value_format.format(float(best_row[metric_col]))
