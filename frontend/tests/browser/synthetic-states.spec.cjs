// Controlled SOFTWARE TESTS ONLY. These responses never modify the static artifact.
const { test, expect } = require("@playwright/test");
const { basePath, browserHealth, ready, syntheticSnapshot, interceptSynthetic, downloadTable } = require("./helpers.cjs");

for (const [name, fault] of Object.entries({
  "required 404": { status: 404, body: "Synthetic required-data fault" },
  "malformed JSON": { contentType: "application/json", body: "{broken" },
  "incompatible schema": { contentType: "application/json", body: "{}" },
})) {
  test(`synthetic ${name} fails visibly and supports keyboard retry`, async ({ page }) => {
    const healthy = browserHealth(page, name === "required 404" ? [`${basePath}/data/event_study.json`] : []);
    await interceptSynthetic(page, syntheticSnapshot(), { event_study: fault });
    await page.goto("./");
    await expect(page.getByRole("main").getByRole("alert")).toContainText("Required research data could not be loaded or validated");
    await expect(page.locator("#market-response")).toHaveCount(0);
    await page.unroute(`**${basePath}/data/*.json`);
    await interceptSynthetic(page, syntheticSnapshot());
    await page.getByRole("button", { name: "Try loading again" }).focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("heading", { name: "Key evidence", exact: true })).toBeVisible();
    healthy();
  });
}

test("synthetic loading state preserves the introduction until required data is ready", async ({ page }) => {
  const healthy = browserHealth(page);
  let release;
  const held = new Promise((resolve) => { release = resolve; });
  await interceptSynthetic(page, syntheticSnapshot());
  await page.route(`**${basePath}/data/manifest.json`, async (route) => {
    await held;
    await route.fallback();
  });
  await page.goto("./");
  await expect(page.getByRole("status")).toContainText("Loading the research snapshot");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  release();
  await expect(page.getByRole("heading", { name: "Key evidence", exact: true })).toBeVisible();
  healthy();
});

test("synthetic null observations remain gaps, with genuine zero retained in table and CSV", async ({ page }) => {
  const healthy = browserHealth(page);
  await interceptSynthetic(page, syntheticSnapshot());
  await ready(page);
  const curves = page.locator("#market-response .recharts-line-curve");
  await expect(curves).toHaveCount(2);
  for (const curve of await curves.all()) {
    await expect.poll(async () => ((await curve.getAttribute("d")) || "").match(/M/g)?.length).toBe(2);
  }
  await page.locator("summary").filter({ hasText: "Details: event-study estimates, uncertainty, counts, and windows" }).click();
  const { rows } = await downloadTable(page, "Download event-study estimates and inference (CSV)");
  expect(rows.filter((row) => row[1] === "0").map((row) => row[4])).toEqual(["n/a", "n/a"]);
  expect(rows.filter((row) => row[1] === "1").map((row) => row[4])).toEqual(["0.000 bps", "0.000 bps"]);
  healthy();
});

for (const [name, label] of [["local_projections", "Dynamic response"], ["evidence_map", "Evidence map"]]) {
  test(`synthetic optional ${name} 404 stays local to its section and public view excludes it`, async ({ page }) => {
    const healthy = browserHealth(page, [`${basePath}/data/${name}.json`]);
    const snapshot = syntheticSnapshot([name]);
    snapshot.manifest.profile = "local";
    await interceptSynthetic(page, snapshot, { [name]: { status: 404, body: "Synthetic optional-data fault" } });
    const requests = [];
    page.on("request", (request) => { requests.push(new URL(request.url()).pathname); });
    await ready(page);
    expect(requests).not.toContain(`${basePath}/data/${name}.json`);
    await ready(page, "local/");
    await expect(page.getByRole("status")).toHaveText(`${label} is unavailable in this snapshot.`);
    await expect(page.getByRole("main").getByRole("alert")).toHaveCount(0);
    await expect(page.locator("#market-response .recharts-line-curve")).toHaveCount(2);
    expect(requests).toContain(`${basePath}/data/${name}.json`);
    healthy();
  });
}

test("synthetic local evidence map retains its details and keyboard download", async ({ page }) => {
  const healthy = browserHealth(page);
  const snapshot = syntheticSnapshot(["evidence_map"]);
  snapshot.manifest.profile = "local";
  await interceptSynthetic(page, snapshot);
  await ready(page, "local/");
  const details = page.locator("summary").filter({ hasText: "Details: evidence across all local methods" });
  await details.focus();
  await page.keyboard.press("Enter");
  const { rows, filename } = await downloadTable(page, "Download evidence map (CSV)");
  expect(filename).toBe("evidence_map.csv");
  expect(rows).toHaveLength(2);
  expect(rows[1]).toContain("Test fixture");
  healthy();
});
