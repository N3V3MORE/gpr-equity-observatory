import pandas as pd
import pytest

from gprobs.analysis.monthly_benchmark import run_panel_interaction, run_spread_regression
from gprobs.data.datasets import MONTHLY_BENCHMARK_SAMPLE
from gprobs.data.monthly_sample import build_monthly_benchmark_sample
from gprobs.project_paths import ProjectPaths
from gprobs.reporting.outputs import table_path
from scripts.run_monthly_benchmark_regressions import run_monthly_benchmark_regressions


def _sample_panel() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=8, freq="MS")
    rows = []
    for idx, date in enumerate(dates):
        shock = float(idx - 3)
        for market_id, market_class, multiplier in [
            ("developed", "developed", -0.2),
            ("emerging", "emerging", -0.5),
        ]:
            rows.append(
                {
                    "date_month": date,
                    "market_id": market_id,
                    "market_class": market_class,
                    "ret_fwd_1m": multiplier * shock,
                    "spread_em_dev": -0.3 * shock,
                    "gpr_global_z": shock,
                    "sample_global_cycle": idx / 10,
                }
            )
    return pd.DataFrame(rows)


def test_run_spread_regression_returns_hac_metadata():
    result = run_spread_regression(
        _sample_panel(),
        horizon=1,
        shock_col="gpr_global_z",
        controls=["sample_global_cycle"],
        maxlags=2,
    )

    table = result.to_frame()

    assert result.se_type == "HAC"
    assert result.metadata == {"horizon": 1, "model": "spread", "maxlags": 2}
    assert result.nobs == 8
    assert "gpr_global_z" in table["term"].tolist()


def test_run_spread_regression_rejects_nonunique_month_predictors():
    panel = _sample_panel()
    panel.loc[panel["market_id"] == "emerging", "gpr_global_z"] += 1.0

    with pytest.raises(ValueError, match="unique within date_month"):
        run_spread_regression(panel, horizon=1, shock_col="gpr_global_z")


def test_run_spread_regression_rejects_incomplete_market_month_pairs():
    panel = _sample_panel()
    bad_panel = panel[
        ~((panel["date_month"] == pd.Timestamp("2020-01-01")) & (panel["market_id"] == "emerging"))
    ]

    with pytest.raises(ValueError, match="developed and emerging"):
        run_spread_regression(bad_panel, horizon=1, shock_col="gpr_global_z")


def test_run_panel_interaction_rejects_weak_cluster_count_even_if_lower_requested():
    with pytest.raises(ValueError, match="at least 3 unique market_id clusters"):
        run_panel_interaction(
            _sample_panel(),
            horizon=1,
            shock_col="gpr_global_z",
            controls=["sample_global_cycle"],
            cluster_min_groups=1,
        )


def test_run_panel_interaction_includes_emerging_interaction_with_sufficient_clusters():
    dates = pd.date_range("2020-01-01", periods=8, freq="MS")
    rows = []
    for idx, date in enumerate(dates):
        shock = float(idx - 3)
        for market_id, market_class, multiplier in [
            ("developed_a", "developed", -0.2),
            ("developed_b", "developed", -0.1),
            ("emerging_a", "emerging", -0.5),
            ("emerging_b", "emerging", -0.4),
        ]:
            rows.append(
                {
                    "date_month": date,
                    "market_id": market_id,
                    "market_class": market_class,
                    "ret_fwd_1m": multiplier * shock,
                    "gpr_global_z": shock,
                    "sample_global_cycle": idx / 10,
                }
            )
    panel = pd.DataFrame(rows)

    result = run_panel_interaction(panel, horizon=1, shock_col="gpr_global_z", controls=["sample_global_cycle"])

    assert "emerging_x_gpr_global_z" in result.to_frame()["term"].tolist()
    assert result.se_type == "clustered"


def test_run_monthly_benchmark_regressions_writes_monthly_namespaced_table(tmp_path):
    build_monthly_benchmark_sample(root=tmp_path)

    run_monthly_benchmark_regressions(MONTHLY_BENCHMARK_SAMPLE, root=tmp_path, horizons=[1])

    paths = ProjectPaths(tmp_path)
    output = table_path(paths, "table_02_baseline_regressions.csv", MONTHLY_BENCHMARK_SAMPLE)
    table = pd.read_csv(output)

    assert output.exists()
    assert not (tmp_path / "reports" / "tables" / "table_02_baseline_regressions.csv").exists()
    assert table["horizon"].tolist() == [1, 1, 1]
    assert "gpr_change_z" in table["term"].tolist()
