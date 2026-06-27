// Central friendly-label map. No raw column name ever reaches the screen
// without going through one of these configs. This is the single source of
// truth for plain-English headers, tooltips, and value formatting.

import { bps, fixed, multiple, num, percent, signedFixed, str } from "./format";

export type Align = "left" | "right";

export interface ColumnSpec {
  key: string;
  label: string;
  tooltip?: string;
  align?: Align;
  format?: (value: unknown) => string;
}

export const MODEL_NAME_LABELS: Record<string, string> = {
  constant_baseline: "Baseline (historical average)",
  volatility_only: "Volatility only",
  gpr_only: "GPR only",
  market_controls_only: "Market controls only",
  volatility_plus_gpr: "Volatility + GPR",
  full_features: "All features",
};

export function modelName(value: unknown): string {
  const raw = str(value);
  return MODEL_NAME_LABELS[raw] ?? raw;
}

export const MODEL_COMPARISON_COLUMNS: ColumnSpec[] = [
  {
    key: "model_name",
    label: "Model",
    tooltip: "Which group of inputs the model was allowed to use.",
    format: modelName,
  },
  {
    key: "what_it_uses",
    label: "What it uses",
    tooltip: "A short description of the inputs fed to this model.",
  },
  {
    key: "mean_roc_auc",
    label: "Ranking score",
    tooltip: "How well the model separates bad outcomes from normal ones. 0.5 is no better than a coin flip; higher is better.",
    align: "right",
    format: (v) => fixed(v, 3),
  },
  {
    key: "delta_auc_vs_constant_baseline",
    label: "Improvement vs baseline",
    tooltip: "How much better this model ranks risk than just using the historical average rate. Near zero means no real help.",
    align: "right",
    format: (v) => signedFixed(v, 3),
  },
  {
    key: "mean_average_precision",
    label: "High-risk hit rate",
    tooltip: "Of the actual bad outcomes, how concentrated they are near the top of the ranked list. Higher is better.",
    align: "right",
    format: (v) => fixed(v, 3),
  },
  {
    key: "delta_ap_vs_constant_baseline",
    label: "Hit-rate improvement",
    tooltip: "Improvement in high-risk hit rate over the baseline.",
    align: "right",
    format: (v) => signedFixed(v, 3),
  },
  {
    key: "top_decile_lift",
    label: "Top-10% concentration",
    tooltip: "How much more common bad outcomes are in the riskiest 10% of rows versus the whole sample. 1x means no help; higher is better.",
    align: "right",
    format: (v) => multiple(v, 2),
  },
  {
    key: "mean_brier_score",
    label: "Probability error",
    tooltip: "How close predicted probabilities were to what actually happened. Lower is better.",
    align: "right",
    format: (v) => fixed(v, 3),
  },
  {
    key: "delta_brier_vs_constant_baseline",
    label: "Error improvement",
    tooltip: "How much the probability error dropped versus the baseline. Higher is better.",
    align: "right",
    format: (v) => signedFixed(v, 3),
  },
  {
    key: "model_verdict",
    label: "Verdict",
    tooltip: "A cautious plain-English summary of how much ranking signal this model shows.",
  },
];

export const EVIDENCE_MAP_COLUMNS: ColumnSpec[] = [
  { key: "Method", label: "Method" },
  { key: "Question answered", label: "Question answered" },
  { key: "Direction", label: "Direction" },
  { key: "Estimate", label: "Estimate" },
  { key: "p-value / metric", label: "p-value / metric", tooltip: "A statistical check; smaller p-values mean stronger evidence, but not proof." },
  { key: "Evidence strength", label: "Evidence strength" },
  { key: "Plain-English takeaway", label: "Plain-English takeaway" },
];

export const REGRESSION_TERM_COLUMNS: ColumnSpec[] = [
  {
    key: "term",
    label: "Term",
    tooltip: "The variable being measured. The 'emerging-market interaction' is the extra GPR effect for emerging markets versus developed markets.",
    format: termLabel,
  },
  {
    key: "estimate",
    label: "Estimate",
    tooltip: "The estimated relationship. Negative means GPR rises are associated with lower returns.",
    align: "right",
    format: (v) => bps(v),
  },
  { key: "std_error", label: "Std. error", align: "right", format: (v) => bps(v) },
  { key: "t_stat", label: "t-stat", align: "right", format: (v) => fixed(v, 2) },
  {
    key: "p_value",
    label: "p-value",
    tooltip: "Smaller means stronger evidence the estimate is not just noise. Below 0.05 is a common threshold; it is not proof.",
    align: "right",
    format: (v) => fixed(v, 3),
  },
];

export const PANEL_ROBUSTNESS_COLUMNS: ColumnSpec[] = [
  { key: "scenario", label: "Scenario", tooltip: "Which crisis window was excluded before re-running the model." },
  { key: "term", label: "Term", format: termLabel },
  { key: "estimate", label: "Estimate", align: "right", format: (v) => bps(v) },
  { key: "std_error", label: "Std. error", align: "right", format: (v) => bps(v) },
  { key: "t_stat", label: "t-stat", align: "right", format: (v) => fixed(v, 2) },
  { key: "p_value", label: "p-value", align: "right", format: (v) => fixed(v, 3) },
  { key: "observation_count", label: "Observations", align: "right", format: (v) => num(v) },
];

export const QUANTILE_COLUMNS: ColumnSpec[] = [
  {
    key: "quantile",
    label: "Return percentile",
    tooltip: "Lower percentiles describe worse return days. 0.1 = the worst 10% of days.",
    align: "right",
    format: (v) => percent(v, 0),
  },
  { key: "term", label: "Term", format: termLabel },
  { key: "estimate", label: "Estimate", align: "right", format: (v) => bps(v) },
  { key: "std_error", label: "Std. error", align: "right", format: (v) => bps(v) },
  { key: "t_stat", label: "t-stat", align: "right", format: (v) => fixed(v, 2) },
  { key: "p_value", label: "p-value", align: "right", format: (v) => fixed(v, 3) },
  { key: "inference", label: "Inference" },
];

export const LOCAL_PROJECTION_COLUMNS: ColumnSpec[] = [
  { key: "horizon", label: "Days after shock", align: "right", format: (v) => num(v) },
  { key: "market_group", label: "Market group", format: groupLabel },
  { key: "estimate", label: "Estimated response", align: "right", format: (v) => bps(v) },
  { key: "ci_low", label: "Low (95%)", align: "right", format: (v) => bps(v) },
  { key: "ci_high", label: "High (95%)", align: "right", format: (v) => bps(v) },
  { key: "p_value", label: "p-value", align: "right", format: (v) => fixed(v, 3) },
];

export const COUNTRY_COVERAGE_COLUMNS: ColumnSpec[] = [
  { key: "country", label: "Country" },
  { key: "ticker", label: "ETF" },
  { key: "market_group", label: "Market group", format: groupLabel },
  { key: "first_date", label: "First date" },
  { key: "last_date", label: "Last date" },
  { key: "observation_count", label: "Observations", align: "right", format: (v) => num(v) },
];

export const LARGE_RETURNS_COLUMNS: ColumnSpec[] = [
  { key: "date", label: "Date" },
  { key: "country", label: "Country" },
  { key: "ticker", label: "ETF" },
  { key: "return", label: "Return", align: "right", format: (v) => percent(v) },
  { key: "abs_return", label: "Absolute return", align: "right", format: (v) => percent(v) },
];

export const THRESHOLD_COLUMNS: ColumnSpec[] = [
  { key: "model_name", label: "Model", format: modelName },
  { key: "threshold", label: "Risk cutoff", align: "right", format: (v) => percent(v, 0) },
  { key: "precision", label: "Precision", tooltip: "Of the rows flagged as high risk, the share that actually had a bad outcome.", align: "right", format: (v) => percent(v) },
  { key: "recall", label: "Recall", tooltip: "Of the actual bad outcomes, the share the model caught.", align: "right", format: (v) => percent(v) },
  { key: "f1", label: "F1", align: "right", format: (v) => fixed(v, 3) },
  { key: "share_flagged", label: "Share flagged", align: "right", format: (v) => percent(v) },
  { key: "event_rate_flagged", label: "Event rate (flagged)", align: "right", format: (v) => percent(v) },
  { key: "observation_count", label: "Observations", align: "right", format: (v) => num(v) },
];

export const COUNTRY_RISK_COLUMNS: ColumnSpec[] = [
  { key: "country", label: "Country" },
  { key: "market_group", label: "Market group", format: groupLabel },
  { key: "model_name", label: "Model", format: modelName },
  { key: "average_predicted_probability", label: "Avg. predicted risk", align: "right", format: (v) => percent(v) },
  { key: "realized_event_rate", label: "Realized bad-outcome rate", align: "right", format: (v) => percent(v) },
  { key: "observation_count", label: "Observations", align: "right", format: (v) => num(v) },
];

export const FEATURE_IMPORTANCE_COLUMNS: ColumnSpec[] = [
  { key: "feature", label: "Feature", format: featureLabel },
  { key: "coefficient", label: "Coefficient", align: "right", format: (v) => fixed(v, 3) },
  { key: "abs_coefficient", label: "Importance", align: "right", format: (v) => fixed(v, 3) },
];

export const DRAWDOWN_METRICS_COLUMNS: ColumnSpec[] = [
  { key: "fold", label: "Fold", align: "right", format: (v) => num(v) },
  { key: "model_name", label: "Model", format: modelName },
  { key: "train_start", label: "Train start" },
  { key: "train_end", label: "Train end" },
  { key: "test_start", label: "Test start" },
  { key: "test_end", label: "Test end" },
  { key: "roc_auc", label: "Ranking score", align: "right", format: (v) => fixed(v, 3) },
  { key: "average_precision", label: "Hit rate", align: "right", format: (v) => fixed(v, 3) },
  { key: "brier_score", label: "Probability error", align: "right", format: (v) => fixed(v, 3) },
  { key: "base_rate", label: "Event rate", align: "right", format: (v) => percent(v) },
  { key: "observation_count", label: "Observations", align: "right", format: (v) => num(v) },
];

export const MONTHLY_PROVENANCE_COLUMNS: ColumnSpec[] = [
  { key: "field", label: "Field", format: provenanceLabel },
  { key: "value", label: "Value" },
];

export const MONTHLY_REGRESSION_COLUMNS: ColumnSpec[] = [
  { key: "horizon", label: "Horizon (months)", align: "right", format: (v) => num(v) },
  { key: "term", label: "Term", format: termLabel },
  { key: "estimate", label: "Estimate", align: "right", format: (v) => fixed(v, 4) },
  { key: "std_error", label: "Std. error", align: "right", format: (v) => fixed(v, 4) },
  { key: "t_value", label: "t-value", align: "right", format: (v) => fixed(v, 2) },
  { key: "p_value", label: "p-value", align: "right", format: (v) => fixed(v, 3) },
  { key: "nobs", label: "Observations", align: "right", format: (v) => num(v) },
  { key: "adjusted_r2", label: "Adj. R-squared", align: "right", format: (v) => fixed(v, 3) },
];

export const MONTHLY_FORECAST_COLUMNS: ColumnSpec[] = [
  { key: "model", label: "Model" },
  { key: "rmse", label: "RMSE", align: "right", format: (v) => fixed(v, 4) },
  { key: "mae", label: "MAE", align: "right", format: (v) => fixed(v, 4) },
  { key: "oos_r2", label: "Out-of-sample R-squared", align: "right", format: (v) => fixed(v, 3) },
  { key: "n_forecasts", label: "Forecasts", align: "right", format: (v) => num(v) },
  { key: "first_forecast_date", label: "First forecast" },
  { key: "last_forecast_date", label: "Last forecast" },
];

export const TOP_SHOCKS_COLUMNS: ColumnSpec[] = [
  { key: "date", label: "Date" },
  { key: "gpr", label: "GPR level", align: "right", format: (v) => num(v, "0") },
  { key: "gpr_change", label: "Daily change", align: "right", format: (v) => signedFixed(v, 1) },
  { key: "gpr_act", label: "Actions", align: "right", format: (v) => num(v, "0") },
  { key: "gpr_threat", label: "Threats", align: "right", format: (v) => num(v, "0") },
  { key: "event", label: "Event" },
];

function termLabel(value: unknown): string {
  const raw = str(value);
  if (raw === "gpr_change_z") return "GPR jump (overall)";
  if (raw === "gpr_change_z:emerging_market") return "GPR jump (emerging-market extra)";
  return raw;
}

function groupLabel(value: unknown): string {
  const raw = str(value);
  if (raw === "emerging") return "Emerging markets";
  if (raw === "developed") return "Developed markets";
  return raw;
}

function featureLabel(value: unknown): string {
  const raw = str(value);
  const map: Record<string, string> = {
    gpr_change_z: "GPR jump",
    volatility: "Recent volatility",
    vix: "VIX",
    oil: "Oil",
    dxy: "US dollar",
    rates: "Interest rates",
  };
  return map[raw] ?? raw;
}

function provenanceLabel(value: unknown): string {
  const raw = str(value);
  const map: Record<string, string> = {
    mode: "Mode",
    dataset_mode: "Dataset mode",
    source_count: "Source count",
    row_count: "Row count",
    sample_start: "Sample start",
    sample_end: "Sample end",
    used_placeholder_gdelt: "Used placeholder GDELT",
    used_placeholder_macro: "Used placeholder macro",
  };
  return map[raw] ?? raw;
}
