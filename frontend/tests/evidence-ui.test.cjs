const assert = require("node:assert/strict");
const test = require("node:test");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const { loadTs } = require("./load-ts.cjs");
const { validSnapshot } = require("./snapshot-fixture.cjs");
const { DATASET_NAMES } = loadTs("src/lib/types.ts");

const mocks = {
  "@/components/charts": Object.fromEntries([
    "EventRobustnessChart", "EventStudyChart", "LocalProjectionChart", "QuantileChart", "GprTimelineChart", "CumulativeReturnsChart",
  ].map((name) => [name, () => React.createElement("div", { "data-chart": name })])),
  "@/components/LazyRollingBeta": { LazyRollingBeta: () => null },
};
const { HowMarketsReact } = loadTs("src/sections/HowMarketsReact.tsx", mocks);
const { Overview } = loadTs("src/sections/Overview.tsx", mocks);
const render = (component, bundle) => renderToStaticMarkup(React.createElement(component, { bundle }));

function evidenceBundle() {
  const bundle = validSnapshot();
  bundle.dataset_status = Object.fromEntries(DATASET_NAMES.map((name) => [name, bundle.manifest.datasets.includes(name) ? "available" : "excluded"]));
  bundle.overview.headline = { ...bundle.overview.headline, shock_count: 3, selected_event_count: 2, represented_event_count: null };
  bundle.overview.definitions = {
    shock_days: "3 flagged GPR-change dates inside 2024-01-01 to 2024-01-03.",
    largest_jumps: "Red dots show the largest GPR jumps within the panel coverage, not the selected event set.",
    selected_events: "Peak events are selected by Python across the GPR history, then clipped to panel coverage.",
    event_alignment: "Day 0 is each ETF's first trading observation on or after the selected GPR date.",
    accumulation: "Each ETF-event accumulates from its first available relative day, including negative relative days; no reset at day 0.",
    inference: "Existing standard errors and p-values are not adjusted for dependence between ETFs exposed to common events.",
    return_units: "Returns are decimal log returns from USD ETF proxies; the table converts them to basis points.",
  };
  bundle.event_study = [{
    market_group: "developed", relative_day: 1, accumulation_start_day: -5,
    average_abnormal_return: 0.0001, cumulative_average_abnormal_return: -0.0012,
    std_error: 0.0005, t_stat: -2.4, p_value: 0.04, observation_count: 123, event_count: 19,
  }];
  bundle.gpr_timeline.top_shocks = [{ date: "2024-01-02", gpr: 12, gpr_change: 5, gpr_change_shock: true, selected_for_event_study: false }];
  bundle.gpr_timeline.selected_events = [{ date: "2024-01-03", gpr: 13, gpr_change: 6, gpr_change_shock: true, represented_in_abnormal_study: null }];
  return bundle;
}

test("event-study UI displays inference and window definitions with accessible detail and CSV controls", () => {
  const html = render(HowMarketsReact, evidenceBundle());
  assert.match(html, /<summary[^>]*>Details: event-study estimates, uncertainty, counts, and windows<\/summary>/);
  assert.match(html, /Average cumulative abnormal returns around selected GPR events/);
  for (const label of [
    "Endpoint (relative trading day)", "Earliest series day", "Cumulative std. error (bps)",
    "Cumulative t-statistic", "Cumulative p-value (unadjusted)", "ETF-event observations", "Represented event dates",
    "Download event-study definitions (CSV)", "Download event-study estimates and inference (CSV)",
  ]) assert.ok(html.includes(label), label);
  for (const value of ["-12.000 bps", "5.000 bps", "-2.4000", "0.0400", ">123<", ">19<"]) assert.ok(html.includes(value), value);
  assert.match(html, /not adjusted for dependence between ETFs exposed to common events/);
  assert.match(html, /including negative relative days; no reset at day 0/);
  assert.match(html, /No confidence bands are shown/);
  assert.match(html, /Weak evidence is not proof of no effect/);
  assert.match(html, /USD-traded country ETF proxies/);
  assert.doesNotMatch(html, /Bands and p-values live|In the current data, this is not strong|post-shock window/);
});

test("overview distinguishes coverage, flagged counts, largest jumps, selection, and unavailable representation", () => {
  const html = render(Overview, evidenceBundle());
  assert.match(html, /Flagged GPR shock days/);
  assert.match(html, /3 flagged GPR-change dates inside 2024-01-01 to 2024-01-03/);
  assert.match(html, /Largest GPR jumps within panel coverage/);
  assert.match(html, /Selected event dates within panel coverage: <strong>2<\/strong>/);
  assert.match(html, /recorded abnormal-return windows within that coverage: <strong>unavailable<\/strong>/);
  assert.match(html, /Download selected event dates \(CSV\)/);
  assert.match(html, /2024-01-02/);
  assert.match(html, /2024-01-03/);
  assert.match(html, /What this snapshot supports/);
  assert.doesNotMatch(html, /Largest GPR shock days|which anchor the rest of the analysis/);
});
