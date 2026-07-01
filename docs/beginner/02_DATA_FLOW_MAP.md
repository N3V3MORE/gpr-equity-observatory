# 02 - Data Flow Map

This file explains what each major output means.

## Required original inputs

| Input | Plain meaning | Why it exists |
|---|---|---|
| `data/country_universe.csv` | List of country ETFs | Tells the project which markets to study |
| Caldara-Iacoviello daily GPR file | Geopolitical risk index | Main risk variable |
| Yahoo Finance ETF prices | ETF market prices | Used to calculate country ETF returns |
| Yahoo Finance market controls | Global market context | Used so regressions are not only GPR versus returns |

## Core generated files

| Output file | Plain meaning | Beginner page |
|---|---|---|
| `gpr_daily.csv` | Daily geopolitical risk data | GPR Data |
| `returns_panel.csv` | ETF daily returns | Market Reaction |
| `market_controls.csv` | Global control variables | Regression Results |
| `analysis_panel.csv` | GPR plus ETF returns merged together | Start Here, Regression Results |
| `group_return_summary.csv` | Average returns by developed and emerging markets | Market Reaction |

## Event-study files

| Output file | Plain meaning | Beginner page |
|---|---|---|
| `event_study_summary.csv` | Raw market returns around GPR shock days | Market Reaction |
| `event_study_abnormal_summary.csv` | Market returns after removing normal market movement | Market Reaction |
| `event_robustness_summary.csv` | Same event test using different windows and shock definitions | Advanced expander |

## Regression files

| Output file | Plain meaning | Beginner page |
|---|---|---|
| `panel_regression_baseline.csv` | Basic regression | Technical expander |
| `panel_regression_controlled.csv` | Regression with controls | Regression Results |
| `panel_regression_date_fe.csv` | Cleaner developed versus emerging comparison | Regression Results |
| `panel_sample_robustness.csv` | Checks if result depends on crisis windows | Regression Results |
| `quantile_regression_results.csv` | Checks worse return days separately | Regression Results |
| `local_projection_results.csv` | Shows response path after shocks | Market Reaction or Regression Results |

## Prediction files

| Output file | Plain meaning | Beginner page |
|---|---|---|
| `drawdown_model_metrics.csv` | How well the drawdown risk model ranks risk | Prediction Lab |
| `drawdown_model_predictions.csv` | Prediction rows by date and ETF | Technical expander |
| `drawdown_model_threshold_metrics.csv` | Precision and recall at thresholds | Technical expander |
| `drawdown_model_calibration.csv` | Whether predicted probabilities match real rates | Technical expander |
| `drawdown_model_lift.csv` | Whether top-risk buckets have more drawdowns | Prediction Lab |
| `drawdown_country_risk_summary.csv` | Average risk by country | Prediction Lab |
| `drawdown_feature_importance.csv` | Which variables matter most in the model | Prediction Lab |

## Data quality files

| Output file | Plain meaning | Beginner page |
|---|---|---|
| `large_return_flags.csv` | Suspiciously large ETF return days | Data Quality |
| `rolling_gpr_beta.csv` | Rolling country sensitivity to GPR | Data Quality or Advanced |
| `evidence_summary.csv` | Compact evidence table | Start Here |

## Beginner interpretation rule

Never show a raw file first.

Show a readable table first.
Then put the raw file in an expander.
