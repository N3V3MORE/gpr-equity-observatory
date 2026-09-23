import type {
  Copy,
  DatasetName,
  DatasetStatus,
  FrontendBundle,
  Manifest,
  Row,
} from "./types";
import { DATASET_NAMES } from "./types";

const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");
const DATA_DIR = "data";
const DATA_BASE = `${BASE_PATH}/${DATA_DIR}`;

type PartialCopy = Partial<Omit<Copy, "monthly_notices" | "prediction_lab">> & {
  monthly_notices?: Partial<Copy["monthly_notices"]>;
  prediction_lab?: Partial<Copy["prediction_lab"]>;
};

export const REQUIRED_DATASETS: readonly DatasetName[] = [
  "copy", "overview", "gpr_timeline", "evidence_map", "event_study",
  "regression", "reader_summaries", "country_coverage",
];
const PREDICTION_DATASETS: readonly DatasetName[] = [
  "prediction_summary", "drawdown_calibration", "drawdown_lift", "drawdown_threshold_metrics",
  "drawdown_country_risk_summary", "drawdown_feature_importance", "drawdown_metrics",
];

async function fetchJson(path: string): Promise<unknown> {
  const res = await fetch(`${DATA_BASE}/${path}`);
  if (!res.ok) {
    throw new Error(`Failed to load ${path}: ${res.status}`);
  }
  try {
    return await res.json();
  } catch {
    throw new Error(`Invalid JSON in ${path}`);
  }
}

function emptyBundle(): FrontendBundle {
  return {
    manifest: { available: false },
    dataset_status: Object.fromEntries(DATASET_NAMES.map((name) => [name, "excluded"])) as Record<DatasetName, DatasetStatus>,
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
    overview: {
      headline: { country_count: 0, start_date: "", end_date: "", shock_count: 0, selected_event_count: 0, represented_event_count: null },
      definitions: { shock_days: "", largest_jumps: "", selected_events: "", event_alignment: "", accumulation: "", inference: "", return_units: "" },
    },
    gpr_timeline: { series: [], top_shocks: [], selected_events: [] },
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
    reader_summaries: { output_files: [], market_reaction: [], regression_translation: [] },
    country_coverage: [],
    large_returns: [],
    monthly: { available: false },
  };
}

function mergeCopyDefaults(copy: PartialCopy | null): Copy {
  const defaults = emptyBundle().copy;
  if (!copy) return defaults;
  return {
    central_question: copy.central_question ?? defaults.central_question,
    intro: copy.intro ?? defaults.intro,
    main_takeaway: copy.main_takeaway ?? defaults.main_takeaway,
    use_note: copy.use_note ?? defaults.use_note,
    job_statements: copy.job_statements ?? defaults.job_statements,
    reader_path: copy.reader_path ?? defaults.reader_path,
    current_answer_points: copy.current_answer_points ?? defaults.current_answer_points,
    does_not_prove_points: copy.does_not_prove_points ?? defaults.does_not_prove_points,
    method_map: copy.method_map ?? defaults.method_map,
    glossary: copy.glossary ?? defaults.glossary,
    prediction_metric_explanations:
      copy.prediction_metric_explanations ?? defaults.prediction_metric_explanations,
    how_to_read: copy.how_to_read ?? defaults.how_to_read,
    beginner_guides: copy.beginner_guides ?? defaults.beginner_guides,
    monthly_notices: { ...defaults.monthly_notices, ...(copy.monthly_notices ?? {}) },
    prediction_lab: { ...defaults.prediction_lab, ...(copy.prediction_lab ?? {}) },
  };
}

function check(condition: unknown, field: string): asserts condition {
  if (!condition) throw new Error(`Invalid snapshot data: ${field}`);
}
function record(value: unknown, field: string): asserts value is Row {
  check(value !== null && typeof value === "object" && !Array.isArray(value), field);
}
const finite = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
const text = (value: unknown): value is string => typeof value === "string" && value.trim().length > 0;
const date = (value: unknown) => typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)
  && Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;

// These checks describe the fields rendered by this page, not a general schema engine.
function rows(value: unknown, field: string, strings: string[], numbers: string[], coordinates: string[] = [], allowEmpty = false): asserts value is Row[] {
  check(Array.isArray(value) && (allowEmpty || value.length > 0), field);
  for (const [index, row] of value.entries()) {
    record(row, `${field}[${index}]`);
    for (const key of strings) check(text(row[key]), `${field}[${index}].${key}`);
    for (const key of numbers) check(row[key] === null || finite(row[key]), `${field}[${index}].${key}`);
    for (const key of coordinates) check(finite(row[key]), `${field}[${index}].${key}`);
  }
}
function observed(value: Row[], key: string, field: string) {
  check(value.some((row) => finite(row[key])), `${field}.${key} has no observations`);
}
function marketGroups(value: Row[], field: string) {
  check(value.every((row) => row.market_group === "developed" || row.market_group === "emerging"), `${field}.market_group`);
}
function strings(value: unknown, field: string) {
  check(Array.isArray(value) && value.length > 0 && value.every(text), field);
}
function stringMap(value: unknown, field: string): asserts value is Record<string, string> {
  record(value, field);
  check(Object.keys(value).length > 0 && Object.values(value).every(text), field);
}

function validateManifest(value: unknown): Manifest {
  record(value, "manifest.json");
  check(typeof value.available === "boolean", "manifest.available");
  const versioned = ["schema_version", "profile", "datasets"].some((key) => key in value);
  if (versioned) {
    check(value.schema_version === 1, "manifest.schema_version (expected 1)");
    check(value.profile === "local" || value.profile === "public", "manifest.profile");
    check(Array.isArray(value.datasets) && value.datasets.every((name) => DATASET_NAMES.includes(name))
      && new Set(value.datasets).size === value.datasets.length, "manifest.datasets");
  }
  if (!value.available) {
    check(value.profile !== "public", "public snapshot is unavailable");
    if (value.missing_files !== undefined) check(Array.isArray(value.missing_files) && value.missing_files.every(text), "manifest.missing_files");
  } else {
    check(date(value.build_date) && date(value.start_date) && date(value.end_date), "manifest dates");
    check(String(value.start_date) <= String(value.end_date), "manifest date range");
    check(Number.isInteger(value.country_count) && Number(value.country_count) > 0, "manifest.country_count");
    check(Number.isInteger(value.shock_count) && Number(value.shock_count) >= 0, "manifest.shock_count");
    if (versioned) check(REQUIRED_DATASETS.every((name) => (value.datasets as unknown[]).includes(name)), "manifest.datasets missing required payload");
  }
  const publication_status = value.profile === "public" && value.publication_status === "approved" ? "approved" : "candidate";
  const approved_downloads = publication_status === "approved" && Array.isArray(value.approved_downloads)
    ? value.approved_downloads.filter((entry: unknown) => {
      if (entry === null || typeof entry !== "object" || Array.isArray(entry)) return false;
      const download = entry as Row;
      return text(download.label) && typeof download.path === "string"
        && /^downloads\/[a-z0-9][a-z0-9._-]*$/i.test(download.path) && !download.path.includes("..");
    }) : [];
  return { ...value, publication_status, approved_downloads, monthly_mode: text(value.monthly_mode) ? value.monthly_mode : null } as unknown as Manifest;
}

function validateCopy(value: unknown) {
  record(value, "copy");
  for (const key of ["central_question", "intro", "main_takeaway", "use_note"]) check(text(value[key]), `copy.${key}`);
  rows(value.job_statements, "copy.job_statements", ["title", "body"], []);
  rows(value.reader_path, "copy.reader_path", ["step", "title", "body"], []);
  rows(value.method_map, "copy.method_map", ["Question", "Tool", "Output", "What to look for"], []);
  strings(value.current_answer_points, "copy.current_answer_points");
  strings(value.does_not_prove_points, "copy.does_not_prove_points");
  stringMap(value.glossary, "copy.glossary");
  record(value.how_to_read, "copy.how_to_read");
  check(text(value.how_to_read.market_response) && text(value.how_to_read.regression), "copy.how_to_read core sections");
}

const REGRESSION_NUMBERS = ["estimate", "std_error", "t_stat", "p_value"];
const EVENT_INFERENCE_NUMBERS = ["std_error", "t_stat", "p_value", "observation_count", "event_count", "accumulation_start_day"];
function eventInference(value: Row[], field: string) {
  for (const row of value) {
    check(Number.isInteger(row.relative_day), `${field}.relative_day`);
    check(row.p_value === null || (Number(row.p_value) >= 0 && Number(row.p_value) <= 1), `${field}.p_value`);
    check(row.std_error === null || Number(row.std_error) >= 0, `${field}.std_error`);
    for (const key of ["observation_count", "event_count"]) {
      check(row[key] === null || (Number.isInteger(row[key]) && Number(row[key]) >= 0), `${field}.${key}`);
    }
    if (finite(row.cumulative_average_abnormal_return)) {
      check(Number.isInteger(row.accumulation_start_day) && Number(row.accumulation_start_day) <= Number(row.relative_day), `${field}.accumulation_start_day`);
    }
  }
}
function validatePayload(name: DatasetName, value: unknown) {
  switch (name) {
    case "copy": validateCopy(value); return;
    case "overview":
      record(value, name); record(value.headline, `${name}.headline`);
      check(Number.isInteger(value.headline.country_count) && Number(value.headline.country_count) > 0, "overview.country_count");
      check(Number.isInteger(value.headline.shock_count) && Number(value.headline.shock_count) >= 0, "overview.shock_count");
      check(date(value.headline.start_date) && date(value.headline.end_date), "overview dates");
      check(Number.isInteger(value.headline.selected_event_count) && Number(value.headline.selected_event_count) >= 0, "overview.selected_event_count");
      check(value.headline.represented_event_count === null || (Number.isInteger(value.headline.represented_event_count) && Number(value.headline.represented_event_count) >= 0), "overview.represented_event_count");
      record(value.definitions, "overview.definitions");
      for (const key of ["shock_days", "largest_jumps", "selected_events", "event_alignment", "accumulation", "inference", "return_units"]) check(text(value.definitions[key]), `overview.definitions.${key}`);
      return;
    case "gpr_timeline":
      record(value, name);
      rows(value.series, `${name}.series`, ["date"], ["gpr"]);
      observed(value.series, "gpr", name);
      rows(value.top_shocks, `${name}.top_shocks`, ["date"], ["gpr", "gpr_change", "gpr_act", "gpr_threat"], [], true);
      rows(value.selected_events, `${name}.selected_events`, ["date"], ["gpr", "gpr_change"], [], true);
      check([...value.series, ...value.top_shocks, ...value.selected_events].every((row) => date(row.date)), `${name}.date`);
      for (const row of [...value.series, ...value.top_shocks]) {
        check(typeof row.gpr_change_shock === "boolean" && typeof row.selected_for_event_study === "boolean", `${name}.event flags`);
      }
      for (const row of value.selected_events) {
        check(row.gpr_change_shock === true, `${name}.selected_events.shock flag`);
        check(row.represented_in_abnormal_study === null || typeof row.represented_in_abnormal_study === "boolean", `${name}.selected_events.represented_in_abnormal_study`);
      }
      return;
    case "evidence_map":
      rows(value, name, ["Method", "Question answered", "Direction", "Estimate", "p-value / metric", "Evidence strength", "Plain-English takeaway"], []); return;
    case "event_study":
      rows(value, name, ["market_group"], ["average_abnormal_return", "cumulative_average_abnormal_return", ...EVENT_INFERENCE_NUMBERS], ["relative_day"]);
      eventInference(value, name);
      marketGroups(value, name);
      for (const group of ["developed", "emerging"]) observed(value.filter((row) => row.market_group === group), "cumulative_average_abnormal_return", `${name}.${group}`); return;
    case "regression":
      record(value, name);
      for (const model of ["baseline", "controlled", "date_fe"]) {
        const table = value[model];
        rows(table, `${name}.${model}`, ["term"], REGRESSION_NUMBERS);
        observed(table, "estimate", `${name}.${model}`);
        check(table.some((row) => row.term === "gpr_change_z:emerging_market"), `${name}.${model}.interaction`);
        if (model !== "date_fe") check(table.some((row) => row.term === "gpr_change_z"), `${name}.${model}.gpr`);
      } return;
    case "reader_summaries":
      record(value, name);
      rows(value.output_files, `${name}.output_files`, ["file", "reader_page", "plain_meaning"], [], ["rows"]);
      rows(value.market_reaction, `${name}.market_reaction`, ["market_group", "direction", "evidence_strength", "plain_note"], ["cumulative_average_abnormal_return", ...EVENT_INFERENCE_NUMBERS], ["relative_day"]);
      eventInference(value.market_reaction, `${name}.market_reaction`);
      rows(value.regression_translation, `${name}.regression_translation`, ["test", "what_it_checks", "direction", "evidence_strength", "plain_note"], ["estimate", "p_value"]); return;
    case "country_coverage":
      rows(value, name, ["country", "ticker", "market_group", "first_date", "last_date"], [], ["observation_count"]);
      marketGroups(value, name);
      check(value.every((row) => date(row.first_date) && date(row.last_date) && String(row.first_date) <= String(row.last_date) && Number(row.observation_count) > 0), name); return;
    case "group_returns": rows(value, name, ["date", "market_group"], ["cumulative_average_return"]); marketGroups(value, name); return;
    case "event_robustness": rows(value, name, ["market_group"], ["cumulative_average_abnormal_return"], ["window", "shock_quantile"]); marketGroups(value, name); return;
    case "panel_sample_robustness": rows(value, name, ["scenario", "term"], [...REGRESSION_NUMBERS, "observation_count"]); return;
    case "quantile_regression":
      rows(value, name, ["term"], ["estimate"], ["quantile"]);
      check(value.every((row) => ["gpr_change_z", "gpr_change_z:emerging_market"].includes(String(row.term))
        && Number(row.quantile) > 0 && Number(row.quantile) < 1), name); return;
    case "local_projections": rows(value, name, ["market_group"], ["estimate", "ci_low", "ci_high"], ["horizon"]); marketGroups(value, name); return;
    case "rolling_beta": rows(value, name, ["date", "country"], ["rolling_gpr_beta"]); return;
    case "large_returns": rows(value, name, ["date", "country", "ticker"], ["return", "abs_return"], [], true); return;
    case "drawdown_calibration": rows(value, name, ["model_name"], ["mean_predicted_probability", "realized_event_rate", "observation_count"], ["probability_decile"]); return;
    case "drawdown_lift": rows(value, name, ["model_name", "bucket"], ["lift", "event_rate", "base_event_rate", "observation_count"]); return;
    case "drawdown_feature_importance": rows(value, name, ["feature"], ["coefficient", "abs_coefficient"]); return;
    case "drawdown_threshold_metrics": rows(value, name, ["model_name"], ["threshold", "precision", "recall", "f1", "share_flagged", "event_rate_flagged", "observation_count"]); return;
    case "drawdown_country_risk_summary": rows(value, name, ["country", "market_group", "model_name"], ["average_predicted_probability", "realized_event_rate", "observation_count"]); return;
    case "drawdown_metrics": rows(value, name, ["model_name", "train_start", "train_end", "test_start", "test_end"], ["roc_auc", "average_precision", "brier_score", "base_rate", "observation_count"], ["fold"]); return;
    case "prediction_summary":
      record(value, name);
      rows(value.model_comparison, `${name}.model_comparison`, ["model_name", "what_it_uses", "model_verdict"], ["mean_roc_auc", "delta_auc_vs_constant_baseline", "mean_average_precision", "delta_ap_vs_constant_baseline", "mean_brier_score", "delta_brier_vs_constant_baseline", "top_decile_lift"]);
      check(finite(value.mean_event_rate), `${name}.mean_event_rate`);
      record(value.best_metrics, `${name}.best_metrics`);
      for (const key of ["auc", "ap", "lift"]) {
        const metric = value.best_metrics[key];
        record(metric, `${name}.best_metrics.${key}`);
        check(text(metric.label) && text(metric.value), `${name}.best_metrics.${key}`);
      } return;
    case "monthly":
      record(value, name); check(typeof value.available === "boolean", `${name}.available`);
      if (!value.available) return;
      check(value.mode === "sample" || value.mode === "real", `${name}.mode`);
      check(text(value.mode_label) && date(value.start_month) && date(value.end_month) && finite(value.source_count), `${name}.metadata`);
      strings(value.source_names, `${name}.source_names`);
      rows(value.provenance, `${name}.provenance`, ["field"], []);
      check(value.provenance.every((row) => typeof row.value === "string"), `${name}.provenance.value`);
      rows(value.month_level, `${name}.month_level`, ["date_month"], ["gpr_change_z", "spread_em_dev"]);
      if (value.regressions != null) rows(value.regressions, `${name}.regressions`, ["term"], ["estimate", "std_error", "t_value", "p_value", "nobs", "adjusted_r2"], ["horizon"], true);
      if (value.forecasts != null) rows(value.forecasts, `${name}.forecasts`, ["model", "first_forecast_date", "last_forecast_date"], ["rmse", "mae", "oos_r2", "n_forecasts"], [], true); return;
  }
}

function includesDataset(manifest: Manifest, name: DatasetName) {
  return manifest.datasets ? manifest.datasets.includes(name) : manifest.profile !== "public";
}

function validateDisplayedCoverage(bundle: FrontendBundle) {
  const { headline } = bundle.overview;
  for (const key of ["country_count", "shock_count", "start_date", "end_date"] as const) {
    check(headline[key] === bundle.manifest[key], `overview.${key} does not match manifest`);
  }
  const { series, top_shocks, selected_events } = bundle.gpr_timeline;
  const inCoverage = (value: unknown) => String(value) >= headline.start_date && String(value) <= headline.end_date;
  const timeline = new Map(series.map((row) => [row.date, row]));
  check(timeline.size === series.length && series.every((row) => inCoverage(row.date)), "timeline sample coverage");
  check(series.filter((row) => row.gpr_change_shock).length === headline.shock_count, "headline flagged shock count");
  check(selected_events.length === headline.selected_event_count, "headline selected event count");
  check(headline.represented_event_count === null
    ? selected_events.every((row) => row.represented_in_abnormal_study === null)
    : selected_events.every((row) => typeof row.represented_in_abnormal_study === "boolean")
      && selected_events.filter((row) => row.represented_in_abnormal_study).length === headline.represented_event_count,
  "headline represented event count");
  check(series.filter((row) => row.selected_for_event_study).length === selected_events.length, "timeline selected event count");
  for (const [name, selectedRows] of [["largest jumps", top_shocks], ["selected events", selected_events]] as const) {
    check(new Set(selectedRows.map((row) => row.date)).size === selectedRows.length, `${name} duplicate dates`);
    for (const row of selectedRows) {
      const source = timeline.get(row.date);
      check(source && source.gpr === row.gpr && source.gpr_change === row.gpr_change && source.gpr_change_shock === row.gpr_change_shock, `${name} must match the displayed timeline`);
      if (name === "selected events") check(source.selected_for_event_study === true, "selected event is not selected in timeline");
      else check(source.selected_for_event_study === row.selected_for_event_study, "largest jumps event selection flag");
    }
  }
  const countries = bundle.country_coverage;
  check(new Set(countries.map((row) => row.country)).size === headline.country_count, "headline country count");
  check(countries.every((row) => inCoverage(row.first_date) && inCoverage(row.last_date))
    && countries.some((row) => row.first_date === headline.start_date)
    && countries.some((row) => row.last_date === headline.end_date), "country sample coverage");
}

// The static release gate uses the same field and coverage checks as the browser.
export function validatePublicSnapshot(payloads: Record<string, unknown>): FrontendBundle {
  const manifest = validateManifest(payloads.manifest);
  check(manifest.available && manifest.profile === "public", "available public snapshot required");
  const bundle = { ...emptyBundle(), manifest };
  for (const name of REQUIRED_DATASETS) {
    validatePayload(name, payloads[name]);
    Object.assign(bundle, { [name]: payloads[name] });
    bundle.dataset_status[name] = "available";
  }
  validateDisplayedCoverage(bundle);
  return bundle;
}

export async function loadBundle({ publicOnly = false, localOnly = false }: { publicOnly?: boolean; localOnly?: boolean } = {}): Promise<FrontendBundle> {
  const manifest = validateManifest(await fetchJson("manifest.json"));
  if (localOnly && manifest.profile === "public") throw new Error("The local research view requires a local snapshot.");
  const bundle = { ...emptyBundle(), manifest };
  if (!manifest.available) return bundle; // Local development's explicit missing-data state.

  await Promise.all(DATASET_NAMES.map(async (name) => {
    if (!includesDataset(manifest, name) || (publicOnly && !REQUIRED_DATASETS.includes(name))) return;
    if (name === "rolling_beta") { bundle.dataset_status[name] = "deferred"; return; }
    try {
      const value = await fetchJson(`${name}.json`);
      validatePayload(name, value);
      Object.assign(bundle, { [name]: value });
      bundle.dataset_status[name] = "available";
    } catch (error) {
      if (REQUIRED_DATASETS.includes(name)) throw new Error(`Required dataset ${name}: ${error instanceof Error ? error.message : "failed to load"}`);
      bundle.dataset_status[name] = "unavailable";
    }
  }));
  validateDisplayedCoverage(bundle);

  // Optional copy is validated separately so it cannot break the core page.
  const rawCopy = bundle.copy;
  const safeCopy: PartialCopy = {
    ...rawCopy,
    how_to_read: Object.fromEntries(Object.entries(rawCopy.how_to_read).filter(([, value]) => text(value))),
    monthly_notices: undefined, prediction_lab: undefined, prediction_metric_explanations: undefined,
  };
  let predictionCopyValid = false;
  try {
    stringMap(rawCopy.prediction_metric_explanations, "copy.prediction_metric_explanations");
    record(rawCopy.prediction_lab, "copy.prediction_lab");
    for (const key of ["conclusion", "validation_heading", "validation_caption", "feature_importance_caption"] as const) check(text(rawCopy.prediction_lab[key]), `copy.prediction_lab.${key}`);
    check(finite(rawCopy.prediction_lab.drawdown_horizon_days) && finite(rawCopy.prediction_lab.drawdown_threshold), "copy.prediction_lab parameters");
    safeCopy.prediction_lab = rawCopy.prediction_lab;
    safeCopy.prediction_metric_explanations = rawCopy.prediction_metric_explanations;
    predictionCopyValid = true;
  } catch { /* The optional Prediction Lab is unavailable below. */ }
  const predictionStates = PREDICTION_DATASETS.map((name) => bundle.dataset_status[name]);
  bundle.dataset_status.prediction_summary = predictionStates.every((state) => state === "excluded") ? "excluded"
    : predictionCopyValid && predictionStates.every((state) => state === "available") ? "available" : "unavailable";
  try {
    record(rawCopy.monthly_notices, "copy.monthly_notices");
    for (const key of ["sample", "real", "cluster", "mode_priority"] as const) check(text(rawCopy.monthly_notices[key]), `copy.monthly_notices.${key}`);
    safeCopy.monthly_notices = rawCopy.monthly_notices;
  } catch {
    if (bundle.dataset_status.monthly !== "excluded") bundle.dataset_status.monthly = "unavailable";
  }
  if (!bundle.monthly.available && bundle.dataset_status.monthly === "available") bundle.dataset_status.monthly = "unavailable";
  bundle.copy = mergeCopyDefaults(safeCopy);
  return bundle;
}

// Kept lazy; the manifest check also prevents direct calls from fetching excluded data.
export async function loadRollingBeta(manifest: Manifest): Promise<Row[] | null> {
  if (!manifest.available || !includesDataset(manifest, "rolling_beta")) return null;
  try {
    const value = await fetchJson("rolling_beta.json");
    validatePayload("rolling_beta", value);
    return value as Row[];
  } catch {
    return null;
  }
}

export type { Row };
