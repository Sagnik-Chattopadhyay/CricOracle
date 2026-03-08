from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Float, DateTime
from db import Base
import datetime

class Team(Base):
    __tablename__ = "teams"
    team_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    cricsheet_id = Column(String, unique=True, index=True) # Optional
    short_name = Column(String)
    country = Column(String)
    team_type = Column(String) # 'Franchise' or 'International'

class Player(Base):
    __tablename__ = "players"
    player_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    cricsheet_id = Column(String, unique=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"))
    role = Column(String)
    batting_style = Column(String)
    bowling_style = Column(String)
    nationality = Column(String)
    dob = Column(Date)

class Venue(Base):
    __tablename__ = "venues"
    venue_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    city = Column(String)
    country = Column(String)
    avg_1st_innings_score = Column(Integer)
    pitch_type = Column(String)

class Match(Base):
    __tablename__ = "matches"
    match_id = Column(Integer, primary_key=True, index=True)
    team_a_id = Column(Integer, ForeignKey("teams.team_id"))
    team_b_id = Column(Integer, ForeignKey("teams.team_id"))
    venue_id = Column(Integer, ForeignKey("venues.venue_id"))
    date = Column(Date, index=True)
    format = Column(String, index=True)
    toss_winner_id = Column(Integer, ForeignKey("teams.team_id"))
    toss_decision = Column(String)
    winner_id = Column(Integer, ForeignKey("teams.team_id"))
    win_margin = Column(String)
    is_dl_applied = Column(Boolean, default=False)

class Delivery(Base):
    __tablename__ = "deliveries"
    delivery_id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), index=True)
    innings = Column(Integer)
    over = Column(Integer)
    ball = Column(Integer)
    batting_team_id = Column(Integer, ForeignKey("teams.team_id"))
    bowling_team_id = Column(Integer, ForeignKey("teams.team_id"))
    batsman_id = Column(Integer, ForeignKey("players.player_id"), index=True)
    non_striker_id = Column(Integer, ForeignKey("players.player_id"))
    bowler_id = Column(Integer, ForeignKey("players.player_id"), index=True)
    runs_off_bat = Column(Integer)
    extras = Column(Integer)
    wicket_type = Column(String)
    player_dismissed_id = Column(Integer, ForeignKey("players.player_id"))

class PlayerForm(Base):
    __tablename__ = "player_form"
    form_id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.player_id"))
    format = Column(String)
    form_score = Column(Float)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
