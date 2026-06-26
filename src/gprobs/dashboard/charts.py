import pandas as pd
import plotly.express as px


def build_gpr_shock_timeline(gpr: pd.DataFrame):
    timeline = gpr.sort_values("date")
    top_shocks = gpr.sort_values("gpr_change", ascending=False).head(25)
    fig = px.line(timeline, x="date", y="gpr", title="GPR Index With Top Shock Dates")
    fig.add_scatter(
        x=top_shocks["date"],
        y=top_shocks["gpr"],
        mode="markers",
        name="Top GPR changes",
        customdata=top_shocks[["gpr_change", "event"]],
        hovertemplate=(
            "Date=%{x}<br>GPR=%{y}<br>GPR change=%{customdata[0]}"
            "<br>Event=%{customdata[1]}<extra></extra>"
        ),
    )
    return fig
