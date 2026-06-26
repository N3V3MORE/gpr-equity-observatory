---
name: Release hardening task
about: Docs, CI, review, screenshot, packaging, or validation work that preserves the locked scope
labels: release-hardening
---

## Task

What needs to be hardened?

## Feature-Lock Check

- [ ] This is release hardening.
- [ ] This preserves the current feature-locked scope.
- [ ] No new research, data, model, dashboard, or product behavior is added.
- [ ] Any scope change has an explicit unlock decision linked here:

## Area

- [ ] README or reviewer navigation
- [ ] Reproducibility or setup docs
- [ ] Pull request, issue, or release notes
- [ ] Screenshot refresh without dashboard behavior changes
- [ ] Tests, CI, or validation contracts
- [ ] Claim-safety or limitation wording

## Guardrails

- [ ] `config/sources.yml` is not committed.
- [ ] Raw third-party data, credentials, and local source files are not
      committed.
- [ ] Daily ETF outputs and monthly benchmark outputs remain separate.
- [ ] Sample-mode outputs are not presented as empirical evidence.
- [ ] The project is not framed as investment advice or a trading system.
- [ ] No causal or strong emerging-market asymmetry claim is added without
      validated supporting evidence.

## Checks

- [ ] `ruff check .`
- [ ] `pytest --cov=gprobs --cov=app --cov-report=term-missing -q`
- [ ] Additional command, if relevant:
