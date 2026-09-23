const fs = require("node:fs");
const path = require("node:path");
const { expect } = require("@playwright/test");
const { validSnapshot } = require("../snapshot-fixture.cjs");

const artifactRoot = path.resolve(process.env.GPR_ARTIFACT_DIR || path.join(__dirname, "../../out"));
const basePath = (process.env.NEXT_PUBLIC_BASE_PATH || "").replace(/\/$/, "");
const readPayload = (name) => JSON.parse(fs.readFileSync(path.join(artifactRoot, "data", `${name}.json`), "utf8"));

function browserHealth(page, expected404 = []) {
  const failures = [];
  page.on("pageerror", (error) => failures.push(error.message));
  page.on("requestfailed", (request) => failures.push(`${request.url()}: ${request.failure()?.errorText}`));
  page.on("response", (response) => {
    if (response.status() >= 400 && !(response.status() === 404 && expected404.includes(new URL(response.url()).pathname))) {
      failures.push(`${response.status()} ${response.url()}`);
    }
  });
  page.on("console", (message) => {
    if (message.type() !== "error") return;
    const url = message.location().url;
    const expected = url && expected404.includes(new URL(url).pathname) && /server responded with a status of 404/.test(message.text());
    if (!expected) failures.push(`${message.text()} ${url}`);
  });
  return () => expect(failures, "No unexplained HTTP, network, console, or page errors").toEqual([]);
}

async function ready(page, route = "./") {
  await page.goto(route);
  await expect(page.getByRole("navigation", { name: "Research sections" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Key evidence", exact: true })).toBeVisible();
}

async function expectDrawnCurve(curve) {
  await expect(curve).toHaveAttribute("d", /[LC]/);
  // Recharts initially creates a path with a zero-length visible stroke.
  // Wait for the actual curve to finish drawing, not merely for an SVG node.
  await expect.poll(() => curve.evaluate((node) => {
    const dash = node.getAttribute("stroke-dasharray");
    return !dash || parseFloat(dash) >= node.getTotalLength() - 0.01;
  })).toBe(true);
}

function syntheticSnapshot(extra = []) {
  const snapshot = validSnapshot(extra);
  snapshot.manifest.data_kind = "synthetic";
  snapshot.manifest.snapshot_id = "synthetic-browser-fault-cases";
  snapshot.copy.current_answer_points = ["SYNTHETIC SOFTWARE TEST: not research evidence or publication data."];
  snapshot.gpr_timeline.series.forEach((row, index) => { row.gpr = [10, 15, 20][index]; });
  snapshot.event_study = ["developed", "emerging"].flatMap((market_group) => [-2, -1, 0, 1, 2].map((relative_day, index) => ({
    ...snapshot.event_study[0], market_group, relative_day, accumulation_start_day: -2,
    average_abnormal_return: [0.01, 0.02, null, 0, 0.03][index],
    cumulative_average_abnormal_return: [0.01, 0.02, null, 0, 0.03][index],
  })));
  return snapshot;
}

async function interceptSynthetic(page, snapshot, faults = {}) {
  await page.route(`**${basePath}/data/*.json`, async (route) => {
    const name = path.basename(new URL(route.request().url()).pathname, ".json");
    if (faults[name]) { await route.fulfill(faults[name]); return; }
    if (!(name in snapshot)) { await route.fulfill({ status: 404, body: "Synthetic optional-data fault" }); return; }
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(snapshot[name]) });
  });
}

// Read real CSV quoting, including embedded commas/newlines in explanatory text.
function parseCsv(text) {
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let index = 0; index < text.length; index++) {
    const character = text[index];
    if (character === '"') {
      if (quoted && text[index + 1] === '"') { cell += '"'; index++; }
      else quoted = !quoted;
    } else if (!quoted && (character === "," || character === "\n")) {
      row.push(cell.replace(/\r$/, "")); cell = "";
      if (character === "\n") { rows.push(row); row = []; }
    } else cell += character;
  }
  if (cell || row.length) { row.push(cell.replace(/\r$/, "")); rows.push(row); }
  return rows;
}

async function downloadTable(page, label) {
  const control = page.getByRole("button", { name: label, exact: true });
  const table = control.locator("../..").locator("table");
  const expectedRows = await table.locator("tr").evaluateAll((rows) => rows.map((row) => [...row.children].map((cell) => {
    const clone = cell.cloneNode(true);
    clone.querySelectorAll("[aria-label]").forEach((node) => node.remove());
    return clone.textContent.trim();
  })));
  await control.focus();
  await expect(control).toBeFocused();
  const downloaded = page.waitForEvent("download");
  await page.keyboard.press("Enter");
  const download = await downloaded;
  const text = fs.readFileSync(await download.path(), "utf8");
  expect(parseCsv(text)).toEqual(expectedRows);
  return { text, rows: parseCsv(text), filename: download.suggestedFilename() };
}

module.exports = { artifactRoot, basePath, readPayload, browserHealth, ready, expectDrawnCurve, syntheticSnapshot, interceptSynthetic, parseCsv, downloadTable };
