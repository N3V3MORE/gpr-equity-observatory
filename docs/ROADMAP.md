# Roadmap

This roadmap separates finished merge work from future research extensions.

Feature lock is active on `codex/pre-merge-gpr-cleanup` and the current
packaging branch, `codex/polish-readme-reviewer-path`. V0.2 is in
release-hardening mode. V0.3 and V1.0 items are post-lock work and should not
be started unless the user explicitly unlocks feature work.

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

## Active Backlog Issues

Future work is tracked in GitHub issues rather than scattered planning notes:

- [#1 Package current project for portfolio use](https://github.com/N3V3MORE/gpr-equity-observatory/issues/1)
- [#2 Improve dashboard usability without changing models](https://github.com/N3V3MORE/gpr-equity-observatory/issues/2)
- [#3 Decide deployment data strategy](https://github.com/N3V3MORE/gpr-equity-observatory/issues/3)
- [#4 Plan future FRED macro-controls extension](https://github.com/N3V3MORE/gpr-equity-observatory/issues/4)
- [#5 Scope later country-specific GPR or GDELT extension](https://github.com/N3V3MORE/gpr-equity-observatory/issues/5)

## V0.3 Research Extensions

Status: post-lock only.

Potential next work:

- add FRED macro controls if an API key is available
- add selected real macro controls to the monthly benchmark
- add a narrow GDELT extension after choosing event types and countries
- add country-specific GPR if the extraction method is reliable

These should be added only with source validation and explicit interpretation
rules.

## V1.0 Research Upgrade

Status: post-lock only.

Potential larger upgrade:

- country-level monthly panel with enough countries for credible clustered
  inference
- richer robustness package
- screenshot refreshes after future visual dashboard changes
- optional public deployment after deciding data-publication policy

## Do Not Add Casually

Do not add:

- raw third-party data
- local-only source configs
- sample-mode outputs as empirical findings
- real local paths in manifests
- claims that the monthly benchmark is a country-panel proof
- claims that the project is a trading system or investment advice
