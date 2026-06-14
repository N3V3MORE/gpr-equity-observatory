from io import BytesIO
from pathlib import Path

import pandas as pd

from gprobs.config import (
    DEFAULT_DOWNLOAD_RETRIES,
    DEFAULT_DOWNLOAD_TIMEOUT_SECONDS,
    DEFAULT_GPR_SHOCK_QUANTILE,
    DEFAULT_RETRY_BACKOFF_SECONDS,
    RAW_DATA_DIR,
)
from gprobs.data.download_cache import download_url_to_cache, fetch_url_bytes, retry

DAILY_GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
DEFAULT_GPR_CACHE_PATH = RAW_DATA_DIR / "gpr_daily_recent.xls"

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


def _add_gpr_change(gpr: pd.DataFrame) -> pd.DataFrame:
    """Add the daily GPR jump used by shock/event specifications."""
    changed = gpr.sort_values("date").reset_index(drop=True).copy()
    changed["gpr_change"] = changed["gpr"].diff()
    return changed


def download_daily_gpr(
    url: str = DAILY_GPR_URL,
    cache_path: str | Path | None = DEFAULT_GPR_CACHE_PATH,
    *,
    refresh: bool = False,
    timeout: int = DEFAULT_DOWNLOAD_TIMEOUT_SECONDS,
    retries: int = DEFAULT_DOWNLOAD_RETRIES,
    retry_backoff_seconds: float = DEFAULT_RETRY_BACKOFF_SECONDS,
) -> pd.DataFrame:
    """Download and clean the official daily GPR index file."""
    if cache_path is None:
        payload = retry(
            lambda: fetch_url_bytes(url, timeout),
            retries=retries,
            backoff_seconds=retry_backoff_seconds,
        )
        raw_source = BytesIO(payload)
    else:
        raw_source = download_url_to_cache(
            url,
            cache_path,
            refresh=refresh,
            timeout=timeout,
            retries=retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )

    raw = pd.read_excel(raw_source)
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
    cleaned = _add_gpr_change(cleaned)
    ordered_columns = [
        "date",
        "article_count",
        "gpr",
        "gpr_change",
        "gpr_act",
        "gpr_threat",
        "gpr_ma7",
        "gpr_ma30",
        "event",
    ]
    return cleaned[ordered_columns]


def mark_top_quantile_shocks(
    gpr: pd.DataFrame,
    quantile: float = DEFAULT_GPR_SHOCK_QUANTILE,
    value_column: str = "gpr_change",
) -> pd.DataFrame:
    """Flag days where GPR has an unusually large positive daily jump."""
    if not 0 < quantile < 1:
        raise ValueError("quantile must be between 0 and 1.")
    if value_column == "gpr_change" and value_column not in gpr.columns:
        gpr = _add_gpr_change(gpr)
    if value_column not in gpr.columns:
        raise ValueError(f"GPR data is missing column: {value_column}")

    marked = gpr.copy()
    threshold = marked[value_column].quantile(quantile)
    marked["gpr_shock"] = marked[value_column] >= threshold
    marked["gpr_shock_threshold"] = threshold
    return marked
