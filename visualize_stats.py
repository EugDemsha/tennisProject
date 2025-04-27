from sqlmodel import Session, select
from db import engine, Player, MatchStats
import plotly.graph_objects as go

def get_match_stats(match_id: int):
    with Session(engine) as session:
        stats = session.exec(
            select(MatchStats)
            .where(MatchStats.match_id == match_id)
            .order_by(MatchStats.player_id)
        ).all()

        players = []
        aces = []
        double_faults = []

        for stat in stats:
            player = session.get(Player, stat.player_id)
            players.append(player.name if player else f"Player {stat.player_id}")
            aces.append(stat.aces)
            double_faults.append(stat.double_faults)

    return players, aces, double_faults

def plot_stacked_bar(players, aces, double_faults):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=players,
        y=aces,
        name='Aces',
        marker_color='#0077B6'
    ))

    fig.add_trace(go.Bar(
        x=players,
        y=double_faults,
        name='Double Faults',
        marker_color='#B94E48'
    ))

    fig.update_layout(
        barmode='stack',
        title="Сравнение подач навылет и двойных ошибок",
        xaxis_title="Player",
        yaxis_title="Count",
        template="plotly_white"
    )

    fig.show()

if __name__ == "__main__":
    players, aces, double_faults = get_match_stats(match_id=1)
    plot_stacked_bar(players, aces, double_faults)