# Data Source Decisions

This note records the main external-data choices left in the project. These are
research-design decisions, not just coding tasks.

## FRED Macro Controls

Official source:

- [FRED API documentation](https://fred.stlouisfed.org/docs/api/fred/)
- [FRED API key documentation](https://fred.stlouisfed.org/docs/api/api_key.html)

Current status:

- The project already has no-key market controls from Yahoo Finance proxies.
- Adding FRED would improve macro interpretation, especially for rates, spreads,
  inflation, and other economic controls.
- FRED API access requires an API key.

Decision needed:

- Whether to use a FRED API key.
- Which macro controls to add first.

Recommended first FRED controls:

- High-yield credit spread or financial stress proxy.
- Federal funds rate or policy-rate proxy.
- Inflation expectation or inflation series, if used at monthly frequency.

Economics warning:

Daily ETF returns and monthly macro variables do not naturally line up. Any
monthly or quarterly macro control must be lagged and documented carefully to
avoid look-ahead bias.

## Country-Specific GPR

Official source:

- [Country-Specific GPR page](https://www.matteoiacoviello.com/gpr_country.htm)
- [Main GPR page](https://www.matteoiacoviello.com/gpr.htm)

Current status:

- The current pipeline uses the official daily global GPR file.
- The official site says country-specific indexes exist for advanced and
  emerging economies.
- The country pages appear to be chart-oriented pages rather than a simple
  single workbook download.

Decision needed:

- Whether to scrape or manually structure the country-specific country pages.
- Whether country-specific GPR should be a core result or an appendix
  robustness check.

Recommendation:

- Treat country-specific GPR as a later robustness extension, not as the next
  core dependency.
- Do not scrape the pages until we choose a narrow country list and confirm that
  the extracted data can be validated.

## Monthly Benchmark Sources

Current status:

- The monthly benchmark layer has two modes:
  - `monthly_benchmark_sample`: deterministic generated data for CI and
    software validation.
  - `monthly_benchmark_real`: user-supplied GPR and Kenneth French factor
    files.
- Real monthly source configuration lives in local-only `config/sources.yml`,
  copied from `config/sources.sample.yml`.
- Real source manifests hash local input files but redact absolute local paths.
- HTTPS real sources require an expected SHA-256 hash. Non-HTTPS URL schemes are
  rejected.

Source choices:

- Monthly GPR uses the Caldara-Iacoviello monthly export format with `GPR`,
  `GPRT`, and `GPRA` columns mapped to project-standard names.
- Monthly developed/emerging returns use Kenneth French factor zip files and the
  `Mkt-RF` and `RF` monthly columns.

Interpretation rule:

- The developed/emerging monthly benchmark is an aggregate comparison. It should
  not be presented as country-level or country-clustered panel evidence.

## GDELT News/Event Data

Official source:

- [GDELT data documentation](https://www.gdeltproject.org/data.html)

Current status:

- GDELT is valuable but broad and noisy.
- The current project already has a strong core without it.

Decision needed:

- Whether to use GDELT event data, GDELT GKG, or the DOC API.
- Which countries and event types to include.

Recommendation:

- Do not add full GDELT ingestion yet.
- If used, start with a narrow extension: one or two countries, conflict-related
  events, and simple daily counts.

## Recommended Order

1. Decide deployment data strategy.
2. If richer economics matters more than public deployment, add FRED first.
3. Add country-specific GPR only after deciding the extraction method.
4. Add GDELT last, with a narrow and testable scope.
