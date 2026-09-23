"""Export chart-ready JSON for the Next.js frontend.

The frontend is presentation-only. Every derived table that the dashboard
computes in Python is computed here too (reusing the same helpers) and written
as JSON so the TypeScript app never needs to reimplement analysis logic or
research-claim wording.
"""

from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from gprobs.analysis.event_study import select_peak_cluster_events
from gprobs.config import (
    DEFAULT_GPR_SHOCK_QUANTILE,
    DRAWDOWN_HORIZON_DAYS,
    DRAWDOWN_THRESHOLD,
    EVENT_MIN_GAP_DAYS,
    GPR_EXPANDING_SHOCK_MIN_PERIODS,
)
from gprobs.dashboard.components import (
    BEGINNER_TAB_GUIDES,
    CENTRAL_PROJECT_QUESTION,
    DASHBOARD_INTRO,
    DASHBOARD_MAIN_TAKEAWAY,
    DASHBOARD_USE_NOTE,
    GLOSSARY_TERMS,
    HOW_TO_READ_NOTES,
    METHOD_MAP_ROWS,
    OVERVIEW_CURRENT_ANSWER_POINTS,
    OVERVIEW_DOES_NOT_PROVE_POINTS,
    OVERVIEW_JOB_STATEMENTS,
    OVERVIEW_READER_PATH,
    PREDICTION_METRIC_EXPLANATIONS,
    build_snapshot_answer,
)
from gprobs.dashboard.contracts import (
    OUTPUT_SPECS,
    PROJECT_ROOT,
    OutputSpec,
    validate_output_schema,
)
from gprobs.dashboard.evidence import build_evidence_map
from gprobs.dashboard.metrics import build_country_coverage, select_key_regression_terms
from gprobs.dashboard.monthly import (
    MONTHLY_CLUSTER_NOTICE,
    MONTHLY_EMPTY_STATE_COMMANDS,
    MONTHLY_EMPTY_STATE_NOTE,
    MONTHLY_MODE_PRIORITY_NOTICE,
    MONTHLY_MODES,
    MONTHLY_REAL_NOTICE,
    MONTHLY_SAMPLE_NOTICE,
    _load_monthly_output_mode,
    monthly_provenance_rows,
)
from gprobs.dashboard.prediction import (
    FEATURE_IMPORTANCE_CAPTION,
    ML_VALIDATION_CAPTION,
    ML_VALIDATION_HEADING,
    PREDICTION_LAB_CONCLUSION,
    best_model_metric_labels,
    build_model_summary,
)

__all__ = ["build_frontend_payloads", "write_frontend_payloads", "export_frontend_data"]

DEFAULT_TARGET_DIR = PROJECT_ROOT / "frontend" / "public" / "data"
SNAPSHOT_SCHEMA_VERSION = 1

OUTPUT_FILE_MEANINGS = {
    "gpr": ("GPR Data", "Daily geopolitical risk values and shock flags."),
    "analysis_panel": ("Start Here", "The main daily dataset: country ETF returns merged with GPR and controls."),
    "group_returns": ("Market Reaction", "Average daily ETF returns by developed and emerging market group."),
    "abnormal_event_study": ("Market Reaction", "Average abnormal returns around GPR shock days."),
    "controlled_regression": ("Regression Results", "The panel regression after market controls are included."),
    "date_fe_regression": ("Regression Results", "The developed-versus-emerging comparison with date fixed effects."),
    "quantile_regression": ("Regression Results", "The downside-risk check across return percentiles."),
    "local_projections": ("Market Reaction", "The estimated response path after GPR shock days."),
    "drawdown_metrics": ("Prediction Lab", "Out-of-sample drawdown-risk classifier scores."),
    "drawdown_lift": ("Prediction Lab", "How concentrated bad outcomes are in high-risk buckets."),
    "drawdown_country_risk_summary": ("Prediction Lab", "Average predicted and realized drawdown risk by country."),
    "rolling_beta": ("Country Sensitivity", "Rolling country ETF sensitivity to GPR."),
    "large_returns": ("Data Quality", "Large daily ETF returns worth checking before over-interpreting results."),
    "evidence_summary": ("Start Here", "A compact cross-method evidence table."),
}


def _spec_path(spec: OutputSpec, root: Path) -> Path:
    return root / spec.path.relative_to(PROJECT_ROOT)


def _read_output(spec: OutputSpec, root: Path) -> pd.DataFrame:
    options: dict[str, Any] = {}
    if spec.date_columns:
        options["parse_dates"] = list(spec.date_columns)
    if spec.low_memory is not None:
        options["low_memory"] = spec.low_memory
    df = pd.read_csv(_spec_path(spec, root), **options)
    validate_output_schema(df, spec)
    return df


def _missing_spec_paths(root: Path) -> list[str]:
    missing: list[str] = []
    for spec in OUTPUT_SPECS.values():
        path = _spec_path(spec, root)
        if not path.exists():
            missing.append(str(path.relative_to(root)))
    return missing


def _scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        v = float(value)
        return None if not math.isfinite(v) else v
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    return value


def _df_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d")
    records = df.to_dict(orient="records")
    return [{key: _scalar(value) for key, value in record.items()} for record in records]


def _direction_label(value: Any) -> str:
    if value is None or pd.isna(value):
        return "Unknown"
    numeric = float(value)
    if abs(numeric) < 1e-12:
        return "Near zero"
    return "Positive" if numeric > 0 else "Negative"


def _p_value_reader_label(value: Any) -> str:
    if value is None or pd.isna(value):
        return "Descriptive only"
    numeric = float(value)
    if numeric < 0.05:
        return "Conventional p < 0.05"
    if numeric < 0.10:
        return "Suggestive p < 0.10"
    return "Weak in this run"


def _market_group_label(value: Any) -> str:
    raw = str(value)
    if raw == "developed":
        return "Developed markets"
    if raw == "emerging":
        return "Emerging markets"
    return raw


def _load_monthly_bundle(root: Path):
    for mode, config in MONTHLY_MODES.items():
        bundle = _load_monthly_output_mode(mode, dataclasses.replace(config, root=root))
        if bundle is not None:
            return bundle
    return None


def _output_file_rows(outputs: dict[str, pd.DataFrame]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, (reader_page, meaning) in OUTPUT_FILE_MEANINGS.items():
        spec = OUTPUT_SPECS[key]
        rows.append(
            {
                "file": str(spec.path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "reader_page": reader_page,
                "rows": int(len(outputs[key])),
                "plain_meaning": meaning,
            }
        )
    return rows


def _event_study_reader_rows(abnormal: pd.DataFrame) -> list[dict[str, Any]]:
    abnormal = abnormal.copy()
    abnormal["accumulation_start_day"] = abnormal.groupby("market_group")["relative_day"].transform("min")
    wanted_days = [0, 1, 5, 10]
    key_days = abnormal.loc[abnormal["relative_day"].isin(wanted_days)].copy()
    if key_days.empty:
        key_days = abnormal.copy()
    key_days = key_days.sort_values(["market_group", "relative_day"])

    rows: list[dict[str, Any]] = []
    for row in key_days.to_dict(orient="records"):
        group = _market_group_label(row["market_group"])
        day = int(row["relative_day"])
        estimate = row["cumulative_average_abnormal_return"]
        start_day = int(row["accumulation_start_day"])
        direction = _direction_label(estimate)
        strength = _p_value_reader_label(row.get("p_value"))
        rows.append(
            {
                "market_group": group,
                "relative_day": day,
                "cumulative_average_abnormal_return": estimate,
                "average_abnormal_return": row["average_abnormal_return"],
                "std_error": row["std_error"],
                "t_stat": row["t_stat"],
                "p_value": row["p_value"],
                "observation_count": row["observation_count"],
                "event_count": row["event_count"],
                "accumulation_start_day": start_day,
                "direction": direction,
                "evidence_strength": strength,
                "plain_note": (
                    f"{group} cumulative abnormal log return was {direction.lower()} at relative day {day}; "
                    f"the displayed series starts at day {start_day} and is not rebased at this checkpoint. "
                    f"The existing p-value is {strength.lower()} and is not adjusted for dependence "
                    "between ETFs exposed to common events. Weak evidence is not proof of no effect."
                ),
            }
        )
    return [{key: _scalar(value) for key, value in row.items()} for row in rows]


def _first_term_row(df: pd.DataFrame, term: str) -> pd.Series | None:
    matches = df.loc[df["term"] == term]
    if matches.empty:
        return None
    return matches.iloc[0]


def _reader_regression_row(
    *,
    test: str,
    check: str,
    row: pd.Series | None,
    note: str,
) -> dict[str, Any]:
    if row is None:
        return {
            "test": test,
            "what_it_checks": check,
            "direction": "Missing",
            "estimate": None,
            "p_value": None,
            "evidence_strength": "Missing output",
            "plain_note": note,
        }
    return {
        "test": test,
        "what_it_checks": check,
        "direction": _direction_label(row.get("estimate")),
        "estimate": row.get("estimate"),
        "p_value": row.get("p_value"),
        "evidence_strength": _p_value_reader_label(row.get("p_value")),
        "plain_note": note,
    }


def _regression_translation_rows(outputs: dict[str, pd.DataFrame]) -> list[dict[str, Any]]:
    controlled_gpr = _first_term_row(outputs["controlled_regression"], "gpr_change_z")
    emerging_extra = _first_term_row(outputs["date_fe_regression"], "gpr_change_z:emerging_market")

    quantile = outputs["quantile_regression"].sort_values("quantile")
    quantile_gpr = _first_term_row(quantile, "gpr_change_z")
    if quantile_gpr is None and not quantile.empty:
        quantile_gpr = quantile.iloc[0]

    return [
        _reader_regression_row(
            test="Controlled GPR association",
            check="Whether GPR jumps are associated with ETF returns after market controls.",
            row=controlled_gpr,
            note="Read this as conditional association, not cause and effect.",
        ),
        _reader_regression_row(
            test="Emerging-market extra response",
            check="Whether emerging-market ETFs have an extra GPR response versus developed-market ETFs.",
            row=emerging_extra,
            note="This is the cleanest daily-panel check for the emerging-market question.",
        ),
        _reader_regression_row(
            test="Downside-risk check",
            check="Whether lower-return days show a different GPR relationship.",
            row=quantile_gpr,
            note="This is a tail-risk diagnostic; it is not proof that the pattern is stable.",
        ),
    ]


def _static_copy() -> dict[str, Any]:
    return {
        "central_question": CENTRAL_PROJECT_QUESTION,
        "intro": DASHBOARD_INTRO,
        "main_takeaway": DASHBOARD_MAIN_TAKEAWAY,
        "use_note": DASHBOARD_USE_NOTE,
        "job_statements": [
            {"title": title, "body": body} for title, body in OVERVIEW_JOB_STATEMENTS
        ],
        "reader_path": [dict(row) for row in OVERVIEW_READER_PATH],
        "current_answer_points": list(OVERVIEW_CURRENT_ANSWER_POINTS),
        "does_not_prove_points": list(OVERVIEW_DOES_NOT_PROVE_POINTS),
        "method_map": [dict(row) for row in METHOD_MAP_ROWS],
        "glossary": dict(GLOSSARY_TERMS),
        "prediction_metric_explanations": dict(PREDICTION_METRIC_EXPLANATIONS),
        "how_to_read": dict(HOW_TO_READ_NOTES),
        "beginner_guides": {
            key: {
                "question": value["question"],
                "takeaways": [
                    {"title": title, "body": body} for title, body in value["takeaways"]
                ],
                "does_not_prove": value["does_not_prove"],
            }
            for key, value in BEGINNER_TAB_GUIDES.items()
        },
        "monthly_notices": {
            "sample": MONTHLY_SAMPLE_NOTICE,
            "real": MONTHLY_REAL_NOTICE,
            "cluster": MONTHLY_CLUSTER_NOTICE,
            "mode_priority": MONTHLY_MODE_PRIORITY_NOTICE,
            "empty_state_commands": list(MONTHLY_EMPTY_STATE_COMMANDS),
            "empty_state_note": MONTHLY_EMPTY_STATE_NOTE,
        },
        "prediction_lab": {
            "conclusion": PREDICTION_LAB_CONCLUSION,
            "validation_heading": ML_VALIDATION_HEADING,
            "validation_caption": ML_VALIDATION_CAPTION,
            "feature_importance_caption": FEATURE_IMPORTANCE_CAPTION,
            "drawdown_horizon_days": int(DRAWDOWN_HORIZON_DAYS),
            "drawdown_threshold": float(DRAWDOWN_THRESHOLD),
        },
    }


def _recorded_abnormal_event_dates(root: Path, selected_dates: pd.Series) -> pd.DatetimeIndex | None:
    path = root / "data" / "processed" / "event_windows_abnormal.csv"
    if not path.exists():
        return None
    recorded = pd.read_csv(path, usecols=["event_date"])
    dates = pd.DatetimeIndex(pd.to_datetime(recorded["event_date"], errors="raise").drop_duplicates())
    if dates.isna().any() or not dates.isin(selected_dates).all():
        raise ValueError("Recorded abnormal event dates do not match the selected GPR events.")
    return dates


def _overview_payloads(
    outputs: dict[str, pd.DataFrame], panel: pd.DataFrame, gpr: pd.DataFrame, root: Path
) -> dict[str, Any]:
    start_date = panel["date"].min().date().isoformat()
    end_date = panel["date"].max().date().isoformat()
    country_count = int(panel["country"].nunique())
    gpr = gpr.copy()
    gpr["gpr_change_shock"] = gpr["gpr_change_shock"].eq(True)
    # Match run_event_study: select peaks before restricting the overview dates.
    selected_dates = select_peak_cluster_events(
        gpr, shock_column="gpr_change_shock", value_column="gpr_change", min_gap_days=EVENT_MIN_GAP_DAYS
    )
    gpr["selected_for_event_study"] = gpr["date"].isin(selected_dates)
    gpr_window = gpr.loc[gpr["date"].between(start_date, end_date)].sort_values("date")
    shock_count = int(gpr_window["gpr_change_shock"].sum())
    top_shocks = gpr_window.dropna(subset=["gpr_change"]).sort_values("gpr_change", ascending=False).head(25)
    selected_events = gpr_window.loc[
        gpr_window["selected_for_event_study"], ["date", "gpr", "gpr_change", "gpr_change_shock"]
    ].copy()
    recorded_dates = _recorded_abnormal_event_dates(root, selected_dates)
    represented_count = None
    selected_events["represented_in_abnormal_study"] = None
    if recorded_dates is not None:
        selected_events["represented_in_abnormal_study"] = selected_events["date"].isin(recorded_dates)
        represented_count = int(((recorded_dates >= start_date) & (recorded_dates <= end_date)).sum())
    timeline_columns = [
        "date", "gpr", "gpr_change", "gpr_act", "gpr_threat", "event",
        "gpr_change_shock", "selected_for_event_study",
    ]

    group_chart = outputs["group_returns"].copy()
    group_chart["cumulative_average_return"] = group_chart.groupby("market_group")[
        "average_return"
    ].cumsum()

    evidence_map = build_evidence_map(outputs["evidence_summary"])

    return {
        "overview": {
            "headline": {
                "country_count": country_count,
                "start_date": start_date,
                "end_date": end_date,
                "shock_count": shock_count,
                "selected_event_count": int(len(selected_events)),
                "represented_event_count": represented_count,
            },
            "definitions": {
                "shock_days": (
                    "Flagged GPR-change days within the displayed ETF-panel dates, using the stored "
                    f"expanding-window flag: change at or above the prior-data {DEFAULT_GPR_SHOCK_QUANTILE:.0%} "
                    f"quantile after at least {GPR_EXPANDING_SHOCK_MIN_PERIODS} prior observations."
                ),
                "largest_jumps": (
                    "The 25 largest available daily GPR index-point changes within the displayed sample. "
                    "These highlighted dates are not necessarily flagged days or selected event-study dates."
                ),
                "selected_events": (
                    "Peak dates are selected from flagged days over the full GPR source history before "
                    f"clipping this list to the displayed sample: gaps of at least {EVENT_MIN_GAP_DAYS} calendar "
                    "days separate clusters, and the largest GPR change in each cluster is selected. "
                    "Selection does not guarantee usable ETF estimation history. Represented dates come "
                    "from the recorded abnormal-event windows when available; otherwise they are unknown. "
                    "Per-group, per-day contributing event counts are reported in the inference table."
                ),
                "event_alignment": (
                    "Day 0 is each ETF's first available trading observation on or after the GPR event date; "
                    "relative days count ETF trading observations, not calendar days."
                ),
                "accumulation": (
                    "Abnormal cumulative returns sum each ETF-event's abnormal log returns from its first "
                    "available relative day, then average those cumulative sums. Raw cumulative returns sum "
                    "the group average log return from its earliest relative day. The table reports each "
                    "group series' earliest day; boundary-truncated ETF-event windows can start later. "
                    "Negative relative days are included: neither series resets to zero on day 0. "
                    "Known raw-window limitation, left unchanged: events before an ETF's first observation "
                    "can be aligned to that first observation, so raw counts can include pre-inception events. "
                    "The abnormal-return builder excludes those cases through its estimation-history requirement."
                ),
                "inference": (
                    "Existing standard errors equal the sample standard deviation of ETF-event cumulative "
                    "abnormal returns divided by the square root of their count; p-values use a two-sided "
                    "Student t test. This inference is not adjusted for dependence between ETFs exposed "
                    "to common events. Observation counts describe nonmissing daily abnormal returns; "
                    "event counts describe distinct dates at that relative day. No confidence intervals "
                    "are supplied. Weak evidence is not proof of no effect."
                ),
                "return_units": (
                    "Returns and standard errors are decimal log-return units in the export; multiplying "
                    "by 100 gives log-return percentage points. They are USD country-ETF proxies, not "
                    "local-market simple returns, causal effects, or trading forecasts."
                ),
            },
        },
        "gpr_timeline": {
            "series": _df_records(gpr_window[timeline_columns]),
            "top_shocks": _df_records(top_shocks[timeline_columns]),
            "selected_events": _df_records(selected_events),
        },
        "group_returns": _df_records(
            group_chart[["date", "market_group", "average_return", "cumulative_average_return"]]
        ),
        "evidence_map": _df_records(evidence_map),
    }


def _explanation_payloads(outputs: dict[str, pd.DataFrame]) -> dict[str, Any]:
    abnormal = outputs["abnormal_event_study"].loc[
        :, list(OUTPUT_SPECS["abnormal_event_study"].required_columns)
    ].copy()
    abnormal["accumulation_start_day"] = abnormal.groupby("market_group")["relative_day"].transform("min")
    raw = outputs["event_study"].loc[:, list(OUTPUT_SPECS["event_study"].required_columns)].copy()
    raw["raw_accumulation_start_day"] = raw.groupby("market_group")["relative_day"].transform("min")
    raw = raw.rename(columns={"observation_count": "raw_observation_count", "event_count": "raw_event_count"})
    event_study = (
        abnormal
        .merge(
            raw,
            on=["relative_day", "market_group"],
            how="outer",
        )
        .sort_values(["market_group", "relative_day"])
    )

    robustness = outputs["event_robustness"].copy()
    robustness["shock_quantile_label"] = robustness["shock_quantile"].map(lambda value: f"{value:.0%}")

    return {
        "event_study": _df_records(event_study),
        "event_robustness": _df_records(robustness),
        "regression": {
            "baseline": _df_records(select_key_regression_terms(outputs["regression"])),
            "controlled": _df_records(select_key_regression_terms(outputs["controlled_regression"])),
            "date_fe": _df_records(select_key_regression_terms(outputs["date_fe_regression"])),
        },
        "panel_sample_robustness": _df_records(outputs["panel_sample_robustness"]),
        "quantile_regression": _df_records(select_key_regression_terms(outputs["quantile_regression"])),
        "local_projections": _df_records(outputs["local_projections"]),
        "rolling_beta": _df_records(outputs["rolling_beta"][["date", "country", "market_group", "rolling_gpr_beta"]]),
    }


def _prediction_payloads(outputs: dict[str, pd.DataFrame]) -> dict[str, Any]:
    model_summary = build_model_summary(outputs["drawdown_metrics"], outputs["drawdown_lift"])
    best_labels = best_model_metric_labels(model_summary)
    mean_base_rate = float(outputs["drawdown_metrics"]["base_rate"].mean())

    return {
        "prediction_summary": {
            "model_comparison": _df_records(model_summary),
            "best_metrics": {
                key: {"label": label, "value": value}
                for key, (label, value) in best_labels.items()
            },
            "mean_event_rate": mean_base_rate,
        },
        "drawdown_calibration": _df_records(outputs["drawdown_calibration"]),
        "drawdown_lift": _df_records(outputs["drawdown_lift"]),
        "drawdown_threshold_metrics": _df_records(outputs["drawdown_threshold_metrics"]),
        "drawdown_country_risk_summary": _df_records(outputs["drawdown_country_risk_summary"]),
        "drawdown_feature_importance": _df_records(outputs["drawdown_importance"]),
        "drawdown_metrics": _df_records(outputs["drawdown_metrics"]),
    }


def _data_methods_payloads(outputs: dict[str, pd.DataFrame], panel: pd.DataFrame, root: Path) -> dict[str, Any]:
    coverage = build_country_coverage(panel)
    monthly_bundle = _load_monthly_bundle(root)

    monthly: dict[str, Any]
    if monthly_bundle is None:
        monthly = {"available": False}
    else:
        panel_month = monthly_bundle.panel.copy()
        panel_month["date_month"] = pd.to_datetime(panel_month["date_month"])
        month_level = panel_month.drop_duplicates("date_month").sort_values("date_month")
        provenance = monthly_provenance_rows(monthly_bundle)
        monthly = {
            "available": True,
            "mode": monthly_bundle.mode,
            "mode_label": monthly_bundle.mode_label,
            "start_month": month_level["date_month"].min().date().isoformat(),
            "end_month": month_level["date_month"].max().date().isoformat(),
            "source_count": len(monthly_bundle.source_names),
            "source_names": list(monthly_bundle.source_names),
            "provenance": _df_records(provenance),
            "month_level": _df_records(
                month_level[["date_month", "gpr_change_z", "spread_em_dev"]]
            ),
            "regressions": _df_records(monthly_bundle.regressions) if monthly_bundle.regressions is not None else None,
            "forecasts": _df_records(monthly_bundle.forecasts) if monthly_bundle.forecasts is not None else None,
        }

    return {
        "country_coverage": _df_records(coverage),
        "large_returns": _df_records(outputs["large_returns"][["date", "ticker", "country", "return", "abs_return"]]),
        "monthly": monthly,
    }


def _reader_summary_payloads(outputs: dict[str, pd.DataFrame]) -> dict[str, Any]:
    return {
        "reader_summaries": {
            "output_files": _output_file_rows(outputs),
            "market_reaction": _event_study_reader_rows(outputs["abnormal_event_study"]),
            "regression_translation": _regression_translation_rows(outputs),
        }
    }


def build_frontend_payloads(root: Path | None = None) -> dict[str, Any]:
    """Build every JSON payload the frontend needs, rooted at ``root``.

    When processed data is missing, returns a minimal payload with
    ``available=False`` plus the static copy so the frontend can render an
    empty state.
    """
    root = Path(root) if root is not None else PROJECT_ROOT
    payloads: dict[str, Any] = {"copy": _static_copy()}

    missing = _missing_spec_paths(root)
    if missing:
        payloads["manifest"] = {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "profile": "local",
            "datasets": sorted(payloads),
            "available": False,
            "missing_files": missing,
            "build_date": pd.Timestamp.now("UTC").date().isoformat(),
        }
        return payloads

    outputs = {name: _read_output(spec, root) for name, spec in OUTPUT_SPECS.items()}
    panel = outputs["analysis_panel"]
    gpr = outputs["gpr"]

    payloads.update(_overview_payloads(outputs, panel, gpr, root))
    payloads.update(_explanation_payloads(outputs))
    payloads.update(_prediction_payloads(outputs))
    payloads.update(_data_methods_payloads(outputs, panel, root))
    payloads.update(_reader_summary_payloads(outputs))
    answer_points = build_snapshot_answer(outputs["controlled_regression"], outputs["date_fe_regression"])
    payloads["copy"]["intro"] = (
        "This dashboard studies whether equity markets respond to geopolitical risk shocks, "
        f"using {payloads['overview']['headline']['country_count']} country ETF proxies in this snapshot."
    )
    payloads["copy"]["main_takeaway"] = answer_points[0]
    payloads["copy"]["current_answer_points"] = answer_points

    payloads["manifest"] = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "profile": "local",
        "datasets": sorted(payloads),
        "available": True,
        "build_date": pd.Timestamp.now("UTC").date().isoformat(),
        "start_date": panel["date"].min().date().isoformat(),
        "end_date": panel["date"].max().date().isoformat(),
        "country_count": int(panel["country"].nunique()),
        "shock_count": payloads["overview"]["headline"]["shock_count"],
        "monthly_mode": (
            payloads["monthly"]["mode"] if payloads["monthly"].get("available") else None
        ),
    }
    return payloads


def write_frontend_payloads(payloads: dict[str, Any], target_dir: Path) -> Path:
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        path = target_dir / f"{name}.json"
        path.write_text(
            json.dumps(payload, indent=2, default=_json_default), encoding="utf-8"
        )
    return target_dir


def export_frontend_data(root: Path | None = None, target_dir: Path | None = None) -> Path:
    root = Path(root) if root is not None else PROJECT_ROOT
    target = Path(target_dir) if target_dir is not None else root / "frontend" / "public" / "data"
    payloads = build_frontend_payloads(root)
    return write_frontend_payloads(payloads, target)


def _json_default(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
