# Roadmap

This roadmap separates finished merge work from future research extensions.

## Current Integrated State

The repository now combines:

- the original daily ETF GPR Equity Observatory
- GeoRiskLab-style provenance helpers
- deterministic monthly benchmark sample mode
- user-supplied monthly benchmark real mode
- monthly HAC benchmark regressions
- monthly expanding-window forecast comparisons
- a unified task runner
- a Monthly Benchmark dashboard tab

## V0.2 Wrap-Up

Status: implemented on the current merge branch.

Included:

- daily ETF workflow preserved
- monthly benchmark sample and real modes added
- source manifests and local-only source policy added
- monthly benchmark models added
- CI monthly sample pipeline added
- docs consolidated around the daily/monthly distinction

## V0.3 Research Extensions

Potential next work:

- add FRED macro controls if an API key is available
- add selected real macro controls to the monthly benchmark
- add a narrow GDELT extension after choosing event types and countries
- add country-specific GPR if the extraction method is reliable

These should be added only with source validation and explicit interpretation
rules.

## V1.0 Research Upgrade

Potential larger upgrade:

- country-level monthly panel with enough countries for credible clustered
  inference
- richer robustness package
- refreshed dashboard screenshots
- optional public deployment after deciding data-publication policy

## Do Not Add Casually

Do not add:

- raw third-party data
- local-only source configs
- sample-mode outputs as empirical findings
- real local paths in manifests
- claims that the monthly benchmark is a country-panel proof
- claims that the project is a trading system or investment advice
