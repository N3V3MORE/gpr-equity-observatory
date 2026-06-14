import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from gprobs.analysis.panel_regression import CONTROL_COLUMNS


DEFAULT_FEATURE_COLUMNS = [
    "gpr_z",
    "gpr_shock",
    "global_market_return",
    "vix_change",
    "oil_change",
    "dollar_return",
    "us10y_change",
    "lag_return_1d",
    "rolling_volatility",
    "emerging_market",
]

METRIC_COLUMNS = [
    "fold",
    "train_start",
    "train_end",
    "test_start",
    "test_end",
    "roc_auc",
    "average_precision",
    "base_rate",
    "observation_count",
]


def build_drawdown_dataset(
    panel: pd.DataFrame,
    horizon: int = 20,
    threshold: float = -0.05,
    volatility_window: int = 20,
) -> pd.DataFrame:
    """Build a time-ordered dataset for forward drawdown classification."""
    if horizon < 1:
        raise ValueError("horizon must be at least 1.")
    if volatility_window < 2:
        raise ValueError("volatility_window must be at least 2.")

    columns = [
        "date",
        "ticker",
        "country",
        "market_group",
        "return",
        "gpr",
        "gpr_shock",
    ] + CONTROL_COLUMNS
    data = panel[columns].copy()
    data["gpr_shock"] = data["gpr_shock"].map(_coerce_shock_to_int)

    gpr_std = data["gpr"].std(ddof=0)
    if gpr_std == 0:
        raise ValueError("GPR has no variation, so drawdown features cannot be built.")
    data["gpr_z"] = (data["gpr"] - data["gpr"].mean()) / gpr_std
    data["emerging_market"] = (data["market_group"] == "emerging").astype(int)

    frames = []
    for _, ticker_data in data.groupby("ticker"):
        ticker_data = ticker_data.sort_values("date").copy()
        ticker_data["lag_return_1d"] = ticker_data["return"].shift(1).fillna(0.0)
        ticker_data["rolling_volatility"] = (
            ticker_data["return"].shift(1).rolling(volatility_window, min_periods=2).std()
            .fillna(0.0)
        )
        ticker_data["forward_min_return"] = _forward_min_cumulative_return(
            ticker_data["return"],
            horizon,
        )
        ticker_data["drawdown_risk"] = (
            ticker_data["forward_min_return"] <= threshold
        ).astype(int)
        frames.append(ticker_data)

    dataset = pd.concat(frames, ignore_index=True)
    keep_columns = [
        "date",
        "ticker",
        "country",
        "market_group",
        "forward_min_return",
        "drawdown_risk",
    ] + DEFAULT_FEATURE_COLUMNS
    dataset = dataset[keep_columns].dropna()
    return dataset.sort_values(["date", "ticker"]).reset_index(drop=True)


def evaluate_drawdown_classifier(
    dataset: pd.DataFrame,
    n_splits: int = 5,
    feature_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Evaluate drawdown classification with chronological validation folds."""
    feature_columns = feature_columns or DEFAULT_FEATURE_COLUMNS
    folds = _date_folds(dataset, n_splits=n_splits)

    rows = []
    for fold_number, (train_dates, test_dates) in enumerate(folds, start=1):
        train = dataset.loc[dataset["date"].isin(train_dates)]
        test = dataset.loc[dataset["date"].isin(test_dates)]
        model = _make_classifier()
        model.fit(train[feature_columns], train["drawdown_risk"])
        probabilities = model.predict_proba(test[feature_columns])[:, 1]

        rows.append(
            {
                "fold": fold_number,
                "train_start": train["date"].min(),
                "train_end": train["date"].max(),
                "test_start": test["date"].min(),
                "test_end": test["date"].max(),
                "roc_auc": _safe_roc_auc(test["drawdown_risk"], probabilities),
                "average_precision": average_precision_score(
                    test["drawdown_risk"],
                    probabilities,
                ),
                "base_rate": test["drawdown_risk"].mean(),
                "observation_count": len(test),
            }
        )

    return pd.DataFrame(rows, columns=METRIC_COLUMNS)


def fit_drawdown_feature_importance(
    dataset: pd.DataFrame,
    feature_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Fit the classifier on all data and return standardized coefficients."""
    feature_columns = feature_columns or DEFAULT_FEATURE_COLUMNS
    model = _make_classifier()
    model.fit(dataset[feature_columns], dataset["drawdown_risk"])

    coefficients = model.named_steps["model"].coef_[0]
    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "coefficient": coefficients,
        }
    )
    importance["abs_coefficient"] = importance["coefficient"].abs()
    return importance.sort_values("abs_coefficient", ascending=False).reset_index(drop=True)


def _coerce_shock_to_int(value) -> int:
    if isinstance(value, str):
        return int(value.strip().lower() == "true")
    return int(bool(value))


def _forward_min_cumulative_return(returns: pd.Series, horizon: int) -> pd.Series:
    cumulative_paths = []
    cumulative = pd.Series(0.0, index=returns.index)
    for offset in range(1, horizon + 1):
        cumulative = cumulative + returns.shift(-offset)
        cumulative_paths.append(cumulative.copy())

    return pd.concat(cumulative_paths, axis=1).min(axis=1)


def _date_folds(dataset: pd.DataFrame, n_splits: int) -> list[tuple[pd.Series, pd.Series]]:
    unique_dates = pd.Series(sorted(dataset["date"].drop_duplicates()))
    if n_splits < 1:
        raise ValueError("n_splits must be at least 1.")
    if len(unique_dates) < n_splits + 2:
        raise ValueError("Not enough dates for the requested number of splits.")

    test_size = len(unique_dates) // (n_splits + 1)
    folds = []
    for split_number in range(n_splits):
        test_start = test_size * (split_number + 1)
        test_end = test_start + test_size
        if split_number == n_splits - 1:
            test_end = len(unique_dates)

        train_dates = unique_dates.iloc[:test_start]
        test_dates = unique_dates.iloc[test_start:test_end]
        folds.append((train_dates, test_dates))

    return folds


def _make_classifier() -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def _safe_roc_auc(target: pd.Series, probabilities: np.ndarray) -> float:
    if target.nunique() < 2:
        return float("nan")
    return roc_auc_score(target, probabilities)
