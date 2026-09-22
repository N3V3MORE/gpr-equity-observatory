const assert = require("node:assert/strict");
const test = require("node:test");
const { loadTs } = require("./load-ts.cjs");
const { TOP_SHOCKS_COLUMNS } = loadTs("src/lib/labels.ts");
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
