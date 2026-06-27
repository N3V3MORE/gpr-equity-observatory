# Data Sources

This document describes the data-source policy for the combined GPR Equity
Observatory and monthly benchmark workflow.

## Daily ETF Sources

The daily ETF pipeline uses:

- 20 country ETF proxies listed in `data/country_universe.csv`.
- Yahoo Finance data through `yfinance` for adjusted ETF prices.
- Caldara-Iacoviello daily GPR data.
- Public no-key market controls from Yahoo Finance proxies.

Daily ETF returns are USD log returns. They are useful for reproducible
global-investor exposure, but they are not pure local-currency equity index
returns.

## Daily Market Controls

The current controls are:

- ACWI global equity return.
- VIX level change.
- WTI crude oil futures level change.
- UUP US dollar return.
- US 10-year yield proxy level change.

WTI is a level change because WTI traded below zero in April 2020.

## FRED Macro Controls

The optional FRED macro-control extension uses `FRED_API_KEY` from the local
environment and writes standalone artifacts:

- raw API responses under `data/raw/fred/`
- processed controls at `data/processed/fred_macro_controls.csv`
- a local source manifest at `data/metadata/fred_source_manifest.json`

The first selected controls are Moody's Baa corporate spread over the 10-year
Treasury (`BAA10Y`), effective federal funds rate (`DFF`), and 10-year
breakeven inflation expectations (`T10YIE`). These controls are a macro
robustness extension, not a new headline result. Current daily conclusions
remain based on the existing no-key market controls.

Only lagged FRED columns should be used in later predictive models. The raw
same-date FRED columns are kept for provenance and inspection, not for immediate
model integration.

## Monthly Benchmark Sources

The monthly benchmark pipeline uses two modes.

Sample mode:

- deterministic generated GPR, return, GDELT, and macro-like sample data
- committed code only
- no external data dependency

Sample mode is not empirical evidence.

Real mode:

- user-supplied Caldara-Iacoviello monthly GPR export
- user-supplied Kenneth French developed-market factor zip
- user-supplied Kenneth French emerging-market factor zip

Real mode reads `config/sources.yml`, which is copied from
`config/sources.sample.yml`. The real config is local only and ignored by Git.

## Provenance Policy

Monthly real sources are hashed before use. Manifests record source names,
redacted source references, and SHA-256 hashes. Absolute local paths are not
intended to be committed.

HTTPS sources require an expected SHA-256 hash. Non-HTTPS URL schemes are
rejected.

## GDELT And Other Macro Controls

GDELT and broader macro controls are staged extensions. Current monthly real
mode uses explicit placeholder GDELT and macro columns until validated real
inputs are added.

Do not describe placeholder GDELT or placeholder macro columns as real data.

## Claims Boundary

The project is not a trading system and not investment advice. Data choices
support reproducible applied economics work, not causal proof. The monthly
benchmark is an aggregate benchmark and not a country-panel proof.
