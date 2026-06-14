# GPR Equity Observatory Results Brief

## Main Takeaway

The controlled panel regression now estimates responses to daily GPR jumps. The clean H1 test is the date fixed-effects emerging-market interaction, which absorbs common global shocks and reports the within-date EM differential.
The older controlled interaction alone is not strong evidence of a reliably larger emerging-market response.

## Key Evidence

| Method | Estimate | p-value |
| --- | ---: | ---: |
| Controlled panel regression | -0.4 bps | 0.328 |
| Controlled emerging interaction | -0.6 bps | 0.551 |
| Date fixed-effects emerging interaction | -0.6 bps | 0.557 |
| Tail-risk quantile regression | -0.8 bps | 0.280 |
| Local projection developed | 0.246% | <0.001 |
| Local projection emerging | 0.128% | 0.128 |
| Drawdown classifier | 0.612 | n/a |

## Sample Robustness

Under `Excluding COVID and Russia windows`, the controlled one-SD GPR-jump coefficient is -0.6 bps with p-value 0.194. The emerging interaction is -0.8 bps with p-value 0.396.

That means the main controlled GPR-jump coefficient is not only a COVID or Russia-Ukraine result. But the emerging-market asymmetry claim remains weak in the current specification.

## How To Explain This

- This is an empirical risk-response project, not a trading system.
- ETF returns are USD returns, so they include currency exposure.
- GPR jumps are not randomized events, so the results are associations.
- The date fixed-effects specification identifies the emerging-market differential, not a separate global GPR-jump coefficient.
- The best current conclusion is cautious: GPR jumps are linked to equity risk, but emerging-market asymmetry is not yet a strong finding.
