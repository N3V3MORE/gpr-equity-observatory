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
        "gpr_change",
        "gpr_act",
        "gpr_threat",
        "gpr_ma7",
        "gpr_ma30",
        "event",
    ]
    assert cleaned.loc[0, "date"] == pd.Timestamp("2024-01-01")
    assert cleaned.loc[1, "gpr"] == 140.0
    assert pd.isna(cleaned.loc[0, "gpr_change"])
    assert cleaned.loc[1, "gpr_change"] == 60.0


def test_mark_top_quantile_shocks_flags_large_positive_gpr_jumps():
    gpr = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ),
            "gpr": [10.0, 100.0, 101.0, 102.0, 160.0],
        }
    )

    marked = mark_top_quantile_shocks(gpr, quantile=0.75, expanding_min_periods=2)

    assert marked["gpr_change"].tolist()[1:] == [90.0, 1.0, 1.0, 58.0]
    assert marked["gpr_shock_full_sample"].tolist() == [False, True, False, False, False]
    assert marked["gpr_shock"].tolist() == [False, False, False, False, True]
    assert marked["gpr_shock_threshold"].nunique() == 1
    assert marked["gpr_shock_threshold"].iloc[0] > 58.0


def test_mark_top_quantile_shocks_names_full_sample_and_expanding_change_shocks():
    gpr = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ),
            "gpr": [100.0, 110.0, 130.0, 230.0, 260.0],
        }
    )

    marked = mark_top_quantile_shocks(
        gpr,
        quantile=0.80,
        expanding_min_periods=2,
    )

    expected_columns = {
        "gpr_change",
        "gpr_change_z",
        "gpr_change_shock",
        "gpr_change_shock_full_sample",
        "gpr_change_shock_expanding",
        "gpr_shock_full_sample",
        "gpr_shock_expanding",
        "gpr_shock",
        "gpr_shock_threshold",
    }
    assert expected_columns.issubset(marked.columns)
    assert marked["gpr_change"].tolist()[1:] == [10.0, 20.0, 100.0, 30.0]
    assert marked["gpr_change_shock_full_sample"].tolist() == [False, False, False, True, False]
    assert marked["gpr_shock_full_sample"].equals(marked["gpr_change_shock_full_sample"])
    assert marked["gpr_shock"].equals(marked["gpr_change_shock"])
    assert marked["gpr_change_shock_expanding"].tolist() == [False, False, False, True, False]
    assert marked["gpr_change_shock"].equals(marked["gpr_change_shock_expanding"])
    assert marked["gpr_shock_expanding"].equals(marked["gpr_change_shock_expanding"])
