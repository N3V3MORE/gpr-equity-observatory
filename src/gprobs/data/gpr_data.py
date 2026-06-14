import pandas as pd


DAILY_GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"

GPR_COLUMN_MAP = {
    "date": "date",
    "N10D": "article_count",
    "GPRD": "gpr",
    "GPRD_ACT": "gpr_act",
    "GPRD_THREAT": "gpr_threat",
    "GPRD_MA7": "gpr_ma7",
    "GPRD_MA30": "gpr_ma30",
    "event": "event",
}


def download_daily_gpr(url: str = DAILY_GPR_URL) -> pd.DataFrame:
    """Download and clean the official daily GPR index file."""
    raw = pd.read_excel(url)
    return clean_daily_gpr(raw)


def clean_daily_gpr(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean official daily GPR data into project-friendly column names."""
    missing_columns = [column for column in GPR_COLUMN_MAP if column not in raw.columns]
    if missing_columns:
        raise ValueError(f"Daily GPR data is missing columns: {missing_columns}")

    cleaned = raw[list(GPR_COLUMN_MAP)].rename(columns=GPR_COLUMN_MAP).copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"])

    numeric_columns = [
        "article_count",
        "gpr",
        "gpr_act",
        "gpr_threat",
        "gpr_ma7",
        "gpr_ma30",
    ]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=["date", "gpr"])
    cleaned = cleaned.sort_values("date").reset_index(drop=True)
    return cleaned


def mark_top_quantile_shocks(
    gpr: pd.DataFrame,
    quantile: float = 0.95,
    value_column: str = "gpr",
) -> pd.DataFrame:
    """Flag days where GPR is unusually high within the sample."""
    if not 0 < quantile < 1:
        raise ValueError("quantile must be between 0 and 1.")
    if value_column not in gpr.columns:
        raise ValueError(f"GPR data is missing column: {value_column}")

    marked = gpr.copy()
    threshold = marked[value_column].quantile(quantile)
    marked["gpr_shock"] = marked[value_column] >= threshold
    marked["gpr_shock_threshold"] = threshold
    return marked
