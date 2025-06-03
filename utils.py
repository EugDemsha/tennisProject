import pandas as pd
from sqlmodel import Session, select
from db import engine, Tournament, Match, Player, Stats

def list_tournaments():
    with Session(engine) as session:
        tournaments = session.exec(select(Tournament)).all()
        return [(t.id, f"{t.name} ({t.city}, {t.year})") for t in tournaments]


def list_players():
    with Session(engine) as session:
        players = session.exec(select(Player)).all()
        return [(t.id, t.name) for t in players]


def list_matches_for_tournament(tournament_id: int):
    with Session(engine) as session:
        matches = session.exec(
            select(Match).where(Match.tournament_id == tournament_id)
        ).all()
        result = []
        for match in matches:
            p1 = session.get(Player, match.player1_id)
            p2 = session.get(Player, match.player2_id)
            result.append((match.id, f"{p1.name} vs {p2.name}"))
        return result


def get_match_stats(match_id: int):
    with Session(engine) as session:
        stats = session.exec(select(Stats).where(Stats.match_id == match_id)).all()
        rows = []
        for s in stats:
            player = session.get(Player, s.player_id)
            data = s.dict()
            data['player'] = player.name
            rows.append(data)
        # return pd.DataFrame(rows).drop(columns=["id", "match_id", "player_id"])
        return pd.DataFrame(rows)

def get_player_stats_across_matches(player_id: int, tournament_id: int):
    with Session(engine) as session:
        player = session.get(Player, player_id)

        matches = session.exec(
            select(Match).where(
                (Match.tournament_id == tournament_id) &
                ((Match.player1_id == player_id) | (Match.player2_id == player_id))
            )
        ).all()

        rows = []
        for match in matches:
            stats = session.exec(
                select(Stats).where(
                    (Stats.match_id == match.id) & (Stats.player_id == player_id)
                )
            ).first()
            if stats:
                row = stats.dict()
                row["match_id"] = match.id
                row["player"] = player.name
                rows.append(row)

        # Sort by match_id descending (lower = later match)
        df = pd.DataFrame(rows).sort_values(by="match_id", ascending=False)
        return df


def get_players_in_tournament(tournament_id: int):
    with Session(engine) as session:
        matches = session.exec(
            select(Match).where(Match.tournament_id == tournament_id)
        ).all()

        player_ids = set()
        for match in matches:
            player_ids.add(match.player1_id)
            player_ids.add(match.player2_id)

        players = session.exec(
            select(Player).where(Player.id.in_(player_ids))
        ).all()

        return [(player.id, player.name) for player in players]


def get_player_stat_values(player_id: int, stat: str) -> list[float]:
    with Session(engine) as session:
        stmt = select(getattr(Stats, stat)).where(Stats.player_id == player_id)
        results = session.exec(stmt).all()

    return [r for r in results if r is not None]