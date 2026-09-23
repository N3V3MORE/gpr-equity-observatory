// Publication is an explicit, checksum-bound review, separate from UI fixtures.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { execFileSync } = require("node:child_process");
const { loadTs } = require("../tests/load-ts.cjs");
const { REQUIRED_DATASETS, validatePublicSnapshot } = loadTs("src/lib/data.ts");
const { rowsToCsv } = loadTs("src/lib/csv.ts");
const labels = loadTs("src/lib/labels.ts");

const REPO = path.resolve(__dirname, "../..");
const APPROVAL = "publication/approved-snapshot.json";
const SYNTHETIC_MARKER = "SYNTHETIC_TEST_ARTIFACT.txt";
const TABLES = {
  event_study: { rows: bundle => bundle.event_study, columns: labels.EVENT_STUDY_COLUMNS, units: "basis_points" },
  regression_controlled: { rows: bundle => bundle.regression.controlled, columns: labels.REGRESSION_TERM_COLUMNS, units: "basis_points" },
  regression_date_fe: { rows: bundle => bundle.regression.date_fe, columns: labels.REGRESSION_TERM_COLUMNS, units: "basis_points" },
  country_coverage: { rows: bundle => bundle.country_coverage, columns: labels.COUNTRY_COVERAGE_COLUMNS, units: "observations_and_dates" },
};
const check = (condition, message) => { if (!condition) throw new Error(message); };
const nonempty = value => typeof value === "string" && value.trim().length > 0;
const sha256 = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
const digest = value => typeof value === "string" && /^[a-f0-9]{64}$/.test(value) && !/^0+$/.test(value);
const timestamp = value => nonempty(value) && /^\d{4}-\d{2}-\d{2}T/.test(value) && Number.isFinite(Date.parse(value));
const readJson = filename => {
  try { return JSON.parse(fs.readFileSync(filename, "utf8")); }
  catch (error) { throw new Error(`Cannot read valid JSON: ${filename}: ${error.message}`); }
};

function filesUnder(directory) {
  check(fs.existsSync(directory), `Missing directory: ${directory}`);
  check(!fs.lstatSync(directory).isSymbolicLink(), `Symlink is not a release input: ${directory}`);
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const filename = path.join(directory, entry.name);
    check(!entry.isSymbolicLink(), `Symlink is not a release input: ${filename}`);
    if (entry.isDirectory()) return filesUnder(filename).map(child => `${entry.name}/${child}`);
    check(entry.isFile(), `Not a regular file: ${filename}`);
    return [entry.name];
  }).sort();
}

function readPayloads(directory) {
  const payloads = Object.fromEntries(["manifest", ...REQUIRED_DATASETS].map(name =>
    [name, readJson(path.join(directory, "data", `${name}.json`))]));
  const bundle = validatePublicSnapshot(payloads);
  check(JSON.stringify([...payloads.manifest.datasets].sort()) === JSON.stringify([...REQUIRED_DATASETS].sort()),
    "Public-v1 must include exactly the required datasets; optional data stays local");
  return { payloads, bundle };
}

function validateDownloads(directory, payloads) {
  const downloads = payloads.manifest.approved_downloads;
  check(Array.isArray(downloads) && downloads.some(item => item.table === "event_study"), "An event-study table download is required");
  const seen = new Set();
  for (const item of downloads) {
    check(item && nonempty(item.label) && typeof item.path === "string" && /^downloads\/[a-z0-9][a-z0-9._-]*\.csv$/i.test(item.path)
      && !item.path.includes("..") && !seen.has(item.path), "Invalid or duplicate download path/label");
    seen.add(item.path);
    const table = TABLES[item.table];
    check(table && item.units === table.units, `Unsupported table or units: ${item.table}`);
    const expected = rowsToCsv(table.rows(payloads), table.columns);
    check(fs.readFileSync(path.join(directory, item.path), "utf8") === expected,
      `Download does not match its approved table and units: ${item.path}`);
  }
  return downloads.map(item => item.path);
}

function validatePublication({ repoRoot = REPO, tracked = false } = {}) {
  const approvalPath = path.join(repoRoot, APPROVAL);
  const approvalStat = fs.lstatSync(approvalPath);
  check(approvalStat.isFile() && !approvalStat.isSymbolicLink(), "Approval must be a regular non-symlink file");
  check(fs.realpathSync(approvalPath).startsWith(`${fs.realpathSync(repoRoot)}${path.sep}`), "Approval resolves outside the repository");
  const review = readJson(approvalPath);
  check(review.schema_version === 1 && typeof review.snapshot_id === "string" && /^[a-z0-9][a-z0-9-]{0,79}$/.test(review.snapshot_id), "Invalid publication record version or snapshot_id");
  check(review.snapshot_dir === `publication/snapshots/${review.snapshot_id}`, "snapshot_dir must match the selected publication snapshot_id");
  const directory = path.join(repoRoot, review.snapshot_dir);
  check(fs.realpathSync(directory).startsWith(`${fs.realpathSync(repoRoot)}${path.sep}`), "Snapshot resolves outside the repository");
  // Inspect every path before reads; neither symlinks nor extra local data are deployable.
  const actualFiles = filesUnder(directory);
  const { payloads, bundle } = readPayloads(directory);
  const manifest = payloads.manifest;
  check(review.data_kind === "real" && manifest.data_kind === "real", "Synthetic or unreviewed data cannot satisfy the real-publication gate");
  check(manifest.snapshot_id === review.snapshot_id && manifest.publication_status === "approved", "Snapshot is not approved by this review record");
  check(!/\bsynthetic\b|\btest fixture\b|Test country|Test question/i.test(JSON.stringify(payloads)), "Synthetic fixture content cannot be published as research");
  check(review.review?.status === "approved" && nonempty(review.review.reviewed_by) && timestamp(review.review.reviewed_at)
    && nonempty(review.review.notes), "Explicit reviewer, review time, and review notes are required");
  check(Array.isArray(review.sources), "Daily source provenance is required");
  for (const id of ["gpr", "etf_prices", "controls"]) {
    const entries = review.sources.filter(source => source.id === id);
    check(entries.length === 1, `Exactly one provenance record is required for ${id}`);
    const source = entries[0];
    check(nonempty(source.url) && /^https:\/\//.test(source.url) && !/example\.(com|org|net)/i.test(source.url)
      && timestamp(source.retrieved_at) && digest(source.sha256) && nonempty(source.redistribution_review), `Incomplete source/redistribution review for ${id}`);
  }
  check(!/\bTODO\b|\bUNREVIEWED\b|REPLACE_ME/i.test(JSON.stringify(review.review) + JSON.stringify(review.sources)), "Review still contains placeholders");
  const downloadFiles = validateDownloads(directory, payloads);
  const expectedFiles = [...["manifest", ...REQUIRED_DATASETS].map(name => `data/${name}.json`), ...downloadFiles].sort();
  check(JSON.stringify(actualFiles) === JSON.stringify(expectedFiles), "Snapshot contains missing or unselected files");
  check(review.files && JSON.stringify(Object.keys(review.files).sort()) === JSON.stringify(expectedFiles), "Review must checksum every selected file, including the manifest");
  for (const file of expectedFiles) {
    check(digest(review.files[file]) && sha256(fs.readFileSync(path.join(directory, file))) === review.files[file], `Review checksum mismatch: ${file}`);
  }
  if (tracked) {
    const selected = [APPROVAL, ...expectedFiles.map(file => `${review.snapshot_dir}/${file}`)];
    execFileSync("git", ["-C", repoRoot, "ls-files", "--error-unmatch", "--", ...selected], { stdio: "pipe" });
    execFileSync("git", ["-C", repoRoot, "diff", "--exit-code", "HEAD", "--", ...selected], { stdio: "pipe" });
  }
  return { review, directory, payloads, bundle, files: expectedFiles };
}

function stageFiles(directory, destination, files) {
  // Refuse to replace an existing local export or silently carry extra public files.
  const existing = fs.existsSync(destination) ? filesUnder(destination) : [];
  for (const file of existing) {
    check(files.includes(file) && fs.readFileSync(path.join(destination, file)).equals(fs.readFileSync(path.join(directory, file))),
      `Refusing to overwrite or publish unrelated file: ${path.join(destination, file)}. Use a clean checkout.`);
  }
  for (const file of files) {
    const target = path.join(destination, file);
    if (fs.existsSync(target)) continue;
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(path.join(directory, file), target, fs.constants.COPYFILE_EXCL);
  }
}

function verifyStaged(release, directory, { artifact = false } = {}) {
  check(!fs.existsSync(path.join(directory, SYNTHETIC_MARKER)), "A synthetic test artifact cannot be released");
  const actual = artifact
    ? ["data", "downloads"].flatMap(folder => filesUnder(path.join(directory, folder)).map(file => `${folder}/${file}`)).sort()
    : filesUnder(directory);
  check(JSON.stringify(actual) === JSON.stringify(release.files), "Staged data/downloads do not match the reviewed file selection");
  for (const file of release.files) {
    check(sha256(fs.readFileSync(path.join(directory, file))) === release.review.files[file], `Staged checksum mismatch: ${file}`);
  }
  if (artifact) {
    const generated = /^(?:_next\/static\/.*\.(?:js|css|woff2?|ttf|otf|svg|png|webp|ico|jpe?g)|(?:local\/|404\/|_not-found\/)?(?:index\.html|index\.txt|__next\.[a-zA-Z0-9_.-]+\.txt)|(?:local\/__next\.local|_not-found\/__next\._not-found)\/__PAGE__\.txt|404\.html|icon\.svg)$/;
    check(filesUnder(directory).every(file => release.files.includes(file) || generated.test(file)), "Unexpected file in the static artifact");
    const html = fs.readFileSync(path.join(directory, "index.html"), "utf8");
    check(html.includes("How are geopolitical risk jumps associated") && html.includes("Research limitations:"), "Built HTML lacks meaningful research content");
  }
}

function sealArtifact(release, frontend) {
  const seal = { review_sha256:sha256(fs.readFileSync(path.join(frontend,"..",APPROVAL))), files:snapshotHashes(path.join(frontend,"out")) };
  fs.writeFileSync(path.join(frontend,".release-artifact.json"),JSON.stringify(seal,null,2)+"\n");
  return seal;
}

function verifyArtifact(release, frontend) {
  verifyStaged(release,path.join(frontend,"out"),{artifact:true});
  const seal = readJson(path.join(frontend,".release-artifact.json"));
  check(seal.review_sha256 === sha256(fs.readFileSync(path.join(frontend,"..",APPROVAL))), "Artifact approval changed after build");
  check(JSON.stringify(seal.files) === JSON.stringify(snapshotHashes(path.join(frontend,"out"))), "Built artifact changed after release checks/build");
}

function snapshotHashes(directory) {
  return Object.fromEntries(filesUnder(directory).map(file => [file, sha256(fs.readFileSync(path.join(directory, file)))]));
}

function prepare({ source, id, repoRoot = REPO }) {
  check(source && /^[a-z0-9][a-z0-9-]{0,79}$/.test(id ?? ""), "prepare requires --source <export-directory> and --id <snapshot-id>");
  const directory = path.join(repoRoot, "publication/snapshots", id);
  const draft = path.join(repoRoot, "publication", `${id}.review-draft.json`);
  check(!fs.existsSync(directory) && !fs.existsSync(draft), `Refusing to overwrite ${directory} or ${draft}`);
  const payloads = Object.fromEntries(["manifest", ...REQUIRED_DATASETS].map(name => [name, readJson(path.join(source, `${name}.json`))]));
  const copyKeys = ["central_question", "intro", "main_takeaway", "use_note", "job_statements", "reader_path", "current_answer_points", "does_not_prove_points", "method_map", "glossary", "how_to_read"];
  payloads.copy = Object.fromEntries(copyKeys.map(key => [key, payloads.copy[key]]));
  payloads.copy.job_statements = payloads.copy.job_statements.filter(row => row.title === "Explanation");
  payloads.copy.method_map = payloads.copy.method_map.filter(row => ["Event study", "Panel regression"].includes(row.Tool));
  payloads.copy.how_to_read = Object.fromEntries(["market_response", "regression"].map(key => [key, payloads.copy.how_to_read[key]]));
  payloads.reader_summaries.regression_translation = payloads.reader_summaries.regression_translation.filter(row => ["Controlled GPR association", "Emerging-market extra response"].includes(row.test));
  payloads.reader_summaries.output_files = payloads.reader_summaries.output_files.filter(row => ["gpr_daily.csv", "analysis_panel.csv", "event_study_abnormal_summary.csv"].includes(path.basename(row.file)));
  const previous = payloads.manifest;
  payloads.manifest = {
    schema_version: 1, profile: "public", available: previous.available, snapshot_id: id,
    data_kind: previous.data_kind === "synthetic" ? "synthetic" : "unreviewed", publication_status: "candidate",
    datasets: [...REQUIRED_DATASETS], build_date: previous.build_date,
    start_date: previous.start_date, end_date: previous.end_date, country_count: previous.country_count, shock_count: previous.shock_count,
    approved_downloads: Object.entries(TABLES).map(([table, spec]) => ({label: `Download ${table.replaceAll("_", " ")} (CSV)`, path: `downloads/${table}.csv`, table, units: spec.units})),
  };
  validatePublicSnapshot(payloads);
  fs.mkdirSync(path.join(directory, "data"), { recursive: true });
  fs.mkdirSync(path.join(directory, "downloads"));
  for (const [name, value] of Object.entries(payloads)) fs.writeFileSync(path.join(directory, "data", `${name}.json`), JSON.stringify(value, null, 2) + "\n", {flag:"wx"});
  for (const [name, spec] of Object.entries(TABLES)) fs.writeFileSync(path.join(directory, "downloads", `${name}.csv`), rowsToCsv(spec.rows(payloads), spec.columns), {flag:"wx"});
  fs.writeFileSync(draft, JSON.stringify({
    schema_version: 1, snapshot_id: id, snapshot_dir: `publication/snapshots/${id}`, data_kind: "unreviewed",
    review: {status: "unreviewed", reviewed_by: "", reviewed_at: "", notes: ""},
    sources: ["gpr", "etf_prices", "controls"].map(sourceId => ({id:sourceId, url:"", retrieved_at:"", sha256:"", redistribution_review:""})),
    files: snapshotHashes(directory),
  }, null, 2) + "\n", {flag:"wx"});
  return { directory, draft };
}

function main(args) {
  const command = args[0];
  const value = flag => args.includes(flag) ? args[args.indexOf(flag) + 1] : undefined;
  if (command === "prepare") return console.log(prepare({source:value("--source"), id:value("--id")}));
  if (command === "hashes") {
    const id = value("--id");
    check(/^[a-z0-9][a-z0-9-]{0,79}$/.test(id ?? ""), "hashes requires --id");
    return console.log(JSON.stringify(snapshotHashes(path.join(REPO, "publication/snapshots", id)), null, 2));
  }
  check(["validate", "stage", "artifact"].includes(command), "Expected prepare, hashes, validate, stage, or artifact");
  const release = validatePublication({tracked:args.includes("--tracked") || command === "artifact"});
  if (command === "stage") stageFiles(release.directory, path.join(REPO, "frontend/public"), release.files);
  if (command === "artifact") verifyArtifact(release, path.join(REPO,"frontend"));
  console.log(`Validated reviewed real snapshot ${release.review.snapshot_id}${command === "artifact" ? " and built artifact" : ""}`);
}

module.exports = { APPROVAL, REPO, SYNTHETIC_MARKER, TABLES, readPayloads, validateDownloads, validatePublication, stageFiles, verifyStaged, snapshotHashes, prepare, sealArtifact, verifyArtifact };
if (require.main === module) {
  try { main(process.argv.slice(2)); }
  catch (error) { console.error(`Publication blocked: ${error.message}`); process.exitCode = 1; }
}
