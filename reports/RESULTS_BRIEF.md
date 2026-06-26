# GPR Equity Observatory Results Brief

## Main Takeaway

The controlled panel regression now estimates responses to daily GPR jumps. The clean H1 test is the date fixed-effects emerging-market interaction, which absorbs common global shocks and reports the within-date EM differential.
The older controlled interaction alone is not strong evidence of a reliably larger emerging-market response.

## Key Evidence

| Method | Estimate | p-value | Inference |
| --- | ---: | ---: | --- |
| Controlled panel regression | -0.4 bps | 0.325 | two-way clustered by ticker/date |
| Controlled emerging interaction | -0.5 bps | 0.574 | two-way clustered by ticker/date |
| Date fixed-effects emerging interaction | -0.6 bps | 0.563 | two-way clustered by ticker/date |
| Tail-risk quantile regression | -0.8 bps | 0.271 | i.i.d. QuantReg asymptotic p-value |
| Local projection developed | 0.010% | 0.858 | two-way clustered by ticker/date |
| Local projection emerging | -0.057% | 0.587 | two-way clustered by ticker/date |
| Drawdown classifier | 0.617 | n/a | cross-validation metric |

Local projection rows are market-model abnormal return responses, not raw cumulative ETF returns.
Prediction Lab treats the drawdown model as an out-of-sample risk-classification experiment, not as a trading signal.

## Sample Robustness

Under `Excluding COVID and Russia windows`, the controlled one-SD GPR-jump coefficient is -0.6 bps with p-value 0.190. The emerging interaction is -0.8 bps with p-value 0.419.

That means the main controlled GPR-jump coefficient is not only a COVID or Russia-Ukraine result. But the emerging-market asymmetry claim remains weak in the current specification.

## How To Explain This

- This is an empirical risk-response project, not a trading system.
- ETF returns are USD returns, so they include currency exposure.
- GPR jumps are not randomized events, so the results are associations.
- The date fixed-effects specification identifies the emerging-market differential, not a separate global GPR-jump coefficient.
- The best current conclusion is cautious: GPR jumps are linked to equity risk, but emerging-market asymmetry is not yet a strong finding.
