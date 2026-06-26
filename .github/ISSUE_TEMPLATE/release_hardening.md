---
name: Release hardening task
about: Docs, CI, review, screenshot, packaging, or validation work
labels: release-hardening
---

## Task

What needs to be hardened?

## Scope and Guardrail Check

- [ ] This is release hardening.
- [ ] This preserves the current release baseline.
- [ ] No new research, data, model, dashboard, or product behavior is added.
- [ ] Any scope change has a scoped plan, issue, or PR description linked here:

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
