# GPR Equity Observatory Research Note

## Abstract

This project studies whether equity-market responses to geopolitical risk differ
between emerging and developed market ETF proxies. It builds a reproducible
Python pipeline using daily country ETF returns, daily Caldara-Iacoviello GPR
data, public market controls, event studies, panel regressions, quantile
regressions, local projections, rolling sensitivities, and a simple drawdown-risk
classifier.

The current evidence is mixed. Market-controlled regressions show a negative
average association between standardized GPR and ETF returns, but the emerging
market interaction is not statistically strong. Tail-risk estimates are
directionally consistent with stronger downside effects, but they are not yet
decisive. The strongest current contribution is the transparent empirical
pipeline rather than a single headline result.

## Research Question

The main question is:

> Do emerging equity markets respond more strongly, and more asymmetrically, to
> geopolitical risk shocks than developed equity markets?

The project tests this question through several complementary views:

- Event studies: what happens around high-GPR shock dates?
- Panel regressions: how are returns associated with GPR after controls?
- Quantile regressions: does GPR matter more in the left tail of returns?
- Local projections: how does the response path evolve over later horizons?
- Drawdown classification: do current risk conditions help identify future
  downside-risk episodes?

## Data

The country universe contains 20 ETF proxies: 10 developed markets and 10
emerging markets. ETF returns are daily log returns in US dollars. This makes the
data easy to reproduce and relevant for global-investor exposure, but it also
means the returns combine local equity-market performance and exchange-rate
movement against the dollar.

The geopolitical-risk source is the Caldara-Iacoviello daily GPR index. The
project uses the aggregate GPR index, the act and threat components where
available, and a high-GPR shock indicator based on the top 5 percent of the GPR
distribution.

The current market controls use public no-key proxies:

- ACWI: global equity return.
- VIX: change in risk aversion.
- WTI crude oil futures: daily level change.
- UUP: US dollar return.
- US 10-year yield proxy: daily level change.

Oil is not treated as a log return because WTI futures traded below zero in
April 2020. Using a level change avoids an invalid mathematical transformation.

## Methods

### Event Study

The event study selects high-GPR dates and separates events that are too close
together. It reports raw ETF return windows and market-model abnormal returns.
The abnormal-return version estimates a pre-event market model for each ETF:

```text
ETF return = alpha + beta * global market return + error
```

Expected returns from this model are subtracted from observed ETF returns inside
the event window.

### Panel Regression

The baseline panel regression estimates the association between ETF returns and
standardized GPR:

```text
return_it = GPR_t + GPR_t * emerging_i + ETF fixed effects + error_it
```

The controlled version adds global equity returns, VIX changes, oil changes,
dollar returns, and US 10-year yield changes.

The coefficient on `gpr_z` is the developed-market association. The coefficient
on `gpr_z:emerging_market` is the additional emerging-market association.

### Quantile Regression

Quantile regression estimates the GPR association at different points of the
return distribution. The lower quantiles are especially relevant because the
research question is about downside asymmetry, not only average returns.

### Local Projections

Local projections estimate cumulative return responses at horizons from 0 to 20
trading days after a GPR shock. This provides a response path rather than a
single event-window average.

### Drawdown Classifier

The drawdown classifier predicts whether an ETF experiences a forward
20-trading-day cumulative log-return drawdown of at least 5 percent. Validation
uses chronological folds, so the model always trains on earlier dates and tests
on later dates. This avoids the common mistake of randomly splitting time-series
data.

## Current Results

The controlled panel regression estimates the developed-market GPR coefficient
at about `-0.000064`, with a p-value around `0.006`. The emerging-market
interaction is positive at about `0.000090`, but the p-value is around `0.127`.
This means the current model suggests a negative average GPR association for
developed-market ETF returns, but it does not strongly support a differential
average response for emerging markets after controls.

The quantile regression results are more suggestive than conclusive. The
10th-percentile GPR coefficient is more negative than the median coefficient,
which is directionally consistent with downside concentration. However, the
p-values are not strong enough to describe this as a firm result.

The local projection estimates show small cumulative responses and wide
confidence intervals. Emerging-market response estimates are often larger but
less precise. This is useful as a diagnostic response path, not as a standalone
claim.

The drawdown classifier has a mean ROC AUC of about `0.614` and average
precision of about `0.370`, compared with a mean event rate of about `28.5%`.
This is modest predictive signal. Rolling volatility is the largest feature by
standardized coefficient. GPR features are small in the current classifier, so
the ML layer should be described as exploratory.

## Interpretation

The current evidence supports a cautious interpretation:

- GPR is associated with equity-market risk, but the sign and strength depend on
  model specification.
- The emerging-market asymmetry hypothesis is not yet strongly supported in the
  average controlled panel regression.
- Tail-risk and local-projection results are useful diagnostics, but they need
  robustness checks before they can carry the main conclusion.
- The ML model is useful for disciplined risk classification practice, but it is
  not a strong prediction engine.

The project should therefore be presented as a transparent empirical platform,
not as a finished proof of a single hypothesis.

## Limitations

ETF returns are imperfect proxies for local equity markets. They are practical
and reproducible, but they include currency exposure, ETF liquidity effects, and
global-investor pricing.

GPR shocks are not causal experiments. High GPR often coincides with oil shocks,
global risk-aversion shocks, monetary-policy news, and other macro-financial
events. Controls help, but they do not eliminate confounding.

The controlled sample begins in 2008 because ACWI data begin then. This removes
some earlier events from controlled models.

The current project uses global GPR, not country-specific GPR. Country-specific
GPR could change the interpretation of country-level sensitivity.

## Next Steps

The most useful next steps are:

- Add robustness checks for event windows and GPR shock thresholds.
- Add a compact table comparing baseline, controlled, quantile, and local
  projection results.
- Add FRED macro controls if an API key is available.
- Add country-specific GPR data where coverage is reliable.
- Delay GDELT until the core empirical story is clearer.

## Conclusion

GPR Equity Observatory now has the structure of a serious reproducible applied
economics project. The current empirical results are not a simple confirmation
of the emerging-market asymmetry hypothesis, but that is not a weakness. The
project is stronger because it reports mixed evidence clearly, documents
limitations, and gives a foundation for robustness checks and future extensions.
