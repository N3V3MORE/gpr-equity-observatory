from urllib.error import URLError

import pandas as pd

from gprobs.data.download_cache import download_url_to_cache, retry
from gprobs.data.gpr_data import download_daily_gpr
from gprobs.data.market_data import download_adjusted_prices


def _raw_gpr_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "N10D": [100],
            "GPRD": [120.0],
            "GPRD_ACT": [80.0],
            "GPRD_THREAT": [40.0],
            "GPRD_MA7": [110.0],
            "GPRD_MA30": [100.0],
            "event": ["sample"],
        }
    )


def test_retry_recovers_from_transient_failure():
    attempts = {"count": 0}

    def flaky_operation():
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise URLError("temporary outage")
        return "ok"

    assert retry(flaky_operation, retries=2, backoff_seconds=0) == "ok"
    assert attempts["count"] == 2


def test_download_url_to_cache_reuses_existing_file_without_fetch(tmp_path):
    cache_path = tmp_path / "cached.xls"
    cache_path.write_bytes(b"already cached")

    def fetcher(url: str, timeout: int) -> bytes:
        raise AssertionError("fetcher should not run when cache exists")

    result = download_url_to_cache(
        "https://example.com/source.xls",
        cache_path,
        fetcher=fetcher,
    )

    assert result == cache_path
    assert cache_path.read_bytes() == b"already cached"


def test_download_daily_gpr_reads_cached_excel_without_network(monkeypatch, tmp_path):
    cache_path = tmp_path / "gpr_daily_recent.xls"
    cache_path.write_bytes(b"cached excel bytes")

    def fake_read_excel(path):
        assert path == cache_path
        return _raw_gpr_frame()

    monkeypatch.setattr(pd, "read_excel", fake_read_excel)

    gpr = download_daily_gpr(cache_path=cache_path)

    assert gpr.loc[0, "date"] == pd.Timestamp("2024-01-01")
    assert gpr.loc[0, "gpr"] == 120.0


def test_download_adjusted_prices_reuses_cached_yfinance_payload(tmp_path):
    cache_path = tmp_path / "prices.pkl"
    raw = pd.DataFrame(
        {"Adj Close": [100.0, 105.0]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    raw.to_pickle(cache_path)

    prices = download_adjusted_prices(["SPY"], cache_path=cache_path)

    assert prices.columns.tolist() == ["price"]
    assert prices.loc[pd.Timestamp("2024-01-02"), "price"] == 105.0


def test_download_adjusted_prices_retries_and_refreshes_cache(monkeypatch, tmp_path):
    cache_path = tmp_path / "prices.pkl"
    attempts = {"count": 0}
    raw = pd.DataFrame(
        {"Adj Close": [100.0, 105.0]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )

    class FakeYFinance:
        @staticmethod
        def download(**kwargs):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise RuntimeError("temporary yfinance failure")
            return raw

    monkeypatch.setitem(__import__("sys").modules, "yfinance", FakeYFinance)

    prices = download_adjusted_prices(
        ["SPY"],
        cache_path=cache_path,
        refresh=True,
        retries=2,
        retry_backoff_seconds=0,
    )

    assert attempts["count"] == 2
    assert cache_path.exists()
    assert prices.loc[pd.Timestamp("2024-01-02"), "price"] == 105.0
