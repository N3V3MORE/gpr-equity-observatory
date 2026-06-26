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

## Acceptance Criteria

- [ ] Ingestion code runs outside notebooks
- [ ] Output schema documented
- [ ] Tests added
- [ ] Data source docs updated
- [ ] No raw restricted data or local secrets committed
