import dash
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from plotly.subplots import make_subplots


# Load and sort the DataFrame by 'Total PAV' in descending order
def get_player_data() -> pd.DataFrame:
    conn = sqlite3.connect("HPN_Data.db")
    df = pd.read_sql_query("SELECT * FROM PlayerRatings2023", conn)
    conn.close()
    df_sorted = df.sort_values("Total_PAV", ascending=True)
    return df_sorted


df_sorted = get_player_data()

app = dash.Dash(__name__)

fig = make_subplots(rows=1, cols=1)
trace = go.Bar(
    x=df_sorted["Player"], y=df_sorted["Total_PAV"], name="Total PAV", opacity=1
)
fig.add_trace(trace)

fig.update_layout(
    title="AFL Player Ratings 2023: Total PAV",
    xaxis_title="Player",
    xaxis=dict(showticklabels=False),
    yaxis_title="Total PAV",
)

app.layout = html.Div(
    [
        dcc.Graph(id="bar-chart", figure=fig),
        dcc.Dropdown(
            id="team-slicer",
            options=[
                {"label": team, "value": team} for team in df_sorted["TM"].unique()
            ],
            value=None,
            placeholder="Select a Team",
            multi=False,
        ),
    ]
)


@app.callback(Output("bar-chart", "figure"), [Input("team-slicer", "value")])
def update_bar_chart(selected_team: str) -> go.Figure:
    if selected_team:
        opacity = [0.6 if tm == selected_team else 0.1 for tm in df_sorted["TM"]]
        hovertemplate = [
            f"{player}<br>{total_pav}" if tm == selected_team else "<extra></extra>"
            for player, total_pav, tm in zip(
                df_sorted["Player"], df_sorted["Total_PAV"], df_sorted["TM"]
            )
        ]
    else:
        opacity = [1] * len(df_sorted)
        hovertemplate = [
            f"{player}<br>{total_pav}"
            for player, total_pav in zip(df_sorted["Player"], df_sorted["Total_PAV"])
        ]

    updated_trace = go.Bar(
        x=df_sorted["Player"],
        y=df_sorted["Total_PAV"],
        name="",
        marker=dict(opacity=opacity),
        hovertemplate=hovertemplate,
        hoverinfo="text",
        showlegend=False,
    )

    updated_fig = make_subplots(rows=1, cols=1)
    updated_fig.add_trace(updated_trace)
    updated_fig.update_layout(
        title="AFL Player Ratings 2023: Total PAV",
        xaxis_title="Player",
        xaxis=dict(showticklabels=False),
        yaxis_title="Total PAV",
    )

    return updated_fig


if __name__ == "__main__":
    app.run_server(debug=True)
