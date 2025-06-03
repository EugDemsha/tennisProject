from dash import Dash, html, dcc, callback, Output, Input
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from visualizing.utils import (list_tournaments,
                               list_matches_for_tournament,
                               get_match_stats,
                               get_players_in_tournament,
                               get_player_stats_across_matches,
                               get_player_stat_values,
                               list_players,
                               engine)
from sqlmodel import Session, select
from db import Player, Tournament

english_terms_dict = {
    "first_serve": "% попаданий 1-ой подачи",
    "first_serve_points_won": "% выигранной 1-ой подачи",
    "second_serve_points_won": "% выигранной 2-ой подачи",
    "break_points_saved": "% спасенных брейк-пойнтов",
    "first_serve_return_points_won": "% побед на приеме 1-ой подачи",
    "second_serve_return_points_won": "% побед на приеме 2-ой подачи",
    "break_points_converted": "% реализованных брейк-пойнтов",
    "net_points_won": "% выигранных очков у сетки",
    "service_points_won": "% побед на подаче",
    "return_points_won": "% побед на приеме",
    "total_points_won": "% побед",
    "aces": "подачи навылет",
    "double_faults": "двойные ошибки",
    "winners": "активно выигранные",
    "unforced_errors": "невынужденные ошибки",
}

def get_swap_dict(d):
    return {v: k for k, v in d.items()}

russian_terms_dict = get_swap_dict(english_terms_dict)

app = Dash()

# Requires Dash 2.17.0 or later
app.layout = html.Div(
    children=[
        html.H1('Tennis Statistics', style={'textAlign': 'center', 'color': '#333'}),

        html.Div([
            html.H2("Анализ турнира"),
            html.H3("Турнир"),
            dcc.Dropdown(
                options=[{'label': i[1], 'value': i[0]} for i in list_tournaments()],
                id='tournament-dropdown',
                value=1,
                style={
                        'backgroundColor': '#f1f2eb',
                        'color': '#000',
                        'border': '1px solid #999',
                        'fontFamily': 'Helvetica'
                        },
            ),

            html.H3("Игрок"),
            dcc.Dropdown(id='player-dropdown',
                         value=1,
                         style={
                             'backgroundColor': '#f1f2eb',
                             'color': '#000',
                             'border': '1px solid #999',
                         }
                         ),
            html.Div(
                dcc.Graph(id='line-plot'),
            ),

            html.H3("Матч"),
            dcc.Dropdown(id='match-dropdown',
                         value=1,
                         style={
                             'backgroundColor': '#f1f2eb',
                             'color': '#000',
                             'border': '1px solid #999',
                         }
                         ),

            dcc.Graph(id='spider-plot'),

            html.Hr(),
            html.H2("Анализ игрока"),
            html.H3("Игрок"),
            dcc.Dropdown(id='player-scatter-dropdown',
                         options=[{'label': i[1], 'value': i[0]} for i in list_players()],
                         value=1,
                         style={
                             'backgroundColor': '#f1f2eb',
                             'color': '#000',
                             'border': '1px solid #999',
                         }
                         ),
            html.H3("Первая метрика"),
            dcc.Dropdown(id='stat1-dropdown',
                         options=list(russian_terms_dict.keys()),
                         value="% побед на подаче",
                         style={
                             'backgroundColor': '#f1f2eb',
                             'color': '#000',
                             'border': '1px solid #999',
                         }
                         ),
            html.H3("Вторая метрика"),
            dcc.Dropdown(id='stat2-dropdown',
                         options=list(russian_terms_dict.keys()),
                         value="% побед на приеме",
                         style={
                             'backgroundColor': '#f1f2eb',
                             'color': '#000',
                             'border': '1px solid #999',
                         }
                         ),

            dcc.Graph(id='scatter-plot'),
            dcc.Graph(id='stat-violin'),
            # dcc.Graph(id='stat2-violin'),

        ], style={
            'maxWidth': '1000px',
            'margin': '0 auto',
            'padding': '20px',
        })
    ],
    style={
        'backgroundColor': '#f1f2eb',
        'minHeight': '100vh',
        'padding': '20px',
        'fontFamily': 'Helvetica'
    }
)
@callback(
    Output('match-dropdown', 'options'),
    Input('tournament-dropdown', 'value')
)
def set_player_options(selected_tournament):
    return [{'label': i[1], 'value': i[0]} for i in list_matches_for_tournament(selected_tournament)]

@callback(
    Output('spider-plot', 'figure'),
    Input('match-dropdown', 'value')
)
def plot_spider_for_match(match_id):
    print(match_id)
    df = get_match_stats(match_id)
    print(df)

    categories = [
        "first_serve", "first_serve_points_won",
        "second_serve_points_won", "break_points_saved",
        "first_serve_return_points_won", "second_serve_return_points_won",
        "break_points_converted", "net_points_won",
        "service_points_won", "return_points_won", "total_points_won"
    ]

    df["radar_area"] = df[categories].sum(axis=1)
    df_sorted = df.sort_values("radar_area", ascending=False)

    fig = go.Figure()

    custom_colors = ["#a13920", "#33658a"]

    for i, (_, row) in enumerate(df_sorted.iterrows()):
        fig.add_trace(go.Scatterpolar(
            r=[row[c] for c in categories],
            theta=[english_terms_dict[c] for c in categories],
            fill='toself',
            name=row["player"],
            line=dict(color=custom_colors[i % 2])
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="#E9EAE3",
            radialaxis=dict(
                visible=True,
                range=[0, 1 if df[categories].max().max() <= 1 else None],
                gridcolor='white',
                linecolor='white'
            ),
            angularaxis=dict(
                gridcolor='white',
                linecolor='white'
            )
        ),
        title={
            'text': f"Лучевая диаграмма для матча",
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=True,
        legend=dict(
            x=0.85,
            y=1,
            xanchor="left"
        ),
        paper_bgcolor="#f1f2eb",
        plot_bgcolor="#f1f2eb",
        height=600,
        font=dict(family='Helvetica'),
    )
    return fig
#d9dddc
@callback(
    Output('player-dropdown', 'options'),
    Input('tournament-dropdown', 'value')
)
def set_match_options(selected_tournament):
    return [{'label': i[1], 'value': i[0]} for i in get_players_in_tournament(selected_tournament)]
@callback(
    Output('line-plot', 'figure'),
    Input('player-dropdown', 'value'),
    Input('tournament-dropdown', 'value'),
)
def plot_stat_lines(player_id, tournament_id):
    df = get_player_stats_across_matches(player_id, tournament_id)

    if df.empty:
        print("No data found.")
        return

    categories = ["aces", "double_faults", "winners", "unforced_errors"]
    df = df[["match_id"] + categories].sort_values(by="match_id", ascending=False)

    df_plot = df.set_index("match_id").T
    df_plot.columns = [str(mid) for mid in df_plot.columns]
    df_plot["stat"] = df_plot.index


    with Session(engine) as session:
        player = session.get(Player, player_id)
        tournament = session.get(Tournament, tournament_id)
        player_name = player.name if player else f"Player #{player_id}"
        tournament_name = tournament.name if tournament else f"Tournament #{tournament_id}"

    stat_colors = {
        "aces": "#33658a",             # court blue
        "double_faults": "#a13920",    # clay red
        "winners": "#a3a702",          # green
        "unforced_errors": "#6e4f37"   # dark gray
    }

    fig = go.Figure()

    for _, row in df_plot.iterrows():
        fig.add_trace(go.Scatter(
            x=df_plot.columns[:-1],
            y=row[:-1],
            mode='lines+markers',
            name=english_terms_dict.get(row["stat"], row["stat"]),
            line=dict(color=stat_colors.get(row["stat"], "#000000"))
        ))

    fig.update_layout(
        title={
            'text': f"Динамика показателей {player_name} на {tournament_name}",
            'x': 0.5,
            'xanchor': 'center'
        },

        xaxis=dict(
            title="ID матча", # Ensures x-axis starts at 0
        ),
        yaxis=dict(
            title="Количество",  # Ensures y-axis starts at 0
        ),
        legend_title="Показатели",
        paper_bgcolor="#f1f2eb",
        plot_bgcolor="#E9EAE3",  # match spider plot
        # margin=dict(l=40, r=40, t=60, b=40),
        # width=1000,
        # height=600,
        font=dict(family='Helvetica'),
    )
    return fig


@callback(
    Output('scatter-plot', 'figure'),
    Input('player-scatter-dropdown', 'value'),
    Input('stat1-dropdown', 'value'),
    Input('stat2-dropdown', 'value')
)
def plot_stat_scatter(player_id: int, stat_x_r: str, stat_y_r: str):

    with Session(engine) as session:
        player = session.get(Player, player_id)
        player_name = player.name if player else f"Player #{player_id}"

    stat_x = russian_terms_dict[stat_x_r]
    stat_y = russian_terms_dict[stat_y_r]

    print(stat_x, stat_y)
    x_vals = get_player_stat_values(player_id, stat_x)
    y_vals = get_player_stat_values(player_id, stat_y)

    x_range = [-0.03, 1.02] if all(0 <= x <= 1 for x in x_vals) else None
    y_range = [-0.03, 1.02] if all(0 <= y <= 1 for y in y_vals) else None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers',
        marker=dict(size=10, color='#a3a702'),
        name=f"{stat_y_r} vs {stat_x_r}",

    ))

    fig.update_layout(
        title={
            'text': f"Сравнение показателей для {player_name}",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title=stat_x_r,
            range=x_range,
            rangemode='normal' if not x_range else None
        ),
        yaxis=dict(
            title=stat_y_r,
            range=y_range,
            rangemode='normal' if not y_range else None
        ),
        paper_bgcolor="#f1f2eb",
        plot_bgcolor="#E9EAE3",
        font=dict(family="Helvetica"),
    )
    return fig

def get_stats(player_id: int, stat_r: str):
    stat = russian_terms_dict[stat_r]
    vals = get_player_stat_values(player_id, stat)
    return vals

def draw_violin(stat_name, stat_list, color):
    fig = go.Figure()
    fig.add_trace(go.Violin(
        x=stat_list,
        name='',
        marker_color=color,
        )
    )

    fig.update_layout(
        title=f"Распределение показателя {stat_name}",
        paper_bgcolor="#f1f2eb",
        plot_bgcolor="#E9EAE3",
        font=dict(family="Helvetica"),
        showlegend=False,
        height=300,
        width=600
    )
    return fig

@callback(
    Output('stat-violin', 'figure'),
    Input('player-scatter-dropdown', 'value'),
    Input('stat1-dropdown', 'value'),
    Input('stat2-dropdown', 'value'),
)
def draw_violins(player_id: int, stat_x_r: str, stat_y_r: str):
    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        f"Распределение показателя {stat_x_r}",
        f"Распределение показателя {stat_y_r}"
    ), horizontal_spacing=0.07)
    stat_list_1 = get_stats(player_id, stat_x_r)
    fig.add_trace(go.Violin(x=stat_list_1,
                            name='',
                            marker_color='#a13920'),
                  row=1, col=1)

    stat_list_2 = get_stats(player_id, stat_y_r)
    fig.add_trace(go.Violin(x=stat_list_2,
                            name='',
                            marker_color='#6e4f37'),
                  row=1, col=2)

    for annotation in fig['layout']['annotations']:
        annotation['y'] += 0.1

    fig.update_layout(
        paper_bgcolor="#f1f2eb",
        plot_bgcolor="#E9EAE3",
        font=dict(family="Helvetica"),
        showlegend=False,
        height=300,
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)