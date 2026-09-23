const { execFileSync } = require("node:child_process");
const path = require("node:path");

module.exports = async () => {
  if (process.env.GPR_BROWSER_PUBLICATION !== "1") return;
  const frontend = path.resolve(__dirname, "../..");
  if (process.env.GPR_ARTIFACT_DIR && path.resolve(process.env.GPR_ARTIFACT_DIR) !== path.join(frontend, "out")) {
    throw new Error("Publication checks require the exact frontend/out release artifact.");
  }
  // Fails closed: this requires the committed approval record and exact artifact bytes.
  execFileSync(process.execPath, ["scripts/public-snapshot.cjs", "artifact"], { cwd: frontend, stdio: "inherit" });
};
