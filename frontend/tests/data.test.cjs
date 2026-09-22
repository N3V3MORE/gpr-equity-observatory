const assert = require("node:assert/strict");
const test = require("node:test");
const { loadTs } = require("./load-ts.cjs");
const { CORE, validSnapshot } = require("./snapshot-fixture.cjs");

function runtime(t, payloads, overrides = {}, basePath = "") {
  const oldFetch = global.fetch;
  const oldBasePath = process.env.NEXT_PUBLIC_BASE_PATH;
  process.env.NEXT_PUBLIC_BASE_PATH = basePath;
  const requests = [];
  global.fetch = async (url) => {
    requests.push(url);
    const name = url.split("/").at(-1).replace(/\.json$/, "");
    if (Object.hasOwn(overrides, name)) {
      const response = overrides[name];
      if (response instanceof Error) throw response;
      return new Response(response.body ?? "", { status: response.status ?? 200 });
    }
    return Object.hasOwn(payloads, name)
      ? new Response(JSON.stringify(payloads[name])) : new Response("missing", { status: 404 });
  };
  t.after(() => {
    global.fetch = oldFetch;
    if (oldBasePath === undefined) delete process.env.NEXT_PUBLIC_BASE_PATH;
    else process.env.NEXT_PUBLIC_BASE_PATH = oldBasePath;
  });
  return { ...loadTs("src/lib/data.ts"), requests };
}

test("valid public core preserves zero and null and never fetches excluded optional datasets", async (t) => {
  const api = runtime(t, validSnapshot(), {}, "/observatory/");
  const bundle = await api.loadBundle();
  assert.deepEqual(bundle.gpr_timeline.series.map((row) => row.gpr), [0, null, 1]);
  assert.equal(bundle.regression.controlled[0].estimate, 0);
  assert.equal(bundle.regression.controlled[0].p_value, null);
  assert.deepEqual(new Set(api.requests), new Set(["manifest", ...CORE].map((name) => `/observatory/data/${name}.json`)));
  assert.equal(bundle.dataset_status.monthly, "excluded");
  assert.equal(bundle.dataset_status.prediction_summary, "excluded");
  assert.equal(await api.loadRollingBeta(bundle.manifest), null);
  assert.equal(api.requests.length, CORE.length + 1);
});

for (const name of ["manifest", ...CORE]) {
  test(`required ${name} 404 produces a loading error`, async (t) => {
    const api = runtime(t, validSnapshot(), { [name]: { status: 404 } });
    await assert.rejects(api.loadBundle(), new RegExp(`${name}.*404`));
  });
  test(`malformed JSON in required ${name} is rejected`, async (t) => {
    const api = runtime(t, validSnapshot(), { [name]: { body: "{broken" } });
    await assert.rejects(api.loadBundle(), /Invalid JSON/);
  });
}

const malformed = {
  copy: (p) => { p.copy.job_statements = [null]; },
  overview: (p) => { p.overview.headline = {}; },
  gpr_timeline: (p) => { p.gpr_timeline.series = [{ date: "2024-01-01" }]; },
  evidence_map: (p) => { p.evidence_map = [{}]; },
  event_study: (p) => { p.event_study[0].relative_day = " "; },
  regression: (p) => { p.regression.controlled = []; },
  reader_summaries: (p) => { p.reader_summaries.regression_translation = {}; },
  country_coverage: (p) => { p.country_coverage = [{ country: "Test" }]; },
};
for (const [name, mutate] of Object.entries(malformed)) {
  test(`a valid manifest cannot hide incompatible required ${name}`, async (t) => {
    const payloads = validSnapshot(); mutate(payloads);
    await assert.rejects(runtime(t, payloads).loadBundle(), new RegExp(`Required dataset ${name}`));
  });
}

test("required event data only needs the fields used by the public page", async (t) => {
  const payloads = validSnapshot();
  payloads.event_study.forEach((row) => { delete row.cumulative_average_return; });
  const bundle = await runtime(t, payloads).loadBundle();
  assert.equal(bundle.dataset_status.event_study, "available");
});

test("empty or entirely null core evidence cannot become a ready dashboard", async (t) => {
  const payloads = validSnapshot(); payloads.gpr_timeline.series.forEach((row) => { row.gpr = null; });
  await assert.rejects(runtime(t, payloads).loadBundle(), /no observations/);
});

for (const mutate of [
  (m) => { m.schema_version = 2; },
  (m) => { delete m.schema_version; },
  (m) => { m.profile = "unknown"; },
  (m) => { m.datasets = m.datasets.filter((name) => name !== "event_study"); },
  (m) => { m.datasets.push("../private"); },
  (m) => { m.available = "true"; },
  (m) => { m.available = false; },
]) {
  test("incompatible public manifest is rejected before payload loading", async (t) => {
    const payloads = validSnapshot(); mutate(payloads.manifest);
    const api = runtime(t, payloads);
    await assert.rejects(api.loadBundle(), /Invalid snapshot data/);
    assert.equal(api.requests.length, 1);
  });
}

test("manifest and overview coverage must agree", async (t) => {
  const payloads = validSnapshot(); payloads.manifest.country_count = 2;
  await assert.rejects(runtime(t, payloads).loadBundle(), /does not match manifest/);
});

for (const response of [{ status: 404 }, { body: "{broken" }, { body: "{}" }, new Error("offline")]) {
  test("an optional failure stays local to its section", async (t) => {
    const payloads = validSnapshot(["local_projections", "monthly"]);
    const api = runtime(t, payloads, { local_projections: response, monthly: response });
    const bundle = await api.loadBundle();
    assert.equal(bundle.dataset_status.event_study, "available");
    assert.equal(bundle.dataset_status.local_projections, "unavailable");
    assert.equal(bundle.dataset_status.monthly, "unavailable");
    assert.equal(bundle.manifest.available, true);
  });
}

test("valid optional data preserves missing bounds and zero", async (t) => {
  const payloads = validSnapshot(["local_projections", "large_returns"]);
  payloads.local_projections = [{ market_group: "developed", horizon: 0, estimate: 0, ci_low: null, ci_high: null }];
  payloads.large_returns = [];
  const bundle = await runtime(t, payloads).loadBundle();
  assert.deepEqual(bundle.local_projections, payloads.local_projections);
  assert.equal(bundle.dataset_status.large_returns, "available");
});

test("rolling data stays lazy, uses the base path, and isolates invalid rows", async (t) => {
  const payloads = validSnapshot(["rolling_beta"]);
  payloads.rolling_beta = [{ date: "2024-01-01", country: "Test", rolling_gpr_beta: 0 }, { date: "2024-01-02", country: "Test", rolling_gpr_beta: null }];
  const api = runtime(t, payloads, {}, "/observatory");
  const bundle = await api.loadBundle();
  assert.equal(bundle.dataset_status.rolling_beta, "deferred");
  assert.ok(!api.requests.some((url) => url.includes("rolling_beta")));
  assert.deepEqual(await api.loadRollingBeta(bundle.manifest), payloads.rolling_beta);
  assert.equal(api.requests.at(-1), "/observatory/data/rolling_beta.json");
  payloads.rolling_beta[0].rolling_gpr_beta = "invalid";
  assert.equal(await api.loadRollingBeta(bundle.manifest), null);
  delete payloads.rolling_beta;
  assert.equal(await api.loadRollingBeta(bundle.manifest), null);
});

test("legacy local exports still validate their required payloads", async (t) => {
  const payloads = validSnapshot();
  for (const key of ["schema_version", "profile", "datasets"]) delete payloads.manifest[key];
  const api = runtime(t, payloads);
  assert.equal((await api.loadBundle()).dataset_status.overview, "available");
  delete payloads.event_study;
  await assert.rejects(api.loadBundle(), /event_study.*404/);
});

test("explicit unavailable local manifest keeps the development empty state", async (t) => {
  const api = runtime(t, { manifest: { available: false, schema_version: 1, profile: "local", datasets: ["copy"], missing_files: ["panel.csv"] } });
  assert.equal((await api.loadBundle()).manifest.available, false);
  assert.deepEqual(api.requests, ["/data/manifest.json"]);
});

test("malformed excluded optional copy and monthly metadata cannot break core data", async (t) => {
  const payloads = validSnapshot();
  payloads.copy.how_to_read.downside_risk = { invalid: true };
  payloads.copy.prediction_lab = [];
  payloads.copy.monthly_notices = 42;
  payloads.manifest.monthly_mode = { invalid: true };
  const bundle = await runtime(t, payloads).loadBundle();
  assert.equal(bundle.dataset_status.event_study, "available");
  assert.equal(bundle.dataset_status.prediction_summary, "excluded");
  assert.equal(bundle.copy.how_to_read.downside_risk, undefined);
  assert.equal(bundle.manifest.monthly_mode, null);
});

test("unsupported terms and market groups are unavailable rather than mislabeled", async (t) => {
  const payloads = validSnapshot(["quantile_regression", "local_projections"]);
  payloads.quantile_regression = [{ term: "Intercept", quantile: 0.1, estimate: 100 }];
  payloads.local_projections = [{ market_group: "unknown", horizon: 0, estimate: 0, ci_low: null, ci_high: null }];
  const bundle = await runtime(t, payloads).loadBundle();
  assert.equal(bundle.dataset_status.quantile_regression, "unavailable");
  assert.equal(bundle.dataset_status.local_projections, "unavailable");
  payloads.event_study.push({ market_group: "unknown", relative_day: 0, cumulative_average_abnormal_return: 1, cumulative_average_return: 1 });
  await assert.rejects(runtime(t, payloads).loadBundle(), /event_study.market_group/);
});

test("a partial Prediction Lab cannot look available", async (t) => {
  const payloads = validSnapshot(["prediction_summary"]);
  payloads.prediction_summary = { model_comparison: [{}], best_metrics: {}, mean_event_rate: 0 };
  const bundle = await runtime(t, payloads).loadBundle();
  assert.equal(bundle.dataset_status.prediction_summary, "unavailable");
  assert.equal(bundle.dataset_status.overview, "available");
});
