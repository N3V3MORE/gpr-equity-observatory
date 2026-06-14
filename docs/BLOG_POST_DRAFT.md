# Geopolitical Risk And Equity Markets: Building A Reproducible Observatory

Geopolitical risk is easy to talk about and hard to measure well. Markets react
to wars, sanctions, diplomatic crises, terrorist attacks, and political
instability, but those events rarely happen in isolation. They often arrive at
the same time as oil shocks, currency moves, volatility spikes, and broader
macro-financial stress.

GPR Equity Observatory is my attempt to turn that problem into a reproducible
quant economics project. The central question is simple:

> Do emerging equity markets respond more strongly to geopolitical risk shocks
> than developed markets?

The project does not try to build a trading system. It studies risk
transmission. The aim is to build a transparent empirical workflow that can be
checked, extended, and explained.

## Data

The project uses 20 country ETF proxies: 10 developed market ETFs and 10
emerging market ETFs. ETF returns are daily log returns in US dollars. This is
not a perfect measure of local equity performance because it includes currency
effects, but it is practical and reproducible with public data.

Geopolitical risk is measured using the Caldara-Iacoviello GPR index. The
pipeline also includes no-key market controls: global equity returns, VIX
changes, oil changes, dollar returns, and US 10-year yield changes.

One small but important data detail is oil. WTI crude futures traded below zero
in April 2020, so oil cannot always be treated as a log return. The project uses
oil level changes instead.

## Methods

The project uses several methods because no single model is enough.

Event studies ask what happens around high-GPR shock dates. A raw event study
shows average ETF returns around shocks, while an abnormal-return event study
subtracts the return expected from a simple market model.

Panel regressions estimate the average association between GPR and returns,
including an interaction for emerging markets. The controlled model adds global
market, volatility, oil, dollar, and yield controls.

Quantile regressions ask whether GPR matters more during bad return states than
during normal days. This is important because the research question is about
asymmetry, not just average returns.

Local projections estimate the response path over later horizons after GPR
shock days.

Robustness checks rerun the event-study logic under different GPR shock
thresholds and event-window lengths. The panel robustness layer also reruns the
controlled regression after excluding the COVID crash and Russia-Ukraine
invasion windows.

A simple drawdown classifier asks whether current GPR and market conditions help
identify higher forward downside risk. It uses chronological validation rather
than random splits, because random splits are inappropriate for time-series
prediction.

## What The Current Results Say

The current evidence is mixed, which is useful.

The controlled panel regression finds a negative average association between
standardized GPR and ETF returns. However, the emerging-market interaction is
not statistically strong after controls. That means the current evidence does
not yet prove that emerging markets have a stronger average response.

The quantile regressions are directionally interesting. The GPR coefficient at
the 10th percentile is more negative than at the median, which is consistent
with downside concentration. But the p-values are not strong enough to treat
this as a firm result.

The local projections show small response estimates with wide confidence
intervals, especially for emerging markets.

The robustness results are useful but still cautious. Under the 90th-percentile
shock definition, emerging-market abnormal returns are more negative than
developed-market abnormal returns over the 10-day event window. But the
95th-percentile shock definition is less stable. In the panel sample checks,
the controlled GPR coefficient remains negative after excluding COVID and
Russia-Ukraine windows, while the emerging-market interaction becomes weaker.

The drawdown classifier has modest signal. Its mean ROC AUC is about 0.614, and
rolling volatility is the most important feature. GPR variables are small in the
current model.

## Why This Is Still A Useful Result

A project like this is stronger when it reports mixed evidence honestly. The
goal is not to force a dramatic conclusion. The goal is to build a credible
empirical platform.

The useful outcome is that the project now has:

- a reproducible data pipeline,
- tested data and feature logic,
- multiple empirical methods,
- robustness checks,
- a dashboard for interpretation,
- a research note,
- a technical appendix,
- a short generated results brief,
- and clear limitations.

That foundation makes it possible to add better macro controls, country-specific
GPR data, and eventually news-event features without losing the empirical
structure.

## Next Steps

The next step is not to add complexity for its own sake. The priority should be
better external data where it clearly improves interpretation: FRED macro
controls if an API key is available, and country-specific GPR where coverage is
reliable.

Only after that would I add a GDELT extension. News-event data could be useful,
but it is noisy and can easily distract from the main economics question.

The current conclusion is therefore careful: geopolitical risk is associated
with equity-market risk, but the emerging-versus-developed asymmetry is not yet
a settled result in this version. The project is valuable because it makes that
assessment reproducible.
