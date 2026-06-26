# GPR Equity Observatory Research Note

## Abstract

This project studies whether equity-market responses to geopolitical risk differ
between emerging and developed market ETF proxies. It builds a reproducible
Python pipeline using daily country ETF returns, daily Caldara-Iacoviello GPR
data, public market controls, event studies, panel regressions, quantile
regressions, local projections, rolling sensitivities, and a Prediction Lab for
drawdown-risk classification.

The repository also includes a separate monthly benchmark layer. That layer
uses deterministic sample mode for software validation and user-supplied real
mode for aggregate developed/emerging benchmark analysis. It is deliberately
kept separate from the daily ETF evidence.

The current evidence is mixed. Market-controlled regressions show small,
statistically weak average responses to standardized daily GPR jumps. The
date-fixed-effects interaction, which is the cleanest H1 test, does not show a
reliable emerging-market differential. Event studies are more suggestive in the
10-day window after 90th-percentile GPR jumps, but they are not decisive. The
strongest current contribution is the transparent empirical pipeline rather than
a single headline result.

## Research Question

The main question is:

> Do emerging equity markets respond more strongly, and more asymmetrically, to
> geopolitical risk shocks than developed equity markets?

The project tests this question through several complementary views:

- Event studies: what happens around large daily GPR jumps?
- Panel regressions: how are returns associated with GPR jumps after controls?
- Quantile regressions: does GPR matter more in the left tail of returns?
- Local projections: how does the market-adjusted response path evolve over
  later horizons?
- Prediction Lab: do current risk conditions help rank future downside-risk
  episodes out of sample?
- Monthly benchmark: do aggregate developed/emerging returns show a lower
  frequency benchmark association with monthly GPR changes?

## Data

The country universe contains 20 ETF proxies: 10 developed markets and 10
emerging markets. ETF returns are daily log returns in US dollars. This makes the
data easy to reproduce and relevant for global-investor exposure, but it also
means the returns combine local equity-market performance and exchange-rate
movement against the dollar.

The geopolitical-risk source is the Caldara-Iacoviello daily GPR index. The
project uses the aggregate GPR index, the act and threat components where
available, the daily GPR change, and a shock indicator based on top-decile
positive GPR jumps.

The current market controls use public no-key proxies:

- ACWI: global equity return.
- VIX: change in risk aversion.
- WTI crude oil futures: daily level change.
- UUP: US dollar return.
- US 10-year yield proxy: daily level change.

Oil is not treated as a log return because WTI futures traded below zero in
April 2020. Using a level change avoids an invalid mathematical transformation.

The monthly benchmark uses either deterministic sample mode or real mode. Sample
mode is not empirical evidence. Real mode uses user-supplied monthly
Caldara-Iacoviello GPR and Kenneth French developed/emerging factor files, with
local source hashes and redacted manifests.

## Methods

### Event Study

The event study selects large positive GPR-jump dates and separates events that
are too close together. It reports raw ETF return windows and market-model
abnormal returns.
The abnormal-return version estimates a pre-event market model for each ETF:

```text
ETF return = alpha + beta * global market return + error
```

Expected returns from this model are subtracted from observed ETF returns inside
the event window.

### Panel Regression

The baseline panel regression estimates the association between ETF returns and
standardized daily GPR changes:

```text
return_it = GPRChangeZ_t + GPRChangeZ_t * emerging_i + ETF fixed effects + error_it
```

The controlled version adds global equity returns, VIX changes, oil changes,
dollar returns, and US 10-year yield changes.

The coefficient on `gpr_change_z` is the developed-market response to a one-SD
GPR jump. The coefficient on `gpr_change_z:emerging_market` is the additional
emerging-market response.

The H1 specification adds date fixed effects:

```text
return_it = GPRChangeZ_t * emerging_i + ETF fixed effects + date fixed effects + error_it
```

With date fixed effects, the common daily GPR jump is absorbed. The identified
coefficient is therefore the within-date emerging-market differential, not a
standalone global GPR effect.

The sample-robustness version reruns the controlled panel model after excluding
major crisis windows. This checks whether the main coefficient is mostly driven
by a short crisis episode.

### Quantile Regression

Quantile regression estimates the GPR association at different points of the
return distribution. The lower quantiles are especially relevant because the
research question is about downside asymmetry, not only average returns.

### Local Projections

Local projections estimate cumulative market-model abnormal return responses at
horizons from 0 to 20 trading days after a GPR shock. For each ticker and base
date, the expected return path is estimated from pre-date ETF sensitivity to the
global market return, then subtracted from the forward ETF return path. This
keeps the response path aligned with the abnormal-return event-study design.
The developed row is the base GPR-shock response. The emerging row is the
combined emerging-market response, equal to the developed response plus the
emerging interaction, and its p-value is computed for that combined estimate.

### Prediction Lab

Prediction Lab predicts whether an ETF experiences a forward 20-trading-day
cumulative log-return drawdown of at least 5 percent. Validation uses purged
chronological folds, so the model always trains on earlier dates and tests on
later dates. This avoids the common mistake of randomly splitting time-series
data.

The saved predictions are out of sample. The model comparison includes
constant, volatility-only, GPR-only, market-controls-only, volatility-plus-GPR,
and full-feature variants. The diagnostics include Brier score, threshold
metrics, calibration by predicted-risk decile, top-bucket lift, and country risk
summaries.

### Evidence Summary

The pipeline also builds a compact evidence-summary table. This is not a new
model. It is a communication layer that places the main event-study, regression,
quantile, local-projection, and drawdown-classifier outputs in one table with
plain-English interpretation.

### Monthly Benchmark

The monthly benchmark builds an aggregate developed/emerging monthly panel. The
main benchmark regression uses the emerging-minus-developed forward return
spread and HAC standard errors. Forecast comparisons use expanding windows and
OOS R2 against a historical-mean benchmark.

This monthly layer is not a replacement for the daily ETF panel. With only two
aggregate markets, it cannot support credible country-clustered inference and
is not a country-panel proof.

## Current Results

The controlled panel regression estimates the developed-market GPR-jump
coefficient at about `-0.4` basis points per one-SD GPR jump, with a p-value
around `0.325`. The controlled emerging-market interaction is about `-0.5` basis
points, with a p-value around `0.574`. The date-fixed-effects H1 interaction is
also about `-0.6` basis points, with a p-value around `0.563`. This is a sharper
and more interpretable specification, but it does not strongly support a
differential average response for emerging markets.

The sample-robustness checks keep the controlled GPR-jump coefficient negative
after excluding the COVID-crash window, the Russia-Ukraine invasion window, or
both. Under the combined exclusion, the developed-market coefficient is about
`-0.6` basis points and the emerging interaction is about `-0.8` basis points,
but neither is statistically strong.

The quantile regression results are more suggestive than conclusive. The
10th-percentile GPR-jump coefficient is about `-0.8` basis points, which is
directionally consistent with downside concentration. However, the p-value is
around `0.271`, so this is not a firm result.

The abnormal-return local projection estimates now line up better with the
event-study framing. At the 20-day horizon, the developed-market estimate is
near zero at about `0.01%`, while the emerging-market estimate is negative at
about `-0.06%`. This is useful as a diagnostic response path, not as a
standalone claim.

Prediction Lab has modest ranking signal. The full-features model has mean ROC
AUC around `0.617`, average precision around `0.373`, and mean out-of-sample
base event rate around `28.6%`. Its top-decile lift is about `1.47x`.
Volatility-only and volatility-plus-GPR variants are similar, while `gpr_only`
is weak. The ML layer should therefore be described as exploratory risk
classification, not a trading signal or evidence that GPR alone predicts
drawdowns.

The event-study robustness checks compare 90th- and 95th-percentile GPR-jump
definitions across 3-, 5-, and 10-trading-day windows. The 90th-percentile jump
definition produces a more negative 10-day cumulative abnormal return for
emerging markets, around `-0.23%`, versus about `-0.12%` for developed markets.
The 95th-percentile jump definition is less supportive, with positive 10-day
abnormal returns in both groups. This is useful evidence, but it is not a clean
confirmation of the asymmetry hypothesis.

The compact evidence table makes the mixed evidence especially clear. The
baseline GPR-jump coefficient is positive, while the controlled panel
coefficient is negative, and the date-fixed-effects interaction is small and
statistically weak. That is an important warning against over-selling a single
headline result.

Monthly sample-mode results, when generated, should not be included as empirical
findings. Monthly real-mode benchmark outputs require user-supplied source files
and provenance checks before interpretation.

## Interpretation

The current evidence supports a cautious interpretation:

- GPR jumps are associated with equity-market risk, but the sign and strength
  depend on model specification.
- The emerging-market asymmetry hypothesis is not yet strongly supported in the
  average controlled or date-fixed-effects panel regression.
- Tail-risk, abnormal-return local-projection, and event-study robustness
  results are useful diagnostics, but they do not yet carry the main conclusion
  alone.
- Prediction Lab is useful for disciplined out-of-sample risk classification
  practice, but it is not a strong prediction engine or trading signal.
- The monthly benchmark is useful for reproducibility and aggregate comparison,
  but it should not be mixed with daily ETF findings or described as causal.

The project should therefore be presented as a transparent empirical platform,
not as a finished proof of a single hypothesis.

## Limitations

ETF returns are imperfect proxies for local equity markets. They are practical
and reproducible, but they include currency exposure, ETF liquidity effects, and
global-investor pricing.

### Identification

GPR shocks are not causal experiments. Large GPR jumps often coincide with oil
shocks, global risk-aversion shocks, monetary-policy news, and other
macro-financial events. Market controls help, and date fixed effects absorb
common daily shocks, but they do not eliminate every source of confounding.

The event-study timing should also be interpreted carefully. A news-based GPR
jump can reflect information that markets partly anticipated before the event
date, or information that arrived after a local market close. The event date is
therefore a disciplined anchor, not proof that the shock was fully unanticipated.

ETF returns are USD returns. This is appropriate for a global investor, but it
means the measured response combines local equity returns and exchange-rate
movements against the dollar. Some apparent emerging-market sensitivity can
therefore be currency exposure rather than pure equity-market risk transmission.

The controlled sample begins in 2008 because ACWI data begin then. This removes
some earlier events from controlled models.

The current project uses global GPR, not country-specific GPR. Country-specific
GPR could change the interpretation of country-level sensitivity.

The monthly real workflow is local only by default. Source configs, raw inputs,
and real generated outputs are not committed unless a separate data-publication
decision is made.

## Next Steps

The most useful next steps are:

- Add FRED macro controls if an API key is available.
- Add validated real macro controls to the monthly benchmark if source coverage
  is strong enough.
- Add country-specific GPR data where coverage is reliable.
- Delay GDELT until the core empirical story is clearer.

## Conclusion

GPR Equity Observatory now has the structure of a serious reproducible applied
economics project. The current empirical results are not a simple confirmation
of the emerging-market asymmetry hypothesis, but that is not a weakness. The
project is stronger because it reports mixed evidence clearly, documents
limitations, and gives a foundation for robustness checks and future extensions.
