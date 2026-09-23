const assert = require("node:assert/strict");
const test = require("node:test");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const { loadTs } = require("./load-ts.cjs");
const { validSnapshot } = require("./snapshot-fixture.cjs");

const render = (component, props) => renderToStaticMarkup(React.createElement(component, props));
const { OptionalDataset } = loadTs("src/components/OptionalDataset.tsx");
const { SectionNav } = loadTs("src/components/SectionNav.tsx");
const { DataAndMethods } = loadTs("src/sections/DataAndMethods.tsx", {
  "@/components/charts": Object.fromEntries(["MonthlyForecastChart", "MonthlyGprChart", "MonthlySpreadChart"]
    .map((name) => [name, () => React.createElement("div", { "data-chart": name })])),
});
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

test("monthly data stays local and uses validated payload fields instead of manifest metadata", () => {
  const bundle = validSnapshot(["monthly"]);
  bundle.manifest.monthly_mode = { malformed: true };
  bundle.copy.monthly_notices = { sample: "Software demonstration, not empirical evidence." };
  bundle.monthly = { available: true, mode: "sample", mode_label: "Sample benchmark" };
  bundle.dataset_status = { monthly: "available", large_returns: "excluded" };
  const html = render(DataAndMethods, { bundle, local: true });
  assert.match(html, /Sample benchmark/);
  assert.match(html, /Software demonstration, not empirical evidence/);
  const publicHtml = render(DataAndMethods, { bundle });
  assert.match(publicHtml, /Data quality and coverage/);
  assert.doesNotMatch(publicHtml, /Sample benchmark|Monthly benchmark|MonthlyGprChart/);
});

test("missing large-return data does not claim zero flags; monthly failure stays local", () => {
  const bundle = validSnapshot();
  bundle.copy.monthly_notices = {};
  bundle.large_returns = [];
  bundle.monthly = { available: false };
  bundle.dataset_status = { large_returns: "unavailable", monthly: "unavailable" };
  const unavailable = render(DataAndMethods, { bundle, local: true });
  assert.match(unavailable, /Large-return flags is unavailable/);
  assert.match(unavailable, /Monthly benchmark is unavailable/);
  assert.match(unavailable, /Download country coverage/);
  assert.doesNotMatch(unavailable, /No large daily returns flagged|Build them with/);

  bundle.dataset_status = { large_returns: "available", monthly: "excluded" };
  const available = render(DataAndMethods, { bundle, local: true });
  assert.match(available, /No large daily returns flagged/);
  assert.doesNotMatch(available, /Monthly benchmark|Large-return flags is unavailable/);
});

test("public methods focus on daily research, retain coverage downloads, and keep details closed", () => {
  const bundle = validSnapshot();
  bundle.copy.method_map = ["Event study", "Panel regression", "Prediction Lab", "Monthly benchmark", "Quantile regression"]
    .map((Tool) => ({ Tool, Question: `Question for ${Tool}`, Output: "Table", "What to look for": "Uncertainty" }));
  bundle.copy.glossary = { GPR: "Geopolitical risk", AUC: "Prediction metric" };
  bundle.dataset_status = { large_returns: "unavailable", monthly: "unavailable" };
  const html = render(DataAndMethods, { bundle });
  for (const label of ["Event study", "Panel regression", "Download country coverage (CSV)", "Data sources", "USD-traded country ETF proxies", "Approved data download not available"]) {
    assert.ok(html.includes(label), label);
  }
  assert.doesNotMatch(html, /Prediction Lab|Monthly benchmark|Quantile regression|Prediction metric|Large-return flags|generated files|Countries checked|<details[^>]* open=/);
  assert.match(html, /href="https:\/\/www.matteoiacoviello.com\/gpr.htm"/);
  assert.match(html, /href="https:\/\/github.com\/N3V3MORE\/gpr-equity-observatory\/blob\/main\/docs\/DATA_SOURCES.md"/);
});

test("approved data links require explicit approval and respect the deployment prefix", (t) => {
  const previous = process.env.NEXT_PUBLIC_BASE_PATH;
  t.after(() => {
    if (previous === undefined) delete process.env.NEXT_PUBLIC_BASE_PATH;
    else process.env.NEXT_PUBLIC_BASE_PATH = previous;
  });
  for (const prefix of ["", "/research/"]) {
    process.env.NEXT_PUBLIC_BASE_PATH = prefix;
    const { DataAndMethods: Methods } = loadTs("src/sections/DataAndMethods.tsx");
    const bundle = validSnapshot();
    bundle.manifest.approved_downloads = [{ label: "Approved summary data (CSV)", path: "downloads/summary.csv" }];
    bundle.dataset_status = {};
    const candidate = render(Methods, { bundle });
    assert.match(candidate, /Approved data download not available/);
    assert.doesNotMatch(candidate, /href="[^"]*downloads\/summary.csv"/);
    bundle.manifest.publication_status = "approved";
    const approved = render(Methods, { bundle });
    assert.ok(approved.includes(`href="${prefix.replace(/\/$/, "")}/downloads/summary.csv" download=""`));
    assert.match(approved, /Approved summary data \(CSV\)/);
    assert.doesNotMatch(approved, /Approved data download not available/);
  }
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
