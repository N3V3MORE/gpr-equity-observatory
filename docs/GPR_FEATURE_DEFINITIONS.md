# GPR Feature Definitions

This note disambiguates GPR columns that intentionally share names across
different workflow stages. Do not rename output columns in a small cleanup
without a migration plan; downstream tables, dashboard schema checks, and tests
expect the current names.

## Core Columns

- `gpr`: daily Caldara-Iacoviello geopolitical risk index level.
- `gpr_change`: first difference of the GPR index level.
- `gpr_global`: monthly Caldara-Iacoviello global GPR level in the monthly
  benchmark layer.

## Z-Score Contexts

`gpr_change_z` is overloaded. The column name is stable, but the standardization
context depends on the workflow:

- Daily descriptive z-score: created in the daily GPR output from the
  full-sample mean and standard deviation of daily `gpr_change`. It is not
  time-aware. Use it for descriptive tables and daily shock summaries, not as
  out-of-sample evidence.
- Panel regression z-score: created inside the daily ETF panel regression
  preparation from the regression sample mean and standard deviation. It is not
  time-aware. Robustness subsamples reuse the full controlled-sample
  standardization so coefficients stay comparable.
- Prediction Lab expanding z-score: created inside the drawdown-risk dataset
  builder from the prior expanding mean and standard deviation available at
  each prediction date. It is time-aware and is the `gpr_change_z` used by
  out-of-sample Prediction Lab models.
- Monthly benchmark descriptive z-score: created in the monthly benchmark
  feature builder from the full monthly sample. It is not time-aware and belongs
  to the aggregate developed/emerging monthly benchmark layer.

When adding a new model feature, choose the standardization context explicitly.
Use a prior expanding transform for genuinely out-of-sample prediction work.

## Shock Flags And Aliases

The preferred future shock flag name is `gpr_change_shock_expanding`: a positive
top-quantile `gpr_change` indicator using only prior observations for the
threshold.

Compatibility aliases remain in outputs:

- `gpr_change_shock`: compatibility alias for `gpr_change_shock_expanding`.
- `gpr_shock`: compatibility alias for the expanding GPR-change shock used by
  event-study and local-projection code.
- `gpr_shock_expanding`: compatibility alias for the expanding shock flag.
- `gpr_change_shock_full_sample` and `gpr_shock_full_sample`: full-sample shock
  flags retained for comparison and robustness only.

New code should prefer `gpr_change_shock_expanding` when it means the expanding
daily GPR-change shock. Keep existing aliases until a larger output-column
migration is planned and tested.
