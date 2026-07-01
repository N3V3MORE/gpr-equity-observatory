# 00 - Start Here

This is the beginner restart plan.

## The problem

The original project works like a serious applied economics project, but the user-facing page is too hard to understand.

The dashboard shows too many raw outputs before explaining what they mean.

## The fix

Keep the serious engine.
Rebuild the front page slowly.

In this repository, the public app still lives in `frontend/`. The restart
files below are a local beginner dashboard and cockpit so a new reader can
understand the project before opening the deeper research folders.

## New files

```text
app_restart.py
```

The beginner dashboard. This is where we build the user-facing version step by step.

```text
app_dev_cockpit.py
```

The developer cockpit. This is where you can run steps, see logs, see file status, and preview outputs.

```text
docs/beginner/
```

Plain-English architecture, table design, and agent task cards.

## The restart order

1. Home page
2. Files used table
3. GPR data page
4. Market reaction page
5. Regression translation page
6. Prediction Lab translation page
7. Data quality page
8. Monthly benchmark page
9. Advanced raw tables hidden in expanders

## The rule

One step equals one visible thing.

Do not add the next page until the current page makes sense.
