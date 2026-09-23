// Types mirror the JSON payloads written by scripts/export_frontend_data.py.

export const DATASET_NAMES = [
  "copy", "overview", "gpr_timeline", "group_returns", "evidence_map", "event_study",
  "event_robustness", "regression", "panel_sample_robustness", "quantile_regression",
  "local_projections", "rolling_beta", "prediction_summary", "drawdown_calibration",
  "drawdown_lift", "drawdown_threshold_metrics", "drawdown_country_risk_summary",
  "drawdown_feature_importance", "drawdown_metrics", "reader_summaries",
  "country_coverage", "large_returns", "monthly",
] as const;

export type DatasetName = (typeof DATASET_NAMES)[number];
export type DatasetStatus = "available" | "unavailable" | "excluded" | "deferred";

export interface Manifest {
  available: boolean;
  // Absent together only for legacy local exports. A profile is not publication approval.
  schema_version?: 1;
  profile?: "local" | "public";
  datasets?: DatasetName[];
  // Publication approval is recorded separately from dataset selection.
  publication_status?: "candidate" | "approved";
  snapshot_id?: string;
  data_kind?: "real" | "synthetic" | "unreviewed";
  approved_downloads?: { label: string; path: string; table?: string; units?: string }[];
  build_date?: string;
  start_date?: string;
  end_date?: string;
  country_count?: number;
  shock_count?: number;
  monthly_mode?: string | null;
  missing_files?: string[];
}

export interface Copy {
  central_question: string;
  intro: string;
  main_takeaway: string;
  use_note: string;
  job_statements: { title: string; body: string }[];
  reader_path: { step: string; title: string; body: string }[];
  current_answer_points: string[];
  does_not_prove_points: string[];
  method_map: { Question: string; Tool: string; Output: string; "What to look for": string }[];
  glossary: Record<string, string>;
  prediction_metric_explanations: Record<string, string>;
  how_to_read: Record<string, string>;
  beginner_guides: Record<
    string,
    { question: string; takeaways: { title: string; body: string }[]; does_not_prove: string }
  >;
  monthly_notices: {
    sample: string;
    real: string;
    cluster: string;
    mode_priority: string;
    empty_state_commands: string[];
    empty_state_note: string;
  };
  prediction_lab: {
    conclusion: string;
    validation_heading: string;
    validation_caption: string;
    feature_importance_caption: string;
    drawdown_horizon_days: number;
    drawdown_threshold: number;
  };
}

export type Row = Record<string, unknown>;

export interface OverviewPayload {
  headline: {
    country_count: number;
    start_date: string;
    end_date: string;
    shock_count: number;
    selected_event_count: number;
    represented_event_count: number | null;
  };
  definitions: Record<"shock_days" | "largest_jumps" | "selected_events" | "event_alignment" | "accumulation" | "inference" | "return_units", string>;
}

export interface GprTimelinePayload {
  series: Row[];
  top_shocks: Row[];
  selected_events: Row[];
}

export interface MonthlyPayload {
  available: boolean;
  mode?: string;
  mode_label?: string;
  start_month?: string;
  end_month?: string;
  source_count?: number;
  source_names?: string[];
  provenance?: Row[];
  month_level?: Row[];
  regressions?: Row[] | null;
  forecasts?: Row[] | null;
}

export interface PredictionSummaryPayload {
  model_comparison: Row[];
  best_metrics: {
    auc?: { label: string; value: string };
    ap?: { label: string; value: string };
    lift?: { label: string; value: string };
  };
  mean_event_rate: number;
}

export interface ReaderSummariesPayload {
  output_files: Row[];
  market_reaction: Row[];
  regression_translation: Row[];
}

export interface FrontendBundle {
  manifest: Manifest;
  dataset_status: Record<DatasetName, DatasetStatus>;
  copy: Copy;
  overview: OverviewPayload;
  gpr_timeline: GprTimelinePayload;
  group_returns: Row[];
  evidence_map: Row[];
  event_study: Row[];
  event_robustness: Row[];
  regression: { baseline: Row[]; controlled: Row[]; date_fe: Row[] };
  panel_sample_robustness: Row[];
  quantile_regression: Row[];
  local_projections: Row[];
  rolling_beta: Row[];
  prediction_summary: PredictionSummaryPayload;
  drawdown_calibration: Row[];
  drawdown_lift: Row[];
  drawdown_threshold_metrics: Row[];
  drawdown_country_risk_summary: Row[];
  drawdown_feature_importance: Row[];
  drawdown_metrics: Row[];
  reader_summaries: ReaderSummariesPayload;
  country_coverage: Row[];
  large_returns: Row[];
  monthly: MonthlyPayload;
}
