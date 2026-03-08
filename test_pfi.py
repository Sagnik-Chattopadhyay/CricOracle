from db import SessionLocal
from models import Delivery, Match, Player
from sqlalchemy import desc, func, or_
import math

def calculate_detailed_pfi(db, player_id, match_format='T20I', window=5):
    # 1. Get recent matches where player participated (batted or bowled)
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
    
    if not matches:
        return {"batting_pfi": 0, "bowling_pfi": 0, "total_pfi": 50, "role": "Batter"}
        
    match_ids = [m[0] for m in matches]
    
    batting_scores = []
    bowling_scores = []
    
    total_runs_scored = 0
    total_balls_bowled = 0
    
    for m_id in match_ids:
        # Batting stats
        bat_deliveries = db.query(Delivery).filter_by(match_id=m_id, batsman_id=player_id).all()
        runs = sum(d.runs_off_bat for d in bat_deliveries)
        balls = len(bat_deliveries)
        total_runs_scored += runs
        sr = (runs / balls * 100) if balls > 0 else 0
        bat_score = (runs * 1.5) + (sr * 0.3)
        batting_scores.append(bat_score)
        
        # Bowling stats
        bowl_deliveries = db.query(Delivery).filter_by(match_id=m_id, bowler_id=player_id).all()
        legal_deliveries = [d for d in bowl_deliveries if d.extras == 0 or d.wicket_type is not None] # Simplification
        balls_bowled = len(bowl_deliveries)
        total_balls_bowled += balls_bowled
        runs_conceded = sum(d.runs_off_bat + d.extras for d in bowl_deliveries)
        wickets = sum(1 for d in bowl_deliveries if d.player_dismissed_id is not None)
        
        overs = balls_bowled / 6.0
        econ = (runs_conceded / overs) if overs > 0 else 10.0
        
        # Reward wickets highly, penalize high economy
        bowl_score = (wickets * 30) + (max(0, 10 - econ) * 5) if balls_bowled > 0 else 0
        bowling_scores.append(bowl_score)
        
    weights = [0.4, 0.25, 0.15, 0.1, 0.1][:len(match_ids)]
    total_w = sum(weights)
    weights = [w/total_w for w in weights]
    
    avg_bat_score = sum(s * w for s, w in zip(batting_scores, weights))
    avg_bowl_score = sum(s * w for s, w in zip(bowling_scores, weights))
    
    # Scale out of ~100 max (cap at 150 for extreme outliers)
    bat_pfi = min(150, avg_bat_score)
    bowl_pfi = min(150, avg_bowl_score)
    
    # Determine Role
    if total_balls_bowled > 24 and total_runs_scored > 50:
        role = "All-rounder"
    elif total_balls_bowled > 18:
        role = "Bowler"
    else:
        role = "Batter"
        
    total_pfi = (bat_pfi * 0.5) + (bowl_pfi * 0.5) if role == "All-rounder" else (bat_pfi if role == "Batter" else bowl_pfi)
    
    return {
        "batting_pfi": round(bat_pfi, 1),
        "bowling_pfi": round(bowl_pfi, 1),
        "total_pfi": round(total_pfi, 1),
        "role": role
    }

if __name__ == "__main__":
    db = SessionLocal()
    # Find active players from recent matches (e.g., Hardik Pandya, an all-rounder)
    p = db.query(Player).filter(Player.name.ilike('%Pandya%')).first()
    if p:
        print(f"Stats for {p.name}:")
        print(calculate_detailed_pfi(db, p.player_id))
        
    b = db.query(Player).filter(Player.name.ilike('%Bumrah%')).first()
    if b:
        print(f"\nStats for {b.name}:")
        print(calculate_detailed_pfi(db, b.player_id))
        
    k = db.query(Player).filter(Player.name.ilike('%Kohli%')).first()
    if k:
        print(f"\nStats for {k.name}:")
        print(calculate_detailed_pfi(db, k.player_id))
        
    db.close()
