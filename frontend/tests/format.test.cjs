const assert = require("node:assert/strict");
const test = require("node:test");
const { loadTs } = require("./load-ts.cjs");
const { toNumber, num, fixed, percent, bps, multiple, signedFixed } = loadTs("src/lib/format.ts");

test("missing and invalid numeric input stays null", () => {
  for (const value of [null, undefined, "", " ", "\t\n", "not a number", "1.2x", NaN, Infinity, -Infinity,
    "Infinity", true, false, [], [0], {}, "0x10", "0b10", "1e999"]) {
    assert.equal(toNumber(value), null, `Unexpected number for ${String(value)}`);
  }
});

test("finite numbers, numeric strings, and genuine zero remain numeric", () => {
  for (const [value, expected] of [[0, 0], ["0", 0], [" 0 ", 0], [2.5, 2.5], [" -2.5 ", -2.5],
    ["1e-3", 0.001], [".5", 0.5], ["+2", 2]]) {
    assert.equal(toNumber(value), expected);
  }
  assert.ok(Object.is(toNumber(-0), -0));
});

test("formatters display missing input as unavailable and preserve zero", () => {
  for (const formatter of [num, fixed, percent, bps, multiple, signedFixed]) {
    assert.equal(formatter(" \t "), "n/a");
    assert.notEqual(formatter(0), "n/a");
  }
  assert.equal(percent(0), "0.0%");
  assert.equal(bps(0), "0.0 bps");
});
