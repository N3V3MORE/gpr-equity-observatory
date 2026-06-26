import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from gprobs.analysis.panel_regression import CONTROL_COLUMNS
from gprobs.config import (
    DEFAULT_GPR_SHOCK_QUANTILE,
    DRAWDOWN_HORIZON_DAYS,
    DRAWDOWN_THRESHOLD,
    DRAWDOWN_VOLATILITY_WINDOW_DAYS,
    GPR_EXPANDING_SHOCK_MIN_PERIODS,
)
from gprobs.utils import coerce_shock_to_int

DEFAULT_FEATURE_COLUMNS = [
    "gpr_change_z",
    "gpr_change_shock_expanding",
    "global_market_return",
    "vix_change",
    "oil_change",
    "dollar_return",
    "us10y_change",
    "lag_return_1d",
    "rolling_volatility",
    "emerging_market",
]

VOLATILITY_FEATURE_COLUMNS = ["rolling_volatility"]

METRIC_COLUMNS = [
    "fold",
    "model_name",
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
    horizon: int = DRAWDOWN_HORIZON_DAYS,
    threshold: float = DRAWDOWN_THRESHOLD,
    volatility_window: int = DRAWDOWN_VOLATILITY_WINDOW_DAYS,
) -> pd.DataFrame:
    """Build a time-ordered dataset for forward drawdown classification."""
    if horizon < 1:
        raise ValueError("horizon must be at least 1.")
    if volatility_window < 2:
        raise ValueError("volatility_window must be at least 2.")

    base_columns = [
        "date",
        "ticker",
        "country",
        "market_group",
        "return",
    ] + CONTROL_COLUMNS
    gpr_source_columns = [
        column
        for column in [
            "gpr",
            "gpr_change",
            "gpr_change_shock_expanding",
            "gpr_shock_expanding",
        ]
        if column in panel.columns
    ]
    if "gpr" not in gpr_source_columns and "gpr_change" not in gpr_source_columns:
        raise ValueError("Panel data is missing gpr_change and gpr columns.")

    data = panel[base_columns + gpr_source_columns].copy()
    data = _add_time_aware_gpr_features(data)
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
    dataset = dataset.sort_values(["date", "ticker"]).reset_index(drop=True)
    dataset.attrs["forward_horizon"] = horizon
    return dataset


def evaluate_drawdown_classifier(
    dataset: pd.DataFrame,
    n_splits: int = 5,
    feature_columns: list[str] | None = None,
    embargo_dates: int | None = None,
) -> pd.DataFrame:
    """Evaluate drawdown classification with purged chronological validation folds."""
    model_specs = (
        [("full_features", feature_columns)]
        if feature_columns is not None
        else [
            ("constant_baseline", []),
            ("volatility_only", VOLATILITY_FEATURE_COLUMNS),
            ("full_features", DEFAULT_FEATURE_COLUMNS),
        ]
    )
    if embargo_dates is None:
        embargo_dates = int(dataset.attrs.get("forward_horizon", DRAWDOWN_HORIZON_DAYS))
    folds = _date_folds(dataset, n_splits=n_splits, embargo_dates=embargo_dates)

    rows = []
    for fold_number, (train_dates, test_dates) in enumerate(folds, start=1):
        train = dataset.loc[dataset["date"].isin(train_dates)]
        test = dataset.loc[dataset["date"].isin(test_dates)]
        for model_name, model_features in model_specs:
            probabilities = _predict_probabilities(train, test, model_features)
            roc = (
                roc_auc_score(test["drawdown_risk"], probabilities)
                if test["drawdown_risk"].nunique() >= 2
                else float("nan")
            )

            rows.append(
                {
                    "fold": fold_number,
                    "model_name": model_name,
                    "train_start": train["date"].min(),
                    "train_end": train["date"].max(),
                    "test_start": test["date"].min(),
                    "test_end": test["date"].max(),
                    "roc_auc": roc,
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


def _add_time_aware_gpr_features(data: pd.DataFrame) -> pd.DataFrame:
    daily_gpr = _unique_daily_gpr_frame(data)
    if "gpr_change" not in daily_gpr.columns:
        daily_gpr["gpr_change"] = daily_gpr["gpr"].diff()

    daily_gpr["gpr_change_z"] = _expanding_z_score(daily_gpr["gpr_change"])
    if "gpr_change_shock_expanding" not in daily_gpr.columns:
        if "gpr_shock_expanding" in daily_gpr.columns:
            daily_gpr["gpr_change_shock_expanding"] = daily_gpr[
                "gpr_shock_expanding"
            ]
        else:
            threshold = (
                daily_gpr["gpr_change"]
                .shift(1)
                .expanding(min_periods=GPR_EXPANDING_SHOCK_MIN_PERIODS)
                .quantile(DEFAULT_GPR_SHOCK_QUANTILE)
            )
            daily_gpr["gpr_change_shock_expanding"] = (
                daily_gpr["gpr_change"] >= threshold
            ).fillna(False)

    gpr_features = daily_gpr[
        ["date", "gpr_change", "gpr_change_z", "gpr_change_shock_expanding"]
    ].copy()
    gpr_features["gpr_change_shock_expanding"] = gpr_features[
        "gpr_change_shock_expanding"
    ].map(coerce_shock_to_int)

    drop_columns = [
        column
        for column in ["gpr_change", "gpr_change_z", "gpr_change_shock_expanding"]
        if column in data.columns
    ]
    data = data.drop(columns=drop_columns)
    return data.merge(gpr_features, on="date", how="left")


def _unique_daily_gpr_frame(data: pd.DataFrame) -> pd.DataFrame:
    gpr_columns = [
        column
        for column in [
            "date",
            "gpr",
            "gpr_change",
            "gpr_change_shock_expanding",
            "gpr_shock_expanding",
        ]
        if column in data.columns
    ]
    daily_gpr = data[gpr_columns].drop_duplicates().copy()
    for column in gpr_columns:
        if column == "date":
            continue
        value_counts = daily_gpr.dropna(subset=[column]).groupby("date")[column].nunique()
        if value_counts.gt(1).any():
            raise ValueError(f"{column} must be unique within each date.")

    return (
        daily_gpr.sort_values("date")
        .drop_duplicates(subset=["date"], keep="first")
        .reset_index(drop=True)
    )


def _expanding_z_score(values: pd.Series) -> pd.Series:
    expanding_mean = values.expanding(min_periods=2).mean()
    expanding_std = values.expanding(min_periods=2).std(ddof=0)
    z_score = (values - expanding_mean) / expanding_std
    return z_score.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def _predict_probabilities(
    train: pd.DataFrame,
    test: pd.DataFrame,
    feature_columns: list[str],
) -> np.ndarray:
    if not feature_columns or train["drawdown_risk"].nunique() < 2:
        return np.repeat(train["drawdown_risk"].mean(), len(test))

    model = _make_classifier()
    model.fit(train[feature_columns], train["drawdown_risk"])
    return model.predict_proba(test[feature_columns])[:, 1]


def _forward_min_cumulative_return(returns: pd.Series, horizon: int) -> pd.Series:
    forward_returns = pd.concat(
        [returns.shift(-offset) for offset in range(1, horizon + 1)],
        axis=1,
    )
    cumulative_paths = forward_returns.cumsum(axis=1)
    forward_min = cumulative_paths.min(axis=1)
    forward_min[forward_returns.isna().any(axis=1)] = np.nan

    return forward_min


def _date_folds(
    dataset: pd.DataFrame,
    n_splits: int,
    embargo_dates: int = 0,
) -> list[tuple[pd.Series, pd.Series]]:
    unique_dates = pd.Series(sorted(dataset["date"].drop_duplicates()))
    if n_splits < 1:
        raise ValueError("n_splits must be at least 1.")
    if embargo_dates < 0:
        raise ValueError("embargo_dates must be non-negative.")
    if len(unique_dates) < n_splits + 2:
        raise ValueError("Not enough dates for the requested number of splits.")

    test_size = len(unique_dates) // (n_splits + 1)
    folds = []
    for split_number in range(n_splits):
        test_start = test_size * (split_number + 1)
        test_end = test_start + test_size
        if split_number == n_splits - 1:
            test_end = len(unique_dates)

        train_end = max(test_start - embargo_dates, 0)
        if train_end == 0:
            raise ValueError("Not enough training dates before the embargoed test fold.")

        train_dates = unique_dates.iloc[:train_end]
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

