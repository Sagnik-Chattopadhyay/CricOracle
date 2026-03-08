from db import SessionLocal
from models import Delivery, Match
from sqlalchemy import func, desc, or_
import time

db = SessionLocal()
player_id = 25  # Virat Kohli or someone
match_format = 'T20I'
window = 5

start = time.time()

# Get matches
matches = (
    db.query(Match.match_id)
    .join(Delivery, Match.match_id == Delivery.match_id)
    .filter(Match.format == match_format)
    .filter(or_(Delivery.batsman_id == player_id, Delivery.bowler_id == player_id))
    .group_by(Match.match_id)
    .order_by(desc(Match.date))
    .limit(window)
    .all()
)

match_ids = [m[0] for m in matches]

# O1: Batting query
bat_stats = (
    db.query(
        Delivery.match_id,
        func.sum(Delivery.runs_off_bat).label('runs'),
        func.count(Delivery.delivery_id).label('balls')
    )
    .filter(Delivery.batsman_id == player_id, Delivery.match_id.in_(match_ids))
    .group_by(Delivery.match_id)
    .all()
)
bat_map = {r.match_id: {"runs": r.runs, "balls": r.balls} for r in bat_stats}

# O2: Bowling query
bowl_stats = (
    db.query(
        Delivery.match_id,
        func.count(Delivery.delivery_id).label('balls_bowled'),
        func.sum(Delivery.runs_off_bat + Delivery.extras).label('runs_conceded'),
        func.count(Delivery.player_dismissed_id).label('wickets')
    )
    .filter(Delivery.bowler_id == player_id, Delivery.match_id.in_(match_ids))
    .group_by(Delivery.match_id)
    .all()
)
bowl_map = {r.match_id: {"balls": r.balls_bowled, "runs": r.runs_conceded, "wickets": r.wickets} for r in bowl_stats}

total_runs = 0
total_balls_bowled = 0
batting_scores, bowling_scores = [], []

for m_id in match_ids:
    bs = bat_map.get(m_id, {"runs": 0, "balls": 0})
    runs = bs["runs"]
    balls = bs["balls"]
    total_runs += runs
    sr = (runs / balls * 100) if balls > 0 else 0
    batting_scores.append((runs * 1.5) + (sr * 0.3))
    
    bws = bowl_map.get(m_id, {"balls": 0, "runs": 0, "wickets": 0})
    balls_bowled = bws["balls"]
    total_balls_bowled += balls_bowled
    runs_conceded = bws["runs"]
    wickets = bws["wickets"]
    overs = balls_bowled / 6.0
    econ = (runs_conceded / overs) if overs > 0 else 10.0
    bowl_score = (wickets * 30) + (max(0, 10 - econ) * 5) if balls_bowled > 0 else 0
    bowling_scores.append(bowl_score)

print(batting_scores, bowling_scores)
print(f"Time taken: {time.time() - start:.4f}s")
