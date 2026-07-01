# 03 - User-Facing Tables

The main readability problem is table design.

The serious project has technical tables.
The beginner project needs translation tables.

## Table rule

Every table must answer a question.

Bad table title:

```text
panel_regression_controlled.csv
```

Good table title:

```text
Does GPR still matter after market controls?
```

## Table 1: Project Summary Table

Page: Start Here

Columns:

```text
Question
Simple answer
Evidence used
How to read it
What this means
What not to claim
```

Example rows:

| Question | Simple answer | Evidence used | How to read it | What this means | What not to claim |
|---|---|---|---|---|---|
| Does GPR spike around major events? | Yes | GPR daily index | Input source is documented | The risk index jumps on some major event days | This does not show market impact |
| Do markets react after GPR shocks? | Mixed | Event study and regressions | Compare methods before concluding | Some evidence points negative, but not clean enough to overclaim | Do not say markets always fall |
| Do emerging markets react more? | Not clearly | Date fixed-effects regression | Treat as limited evidence | Current evidence does not clearly support extra EM impact | Do not claim EM asymmetry is settled |
| Can the model rank drawdown risk? | Exploratory | Prediction Lab | Risk-ranking experiment only | It ranks some risk, but not enough for decisions | Do not call it a trading signal |

## Table 2: Files Used Table

Page: Start Here

Columns:

```text
File
What it contains
Why we need it
When it changes
Beginner meaning
```

## Table 3: GPR Shock Table

Page: GPR Data

Columns:

```text
Date
GPR level
Daily jump
Threat risk
Actual event risk
Event label
Plain-English note
```

## Table 4: Market Reaction Table

Page: Market Reaction

Columns:

```text
Market group
Days after shock
Average abnormal return
Direction
Evidence strength
Plain-English note
```

## Table 5: Regression Translation Table

Page: Regression Results

Columns:

```text
Test
What it checks
Direction
P-value
Evidence strength
Plain-English note
```

## Table 6: Prediction Lab Translation Table

Page: Prediction Lab

Columns:

```text
Model
What it tries to do
Score
Usefulness
Plain-English note
```

## How to handle p-values

Use this simple mapping:

| P-value | Label | Plain meaning |
|---:|---|---|
| below 0.05 | Conventional p < 0.05 | Often treated as statistically notable |
| 0.05 to 0.10 | Suggestive p < 0.10 | Interesting, but not enough alone |
| above 0.10 | Weak in this run | Do not use as a headline finding |

## How to handle model AUC

Use this simple mapping:

| AUC | Label | Plain meaning |
|---:|---|---|
| below 0.60 | Weak ranking | Not much reliable ranking in this run |
| 0.60 to 0.70 | Limited ranking | Better than random, but limited |
| above 0.70 | Clearer ranking | Clearer than the weaker variants, still not a trading rule |

## Raw tables

Raw tables should be hidden like this:

```python
with st.expander("Show raw technical table"):
    st.dataframe(raw_table, use_container_width=True, hide_index=True)
```
