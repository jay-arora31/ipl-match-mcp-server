from sqlalchemy import Column, Integer, String, Date, Float, Boolean, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String, unique=True, index=True)  # Cricsheet match ID
    city = Column(String)
    venue = Column(String)
    date = Column(Date)
    season = Column(String)
    match_type = Column(String, default='T20')
    event_name = Column(String)
    match_number = Column(Integer)
    gender = Column(String, default='male')
    overs = Column(Integer, default=20)
    balls_per_over = Column(Integer, default=6)
    
    # Outcome
    winner = Column(String)
    result = Column(String)  # normal win, no result, tie
    win_by_runs = Column(Integer)
    win_by_wickets = Column(Integer)
    win_method = Column(String)  # D/L, etc.
    
    # Toss
    toss_winner = Column(String)
    toss_decision = Column(String)  # bat/field
    
    # Player of the match
    player_of_match = Column(String)
    
    # Officials
    umpires = Column(JSON)
    match_referee = Column(String)
    tv_umpire = Column(String)
    reserve_umpire = Column(String)
    
    # Teams
    team1 = Column(String)
    team2 = Column(String)
    
    # Raw JSON data (for complex queries)
    raw_data = Column(JSON)
    
    # Relationships
    innings = relationship("Innings", back_populates="match")
    deliveries = relationship("Delivery", back_populates="match")

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    short_name = Column(String)

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    cricsheet_id = Column(String, unique=True)  # From registry
    
class Innings(Base):
    __tablename__ = 'innings'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), index=True)
    innings_number = Column(Integer)  # 1 or 2
    team = Column(String)
    total_runs = Column(Integer)
    total_wickets = Column(Integer)
    total_overs = Column(Float)
    run_rate = Column(Float)
    
    # Powerplay stats
    powerplay_runs = Column(Integer)
    powerplay_wickets = Column(Integer)
    
    # Target (for 2nd innings)
    target = Column(Integer)
    
    match = relationship("Match", back_populates="innings")

class Delivery(Base):
    __tablename__ = 'deliveries'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), index=True)
    innings = Column(Integer)
    over = Column(Integer)
    ball = Column(Integer)
    
    # Players
    batter = Column(String, index=True)
    non_striker = Column(String, index=True) 
    bowler = Column(String, index=True)
    
    # Runs
    runs_batter = Column(Integer, default=0)
    runs_extras = Column(Integer, default=0)
    runs_total = Column(Integer, default=0)
    
    # Extras
    extras_type = Column(String)  # wide, noball, bye, legbye
    
    # Wicket
    wicket_taken = Column(Boolean, default=False)
    wicket_type = Column(String)  # caught, bowled, lbw, etc.
    wicket_player_out = Column(String)
    wicket_fielders = Column(JSON)
    
    # Other details
    is_super_over = Column(Boolean, default=False)
    
    match = relationship("Match", back_populates="deliveries")

class PlayerStats(Base):
    __tablename__ = 'player_stats'
    
    id = Column(Integer, primary_key=True)
    player_name = Column(String, index=True)
    
    # Batting stats
    matches_batted = Column(Integer, default=0)
    total_runs = Column(Integer, default=0)
    highest_score = Column(Integer, default=0)
    centuries = Column(Integer, default=0)
    fifties = Column(Integer, default=0)
    sixes = Column(Integer, default=0)
    fours = Column(Integer, default=0)
    balls_faced = Column(Integer, default=0)
    batting_average = Column(Float)
    strike_rate = Column(Float)
    
    # Bowling stats  
    matches_bowled = Column(Integer, default=0)
    wickets_taken = Column(Integer, default=0)
    runs_conceded = Column(Integer, default=0)
    overs_bowled = Column(Float, default=0.0)
    bowling_average = Column(Float)
    economy_rate = Column(Float)
    best_figures = Column(String)
    
class TeamStats(Base):
    __tablename__ = 'team_stats'
    
    id = Column(Integer, primary_key=True)
    team_name = Column(String, index=True)
    
    matches_played = Column(Integer, default=0)
    matches_won = Column(Integer, default=0)
    matches_lost = Column(Integer, default=0)
    matches_no_result = Column(Integer, default=0)
    
    total_runs_scored = Column(Integer, default=0)
    total_runs_conceded = Column(Integer, default=0)
    highest_score = Column(Integer, default=0)
    lowest_score = Column(Integer, default=0)
    
    win_percentage = Column(Float) 