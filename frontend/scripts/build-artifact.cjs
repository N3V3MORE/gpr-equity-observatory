const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { REPO, SYNTHETIC_MARKER, validatePublication, stageFiles, verifyStaged, snapshotHashes, readPayloads, sealArtifact } = require("./public-snapshot.cjs");

function build(mode, {repoRoot = REPO} = {}) {
  const frontend = path.join(repoRoot, "frontend");
  let release;
  if (mode === "public") {
    release = validatePublication({repoRoot, tracked:true});
    verifyStaged(release, path.join(frontend,"public"));
  } else if (mode === "test") {
    const directory = fs.mkdtempSync(path.join(os.tmpdir(),"gpr-synthetic-build-"));
    require("../tests/browser-fixture.cjs").writeBrowserFixture(directory);
    readPayloads(directory);
    stageFiles(directory, path.join(frontend,"public"), Object.keys(snapshotHashes(directory)));
    console.log("SYNTHETIC SOFTWARE TEST BUILD — NOT FOR PUBLICATION");
  } else throw new Error("Expected public or test build mode");
  const result = spawnSync(process.execPath,[require.resolve("next/dist/bin/next"),"build"], {
    cwd:frontend, stdio:"inherit", env:{...process.env,NEXT_TELEMETRY_DISABLED:"1"},
  });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`Static build failed (${result.status})`);
  if (release) {
    verifyStaged(validatePublication({repoRoot, tracked:true}), path.join(frontend,"out"), {artifact:true});
    sealArtifact(release,frontend);
  } else if (!fs.existsSync(path.join(frontend,"out",SYNTHETIC_MARKER))) throw new Error("Synthetic artifact marker is missing");
}
if (require.main === module) {
  try { build(process.argv[2]); }
  catch (error) { console.error(`Build blocked: ${error.message}`); process.exitCode=1; }
}
module.exports = {build};
