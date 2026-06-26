# Profile Packaging

## What You Should Do Now

Use this project as a GitHub/profile research project first. You do not need to
deploy it publicly or add more datasets before showing it.

Recommended next actions:

1. Put the GitHub repository on your profile.
2. Use the CV bullet below.
3. Use the LinkedIn summary below if you want to post the project.
4. Use the three-minute script before interviews or meetings.
5. Use the screenshots in `reports/screenshots/` when you need visuals.

Simple GitHub repository description:

> Reproducible quant economics project studying geopolitical risk and equity
> market responses across developed and emerging market ETF proxies, with a
> separate monthly benchmark layer for reproducibility checks.

## What Not To Claim

Do not claim that this project proves a causal effect. It does not.

Do not claim that it is a trading system. It is not.

Do not claim strong emerging-market asymmetry. The current evidence is mixed:
the controlled and date fixed-effects GPR-jump interactions are small and not
statistically strong.

Do not claim monthly sample mode is empirical evidence. It is not empirical
evidence.

Do not claim the monthly benchmark is a country-panel proof. The current monthly
benchmark is an aggregate developed/emerging comparison and not a country-panel
proof.

The strongest honest claim is:

> I built a reproducible empirical research platform and found cautious evidence
> that geopolitical risk is associated with equity-market risk, while the
> emerging-market asymmetry result remains mixed.

## Optional Future Work In Plain English

You said the future options were confusing, so here is the short version.

- Public deployment means turning the dashboard into a shareable web link. This
  is optional.
- FRED controls means adding more official macroeconomic variables, such as
  interest rates or inflation data. This is useful later, but not required now.
- GDELT or country-specific GPR means adding more advanced news/geopolitical
  data. This is a bigger extension and should wait.

For now, the best choice is to present the current project clearly.

## CV Bullet

Built a reproducible Python research platform measuring equity-market responses
to geopolitical risk across 20 country ETF proxies, implementing event studies,
panel fixed-effects regressions, quantile regressions, local projections, a
drawdown-risk classifier, a monthly benchmark pipeline, and an interactive
Streamlit dashboard.

## Short Project Summary

GPR Equity Observatory is a quant economics project that studies how equity
markets respond to geopolitical risk shocks across emerging and developed market
ETF proxies. It combines daily GPR data, ETF returns, market controls, event
studies, panel regressions, local projections, tail-risk analysis, and a simple
time-aware ML classifier in a reproducible Python pipeline.

The monthly benchmark layer adds deterministic sample mode, user-supplied real
mode, source manifests, HAC spread regressions, and expanding-window forecast
comparisons. It is a benchmark layer, not the main country ETF panel.

## LinkedIn Summary

I built GPR Equity Observatory, a reproducible quant economics project examining
how equity markets respond to geopolitical risk shocks across emerging and
developed economies. The project uses daily country ETF returns, the
Caldara-Iacoviello GPR index, public market controls, event studies, panel
regressions, quantile regressions, local projections, and a simple drawdown-risk
classifier. The output includes a tested Python pipeline, a Streamlit dashboard,
a research note, and a technical appendix.

It also includes a monthly benchmark layer that keeps sample mode and real mode
separate and documents which outputs are local only.

The current evidence is intentionally reported cautiously: GPR is associated
with equity-market risk, but the emerging-market asymmetry result is not yet a
strong statistical conclusion after controls. The main value is the transparent
and reproducible empirical workflow.

## Interview Talking Points

- This is not a stock-prediction project. It studies risk transmission from
  geopolitical uncertainty to international equity-market exposure.
- I used ETFs because they are accessible and reproducible, but I document that
  ETF returns mix local equity returns and dollar exchange-rate exposure.
- The main empirical challenge is confounding: GPR spikes often happen at the
  same time as oil shocks, dollar moves, VIX spikes, and macro news.
- I used several methods because no single model answers the whole question:
  event studies for timing, panel regressions for average association, quantile
  regression for downside asymmetry, and local projections for abnormal-return
  response paths.
- The ML model is deliberately simple and time-aware. It is exploratory, not a
  trading signal.
- The monthly benchmark is useful for reproducibility and aggregate comparison,
  but sample mode is not empirical evidence and real monthly aggregate mode is
  not a country-panel proof.

## Three-Minute Walkthrough Script

This project is called GPR Equity Observatory. It asks whether equity markets,
especially emerging markets, respond differently to geopolitical risk shocks.

The data combine 20 country ETF proxies with the Caldara-Iacoviello daily
geopolitical risk index. I use ETF returns because they are easy to reproduce
with public data, but I explicitly treat them as dollar-based global-investor
exposure rather than pure local market returns.

The pipeline starts by downloading ETF prices, building daily log returns,
ingesting GPR data, adding market controls, and creating a country-day analysis
panel. From there, it runs event studies, market-model abnormal returns, panel
regressions, quantile regressions, local projections, rolling GPR sensitivities,
and a simple drawdown-risk classifier.

The dashboard lets a user inspect GPR shocks, event-study responses, regression
coefficients, tail-risk estimates, local projection paths, ML drawdown metrics,
rolling betas, and data coverage.

There is also a Monthly Benchmark tab. It shows whether the monthly layer is in
sample mode or real mode, displays provenance status, plots monthly GPR shocks
and the developed/emerging aggregate spread, and shows regression and forecast
tables when available.

The current results are mixed. The controlled panel regression finds a negative
association between GPR and returns, but the emerging-market interaction is not
statistically strong. Robustness checks support the controlled GPR association
more than the emerging-market asymmetry claim. The ML classifier has modest
predictive value, with rolling volatility more important than GPR features.

The main strength of the project is not a dramatic headline result. It is the
reproducible empirical framework: the methods are tested, the data pipeline is
clear, the limitations are documented, and the results are presented honestly.

## Likely Questions And Answers

### Why ETFs?

ETFs are free, accessible, and reproducible. They represent global-investor
country exposure. The tradeoff is that returns include currency exposure and ETF
market structure, so I document that limitation.

### Is the result causal?

No. I would not claim full causality. GPR shocks can coincide with oil shocks,
VIX spikes, dollar movements, and macro news. The project measures associations
and response patterns, with controls and robustness checks to improve
interpretability.

### Why quantile regression?

The hypothesis is about downside asymmetry. Mean regressions can miss effects
that mainly appear during bad return states. Quantile regression lets me compare
the GPR association at the 10th percentile, 25th percentile, and median.

### Why use ML?

The ML layer reframes the problem as risk classification: can current conditions
help flag higher short-horizon drawdown risk? I use purged chronological validation to
avoid look-ahead bias and keep the model simple enough to interpret.

### What would improve the project next?

The best next steps are FRED macro controls, country-specific GPR where
reliable, and later a carefully scoped GDELT extension.

## Quick Results Brief

Use `reports/RESULTS_BRIEF.md` when you need a short, honest explanation of the
main result. It is generated from the pipeline outputs, so rebuild it with
`python scripts/build_all.py` rather than editing it by hand.

## Dashboard Screenshots

Profile-ready screenshots are saved in `reports/screenshots/`:

- `dashboard_overview.png`: data scope and main GPR chart.
- `dashboard_robustness.png`: event-study robustness chart.
- `dashboard_panel_regression.png`: regression and sample-robustness tables.
