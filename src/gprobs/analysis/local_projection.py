import math

import pandas as pd
import statsmodels.formula.api as smf

from gprobs.analysis.panel_regression import CONTROL_COLUMNS


LOCAL_PROJECTION_COLUMNS = [
    "horizon",
    "date",
    "ticker",
    "country",
    "market_group",
    "cumulative_return",
    "gpr_shock",
    "emerging_market",
]

RESULT_COLUMNS = [
    "horizon",
    "market_group",
    "estimate",
    "std_error",
    "ci_low",
    "ci_high",
    "p_value",
]


def build_local_projection_data(
    panel: pd.DataFrame,
    max_horizon: int = 20,
    include_controls: bool = False,
) -> pd.DataFrame:
    """Build cumulative future returns for local projection regressions."""
    if max_horizon < 0:
        raise ValueError("max_horizon must be non-negative.")

    base_columns = ["date", "ticker", "country", "market_group", "return", "gpr_shock"]
    if include_controls:
        base_columns = base_columns + CONTROL_COLUMNS

    data = panel[base_columns].dropna(subset=["date", "ticker", "return", "gpr_shock"]).copy()
    data["gpr_shock"] = data["gpr_shock"].map(_coerce_shock_to_int)
    data["emerging_market"] = (data["market_group"] == "emerging").astype(int)

    frames = []
    for _, ticker_data in data.groupby("ticker"):
        ticker_data = ticker_data.sort_values("date").reset_index(drop=True)
        for horizon in range(max_horizon + 1):
            frame = ticker_data.copy()
            frame["horizon"] = horizon
            frame["cumulative_return"] = _forward_cumulative_return(
                ticker_data["return"],
                horizon,
            )
            frames.append(frame)

    if not frames:
        return pd.DataFrame(columns=_projection_columns(include_controls))

    projection_data = pd.concat(frames, ignore_index=True)
    projection_data = projection_data.dropna(subset=["cumulative_return"])
    return projection_data[_projection_columns(include_controls)].reset_index(drop=True)


def estimate_local_projections(
    panel: pd.DataFrame,
    max_horizon: int = 20,
    include_controls: bool = False,
    cluster_by_ticker: bool = True,
) -> pd.DataFrame:
    """Estimate GPR shock response paths for developed and emerging ETFs."""
    data = build_local_projection_data(
        panel,
        max_horizon=max_horizon,
        include_controls=include_controls,
    )

    rows = []
    for horizon, horizon_data in data.groupby("horizon"):
        result = _fit_horizon_model(
            horizon_data,
            include_controls=include_controls,
            cluster_by_ticker=cluster_by_ticker,
        )
        rows.extend(_response_rows(result, int(horizon)))

    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


def _projection_columns(include_controls: bool) -> list[str]:
    columns = LOCAL_PROJECTION_COLUMNS.copy()
    if include_controls:
        columns.extend(CONTROL_COLUMNS)
    return columns


def _coerce_shock_to_int(value) -> int:
    if isinstance(value, str):
        return int(value.strip().lower() == "true")
    return int(bool(value))


def _forward_cumulative_return(returns: pd.Series, horizon: int) -> pd.Series:
    cumulative = pd.Series(0.0, index=returns.index)
    for offset in range(horizon + 1):
        cumulative = cumulative + returns.shift(-offset)
    return cumulative


def _fit_horizon_model(
    data: pd.DataFrame,
    include_controls: bool,
    cluster_by_ticker: bool,
):
    formula = "cumulative_return ~ gpr_shock + gpr_shock:emerging_market + C(ticker)"
    if include_controls:
        controls = " + ".join(CONTROL_COLUMNS)
        formula = (
            "cumulative_return ~ gpr_shock + gpr_shock:emerging_market + "
            f"{controls} + C(ticker)"
        )

    model_columns = ["cumulative_return", "gpr_shock", "emerging_market", "ticker"]
    if include_controls:
        model_columns.extend(CONTROL_COLUMNS)
    data = data.dropna(subset=model_columns)

    model = smf.ols(formula, data=data)
    if cluster_by_ticker:
        return model.fit(cov_type="cluster", cov_kwds={"groups": data["ticker"]})
    return model.fit()


def _response_rows(result, horizon: int) -> list[dict]:
    developed_estimate = result.params.get("gpr_shock", 0.0)
    developed_var = _covariance_value(result, "gpr_shock", "gpr_shock")
    developed_se = math.sqrt(max(developed_var, 0.0))

    interaction_term = "gpr_shock:emerging_market"
    interaction_estimate = result.params.get(interaction_term, 0.0)
    emerging_estimate = developed_estimate + interaction_estimate
    emerging_var = (
        developed_var
        + _covariance_value(result, interaction_term, interaction_term)
        + 2 * _covariance_value(result, "gpr_shock", interaction_term)
    )
    emerging_se = math.sqrt(max(emerging_var, 0.0))

    return [
        _format_response_row(
            horizon,
            "developed",
            developed_estimate,
            developed_se,
            result.pvalues.get("gpr_shock", float("nan")),
        ),
        _format_response_row(
            horizon,
            "emerging",
            emerging_estimate,
            emerging_se,
            result.pvalues.get(interaction_term, float("nan")),
        ),
    ]


def _covariance_value(result, first_term: str, second_term: str) -> float:
    covariance = result.cov_params()
    if first_term not in covariance.index or second_term not in covariance.columns:
        return 0.0
    return float(covariance.loc[first_term, second_term])


def _format_response_row(
    horizon: int,
    market_group: str,
    estimate: float,
    std_error: float,
    p_value: float,
) -> dict:
    return {
        "horizon": horizon,
        "market_group": market_group,
        "estimate": estimate,
        "std_error": std_error,
        "ci_low": estimate - 1.96 * std_error,
        "ci_high": estimate + 1.96 * std_error,
        "p_value": p_value,
    }
