const assert = require("node:assert/strict");
const test = require("node:test");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const { loadTs } = require("./load-ts.cjs");

const render = (component, props) => renderToStaticMarkup(React.createElement(component, props));

function dashboardHarness(loadBundle, initialState = { status: "loading" }) {
  const state = [initialState, 0];
  let cursor = 0;
  let effects = [];
  const section = (name) => ({ local }) => React.createElement("section", { "data-section": name, "data-local": String(local) }, name);
  const { ResearchDashboard } = loadTs("src/components/ResearchDashboard.tsx", {
    react: {
      useState: () => {
        const index = cursor++;
        return [state[index], (value) => { state[index] = typeof value === "function" ? value(state[index]) : value; }];
      },
      useEffect: (effect) => effects.push(effect),
    },
    "@/lib/data": { loadBundle },
    "@/sections/Overview": { Overview: section("current answer") },
    "@/sections/HowMarketsReact": { HowMarketsReact: section("key evidence") },
    "@/sections/DataAndMethods": { DataAndMethods: section("methods and data") },
    "@/sections/PredictionLab": { PredictionLab: () => React.createElement("section", null, "Prediction metrics") },
  });
  return {
    state,
    view(props) {
      cursor = 0;
      effects = [];
      return ResearchDashboard(props ?? {});
    },
    runEffects: () => effects.map((effect) => effect()),
  };
}

const readyBundle = {
  manifest: { available: true, profile: "local" },
  dataset_status: { prediction_summary: "available", rolling_beta: "deferred", monthly: "available" },
};

test("static HTML contains the research question, limitations, links, and accessible loading state", () => {
  const { default: Page } = loadTs("src/app/page.tsx");
  const html = render(Page);
  assert.match(html, /<h1[^>]*>How are geopolitical risk jumps associated with returns in developed and emerging equity markets\?<\/h1>/);
  assert.match(html, /USD-traded country ETFs are proxies/);
  assert.match(html, /associations, not causal effects/);
  assert.match(html, /does not adjust for dependence/);
  assert.match(html, /not investment advice/);
  assert.match(html, /href="#research-content"/);
  assert.match(html, /id="research-content" tabindex="-1"/);
  assert.match(html, /role="status" aria-live="polite"/);
  assert.match(html, /Loading the research snapshot/);
  assert.match(html, /href="https:\/\/github.com\/N3V3MORE\/gpr-equity-observatory"/);
  assert.match(html, /href="https:\/\/github.com\/N3V3MORE\/gpr-equity-observatory\/blob\/main\/reports\/RESULTS_BRIEF.md"/);
  assert.doesNotMatch(html, /v5 unified|not exported|run Python|scripts\/|Prediction Lab|Monthly benchmark|Countries<|Shock days</i);
});

test("public dashboard requests only core evidence and follows the three-section reading order", async () => {
  const calls = [];
  const harness = dashboardHarness(async (options) => { calls.push(options); return readyBundle; });
  harness.view();
  harness.runEffects();
  await new Promise(setImmediate);
  const html = renderToStaticMarkup(harness.view());
  assert.deepEqual(calls, [{ publicOnly: true }]);
  assert.match(html, /aria-label="Research sections"/);
  assert.match(html, /Current answer/);
  assert.match(html, /Key evidence/);
  assert.match(html, /Methods &amp; data/);
  assert.ok(html.indexOf('data-section="current answer"') < html.indexOf('data-section="key evidence"'));
  assert.ok(html.indexOf('data-section="key evidence"') < html.indexOf('data-section="methods and data"'));
  assert.equal((html.match(/data-local="false"/g) ?? []).length, 3);
  assert.doesNotMatch(html, /Prediction metrics|#prediction-lab|#country-sensitivity|Monthly/);
});

test("local exploration retains optional sections with a local-only loader request", async () => {
  const calls = [];
  const harness = dashboardHarness(async (options) => { calls.push(options); return readyBundle; });
  harness.view({ local: true });
  harness.runEffects();
  await new Promise(setImmediate);
  const html = renderToStaticMarkup(harness.view({ local: true }));
  assert.deepEqual(calls, [{ localOnly: true }]);
  assert.match(html, /Prediction metrics|#prediction-lab/);
  assert.match(html, /#country-sensitivity/);
  assert.equal((html.match(/data-local="true"/g) ?? []).length, 3);
});

test("required failures show a visitor-facing error and allow retry without displaying internal paths", async () => {
  const harness = dashboardHarness(async () => { throw new Error("C:/private/input.csv schema mismatch"); });
  harness.view();
  harness.runEffects();
  await new Promise(setImmediate);
  const view = harness.view();
  const html = renderToStaticMarkup(view);
  assert.match(html, /role="alert"/);
  assert.match(html, /Research snapshot unavailable/);
  assert.match(html, /No findings are shown from an incomplete snapshot/);
  assert.doesNotMatch(html, /private|input.csv|schema mismatch|scripts\/|run Python/);
  const retry = view.props.children.find((child) => child?.type === "button");
  retry.props.onClick();
  assert.deepEqual(harness.state, [{ status: "loading" }, 1]);
});

test("absent data and restricted local exploration have meaningful non-empirical states", () => {
  const absent = dashboardHarness(async () => {}, { status: "ready", bundle: { manifest: { available: false } } });
  const absentHtml = renderToStaticMarkup(absent.view());
  assert.match(absentHtml, /Research findings are not available yet/);
  assert.match(absentHtml, /does not report empirical findings/);
  assert.doesNotMatch(absentHtml, /scripts\/|python|npm|Missing files/);
  const restricted = dashboardHarness(async () => {}, { status: "error" });
  assert.match(renderToStaticMarkup(restricted.view({ local: true })), /Local exploration unavailable/);
});

test("an unmounted dashboard does not apply a late data response", async () => {
  let resolve;
  const harness = dashboardHarness(() => new Promise((finish) => { resolve = finish; }));
  harness.view();
  const cleanups = harness.runEffects();
  cleanups.forEach((cleanup) => cleanup());
  resolve(readyBundle);
  await new Promise(setImmediate);
  assert.equal(harness.state[0].status, "loading");
});

test("local return links, build configuration, and favicon metadata honor root and prefixed deployment", async (t) => {
  const previous = process.env.NEXT_PUBLIC_BASE_PATH;
  t.after(() => previous === undefined ? delete process.env.NEXT_PUBLIC_BASE_PATH : process.env.NEXT_PUBLIC_BASE_PATH = previous);
  for (const prefix of ["", "/gpr-equity-observatory", "/gpr-equity-observatory/"]) {
    process.env.NEXT_PUBLIC_BASE_PATH = prefix;
    const basePath = prefix.replace(/\/$/, "");
    const { default: LocalPage, metadata: localMetadata } = loadTs("src/app/local/page.tsx", {
      "@/components/ResearchDashboard": { ResearchDashboard: () => null },
    });
    const { metadata } = loadTs("src/app/layout.tsx", { "./globals.css": {} });
    const configUrl = require("node:url").pathToFileURL(require("node:path").resolve(__dirname, "../next.config.mjs"));
    const { default: config } = await import(`${configUrl}?basePath=${encodeURIComponent(prefix)}`);
    assert.equal(config.basePath, basePath || undefined);
    assert.ok(render(LocalPage).includes(`href="${basePath}/"`));
    assert.equal(metadata.icons.shortcut, `${basePath}/icon.svg`);
    assert.match(metadata.description, /event-study and panel-regression evidence/);
    assert.equal(localMetadata.robots.index, false);
    assert.equal(metadata.openGraph.url, undefined);
  }
});
