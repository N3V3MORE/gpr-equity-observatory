import type {
  Copy,
  FrontendBundle,
  GprTimelinePayload,
  MonthlyPayload,
  OverviewPayload,
  PredictionSummaryPayload,
  Row,
} from "./types";

const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");
const DATA_DIR = "data";
const DATA_BASE = `${BASE_PATH}/${DATA_DIR}`;

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${DATA_BASE}/${path}`);
  if (!res.ok) {
    throw new Error(`Failed to load ${path}: ${res.status}`);
  }
  return (await res.json()) as T;
}

function emptyBundle(): FrontendBundle {
  return {
    manifest: { available: false },
    copy: {
      central_question: "",
      intro: "",
      main_takeaway: "",
      use_note: "",
      job_statements: [],
      reader_path: [],
      current_answer_points: [],
      does_not_prove_points: [],
      method_map: [],
      glossary: {},
      prediction_metric_explanations: {},
      how_to_read: {},
      beginner_guides: {},
      monthly_notices: {
        sample: "",
        real: "",
        cluster: "",
        mode_priority: "",
        empty_state_commands: [],
        empty_state_note: "",
      },
      prediction_lab: {
        conclusion: "",
        validation_heading: "",
        validation_caption: "",
        feature_importance_caption: "",
        drawdown_horizon_days: 0,
        drawdown_threshold: 0,
      },
    },
    overview: { headline: { country_count: 0, start_date: "", end_date: "", shock_count: 0 } },
    gpr_timeline: { series: [], top_shocks: [] },
    group_returns: [],
    evidence_map: [],
    event_study: [],
    event_robustness: [],
    regression: { baseline: [], controlled: [], date_fe: [] },
    panel_sample_robustness: [],
    quantile_regression: [],
    local_projections: [],
    rolling_beta: [],
    prediction_summary: { model_comparison: [], best_metrics: {}, mean_event_rate: 0 },
    drawdown_calibration: [],
    drawdown_lift: [],
    drawdown_threshold_metrics: [],
    drawdown_country_risk_summary: [],
    drawdown_feature_importance: [],
    drawdown_metrics: [],
    country_coverage: [],
    large_returns: [],
    monthly: { available: false },
  };
}

export async function loadBundle(): Promise<FrontendBundle> {
  const manifest = await fetchJson<FrontendBundle["manifest"]>("manifest.json");
  if (!manifest.available) {
    const copy = await safeFetch<Copy>("copy.json");
    return { ...emptyBundle(), manifest, copy: copy ?? emptyBundle().copy };
  }
  const [
    copy,
    overview,
    gpr_timeline,
    group_returns,
    evidence_map,
    event_study,
    event_robustness,
    regression,
    panel_sample_robustness,
    quantile_regression,
    local_projections,
    prediction_summary,
    drawdown_calibration,
    drawdown_lift,
    drawdown_threshold_metrics,
    drawdown_country_risk_summary,
    drawdown_feature_importance,
    drawdown_metrics,
    country_coverage,
    large_returns,
    monthly,
  ] = await Promise.all([
    safeFetch<Copy>("copy.json"),
    safeFetch<OverviewPayload>("overview.json"),
    safeFetch<GprTimelinePayload>("gpr_timeline.json"),
    safeFetch<Row[]>("group_returns.json"),
    safeFetch<Row[]>("evidence_map.json"),
    safeFetch<Row[]>("event_study.json"),
    safeFetch<Row[]>("event_robustness.json"),
    safeFetch<FrontendBundle["regression"]>("regression.json"),
    safeFetch<Row[]>("panel_sample_robustness.json"),
    safeFetch<Row[]>("quantile_regression.json"),
    safeFetch<Row[]>("local_projections.json"),
    safeFetch<PredictionSummaryPayload>("prediction_summary.json"),
    safeFetch<Row[]>("drawdown_calibration.json"),
    safeFetch<Row[]>("drawdown_lift.json"),
    safeFetch<Row[]>("drawdown_threshold_metrics.json"),
    safeFetch<Row[]>("drawdown_country_risk_summary.json"),
    safeFetch<Row[]>("drawdown_feature_importance.json"),
    safeFetch<Row[]>("drawdown_metrics.json"),
    safeFetch<Row[]>("country_coverage.json"),
    safeFetch<Row[]>("large_returns.json"),
    safeFetch<MonthlyPayload>("monthly.json"),
  ]);

  return {
    manifest,
    copy: copy ?? emptyBundle().copy,
    overview: overview ?? emptyBundle().overview,
    gpr_timeline: gpr_timeline ?? emptyBundle().gpr_timeline,
    group_returns: group_returns ?? [],
    evidence_map: evidence_map ?? [],
    event_study: event_study ?? [],
    event_robustness: event_robustness ?? [],
    regression: regression ?? { baseline: [], controlled: [], date_fe: [] },
    panel_sample_robustness: panel_sample_robustness ?? [],
    quantile_regression: quantile_regression ?? [],
    local_projections: local_projections ?? [],
    rolling_beta: [],
    prediction_summary: prediction_summary ?? emptyBundle().prediction_summary,
    drawdown_calibration: drawdown_calibration ?? [],
    drawdown_lift: drawdown_lift ?? [],
    drawdown_threshold_metrics: drawdown_threshold_metrics ?? [],
    drawdown_country_risk_summary: drawdown_country_risk_summary ?? [],
    drawdown_feature_importance: drawdown_feature_importance ?? [],
    drawdown_metrics: drawdown_metrics ?? [],
    country_coverage: country_coverage ?? [],
    large_returns: large_returns ?? [],
    monthly: monthly ?? { available: false },
  };
}

async function safeFetch<T>(path: string): Promise<T | null> {
  try {
    return await fetchJson<T>(path);
  } catch {
    return null;
  }
}

// rolling_beta.json is large (~MBs), so LazyRollingBeta fetches it only when
// the country-sensitivity section is near the viewport.
export async function loadRollingBeta(): Promise<Row[]> {
  const rows = await safeFetch<Row[]>("rolling_beta.json");
  return rows ?? [];
}

export type { Row };
