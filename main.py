import sqlite3
from typing import List

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from plotly.subplots import make_subplots

TEAM_LOOKUP = {
    "AD": "Adelaide Crows",
    "BL": "Brisbane Lions",
    "CA": "Carlton Blues",
    "CW": "Collingwood Magpies",
    "ES": "Essendon Bombers",
    "FR": "Fremantle Dockers",
    "GE": "Geelong Cats",
    "GC": "Gold Coast Suns",
    "GW": "Greater Western Sydney Giants",
    "HW": "Hawthorn Hawks",
    "ME": "Melbourne Demons",
    "NM": "North Melbourne Kangaroos",
    "PA": "Port Adelaide Power",
    "RI": "Richmond Tigers",
    "SK": "St Kilda Saints",
    "SY": "Sydney Swans",
    "WB": "Western Bulldogs",
    "WC": "West Coast Eagles",
}


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
            options=sorted(
                [
                    {"label": TEAM_LOOKUP[team], "value": team}
                    for team in df_sorted["TM"].unique()
                ],
                key=lambda x: x["label"],
            ),
            value=[],
            placeholder="Select Teams",
            multi=True,
        ),
        dcc.Dropdown(
            id="pav-type-selector",
            options=[
                {"label": "Total PAV", "value": "Total_PAV"},
                {"label": "Defensive PAV", "value": "Def_PAV"},
                {"label": "Offensive PAV", "value": "Off_PAV"},
                {"label": "Midfield PAV", "value": "Mid_PAV"},
            ],
            value="Total_PAV",
            placeholder="Select PAV Type",
            multi=False,
        ),
    ]
)


@app.callback(
    Output("bar-chart", "figure"),
    [Input("team-slicer", "value"), Input("pav-type-selector", "value")],
)
def update_bar_chart(selected_teams: List[str], selected_pav_type: str) -> go.Figure:
    # Sorting dataframe based on the selected PAV type
    df_sorted_by_pav_type = df_sorted.sort_values(by=selected_pav_type, ascending=True)

    if selected_teams:
        opacity = [
            0.6 if tm in selected_teams else 0.1 for tm in df_sorted_by_pav_type["TM"]
        ]
        hovertemplate = [
            f"{player}<br>{pav_value}<br>{tm}" if tm in selected_teams else None
            for player, pav_value, tm in zip(
                df_sorted_by_pav_type["Player"],
                df_sorted_by_pav_type[selected_pav_type],
                df_sorted_by_pav_type["TM"],
            )
        ]
    else:
        opacity = [0.6] * len(df_sorted_by_pav_type)
        hovertemplate = [
            f"{player}<br>{pav_value}<br>{tm}"
            for player, pav_value, tm in zip(
                df_sorted_by_pav_type["Player"],
                df_sorted_by_pav_type[selected_pav_type],
                df_sorted_by_pav_type["TM"],
            )
        ]

    updated_trace = go.Bar(
        x=df_sorted_by_pav_type["Player"],
        y=df_sorted_by_pav_type[selected_pav_type],
        name="",
        marker=dict(opacity=opacity),
        hovertemplate=hovertemplate,
        hoverinfo="text",
        showlegend=False,
    )

    updated_fig = make_subplots(rows=1, cols=1)
    updated_fig.add_trace(updated_trace)
    updated_fig.update_layout(
        title=f"AFL Player Ratings 2023: {selected_pav_type.replace('_', ' ')}",
        xaxis_title="Player",
        xaxis=dict(showticklabels=False),
        yaxis_title=selected_pav_type.replace("_", " "),
    )

    return updated_fig


if __name__ == "__main__":
    app.run_server(debug=True)
