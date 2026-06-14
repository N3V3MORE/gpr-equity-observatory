import pandas as pd


ROLLING_COLUMNS = [
    "date",
    "ticker",
    "country",
    "market_group",
    "rolling_gpr_beta",
]


def calculate_rolling_gpr_beta(
    panel: pd.DataFrame,
    window: int = 252,
    min_periods: int = 126,
) -> pd.DataFrame:
    """Estimate rolling return sensitivity to standardized daily GPR."""
    if window < 2:
        raise ValueError("window must be at least 2.")
    if min_periods < 2:
        raise ValueError("min_periods must be at least 2.")

    data = panel[["date", "ticker", "country", "market_group", "return", "gpr"]].dropna().copy()
    gpr_by_date = data[["date", "gpr"]].drop_duplicates()
    gpr_std = gpr_by_date["gpr"].std(ddof=0)
    if gpr_std == 0:
        raise ValueError("GPR has no variation, so rolling beta cannot be calculated.")

    data["gpr_z"] = (data["gpr"] - gpr_by_date["gpr"].mean()) / gpr_std

    frames = []
    for _, country_data in data.groupby("ticker"):
        country_data = country_data.sort_values("date").reset_index(drop=True)
        rolling_covariance = country_data["return"].rolling(
            window=window,
            min_periods=min_periods,
        ).cov(country_data["gpr_z"])
        rolling_variance = country_data["gpr_z"].rolling(
            window=window,
            min_periods=min_periods,
        ).var()

        country_data["rolling_gpr_beta"] = rolling_covariance / rolling_variance
        frames.append(country_data[ROLLING_COLUMNS])

    if not frames:
        return pd.DataFrame(columns=ROLLING_COLUMNS)

    return pd.concat(frames, ignore_index=True)
