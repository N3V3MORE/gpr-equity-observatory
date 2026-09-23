// SYNTHETIC SOFTWARE TEST DATA. Never use this bundle as empirical research.
const fs = require("node:fs");
const path = require("node:path");
const { validSnapshot } = require("./snapshot-fixture.cjs");
const { loadTs } = require("./load-ts.cjs");
const { rowsToCsv } = loadTs("src/lib/csv.ts");
const { EVENT_STUDY_COLUMNS } = loadTs("src/lib/labels.ts");

function browserSnapshot() {
  const bundle = validSnapshot();
  Object.assign(bundle.manifest, {
    snapshot_id: "synthetic-browser-v1", data_kind: "synthetic", publication_status: "approved",
    // The UI flag deliberately exercises links. It is NOT publication approval.
    end_date: "2024-01-05", build_date: "2024-01-06", shock_count: 1,
    approved_downloads: [{label:"SYNTHETIC TEST event-study table (CSV)", path:"downloads/synthetic-event-study.csv", table:"event_study", units:"basis_points"}],
  });
  Object.assign(bundle.overview.headline, {end_date:"2024-01-05", shock_count:1, selected_event_count:1, represented_event_count:1});
  bundle.country_coverage[0].last_date = "2024-01-05";
  bundle.country_coverage[0].observation_count = 5;
  bundle.copy.current_answer_points = ["SYNTHETIC TEST DATA — NOT RESEARCH. These invented values test charts and downloads only."];
  bundle.copy.method_map = ["Event study", "Panel regression"].map(Tool => ({Tool, Question:"Synthetic test method", Output:"Fixture table", "What to look for":"Software behavior only"}));
  bundle.gpr_timeline.series = [0, 10, null, 30, 20].map((gpr, index) => ({date:`2024-01-0${index+1}`, gpr, gpr_change:index === 3 ? 20 : 0, gpr_change_shock:index === 3, selected_for_event_study:index === 3}));
  bundle.gpr_timeline.top_shocks = [{...bundle.gpr_timeline.series[3], gpr_act: null, gpr_threat: 0, event:"Synthetic event"}];
  bundle.gpr_timeline.selected_events = [{...bundle.gpr_timeline.series[3], represented_in_abnormal_study:true}];
  bundle.event_study = ["developed", "emerging"].flatMap((market_group, group) =>
    (group ? [0.0001,null,0.0003,0,0.0005] : [0,0.0002,null,-0.0002,0.0004]).map((value,index) => ({
      market_group, relative_day:index-1, accumulation_start_day:-1, average_abnormal_return:value,
      cumulative_average_abnormal_return:value, std_error:value === null ? null : 0.0001,
      t_stat:value === null ? null : value/0.0001, p_value:value === null ? null : 0.04,
      observation_count:12, event_count:3,
    })));
  bundle.reader_summaries.market_reaction = bundle.event_study.filter(row => row.relative_day === 0).map(row => ({...row, market_group:row.market_group === "developed" ? "Developed markets" : "Emerging markets", direction:"Synthetic", evidence_strength:"Fixture only", plain_note:"Not research"}));
  bundle.reader_summaries.regression_translation[0].test = "Controlled GPR association";
  for (const rows of Object.values(bundle.regression)) for (const row of rows) {
    Object.assign(row, {estimate:-0.00004, std_error:0.00005, t_stat:-0.8, p_value:0.4});
  }
  return bundle;
}

function writeBrowserFixture(directory) {
  const bundle = browserSnapshot();
  fs.mkdirSync(path.join(directory, "data"), {recursive:true});
  fs.mkdirSync(path.join(directory, "downloads"), {recursive:true});
  for (const [name,value] of Object.entries(bundle)) fs.writeFileSync(path.join(directory,"data",`${name}.json`),JSON.stringify(value,null,2)+"\n",{flag:"wx"});
  fs.writeFileSync(path.join(directory,"downloads/synthetic-event-study.csv"), rowsToCsv(bundle.event_study,EVENT_STUDY_COLUMNS),{flag:"wx"});
  fs.writeFileSync(path.join(directory,"SYNTHETIC_TEST_ARTIFACT.txt"),"SYNTHETIC SOFTWARE TEST DATA. NOT A RESEARCH PUBLICATION.\n",{flag:"wx"});
  return bundle;
}
module.exports = {browserSnapshot, writeBrowserFixture};
