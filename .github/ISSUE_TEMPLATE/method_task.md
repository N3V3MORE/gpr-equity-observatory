---
name: Method task
about: Add or revise econometric, forecasting, or validation functionality
labels: methodology
---

## Method

Name:
Purpose:
Main equation or algorithm:

## Scope Gate

- [ ] This is release hardening for already implemented behavior.
- [ ] This is new method work with a scoped plan, issue, or PR description:
- [ ] The result claim this method is meant to support is stated cautiously:

## Inputs

Required columns:
Required frequency:
Required sample:
Dataset mode:

## Outputs

Tables:
Figures:
Metadata or manifests:
Dashboard/reporting changes:

## Failure Modes

What could go wrong?

Examples:
- look-ahead bias
- sample output presented as real evidence
- daily and monthly datasets mixed incorrectly
- weak-cluster inference overstated
- generated artifacts not reproducible

## Acceptance Criteria

- [ ] Method implemented outside notebooks
- [ ] Synthetic-data or fixture test added
- [ ] Output saved reproducibly
- [ ] Methodology docs updated
- [ ] Relevant rebuild command documented and run
- [ ] Public-facing claims remain cautious
- [ ] No causal, trading, or strong emerging-market asymmetry claim is added
      without validated supporting evidence
