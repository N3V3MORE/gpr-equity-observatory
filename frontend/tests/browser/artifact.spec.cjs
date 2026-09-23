// Baseline checks use the staged artifact verbatim. No network interception here.
const { test, expect } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");
const { CORE } = require("../snapshot-fixture.cjs");
const { artifactRoot, basePath, readPayload, browserHealth, ready, expectDrawnCurve, parseCsv, downloadTable } = require("./helpers.cjs");

test("static artifact contains the research question and limitations before JavaScript", async ({ browser, request }, testInfo) => {
  const response = await request.get("./");
  expect(response.ok()).toBeTruthy();
  expect(await response.text()).toContain("USD-traded country ETFs are proxies for equity markets");
  const context = await browser.newContext({ javaScriptEnabled: false, baseURL: response.url(), viewport: testInfo.project.use.viewport });
  const page = await context.newPage();
  await page.goto("./");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("geopolitical risk jumps associated with returns");
  await expect(page.getByText(/Estimates describe associations, not causal effects/)).toBeVisible();
  await expect(page.getByRole("link", { name: "Research code", exact: true })).toHaveAttribute("href", /^https:\/\/github.com\//);
  await context.close();
});

test("artifact renders core charts, keyboard controls, data and prefix-safe assets", async ({ page, request }) => {
  const healthy = browserHealth(page);
  const dataRequests = [];
  page.on("request", (request) => { if (new URL(request.url()).pathname.includes("/data/")) dataRequests.push(new URL(request.url()).pathname); });
  await ready(page);
  await expect(page).toHaveTitle("GPR Equity Observatory");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to research findings" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#research-content")).toBeFocused();
  const navigation = page.getByRole("navigation", { name: "Research sections" });
  await page.keyboard.press("Tab");
  await expect(navigation.getByRole("link", { name: "Current answer" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(navigation.getByRole("link", { name: "Key evidence" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/#how-markets-react$/);
  const manifest = readPayload("manifest");
  if (process.env.GPR_BROWSER_PUBLICATION === "1") {
    expect(manifest.profile).toBe("public");
    expect(manifest.publication_status).toBe("approved");
    expect(manifest.data_kind).toBe("real");
    expect(manifest.approved_downloads.length).toBeGreaterThan(0);
    await expect(page.getByRole("heading", { name: "What this snapshot supports" })).toBeVisible();
  } else if (manifest.data_kind === "synthetic") {
    await expect(page.getByText(/SYNTHETIC/).first()).toBeAttached();
  }
  await expectDrawnCurve(page.locator("#overview .recharts-line-curve").first());
  const curves = page.locator("#market-response .recharts-line-curve");
  await expect(curves).toHaveCount(2);
  for (const curve of await curves.all()) await expectDrawnCurve(curve);
  const chart = page.locator("#market-response .recharts-wrapper");
  await chart.scrollIntoViewIfNeeded();
  await chart.hover({ position: { x: 160, y: 120 } });
  await expect(chart.locator(".recharts-tooltip-wrapper")).toBeVisible();
  const summary = page.locator("summary").filter({ hasText: "Details: event-study estimates, uncertainty, counts, and windows" });
  await summary.focus();
  await page.keyboard.press("Space");
  await expect(summary.locator("..")).toHaveAttribute("open", "");
  for (const details of await page.locator("details").all()) await details.evaluate((node) => { node.open = true; });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  expect([...new Set(dataRequests)].sort()).toEqual(["manifest", ...CORE].map((name) => `${basePath}/data/${name}.json`).sort());
  for (const icon of await page.locator('link[rel*="icon"]').all()) {
    const href = await icon.getAttribute("href");
    expect(new URL(href, page.url()).pathname).toMatch(new RegExp(`^${basePath}/icon\\.svg`));
    expect((await request.get(href)).ok()).toBeTruthy();
  }
  const assets = await page.locator('script[src], link[rel="stylesheet"]').evaluateAll((nodes) => nodes.map((node) => node.src || node.href));
  expect(assets.length).toBeGreaterThan(0);
  expect(assets.every((url) => new URL(url).pathname.startsWith(`${basePath}/_next/`))).toBe(true);
  healthy();
});

test("downloads match displayed tables, source values, and approved static CSVs", async ({ page, request }) => {
  const healthy = browserHealth(page);
  await ready(page);
  for (const details of await page.locator("details").all()) await details.evaluate((node) => { node.open = true; });
  const mappings = {
    event_study: ["Download event-study estimates and inference (CSV)", "basis_points"],
    regression_controlled: ["Download with market controls (CSV)", "basis_points"],
    regression_date_fe: ["Download date fixed-effects model (CSV)", "basis_points"],
    country_coverage: ["Download country coverage (CSV)", "observations_and_dates"],
  };
  const tableDownloads = {};
  for (const [name, [label]] of Object.entries(mappings)) tableDownloads[name] = await downloadTable(page, label);
  const eventRows = tableDownloads.event_study.rows;
  expect(eventRows[0][4]).toBe("Cumulative abnormal log return (bps)");
  expect(eventRows[0][7]).toBe("Cumulative p-value (unadjusted)");
  readPayload("event_study").forEach((source, index) => {
    expect(eventRows[index + 1][1]).toBe(String(source.relative_day));
    expect(eventRows[index + 1][4]).toBe(source.cumulative_average_abnormal_return === null ? "n/a" : `${(source.cumulative_average_abnormal_return * 10_000).toFixed(3)} bps`);
    expect(eventRows[index + 1][5]).toBe(source.std_error === null ? "n/a" : `${(source.std_error * 10_000).toFixed(3)} bps`);
  });
  for (const download of readPayload("manifest").approved_downloads || []) {
    const response = await request.get(`${basePath}/${download.path}`);
    expect(response.ok()).toBeTruthy();
    expect(await response.body()).toEqual(fs.readFileSync(path.join(artifactRoot, download.path)));
    expect(mappings[download.table], "Approved download must identify its corresponding public table").toBeDefined();
    expect(download.units).toBe(mappings[download.table][1]);
    expect(parseCsv(await response.text())).toEqual(tableDownloads[download.table].rows);
    if (readPayload("manifest").publication_status === "approved") {
      const link = page.getByRole("link", { name: download.label, exact: true });
      await expect(link).toHaveAttribute("href", `${basePath}/${download.path}`);
      await link.focus();
      const downloaded = page.waitForEvent("download");
      await page.keyboard.press("Enter");
      expect(fs.readFileSync(await (await downloaded).path())).toEqual(await response.body());
    }
  }
  healthy();
});
