import pandas as pd
import statsmodels.formula.api as smf


BASELINE_FORMULA = "etf_return ~ gpr_z + gpr_z:emerging_market + C(ticker)"
CONTROL_COLUMNS = [
    "global_market_return",
    "vix_change",
    "oil_change",
    "dollar_return",
    "us10y_change",
]
CONTROLLED_FORMULA = (
    "etf_return ~ gpr_z + gpr_z:emerging_market + "
    "global_market_return + vix_change + oil_change + dollar_return + us10y_change + "
    "C(ticker)"
)


def prepare_panel_regression_data(
    panel: pd.DataFrame,
    include_controls: bool = False,
) -> pd.DataFrame:
    """Prepare the return panel for the baseline fixed-effects regression."""
    columns = ["date", "ticker", "market_group", "return", "gpr"]
    if include_controls:
        columns = columns + CONTROL_COLUMNS

    data = panel[columns].dropna().copy()

    data["etf_return"] = data["return"]
    data["emerging_market"] = (data["market_group"] == "emerging").astype(int)

    gpr_std = data["gpr"].std(ddof=0)
    if gpr_std == 0:
        raise ValueError("GPR has no variation, so it cannot be standardized.")

    data["gpr_z"] = (data["gpr"] - data["gpr"].mean()) / gpr_std
    return data


def run_baseline_panel_regression(
    panel: pd.DataFrame,
    cluster_by_ticker: bool = True,
):
    """Estimate return sensitivity to GPR with ticker fixed effects."""
    data = prepare_panel_regression_data(panel)
    model = smf.ols(BASELINE_FORMULA, data=data)

    if cluster_by_ticker:
        return model.fit(cov_type="cluster", cov_kwds={"groups": data["ticker"]})

    return model.fit()


def run_controlled_panel_regression(
    panel: pd.DataFrame,
    cluster_by_ticker: bool = True,
):
    """Estimate GPR sensitivity after adding public market controls."""
    data = prepare_panel_regression_data(panel, include_controls=True)
    model = smf.ols(CONTROLLED_FORMULA, data=data)

    if cluster_by_ticker:
        return model.fit(cov_type="cluster", cov_kwds={"groups": data["ticker"]})

    return model.fit()


def tidy_regression_results(result) -> pd.DataFrame:
    """Convert a statsmodels result into a small readable coefficient table."""
    return pd.DataFrame(
        {
            "term": result.params.index,
            "estimate": result.params.values,
            "std_error": result.bse.values,
            "t_stat": result.tvalues.values,
            "p_value": result.pvalues.values,
        }
    )
