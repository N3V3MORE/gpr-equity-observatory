import pandas as pd


EVENT_WINDOW_COLUMNS = [
    "event_date",
    "event_trading_date",
    "relative_day",
    "date",
    "ticker",
    "country",
    "market_group",
    "region",
    "return",
]

EVENT_SUMMARY_COLUMNS = [
    "market_group",
    "relative_day",
    "average_return",
    "cumulative_average_return",
    "observation_count",
    "event_count",
]


def select_spaced_events(
    gpr: pd.DataFrame,
    min_gap_days: int = 20,
    shock_column: str = "gpr_shock",
) -> pd.Series:
    """Select shock dates while avoiding clusters of nearby shocks."""
    shock_dates = gpr.loc[gpr[shock_column], "date"].sort_values()

    selected_dates = []
    last_selected = None
    for date in shock_dates:
        date = pd.Timestamp(date)
        if last_selected is None or (date - last_selected).days >= min_gap_days:
            selected_dates.append(date)
            last_selected = date

    return pd.Series(selected_dates, name="event_date")


def build_event_windows(
    panel: pd.DataFrame,
    event_dates: pd.Series,
    window: int = 5,
) -> pd.DataFrame:
    """Build ticker-level return windows around each GPR shock date."""
    frames = []

    for _, ticker_panel in panel.groupby("ticker"):
        ticker_panel = ticker_panel.sort_values("date").reset_index(drop=True)
        trading_dates = ticker_panel["date"]

        for event_date in event_dates:
            event_date = pd.Timestamp(event_date)
            event_position = trading_dates.searchsorted(event_date, side="left")
            if event_position >= len(ticker_panel):
                continue

            start_position = max(event_position - window, 0)
            end_position = min(event_position + window + 1, len(ticker_panel))

            event_window = ticker_panel.iloc[start_position:end_position].copy()
            event_window.insert(0, "event_date", event_date)
            event_window.insert(1, "event_trading_date", trading_dates.iloc[event_position])
            event_window.insert(
                2,
                "relative_day",
                list(range(start_position - event_position, end_position - event_position)),
            )
            frames.append(event_window)

    if not frames:
        return pd.DataFrame(columns=EVENT_WINDOW_COLUMNS)

    windows = pd.concat(frames, ignore_index=True)
    return windows[EVENT_WINDOW_COLUMNS]


def summarize_event_windows(windows: pd.DataFrame) -> pd.DataFrame:
    """Average event-window returns by market group and relative day."""
    if windows.empty:
        return pd.DataFrame(columns=EVENT_SUMMARY_COLUMNS)

    summary = (
        windows.groupby(["market_group", "relative_day"], as_index=False)
        .agg(
            average_return=("return", "mean"),
            observation_count=("return", "count"),
            event_count=("event_date", "nunique"),
        )
        .sort_values(["market_group", "relative_day"])
        .reset_index(drop=True)
    )
    summary["cumulative_average_return"] = summary.groupby("market_group")[
        "average_return"
    ].cumsum()
    return summary[EVENT_SUMMARY_COLUMNS]
