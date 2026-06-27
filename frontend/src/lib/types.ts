// Types mirror the JSON payloads written by scripts/export_frontend_data.py.

export interface Manifest {
  available: boolean;
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
  };
}

export interface GprTimelinePayload {
  series: Row[];
  top_shocks: Row[];
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

export interface FrontendBundle {
  manifest: Manifest;
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
  country_coverage: Row[];
  large_returns: Row[];
  monthly: MonthlyPayload;
}
