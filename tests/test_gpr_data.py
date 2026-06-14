import pandas as pd

from gprobs.data.gpr_data import clean_daily_gpr, mark_top_quantile_shocks


def test_clean_daily_gpr_keeps_research_columns_with_clear_names():
    raw = pd.DataFrame(
        {
            "DAY": [20240101, 20240102],
            "N10D": [100, 120],
            "GPRD": [80.0, 140.0],
            "GPRD_ACT": [50.0, 90.0],
            "GPRD_THREAT": [30.0, 110.0],
            "date": ["2024-01-01", "2024-01-02"],
            "GPRD_MA7": [85.0, 90.0],
            "GPRD_MA30": [95.0, 96.0],
            "event": [None, "test event"],
            "var_name": ["metadata", None],
        }
    )

    cleaned = clean_daily_gpr(raw)

    assert cleaned.columns.tolist() == [
        "date",
        "article_count",
        "gpr",
        "gpr_act",
        "gpr_threat",
        "gpr_ma7",
        "gpr_ma30",
        "event",
    ]
    assert cleaned.loc[0, "date"] == pd.Timestamp("2024-01-01")
    assert cleaned.loc[1, "gpr"] == 140.0


def test_mark_top_quantile_shocks_flags_high_gpr_days():
    gpr = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "gpr": [10.0, 20.0, 100.0],
        }
    )

    marked = mark_top_quantile_shocks(gpr, quantile=0.90)

    assert marked["gpr_shock"].tolist() == [False, False, True]
    assert marked["gpr_shock_threshold"].nunique() == 1
    assert marked["gpr_shock_threshold"].iloc[0] > 20.0
