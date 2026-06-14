import warnings

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

BASELINE_FORMULA = (
    "etf_return ~ gpr_change_z + gpr_change_z:emerging_market + C(ticker)"
)
CONTROL_COLUMNS = [
    "global_market_return",
    "vix_change",
    "oil_change",
    "dollar_return",
    "us10y_change",
]
CONTROLLED_FORMULA = (
    "etf_return ~ gpr_change_z + gpr_change_z:emerging_market + "
    "global_market_return + vix_change + oil_change + dollar_return + us10y_change + "
    "C(ticker)"
)
DATE_FE_TERM = "gpr_change_z:emerging_market"


def _add_gpr_change_from_level(panel: pd.DataFrame) -> pd.DataFrame:
    if "gpr_change" in panel.columns:
        return panel.copy()
    if "gpr" not in panel.columns:
        raise ValueError("Panel data is missing gpr_change and gpr columns.")

    data = panel.copy()
    gpr_by_date = data[["date", "gpr"]].dropna().drop_duplicates()
    conflicting_dates = gpr_by_date.groupby("date")["gpr"].nunique()
    if conflicting_dates.gt(1).any():
        raise ValueError("GPR level must be unique within each date.")

    gpr_by_date = gpr_by_date.sort_values("date").reset_index(drop=True)
    gpr_by_date["gpr_change"] = gpr_by_date["gpr"].diff()
    return data.merge(gpr_by_date[["date", "gpr_change"]], on="date", how="left")


def _fit_with_clustered_covariance(
    model,
    data: pd.DataFrame,
    cluster_by_ticker: bool,
    cluster_by_date: bool | None,
):
    if cluster_by_date is None:
        cluster_by_date = cluster_by_ticker
    if not cluster_by_ticker and not cluster_by_date:
        return model.fit()

    groups = {}
    if cluster_by_ticker:
        groups["ticker"] = pd.factorize(data["ticker"])[0]
    if cluster_by_date:
        groups["date"] = pd.factorize(pd.to_datetime(data["date"]))[0]

    cluster_groups = (
        next(iter(groups.values()))
        if len(groups) == 1
        else pd.DataFrame(groups, index=data.index)
    )
    return model.fit(cov_type="cluster", cov_kwds={"groups": cluster_groups})


def _residualize_two_way(
    values: pd.Series,
    groups: pd.DataFrame,
    max_iter: int = 100,
    tolerance: float = 1e-10,
) -> pd.Series:
    residual = values.astype(float).copy()
    for _ in range(max_iter):
        previous = residual.copy()
        for column in groups.columns:
            residual = residual - residual.groupby(groups[column]).transform("mean")
        if (residual - previous).abs().max() < tolerance:
            break
    return residual


def prepare_panel_regression_data(
    panel: pd.DataFrame,
    include_controls: bool = False,
) -> pd.DataFrame:
    """Prepare the return panel for the baseline fixed-effects regression."""
    panel = _add_gpr_change_from_level(panel)
    columns = ["date", "ticker", "market_group", "return", "gpr_change"]
    if include_controls:
        columns = columns + CONTROL_COLUMNS

    data = panel[columns].dropna().copy()

    data["etf_return"] = data["return"]
    data["emerging_market"] = (data["market_group"] == "emerging").astype(int)

    gpr_std = data["gpr_change"].std(ddof=0)
    if gpr_std == 0:
        raise ValueError("GPR change has no variation, so it cannot be standardized.")

    data["gpr_change_z"] = (data["gpr_change"] - data["gpr_change"].mean()) / gpr_std
    return data


def run_baseline_panel_regression(
    panel: pd.DataFrame,
    cluster_by_ticker: bool = True,
    cluster_by_date: bool | None = None,
):
    """Estimate return sensitivity to GPR with ticker fixed effects."""
    data = prepare_panel_regression_data(panel)
    model = smf.ols(BASELINE_FORMULA, data=data)
    return _fit_with_clustered_covariance(
        model,
        data,
        cluster_by_ticker=cluster_by_ticker,
        cluster_by_date=cluster_by_date,
    )


def run_controlled_panel_regression(
    panel: pd.DataFrame,
    cluster_by_ticker: bool = True,
    cluster_by_date: bool | None = None,
):
    """Estimate GPR sensitivity after adding public market controls."""
    data = prepare_panel_regression_data(panel, include_controls=True)
    model = smf.ols(CONTROLLED_FORMULA, data=data)
    return _fit_with_clustered_covariance(
        model,
        data,
        cluster_by_ticker=cluster_by_ticker,
        cluster_by_date=cluster_by_date,
    )


def run_date_fe_panel_regression(
    panel: pd.DataFrame,
    cluster_by_ticker: bool = True,
    cluster_by_date: bool | None = None,
):
    """Estimate the emerging-market differential after absorbing date shocks."""
    data = prepare_panel_regression_data(panel)
    interaction = data["gpr_change_z"] * data["emerging_market"]
    groups = data[["ticker", "date"]]
    model_data = pd.DataFrame(
        {
            "etf_return": _residualize_two_way(data["etf_return"], groups),
            DATE_FE_TERM: _residualize_two_way(interaction, groups),
            "ticker": data["ticker"],
            "date": data["date"],
        }
    )
    model = sm.OLS(model_data["etf_return"], model_data[[DATE_FE_TERM]])
    return _fit_with_clustered_covariance(
        model,
        model_data,
        cluster_by_ticker=cluster_by_ticker,
        cluster_by_date=cluster_by_date,
    )


def tidy_regression_results(result) -> pd.DataFrame:
    """Convert a statsmodels result into a small readable coefficient table."""
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="invalid value encountered in sqrt",
            category=RuntimeWarning,
        )
        std_errors = result.bse.values
        t_stats = result.tvalues.values
        p_values = result.pvalues.values

    return pd.DataFrame(
        {
            "term": result.params.index,
            "estimate": result.params.values,
            "std_error": std_errors,
            "t_stat": t_stats,
            "p_value": p_values,
        }
    )
