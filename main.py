import os
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


def load_data_from_db() -> pd.DataFrame:
    with sqlite3.connect("HPN_Data.db") as conn:
        return pd.read_sql_query("SELECT * FROM PlayerRatings2023", conn)


data = load_data_from_db()


def sort_data_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return df.sort_values(by=column, ascending=True)


def create_bar_chart(
    df: pd.DataFrame, pav_type: str, selected_players: List[str] = None
) -> go.Figure:
    if selected_players:
        opacity = [
            0.6 if player in selected_players else 0.1 for player in df["Player"]
        ]
        hovertemplate = [
            f"{player}<br>{pav_value}<br>{tm}" if player in selected_players else None
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


def build_team_options() -> List[dict]:
    return sorted(
        [{"label": TEAM_LOOKUP[team], "value": team} for team in data["TM"].unique()],
        key=lambda x: x["label"],
    )


def build_pav_options() -> List[dict]:
    return [
        {"label": "Total PAV", "value": "Total_PAV"},
        {"label": "Defensive PAV", "value": "Def_PAV"},
        {"label": "Offensive PAV", "value": "Off_PAV"},
        {"label": "Midfield PAV", "value": "Mid_PAV"},
    ]


def build_player_options() -> List[dict]:
    return [
        {"label": player, "value": player} for player in sorted(data["Player"].unique())
    ]


team_options = build_team_options()
pav_options = build_pav_options()
initial_fig = create_bar_chart(sort_data_by(data, "Total_PAV"), "Total_PAV")

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Select Ranking Metric"),
                        dcc.Dropdown(
                            id="pav-type-selector",
                            options=pav_options,
                            value="Total_PAV",
                            placeholder="Select PAV Type",
                            multi=False,
                        ),
                        html.Label("Select Teams"),
                        dcc.Dropdown(
                            id="team-slicer",
                            options=team_options,
                            value=[],
                            placeholder="Select Teams",
                            multi=True,
                        ),
                        html.Label("Select Players"),
                        dcc.Dropdown(
                            id="player-slicer",
                            options=build_player_options(),
                            value=[],
                            placeholder="Select Players",
                            multi=True,
                        ),
                    ],
                    style={"width": "30%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        dcc.Graph(id="bar-chart", figure=initial_fig),
                    ],
                    style={"width": "70%", "display": "inline-block"},
                ),
            ],
            style={"display": "flex", "flexDirection": "row"},
        ),
        html.Div([], style={"height": "20px"}),
        html.Div([]),
    ]
)


@app.callback(
    Output("bar-chart", "figure"),
    [
        Input("team-slicer", "value"),
        Input("pav-type-selector", "value"),
        Input("player-slicer", "value"),
    ],
)
def update_bar_chart(
    selected_teams: List[str], selected_pav_type: str, selected_players: List[str]
) -> go.Figure:
    sorted_data = sort_data_by(data, selected_pav_type)
    return create_bar_chart(sorted_data, selected_pav_type, selected_players)


@app.callback(
    Output("player-slicer", "value"),
    [Input("team-slicer", "value")],
)
def update_player_selection(selected_teams: List[str]):
    if selected_teams:
        filtered_data = data[data["TM"].isin(selected_teams)]
        return sorted(filtered_data["Player"].unique())
    else:
        return []


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=True, host="0.0.0.0", port=port)
