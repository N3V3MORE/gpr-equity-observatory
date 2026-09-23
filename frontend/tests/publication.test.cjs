const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { execFileSync } = require("node:child_process");
const { APPROVAL, REPO, SYNTHETIC_MARKER, readPayloads, validateDownloads, validatePublication, stageFiles, snapshotHashes, verifyStaged, sealArtifact, verifyArtifact } = require("../scripts/public-snapshot.cjs");
const { build } = require("../scripts/build-artifact.cjs");
const { writeBrowserFixture } = require("./browser-fixture.cjs");
const { CORE } = require("./snapshot-fixture.cjs");

function fixture() {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(),"gpr-publication-test-"));
  const directory = path.join(repoRoot,"publication/snapshots/synthetic-browser-v1");
  const payloads = writeBrowserFixture(directory);
  const record = {schema_version:1,snapshot_id:"synthetic-browser-v1",snapshot_dir:"publication/snapshots/synthetic-browser-v1",data_kind:"synthetic",files:snapshotHashes(directory)};
  fs.writeFileSync(path.join(repoRoot,APPROVAL),JSON.stringify(record));
  return {repoRoot,directory,payloads,record};
}

test("synthetic content passes schema checks only, preserves missing values and real zero", () => {
  const {directory}=fixture();
  const {bundle}=readPayloads(directory);
  assert.equal(bundle.gpr_timeline.series[0].gpr,0);
  assert.equal(bundle.gpr_timeline.series[2].gpr,null);
  assert.equal(bundle.event_study[0].cumulative_average_abnormal_return,0);
  assert.equal(bundle.event_study[2].cumulative_average_abnormal_return,null);
});

for (const name of ["manifest",...CORE]) {
  test(`missing required ${name} blocks the public build before Next.js`, () => {
    const {repoRoot,directory}=fixture();
    // Move only this test's newly created fixture; never touch research outputs.
    fs.renameSync(path.join(directory,"data",`${name}.json`),path.join(directory,"data",`${name}.missing`));
    assert.throws(()=>build("public",{repoRoot}),/Cannot read valid JSON/);
    assert.equal(fs.existsSync(path.join(repoRoot,"frontend/out")),false);
  });
  test(`malformed required ${name} blocks the public build`, () => {
    const {repoRoot,directory}=fixture();
    fs.writeFileSync(path.join(directory,"data",`${name}.json`),"{");
    assert.throws(()=>build("public",{repoRoot}),/Cannot read valid JSON/);
  });
}

test("a manifest cannot conceal incompatible required payloads at publication", () => {
  const {repoRoot,directory}=fixture();
  fs.writeFileSync(path.join(directory,"data/regression.json"),"{}");
  assert.throws(()=>build("public",{repoRoot}),/regression.baseline/);
});

test("a fixture alone, even with the UI approved flag, never satisfies publication", () => {
  const {repoRoot}=fixture();
  assert.throws(()=>validatePublication({repoRoot}),/Synthetic or unreviewed/);
  assert.throws(()=>build("public",{repoRoot}),/Synthetic or unreviewed/);
});

test("relabeling a known synthetic fixture real does not grant publication", () => {
  const {repoRoot,directory,payloads,record}=fixture();
  record.data_kind="real";
  payloads.manifest.data_kind="real";
  fs.writeFileSync(path.join(directory,"data/manifest.json"),JSON.stringify(payloads.manifest));
  fs.writeFileSync(path.join(repoRoot,APPROVAL),JSON.stringify(record));
  assert.throws(()=>validatePublication({repoRoot}),/Synthetic fixture content/);
});

test("missing independent review record blocks publication", () => {
  const repoRoot=fs.mkdtempSync(path.join(os.tmpdir(),"gpr-no-review-"));
  assert.throws(()=>build("public",{repoRoot}),/approved-snapshot.json/);
});

test("a tracked approval path cannot delegate review to a mutable symlink target", t => {
  const {repoRoot}=fixture();
  const approvalPath=path.join(repoRoot,APPROVAL);
  const lstat=fs.lstatSync;
  // Model the OS link metadata without requiring Windows symlink privileges.
  t.mock.method(fs,"lstatSync",(filename,...options)=>filename===approvalPath
    ? {isFile:()=>false,isSymbolicLink:()=>true} : lstat(filename,...options));
  assert.throws(()=>validatePublication({repoRoot}),/regular non-symlink/);
});

test("download bytes and units must match the selected table", () => {
  const {directory,payloads}=fixture();
  assert.deepEqual(validateDownloads(directory,payloads),["downloads/synthetic-event-study.csv"]);
  const csv=fs.readFileSync(path.join(directory,"downloads/synthetic-event-study.csv"),"utf8");
  assert.match(csv,/2\.000 bps/); // 0.0002 decimal log return is 2 basis points.
  assert.match(csv,/0\.000 bps/);
  assert.match(csv,/n\/a/);
  payloads.manifest.approved_downloads[0].units="percent";
  assert.throws(()=>validateDownloads(directory,payloads),/units/);
  payloads.manifest.approved_downloads[0].units="basis_points";
  fs.appendFileSync(path.join(directory,"downloads/synthetic-event-study.csv"),"\nchanged");
  assert.throws(()=>validateDownloads(directory,payloads),/does not match/);
});

test("staging is idempotent and refuses to overwrite unrelated local data", () => {
  const {directory,repoRoot}=fixture();
  const destination=path.join(repoRoot,"frontend/public");
  const files=Object.keys(snapshotHashes(directory));
  stageFiles(directory,destination,files);
  stageFiles(directory,destination,files);
  assert.deepEqual(snapshotHashes(destination),snapshotHashes(directory));
  const unrelated=path.join(destination,"data/local-research.json");
  fs.writeFileSync(unrelated,"preserve this local output");
  assert.throws(()=>stageFiles(directory,destination,files),/Refusing to overwrite/);
  assert.equal(fs.readFileSync(unrelated,"utf8"),"preserve this local output");
});

test("synthetic artifact marker and changed staged bytes block release", () => {
  const {directory,record}=fixture();
  const release={files:Object.keys(record.files).sort(),review:record};
  assert.throws(()=>verifyStaged(release,directory),/synthetic test artifact/);
  const source=path.join(directory,"data");
  const realFiles=Object.keys(snapshotHashes(source));
  const staged=path.join(os.tmpdir(),`gpr-stage-integrity-${Date.now()}-${Math.random()}`);
  stageFiles(source,staged,realFiles);
  const checksums=snapshotHashes(staged);
  verifyStaged({files:realFiles,review:{files:checksums}},staged);
  fs.appendFileSync(path.join(staged,"event_study.json")," ");
  assert.throws(()=>verifyStaged({files:realFiles,review:{files:checksums}},staged),/checksum mismatch/);
  assert.ok(fs.existsSync(path.join(directory,SYNTHETIC_MARKER)));
});

test("artifact integrity covers generated assets and rejects unrelated files outside data", () => {
  const {repoRoot,directory,record}=fixture();
  const frontend=path.join(repoRoot,"frontend");
  const out=path.join(frontend,"out");
  const files=Object.keys(record.files).filter(file=>file!==SYNTHETIC_MARKER).sort();
  stageFiles(directory,out,files);
  fs.writeFileSync(path.join(out,"index.html"),"How are geopolitical risk jumps associated? Research limitations:");
  // Next's static export includes nested route payloads, even without a backend.
  for (const route of ["local/__next.local", "_not-found/__next._not-found"]) {
    fs.mkdirSync(path.join(out,route),{recursive:true});
    fs.writeFileSync(path.join(out,route,"__PAGE__.txt"),"synthetic route payload");
  }
  const release={files,review:record}; // Test file-integrity primitive only, not publication approval.
  sealArtifact(release,frontend);
  verifyArtifact(release,frontend);
  fs.appendFileSync(path.join(out,"index.html"),"changed after checks");
  assert.throws(()=>verifyArtifact(release,frontend),/artifact changed/);
  fs.writeFileSync(path.join(out,"local-source.csv"),"unselected data");
  assert.throws(()=>verifyArtifact(release,frontend),/Unexpected file/);
});

test("reviewed snapshot bytes survive Git checkout with Windows newline conversion enabled", () => {
  const directory=fs.mkdtempSync(path.join(os.tmpdir(),"gpr-checkout-bytes-"));
  const file="publication/snapshots/byte-test/data/manifest.json";
  fs.mkdirSync(path.join(directory,path.dirname(file)),{recursive:true});
  fs.copyFileSync(path.join(REPO,".gitattributes"),path.join(directory,".gitattributes"));
  const original=Buffer.from('{"synthetic_test":"byte preservation only"}\n');
  fs.writeFileSync(path.join(directory,file),original);
  const git=(...args)=>execFileSync("git",["-C",directory,"-c","core.autocrlf=true",...args],{stdio:"pipe"});
  git("init","--quiet");
  git("add","--",".gitattributes",file);
  const checkedOut=path.join(directory,"checkout");
  fs.mkdirSync(checkedOut);
  git("checkout-index","--all",`--prefix=${checkedOut.replaceAll("\\","/")}/`);
  assert.deepEqual(fs.readFileSync(path.join(checkedOut,file)),original);
});

test("reviewed real snapshot passes the non-fixture publication gate", {
  skip:!fs.existsSync(path.join(REPO,APPROVAL)) && "BLOCKED: owner-reviewed real snapshot and provenance are absent; release command fails rather than skipping",
}, () => {
  const release=validatePublication({tracked:true});
  assert.equal(release.payloads.manifest.data_kind,"real");
  assert.equal(release.review.review.status,"approved");
});
