const assert = require("node:assert/strict");
const test = require("node:test");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const { loadTs } = require("./load-ts.cjs");

const render = (component, props) => renderToStaticMarkup(React.createElement(component, props));
const { OptionalDataset } = loadTs("src/components/OptionalDataset.tsx");
const { SectionNav } = loadTs("src/components/SectionNav.tsx");
const { DataAndMethods } = loadTs("src/sections/DataAndMethods.tsx");
const { PredictionLab } = loadTs("src/sections/PredictionLab.tsx");

test("optional content distinguishes excluded, unavailable, and available", () => {
  const props = { label: "Optional evidence", children: "Published chart" };
  assert.equal(render(OptionalDataset, { ...props, status: "excluded" }), "");
  const unavailable = render(OptionalDataset, { ...props, status: "unavailable" });
  assert.match(unavailable, /Optional evidence is unavailable/);
  assert.doesNotMatch(unavailable, /Published chart/);
  assert.equal(render(OptionalDataset, { ...props, status: "available" }), "Published chart");
});

test("excluded optional sections have no navigation anchors", () => {
  const html = render(SectionNav, { prediction: false, rolling: false });
  assert.match(html, /#overview/);
  assert.match(html, /#data-and-methods/);
  assert.doesNotMatch(html, /#prediction-lab|#country-sensitivity/);
});

test("page uses validated monthly data instead of optional manifest metadata", () => {
  const bundle = {
    manifest: { available: true, monthly_mode: { malformed: true } },
    copy: { intro: "Research overview", use_note: "Research only" },
    overview: { headline: { country_count: 1, shock_count: 0, start_date: "2020-01-01", end_date: "2020-01-02" } },
    monthly: { mode: "sample", mode_label: "Sample benchmark" },
    dataset_status: { monthly: "available", prediction_summary: "excluded", rolling_beta: "excluded" },
  };
  const { default: Page } = loadTs("src/app/page.tsx", {
    react: { useEffect: () => {}, useState: () => [{ status: "ready", bundle }] },
    "@/sections/Overview": { Overview: () => "Core overview" },
    "@/sections/HowMarketsReact": { HowMarketsReact: () => "Core evidence" },
    "@/sections/PredictionLab": { PredictionLab: () => null },
    "@/sections/DataAndMethods": { DataAndMethods: () => "Data and methods" },
  });
  const html = render(Page);
  assert.match(html, /Sample benchmark/);
  assert.match(html, /Core evidence/);
});

test("missing large-return data does not claim zero flags; monthly failure stays local", () => {
  const bundle = {
    copy: { monthly_notices: {}, glossary: { GPR: "Geopolitical risk" } },
    country_coverage: [{ country: "A" }],
    large_returns: [],
    reader_summaries: { output_files: [] },
    monthly: { available: false },
    dataset_status: { large_returns: "unavailable", monthly: "unavailable" },
  };
  const unavailable = render(DataAndMethods, { bundle });
  assert.match(unavailable, /Large-return flags is unavailable/);
  assert.match(unavailable, /Monthly benchmark is unavailable/);
  assert.match(unavailable, /Countries checked/);
  assert.doesNotMatch(unavailable, /No large daily returns flagged|Build them with/);

  bundle.dataset_status = { large_returns: "available", monthly: "excluded" };
  const available = render(DataAndMethods, { bundle });
  assert.match(available, /No large daily returns flagged/);
  assert.doesNotMatch(available, /Monthly benchmark|Large-return flags is unavailable/);
});

test("unavailable Prediction Lab shows a notice without metrics or empty charts", () => {
  const html = render(PredictionLab, { bundle: {
    copy: { prediction_lab: {}, prediction_metric_explanations: {} },
    dataset_status: { prediction_summary: "unavailable" },
    prediction_summary: { best_metrics: {}, model_comparison: [], mean_event_rate: null },
  } });
  assert.match(html, /Prediction Lab is unavailable/);
  assert.doesNotMatch(html, /Average bad-outcome rate|Bad-outcome lift by risk bucket|No rows to show/);
});

test("lazy sensitivity handles rejected and missing data without fetching excluded data", async () => {
  for (const status of ["excluded", "unavailable", "deferred"]) {
    for (const rejects of [false, true]) {
      let calls = 0;
      let cursor = 0;
      const state = [true, null, false]; // Section has entered the viewport.
      const effects = [];
      const { LazyRollingBeta } = loadTs("src/components/LazyRollingBeta.tsx", {
        react: {
          useRef: () => ({ current: {} }),
          useState: () => {
            const index = cursor++;
            return [state[index], (value) => { state[index] = value; }];
          },
          useEffect: (effect) => effects.push(effect),
        },
        "@/lib/data": { loadRollingBeta: async () => {
          calls++;
          if (rejects) throw new Error("Optional request failed");
          return null;
        } },
        "@/components/charts": { RollingBetaChart: () => "Unexpected chart" },
      });
      LazyRollingBeta({ status, manifest: { available: true } });
      effects.forEach((effect) => effect());
      await new Promise(setImmediate);
      cursor = 0;
      const output = LazyRollingBeta({ status, manifest: { available: true } });
      if (status === "excluded") assert.equal(output, null);
      else assert.match(renderToStaticMarkup(output), /Country sensitivity is unavailable/);
      assert.equal(calls, status === "deferred" ? 1 : 0);
    }
  }
});
