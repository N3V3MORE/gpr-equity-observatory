const assert = require("node:assert/strict");
const test = require("node:test");
const { loadTs } = require("./load-ts.cjs");
const charts = loadTs("src/components/charts.tsx", {
  react: { useMemo: (factory) => factory() },
  recharts: Object.fromEntries([
    "Bar", "BarChart", "CartesianGrid", "ComposedChart", "Legend", "Line", "LineChart",
    "ReferenceLine", "ResponsiveContainer", "Scatter", "Tooltip", "XAxis", "YAxis",
  ].map((name) => [name, name])),
});

function chart(name, props) {
  const element = charts[name](props).props.children;
  const lines = [element.props.children].flat(Infinity).filter((child) => child?.type === "Line");
  for (const line of lines) assert.equal(line.props.connectNulls, false, `${name} must preserve missing data gaps`);
  return element.props.data;
}

test("timeline and simple monthly charts keep missing observations null", () => {
  const values = [0, null, undefined, "", " \t ", "invalid", NaN, Infinity, "0", 1];
  const expected = values.map((value, index) => index === 0 || index === 8 ? 0 : index === 9 ? 1 : null);
  const series = values.map((gpr, date) => ({ date: String(date), gpr }));
  const timeline = chart("GprTimelineChart", { series, topShocks: series });
  assert.deepEqual(timeline.map((row) => row.gpr), expected);
  assert.deepEqual(timeline.map((row) => row.shock), expected);
  for (const [name, source, output] of [
    ["MonthlyGprChart", "gpr_change_z", "value"],
    ["MonthlySpreadChart", "spread_em_dev", "value"],
    ["MonthlyForecastChart", "oos_r2", "oos_r2"],
  ]) {
    const rows = values.map((value, index) => ({ date_month: String(index), model: String(index), [source]: value }));
    assert.deepEqual(chart(name, { rows }).map((row) => row[output]), expected);
  }
});

test("grouped charts preserve explicit and absent observations without zero bars", () => {
  for (const [name, dimension, observation, groupKey, group] of [
    ["CumulativeReturnsChart", "date", "cumulative_average_return", "market_group", "developed"],
    ["EventStudyChart", "relative_day", "cumulative_average_abnormal_return", "market_group", "developed"],
    ["QuantileChart", "quantile", "estimate", "term", "gpr_change_z"],
    ["CalibrationChart", "probability_decile", "realized_event_rate", "model_name", "full_features"],
    ["LiftChart", "bucket", "lift", "model_name", "full_features"],
  ]) {
    const rows = [
      { [dimension]: 0, [observation]: 0, [groupKey]: group },
      { [dimension]: 1, [observation]: " ", [groupKey]: group },
      { [dimension]: 2, [observation]: 1, [groupKey]: "other" },
      { [dimension]: 3, [observation]: 2, [groupKey]: group },
    ];
    const data = chart(name, { rows });
    assert.deepEqual(data.map((row) => row[group]), [0, null, null, 2], name);
    assert.deepEqual(data.map((row) => row.other), [null, null, 1, null], name);
  }
  const robustness = chart("EventRobustnessChart", { rows: [
    { window: 1, shock_quantile: 0.95, market_group: "developed", cumulative_average_abnormal_return: 0 },
    { window: 1, shock_quantile: 0.95, market_group: "emerging", cumulative_average_abnormal_return: null },
    { window: 2, shock_quantile: 0.95, market_group: "developed", cumulative_average_abnormal_return: 1 },
  ] });
  assert.deepEqual(robustness.map((row) => row.developed), [0, 1]);
  assert.deepEqual(robustness.map((row) => row.emerging), [null, null]);
});

test("invalid numeric coordinates do not become an observation at zero", () => {
  for (const [name, key] of [
    ["EventStudyChart", "relative_day"], ["QuantileChart", "quantile"],
    ["LocalProjectionChart", "horizon"], ["CalibrationChart", "probability_decile"],
  ]) {
    const rows = [null, undefined, "", " ", "invalid"].map((value) => ({
      [key]: value, market_group: "developed", term: "gpr_change_z", model_name: "full_features",
      cumulative_average_abnormal_return: 2, estimate: 2, realized_event_rate: 2,
    }));
    assert.deepEqual(chart(name, { rows }), [], name);
  }
});

test("local projection estimates and each missing confidence bound remain null", () => {
  const data = chart("LocalProjectionChart", { rows: [
    { horizon: 0, market_group: "developed", estimate: 0, ci_low: 0, ci_high: 0 },
    { horizon: 1, market_group: "developed", estimate: null, ci_low: " ", ci_high: "invalid" },
    { horizon: 2, market_group: "emerging", estimate: 1, ci_low: -1 },
  ] });
  assert.deepEqual(data.map((row) => [row.developed_est, row.developed_low, row.developed_high]), [
    [0, 0, 0], [null, null, null], [null, null, null],
  ]);
  assert.deepEqual(data.map((row) => [row.emerging_est, row.emerging_low, row.emerging_high]), [
    [null, null, null], [null, null, null], [1, -1, null],
  ]);
});

test("rolling beta retains country gaps and real zero", () => {
  const data = chart("RollingBetaChart", { rows: [
    { date: "2020-01-01", country: "A", rolling_gpr_beta: 0 },
    { date: "2020-01-02", country: "A", rolling_gpr_beta: null },
    { date: "2020-01-03", country: "B", rolling_gpr_beta: 1 },
    { date: "2020-01-04", country: "A", rolling_gpr_beta: 2 },
  ] });
  assert.deepEqual(data.map((row) => row.A), [0, null, null, 2]);
  assert.deepEqual(data.map((row) => row.B), [null, null, 1, null]);
});

test("feature importance omits missing bars while keeping genuine zero", () => {
  const data = chart("FeatureImportanceChart", { rows: [
    { feature: "missing", abs_coefficient: " " },
    { feature: "zero", abs_coefficient: 0 },
    { feature: "positive", abs_coefficient: 2 },
  ] });
  assert.deepEqual(data, [
    { feature: "zero", importance: 0 },
    { feature: "positive", importance: 2 },
    { feature: "missing", importance: null },
  ]);
});
