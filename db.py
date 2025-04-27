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
    __tablename__ = "tournaments"
    tournament_id: int = Field(default=None, primary_key=True)
    name: str
    city: str
    year: int


class Player(SQLModel, table=True):
    __tablename__ = "players"
    player_id: int = Field(default=None, primary_key=True)
    name: str
    country: str
    ranking: int


class Match(SQLModel, table=True):
    __tablename__ = "tournament_matches"
    match_id: int = Field(default=None, primary_key=True)
    tournament_id: int
    stage: str
    player1_id: int
    player2_id: int
    winner_id: int


class MatchStats(SQLModel, table=True):
    __tablename__ = "match_stats"
    stat_id: int = Field(default=None, primary_key=True)
    match_id: int
    player_id: int
    aces: int = 0
    double_faults: int = 0
    winners: int = 0
    unforced_errors: int = 0


def create_db():
    SQLModel.metadata.create_all(engine)


def insert_tournament(tournament_name, city, year):
    tournament = Tournament(name=tournament_name, city=city, year=year)
    with Session(engine) as session:
        session.add(tournament)
        session.commit()
        session.refresh(tournament)
    return tournament.tournament_id


def insert_player(player_name, country, ranking):
    player = Player(name=player_name, country=country, ranking=ranking)
    with Session(engine) as session:
        session.add(player)
        session.commit()
        session.refresh(player)
    return player.player_id


def insert_match(tournament_id, stage, player1_id, player2_id, winner_id):
    match = Match(tournament_id=tournament_id, stage=stage, player1_id=player1_id, player2_id=player2_id, winner_id=winner_id)
    with Session(engine) as session:
        session.add(match)
        session.commit()
        session.refresh(match)
    return match.match_id


def insert_match_stats(match_id, player_id, stat_dict, dict_key):
    match_stats = MatchStats(
        match_id=match_id,
        player_id=player_id,
        aces=int(stat_dict.get("ACES", {}).get(dict_key, 0)),
        double_faults=int(stat_dict.get("DOUBLE FAULTS", {}).get(dict_key, 0)),
        winners=int(stat_dict.get("WINNERS", {}).get(dict_key, 0)),
        unforced_errors=int(stat_dict.get("UNFORCED ERRORS", {}).get(dict_key, 0)),
    )
    with Session(engine) as session:
        session.add(match_stats)
        session.commit()
