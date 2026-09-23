const assert = require("node:assert/strict");
const test = require("node:test");
const { loadTs } = require("./load-ts.cjs");
const { EVENT_STUDY_COLUMNS, MARKET_REACTION_READER_COLUMNS, SELECTED_EVENT_COLUMNS, TOP_SHOCKS_COLUMNS } = loadTs("src/lib/labels.ts");
const { rowsToCsv } = loadTs("src/lib/csv.ts");

test("top-shock numeric cells preserve missing input and genuine zero", () => {
  const columns = TOP_SHOCKS_COLUMNS.filter(({ key }) => ["gpr", "gpr_act", "gpr_threat"].includes(key));
  assert.equal(columns.length, 3);
  for (const column of columns) {
    for (const missing of [null, undefined, "", " \t ", "invalid"]) {
      assert.equal(column.format(missing), "n/a", column.key);
    }
    for (const zero of [0, "0", " 0 "]) {
      assert.equal(column.format(zero), "0", column.key);
    }
  }
  assert.equal(rowsToCsv([{ gpr: null, gpr_act: undefined, gpr_threat: " " }], columns),
    "GPR level,Actions,Threats\nn/a,n/a,n/a");
  assert.equal(rowsToCsv([{ gpr: 0, gpr_act: 0, gpr_threat: 0 }], columns),
    "GPR level,Actions,Threats\n0,0,0");
});

test("event-study details and CSV retain inference, counts, signed endpoints, and log-return units", () => {
  const row = {
    market_group: "developed", relative_day: -1, accumulation_start_day: -5,
    average_abnormal_return: 0.00012, cumulative_average_abnormal_return: -0.00123,
    std_error: 0.00045, t_stat: -2.7333, p_value: 0.00000012,
    observation_count: 123, event_count: 19,
  };
  assert.deepEqual(EVENT_STUDY_COLUMNS.map(({ key }) => key), [
    "market_group", "relative_day", "accumulation_start_day", "average_abnormal_return",
    "cumulative_average_abnormal_return", "std_error", "t_stat", "p_value", "observation_count", "event_count",
  ]);
  const csv = rowsToCsv([row], EVENT_STUDY_COLUMNS);
  assert.match(csv, /Endpoint \(relative trading day\),Earliest series day/);
  assert.match(csv, /Cumulative abnormal log return \(bps\),Cumulative std\. error \(bps\)/);
  assert.match(csv, /Cumulative p-value \(unadjusted\),ETF-event observations,Represented event dates/);
  assert.match(csv, /Developed markets,-1,-5,1\.200 bps,-12\.300 bps,4\.500 bps,-2\.7333,1\.200e-7,123,19$/);
  assert.doesNotMatch(csv, /confidence|Days after shock/);
  const checkpoint = MARKET_REACTION_READER_COLUMNS.find(({ key }) => key === "cumulative_average_abnormal_return");
  assert.equal(checkpoint.format(row.cumulative_average_abnormal_return), "-0.1%");
  assert.match(checkpoint.label, /log return \(%\)/);
  for (const key of ["std_error", "t_stat", "p_value", "observation_count", "event_count"]) {
    const column = EVENT_STUDY_COLUMNS.find((column) => column.key === key);
    assert.equal(column.format(null), "n/a", key);
    assert.doesNotMatch(column.format(0), /n\/a/, key);
  }
});

test("selected dates and highlighted jumps export distinct boolean statuses without coercion", () => {
  const selected = rowsToCsv([
    { date: "2024-03-01", gpr: 123, gpr_change: 12.5, gpr_change_shock: true, represented_in_abnormal_study: null },
    { date: "2024-04-01", gpr: 100, gpr_change: 0, gpr_change_shock: true, represented_in_abnormal_study: false },
  ], SELECTED_EVENT_COLUMNS);
  assert.match(selected, /Selected GPR event date,GPR level,Daily change \(index points\),Flagged shock day,In recorded abnormal-return windows/);
  assert.match(selected, /2024-03-01,123,\+12\.5,Yes,Unavailable/);
  assert.match(selected, /2024-04-01,100,0\.0,Yes,No/);
  const flags = TOP_SHOCKS_COLUMNS.filter(({ key }) => ["gpr_change_shock", "selected_for_event_study"].includes(key));
  assert.equal(rowsToCsv([{ gpr_change_shock: true, selected_for_event_study: false }], flags),
    "Flagged shock day,Selected event date\nYes,No");
});
