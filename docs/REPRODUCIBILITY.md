# Reproducibility

This project is designed as a local-first reproducible research workflow. It has
two related but separate pipelines:

- The daily ETF pipeline is the main GPR Equity Observatory product.
- The monthly benchmark pipeline is a lower-frequency developed/emerging
  aggregate benchmark ported from GeoRiskLab.

The two pipelines should stay separate in files, charts, and interpretation.

## Environment

Install the editable development environment:

```powershell
python -m pip install -r requirements.txt
```

For the resolver-locked environment:

```powershell
uv sync --all-extras
```

The project requires Python 3.11 or newer.

## Daily ETF Pipeline

The daily ETF pipeline downloads public market data, builds country ETF returns,
adds daily Caldara-Iacoviello GPR data, runs daily empirical models, and writes
dashboard-ready outputs.

Run the daily pipeline:

```powershell
python scripts/run_task.py build-daily
```

Equivalent legacy command:

```powershell
python scripts/build_all.py
```

Generated daily outputs are written under `data/raw/`, `data/processed/`, and
`reports/figures/`. They are local only by default and are ignored by Git.

## Monthly Benchmark Pipeline

The monthly benchmark pipeline has two modes.

Sample mode:

```powershell
python scripts/run_task.py monthly-sample --min-train-months 24
```

Sample mode generates deterministic monthly data, validates the software path,
runs benchmark regressions, and runs forecast comparisons. Sample mode is not
empirical evidence.

Real mode:

```powershell
copy config\sources.sample.yml config\sources.yml
python scripts/run_task.py build-monthly-real
python scripts/run_task.py validate-monthly-real
```

Real mode uses user-supplied local GPR and Kenneth French factor files. The
source config, raw files, real generated outputs, and real manifests are local
only unless the user intentionally publishes them.

## Checks

Run lint:

```powershell
python scripts/run_task.py lint
```

Run tests:

```powershell
python scripts/run_task.py test
```

Run the CI-style monthly sample path:

```powershell
python scripts/run_task.py monthly-sample --min-train-months 24
```

## Dashboard

Run the dashboard:

```powershell
streamlit run app.py
```

The dashboard can run with daily ETF outputs only. If monthly benchmark outputs
exist, it adds the Monthly Benchmark tab content. If monthly outputs are absent,
the tab explains how to build them.

For a concise clean-clone rebuild checklist, see
[docs/REPRODUCIBILITY_CHECKLIST.md](REPRODUCIBILITY_CHECKLIST.md).

## What Is Committed

Committed:

- source code
- tests
- configuration samples
- documentation
- dashboard screenshots
- profile artifacts

Local only by default:

- `config/sources.yml`
- `data/raw/`
- `data/interim/`
- `data/processed/`
- monthly real source manifests
- monthly benchmark result tables
- generated figure outputs

## Claims Boundary

This is not a trading system and not investment advice. The empirical results
are not causal. Sample mode is not empirical evidence. Monthly real mode is an
aggregate benchmark, not a country-panel proof.
