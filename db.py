from sqlmodel import SQLModel, create_engine, Session, Field
from dotenv import load_dotenv
import os

load_dotenv()

DB_ADDRESS = os.getenv("DB_ADDRESS")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)


class Tournament(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    city: str
    year: int = Field(default=2025)


class Player(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class Match(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    player1_id: int = Field(foreign_key="player.id")
    player2_id: int = Field(foreign_key="player.id")
    winner_id: int = Field(foreign_key="player.id")


class Stats(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id")
    player_id: int = Field(foreign_key="player.id")

    serve_rating: int = 0
    aces: int = 0
    double_faults: int = 0
    first_serve: float = 0.0
    first_serve_points_won: float = 0.0
    second_serve_points_won: float = 0.0
    break_points_saved: float = 0.0
    service_games_played: int = 0
    return_rating: int = 0
    first_serve_return_points_won: float = 0.0
    second_serve_return_points_won: float = 0.0
    break_points_converted: float = 0.0
    return_games_played: int = 0
    net_points_won: float = 0.0
    winners: int = 0
    unforced_errors: int = 0
    service_points_won: float = 0.0
    return_points_won: float = 0.0
    total_points_won: float = 0.0


def create_db():
    SQLModel.metadata.create_all(engine)


def insert_tournament(tournament_name, city, year):
    tournament = Tournament(name=tournament_name, city=city, year=year)
    with Session(engine) as session:
        session.add(tournament)
        session.commit()
        session.refresh(tournament)
    return tournament.id


def insert_player(player_name):
    player = Player(name=player_name)
    with Session(engine) as session:
        session.add(player)
        session.commit()
        session.refresh(player)
    return player.id


def insert_match(tournament_id, player1_id, player2_id, winner_id):
    match = Match(
        tournament_id=tournament_id,
        player1_id=player1_id,
        player2_id=player2_id,
        winner_id=winner_id
    )
    with Session(engine) as session:
        session.add(match)
        session.commit()
        session.refresh(match)
    return match.id


def insert_stats(match_id, player_id, stats):
    match_stats = Stats(
        match_id=match_id,
        player_id=player_id,
        serve_rating=stats.get("serve_rating", 0),
        aces=stats.get("aces", 0),
        double_faults=stats.get("double_faults", 0),
        first_serve=stats.get("first_serve", 0.0),
        first_serve_points_won=stats.get("1st_serve_points_won", 0.0),
        second_serve_points_won=stats.get("2nd_serve_points_won", 0.0),
        break_points_saved=stats.get("break_points_saved", 0.0),
        service_games_played=stats.get("service_games_played", 0),
        return_rating=stats.get("return_rating", 0),
        first_serve_return_points_won=stats.get("1st_serve_return_points_won", 0.0),
        second_serve_return_points_won=stats.get("2nd_serve_return_points_won", 0.0),
        break_points_converted=stats.get("break_points_converted", 0.0),
        return_games_played=stats.get("return_games_played", 0),
        net_points_won=stats.get("net_points_won", 0.0),
        winners=stats.get("winners", 0),
        unforced_errors=stats.get("unforced_errors", 0),
        service_points_won=stats.get("service_points_won", 0.0),
        return_points_won=stats.get("return_points_won", 0.0),
        total_points_won=stats.get("total_points_won", 0.0),
    )
    with Session(engine) as session:
        session.add(match_stats)
        session.commit()

if __name__ == "__main__":
    create_db()
