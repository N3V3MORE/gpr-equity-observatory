# GPR Equity Observatory Results Brief

## Main Takeaway

This brief describes the generated evidence-summary and sample-robustness outputs below. A separately published snapshot may differ; use its displayed estimates and uncertainty before applying this narrative to that snapshot.
The controlled panel estimates conditional associations with daily GPR jumps. The date fixed-effects interaction reports the within-date emerging-market differential after absorbing common date shocks; it does not identify a separate global GPR coefficient.
Weak statistical evidence is not proof of no effect. Neither an estimate's sign nor a single specification establishes a reliably larger emerging-market response.

## Key Evidence

| Method | Estimate | p-value | Inference |
| --- | ---: | ---: | --- |
| Controlled panel regression | -0.4 bps | 0.325 | two-way clustered by ticker/date |
| Controlled emerging interaction | -0.5 bps | 0.574 | two-way clustered by ticker/date |
| Date fixed-effects emerging interaction | -0.6 bps | 0.563 | two-way clustered by ticker/date |
| Tail-risk quantile regression | -0.8 bps | 0.271 | i.i.d. QuantReg asymptotic p-value |
| Local projection developed | 0.010% | 0.858 | two-way clustered by ticker/date |
| Local projection emerging | -0.057% | 0.692 | two-way clustered by ticker/date |
| Drawdown classifier | 0.617 | n/a | cross-validation metric |

Local projection rows are market-model abnormal return responses, not raw cumulative ETF returns.
Prediction Lab treats the drawdown model as an out-of-sample risk-classification experiment, not as a trading signal.
Event-study cumulative abnormal returns elsewhere in the dashboard start at each ETF-event's earliest observed relative day, normally the negative window boundary, and include pre-event returns. They are not day-0-onward returns. Their standard errors and t-test p-values are not adjusted for dependence between ETFs exposed to common events; no event-study confidence intervals are supplied here.

## Known Raw Event-Window Limitation (Unchanged)

The raw event-window builder can map an event before an ETF's first observation to that first observation, even when the event occurred years earlier. Raw event counts and returns can therefore include events predating the ETF's observed history. Correcting this requires a separate research change; this presentation patch leaves the estimator and its outputs unchanged. The primary abnormal-return study rejects these cases through its estimation-history requirement, so this particular mapping defect does not affect its table.

## Sample Robustness

Under `Excluding COVID and Russia windows`, the controlled one-SD GPR-jump coefficient is -0.6 bps with p-value 0.190. The emerging interaction is -0.8 bps with p-value 0.419.

These estimates describe a changed sample. Retaining the same sign after excluding crisis windows does not establish a robust GPR association: compare the magnitude, p-value, uncertainty and sample definition with the full-sample result.

## How To Explain This

- This is an empirical risk-response project, not a trading system.
- Country ETFs are USD market proxies, not local equity indexes; their returns include currency exposure.
- GPR jumps are not randomized events, so the results are associations.
- The date fixed-effects specification identifies the emerging-market differential, not a separate global GPR-jump coefficient.
- Conclusions should track the estimates and uncertainty in the displayed snapshot. Weak evidence is not proof of no effect, and these associations do not establish causality.
