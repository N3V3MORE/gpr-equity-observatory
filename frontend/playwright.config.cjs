const { defineConfig } = require("@playwright/test");
const os = require("node:os");
const path = require("node:path");

const basePath = (process.env.NEXT_PUBLIC_BASE_PATH || "").replace(/\/$/, "");
const origin = `http://127.0.0.1:${process.env.GPR_BROWSER_PORT || 4173}`;
process.env.GPR_BROWSER_OUTPUT_DIR ||= path.join(os.tmpdir(), "gpr-public-v1-browser", `${Date.now()}-${process.pid}`);

module.exports = defineConfig({
  testDir: "./tests/browser",
  testMatch: "*.spec.cjs",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  forbidOnly: Boolean(process.env.CI),
  timeout: 30_000,
  expect: { timeout: 10_000 },
  reporter: "list",
  globalSetup: "./tests/browser/publication-setup.cjs",
  outputDir: process.env.GPR_BROWSER_OUTPUT_DIR,
  use: { baseURL: `${origin}${basePath}/`, browserName: "chromium", locale: "en-US", trace: "retain-on-failure", screenshot: "only-on-failure" },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 1000 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
  ],
  webServer: { command: "node scripts/serve-static.cjs", url: `${origin}${basePath}/`, reuseExistingServer: false, timeout: 10_000 },
});
