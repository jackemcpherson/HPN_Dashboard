import sqlite3
from typing import List, Tuple

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


def load_data_from_db() -> pd.DataFrame:
    with sqlite3.connect("HPN_Data.db") as conn:
        return pd.read_sql_query("SELECT * FROM PlayerRatings2023", conn)


def sort_data_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return df.sort_values(by=column, ascending=True)


def create_bar_chart(
    df: pd.DataFrame, pav_type: str, selected_teams: List[str] = None
) -> go.Figure:
    if selected_teams:
        opacity = [0.6 if tm in selected_teams else 0.1 for tm in df["TM"]]
        hovertemplate = [
            f"{player}<br>{pav_value}<br>{tm}" if tm in selected_teams else None
            for player, pav_value, tm in zip(df["Player"], df[pav_type], df["TM"])
        ]
    else:
        opacity = [0.6] * len(df)
        hovertemplate = [
            f"{player}<br>{pav_value}<br>{tm}"
            for player, pav_value, tm in zip(df["Player"], df[pav_type], df["TM"])
        ]

    trace = go.Bar(
        x=df["Player"],
        y=df[pav_type],
        name="",
        marker=dict(opacity=opacity),
        hovertemplate=hovertemplate,
        hoverinfo="text",
        showlegend=False,
    )

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(trace)
    fig.update_layout(
        title=f"AFL Player Ratings 2023: {pav_type.replace('_', ' ')}",
        xaxis_title="Player",
        xaxis=dict(showticklabels=False),
        yaxis_title=pav_type.replace("_", " "),
    )

    return fig


app = dash.Dash(__name__)

initial_data = load_data_from_db()
sorted_by_total_pav = sort_data_by(initial_data, "Total_PAV")
initial_fig = create_bar_chart(sorted_by_total_pav, "Total_PAV")

team_options = sorted(
    [
        {"label": TEAM_LOOKUP[team], "value": team}
        for team in initial_data["TM"].unique()
    ],
    key=lambda x: x["label"],
)
pav_options = [
    {"label": "Total PAV", "value": "Total_PAV"},
    {"label": "Defensive PAV", "value": "Def_PAV"},
    {"label": "Offensive PAV", "value": "Off_PAV"},
    {"label": "Midfield PAV", "value": "Mid_PAV"},
]

app.layout = html.Div(
    [
        dcc.Graph(id="bar-chart", figure=initial_fig),
        dcc.Dropdown(
            id="team-slicer",
            options=team_options,
            value=[],
            placeholder="Select Teams",
            multi=True,
        ),
        dcc.Dropdown(
            id="pav-type-selector",
            options=pav_options,
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
    data = load_data_from_db()
    sorted_data = sort_data_by(data, selected_pav_type)
    return create_bar_chart(sorted_data, selected_pav_type, selected_teams)


if __name__ == "__main__":
    app.run_server(debug=True)
