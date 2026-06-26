---
name: Data source task
about: Add, change, or validate a data source
labels: data
---

## Source

Name:
URL:
Access method:
Terms or licensing note:

## Feature-Lock Gate

- [ ] This is release hardening for an already implemented data contract.
- [ ] This is post-lock data work and has an explicit unlock decision:
- [ ] The source belongs to a narrow documented scope.

## Dataset Mode

- [ ] Daily ETF observatory
- [ ] Monthly benchmark sample
- [ ] Monthly benchmark real
- [ ] Future country-month extension

## Required Fields

- [ ] Date
- [ ] Entity identifier
- [ ] Value fields
- [ ] Source metadata
- [ ] Frequency and units documented

## Validation Checks

- [ ] Date range check
- [ ] Duplicate key check
- [ ] Missingness check
- [ ] Unit check
- [ ] Source manifest written
- [ ] Real/sample mode cannot be confused
- [ ] Daily and monthly outputs stay separate in names, paths, docs, and
      dashboard text

## Acceptance Criteria

- [ ] Ingestion code runs outside notebooks
- [ ] Output schema documented
- [ ] Tests added
- [ ] Data source docs updated
- [ ] Interpretation limits are documented before public-facing claims change
- [ ] No raw restricted data or local secrets committed
- [ ] `config/sources.yml` is not committed
